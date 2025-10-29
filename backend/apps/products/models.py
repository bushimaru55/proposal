from django.db import models
from django.core.validators import FileExtensionValidator
from django.contrib.postgres.fields import ArrayField
from django.conf import settings
import hashlib


class ProductCategory(models.Model):
    """商品カテゴリ"""
    name = models.CharField(max_length=100, unique=True, verbose_name="カテゴリ名")
    description = models.TextField(blank=True, verbose_name="説明")
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='children',
        verbose_name="親カテゴリ"
    )
    
    class Meta:
        verbose_name = "商品カテゴリ"
        verbose_name_plural = "商品カテゴリ"
    
    def __str__(self):
        return self.name


class Product(models.Model):
    """商品マスタ"""
    
    # 基本情報
    name = models.CharField(max_length=255, verbose_name="商品名")
    code = models.CharField(max_length=50, unique=True, verbose_name="商品コード")
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="カテゴリ"
    )
    
    # 商品概要
    short_description = models.TextField(
        max_length=500,
        verbose_name="短い説明"
    )
    full_description = models.TextField(
        blank=True,
        verbose_name="詳細説明"
    )
    
    # 対象顧客・業界
    target_industries = ArrayField(
        models.CharField(max_length=100),
        blank=True,
        default=list,
        verbose_name="対象業界"
    )
    target_customer_size = ArrayField(
        models.CharField(max_length=50),
        blank=True,
        default=list,
        verbose_name="対象企業規模"
    )
    
    # 解決する課題
    pain_points_solved = ArrayField(
        models.TextField(),
        blank=True,
        default=list,
        verbose_name="解決する課題"
    )
    
    # 主要機能・特徴
    key_features = models.JSONField(
        default=list,
        blank=True,
        verbose_name="主要機能"
    )
    
    # 価格情報
    pricing_model = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="価格モデル"
    )
    price_range = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="価格帯"
    )
    
    # 成功事例
    success_cases = models.JSONField(
        default=list,
        blank=True,
        verbose_name="成功事例"
    )
    
    # 競合優位性
    competitive_advantages = ArrayField(
        models.TextField(),
        blank=True,
        default=list,
        verbose_name="競合優位性"
    )
    
    # ステータス
    is_active = models.BooleanField(default=True, verbose_name="有効")
    priority = models.IntegerField(
        default=0,
        verbose_name="優先度"
    )
    
    # メタデータ
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")
    
    class Meta:
        verbose_name = "商品"
        verbose_name_plural = "商品"
        ordering = ['-priority', 'name']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class ProductKnowledge(models.Model):
    """商品ナレッジベース（詳細情報・学習データ）"""
    
    SOURCE_TYPES = [
        ('url', 'URL'),
        ('pdf', 'PDF'),
        ('text', 'テキスト入力'),
        ('manual', '手動入力'),
    ]
    
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='knowledge_base',
        verbose_name="商品"
    )
    
    # ソース情報
    source_type = models.CharField(
        max_length=20,
        choices=SOURCE_TYPES,
        verbose_name="ソースタイプ"
    )
    source_url = models.URLField(blank=True, verbose_name="ソースURL")
    source_file = models.FileField(
        upload_to='products/knowledge/%Y/%m/',
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'txt', 'docx'])],
        verbose_name="ソースファイル"
    )
    
    # コンテンツ
    title = models.CharField(max_length=500, verbose_name="タイトル")
    content = models.TextField(verbose_name="コンテンツ")
    
    # 構造化データ（AI抽出）
    structured_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="構造化データ"
    )
    
    # ベクトル埋め込み（RAG用）
    embedding_hash = models.CharField(
        max_length=64,
        blank=True,
        verbose_name="埋め込みハッシュ"
    )
    
    # メタデータ
    chunk_index = models.IntegerField(
        default=0,
        verbose_name="チャンクインデックス"
    )
    is_active = models.BooleanField(default=True, verbose_name="有効")
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name="処理日時")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    
    class Meta:
        verbose_name = "商品ナレッジ"
        verbose_name_plural = "商品ナレッジ"
        ordering = ['product', 'chunk_index']
    
    def __str__(self):
        return f"{self.product.name} - {self.title}"
    
    def generate_embedding_hash(self):
        """コンテンツのハッシュを生成"""
        content_hash = hashlib.sha256(self.content.encode()).hexdigest()
        self.embedding_hash = content_hash
        return content_hash

