# データベーススキーマ

## ER図概要

```
User (accounts_user)
  ↓ 1:N
UserActivityLog (accounts_useractivitylog)

User
  ↓ 1:N
CSVUpload (analysis_csvupload)
  ↓ 1:N
Analysis (analysis_analysis)

Company (companies_company)
  ← N:1
TalkScript (sales_talkscript)
  → N:1
Analysis (nullable)

TalkScript
  ↓ 1:N
ProposalProductLink (sales_proposalproductlink)
  → N:1
Product (products_product)

TalkScript
  ↓ 1:N
SalesOutcome (sales_salesoutcome)

TalkScript
  ↓ 1:N
TrainingSession (sales_trainingsession)

Product
  ↓ 1:N
ProductKnowledge (products_productknowledge)

TalkScript
  ↓ 1:N
ExportHistory (exports_exporthistory)
```

## テーブル詳細

### accounts_user（ユーザー）
| カラム名 | 型 | 説明 | 制約 |
|---------|---|------|------|
| id | BigInt | 主キー | PK |
| username | VARCHAR(150) | ユーザー名 | UNIQUE, NOT NULL |
| email | VARCHAR(254) | メールアドレス | |
| password | VARCHAR(128) | パスワード（ハッシュ化） | NOT NULL |
| first_name | VARCHAR(150) | 名 | |
| last_name | VARCHAR(150) | 姓 | |
| role | VARCHAR(20) | 役割 | NOT NULL |
| department | VARCHAR(100) | 部署 | |
| employee_id | VARCHAR(50) | 社員番号 | UNIQUE |
| phone_number | VARCHAR(20) | 電話番号 | |
| is_active | BOOLEAN | 有効フラグ | DEFAULT TRUE |
| is_staff | BOOLEAN | スタッフフラグ | DEFAULT FALSE |
| is_superuser | BOOLEAN | スーパーユーザーフラグ | DEFAULT FALSE |
| last_login_ip | INET | 最終ログインIP | |
| last_login | TIMESTAMP | 最終ログイン日時 | |
| date_joined | TIMESTAMP | 登録日時 | NOT NULL |
| created_at | TIMESTAMP | 作成日時 | NOT NULL |
| updated_at | TIMESTAMP | 更新日時 | NOT NULL |

**インデックス:**
- username (UNIQUE)
- email
- employee_id (UNIQUE)

### accounts_useractivitylog（ユーザー活動ログ）
| カラム名 | 型 | 説明 | 制約 |
|---------|---|------|------|
| id | BigInt | 主キー | PK |
| user_id | BigInt | ユーザーID | FK |
| action_type | VARCHAR(20) | アクションタイプ | NOT NULL |
| target_model | VARCHAR(100) | 対象モデル | |
| target_id | INT | 対象ID | |
| description | TEXT | 説明 | |
| ip_address | INET | IPアドレス | |
| user_agent | TEXT | ユーザーエージェント | |
| created_at | TIMESTAMP | 実行日時 | NOT NULL |

**インデックス:**
- (user_id, created_at DESC)
- (action_type, created_at DESC)

### core_systemsettings（システム設定）
| カラム名 | 型 | 説明 | 制約 |
|---------|---|------|------|
| id | BigInt | 主キー | PK |
| singleton_id | INT | シングルトンID | UNIQUE, DEFAULT 1 |
| max_csv_file_size_mb | INT | CSV最大サイズ | DEFAULT 10 |
| default_ai_model | VARCHAR(50) | デフォルトAIモデル | DEFAULT 'gpt-4o' |
| ai_temperature | FLOAT | Temperature | DEFAULT 0.7 |
| scraping_enabled | BOOLEAN | スクレイピング有効 | DEFAULT TRUE |
| updated_by_id | BigInt | 更新者ID | FK |
| updated_at | TIMESTAMP | 更新日時 | NOT NULL |

