"""
Robô do LeiDireta: lê os quadros oficiais do Planalto e grava novas.json
com as leis, leis complementares e decretos mais recentes.

Roda todo dia pelo GitHub Actions (.github/workflows/atualizar.yml).
Se o Planalto bloquear o acesso, o script avisa no log e não altera nada.
"""
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE = "https://www.planalto.gov.br/ccivil_03/"
ARQ = Path(__file__).resolve().parent.parent / "novas.json"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/130.0 Safari/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9",
}
ROTULO = re.compile(r"(\d[\d.]*?)[,;]?de\.?(\d{1,2})[º°]?\.(\d{1,2})\.(\d{2,4})", re.I)


class Bloqueado(Exception):
    pass


def bloco(ano: int) -> str:
    if ano < 2007:
        return "2004-2006"
    ini = 2007 + 4 * ((ano - 2007) // 4)
    return f"{ini}-{ini + 3}"


def baixar(caminho: str):
    r = requests.get(BASE + caminho, headers=HEADERS, timeout=60)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    bruto = r.content
    try:
        texto = bruto.decode("utf-8")
    except UnicodeDecodeError:
        texto = bruto.decode("windows-1252", errors="replace")
    if "Acesso Negado" in texto[:800]:
        return None
    if "requisição foi bloqueada" in texto or "requisicao foi bloqueada" in texto:
        raise Bloqueado(caminho)
    return BeautifulSoup(texto, "html.parser")


def ler_quadro(caminho: str):
    doc = baixar(caminho)
    if doc is None:
        return []
    saida = []
    for tr in doc.find_all("tr"):
        tds = tr.find_all("td", recursive=False)
        if len(tds) < 2:
            continue
        a = tds[0].find("a", href=True)
        if not a:
            continue
        m = ROTULO.search(re.sub(r"\s+", "", a.get_text()))
        if not m:
            continue
        ano = m.group(4)
        if len(ano) == 2:
            ano = "20" + ano
        url = urljoin(BASE + caminho, a["href"])
        if not url.startswith(BASE):
            continue
        ementa = re.sub(r"\s+", " ", tds[1].get_text()).strip()[:140]
        saida.append([int(m.group(1).replace(".", "")),
                      f"{int(m.group(2))}/{int(m.group(3))}/{ano}",
                      url[len(BASE):], ementa])
    return saida


def main():
    agora = datetime.now(timezone(timedelta(hours=-3)))
    ano = agora.year
    q_lei = lambda y: f"_Ato{bloco(y)}/{y}/Lei/_leis{y}.htm"
    q_dec = lambda y: f"_Ato{bloco(y)}/{y}/Decreto/_decretos{y}.htm"

    try:
        leis, decs = ler_quadro(q_lei(ano)), ler_quadro(q_dec(ano))
        ini_l = min((x[0] for x in leis), default=None)
        ini_d = min((x[0] for x in decs), default=None)
        if len(leis) < 60:
            leis += ler_quadro(q_lei(ano - 1))
        if len(decs) < 30:
            decs += ler_quadro(q_dec(ano - 1))
        lcs = ler_quadro("leis/lcp/quadro_lcp.htm")[:6]
    except Bloqueado as e:
        print(f"::warning::O Planalto bloqueou o acesso do robô ({e}). Nada foi alterado.")
        return 0
    except requests.RequestException as e:
        print(f"::warning::Falha ao acessar o Planalto: {e}. Nada foi alterado.")
        return 0

    if not leis:
        print("::warning::Nenhuma lei lida nos quadros; a estrutura do Planalto pode ter mudado. Nada foi alterado.")
        return 0

    leis.sort(key=lambda x: -x[0])
    decs.sort(key=lambda x: -x[0])

    atual = json.loads(ARQ.read_text(encoding="utf-8")) if ARQ.exists() else {}
    inicio = atual.get("inicioAno", {"L": {}, "D": {}})
    inicio.setdefault("L", {})
    inicio.setdefault("D", {})
    if ini_l:
        inicio["L"][str(ano)] = ini_l
    if ini_d:
        inicio["D"][str(ano)] = ini_d

    topo = lambda d, k: (d.get(k) or [[0]])[0][0]
    if atual and all(topo(atual, k) == v for k, v in
                     (("L", leis[0][0]), ("LC", lcs[0][0] if lcs else 0), ("D", decs[0][0] if decs else 0))):
        print("Sem novidades no Planalto.")
        return 0

    novo = {
        "atualizado": agora.strftime("%Y-%m-%dT%H:%M"),
        "L": leis[:60],
        "LC": lcs,
        "D": decs[:30],
        "inicioAno": inicio,
    }
    ARQ.write_text(json.dumps(novo, ensure_ascii=False, indent=0), encoding="utf-8")
    print(f"Atualizado: Lei {leis[0][0]}, LC {lcs[0][0] if lcs else '-'}, Decreto {decs[0][0] if decs else '-'}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
