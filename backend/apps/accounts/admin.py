from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserActivityLog


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'get_full_name', 'role', 'department', 'is_active', 'last_login']
    list_filter = ['role', 'is_active', 'is_staff', 'department', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'employee_id']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('追加情報', {
            'fields': ('role', 'department', 'employee_id', 'phone_number')
        }),
        ('アカウント管理', {
            'fields': ('last_login_ip', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['last_login', 'date_joined', 'created_at', 'updated_at', 'last_login_ip']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # 管理者以外は自分の情報のみ
        if not request.user.is_superuser and not request.user.is_admin():
            qs = qs.filter(id=request.user.id)
        return qs
    
    def has_delete_permission(self, request, obj=None):
        # 管理者のみユーザー削除可能
        if obj and obj == request.user:
            return False  # 自分自身は削除不可
        return request.user.is_admin()


@admin.register(UserActivityLog)
class UserActivityLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action_type', 'target_model', 'target_id', 'ip_address', 'created_at']
    list_filter = ['action_type', 'target_model', 'created_at']
    search_fields = ['user__username', 'description', 'ip_address']
    readonly_fields = ['user', 'action_type', 'target_model', 'target_id', 
                       'description', 'ip_address', 'user_agent', 'created_at']
    date_hierarchy = 'created_at'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

