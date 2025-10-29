from django.shortcuts import render
from django.http import FileResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Export
from .serializers import (
    ExportSerializer,
    ExportListSerializer,
    ExportRequestSerializer
)
from .tasks import generate_pptx_export


class ExportViewSet(viewsets.ReadOnlyModelViewSet):
    """
    PowerPointエクスポートのViewSet（読み取り専用）
    """
    queryset = Export.objects.select_related('talk_script', 'exported_by').all().order_by('-exported_at')
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ExportListSerializer
        return ExportSerializer
    
    @action(detail=False, methods=['post'])
    def create_export(self, request):
        """
        PowerPointファイルをエクスポート
        """
        serializer = ExportRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        talk_script_id = serializer.validated_data['talk_script_id']
        
        # TalkScriptの存在チェック
        from apps.sales.models import TalkScript
        try:
            talk_script = TalkScript.objects.get(id=talk_script_id)
        except TalkScript.DoesNotExist:
            return Response(
                {'message': 'トークスクリプトが見つかりません'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 生成ステータスチェック
        if talk_script.generation_status != 'completed':
            return Response(
                {'message': 'トークスクリプトが完了していません'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Exportレコードを作成
        export = Export.objects.create(
            talk_script=talk_script,
            exported_by=request.user
        )
        
        # 非同期でPowerPoint生成開始
        task = generate_pptx_export.delay(export.id)
        
        return Response({
            'message': 'PowerPoint生成を開始しました',
            'task_id': task.id,
            'export_id': export.id
        }, status=status.HTTP_202_ACCEPTED)
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """
        PowerPointファイルをダウンロード
        """
        export = self.get_object()
        
        if not export.pptx_file:
            return Response(
                {'message': 'ファイルがまだ生成されていません'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # ファイルをダウンロード
        response = FileResponse(
            export.pptx_file.open('rb'),
            content_type='application/vnd.openxmlformats-officedocument.presentationml.presentation'
        )
        response['Content-Disposition'] = f'attachment; filename="{export.pptx_file.name}"'
        
        return response

