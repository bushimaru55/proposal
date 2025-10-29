from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone


class Company(models.Model):
    """企業情報（Webスクレイピング結果）"""
    
    # 基本情報
    url = models.URLField(unique=True, verbose_name="企業URL")
    domain = models.CharField(max_length=255, verbose_name="ドメイン")
    
    # スクレイピング結果
    title = models.CharField(max_length=500, blank=True, verbose_name="ページタイトル")
    meta_description = models.TextField(blank=True, verbose_name="メタディスクリプション")
    main_content = models.TextField(blank=True, verbose_name="メインコンテンツ")
    
    # AI抽出情報
    company_name = models.CharField(max_length=255, blank=True, verbose_name="企業名")
    business_description = models.TextField(blank=True, verbose_name="事業内容")
    industry = models.CharField(max_length=100, blank=True, verbose_name="業界")
    key_services = ArrayField(
        models.CharField(max_length=200),
        blank=True,
        default=list,
        verbose_name="主要サービス"
    )
    target_market = models.TextField(blank=True, verbose_name="ターゲット市場")
    
    # AI生成サマリー
    ai_summary = models.TextField(blank=True, verbose_name="AI生成サマリー")
    pain_points = models.JSONField(
        default=list,
        blank=True,
        verbose_name="推定される課題"
    )
    
    # メタデータ
    scrape_status = models.CharField(
        max_length=20,
        choices=[
            ('success', '成功'),
            ('partial', '部分的'),
            ('failed', '失敗')
        ],
        default='success',
        verbose_name="スクレイピング状態"
    )
    scraped_at = models.DateTimeField(auto_now=True, verbose_name="取得日時")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    
    class Meta:
        verbose_name = "企業情報"
        verbose_name_plural = "企業情報"
        ordering = ['-scraped_at']
    
    def __str__(self):
        return f"{self.company_name or self.domain}"
    
    def needs_update(self, days=30):
        """更新が必要か判定"""
        if not self.scraped_at:
            return True
        age = timezone.now() - self.scraped_at
        return age.days > days

