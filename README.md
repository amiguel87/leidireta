# LeiDireta

Índice de consulta rápida da legislação federal, com link direto para o texto oficial no site do Planalto.

## O que há neste repositório

- `index.html`: o site inteiro (busca, índice, artigos, painel pessoal).
- `novas.json`: lista das normas publicadas recentemente, atualizada pelo robô.
- `scripts/atualizar_novas.py`: o robô, que lê os quadros oficiais do Planalto.
- `.github/workflows/atualizar.yml`: agenda o robô de segunda a sexta, às 18h17 de Brasília.

## Publicação (uma vez só)

1. No GitHub, crie um repositório **público** chamado `leidireta`, sem marcar nenhuma opção de arquivo inicial.
2. Na página do repositório vazio, clique em **uploading an existing file**, arraste todo o conteúdo desta pasta (incluindo as pastas `.github` e `scripts`) e clique em **Commit changes**.
3. Vá em **Settings > Pages**. Em "Build and deployment", escolha **Deploy from a branch**, branch **main**, pasta **/ (root)** e salve. Em poucos minutos o site abre em `https://amiguel87.github.io/leidireta/`.
4. Em **Settings > Actions > General**, em "Workflow permissions", marque **Read and write permissions** e salve.
5. Na aba **Actions**, abra "Atualizar normas recentes" e clique em **Run workflow** para testar o robô. Se o log mostrar "Atualizado" ou "Sem novidades", ele está funcionando. Se mostrar que o Planalto bloqueou o acesso, o site continua no ar normalmente e só a lista de novidades fica parada.

## Domínio leidireta.com.br

1. Registre `leidireta.com.br` no Registro.br.
2. No DNS do domínio, crie quatro registros `A` para `@` com os IPs 185.199.108.153, 185.199.109.153, 185.199.110.153 e 185.199.111.153, e um registro `CNAME` para `www` apontando para `amiguel87.github.io`.
3. Só depois de registrar o domínio e criar esses registros, vá em **Settings > Pages**, digite `leidireta.com.br` em "Custom domain", salve e, quando a opção aparecer, marque **Enforce HTTPS**. A propagação pode levar até 24 horas. Até lá o site continua no endereço provisório.
