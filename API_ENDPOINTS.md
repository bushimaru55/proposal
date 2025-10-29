# API エンドポイント一覧

## 概要
本システムは Django REST Framework (DRF) を使用して構築されたRESTful APIを提供します。
すべてのエンドポイントは認証が必要です（`IsAuthenticated` permission）。

## ベースURL
```
http://localhost:8000/api/
```

---

## 🏢 企業情報 (Companies)

### エンドポイント: `/api/companies/`

#### 企業一覧取得
```http
GET /api/companies/
```

**クエリパラメータ:**
- `name` (string): 企業名で部分一致検索
- `industry` (string): 業界で部分一致検索
- `scraping_status` (choice): スクレイピングステータスでフィルター

**レスポンス例:**
```json
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "name": "株式会社サンプル",
      "website_url": "https://example.com",
      "industry": "IT・ソフトウェア",
      "scraping_status": "completed",
      "created_by_name": "山田太郎",
      "created_at": "2025-10-29T10:00:00Z"
    }
  ]
}
```

#### 企業詳細取得
```http
GET /api/companies/{id}/
```

#### 企業作成（自動スクレイピング開始）
```http
POST /api/companies/
Content-Type: application/json

{
  "name": "株式会社サンプル",
  "website_url": "https://example.com",
  "industry": "IT・ソフトウェア"
}
```

#### 企業情報更新
```http
PUT /api/companies/{id}/
PATCH /api/companies/{id}/
```

#### 企業情報削除
```http
DELETE /api/companies/{id}/
```

#### スクレイピング実行
```http
POST /api/companies/{id}/scrape/

{
  "force_rescrape": false
}
```

#### 統計情報取得
```http
GET /api/companies/stats/
```

**レスポンス例:**
```json
{
  "total": 50,
  "by_status": {
    "pending": {"label": "未処理", "count": 5},
    "processing": {"label": "処理中", "count": 3},
    "completed": {"label": "完了", "count": 40},
    "failed": {"label": "失敗", "count": 2}
  }
}
```

---

## 📦 商品管理 (Products)

### カテゴリ管理: `/api/products/categories/`

#### カテゴリ一覧
```http
GET /api/products/categories/
```

#### カテゴリ作成・更新・削除
```http
POST /api/products/categories/
PUT /api/products/categories/{id}/
PATCH /api/products/categories/{id}/
DELETE /api/products/categories/{id}/
```

### 商品管理: `/api/products/products/`

#### 商品一覧取得
```http
GET /api/products/products/
```

**クエリパラメータ:**
- `name` (string): 商品名で部分一致検索
- `category` (integer): カテゴリIDでフィルター
- `is_active` (boolean): 有効/無効でフィルター

#### 商品詳細取得
```http
GET /api/products/products/{id}/
```

#### 商品のナレッジ一覧取得
```http
GET /api/products/products/{id}/knowledge/
```

#### 商品作成・更新・削除
```http
POST /api/products/products/
PUT /api/products/products/{id}/
PATCH /api/products/products/{id}/
DELETE /api/products/products/{id}/
```

### 商品ナレッジ管理: `/api/products/knowledge/`

#### ナレッジ作成（自動処理開始）
```http
POST /api/products/knowledge/

{
  "product": 1,
  "source_type": "url",
  "source_url": "https://example.com/product"
}
```

または

```http
POST /api/products/knowledge/
Content-Type: multipart/form-data

product: 1
source_type: pdf
pdf_file: [binary]
```

#### ナレッジ再処理
```http
POST /api/products/knowledge/{id}/reprocess/
```

---

## 📊 CSV分析 (Analysis)

### CSVアップロード: `/api/analysis/csv-uploads/`

#### CSV一覧取得
```http
GET /api/analysis/csv-uploads/
```

#### CSVアップロード
```http
POST /api/analysis/csv-uploads/
Content-Type: multipart/form-data

file: [CSV file]
description: "説明文"
```

#### CSV分析実行
```http
POST /api/analysis/csv-uploads/{id}/analyze/

{
  "custom_prompt": "カスタムプロンプト（任意）"
}
```

### 分析結果: `/api/analysis/analyses/`

#### 分析結果一覧
```http
GET /api/analysis/analyses/
```

#### 分析結果詳細
```http
GET /api/analysis/analyses/{id}/
```

#### 新規分析作成
```http
POST /api/analysis/analyses/create_analysis/

{
  "csv_upload_id": 1,
  "custom_prompt": "カスタムプロンプト（任意）"
}
```

---

## 💬 営業管理 (Sales)

### トークスクリプト: `/api/sales/talk-scripts/`

