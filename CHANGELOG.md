# 変更履歴

## [1.1.0] - 2025-10-29

### 追加機能

#### バックエンド
- **PDF処理機能** (`backend/apps/products/processors.py`)
  - PyPDF2とpdfplumberによる高精度テキスト抽出
  - 自動チャンク分割機能
  - URLからのコンテンツ取得
  - AI構造化処理

- **CSV分析タスク** (`backend/apps/analysis/tasks.py`)
  - pandasによるCSV解析
  - OpenAI GPT-4oによるAI分析
  - 基本統計情報自動取得
  - カスタムプロンプト対応
  - バッチ処理機能

- **商品ナレッジ処理タスク** (`backend/apps/products/tasks.py`)
  - PDF/URL/テキストの非同期処理
  - バッチ処理対応
  - 自動リトライ機能

#### API エンドポイント
全アプリに完全なDRF ViewSets実装：

- **CompanyViewSet**
  - 企業情報のCRUD操作
  - スクレイピング実行エンドポイント
  - 統計情報取得

- **ProductViewSet / ProductCategoryViewSet / ProductKnowledgeViewSet**
  - 商品マスターの完全管理
  - ナレッジ管理とバッチ処理
  - 再処理機能

- **CSVUploadViewSet / AnalysisViewSet**
  - CSVアップロードと分析実行
  - カスタムプロンプト対応
  - 分析結果の取得

- **TalkScriptViewSet / SalesOutcomeViewSet / TrainingSessionViewSet**
  - トークスクリプト生成・再生成
  - 商談結果記録とAI学習
  - トレーニングセッション管理
  - 統計情報取得

- **ExportViewSet**
  - PowerPoint生成
  - ファイルダウンロード

#### シリアライザ
全モデルの完全なシリアライザ実装：
- 一覧用・詳細用の最適化
- 入力バリデーション
- ネストされたデータ対応
- カスタムフィールド（ファイルサイズ、関連データなど）

#### フロントエンドUI
新規テンプレート：
- `proposal/create.html`
  - 企業情報入力画面
  - ステップインジケーター
  - リアルタイムバリデーション
  - スクレイピング進捗表示

- `proposal/script_generate.html`
  - CSV任意アップロード
  - セクション選択機能
  - リアルタイム分析進捗表示

- `proposal/training.html`
  - 2カラムレイアウト（企業情報/分析 | トークスクリプト）
  - トレーニングタイマー
  - 商品情報表示
  - リアルタイムデータ読み込み

### 改善
- URLルーティングの最適化
- エラーハンドリングの強化
- ドキュメントの更新

### ドキュメント
- `AIdocs/99_implementation_status.md` 更新
- `CHANGELOG.md` 追加

---

## [1.0.0] - 2025-10-29

### 初回リリース

#### 基盤機能
- Docker環境構築
- Django 5.0プロジェクト初期化
- PostgreSQL 16データベース
- Redis 7キャッシュ/ブローカー
- Celery非同期タスクキュー

#### 認証・権限システム
- カスタムユーザーモデル
- 3つの役割（管理者/営業マネージャー/営業担当者）
- ログイン/ログアウト機能
- ユーザー活動ログ

#### システム設定・プロンプト管理
- SystemSettings（シングルトン）
- PromptTemplate（バージョン管理）
- 管理画面カスタマイズ

#### 商品管理
- Product, ProductCategory, ProductKnowledge モデル
- URL/PDF/テキスト入力対応
- 管理画面での商品登録・編集

#### 企業情報管理
- Company モデル
- Webスクレイピング（BeautifulSoup4, trafilatura）
- robots.txt尊重
- AIによる情報構造化
- 非同期処理（Celery）

#### CSV分析
- CSVUpload, Analysis モデル
- オプション機能
- CSV有無による条件分岐

#### 商品マッチング
- ProductMatcher実装
- AIによる適合度判定
- マッチング理由生成

#### トークスクリプト生成
- TalkScript モデル
- セクション選択機能
- CSV有無対応
- 商品情報組み込み
- 商談結果学習機能

#### PowerPoint出力
- python-pptx実装
- セクション別スライド作成
- 企業情報・商品情報スライド
- ダウンロード機能

#### 商談結果管理
- SalesOutcome モデル
- フィードバック記録
- AI学習データ活用

#### UI
- ベーステンプレート
- ログイン画面
- ダッシュボード

#### ドキュメント
- README.md
- QUICK_START.md
- AIdocsディレクトリ（6ファイル）
- setup.shスクリプト

