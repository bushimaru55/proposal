from django.db import models
from django.conf import settings


class ExportHistory(models.Model):
    """エクスポート履歴"""
    
    EXPORT_TYPES = [
        ('pptx', 'PowerPoint'),
        ('pdf', 'PDF'),
        ('docx', 'Word'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '処理待ち'),
        ('processing', '処理中'),
        ('completed', '完了'),
        ('failed', '失敗'),
    ]
    
    # 関連
    talk_script = models.ForeignKey(
        'sales.TalkScript',
        on_delete=models.CASCADE,
        related_name='exports',
        verbose_name="トークスクリプト"
    )
    
    # エクスポート設定
    export_type = models.CharField(
        max_length=10,
        choices=EXPORT_TYPES,
        default='pptx',
        verbose_name="エクスポート形式"
    )
    
    # ファイル情報
    file_path = models.FileField(
        upload_to='exports/%Y/%m/%d/',
        blank=True,
        verbose_name="ファイルパス"
    )
    file_size = models.IntegerField(null=True, blank=True, verbose_name="ファイルサイズ（バイト）")
    
    # ステータス
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="ステータス"
    )
    error_message = models.TextField(blank=True, verbose_name="エラーメッセージ")
    
    # 実行者
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='exports',
        verbose_name="実行者"
    )
    
    # タイムスタンプ
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="完了日時")
    
    class Meta:
        verbose_name = "エクスポート履歴"
        verbose_name_plural = "エクスポート履歴"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_export_type_display()} - {self.talk_script.company.company_name}"

