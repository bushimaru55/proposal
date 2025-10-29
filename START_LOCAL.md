# ローカル環境での動作検証手順

## 前提条件

- Docker Desktop がインストールされていること
- OpenAI APIキーを持っていること（取得: https://platform.openai.com/api-keys）

---

## 🚀 クイックスタート

### 1. Dockerを起動

Docker Desktopアプリを起動してください。

### 2. 環境変数の設定

`.env`ファイルが作成されているはずです。OpenAI APIキーを設定してください：

```bash
# .envファイルを開いて編集
nano .env

# または
code .env  # VS Codeの場合
```

`OPENAI_API_KEY`の値を実際のAPIキーに置き換えてください：
```
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxx
```

### 3. 自動セットアップスクリプトを実行

```bash
./setup.sh
```

このスクリプトは以下を自動で実行します：
- Dockerコンテナのビルド
- データベースのマイグレーション
- 初期データの作成（管理者ユーザー、設定、プロンプト）
- サービスの起動

### 4. アクセス確認

セットアップ完了後、以下のURLにアクセスできます：

- **メインアプリ**: http://localhost:8000
- **管理画面**: http://localhost:8000/admin
  - ユーザー名: `admin`
  - パスワード: `admin123`
- **API**: http://localhost:8000/api/

---

## 🔍 動作検証の流れ

### ステップ1: 管理画面にログイン

1. http://localhost:8000/admin にアクセス
2. `admin` / `admin123` でログイン
3. システム設定やプロンプトテンプレートを確認

### ステップ2: 商品情報を登録

管理画面で商品を登録します：

1. **商品カテゴリ**を作成
   - Products → Product categories → Add
   - 例：「SaaSソリューション」

2. **商品**を作成
   - Products → Products → Add
   - 名前、説明、価格などを入力

3. **商品ナレッジ**を追加
   - Products → Product knowledges → Add
   - ソースタイプを選択（URL/PDF/テキスト）
   - 保存すると自動的に処理が開始されます

### ステップ3: 企業情報を取得

#### APIを使用する場合：

```bash
# 企業情報を作成（自動スクレイピング開始）
curl -X POST http://localhost:8000/api/companies/ \
  -H "Content-Type: application/json" \
  -u admin:admin123 \
  -d '{
    "name": "株式会社サンプル",
    "website_url": "https://www.example.co.jp"
  }'
```

#### 管理画面を使用する場合：

1. Companies → Companies → Add
2. 企業名とWebサイトURLを入力
3. 保存すると自動的にスクレイピングが開始されます

### ステップ4: CSV分析（オプション）

CSVファイルがある場合：

```bash
# CSVをアップロード
curl -X POST http://localhost:8000/api/analysis/csv-uploads/ \
  -u admin:admin123 \
  -F "file=@sample.csv" \
  -F "description=テストデータ"

# 分析を実行
curl -X POST http://localhost:8000/api/analysis/csv-uploads/1/analyze/ \
  -u admin:admin123
```

### ステップ5: トークスクリプト生成

```bash
# トークスクリプトを生成
curl -X POST http://localhost:8000/api/sales/talk-scripts/generate/ \
  -H "Content-Type: application/json" \
  -u admin:admin123 \
  -d '{
    "company_id": 1,
    "analysis_id": 1,
    "selected_sections": [
      "opening",
      "problem_identification",
      "proposal",
      "objection_handling",
      "closing"
    ]
  }'
```

### ステップ6: PowerPoint出力

```bash
# PowerPointを生成
curl -X POST http://localhost:8000/api/exports/create_export/ \
  -H "Content-Type: application/json" \
  -u admin:admin123 \
  -d '{
    "talk_script_id": 1
  }'

# ダウンロード
curl -X GET http://localhost:8000/api/exports/1/download/ \
  -u admin:admin123 \
  --output proposal.pptx
```

---

## 🐛 トラブルシューティング

### ログの確認

```bash
# 全サービスのログ
docker-compose logs -f

# 特定のサービスのログ
docker-compose logs -f web
docker-compose logs -f celery
docker-compose logs -f celery-beat
```

### サービスの状態確認

```bash
docker-compose ps
```

### データベースのリセット

```bash
# 全データを削除して再構築
docker-compose down -v
./setup.sh
```

### Celeryタスクの確認

Celeryワーカーが正常に動作しているか確認：

```bash
docker-compose exec celery celery -A config inspect active
```

### コンテナの再起動

```bash
# 全サービス再起動
docker-compose restart

# 特定のサービスのみ
docker-compose restart web
docker-compose restart celery
```

---

## 📊 動作確認チェックリスト

- [ ] Docker Desktopが起動している
- [ ] `.env`ファイルにOpenAI APIキーを設定した
- [ ] `./setup.sh`が正常に完了した
- [ ] http://localhost:8000 にアクセスできる
- [ ] 管理画面にログインできる
- [ ] 商品カテゴリを作成できる
- [ ] 商品を作成できる
- [ ] 商品ナレッジ（URL/PDF/テキスト）を追加できる
- [ ] 企業情報を作成し、スクレイピングが動作する
- [ ] CSVをアップロードして分析できる（オプション）
- [ ] トークスクリプトが生成される
- [ ] PowerPointファイルが生成され、ダウンロードできる
- [ ] 商談結果を記録できる

---

## 🔧 開発用コマンド

### Djangoシェル

```bash
docker-compose exec web python manage.py shell
```

### マイグレーション作成

```bash
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

### 静的ファイル収集

```bash
docker-compose exec web python manage.py collectstatic --noinput
```

### スーパーユーザー作成

```bash
docker-compose exec web python manage.py createsuperuser
```

---

## 📝 テストデータの例

### サンプル企業URL

- https://www.cybozu.co.jp/
- https://www.sansan.com/
- https://www.freee.co.jp/

### サンプルCSVデータ

```csv
顧客名,業界,従業員数,売上,課題
株式会社A,製造業,500,1000000000,生産効率の改善
株式会社B,IT,100,500000000,リモートワーク対応
株式会社C,小売,1000,5000000000,在庫管理の最適化
```

---

## 🆘 サポート

問題が発生した場合：

1. ログを確認: `docker-compose logs -f`
2. GitHubのIssuesに報告
3. `AIdocs/`ディレクトリのドキュメントを参照

---

## 🎯 次のステップ

動作確認が完了したら：

1. 実際の商品データを登録
2. プロンプトテンプレートをカスタマイズ
3. システム設定を調整
4. チームメンバーのアカウントを作成
5. 実際の顧客データでテスト

