from django.contrib import admin
from .models import CSVUpload, Analysis


@admin.register(CSVUpload)
class CSVUploadAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'uploaded_by', 'row_count', 'column_count', 'uploaded_at']
    list_filter = ['uploaded_at', 'uploaded_by']
    search_fields = ['file_name']
    readonly_fields = ['file_name', 'file_size', 'row_count', 'column_count', 
                       'uploaded_by', 'uploaded_at']
    date_hierarchy = 'uploaded_at'
    
    def has_add_permission(self, request):
        # アップロードはAPIから
        return False


@admin.register(Analysis)
class AnalysisAdmin(admin.ModelAdmin):
    list_display = ['id', 'csv_upload', 'status', 'model_used', 'token_count', 'created_by', 'created_at']
    list_filter = ['status', 'model_used', 'created_at']
    search_fields = ['prompt', 'result']
    readonly_fields = ['csv_upload', 'model_used', 'token_count', 'created_by', 
                       'created_at', 'completed_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('基本情報', {
            'fields': ('csv_upload', 'prompt', 'status')
        }),
        ('結果', {
            'fields': ('result', 'error_message'),
        }),
        ('AI情報', {
            'fields': ('model_used', 'token_count'),
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

