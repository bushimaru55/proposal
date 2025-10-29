from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters import rest_framework as filters

from .models import ProductCategory, Product, ProductKnowledge
from .serializers import (
    ProductCategorySerializer,
    ProductSerializer,
    ProductListSerializer,
    ProductKnowledgeSerializer
)
from .tasks import process_product_knowledge_task


class ProductCategoryViewSet(viewsets.ModelViewSet):
    """商品カテゴリのViewSet"""
    queryset = ProductCategory.objects.all().order_by('display_order', 'name')
    serializer_class = ProductCategorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == 'list':
            # 商品数を注釈
            from django.db.models import Count
            queryset = queryset.annotate(product_count=Count('product'))
        return queryset


class ProductFilter(filters.FilterSet):
    """商品のフィルター"""
    name = filters.CharFilter(lookup_expr='icontains')
    category = filters.NumberFilter(field_name='category__id')
    is_active = filters.BooleanFilter()
    
    class Meta:
        model = Product
        fields = ['name', 'category', 'is_active']


class ProductViewSet(viewsets.ModelViewSet):
    """
    商品のViewSet
    """
    queryset = Product.objects.select_related('category').all().order_by('display_order', 'name')
    permission_classes = [IsAuthenticated]
    filterset_class = ProductFilter
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductSerializer
    
    @action(detail=True, methods=['get'])
    def knowledge(self, request, pk=None):
        """
        商品のナレッジ一覧を取得
        """
        product = self.get_object()
        knowledge_items = product.productknowledge_set.all()
        serializer = ProductKnowledgeSerializer(knowledge_items, many=True)
        return Response(serializer.data)


class ProductKnowledgeViewSet(viewsets.ModelViewSet):
    """
    商品ナレッジのViewSet
    """
    queryset = ProductKnowledge.objects.select_related('product').all().order_by('-created_at')
    serializer_class = ProductKnowledgeSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        """ナレッジ作成時に処理を開始"""
        knowledge = serializer.save()
        
        # 非同期で処理開始
        process_product_knowledge_task.delay(knowledge.id)
    
    @action(detail=True, methods=['post'])
    def reprocess(self, request, pk=None):
        """
        ナレッジの再処理を実行
        """
        knowledge = self.get_object()
        
        if knowledge.processing_status == 'processing':
            return Response(
                {'message': '処理中です'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # ステータスをリセット
        knowledge.processing_status = 'pending'
        knowledge.save(update_fields=['processing_status'])
        
        # 再処理開始
        task = process_product_knowledge_task.delay(knowledge.id)
        
        return Response({
            'message': '再処理を開始しました',
            'task_id': task.id
        }, status=status.HTTP_202_ACCEPTED)

