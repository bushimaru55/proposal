from django.contrib import admin
from .models import Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'domain', 'industry', 'scrape_status', 'scraped_at']
    list_filter = ['industry', 'scrape_status', 'scraped_at']
    search_fields = ['company_name', 'domain', 'url']
    readonly_fields = ['scraped_at', 'created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('基本情報', {
            'fields': ('url', 'domain', 'company_name', 'industry')
        }),
        ('スクレイピング結果', {
            'fields': ('title', 'meta_description', 'main_content', 'scrape_status', 'scraped_at')
        }),
        ('AI抽出情報', {
            'fields': ('business_description', 'key_services', 'target_market', 
                      'pain_points', 'ai_summary'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # 営業マネージャー以上は全て閲覧可能
        return qs

