from django.contrib import admin
from django import forms
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
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
            'fields': ('openai_api_key', 'ai_enabled', 'api_key_status', 'ai_test_buttons'),
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
    
    readonly_fields = ['updated_by', 'updated_at', 'api_key_status', 'ai_test_buttons']
    
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
    
    def ai_test_buttons(self, obj):
        """AI機能のテストボタン"""
        html = '''
        <div style="margin: 15px 0;">
            <button type="button" onclick="testOpenAIConnection()" 
                    style="padding: 10px 20px; background: #28a745; color: white; border: none; 
                           border-radius: 4px; cursor: pointer; font-size: 14px; margin-right: 10px;">
                🔍 接続テスト
            </button>
            
            <a href="/ai-chat/" target="_blank"
               style="padding: 10px 20px; background: #007bff; color: white; border: none; 
                      border-radius: 4px; cursor: pointer; font-size: 14px; text-decoration: none;
                      display: inline-block;">
                💬 AIチャットテスト
            </a>
            
            <div id="test-result" style="margin-top: 15px;"></div>
        </div>
        
        <script>
        function testOpenAIConnection() {
            const resultDiv = document.getElementById('test-result');
            resultDiv.innerHTML = '<div style="padding: 10px; background: #e7f3ff; border-radius: 4px;">⏳ テスト実行中...</div>';
            
            fetch('/test-openai/', {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    let html = '<div style="padding: 15px; background: #d4edda; border: 1px solid #c3e6cb; border-radius: 4px; color: #155724;">';
                    html += '<strong>✅ 接続成功！</strong><br><br>';
                    html += '<strong>APIキー:</strong> ' + data.details.api_key_masked + '<br>';
                    html += '<strong>モデル:</strong> ' + data.details.model + '<br>';
                    html += '<strong>Temperature:</strong> ' + data.details.temperature + '<br>';
                    html += '<strong>テスト応答:</strong> ' + data.details.test_response + '<br>';
                    html += '<strong>トークン使用:</strong> ' + data.details.usage.total_tokens + ' (入力: ' + data.details.usage.prompt_tokens + ', 出力: ' + data.details.usage.completion_tokens + ')';
                    html += '</div>';
                    resultDiv.innerHTML = html;
                } else {
                    let html = '<div style="padding: 15px; background: #f8d7da; border: 1px solid #f5c6cb; border-radius: 4px; color: #721c24;">';
                    html += '<strong>❌ 接続失敗</strong><br><br>';
                    html += '<strong>エラー:</strong> ' + data.error + '<br>';
                    html += '<strong>詳細:</strong> ' + data.details;
                    html += '</div>';
                    resultDiv.innerHTML = html;
                }
            })
            .catch(error => {
                resultDiv.innerHTML = '<div style="padding: 15px; background: #f8d7da; border-radius: 4px; color: #721c24;">❌ エラー: ' + error.message + '</div>';
            });
        }
        </script>
        '''
        return mark_safe(html)
    
    ai_test_buttons.short_description = 'AI機能テスト'
    
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
        ('🔵 1. システムプロンプト（AIの役割定義）', {
            'fields': ('system_prompt',),
            'description': '''
            <div style="background: #e7f3ff; padding: 15px; border-radius: 5px; margin: 10px 0; border-left: 4px solid #007bff;">
                <strong>💡 システムプロンプトの用途：</strong><br><br>
                これはAIに「あなたは誰で、どのような役割を持つのか」を定義するプロンプトです。<br><br>
                
                <strong>例:</strong><br>
                • 「あなたは企業分析の専門家です。Webサイトの情報から企業の特徴を正確に抽出します。」<br>
                • 「あなたは経験豊富な営業トレーナーです。効果的な営業トークスクリプトを作成します。」<br>
                • 「あなたはデータ分析の専門家です。CSVデータを分析し、ビジネスインサイトを提供します。」<br><br>
                
                <strong>注意:</strong> ここに入力された内容は、すべてのAI生成において一貫して使用されます。
            </div>
            '''
        }),
        ('🟢 2. ユーザープロンプト（具体的なタスク指示）', {
            'fields': ('user_prompt_template',),
            'description': '''
            <div style="background: #f0fff4; padding: 15px; border-radius: 5px; margin: 10px 0; border-left: 4px solid #28a745;">
                <strong>💡 ユーザープロンプトの用途：</strong><br><br>
                これは具体的に「何をしてほしいのか」を指示するプロンプトです。変数を使用して動的な情報を埋め込めます。<br><br>
                
                <strong>使用可能な変数：</strong><br>
                <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
                    <tr style="background: #f8f9fa;">
                        <th style="padding: 8px; border: 1px solid #dee2e6; text-align: left;">変数</th>
                        <th style="padding: 8px; border: 1px solid #dee2e6; text-align: left;">説明</th>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #dee2e6;"><code>{{analysis_result}}</code></td>
                        <td style="padding: 8px; border: 1px solid #dee2e6;">CSV分析の結果</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #dee2e6;"><code>{{company_info}}</code></td>
                        <td style="padding: 8px; border: 1px solid #dee2e6;">企業情報（スクレイピング結果）</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #dee2e6;"><code>{{company_info.company_name}}</code></td>
                        <td style="padding: 8px; border: 1px solid #dee2e6;">企業名のみ</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #dee2e6;"><code>{{company_info.industry}}</code></td>
                        <td style="padding: 8px; border: 1px solid #dee2e6;">業界</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #dee2e6;"><code>{{product_info}}</code></td>
                        <td style="padding: 8px; border: 1px solid #dee2e6;">商品情報</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #dee2e6;"><code>{{basic_stats}}</code></td>
                        <td style="padding: 8px; border: 1px solid #dee2e6;">基本統計情報（CSV解析用）</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #dee2e6;"><code>{{data_summary}}</code></td>
                        <td style="padding: 8px; border: 1px solid #dee2e6;">データサマリー（CSV解析用）</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #dee2e6;"><code>{{learning_context}}</code></td>
                        <td style="padding: 8px; border: 1px solid #dee2e6;">学習コンテキスト（営業結果からの学習）</td>
                    </tr>
                </table><br>
                
                <strong>例:</strong><br>
                <code>以下の企業情報を分析してください：<br>
                企業名: {{company_info.company_name}}<br>
                業界: {{company_info.industry}}</code>
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

