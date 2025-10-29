"""
企業情報取得のCeleryタスク
"""
from celery import shared_task
from django.utils import timezone
import logging
import json

from apps.core.utils import get_openai_api_key, is_ai_enabled

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def scrape_and_structure_company(self, company_id):
    """
    企業情報のスクレイピングとAI構造化
    """
    from apps.companies.models import Company
    from apps.companies.scraper import CompanyScraper
    from apps.core.models import SystemSettings
    from openai import OpenAI
    
    try:
        # 進捗更新: 開始
        self.update_state(state='PROGRESS', meta={'progress': 0, 'status': 'スクレイピング開始'})
        
        # 企業取得
        company = Company.objects.get(id=company_id)
        
        # システム設定取得
        settings = SystemSettings.get_settings()
        
        if not settings.scraping_enabled:
            raise Exception("スクレイピング機能が無効化されています")
        
        # スクレイピング実行
        scraper = CompanyScraper(
            company.url,
            timeout=settings.scraping_timeout_seconds,
            delay=settings.scraping_delay_seconds
        )
        scraped_data = scraper.scrape()
        
        if scraped_data['status'] == 'failed':
            company.scrape_status = 'failed'
            company.save()
            raise Exception(scraped_data.get('error', 'スクレイピング失敗'))
        
        # 進捗更新: 50%
        self.update_state(state='PROGRESS', meta={'progress': 50, 'status': 'AI分析中'})
        
        # AIで構造化
        client = OpenAI(api_key=get_openai_api_key())
        
        prompt = f"""
以下は企業のWebサイトからスクレイピングした情報です。
この情報から、企業の重要な情報を抽出して構造化してください。

# スクレイピングデータ
タイトル: {scraped_data['title']}
説明: {scraped_data['meta_description']}
見出し: {', '.join(scraped_data.get('headings', []))}
本文（抜粋）: {scraped_data['main_content'][:2000]}

# 抽出してほしい情報（JSON形式で返してください）
{{
  "company_name": "企業名",
  "business_description": "事業内容の簡潔な説明",
  "industry": "業界（IT、製造、小売など）",
  "key_services": ["主要サービス1", "主要サービス2"],
  "target_market": "ターゲット市場・顧客層",
  "pain_points": ["推定される課題1", "推定される課題2"],
  "ai_summary": "企業の特徴を3-4文で要約"
}}

※情報が不明な項目は空文字または空配列を返してください。
"""
        
        response = client.chat.completions.create(
            model=settings.default_ai_model or "gpt-4o-mini",
            messages=[
                {"role": "system", "content": "あなたは企業分析の専門家です。Webサイトの情報から企業の特徴を正確に抽出します。"},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        
        structured_info = json.loads(response.choices[0].message.content)
        
        # データベース保存
        company.title = scraped_data['title']
        company.meta_description = scraped_data['meta_description']
        company.main_content = scraped_data['main_content']
        company.scrape_status = scraped_data['status']
        
        # AI抽出情報
        company.company_name = structured_info.get('company_name', '')
        company.business_description = structured_info.get('business_description', '')
        company.industry = structured_info.get('industry', '')
        company.key_services = structured_info.get('key_services', [])
        company.target_market = structured_info.get('target_market', '')
        company.pain_points = structured_info.get('pain_points', [])
        company.ai_summary = structured_info.get('ai_summary', '')
        
        company.scraped_at = timezone.now()
        company.save()
        
        logger.info(f"企業情報取得完了: {company_id} - {company.company_name}")
        
        return {
            'status': 'success',
            'company_id': company_id,
            'company_name': company.company_name
        }
        
    except Exception as e:
        logger.error(f"企業情報取得エラー: {e}")
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise

