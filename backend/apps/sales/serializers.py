"""
営業管理のシリアライザ
"""
from rest_framework import serializers
from .models import TalkScript, SalesOutcome, TrainingSession
from apps.products.serializers import ProposalProductLinkSerializer


class TalkScriptSerializer(serializers.ModelSerializer):
    """トークスクリプトのシリアライザ"""
    
    company_name = serializers.CharField(source='company.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    generation_status_display = serializers.CharField(source='get_generation_status_display', read_only=True)
    linked_products = ProposalProductLinkSerializer(many=True, read_only=True, source='proposalproductlink_set')
    
    class Meta:
        model = TalkScript
        fields = [
            'id',
            'company',
            'company_name',
            'analysis',
            'selected_sections',
            'opening_script',
            'problem_identification_script',
            'proposal_script',
            'objection_handling_script',
            'closing_script',
            'additional_notes',
            'generation_prompt_used',
            'learning_context',
            'generation_status',
            'generation_status_display',
            'linked_products',
            'created_by',
            'created_by_name',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'opening_script',
            'problem_identification_script',
            'proposal_script',
            'objection_handling_script',
            'closing_script',
            'generation_prompt_used',
            'learning_context',
            'generation_status',
            'created_at',
            'updated_at'
        ]
    
    def validate_selected_sections(self, value):
        """選択されたセクションの検証"""
        valid_sections = ['opening', 'problem_identification', 'proposal', 'objection_handling', 'closing']
        
        if not value:
            raise serializers.ValidationError("最低1つのセクションを選択してください")
        
        for section in value:
            if section not in valid_sections:
                raise serializers.ValidationError(f"無効なセクション: {section}")
        
        return value


class TalkScriptListSerializer(serializers.ModelSerializer):
    """トークスクリプト一覧用の軽量シリアライザ"""
    
    company_name = serializers.CharField(source='company.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = TalkScript
        fields = [
            'id',
            'company_name',
            'selected_sections',
            'generation_status',
            'product_count',
            'created_by_name',
            'created_at'
        ]
    
    def get_product_count(self, obj):
        """紐付いた商品数"""
        return obj.proposalproductlink_set.count()


class TalkScriptGenerateRequestSerializer(serializers.Serializer):
    """トークスクリプト生成リクエスト用"""
    
    company_id = serializers.IntegerField()
    analysis_id = serializers.IntegerField(required=False, allow_null=True)
    selected_sections = serializers.ListField(
        child=serializers.CharField(),
        default=['opening', 'problem_identification', 'proposal', 'objection_handling', 'closing']
    )


class SalesOutcomeSerializer(serializers.ModelSerializer):
    """商談結果のシリアライザ"""
    
    talk_script_company = serializers.CharField(source='talk_script.company.name', read_only=True)
    recorded_by_name = serializers.CharField(source='recorded_by.get_full_name', read_only=True)
    outcome_display = serializers.CharField(source='get_outcome_display', read_only=True)
    
    class Meta:
        model = SalesOutcome
        fields = [
            'id',
            'talk_script',
            'talk_script_company',
            'outcome',
            'outcome_display',
            'meeting_date',
            'notes',
            'what_worked',
            'what_didnt_work',
            'customer_feedback',
            'next_action',
            'recorded_by',
            'recorded_by_name',
            'recorded_at'
        ]
        read_only_fields = ['id', 'recorded_at']


class SalesOutcomeListSerializer(serializers.ModelSerializer):
    """商談結果一覧用の軽量シリアライザ"""
    
    company_name = serializers.CharField(source='talk_script.company.name', read_only=True)
    recorded_by_name = serializers.CharField(source='recorded_by.get_full_name', read_only=True)
    outcome_display = serializers.CharField(source='get_outcome_display', read_only=True)
    
    class Meta:
        model = SalesOutcome
        fields = [
            'id',
            'company_name',
            'outcome_display',
            'meeting_date',
            'recorded_by_name',
            'recorded_at'
        ]


class TrainingSessionSerializer(serializers.ModelSerializer):
    """トレーニングセッションのシリアライザ"""
    
    talk_script_company = serializers.CharField(source='talk_script.company.name', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = TrainingSession
        fields = [
            'id',
            'user',
            'user_name',
            'talk_script',
            'talk_script_company',
            'duration_minutes',
            'sections_practiced',
            'self_assessment',
            'notes',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']

