from django.contrib import admin
from django import forms
from django.utils.html import format_html
from .models import SystemSettings, PromptTemplate, PromptVersion


class SystemSettingsAdminForm(forms.ModelForm):
    """システム設定用のカスタムフォーム"""
    
    class Meta:
        model = SystemSettings
        fields = '__all__'
        widgets = {
            'openai_api_key': forms.PasswordInput(render_value=True),
        }


@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    form = SystemSettingsAdminForm
    
    fieldsets = (
        ('🔑 API設定', {
            'fields': ('openai_api_key', 'ai_enabled', 'api_key_status'),
            'description': 'OpenAI APIキーを設定してください。空の場合は環境変数から取得します。'
        }),
        ('CSV処理設定', {
            'fields': ('max_csv_file_size_mb', 'allowed_csv_encodings'),
            'classes': ('collapse',)
        }),
        ('AI設定', {
            'fields': ('default_ai_model', 'ai_temperature', 'max_tokens_per_request', 'daily_token_limit'),
        }),
        ('スクレイピング設定', {
            'fields': ('scraping_enabled', 'scraping_timeout_seconds', 
                      'scraping_delay_seconds', 'respect_robots_txt'),
        }),
        ('PDF処理設定', {
            'fields': ('max_pdf_file_size_mb', 'pdf_processing_enabled'),
        }),
        ('セキュリティ設定', {
            'fields': ('session_timeout_minutes', 'max_login_attempts', 'lockout_duration_minutes'),
        }),
        ('通知設定', {
            'fields': ('enable_email_notifications', 'admin_email'),
        }),
        ('その他', {
            'fields': ('maintenance_mode', 'maintenance_message', 'system_announcement'),
        }),
        ('メタ情報', {
            'fields': ('updated_by', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['updated_by', 'updated_at', 'api_key_status']
    
    def api_key_status(self, obj):
        """APIキーの設定状態を表示"""
        if obj and obj.openai_api_key:
            masked_key = obj.openai_api_key[:7] + '...' + obj.openai_api_key[-4:] if len(obj.openai_api_key) > 20 else '***'
            return format_html('<span style="color: green;">✓ DBに設定済み ({})</span>', masked_key)
        else:
            import os
            env_key = os.getenv('OPENAI_API_KEY', '')
            if env_key:
                return format_html('<span style="color: orange;">⚠ 環境変数を使用</span>')
            else:
                return format_html('<span style="color: red;">✗ 未設定</span>')
    
    api_key_status.short_description = 'APIキー状態'
    
    def has_add_permission(self, request):
        # シングルトンなので追加不可
        return False
    
    def has_delete_permission(self, request, obj=None):
        # シングルトンなので削除不可
        return False
    
    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
        
        # 保存後にメッセージを表示
        if obj.openai_api_key:
            self.message_user(
                request,
                '✓ OpenAI APIキーが正常に保存されました。',
                level='SUCCESS'
            )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # 管理者のみアクセス可能
        if not request.user.is_admin():
            return qs.none()
        return qs


class PromptVersionInline(admin.TabularInline):
    model = PromptVersion
    extra = 0
    readonly_fields = ['version', 'system_prompt', 'user_prompt_template', 
                       'change_summary', 'created_by', 'created_at']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(PromptTemplate)
class PromptTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'template_type', 'version', 'is_active', 'is_default', 'updated_at']
    list_filter = ['template_type', 'is_active', 'is_default']
    search_fields = ['name', 'description']
    readonly_fields = ['version', 'created_by', 'created_at', 'updated_by', 'updated_at']
    inlines = [PromptVersionInline]
    
    fieldsets = (
        ('基本情報', {
            'fields': ('name', 'template_type', 'description', 'is_active', 'is_default')
        }),
        ('プロンプト設定', {
            'fields': ('system_prompt', 'user_prompt_template'),
            'description': '''
            <div style="background: #f0f8ff; padding: 10px; border-radius: 5px; margin: 10px 0;">
                <strong>使用可能な変数：</strong><br>
                • {{analysis_result}} - データ分析結果<br>
                • {{company_info}} - 企業情報<br>
                • {{product_info}} - 商品情報<br>
                • {{custom_input}} - カスタム入力<br>
            </div>
            '''
        }),
        ('AI設定（オプション）', {
            'fields': ('model_override', 'temperature_override'),
            'classes': ('collapse',),
            'description': '空欄の場合はシステムデフォルト設定を使用'
        }),
        ('メタ情報', {
            'fields': ('version', 'created_by', 'created_at', 'updated_by', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        # バージョン履歴を保存
        if change:
            # 既存オブジェクトの変更
            old_obj = PromptTemplate.objects.get(pk=obj.pk)
            if (old_obj.system_prompt != obj.system_prompt or 
                old_obj.user_prompt_template != obj.user_prompt_template):
                # プロンプトが変更された場合、バージョンアップ
                obj.version += 1
                
                # 履歴を保存
                PromptVersion.objects.create(
                    prompt_template=obj,
                    version=obj.version,
                    system_prompt=obj.system_prompt,
                    user_prompt_template=obj.user_prompt_template,
                    created_by=request.user
                )
        else:
            obj.created_by = request.user
        
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # 管理者以外は閲覧のみ
        return qs
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_admin()
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_admin()

