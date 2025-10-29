"""
CSV分析のシリアライザ
"""
from rest_framework import serializers
from .models import CSVUpload, Analysis


class CSVUploadSerializer(serializers.ModelSerializer):
    """CSVアップロードのシリアライザ"""
    
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    file_size_mb = serializers.SerializerMethodField()
    has_analysis = serializers.SerializerMethodField()
    
    class Meta:
        model = CSVUpload
        fields = [
            'id',
            'file',
            'file_name',
            'file_size',
            'file_size_mb',
            'description',
            'uploaded_by',
            'uploaded_by_name',
            'has_analysis',
            'uploaded_at'
        ]
        read_only_fields = ['id', 'file_name', 'file_size', 'uploaded_at']
    
    def get_file_size_mb(self, obj):
        """ファイルサイズをMB単位で返す"""
        return round(obj.file_size / (1024 * 1024), 2)
    
    def get_has_analysis(self, obj):
        """分析済みかどうか"""
        return hasattr(obj, 'analysis') and obj.analysis is not None
    
    def validate_file(self, value):
        """CSVファイルの検証"""
        if not value.name.endswith('.csv'):
            raise serializers.ValidationError("CSVファイルのみアップロード可能です")
        
        # ファイルサイズチェック（50MB以下）
        if value.size > 50 * 1024 * 1024:
            raise serializers.ValidationError("ファイルサイズは50MB以下にしてください")
        
        return value


class AnalysisSerializer(serializers.ModelSerializer):
    """分析結果のシリアライザ"""
    
    csv_file_name = serializers.CharField(source='csv_upload.file_name', read_only=True)
    analyzed_by_name = serializers.CharField(source='analyzed_by.get_full_name', read_only=True)
    
    class Meta:
        model = Analysis
        fields = [
            'id',
            'csv_upload',
            'csv_file_name',
            'analysis_result',
            'metadata',
            'analyzed_by',
            'analyzed_by_name',
            'analyzed_at'
        ]
        read_only_fields = ['id', 'analyzed_at']


class AnalysisListSerializer(serializers.ModelSerializer):
    """分析結果一覧用の軽量シリアライザ"""
    
    csv_file_name = serializers.CharField(source='csv_upload.file_name', read_only=True)
    analyzed_by_name = serializers.CharField(source='analyzed_by.get_full_name', read_only=True)
    preview = serializers.SerializerMethodField()
    
    class Meta:
        model = Analysis
        fields = [
            'id',
            'csv_file_name',
            'preview',
            'analyzed_by_name',
            'analyzed_at'
        ]
    
    def get_preview(self, obj):
        """分析結果のプレビュー（最初の200文字）"""
        if obj.analysis_result:
            return obj.analysis_result[:200] + ('...' if len(obj.analysis_result) > 200 else '')
        return ""


class AnalysisRequestSerializer(serializers.Serializer):
    """分析リクエスト用"""
    
    csv_upload_id = serializers.IntegerField()
    custom_prompt = serializers.CharField(required=False, allow_blank=True)

