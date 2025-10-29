"""
PowerPointエクスポートのシリアライザ
"""
from rest_framework import serializers
from .models import Export


class ExportSerializer(serializers.ModelSerializer):
    """エクスポートのシリアライザ"""
    
    talk_script_company = serializers.CharField(source='talk_script.company.name', read_only=True)
    exported_by_name = serializers.CharField(source='exported_by.get_full_name', read_only=True)
    file_size_mb = serializers.SerializerMethodField()
    
    class Meta:
        model = Export
        fields = [
            'id',
            'talk_script',
            'talk_script_company',
            'pptx_file',
            'file_size',
            'file_size_mb',
            'exported_by',
            'exported_by_name',
            'exported_at'
        ]
        read_only_fields = ['id', 'pptx_file', 'file_size', 'exported_at']
    
    def get_file_size_mb(self, obj):
        """ファイルサイズをMB単位で返す"""
        if obj.file_size:
            return round(obj.file_size / (1024 * 1024), 2)
        return 0


class ExportListSerializer(serializers.ModelSerializer):
    """エクスポート一覧用の軽量シリアライザ"""
    
    talk_script_company = serializers.CharField(source='talk_script.company.name', read_only=True)
    exported_by_name = serializers.CharField(source='exported_by.get_full_name', read_only=True)
    
    class Meta:
        model = Export
        fields = [
            'id',
            'talk_script_company',
            'exported_by_name',
            'exported_at'
        ]


class ExportRequestSerializer(serializers.Serializer):
    """PowerPointエクスポートリクエスト用"""
    
    talk_script_id = serializers.IntegerField()

