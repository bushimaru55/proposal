from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.conf import settings


class TalkScript(models.Model):
    """生成されたトークスクリプト"""
    
    STATUS_CHOICES = [
        ('draft', '下書き'),
        ('active', '使用中'),
        ('archived', 'アーカイブ'),
    ]
    
    # 関連（CSVはオプション）
    analysis = models.ForeignKey(
        'analysis.Analysis',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="分析結果"
    )
    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        verbose_name="企業情報"
    )
    template = models.ForeignKey(
        'core.PromptTemplate',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="使用テンプレート"
    )
    
    # 生成されたスクリプト（セクション別）
    script_sections = models.JSONField(
        default=dict,
        verbose_name="スクリプトセクション"
    )
    
    # 選択されたセクション
    selected_sections = ArrayField(
        models.CharField(max_length=50),
        default=list,
        blank=True,
        verbose_name="選択されたセクション"
    )
    
    # AI情報
    model_used = models.CharField(max_length=50, verbose_name="使用モデル")
    total_tokens = models.IntegerField(null=True, blank=True, verbose_name="トークン数")
    generation_time = models.FloatField(null=True, blank=True, verbose_name="生成時間(秒)")
    
    # ステータス
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name="ステータス"
    )
    
    # メタデータ
    version = models.IntegerField(default=1, verbose_name="バージョン")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='talk_scripts',
        verbose_name="作成者"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")
    
    class Meta:
        verbose_name = "トークスクリプト"
        verbose_name_plural = "トークスクリプト"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.company.company_name} - v{self.version}"


class ProposalProductLink(models.Model):
    """提案と商品の紐付け"""
    
    talk_script = models.ForeignKey(
        TalkScript,
        on_delete=models.CASCADE,
        related_name='proposed_products',
        verbose_name="トークスクリプト"
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        verbose_name="商品"
    )
    
    # マッチング情報
    relevance_score = models.FloatField(
        default=0.0,
        verbose_name="関連性スコア"
    )
    matching_reasons = ArrayField(
        models.TextField(),
        blank=True,
        default=list,
        verbose_name="マッチング理由"
    )
    
    # 提案順序
    proposal_order = models.IntegerField(
        default=1,
        verbose_name="提案順序"
    )
    
    # 使用されたナレッジ
    used_knowledge = models.ManyToManyField(
        'products.ProductKnowledge',
        blank=True,
        verbose_name="使用ナレッジ"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    
    class Meta:
        verbose_name = "提案商品"
        verbose_name_plural = "提案商品"
        ordering = ['talk_script', 'proposal_order']
        unique_together = ['talk_script', 'product']
    
    def __str__(self):
        return f"{self.talk_script.company.company_name} → {self.product.name}"


class SalesOutcome(models.Model):
    """商談結果（AI学習用）"""
    
    OUTCOME_CHOICES = [
        ('won', '受注'),
        ('lost', '失注'),
        ('pending', '検討中'),
        ('no_response', '無応答'),
    ]
    
    # 関連
    talk_script = models.ForeignKey(
        TalkScript,
        on_delete=models.CASCADE,
        related_name='outcomes',
        verbose_name="トークスクリプト"
    )
    
    # 結果
    outcome = models.CharField(
        max_length=20,
        choices=OUTCOME_CHOICES,
        verbose_name="結果"
    )
    
    # フィードバック
    what_worked = models.TextField(
        blank=True,
        verbose_name="うまくいった点"
    )
    what_didnt_work = models.TextField(
        blank=True,
        verbose_name="改善が必要な点"
    )
    customer_objections = models.JSONField(
        default=list,
        blank=True,
        verbose_name="顧客の懸念点"
    )
    
    # 詳細情報
    meeting_date = models.DateField(null=True, blank=True, verbose_name="商談日")
    notes = models.TextField(blank=True, verbose_name="その他メモ")
    
    # AI学習用フラグ
    used_for_training = models.BooleanField(
        default=True,
        verbose_name="学習データとして使用"
    )
    
    # 記録者
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sales_outcomes',
        verbose_name="記録者"
    )
    
    # メタデータ
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="登録日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")
    
    class Meta:
        verbose_name = "商談結果"
        verbose_name_plural = "商談結果"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.talk_script.company.company_name} - {self.get_outcome_display()}"


class TrainingSession(models.Model):
    """トレーニングセッション記録"""
    
    talk_script = models.ForeignKey(
        TalkScript,
        on_delete=models.CASCADE,
        related_name='training_sessions',
        verbose_name="トークスクリプト"
    )
    
    # トレーニング内容
    duration_minutes = models.IntegerField(null=True, blank=True, verbose_name="練習時間(分)")
    notes = models.TextField(blank=True, verbose_name="気づき・メモ")
    
    # 自己評価
    self_rating = models.IntegerField(
        null=True,
        blank=True,
        choices=[(i, f"{i}点") for i in range(1, 6)],
        verbose_name="自己評価(1-5)"
    )
    
    # 実施者
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='training_sessions',
        verbose_name="実施者"
    )
    
    trained_at = models.DateTimeField(auto_now_add=True, verbose_name="実施日時")
    
    class Meta:
        verbose_name = "トレーニングセッション"
        verbose_name_plural = "トレーニングセッション"
        ordering = ['-trained_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.talk_script.company.company_name}"

