# toybox-server

## 開発

環境は**docker-compose**を利用する。
VSCodeを使っている場合は、devcontainerを用いた開発を推奨。

### 環境構築

#### **【推奨】** VSCodeでDevContainerの機能を用いて環境構築

1. `git clone git@github.com:Kyutech-C3/toybox-server.git`

1. `cd toybox-server`

1. VSCodeに`Remote - Containers`拡張機能を入れた上で、`toybox-server`フォルダをコンテナで起動する。

1. ビルドが完了して、ファイルツリーが表示されたら、新しくターミナルを起動し、  
`pipenv run uvicorn main:app --reload --host 0.0.0.0`  
を実行すると、`http://localhost:8080/docs`をブラウザで開くことでドキュメントが見られる。  
ログインしたい場合は、`http:///localhost:8080/api/v1/auth/discord`をブラウザで開き、Discordでログインする。

#### docker-composeを用いて環境構築

1. `git clone git@github.com:Kyutech-C3/toybox-server.git`
1. `cd toybox-server`
1. `docker-compose up -d`
1. `docker-compose logs -f`
1. 起動後、`http://localhost:8080/docs`をブラウザで開くことでドキュメントが見られる。  
ログインしたい場合は、`http:///localhost:8080/api/v1/auth/discord`をブラウザで開き、Discordでログインする。

### 開発環境起動

1. `uvicorn main:app --reload --host 0.0.0.0`
