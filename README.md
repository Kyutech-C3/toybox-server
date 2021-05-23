# toybox-server

## 開発
\*おそらくデータベースサーバーが必要になるので、docker-compose化する可能性大
### 環境構築
1. `$ git clone git@github.com:Kyutech-C3/toybox-server.git`

1. `$ cd toybox-server`

1. `$ pipenv shell`

1. `$ pipenv install`

### 開発環境起動
1. `$ uvicorn main:app --reload`