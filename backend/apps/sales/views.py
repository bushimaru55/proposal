from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters import rest_framework as filters

from .models import TalkScript, SalesOutcome, TrainingSession
from .serializers import (
    TalkScriptSerializer,
    TalkScriptListSerializer,
    TalkScriptGenerateRequestSerializer,
    SalesOutcomeSerializer,
    SalesOutcomeListSerializer,
    TrainingSessionSerializer
)
from .tasks import generate_talk_script_with_products


class TalkScriptFilter(filters.FilterSet):
    """トークスクリプトのフィルター"""
    company = filters.NumberFilter(field_name='company__id')
    generation_status = filters.ChoiceFilter(choices=TalkScript.GENERATION_STATUS_CHOICES)
    created_by = filters.NumberFilter(field_name='created_by__id')
    
    class Meta:
        model = TalkScript
        fields = ['company', 'generation_status', 'created_by']


class TalkScriptViewSet(viewsets.ModelViewSet):
    """
    トークスクリプトのViewSet
    """
    queryset = TalkScript.objects.select_related('company', 'analysis', 'created_by').all().order_by('-created_at')
    permission_classes = [IsAuthenticated]
    filterset_class = TalkScriptFilter
    
    def get_serializer_class(self):
        if self.action == 'list':
            return TalkScriptListSerializer
        return TalkScriptSerializer
    
    def get_queryset(self):
        """ユーザーの役割に応じてクエリセットをフィルター"""
        queryset = super().get_queryset()
        user = self.request.user
        
        if user.role == 'sales_rep':
            # 営業担当者は自分の案件のみ
            queryset = queryset.filter(created_by=user)
        
        return queryset
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """
        トークスクリプトを生成
        """
        serializer = TalkScriptGenerateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        company_id = serializer.validated_data['company_id']
        analysis_id = serializer.validated_data.get('analysis_id')
        selected_sections = serializer.validated_data['selected_sections']
        
        # 既存のトークスクリプトがあるかチェック
        from apps.companies.models import Company
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return Response(
                {'message': '企業情報が見つかりません'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # トークスクリプトを作成
        talk_script = TalkScript.objects.create(
            company=company,
            analysis_id=analysis_id,
            selected_sections=selected_sections,
            generation_status='pending',
            created_by=request.user
        )
        
        # 非同期で生成開始
        task = generate_talk_script_with_products.delay(talk_script.id)
        
        return Response({
            'message': 'トークスクリプトの生成を開始しました',
            'task_id': task.id,
            'talk_script_id': talk_script.id
        }, status=status.HTTP_202_ACCEPTED)
    
    @action(detail=True, methods=['post'])
    def regenerate(self, request, pk=None):
        """
        トークスクリプトを再生成
        """
        talk_script = self.get_object()
        
        if talk_script.generation_status == 'processing':
            return Response(
                {'message': '生成中です'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # ステータスをリセット
        talk_script.generation_status = 'pending'
        talk_script.save(update_fields=['generation_status'])
        
        # 再生成開始
        task = generate_talk_script_with_products.delay(talk_script.id)
        
        return Response({
            'message': 'トークスクリプトの再生成を開始しました',
            'task_id': task.id
        }, status=status.HTTP_202_ACCEPTED)


class SalesOutcomeFilter(filters.FilterSet):
    """商談結果のフィルター"""
    talk_script = filters.NumberFilter(field_name='talk_script__id')
    outcome = filters.ChoiceFilter(choices=SalesOutcome.OUTCOME_CHOICES)
    recorded_by = filters.NumberFilter(field_name='recorded_by__id')
    
    class Meta:
        model = SalesOutcome
        fields = ['talk_script', 'outcome', 'recorded_by']


class SalesOutcomeViewSet(viewsets.ModelViewSet):
    """
    商談結果のViewSet
    """
    queryset = SalesOutcome.objects.select_related('talk_script', 'recorded_by').all().order_by('-recorded_at')
    permission_classes = [IsAuthenticated]
    filterset_class = SalesOutcomeFilter
    
    def get_serializer_class(self):
        if self.action == 'list':
            return SalesOutcomeListSerializer
        return SalesOutcomeSerializer
    
    def perform_create(self, serializer):
        """商談結果記録時に記録者を設定"""
        serializer.save(recorded_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        商談結果の統計
        """
        total = SalesOutcome.objects.count()
        by_outcome = {}
        for outcome_code, outcome_label in SalesOutcome.OUTCOME_CHOICES:
            count = SalesOutcome.objects.filter(outcome=outcome_code).count()
            by_outcome[outcome_code] = {
                'label': outcome_label,
                'count': count
            }
        
        # 成功率計算
        success_count = SalesOutcome.objects.filter(outcome='won').count()
        success_rate = (success_count / total * 100) if total > 0 else 0
        
        return Response({
            'total': total,
            'by_outcome': by_outcome,
            'success_rate': round(success_rate, 2)
        })


class TrainingSessionViewSet(viewsets.ModelViewSet):
    """
    トレーニングセッションのViewSet
    """
    queryset = TrainingSession.objects.select_related('user', 'talk_script').all().order_by('-created_at')
    serializer_class = TrainingSessionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """ユーザーは自分のトレーニングセッションのみ"""
        queryset = super().get_queryset()
        user = self.request.user
        
        if user.role == 'sales_rep':
            queryset = queryset.filter(user=user)
        
        return queryset
    
    def perform_create(self, serializer):
        """トレーニングセッション作成時にユーザーを設定"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_stats(self, request):
        """
        自分のトレーニング統計
        """
        user = request.user
        sessions = TrainingSession.objects.filter(user=user)
        
        total_sessions = sessions.count()
        total_minutes = sum(s.duration_minutes or 0 for s in sessions)
        
        # 練習したセクションの集計
        section_counts = {}
        for session in sessions:
            for section in session.sections_practiced:
                section_counts[section] = section_counts.get(section, 0) + 1
        
        return Response({
            'total_sessions': total_sessions,
            'total_minutes': total_minutes,
            'section_counts': section_counts
        })

