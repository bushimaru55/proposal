"""
Core app のユーティリティ関数
"""
import os
from django.core.cache import cache


def get_openai_api_key():
    """
    OpenAI APIキーを取得
    優先順位: DB設定 > 環境変数
    
    Returns:
        str: OpenAI APIキー
    """
    # キャッシュから取得を試みる
    cached_key = cache.get('openai_api_key')
    if cached_key:
        return cached_key
    
    # SystemSettingsから取得
    try:
        from .models import SystemSettings
        settings = SystemSettings.get_settings()
        
        if settings.openai_api_key:
            # DBに設定されている場合
            cache.set('openai_api_key', settings.openai_api_key, 300)  # 5分間キャッシュ
            return settings.openai_api_key
    except Exception:
        pass
    
    # 環境変数から取得
    api_key = os.getenv('OPENAI_API_KEY', '')
    if api_key:
        cache.set('openai_api_key', api_key, 300)
    
    return api_key


def is_ai_enabled():
    """
    AI機能が有効かどうかを確認
    
    Returns:
        bool: AI機能が有効な場合True
    """
    try:
        from .models import SystemSettings
        settings = SystemSettings.get_settings()
        return settings.ai_enabled and bool(get_openai_api_key())
    except Exception:
        return bool(get_openai_api_key())


def get_ai_settings():
    """
    AI設定を取得
    
    Returns:
        dict: AI設定の辞書
    """
    try:
        from .models import SystemSettings
        settings = SystemSettings.get_settings()
        
        return {
            'api_key': get_openai_api_key(),
            'model': settings.default_ai_model,
            'temperature': settings.ai_temperature,
            'max_tokens': settings.max_tokens_per_request,
            'enabled': settings.ai_enabled,
        }
    except Exception:
        return {
            'api_key': get_openai_api_key(),
            'model': 'gpt-4o',
            'temperature': 0.7,
            'max_tokens': 4000,
            'enabled': True,
        }


def clear_settings_cache():
    """
    設定関連のキャッシュをクリア
    SystemSettings保存時に呼び出される
    """
    cache.delete('openai_api_key')
    cache.delete('system_settings')


def get_prompt_template(template_type, context=None, fallback_system_prompt=None, fallback_user_prompt=None):
    """
    プロンプトテンプレートを取得してレンダリング
    
    Args:
        template_type: テンプレートタイプ（例: 'csv_analysis'）
        context: レンダリング用のコンテキスト（辞書）
        fallback_system_prompt: フォールバック用のシステムプロンプト
        fallback_user_prompt: フォールバック用のユーザープロンプト
    
    Returns:
        tuple: (system_prompt, user_prompt) または None
    """
    try:
        from .models import PromptTemplate
        
        template = PromptTemplate.objects.filter(
            template_type=template_type,
            is_active=True
        ).order_by('-is_default', '-version').first()
        
        if template:
            # テンプレートをレンダリング
            if context:
                try:
                    from django.template import Template, Context
                    t = Template(template.user_prompt_template)
                    rendered_user_prompt = t.render(Context(context))
                except Exception:
                    # レンダリングエラー時はそのまま返す
                    rendered_user_prompt = template.user_prompt_template
            else:
                rendered_user_prompt = template.user_prompt_template
            
            return (
                template.system_prompt,
                rendered_user_prompt,
                template.model_override,
                template.temperature_override
            )
        
        # テンプレートが見つからない場合はフォールバック
        if fallback_system_prompt and fallback_user_prompt:
            return (fallback_system_prompt, fallback_user_prompt, None, None)
        
    except Exception:
        pass
    
    return None
