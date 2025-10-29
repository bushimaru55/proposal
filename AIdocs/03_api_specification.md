# API仕様書

## エンドポイント一覧

### 企業情報API

#### POST /api/companies/scrape/
企業情報のスクレイピングを開始

**Request:**
```json
{
  "url": "https://example.com"
}
```

**Response:**
```json
{
  "company_id": 1,
  "task_id": "celery-task-id",
  "status": "processing"
}
```

#### GET /api/companies/{id}/
企業情報の取得

**Response:**
```json
{
  "id": 1,
  "url": "https://example.com",
  "company_name": "株式会社Example",
  "industry": "IT",
  "business_description": "...",
  "scrape_status": "success"
}
```

### 商品API

#### GET /api/products/
商品一覧の取得

**Query Parameters:**
- `is_active`: boolean
- `category`: int
- `search`: string

**Response:**
```json
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "name": "商品A",
      "code": "PROD-001",
      "short_description": "...",
      "is_active": true
    }
  ]
}
```

### 分析API

#### POST /api/analysis/csv/upload/
CSVアップロード

**Request:** multipart/form-data
- `file`: CSV file

**Response:**
```json
{
  "upload_id": 1,
  "file_name": "data.csv",
  "row_count": 100,
  "column_count": 10
}
```

#### POST /api/analysis/analyze/
AI分析実行

**Request:**
```json
{
  "csv_upload_id": 1,
  "prompt": "このデータを分析してください"
}
```

**Response:**
```json
{
  "analysis_id": 1,
  "status": "processing",
  "task_id": "celery-task-id"
}
```

### トークスクリプトAPI

#### POST /api/sales/talk-scripts/generate/
トークスクリプト生成

**Request:**
```json
{
  "company_id": 1,
  "analysis_id": 1,  // optional
  "selected_sections": [
    "opening",
    "problem_identification",
    "solution_proposal",
    "objection_handling",
    "closing"
  ]
}
```

**Response:**
```json
{
  "talk_script_id": 1,
  "status": "processing",
  "task_id": "celery-task-id"
}
```

#### GET /api/sales/talk-scripts/{id}/
トークスクリプトの取得

**Response:**
```json
{
  "id": 1,
  "company": {...},
  "script_sections": {
    "opening": "...",
    "problem_identification": "..."
  },
  "proposed_products": [...]
}
```

### エクスポートAPI

#### POST /api/exports/powerpoint/
PowerPoint生成

**Request:**
```json
{
  "talk_script_id": 1
}
```

**Response:**
```json
{
  "export_id": 1,
  "status": "processing",
  "task_id": "celery-task-id"
}
```

#### GET /api/exports/{id}/download/
PowerPointダウンロード

**Response:** PowerPoint file (application/vnd.openxmlformats-officedocument.presentationml.presentation)

## 認証

Django Session Authentication使用

### ログイン
POST /accounts/login/

### ログアウト
POST /accounts/logout/

## エラーレスポンス

```json
{
  "error": "エラーメッセージ",
  "code": "ERROR_CODE",
  "details": {...}
}
```

## ステータスコード

- 200: 成功
- 201: 作成成功
- 400: リクエストエラー
- 401: 認証エラー
- 403: 権限エラー
- 404: Not Found
- 500: サーバーエラー

