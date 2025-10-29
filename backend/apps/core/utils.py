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

