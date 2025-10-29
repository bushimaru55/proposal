from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """カスタムユーザーモデル"""
    
    USER_ROLES = [
        ('admin', '管理者'),
        ('sales_manager', '営業マネージャー'),
        ('sales_rep', '営業担当者'),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=USER_ROLES,
        default='sales_rep',
        verbose_name="役割"
    )
    
    department = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="部署"
    )
    
    employee_id = models.CharField(
        max_length=50,
        blank=True,
        unique=True,
        null=True,
        verbose_name="社員番号"
    )
    
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="電話番号"
    )
    
    last_login_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="最終ログインIP"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")
    
    class Meta:
        verbose_name = "ユーザー"
        verbose_name_plural = "ユーザー"
        ordering = ['username']
    
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
    
    def is_admin(self):
        """管理者かどうか"""
        return self.role == 'admin' or self.is_superuser
    
    def is_sales_manager(self):
        """営業マネージャーかどうか"""
        return self.role in ['admin', 'sales_manager'] or self.is_superuser
    
    def can_edit_settings(self):
        """設定変更権限"""
        return self.is_admin()
    
    def can_edit_products(self):
        """商品編集権限"""
        return self.is_admin()
    
    def can_view_all_proposals(self):
        """全案件閲覧権限"""
        return self.role in ['admin', 'sales_manager'] or self.is_superuser


class UserActivityLog(models.Model):
    """ユーザー活動ログ"""
    
    ACTION_TYPES = [
        ('login', 'ログイン'),
        ('logout', 'ログアウト'),
        ('create', '作成'),
        ('update', '更新'),
        ('delete', '削除'),
        ('view', '閲覧'),
        ('download', 'ダウンロード'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='activity_logs',
        null=True,
        blank=True,
        verbose_name="ユーザー"
    )
    
    action_type = models.CharField(
        max_length=20,
        choices=ACTION_TYPES,
        verbose_name="アクションタイプ"
    )
    
    target_model = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="対象モデル"
    )
    
    target_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="対象ID"
    )
    
    description = models.TextField(
        blank=True,
        verbose_name="説明"
    )
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="IPアドレス"
    )
    
    user_agent = models.TextField(
        blank=True,
        verbose_name="ユーザーエージェント"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="実行日時")
    
    class Meta:
        verbose_name = "ユーザー活動ログ"
        verbose_name_plural = "ユーザー活動ログ"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['action_type', '-created_at']),
        ]
    
    def __str__(self):
        username = self.user.username if self.user else '不明'
        return f"{username} - {self.get_action_type_display()} ({self.created_at})"

