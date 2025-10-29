from django.contrib import admin
from django.utils.html import format_html
from .models import TalkScript, ProposalProductLink, SalesOutcome, TrainingSession


@admin.register(TalkScript)
class TalkScriptAdmin(admin.ModelAdmin):
    list_display = ['company', 'status', 'version', 'model_used', 'created_by', 'created_at']
    list_filter = ['status', 'model_used', 'created_at']
    search_fields = ['company__company_name']
    readonly_fields = ['created_at', 'updated_at', 'total_tokens', 'generation_time']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('基本情報', {
            'fields': ('company', 'analysis', 'template', 'status', 'version')
        }),
        ('セクション', {
            'fields': ('selected_sections', 'script_sections'),
        }),
        ('AI情報', {
            'fields': ('model_used', 'total_tokens', 'generation_time'),
            'classes': ('collapse',)
        }),
        ('メタデータ', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # 営業担当者は自分のもののみ
        if not request.user.can_view_all_proposals():
            qs = qs.filter(created_by=request.user)
        return qs


@admin.register(ProposalProductLink)
class ProposalProductLinkAdmin(admin.ModelAdmin):
    list_display = ['talk_script', 'product', 'proposal_order', 'relevance_score']
    list_filter = ['product', 'proposal_order']
    search_fields = ['talk_script__company__company_name', 'product__name']
    readonly_fields = ['created_at']


@admin.register(SalesOutcome)
class SalesOutcomeAdmin(admin.ModelAdmin):
    list_display = ['talk_script', 'outcome', 'meeting_date', 'used_for_training', 'recorded_by', 'created_at']
    list_filter = ['outcome', 'used_for_training', 'meeting_date']
    search_fields = ['talk_script__company__company_name', 'notes']
    readonly_fields = ['recorded_by', 'created_at', 'updated_at']
    date_hierarchy = 'meeting_date'
    
    fieldsets = (
        ('商談情報', {
            'fields': ('talk_script', 'outcome', 'meeting_date')
        }),
        ('フィードバック', {
            'fields': ('what_worked', 'what_didnt_work', 'customer_objections'),
            'description': 'このフィードバックは今後のAI学習に活用されます'
        }),
        ('その他', {
            'fields': ('notes', 'used_for_training'),
        }),
        ('メタデータ', {
            'fields': ('recorded_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # 新規作成時
            obj.recorded_by = request.user
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # 営業担当者は自分のもののみ
        if not request.user.can_view_all_proposals():
            qs = qs.filter(recorded_by=request.user)
        return qs


@admin.register(TrainingSession)
class TrainingSessionAdmin(admin.ModelAdmin):
    list_display = ['talk_script', 'user', 'duration_minutes', 'self_rating', 'trained_at']
    list_filter = ['self_rating', 'trained_at']
    search_fields = ['talk_script__company__company_name', 'notes']
    readonly_fields = ['user', 'trained_at']
    date_hierarchy = 'trained_at'
    
    def save_model(self, request, obj, form, change):
        if not change:  # 新規作成時
            obj.user = request.user
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # 営業担当者は自分のもののみ
        if not request.user.can_view_all_proposals():
            qs = qs.filter(user=request.user)
        return qs

