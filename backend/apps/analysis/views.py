from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters import rest_framework as filters

from .models import CSVUpload, Analysis
from .serializers import (
    CSVUploadSerializer,
    AnalysisSerializer,
    AnalysisListSerializer,
    AnalysisRequestSerializer
)
from .tasks import analyze_csv_data


class CSVUploadViewSet(viewsets.ModelViewSet):
    """
    CSVアップロードのViewSet
    """
    queryset = CSVUpload.objects.all().order_by('-uploaded_at')
    serializer_class = CSVUploadSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def perform_create(self, serializer):
        """CSVアップロード時にアップロード者を設定"""
        csv_upload = serializer.save(uploaded_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def analyze(self, request, pk=None):
        """
        CSVファイルの分析を実行
        """
        csv_upload = self.get_object()
        
        # 既に分析済みかチェック
        if hasattr(csv_upload, 'analysis') and csv_upload.analysis:
            return Response(
                {
                    'message': '既に分析済みです',
                    'analysis_id': csv_upload.analysis.id
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # カスタムプロンプト（オプション）
        custom_prompt = request.data.get('custom_prompt', None)
        
        # 分析開始
        task = analyze_csv_data.delay(csv_upload.id, custom_prompt)
        
        return Response({
            'message': '分析を開始しました',
            'task_id': task.id,
            'csv_upload_id': csv_upload.id
        }, status=status.HTTP_202_ACCEPTED)


class AnalysisViewSet(viewsets.ReadOnlyModelViewSet):
    """
    分析結果のViewSet（読み取り専用）
    """
    queryset = Analysis.objects.select_related('csv_upload', 'analyzed_by').all().order_by('-analyzed_at')
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AnalysisListSerializer
        return AnalysisSerializer
    
    @action(detail=False, methods=['post'])
    def create_analysis(self, request):
        """
        新規分析を作成（CSVアップロードIDから）
        """
        serializer = AnalysisRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        csv_upload_id = serializer.validated_data['csv_upload_id']
        custom_prompt = serializer.validated_data.get('custom_prompt')
        
        try:
            csv_upload = CSVUpload.objects.get(id=csv_upload_id)
        except CSVUpload.DoesNotExist:
            return Response(
                {'message': 'CSVアップロードが見つかりません'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 分析開始
        task = analyze_csv_data.delay(csv_upload_id, custom_prompt)
        
        return Response({
            'message': '分析を開始しました',
            'task_id': task.id,
            'csv_upload_id': csv_upload_id
        }, status=status.HTTP_202_ACCEPTED)

