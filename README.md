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


## DBの更新
alembicを使用

### 初めて使う場合
`pipenv install` を実行し、パッケージをインストールを行う。

#### バックエンド開発する人
バックエンドでカラムの変更を行ったら以下の作業を行い、DBの更新を行うPythonファイルの生成と実行を行う。

Dockerが起動している状態で以下の作業を行う。

1. Dockerのコンテナに入る  
> `docker container exec -it toybox-server-api-1 /bin/sh`

2. DB更新のPythonファイルの生成  
> `alembic revision --autogenerate -m "<コメントを書く>"`

3. 生成したファイルを実行し、DBを更新  
> `alembic upgrade head`

**現在のマイグレーションのバージョン確認**  
> `alembic current`

**マイグレーション履歴の確認**  
> `alembic history --verbose`

**前のバージョンに戻す**  

数値指定で戻す  
> `alembic downgrade -1`

#### エラーの対応について

1. FileNotFoundError: [Errno 2] No such file or directory: '/api/alembic/versions'  

エラー  
>`FileNotFoundError: [Errno 2] No such file or directory: '/api/alembic/versions'`

対応法  
> `/api/alembic'`のディレクトリ内に空の`versions`ディレクトリを作る

#### フロントエンド開発の人
`バックエンド開発する人`の説明の2番を飛ばし、1番と3番を行ってください。
