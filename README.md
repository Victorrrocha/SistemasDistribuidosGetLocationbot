# SistemasDistribuidosGetLocationbot

Esse bot é parte da atividade da disciplina de Sistemas Distribuídos do semestre 2020.1 do curso de Ciência da Computação da UFRR.

Ele se baseia no tutorial https://medium.com/@mdcg.dev/desenvolvendo-o-seu-primeiro-chatbot-no-telegram-com-python-a9ad787bdf6

## Introdução

Crie um arquivo chamado `.env` no diretório `.\src\conf\` contendo o seguinte:

`TELEGRAM_TOKEN=<seu token>`<br>
`BASE_API_URL=https://http.cat/`

Baixe as bibliotecas `python-telegram-bot`, `python-dotenv`, `pymongo` e `config`.

## Utilização

A aplicação utiliza MongoDB como banco de dados. Para a aplicação se conectar ao MongoDB, é necessário iniciar o [Daemon do MongoDB](https://docs.mongodb.com/manual/reference/program/mongod.exe/#bin.mongod.exe).

Comando para iniciar a aplicação:

`python ./src/core.py` ou <br>
`python3 ./src/core.py`