### core_prompttemplate（プロンプトテンプレート）
| カラム名 | 型 | 説明 | 制約 |
|---------|---|------|------|
| id | BigInt | 主キー | PK |
| name | VARCHAR(200) | テンプレート名 | UNIQUE, NOT NULL |
| template_type | VARCHAR(50) | テンプレートタイプ | NOT NULL |
| description | TEXT | 説明 | |
| system_prompt | TEXT | システムプロンプト | NOT NULL |
| user_prompt_template | TEXT | ユーザープロンプト | NOT NULL |
| version | INT | バージョン | DEFAULT 1 |
| is_active | BOOLEAN | 有効フラグ | DEFAULT TRUE |
| is_default | BOOLEAN | デフォルトフラグ | DEFAULT FALSE |
| created_by_id | BigInt | 作成者ID | FK |
| updated_by_id | BigInt | 更新者ID | FK |
| created_at | TIMESTAMP | 作成日時 | NOT NULL |
| updated_at | TIMESTAMP | 更新日時 | NOT NULL |

**インデックス:**
- name (UNIQUE)
- (template_type, is_default)

### products_product（商品）
| カラム名 | 型 | 説明 | 制約 |
|---------|---|------|------|
| id | BigInt | 主キー | PK |
| name | VARCHAR(255) | 商品名 | NOT NULL |
| code | VARCHAR(50) | 商品コード | UNIQUE, NOT NULL |
| category_id | BigInt | カテゴリID | FK |
| short_description | TEXT | 短い説明 | NOT NULL |
| full_description | TEXT | 詳細説明 | |
| target_industries | TEXT[] | 対象業界 | ARRAY |
| pain_points_solved | TEXT[] | 解決する課題 | ARRAY |
| key_features | JSONB | 主要機能 | |
| pricing_model | VARCHAR(100) | 価格モデル | |
| price_range | VARCHAR(200) | 価格帯 | |
| is_active | BOOLEAN | 有効フラグ | DEFAULT TRUE |
| priority | INT | 優先度 | DEFAULT 0 |
| created_at | TIMESTAMP | 作成日時 | NOT NULL |
| updated_at | TIMESTAMP | 更新日時 | NOT NULL |

**インデックス:**
- code (UNIQUE)
- priority DESC

### companies_company（企業情報）
| カラム名 | 型 | 説明 | 制約 |
|---------|---|------|------|
| id | BigInt | 主キー | PK |
| url | VARCHAR(200) | 企業URL | UNIQUE, NOT NULL |
| domain | VARCHAR(255) | ドメイン | NOT NULL |
| company_name | VARCHAR(255) | 企業名 | |
| business_description | TEXT | 事業内容 | |
| industry | VARCHAR(100) | 業界 | |
| key_services | TEXT[] | 主要サービス | ARRAY |
| pain_points | JSONB | 推定される課題 | |
| scrape_status | VARCHAR(20) | スクレイピング状態 | NOT NULL |
| scraped_at | TIMESTAMP | 取得日時 | |
| created_at | TIMESTAMP | 作成日時 | NOT NULL |

**インデックス:**
- url (UNIQUE)
- industry
- scraped_at DESC

### analysis_csvupload（CSVアップロード）
| カラム名 | 型 | 説明 | 制約 |
|---------|---|------|------|
| id | BigInt | 主キー | PK |
| file | VARCHAR(100) | ファイルパス | NOT NULL |
| file_name | VARCHAR(255) | ファイル名 | NOT NULL |
| file_size | INT | ファイルサイズ | NOT NULL |
| row_count | INT | 行数 | |
| column_count | INT | 列数 | |
| uploaded_by_id | BigInt | アップロード者ID | FK, NOT NULL |
| uploaded_at | TIMESTAMP | アップロード日時 | NOT NULL |

**インデックス:**
- uploaded_by_id
- uploaded_at DESC

### analysis_analysis（分析結果）
| カラム名 | 型 | 説明 | 制約 |
|---------|---|------|------|
| id | BigInt | 主キー | PK |
| csv_upload_id | BigInt | CSVアップロードID | FK, NOT NULL |
| prompt | TEXT | 分析プロンプト | NOT NULL |
| result | TEXT | 分析結果 | |
| model_used | VARCHAR(50) | 使用モデル | |
| token_count | INT | トークン数 | |
| status | VARCHAR(20) | ステータス | NOT NULL |
| created_by_id | BigInt | 実行者ID | FK, NOT NULL |
| created_at | TIMESTAMP | 作成日時 | NOT NULL |
| completed_at | TIMESTAMP | 完了日時 | |

**インデックス:**
- csv_upload_id
- created_by_id
- status
- created_at DESC

