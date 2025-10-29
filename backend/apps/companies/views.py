from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters import rest_framework as filters

from .models import Company
from .serializers import (
    CompanySerializer,
    CompanyListSerializer,
    CompanyScrapeRequestSerializer
)
from .tasks import scrape_and_structure_company


class CompanyFilter(filters.FilterSet):
    """企業情報のフィルター"""
    company_name = filters.CharFilter(lookup_expr='icontains')
    industry = filters.CharFilter(lookup_expr='icontains')
    scrape_status = filters.ChoiceFilter(choices=[
        ('success', '成功'),
        ('partial', '部分的'),
        ('failed', '失敗')
    ])
    
    class Meta:
        model = Company
        fields = ['company_name', 'industry', 'scrape_status']


class CompanyViewSet(viewsets.ModelViewSet):
    """
    企業情報のViewSet
    
    list: 企業情報一覧
    retrieve: 企業情報詳細
    create: 企業情報作成（自動スクレイピング開始）
    update: 企業情報更新
    partial_update: 企業情報部分更新
    destroy: 企業情報削除
    scrape: 企業情報スクレイピング実行
    """
    queryset = Company.objects.all().order_by('-created_at')
    permission_classes = [IsAuthenticated]
    filterset_class = CompanyFilter
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CompanyListSerializer
        return CompanySerializer
    
    def perform_create(self, serializer):
        """企業情報作成時にスクレイピングを開始"""
        company = serializer.save()
        
        # 非同期でスクレイピング開始
        # scrape_and_structure_company.delay(company.id)
    
    @action(detail=True, methods=['post'])
    def scrape(self, request, pk=None):
        """
        企業情報のスクレイピングを実行
        """
        company = self.get_object()
        
        serializer = CompanyScrapeRequestSerializer(data={
            'company_id': company.id,
            'force_rescrape': request.data.get('force_rescrape', False)
        })
        serializer.is_valid(raise_exception=True)
        
        # スクレイピングステータスをチェック
        if company.scrape_status == 'processing':
            return Response(
                {'message': 'スクレイピング処理中です'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # スクレイピング開始
        # task = scrape_and_structure_company.delay(company.id)
        task = None
        
        return Response({
            'message': 'スクレイピングを開始しました',
            'task_id': task.id,
            'company_id': company.id
        }, status=status.HTTP_202_ACCEPTED)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        企業情報の統計
        """
        total = Company.objects.count()
        status_choices = [
            ('success', '成功'),
            ('partial', '部分的'),
            ('failed', '失敗')
        ]
        by_status = {}
        for status_code, status_label in status_choices:
            count = Company.objects.filter(scrape_status=status_code).count()
            by_status[status_code] = {
                'label': status_label,
                'count': count
            }
        
        return Response({
            'total': total,
            'by_status': by_status
        })

