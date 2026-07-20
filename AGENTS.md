# YouTube LINE Notifier 開発ルール

## 目的

YouTube WebSubで特定チャンネルの動画公開通知を受信し、
LINE Messaging APIで通知する。

## 実行環境

- Ubuntu 22.04
- Docker Compose
- Python 3.10
- FastAPI
- SQLiteを追加予定
- ホスト側公開は127.0.0.1:8100のみ

## セキュリティ制約

- .envを開かない、表示しない、変更しない
- LINEアクセストークンやユーザーIDを出力しない
- 秘密情報をGitへ登録しない
- 外部公開範囲を増やさない
- /opt/youtube-line-notifier以外を変更しない
- sudoを使用しない
- 既存のDockerプロジェクトを操作しない

## 既存動作

- GET /health はHTTP 200を返す
- GET /websub はhub.challengeを返す
- POST /websub はYouTube Atom XMLを解析する
- LINE Messaging APIへの通知が動作する

## リファクタリング方針

外部仕様を変えず、次の責務へ分離する。

- app/main.py
  - FastAPIアプリとHTTPエンドポイント
- app/config.py
  - 環境変数
- app/database.py
  - SQLite接続と初期化
- app/youtube.py
  - Atom XML解析
- app/line.py
  - LINE Messaging API送信
- app/video_repository.py
  - 通知済み動画の検索と保存
- app/notification_service.py
  - 重複確認、LINE通知、履歴保存

## 完了条件

- docker compose up -d --build が成功する
- GET /health がHTTP 200
- WebSub GET検証が成功する
- WebSub POSTがXMLを解析できる
- 同一video_idの1回目は通知する
- 同一video_idの2回目は通知しない
- SQLiteを./dataへ永続化する
- 既存コンテナが停止していない
- git diffで変更内容を確認できる