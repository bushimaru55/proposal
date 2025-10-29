"""
商品マッチング機能
"""
from openai import OpenAI
import json
import logging

logger = logging.getLogger(__name__)


class ProductMatcher:
    """分析結果と企業情報から最適な商品を選択"""
    
    def __init__(self):
        self.client = OpenAI()
    
    def match_products(self, company_info, available_products, analysis_result=None):
        """
        最適な商品を選択
        
        Args:
            company_info: 企業情報（Company モデル）
            available_products: 利用可能な商品リスト（Product モデル）
            analysis_result: CSV分析結果（オプション）
        
        Returns:
            選択された商品とマッチング理由のリスト
        """
        
        # 商品情報を簡潔にまとめる
        products_summary = []
        for product in available_products:
            products_summary.append({
                'id': product.id,
                'name': product.name,
                'code': product.code,
                'description': product.short_description,
                'target_industries': product.target_industries,
                'pain_points_solved': product.pain_points_solved,
                'key_features': [f.get('name', '') for f in product.key_features] if product.key_features else []
            })
        
        # プロンプト構築
        base_prompt = f"""
あなたは商品提案の専門家です。
以下の情報から、顧客に最適な商品を選択してください。

# 提案先企業情報
- 企業名: {company_info.company_name}
- 業界: {company_info.industry}
- 事業内容: {company_info.business_description}
- 推定される課題: {', '.join(company_info.pain_points) if company_info.pain_points else '不明'}
"""
        
        # CSV分析結果がある場合は追加
        if analysis_result:
            base_prompt += f"\n\n# データ分析結果\n{analysis_result[:1500]}"
        
        base_prompt += f"""

# 提案可能な商品リスト
{json.dumps(products_summary, ensure_ascii=False, indent=2)}

---

上記を踏まえて、以下のJSON形式で回答してください：

{{
  "recommended_products": [
    {{
      "product_id": 商品ID,
      "product_name": "商品名",
      "relevance_score": 0.0-1.0（適合度）,
      "matching_reasons": [
        "マッチング理由1",
        "マッチング理由2"
      ],
      "proposal_angle": "この企業への提案切り口"
    }}
  ],
  "proposal_strategy": "全体的な提案戦略"
}}

※最大3商品まで、関連性の高い順に選択してください。
※関連性が低い場合は、無理に選択しないでください。
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",  # マッチングは重要なので高品質モデル
                messages=[
                    {"role": "system", "content": "あなたは顧客のニーズを深く理解し、最適な商品を提案する専門家です。"},
                    {"role": "user", "content": base_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.5
            )
            
            result = json.loads(response.choices[0].message.content)
            logger.info(f"商品マッチング完了: {len(result.get('recommended_products', []))}件")
            return result
            
        except Exception as e:
            logger.error(f"商品マッチングエラー: {e}")
            # フォールバック: 優先度が高い商品を返す
            if available_products:
                return {
                    'recommended_products': [
                        {
                            'product_id': available_products[0].id,
                            'product_name': available_products[0].name,
                            'relevance_score': 0.5,
                            'matching_reasons': ['優先度が高い商品です'],
                            'proposal_angle': '汎用的な提案'
                        }
                    ],
                    'proposal_strategy': 'エラーが発生しました'
                }
            return {
                'recommended_products': [],
                'proposal_strategy': '提案可能な商品がありません'
            }
    
    def get_relevant_knowledge(self, product, top_k=5):
        """
        商品ナレッジから関連情報を取得
        """
        from apps.products.models import ProductKnowledge
        
        knowledge_items = ProductKnowledge.objects.filter(
            product=product,
            is_active=True
        ).order_by('-created_at')[:top_k]
        
        return knowledge_items