### sales_talkscript（トークスクリプト）
| カラム名 | 型 | 説明 | 制約 |
|---------|---|------|------|
| id | BigInt | 主キー | PK |
| analysis_id | BigInt | 分析結果ID | FK, NULLABLE |
| company_id | BigInt | 企業情報ID | FK, NOT NULL |
| template_id | BigInt | テンプレートID | FK |
| script_sections | JSONB | スクリプトセクション | NOT NULL |
| selected_sections | TEXT[] | 選択されたセクション | ARRAY |
| model_used | VARCHAR(50) | 使用モデル | NOT NULL |
| total_tokens | INT | トークン数 | |
| generation_time | FLOAT | 生成時間 | |
| status | VARCHAR(20) | ステータス | NOT NULL |
| version | INT | バージョン | DEFAULT 1 |
| created_by_id | BigInt | 作成者ID | FK, NOT NULL |
| created_at | TIMESTAMP | 作成日時 | NOT NULL |
| updated_at | TIMESTAMP | 更新日時 | NOT NULL |

**インデックス:**
- company_id
- analysis_id
- created_by_id
- created_at DESC

### sales_proposalproductlink（提案商品リンク）
| カラム名 | 型 | 説明 | 制約 |
|---------|---|------|------|
| id | BigInt | 主キー | PK |
| talk_script_id | BigInt | トークスクリプトID | FK, NOT NULL |
| product_id | BigInt | 商品ID | FK, NOT NULL |
| relevance_score | FLOAT | 関連性スコア | DEFAULT 0.0 |
| matching_reasons | TEXT[] | マッチング理由 | ARRAY |
| proposal_order | INT | 提案順序 | DEFAULT 1 |
| created_at | TIMESTAMP | 作成日時 | NOT NULL |

**制約:**
- UNIQUE (talk_script_id, product_id)

**インデックス:**
- (talk_script_id, proposal_order)

### sales_salesoutcome（商談結果）
| カラム名 | 型 | 説明 | 制約 |
|---------|---|------|------|
| id | BigInt | 主キー | PK |
| talk_script_id | BigInt | トークスクリプトID | FK, NOT NULL |
| outcome | VARCHAR(20) | 結果 | NOT NULL |
| what_worked | TEXT | うまくいった点 | |
| what_didnt_work | TEXT | 改善が必要な点 | |
| customer_objections | JSONB | 顧客の懸念点 | |
| meeting_date | DATE | 商談日 | |
| used_for_training | BOOLEAN | 学習データとして使用 | DEFAULT TRUE |
| recorded_by_id | BigInt | 記録者ID | FK, NOT NULL |
| created_at | TIMESTAMP | 登録日時 | NOT NULL |
| updated_at | TIMESTAMP | 更新日時 | NOT NULL |

**インデックス:**
- talk_script_id
- outcome
- meeting_date
- created_at DESC

### exports_exporthistory（エクスポート履歴）
| カラム名 | 型 | 説明 | 制約 |
|---------|---|------|------|
| id | BigInt | 主キー | PK |
| talk_script_id | BigInt | トークスクリプトID | FK, NOT NULL |
| export_type | VARCHAR(10) | エクスポート形式 | NOT NULL |
| file_path | VARCHAR(100) | ファイルパス | |
| file_size | INT | ファイルサイズ | |
| status | VARCHAR(20) | ステータス | NOT NULL |
| created_by_id | BigInt | 実行者ID | FK, NOT NULL |
| created_at | TIMESTAMP | 作成日時 | NOT NULL |
| completed_at | TIMESTAMP | 完了日時 | |

**インデックス:**
- talk_script_id
- created_by_id
- created_at DESC

## パフォーマンス最適化

### インデックス戦略
- 外部キーには自動的にインデックス作成
- WHERE句で頻繁に使用されるカラムにインデックス
- ORDER BY句で使用されるカラムにインデックス
- 複合インデックスの活用

### クエリ最適化
- select_related / prefetch_related の活用
- N+1問題の回避
- 不要なカラムの除外（only/defer）
- バッチ処理の活用

## バックアップ戦略

### データベース
- 日次フルバックアップ
- 継続的なWALアーカイブ
- ポイントインタイムリカバリ対応

### ファイル
- メディアファイルの定期バックアップ
- 世代管理（7日分保持）

