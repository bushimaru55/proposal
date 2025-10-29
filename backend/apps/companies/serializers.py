"""
企業情報のシリアライザ
"""
from rest_framework import serializers
from .models import Company


class CompanySerializer(serializers.ModelSerializer):
    """企業情報のシリアライザ"""
    
    scrape_status_display = serializers.CharField(source='get_scrape_status_display', read_only=True)
    
    class Meta:
        model = Company
        fields = [
            'id',
            'url',
            'domain',
            'title',
            'meta_description',
            'main_content',
            'company_name',
            'business_description',
            'industry',
            'key_services',
            'target_market',
            'ai_summary',
            'pain_points',
            'scrape_status',
            'scrape_status_display',
            'scraped_at',
            'created_at'
        ]
        read_only_fields = [
            'id',
            'domain',
            'title',
            'meta_description',
            'main_content',
            'company_name',
            'business_description',
            'industry',
            'key_services',
            'target_market',
            'ai_summary',
            'pain_points',
            'scrape_status',
            'scraped_at',
            'created_at'
        ]
    
    def validate_url(self, value):
        """URLの検証"""
        if not value:
            raise serializers.ValidationError("企業URLは必須です")
        
        if not value.startswith(('http://', 'https://')):
            raise serializers.ValidationError("有効なURLを入力してください")
        
        return value


class CompanyListSerializer(serializers.ModelSerializer):
    """企業情報一覧用の軽量シリアライザ"""
    
    class Meta:
        model = Company
        fields = [
            'id',
            'url',
            'domain',
            'company_name',
            'industry',
            'scrape_status',
            'created_at'
        ]


class CompanyScrapeRequestSerializer(serializers.Serializer):
    """企業情報スクレイピングリクエスト用"""
    
    company_id = serializers.IntegerField()
    force_rescrape = serializers.BooleanField(default=False)

