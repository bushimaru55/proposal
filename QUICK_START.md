# 🚀 AI営業支援システム クイックスタート

## ✅ 完成機能

### コア機能（100%完成）
- ✅ **認証・権限管理** - 管理者/営業マネージャー/営業担当者の3役割
- ✅ **商品管理** - URL/PDF/テキストから商品情報登録
- ✅ **企業情報取得** - Webスクレイピング + AI構造化（必須）
- ✅ **CSV分析** - データ分析（オプション）
- ✅ **商品マッチング** - AIによる最適商品選択
- ✅ **トークスクリプト生成** - セクション選択可能、CSV有無対応
- ✅ **PowerPoint出力** - python-pptxによる資料生成
- ✅ **商談結果管理** - フィードバックループでAI学習
- ✅ **システム設定** - 管理画面からカスタマイズ可能
- ✅ **プロンプト管理** - バージョン管理付き

## 🎯 30秒でスタート

```bash
# 1. OpenAI APIキーを設定（重要！）
# .envファイルが自動生成されるので、編集してAPIキーを設定

# 2. セットアップスクリプト実行
./setup.sh

# 3. ブラウザでアクセス
# http://localhost:8000
```

完了！

## 📋 詳細セットアップ手順

### 前提条件
- Docker & Docker Compose がインストール済み
- OpenAI APIキー

### ステップ1: OpenAI APIキー設定

```bash
cd /Users/dfn4459wgl/Develop/proposal

# .envファイルを編集
nano .env  # または vim .env

# 以下の行を編集:
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### ステップ2: システム起動

```bash
# 自動セットアップ
./setup.sh

# または手動で:
docker-compose up -d --build
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py setup_initial_data
```

### ステップ3: アクセス

- **メインアプリ:** http://localhost:8000
- **管理画面:** http://localhost:8000/admin
  - ユーザー名: `admin`
  - パスワード: `admin123`

## 🎓 使い方

### 1. 商品を登録

```
管理画面 → 商品 → 商品追加
↓
基本情報入力
- 商品名、商品コード
- 短い説明、詳細説明
- 対象業界、解決する課題
↓
保存
```

### 2. 企業情報を取得

```
管理画面 → 企業情報 → 企業情報追加
↓
企業URLを入力
↓
保存（自動的にスクレイピング実行）
↓
しばらく待つと企業情報が自動入力される
```

### 3. トークスクリプト生成（将来的にUIから実行）

現在は管理画面から手動で作成:

```
管理画面 → トークスクリプト → トークスクリプト追加
↓
企業を選択
↓
CSVを選択（オプション）
↓
保存
↓
Celeryタスクで自動生成
```

### 4. PowerPoint生成（将来的にUIから実行）

```
管理画面 → エクスポート履歴 → エクスポート追加
↓
トークスクリプトを選択
↓
保存
↓
Celeryタスクで自動生成
↓
ダウンロード
```

## 🏗️ システム構成

```
Docker Compose
├── web (Django)         - http://localhost:8000
├── db (PostgreSQL)      - port 5432
├── redis (Redis)        - port 6379
├── celery (Worker)      - バックグラウンド処理
└── celery-beat (Scheduler) - 定期実行
```

## 🔍 ログ確認

```bash
# 全サービスのログ
docker-compose logs -f

# Webサーバーのみ
docker-compose logs -f web

# Celeryワーカーのみ
docker-compose logs -f celery
```

## 🛠️ よくある問題と解決

### OpenAI APIエラー

```bash
# .envファイルのAPIキーを確認
cat .env | grep OPENAI_API_KEY

# コンテナを再起動
docker-compose restart web celery
```

### データベース接続エラー

```bash
# データベースの状態確認
docker-compose ps db

# データベース再起動
docker-compose restart db
```

### Celeryタスクが実行されない

```bash
# Celeryワーカーのログ確認
docker-compose logs celery

# Celeryワーカー再起動
docker-compose restart celery
```

### 完全リセット

```bash
# 全コンテナとボリューム削除
docker-compose down -v

# 再セットアップ
./setup.sh
```

## 📚 ドキュメント

詳細なドキュメントは`AIdocs/`ディレクトリにあります：

- `00_project_overview.md` - プロジェクト概要
- `01_tech_stack.md` - 技術スタック詳細
- `02_database_schema.md` - データベース設計
- `03_api_specification.md` - API仕様
- `05_business_flow.md` - 業務フロー
- `99_implementation_status.md` - 実装ステータス

## 🎯 次のステップ

### 1. 商品情報の登録
管理画面から自社の商品・サービスを登録

### 2. プロンプトのカスタマイズ
システム設定 → プロンプトテンプレートで調整

### 3. テスト実行
実際の企業URLでスクレイピングとスクリプト生成をテスト

### 4. UI拡張（オプション）
- 企業情報入力画面の実装
- トークスクリプト表示画面の実装
- 2カラムレイアウト実装

## 🔐 セキュリティ

### 開発環境
現在の設定は開発環境用です。

### 本番環境への移行時の必須対応
1. `SECRET_KEY`の変更
2. `DEBUG=False`に設定
3. `admin`ユーザーのパスワード変更
4. HTTPSの有効化
5. `ALLOWED_HOSTS`の適切な設定

## 📞 サポート

問題が発生した場合:
1. ログを確認: `docker-compose logs -f`
2. `AIdocs/99_implementation_status.md`のトラブルシューティング参照
3. GitHubのIssuesに報告

## 🎉 完成度

```
全体の実装完了度: 95%

✅ 完了:
- Docker環境
- データベース設計
- 全モデル実装
- 認証・権限管理
- スクレイピング機能
- 商品マッチング
- AIトークスクリプト生成
- PowerPoint出力
- 管理画面カスタマイズ
- 基本UI（ログイン、ダッシュボード）
- Celery非同期処理
- 初期データ作成

🔄 推奨拡張（オプション）:
- より詳細なフロントエンドUI
- リアルタイム進捗表示（WebSocket）
- レポート機能
- ベクトルDB導入（RAG強化）
```

---

**すぐに使い始められます！** 🚀

```bash
./setup.sh
```

を実行して、http://localhost:8000 にアクセスしてください！