#### トークスクリプト一覧
```http
GET /api/sales/talk-scripts/
```

**クエリパラメータ:**
- `company` (integer): 企業IDでフィルター
- `generation_status` (choice): 生成ステータスでフィルター
- `created_by` (integer): 作成者IDでフィルター

#### トークスクリプト詳細
```http
GET /api/sales/talk-scripts/{id}/
```

#### トークスクリプト生成
```http
POST /api/sales/talk-scripts/generate/

{
  "company_id": 1,
  "analysis_id": 2,  // オプション
  "selected_sections": [
    "opening",
    "problem_identification",
    "proposal",
    "objection_handling",
    "closing"
  ]
}
```

#### トークスクリプト再生成
```http
POST /api/sales/talk-scripts/{id}/regenerate/
```

### 商談結果: `/api/sales/outcomes/`

#### 商談結果一覧
```http
GET /api/sales/outcomes/
```

#### 商談結果記録
```http
POST /api/sales/outcomes/

{
  "talk_script": 1,
  "outcome": "won",
  "meeting_date": "2025-10-29",
  "notes": "商談メモ",
  "what_worked": "うまくいったこと",
  "what_didnt_work": "うまくいかなかったこと",
  "customer_feedback": "顧客のフィードバック",
  "next_action": "次のアクション"
}
```

#### 商談統計
```http
GET /api/sales/outcomes/stats/
```

**レスポンス例:**
```json
{
  "total": 100,
  "by_outcome": {
    "won": {"label": "受注", "count": 45},
    "lost": {"label": "失注", "count": 30},
    "pending": {"label": "保留中", "count": 25}
  },
  "success_rate": 45.00
}
```

### トレーニングセッション: `/api/sales/training-sessions/`

#### トレーニングセッション一覧
```http
GET /api/sales/training-sessions/
```

#### トレーニングセッション記録
```http
POST /api/sales/training-sessions/

{
  "talk_script": 1,
  "duration_minutes": 30,
  "sections_practiced": ["opening", "proposal"],
  "self_assessment": 4,
  "notes": "練習メモ"
}
```

#### 自分の統計
```http
GET /api/sales/training-sessions/my_stats/
```

**レスポンス例:**
```json
{
  "total_sessions": 15,
  "total_minutes": 450,
  "section_counts": {
    "opening": 10,
    "proposal": 12,
    "closing": 8
  }
}
```

---

## 📄 PowerPointエクスポート (Exports)

### エクスポート: `/api/exports/`

#### エクスポート一覧
```http
GET /api/exports/
```

#### PowerPoint生成
```http
POST /api/exports/create_export/

{
  "talk_script_id": 1
}
```

**レスポンス:**
```json
{
  "message": "PowerPoint生成を開始しました",
  "task_id": "abc123...",
  "export_id": 5
}
```

#### PowerPointダウンロード
```http
GET /api/exports/{id}/download/
```

---

## 認証

### ログイン
```http
POST /accounts/login/

{
  "username": "admin",
  "password": "password"
}
```

### ログアウト
```http
POST /accounts/logout/
```

---

## エラーレスポンス

すべてのエラーレスポンスは以下の形式で返されます：

```json
{
  "detail": "エラーメッセージ"
}
```

または

```json
{
  "field_name": ["エラーメッセージ1", "エラーメッセージ2"]
}
```

### HTTPステータスコード
- `200 OK`: 成功
- `201 Created`: 作成成功
- `202 Accepted`: 非同期処理を受け付けた
- `400 Bad Request`: リクエストが不正
- `401 Unauthorized`: 認証が必要
- `403 Forbidden`: 権限がない
- `404 Not Found`: リソースが見つからない
- `500 Internal Server Error`: サーバーエラー

---

## レート制限

現在、レート制限は設定されていませんが、本番環境では設定を推奨します。

---

## ページネーション

一覧取得エンドポイントはページネーションをサポートしています：

```http
GET /api/companies/?page=2&page_size=10
```

**レスポンス:**
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/companies/?page=3",
  "previous": "http://localhost:8000/api/companies/?page=1",
  "results": [...]
}
```

---

## フィルタリング

多くのエンドポイントで`django-filter`によるフィルタリングをサポートしています。

例：
```http
GET /api/products/products/?category=1&is_active=true&name=サンプル
```

---

## 追加情報

- すべてのタイムスタンプはISO 8601形式（UTC）
- ファイルアップロードは`multipart/form-data`形式
- JSON リクエストは`Content-Type: application/json`ヘッダーが必要
- CSRFトークンは`X-CSRFToken`ヘッダーで送信

