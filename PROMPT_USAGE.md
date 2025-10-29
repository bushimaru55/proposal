# 📋 プロンプト使用箇所の詳細分析

## 📊 まとめ

**プロンプトが使用されている箇所: 7箇所**

| # | ファイル | 機能 | プロンプト種類 | カスタマイズ可能 |
|---|---------|------|---------------|-----------------|
| 1 | `apps/companies/tasks.py` | 企業情報構造化 | ハードコード | ❌ |
| 2 | `apps/products/processors.py` | 商品情報抽出 | ハードコード | ❌ |
| 3 | `apps/products/matching.py` | 商品マッチング | ハードコード | ❌ |
| 4 | `apps/sales/script_generator.py` | トークスクリプト生成 | ハードコード | ❌ |
| 5 | `apps/analysis/tasks.py` | CSV分析 | PromptTemplate | ✅ |
| 6 | `apps/core/views.py` (接続テスト) | APIテスト | ハードコード | ❌ |
| 7 | `apps/core/views.py` (チャット) | AIチャット | ハードコード | ❌ |

