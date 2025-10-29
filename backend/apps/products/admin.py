from django.contrib import admin
from django.utils.html import format_html
from .models import ProductCategory, Product, ProductKnowledge


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'description']
    search_fields = ['name', 'description']
    list_filter = ['parent']


class ProductKnowledgeInline(admin.TabularInline):
    model = ProductKnowledge
    extra = 1
    fields = ['source_type', 'source_url', 'source_file', 'title', 'is_active']
    readonly_fields = []


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'category', 'is_active', 'priority', 'updated_at']
    list_filter = ['category', 'is_active', 'target_industries']
    search_fields = ['name', 'code', 'short_description']
    inlines = [ProductKnowledgeInline]
    
    fieldsets = (
        ('基本情報', {
            'fields': ('name', 'code', 'category', 'short_description', 'full_description')
        }),
        ('ターゲット', {
            'fields': ('target_industries', 'target_customer_size'),
        }),
        ('価値提案', {
            'fields': ('pain_points_solved', 'key_features', 'competitive_advantages'),
        }),
        ('価格・実績', {
            'fields': ('pricing_model', 'price_range', 'success_cases'),
        }),
        ('設定', {
            'fields': ('is_active', 'priority'),
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_admin()
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_admin()


@admin.register(ProductKnowledge)
class ProductKnowledgeAdmin(admin.ModelAdmin):
    list_display = ['product', 'title', 'source_type', 'chunk_index', 'is_active', 'processed_at']
    list_filter = ['source_type', 'is_active', 'product']
    search_fields = ['title', 'content']
    readonly_fields = ['embedding_hash', 'processed_at', 'created_at']
    
    fieldsets = (
        ('基本情報', {
            'fields': ('product', 'title', 'source_type')
        }),
        ('ソース', {
            'fields': ('source_url', 'source_file'),
        }),
        ('コンテンツ', {
            'fields': ('content', 'structured_data'),
        }),
        ('メタデータ', {
            'fields': ('chunk_index', 'is_active', 'embedding_hash', 'processed_at', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_admin()
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_admin()

