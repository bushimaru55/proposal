"""
PowerPointエクスポートのCeleryタスク
"""
from celery import shared_task
from django.utils import timezone
from django.conf import settings
import logging
import os

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def generate_powerpoint_async(self, talk_script_id, user_id):
    """
    PowerPoint生成（非同期）
    
    Args:
        talk_script_id: トークスクリプトID
        user_id: 実行ユーザーID
    """
    from apps.sales.models import TalkScript
    from apps.exports.models import ExportHistory
    from apps.exports.pptx_generator import PowerPointGenerator
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    try:
        # 進捗: 0%
        self.update_state(state='PROGRESS', meta={'progress': 0, 'status': '準備中'})
        
        # データ取得
        talk_script = TalkScript.objects.select_related('company').prefetch_related(
            'proposed_products__product'
        ).get(id=talk_script_id)
        
        user = User.objects.get(id=user_id)
        
        # エクスポート履歴作成
        export = ExportHistory.objects.create(
            talk_script=talk_script,
            export_type='pptx',
            status='processing',
            created_by=user
        )
        
        # 進捗: 20%
        self.update_state(state='PROGRESS', meta={'progress': 20, 'status': 'PowerPoint生成中'})
        
        # PowerPoint生成
        generator = PowerPointGenerator()
        prs = generator.generate_from_talk_script(talk_script)
        
        # 進捗: 70%
        self.update_state(state='PROGRESS', meta={'progress': 70, 'status': 'ファイル保存中'})
        
        # ファイル保存
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        filename = f"proposal_{talk_script.company.company_name}_{timestamp}.pptx"
        
        # メディアディレクトリのパスを作成
        export_dir = os.path.join(
            settings.MEDIA_ROOT,
            'exports',
            timezone.now().strftime('%Y/%m/%d')
        )
        os.makedirs(export_dir, exist_ok=True)
        
        file_path = os.path.join(export_dir, filename)
        
        # 保存
        if generator.save(file_path):
            # 相対パスを保存
            relative_path = os.path.relpath(file_path, settings.MEDIA_ROOT)
            
            export.file_path = relative_path
            export.file_size = os.path.getsize(file_path)
            export.status = 'completed'
            export.completed_at = timezone.now()
            export.save()
            
            logger.info(f"PowerPoint生成完了: {export.id}")
            
            # 進捗: 100%
            self.update_state(state='SUCCESS', meta={'progress': 100, 'status': '完了'})
            
            return {
                'status': 'success',
                'export_id': export.id,
                'file_path': relative_path,
                'file_size': export.file_size
            }
        else:
            raise Exception("PowerPoint保存に失敗しました")
        
    except Exception as e:
        logger.error(f"PowerPoint生成エラー: {e}")
        
        # エラー情報を保存
        if 'export' in locals():
            export.status = 'failed'
            export.error_message = str(e)
            export.save()
        
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise

