from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.cache import cache
from django.conf import settings


class SystemSettings(models.Model):
    """システム設定（管理者のみ変更可能）"""
    
    # シングルトンパターン用
    singleton_id = models.IntegerField(default=1, unique=True)
    
    # === CSV処理設定 ===
    max_csv_file_size_mb = models.IntegerField(
        default=10,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        verbose_name="CSV最大ファイルサイズ（MB）"
    )
    
    allowed_csv_encodings = models.JSONField(
        default=list,
        blank=True,
        verbose_name="許可するCSVエンコーディング"
    )
    
    # === AI設定 ===
    openai_api_key = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="OpenAI APIキー",
        help_text="OpenAI APIキーを入力してください。空の場合は環境変数から取得します。"
    )
    
    default_ai_model = models.CharField(
        max_length=50,
        default='gpt-4o',
        choices=[
            ('gpt-4o', 'GPT-4o（高品質）'),
            ('gpt-4o-mini', 'GPT-4o Mini（コスト重視）'),
        ],
        verbose_name="デフォルトAIモデル"
    )
    
    ai_temperature = models.FloatField(
        default=0.7,
        validators=[MinValueValidator(0.0), MaxValueValidator(2.0)],
        verbose_name="AIのTemperature"
    )
    
    max_tokens_per_request = models.IntegerField(
        default=4000,
        validators=[MinValueValidator(100), MaxValueValidator(16000)],
        verbose_name="1リクエストあたりの最大トークン数"
    )
    
    daily_token_limit = models.IntegerField(
        default=1000000,
        validators=[MinValueValidator(0)],
        verbose_name="1日のトークン上限"
    )
    
    # AI機能の有効化
    ai_enabled = models.BooleanField(
        default=True,
        verbose_name="AI機能を有効化",
        help_text="AI機能（分析、スクリプト生成など）を有効にする"
    )
    
    # === スクレイピング設定 ===
    scraping_enabled = models.BooleanField(
        default=True,
        verbose_name="スクレイピング機能を有効化"
    )
    
    scraping_timeout_seconds = models.IntegerField(
        default=15,
        validators=[MinValueValidator(5), MaxValueValidator(60)],
        verbose_name="スクレイピングタイムアウト（秒）"
    )
    
    scraping_delay_seconds = models.FloatField(
        default=2.0,
        validators=[MinValueValidator(0.5), MaxValueValidator(10.0)],
        verbose_name="スクレイピング間隔（秒）"
    )
    
    respect_robots_txt = models.BooleanField(
        default=True,
        verbose_name="robots.txtを尊重"
    )
    
    # === PDF処理設定 ===
    max_pdf_file_size_mb = models.IntegerField(
        default=20,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        verbose_name="PDF最大ファイルサイズ（MB）"
    )
    
    pdf_processing_enabled = models.BooleanField(
        default=True,
        verbose_name="PDF処理を有効化"
    )
    
    # === セキュリティ設定 ===
    session_timeout_minutes = models.IntegerField(
        default=60,
        validators=[MinValueValidator(5), MaxValueValidator(480)],
        verbose_name="セッションタイムアウト（分）"
    )
    
    max_login_attempts = models.IntegerField(
        default=5,
        validators=[MinValueValidator(3), MaxValueValidator(10)],
        verbose_name="最大ログイン試行回数"
    )
    
    lockout_duration_minutes = models.IntegerField(
        default=30,
        validators=[MinValueValidator(5), MaxValueValidator(1440)],
        verbose_name="アカウントロック時間（分）"
    )
    
    # === 通知設定 ===
    enable_email_notifications = models.BooleanField(
        default=False,
        verbose_name="メール通知を有効化"
    )
    
    admin_email = models.EmailField(
        blank=True,
        verbose_name="管理者メールアドレス"
    )
    
    # === その他 ===
    maintenance_mode = models.BooleanField(
        default=False,
        verbose_name="メンテナンスモード"
    )
    
    maintenance_message = models.TextField(
        blank=True,
        verbose_name="メンテナンスメッセージ"
    )
    
    system_announcement = models.TextField(
        blank=True,
        verbose_name="システムお知らせ"
    )
    
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="更新者"
    )
    
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")
    
    class Meta:
        verbose_name = "システム設定"
        verbose_name_plural = "システム設定"
    
    def save(self, *args, **kwargs):
        # シングルトンパターン
        self.singleton_id = 1
        
        # キャッシュをクリア
        cache.delete('system_settings')
        cache.delete('openai_api_key')  # APIキーのキャッシュもクリア
        
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """設定を取得（キャッシュ付き）"""
        settings_obj = cache.get('system_settings')
        if settings_obj is None:
            settings_obj, _ = cls.objects.get_or_create(singleton_id=1)
            cache.set('system_settings', settings_obj, 300)  # 5分間キャッシュ
        return settings_obj
    
    def get_openai_api_key(self):
        """OpenAI APIキーを取得（DB優先、次に環境変数）"""
        if self.openai_api_key:
            return self.openai_api_key
        return settings.OPENAI_API_KEY
    
    def __str__(self):
        return "システム設定"


class PromptTemplate(models.Model):
    """カスタマイズ可能なプロンプトテンプレート"""
    
    TEMPLATE_TYPES = [
        ('company_analysis', '企業情報分析'),
        ('product_extraction', '商品情報抽出'),
        ('product_matching', '商品マッチング'),
        ('script_opening', 'スクリプト：オープニング'),
        ('script_problem', 'スクリプト：課題特定'),
        ('script_solution', 'スクリプト：ソリューション提案'),
        ('script_objection', 'スクリプト：反論処理'),
        ('script_closing', 'スクリプト：クロージング'),
        ('custom', 'カスタム'),
    ]
    
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name="テンプレート名"
    )
    
    template_type = models.CharField(
        max_length=50,
        choices=TEMPLATE_TYPES,
        verbose_name="テンプレートタイプ"
    )
    
    description = models.TextField(
        blank=True,
        verbose_name="説明"
    )
    
    system_prompt = models.TextField(
        verbose_name="システムプロンプト"
    )
    
    user_prompt_template = models.TextField(
        verbose_name="ユーザープロンプトテンプレート"
    )
    
    # AI設定（オプション）
    model_override = models.CharField(
        max_length=50,
        blank=True,
        choices=[
            ('', 'システムデフォルト'),
            ('gpt-4o', 'GPT-4o'),
            ('gpt-4o-mini', 'GPT-4o Mini'),
        ],
        verbose_name="モデル上書き"
    )
    
    temperature_override = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(2.0)],
        verbose_name="Temperature上書き"
    )
    
    # バージョン管理
    version = models.IntegerField(default=1, verbose_name="バージョン")
    
    is_active = models.BooleanField(default=True, verbose_name="有効")
    is_default = models.BooleanField(default=False, verbose_name="デフォルト")
    
    # 作成・更新情報
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_prompts',
        verbose_name="作成者"
    )
    
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='updated_prompts',
        verbose_name="更新者"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")
    
    class Meta:
        verbose_name = "プロンプトテンプレート"
        verbose_name_plural = "プロンプトテンプレート"
        ordering = ['template_type', 'name']
    
    def __str__(self):
        return f"{self.name} (v{self.version})"
    
    def render(self, context):
        """コンテキストを使ってプロンプトをレンダリング"""
        from django.template import Template, Context
        
        template = Template(self.user_prompt_template)
        rendered = template.render(Context(context))
        return rendered
    
    def save(self, *args, **kwargs):
        # デフォルトは1つだけ（同じtemplate_type内）
        if self.is_default:
            PromptTemplate.objects.filter(
                template_type=self.template_type,
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        
        super().save(*args, **kwargs)


class PromptVersion(models.Model):
    """プロンプトのバージョン履歴"""
    
    prompt_template = models.ForeignKey(
        PromptTemplate,
        on_delete=models.CASCADE,
        related_name='versions',
        verbose_name="プロンプトテンプレート"
    )
    
    version = models.IntegerField(verbose_name="バージョン")
    
    system_prompt = models.TextField(verbose_name="システムプロンプト")
    user_prompt_template = models.TextField(verbose_name="ユーザープロンプトテンプレート")
    
    change_summary = models.TextField(
        blank=True,
        verbose_name="変更内容"
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="作成者"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    
    class Meta:
        verbose_name = "プロンプトバージョン"
        verbose_name_plural = "プロンプトバージョン"
        ordering = ['-version']
        unique_together = ['prompt_template', 'version']
    
    def __str__(self):
        return f"{self.prompt_template.name} - v{self.version}"

