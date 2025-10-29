from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import UserActivityLog


def get_client_ip(request):
    """クライアントIPアドレスを取得"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def login_view(request):
    """ログインビュー"""
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                
                # IPアドレス記録
                user.last_login_ip = get_client_ip(request)
                user.save(update_fields=['last_login_ip'])
                
                # ログ記録
                UserActivityLog.objects.create(
                    user=user,
                    action_type='login',
                    description=f'ログイン成功',
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                messages.success(request, f'ようこそ、{user.get_full_name() or user.username}さん')
                next_url = request.GET.get('next', 'core:dashboard')
                return redirect(next_url)
            else:
                messages.error(request, 'このアカウントは無効化されています')
        else:
            # ログイン失敗のログ
            UserActivityLog.objects.create(
                user=None,
                action_type='login',
                description=f'ログイン失敗: {username}',
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            messages.error(request, 'ユーザー名またはパスワードが正しくありません')
    
    return render(request, 'accounts/login.html')


@login_required
def logout_view(request):
    """ログアウトビュー"""
    # ログ記録
    UserActivityLog.objects.create(
        user=request.user,
        action_type='logout',
        description='ログアウト',
        ip_address=get_client_ip(request)
    )
    
    logout(request)
    messages.success(request, 'ログアウトしました')
    return redirect('accounts:login')

