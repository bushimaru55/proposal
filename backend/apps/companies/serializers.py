"""
企業情報のシリアライザ
"""
from rest_framework import serializers
from .models import Company


class CompanySerializer(serializers.ModelSerializer):
    """企業情報のシリアライザ"""
    
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    scraping_status_display = serializers.CharField(source='get_scraping_status_display', read_only=True)
    
    class Meta:
        model = Company
        fields = [
            'id',
            'name',
            'website_url',
            'industry',
            'employee_count',
            'annual_revenue',
            'business_description',
            'key_products',
            'target_market',
            'challenges',
            'raw_scraped_data',
            'scraping_status',
            'scraping_status_display',
            'scraped_at',
            'created_by',
            'created_by_name',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'raw_scraped_data',
            'scraping_status',
            'scraped_at',
            'created_at',
            'updated_at'
        ]
    
    def validate_website_url(self, value):
        """URLの検証"""
        if not value:
            raise serializers.ValidationError("企業URLは必須です")
        
        if not value.startswith(('http://', 'https://')):
            raise serializers.ValidationError("有効なURLを入力してください")
        
        return value


class CompanyListSerializer(serializers.ModelSerializer):
    """企業情報一覧用の軽量シリアライザ"""
    
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = Company
        fields = [
            'id',
            'name',
            'website_url',
            'industry',
            'scraping_status',
            'created_by_name',
            'created_at'
        ]


class CompanyScrapeRequestSerializer(serializers.Serializer):
    """企業情報スクレイピングリクエスト用"""
    
    company_id = serializers.IntegerField()
    force_rescrape = serializers.BooleanField(default=False)

