"""
トークスクリプト生成機能
"""
from openai import OpenAI
from django.db.models import Q
import logging
import time

logger = logging.getLogger(__name__)


class TalkScriptGenerator:
    """商談結果のフィードバックを活用したトークスクリプト生成"""
    
    SECTION_NAMES = {
        'opening': 'オープニング',
        'problem_identification': '課題特定',
        'solution_proposal': 'ソリューション提案',
        'objection_handling': '反論処理',
        'closing': 'クロージング',
    }
    
    def __init__(self, system_settings=None):
        from apps.core.models import SystemSettings
        self.client = OpenAI()
        self.settings = system_settings or SystemSettings.get_settings()
    
    def get_learning_context(self, company):
        """過去の商談結果から学習コンテキストを生成"""
        from apps.sales.models import SalesOutcome
        
        # 同じ業界の成功事例を取得
        successful_outcomes = SalesOutcome.objects.filter(
            outcome='won',
            used_for_training=True,
            talk_script__company__industry=company.industry
        ).select_related('talk_script')[:5]
        
        # 失敗事例から学ぶ
        failed_outcomes = SalesOutcome.objects.filter(
            outcome='lost',
            used_for_training=True,
            talk_script__company__industry=company.industry
        ).select_related('talk_script')[:3]
        
        learning_context = {
            'success_patterns': [],
            'common_objections': [],
            'avoid_patterns': []
        }
        
        # 成功パターン抽出
        for outcome in successful_outcomes:
            if outcome.what_worked:
                learning_context['success_patterns'].append(outcome.what_worked)
        
        # 失敗パターン・よくある懸念抽出
        for outcome in failed_outcomes:
            if outcome.what_didnt_work:
                learning_context['avoid_patterns'].append(outcome.what_didnt_work)
            if outcome.customer_objections:
                learning_context['common_objections'].extend(outcome.customer_objections)
        
        return learning_context
    
    def generate_section(self, section_name, company_info, selected_products, 
                        analysis_result=None, custom_prompt=None):
        """セクション別のスクリプト生成"""
        
        # 学習コンテキスト取得
        learning_context = self.get_learning_context(company_info)
        
        # プロンプト構築
        base_prompt = custom_prompt or f"""
あなたは経験豊富な営業トレーナーです。
以下の情報を基に、効果的な営業トークスクリプトの「{self.SECTION_NAMES.get(section_name)}」セクションを作成してください。

# 提案先企業情報
- 企業名: {company_info.company_name}
- 業界: {company_info.industry}
- 事業内容: {company_info.business_description}
- 推定される課題: {', '.join(company_info.pain_points) if company_info.pain_points else '不明'}
"""
        
        # CSV分析結果がある場合は追加
        if analysis_result:
            base_prompt += f"\n\n# データ分析結果\n{analysis_result[:1000]}"
        
        # 商品情報を追加
        if selected_products:
            base_prompt += "\n\n# 提案商品\n"
            for idx, prod_info in enumerate(selected_products, 1):
                product = prod_info['product']
                base_prompt += f"\n{idx}. {product.name}\n"
                base_prompt += f"   説明: {product.short_description}\n"
                base_prompt += f"   提案角度: {prod_info.get('proposal_angle', '')}\n"
        
        # 学習コンテキストを組み込む
        if learning_context['success_patterns']:
            base_prompt += f"\n\n【過去の成功事例から学んだポイント】\n"
            base_prompt += "\n".join(f"- {p}" for p in learning_context['success_patterns'][:3])
        
        if section_name == 'objection_handling' and learning_context['common_objections']:
            base_prompt += f"\n\n【よくある懸念点】\n"
            base_prompt += "\n".join(f"- {o}" for o in set(learning_context['common_objections'][:5]))
        
        if learning_context['avoid_patterns']:
            base_prompt += f"\n\n【避けるべき表現・アプローチ】\n"
            base_prompt += "\n".join(f"- {p}" for p in learning_context['avoid_patterns'][:2])
        
        base_prompt += "\n\n---\n\n上記の情報を踏まえて、実際の商談で使える具体的なトークスクリプトを作成してください。"
        
        try:
            response = self.client.chat.completions.create(
                model=self.settings.default_ai_model,
                messages=[
                    {"role": "system", "content": "あなたは経験豊富な営業トレーナーです。効果的な営業トークスクリプトを作成します。"},
                    {"role": "user", "content": base_prompt}
                ],
                temperature=self.settings.ai_temperature,
                max_tokens=self.settings.max_tokens_per_request
            )
            
            return {
                'content': response.choices[0].message.content,
                'tokens': response.usage.total_tokens
            }
            
        except Exception as e:
            logger.error(f"スクリプト生成エラー ({section_name}): {e}")
            return {
                'content': f"[生成エラー: {str(e)}]",
                'tokens': 0
            }
    
    def generate_full_script(self, company, selected_products, selected_sections, analysis=None):
        """完全なトークスクリプトを生成"""
        start_time = time.time()
        
        # 分析結果のテキスト取得（オプション）
        analysis_result = analysis.result if analysis else None
        
        # 各セクションを生成
        script_sections = {}
        total_tokens = 0
        
        for section in selected_sections:
            if section in self.SECTION_NAMES:
                result = self.generate_section(
                    section,
                    company,
                    selected_products,
                    analysis_result
                )
                script_sections[section] = result['content']
                total_tokens += result['tokens']
        
        generation_time = time.time() - start_time
        
        logger.info(f"トークスクリプト生成完了: {len(selected_sections)}セクション, {total_tokens}トークン")
        
        return {
            'script_sections': script_sections,
            'total_tokens': total_tokens,
            'generation_time': generation_time,
            'model_used': self.settings.default_ai_model
        }

