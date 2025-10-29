"""
トークスクリプト生成のCeleryタスク
"""
from celery import shared_task
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def generate_talk_script_async(self, company_id, selected_sections, analysis_id=None):
    """
    商品マッチングを含むトークスクリプト生成（非同期）
    
    Args:
        company_id: 企業ID
        selected_sections: 生成するセクションのリスト
        analysis_id: CSV分析結果ID（オプション）
    """
    from apps.companies.models import Company
    from apps.analysis.models import Analysis
    from apps.products.models import Product
    from apps.products.matching import ProductMatcher
    from apps.sales.script_generator import TalkScriptGenerator
    from apps.sales.models import TalkScript, ProposalProductLink
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    try:
        # 進捗: 0%
        self.update_state(state='PROGRESS', meta={'progress': 0, 'status': '準備中'})
        
        # データ取得
        company = Company.objects.get(id=company_id)
        analysis = Analysis.objects.get(id=analysis_id) if analysis_id else None
        
        # 進捗: 20% - 商品マッチング
        self.update_state(state='PROGRESS', meta={'progress': 20, 'status': '最適な商品を選択中'})
        
        # 有効な商品を取得
        available_products = Product.objects.filter(is_active=True).order_by('-priority')
        
        # 商品マッチング実行
        matcher = ProductMatcher()
        analysis_result = analysis.result if analysis else None
        matching_result = matcher.match_products(
            company,
            available_products,
            analysis_result
        )
        
        # 進捗: 50% - トークスクリプト生成
        self.update_state(state='PROGRESS', meta={'progress': 50, 'status': 'トークスクリプト生成中'})
        
        # 選択された商品情報を整形
        selected_products = []
        for rec in matching_result.get('recommended_products', []):
            try:
                product = Product.objects.get(id=rec['product_id'])
                selected_products.append({
                    'product': product,
                    'relevance_score': rec['relevance_score'],
                    'matching_reasons': rec['matching_reasons'],
                    'proposal_angle': rec['proposal_angle']
                })
            except Product.DoesNotExist:
                logger.warning(f"商品が見つかりません: {rec['product_id']}")
                continue
        
        # トークスクリプト生成
        generator = TalkScriptGenerator()
        script_result = generator.generate_full_script(
            company,
            selected_products,
            selected_sections,
            analysis
        )
        
        # 進捗: 80% - 保存
        self.update_state(state='PROGRESS', meta={'progress': 80, 'status': '保存中'})
        
        # デフォルトユーザーを取得（システム生成の場合）
        # 実際の実装では、タスク呼び出し時にuser_idを渡すべき
        default_user = User.objects.filter(is_staff=True).first()
        
        # TalkScript保存
        talk_script = TalkScript.objects.create(
            analysis=analysis,
            company=company,
            script_sections=script_result['script_sections'],
            selected_sections=selected_sections,
            model_used=script_result['model_used'],
            total_tokens=script_result['total_tokens'],
            generation_time=script_result['generation_time'],
            status='active',
            created_by=default_user
        )
        
        # 商品リンク保存
        for idx, prod_info in enumerate(selected_products, 1):
            ProposalProductLink.objects.create(
                talk_script=talk_script,
                product=prod_info['product'],
                relevance_score=prod_info['relevance_score'],
                matching_reasons=prod_info['matching_reasons'],
                proposal_order=idx
            )
        
        # 完了
        self.update_state(state='SUCCESS', meta={'progress': 100, 'status': '完了'})
        
        logger.info(f"トークスクリプト生成完了: {talk_script.id}")
        
        return {
            'status': 'success',
            'talk_script_id': talk_script.id,
            'products_count': len(selected_products)
        }
        
    except Exception as e:
        logger.error(f"トークスクリプト生成エラー: {e}")
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise

