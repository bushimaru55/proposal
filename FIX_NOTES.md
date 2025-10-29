# ローカル環境構築時のエラー修正ノート

## 発生したエラーと原因

### 1. django-debug-toolbar のモジュールエラー
**原因:** `development.py`で`django-debug-toolbar`を使おうとしていたが、パッケージがインストールされていない
**修正:** `development.py`の該当部分をコメントアウト

### 2. Company モデルのフィールド不一致
**原因:** ViewsとSerializersが想定しているフィールド名が実際のモデルと異なる

**実際のモデル:** `backend/apps/companies/models.py`
- `url` (website_urlではない)
- `company_name` (nameではない)
- `scrape_status` (scraping_statusではない)
- `created_by`フィールドなし

**必要な修正:**
- ✅ `views.py`: フィールド名を修正
- ✅ `serializers.py`: フィールド名を修正

### 3. ProposalProductLink の参照エラー
**原因:** `ProposalProductLink`は`apps.sales.models`に定義されているが、`apps.products.serializers`からインポートしようとしていた

**修正:** `products/serializers.py`から該当コードを削除

### 4. ProductCategory の display_order フィールドエラー
**原因:** `ProductCategory`モデルに`display_order`フィールドが存在しない

## 推奨アプローチ

現在の状況では、既存のモデル構造が想定と大きく異なるため、以下のアプローチを推奨：

### オプション A: 既存モデルに合わせてViews/Serializersを全面的に修正
- 時間がかかるが、既存のDB構造を維持できる

### オプション B: モデルを設計通りに作り直す
- クリーンな実装が可能
- 移行が必要

### オプション C: 最小限の機能で動作確認を優先
1. 一旦、全てのカスタムViews/Serializersをコメントアウト
2. Django adminのみで動作確認
3. 段階的に機能を追加

## 現状

コンテナは起動しているが、マイグレーション実行前の段階でエラーが発生中。
URLの解決とモデルのインポート時点でエラー。

## 次のステップ提案

1. **短期的解決（動作確認優先）:**
   - カスタムAPI ViewSetを一旦無効化
   - Django admin経由でモデルの動作確認
   - その後、段階的にAPIを有効化

2. **長期的解決：**
   - 全モデル構造を確認
   - Views/Serializers を既存モデルに完全に合わせる
   - または、モデルを設計通りに作り直す

ユーザーにどちらのアプローチを希望するか確認が必要です。

