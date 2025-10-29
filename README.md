# AI営業支援システム

Django + Docker環境で構築されたAI営業支援システムです。CSV分析（オプション）、企業情報収集、商品マッチング、AIトークスクリプト生成、PowerPoint出力機能を提供します。

## 主要機能

1. **ユーザー認証・権限管理**
   - 管理者/営業マネージャー/営業担当者の3つの役割
   - ログイン/ログアウト機能
   - ユーザー活動ログ

2. **商品管理**
   - URL/PDF/テキスト入力からの商品情報登録
   - 商品カテゴリ管理
   - 商品ナレッジベース

3. **企業情報取得**
   - Webスクレイピングによる自動収集（必須）
   - AIによる情報構造化
   - robots.txt尊重

4. **CSV分析（オプション）**
   - CSVファイルアップロード
   - AIによるデータ分析
   - 分析結果の保存

5. **商品マッチング**
   - 企業情報と商品の自動マッチング
   - AIによる適合度判定
   - マッチング理由の生成

6. **トークスクリプト生成**
   - セクション選択可能（オープニング、課題特定、提案、反論処理、クロージング）
   - CSV有無による条件分岐
   - 商品情報の組み込み
   - 商談結果からの学習

7. **PowerPoint出力**
   - python-pptxによる生成
   - セクション別スライド作成
   - ダウンロード機能

8. **商談結果管理**
   - フィードバック記録
   - AI学習データとして活用
   - 成功パターン分析

9. **システム設定・プロンプト管理**
   - 管理画面からの設定変更
   - プロンプトテンプレートのバージョン管理
   - システム全体のカスタマイズ

## 技術スタック

- **Backend**: Django 5.0, Django REST Framework
- **Database**: PostgreSQL 16
- **Cache/Queue**: Redis 7
- **Task Queue**: Celery
- **PDF処理**: PyPDF2, pdfplumber
- **スクレイピング**: BeautifulSoup4, trafilatura
- **PowerPoint**: python-pptx
- **AI**: OpenAI API (gpt-4o/gpt-4o-mini)
- **Container**: Docker, Docker Compose

## セットアップ

### 前提条件

- Docker & Docker Compose
- OpenAI APIキー

### インストール手順

1. リポジトリのクローン

```bash
git clone <repository-url>
cd proposal
```

2. 環境変数の設定

```bash
cp .env.example .env
# .envファイルを編集してOpenAI APIキーを設定
```

3. Dockerコンテナのビルドと起動

```bash
docker-compose up -d --build
```

4. データベースマイグレーション

```bash
docker-compose exec web python manage.py migrate
```

5. スーパーユーザーの作成

```bash
docker-compose exec web python manage.py createsuperuser
```

6. 初期データの作成（オプション）

```bash
docker-compose exec web python manage.py loaddata initial_data
```

7. ブラウザでアクセス

```
http://localhost:8000
```

管理画面: http://localhost:8000/admin

## 使用方法

### 初回セットアップ

1. 管理画面にログイン
2. システム設定を確認・調整
3. プロンプトテンプレートを設定
4. 商品情報を登録

### 基本的なワークフロー

1. **企業情報の登録**
   - 企業URLを入力
   - 自動的にスクレイピング実行
   - AIが企業情報を構造化

2. **CSV分析（オプション）**
   - CSVファイルをアップロード
   - プロンプトを入力して分析実行
   - 分析結果を確認

3. **トークスクリプト生成**
   - 企業を選択
   - CSVがあれば選択（オプション）
   - 生成するセクションを選択
   - AIがトークスクリプトを生成

4. **PowerPoint出力**
   - トークスクリプトを選択
   - PowerPoint生成を実行
   - ファイルをダウンロード

5. **商談結果の記録**
   - 商談後、結果を記録
   - うまくいった点・改善点を入力
   - AIが学習データとして活用

## ディレクトリ構成

```
proposal/
├── AIdocs/                      # 仕様書
├── backend/                     # Djangoプロジェクト
│   ├── config/                  # プロジェクト設定
│   ├── apps/                    # Djangoアプリケーション
│   │   ├── core/               # システム設定・プロンプト管理
│   │   ├── accounts/           # 認証・ユーザー管理
│   │   ├── products/           # 商品管理
│   │   ├── companies/          # 企業情報管理
│   │   ├── analysis/           # CSV分析（オプション）
│   │   ├── sales/              # トークスクリプト生成
│   │   └── exports/            # PowerPoint出力
│   ├── templates/              # テンプレート
│   ├── static/                 # 静的ファイル
│   ├── media/                  # メディアファイル
│   └── requirements.txt        # Pythonパッケージ
├── docker-compose.yml          # Docker構成
└── README.md
```

## 開発

### ローカル開発環境

```bash
# ログの確認
docker-compose logs -f web

# Djangoシェル
docker-compose exec web python manage.py shell

# テストの実行
docker-compose exec web python manage.py test

# マイグレーションの作成
docker-compose exec web python manage.py makemigrations

# マイグレーションの適用
docker-compose exec web python manage.py migrate
```

### Celeryの確認

```bash
# Celeryワーカーのログ
docker-compose logs -f celery

# Celeryタスクの実行確認
docker-compose exec web python manage.py shell
>>> from apps.companies.tasks import scrape_company_info
>>> scrape_company_info.delay(company_id, url)
```

## トラブルシューティング

### データベース接続エラー

```bash
# PostgreSQLコンテナの状態確認
docker-compose ps db

# データベース接続テスト
docker-compose exec web python manage.py dbshell
```

### Celeryタスクが実行されない

```bash
# Redisの状態確認
docker-compose exec redis redis-cli ping

# Celeryワーカーの再起動
docker-compose restart celery
```

### スクレイピングエラー

- robots.txtの設定を確認
- タイムアウト時間を延長
- システム設定でスクレイピング間隔を調整

## ライセンス

MIT License

## サポート

問題が発生した場合は、GitHubのIssuesに報告してください。

