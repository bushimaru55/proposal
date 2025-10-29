"""
Core app のビュー
"""
from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
import logging

from .utils import get_openai_api_key, is_ai_enabled, get_ai_settings
from .models import SystemSettings

logger = logging.getLogger(__name__)


@staff_member_required
def dashboard_view(request):
    """ダッシュボード（ホーム画面）"""
    return render(request, 'dashboard/index.html')


@staff_member_required
def test_openai_connection(request):
    """
    OpenAI API接続テスト
    管理画面から呼ばれる
    """
    try:
        from openai import OpenAI
        
        # APIキーの取得
        api_key = get_openai_api_key()
        
        if not api_key:
            return JsonResponse({
                'success': False,
                'error': 'APIキーが設定されていません',
                'details': '管理画面でOpenAI APIキーを設定してください。'
            })
        
        # AI機能の有効状態確認
        if not is_ai_enabled():
            return JsonResponse({
                'success': False,
                'error': 'AI機能が無効です',
                'details': 'システム設定でAI機能を有効にしてください。'
            })
        
        # AI設定取得
        settings = get_ai_settings()
        
        # 簡単なテストリクエスト
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # コスト節約のためminiを使用
            messages=[
                {"role": "system", "content": "あなたは親切なアシスタントです。"},
                {"role": "user", "content": "接続テストです。短く挨拶してください。"}
            ],
            max_tokens=50
        )
        
        ai_response = response.choices[0].message.content
        
        return JsonResponse({
            'success': True,
            'message': 'OpenAI APIとの接続に成功しました',
            'details': {
                'api_key_masked': api_key[:7] + '...' + api_key[-4:] if len(api_key) > 20 else '***',
                'model': settings['model'],
                'temperature': settings['temperature'],
                'test_response': ai_response,
                'usage': {
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                }
            }
        })
        
    except Exception as e:
        logger.error(f"OpenAI API connection test failed: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': f'{type(e).__name__}: {str(e)}',
            'details': 'APIキーが無効か、OpenAIサービスに問題がある可能性があります。'
        })


@staff_member_required
def ai_chat_test(request):
    """
    AI チャットテスト画面
    管理画面から簡単にAIとチャットできる
    """
    settings = SystemSettings.get_settings()
    ai_settings = get_ai_settings()
    
    context = {
        'settings': settings,
        'ai_settings': ai_settings,
        'api_key_set': bool(get_openai_api_key()),
        'ai_enabled': is_ai_enabled(),
    }
    
    return render(request, 'admin/core/ai_chat_test.html', context)


@staff_member_required
@require_http_methods(["POST"])
def ai_chat_send(request):
    """
    AIチャットメッセージ送信
    """
    try:
        from openai import OpenAI
        
        # リクエストボディからメッセージを取得
        data = json.loads(request.body)
        user_message = data.get('message', '')
        conversation_history = data.get('history', [])
        
        if not user_message:
            return JsonResponse({
                'success': False,
                'error': 'メッセージが空です'
            })
        
        # APIキーの確認
        api_key = get_openai_api_key()
        if not api_key or not is_ai_enabled():
            return JsonResponse({
                'success': False,
                'error': 'AI機能が有効でないか、APIキーが設定されていません'
            })
        
        # AI設定取得
        settings = get_ai_settings()
        
        # 会話履歴を構築
        messages = [
            {"role": "system", "content": "あなたは親切で知識豊富なAIアシスタントです。日本語で丁寧に応答してください。"}
        ]
        
        # 過去の会話を追加（最新10件まで）
        for msg in conversation_history[-10:]:
            messages.append({
                "role": msg['role'],
                "content": msg['content']
            })
        
        # 新しいユーザーメッセージを追加
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        # OpenAI APIコール
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=settings['model'],
            messages=messages,
            temperature=settings['temperature'],
            max_tokens=settings['max_tokens']
        )
        
        ai_message = response.choices[0].message.content
        
        return JsonResponse({
            'success': True,
            'message': ai_message,
            'usage': {
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens
            },
            'model': response.model
        })
        
    except Exception as e:
        logger.error(f"AI chat error: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': f'{type(e).__name__}: {str(e)}'
        })
