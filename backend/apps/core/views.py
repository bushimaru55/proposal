from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from apps.core.models import SystemSettings


@login_required
def dashboard(request):
    """ダッシュボード"""
    settings = SystemSettings.get_settings()
    
    context = {
        'user': request.user,
        'system_announcement': settings.system_announcement,
    }
    
    return render(request, 'dashboard/index.html', context)

