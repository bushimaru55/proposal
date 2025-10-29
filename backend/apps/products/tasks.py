"""
商品管理の非同期タスク
"""
import logging
from celery import shared_task
from django.core.files.base import ContentFile

from .models import ProductKnowledge
from .processors import process_product_knowledge

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_product_knowledge_task(self, knowledge_id: int):
    """
    商品ナレッジの非同期処理
    PDF/URL/テキストから情報を抽出して構造化
    
    Args:
        knowledge_id: ProductKnowledgeのID
    """
    try:
        knowledge = ProductKnowledge.objects.select_related('product').get(id=knowledge_id)
        
        logger.info(f"Processing ProductKnowledge #{knowledge_id} ({knowledge.source_type})")
        
        # ソースに応じて content を決定
        if knowledge.source_type == 'pdf' and knowledge.pdf_file:
            content = knowledge.pdf_file.path
        elif knowledge.source_type == 'url' and knowledge.source_url:
            content = knowledge.source_url
        elif knowledge.source_type == 'text' and knowledge.raw_text:
            content = knowledge.raw_text
        else:
            raise ValueError(f"Invalid source configuration for knowledge #{knowledge_id}")
        
        # 処理実行
        structured_data = process_product_knowledge(
            source_type=knowledge.source_type,
            content=content,
            product_name=knowledge.product.name
        )
        
        # 結果を保存
        knowledge.structured_data = structured_data
        knowledge.processing_status = 'completed'
        knowledge.save(update_fields=['structured_data', 'processing_status', 'updated_at'])
        
        logger.info(f"Successfully processed ProductKnowledge #{knowledge_id}")
        return {
            'status': 'success',
            'knowledge_id': knowledge_id,
            'product_name': knowledge.product.name
        }
    
    except ProductKnowledge.DoesNotExist:
        logger.error(f"ProductKnowledge #{knowledge_id} not found")
        return {'status': 'error', 'message': 'Knowledge not found'}
    
    except Exception as e:
        logger.error(f"Error processing ProductKnowledge #{knowledge_id}: {e}")
        
        # リトライ処理
        try:
            knowledge = ProductKnowledge.objects.get(id=knowledge_id)
            knowledge.processing_status = 'failed'
            knowledge.save(update_fields=['processing_status', 'updated_at'])
        except:
            pass
        
        # タスクをリトライ
        raise self.retry(exc=e, countdown=60 * (self.request.retries + 1))


@shared_task
def batch_process_product_knowledge(knowledge_ids: list):
    """
    複数の商品ナレッジを一括処理
    
    Args:
        knowledge_ids: ProductKnowledgeのIDリスト
    """
    results = []
    for knowledge_id in knowledge_ids:
        result = process_product_knowledge_task.delay(knowledge_id)
        results.append({
            'knowledge_id': knowledge_id,
            'task_id': result.id
        })
    
    logger.info(f"Batch processing initiated for {len(knowledge_ids)} knowledge items")
    return results


@shared_task
def cleanup_old_processing_tasks():
    """
    古い処理中ステータスをクリーンアップ（定期実行）
    24時間以上 'processing' のままの場合は 'failed' に変更
    """
    from django.utils import timezone
    from datetime import timedelta
    
    threshold = timezone.now() - timedelta(hours=24)
    
    stale_knowledge = ProductKnowledge.objects.filter(
        processing_status='processing',
        updated_at__lt=threshold
    )
    
    count = stale_knowledge.update(processing_status='failed')
    
    if count > 0:
        logger.warning(f"Cleaned up {count} stale processing tasks")
    
    return {'cleaned_up': count}

