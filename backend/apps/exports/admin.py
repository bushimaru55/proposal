from django.contrib import admin
from .models import ExportHistory


@admin.register(ExportHistory)
class ExportHistoryAdmin(admin.ModelAdmin):
    list_display = ['talk_script', 'export_type', 'status', 'file_size', 'created_by', 'created_at']
    list_filter = ['export_type', 'status', 'created_at']
    search_fields = ['talk_script__company__company_name']
    readonly_fields = ['file_size', 'created_by', 'created_at', 'completed_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('基本情報', {
            'fields': ('talk_script', 'export_type', 'status')
        }),
        ('ファイル情報', {
            'fields': ('file_path', 'file_size'),
        }),
        ('エラー情報', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
        ('メタデータ', {
            'fields': ('created_by', 'created_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # 営業担当者は自分のもののみ
        if not request.user.can_view_all_proposals():
            qs = qs.filter(created_by=request.user)
        return qs

