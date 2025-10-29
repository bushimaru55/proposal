"""
URL configuration for proposal project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('apps.accounts.urls')),
    # API endpoints (一時的に無効化 - モデル修正後に有効化)
    # path('api/companies/', include('apps.companies.urls')),
    # path('api/products/', include('apps.products.urls')),
    # path('api/analysis/', include('apps.analysis.urls')),
    # path('api/sales/', include('apps.sales.urls')),
    # path('api/exports/', include('apps.exports.urls')),
    path('', include('apps.core.urls')),
]

# Media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug toolbar
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns

# Customize admin site
admin.site.site_header = "AI営業支援システム 管理画面"
admin.site.site_title = "AI営業支援システム"
admin.site.index_title = "管理メニュー"

