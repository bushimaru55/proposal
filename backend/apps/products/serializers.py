"""
商品管理のシリアライザ
"""
from rest_framework import serializers
from .models import ProductCategory, Product, ProductKnowledge, ProposalProductLink


class ProductCategorySerializer(serializers.ModelSerializer):
    """商品カテゴリのシリアライザ"""
    
    product_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = ProductCategory
        fields = [
            'id',
            'name',
            'description',
            'display_order',
            'is_active',
            'product_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductKnowledgeSerializer(serializers.ModelSerializer):
    """商品ナレッジのシリアライザ"""
    
    source_type_display = serializers.CharField(source='get_source_type_display', read_only=True)
    processing_status_display = serializers.CharField(source='get_processing_status_display', read_only=True)
    
    class Meta:
        model = ProductKnowledge
        fields = [
            'id',
            'product',
            'source_type',
            'source_type_display',
            'source_url',
            'pdf_file',
            'raw_text',
            'structured_data',
            'processing_status',
            'processing_status_display',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'structured_data', 'processing_status', 'created_at', 'updated_at']
    
    def validate(self, data):
        """ソースタイプに応じた検証"""
        source_type = data.get('source_type')
        
        if source_type == 'url' and not data.get('source_url'):
            raise serializers.ValidationError({"source_url": "URLを入力してください"})
        
        if source_type == 'pdf' and not data.get('pdf_file'):
            raise serializers.ValidationError({"pdf_file": "PDFファイルをアップロードしてください"})
        
        if source_type == 'text' and not data.get('raw_text'):
            raise serializers.ValidationError({"raw_text": "テキストを入力してください"})
        
        return data


class ProductSerializer(serializers.ModelSerializer):
    """商品のシリアライザ"""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    knowledge_items = ProductKnowledgeSerializer(many=True, read_only=True, source='productknowledge_set')
    
    class Meta:
        model = Product
        fields = [
            'id',
            'category',
            'category_name',
            'name',
            'description',
            'price',
            'is_active',
            'display_order',
            'knowledge_items',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductListSerializer(serializers.ModelSerializer):
    """商品一覧用の軽量シリアライザ"""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    knowledge_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id',
            'category_name',
            'name',
            'price',
            'is_active',
            'knowledge_count',
            'created_at'
        ]
    
    def get_knowledge_count(self, obj):
        """ナレッジアイテム数を返す"""
        return obj.productknowledge_set.count()


class ProposalProductLinkSerializer(serializers.ModelSerializer):
    """提案-商品リンクのシリアライザ"""
    
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = ProposalProductLink
        fields = [
            'id',
            'talk_script',
            'product',
            'product_name',
            'match_score',
            'match_reason',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']

