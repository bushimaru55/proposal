from django.db import models
from django.core.validators import FileExtensionValidator
from django.conf import settings
import pandas as pd


class CSVUpload(models.Model):
    """CSVアップロード履歴"""
    
    file = models.FileField(
        upload_to='uploads/csv/%Y/%m/%d/',
        validators=[FileExtensionValidator(allowed_extensions=['csv', 'txt'])],
        verbose_name="CSVファイル"
    )
    file_name = models.CharField(max_length=255, verbose_name="ファイル名")
    file_size = models.IntegerField(verbose_name="ファイルサイズ（バイト）")
    row_count = models.IntegerField(null=True, blank=True, verbose_name="行数")
    column_count = models.IntegerField(null=True, blank=True, verbose_name="列数")
    
    # アップロード者
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='csv_uploads',
        verbose_name="アップロード者"
    )
    
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="アップロード日時")
    
    class Meta:
        verbose_name = "CSVアップロード"
        verbose_name_plural = "CSVアップロード"
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.file_name} ({self.uploaded_at})"
    
    def save(self, *args, **kwargs):
        if not self.pk and self.file:  # 新規作成時のみ
            self.file_name = self.file.name
            self.file_size = self.file.size
            
            try:
                # pandasでCSV解析
                df = pd.read_csv(self.file)
                self.row_count = len(df)
                self.column_count = len(df.columns)
            except Exception as e:
                # エラーが発生しても保存は継続
                self.row_count = 0
                self.column_count = 0
        
        super().save(*args, **kwargs)


class Analysis(models.Model):
    """AI分析結果"""
    
    STATUS_CHOICES = [
        ('pending', '処理待ち'),
        ('processing', '処理中'),
        ('completed', '完了'),
        ('failed', '失敗'),
    ]
    
    # 関連
    csv_upload = models.ForeignKey(
        CSVUpload,
        on_delete=models.CASCADE,
        related_name='analyses',
        verbose_name="CSVアップロード"
    )
    
    # プロンプト
    prompt = models.TextField(verbose_name="分析プロンプト")
    
    # 結果
    result = models.TextField(blank=True, verbose_name="分析結果")
    
    # AI情報
    model_used = models.CharField(max_length=50, blank=True, verbose_name="使用モデル")
    token_count = models.IntegerField(null=True, blank=True, verbose_name="使用トークン数")
    
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
        related_name='analyses',
        verbose_name="実行者"
    )
    
    # タイムスタンプ
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="完了日時")
    
    class Meta:
        verbose_name = "分析結果"
        verbose_name_plural = "分析結果"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"分析 {self.id} - {self.get_status_display()}"

