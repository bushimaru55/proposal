"""
初期データセットアップコマンド
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.core.models import SystemSettings, PromptTemplate

User = get_user_model()


class Command(BaseCommand):
    help = '初期データを作成'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('初期データのセットアップを開始します...'))
        
        # 管理者ユーザー作成
        self.create_admin_user()
        
        # システム設定作成
        self.create_system_settings()
        
        # デフォルトプロンプトテンプレート作成
        self.create_default_prompts()
        
        self.stdout.write(self.style.SUCCESS('\n✓ 初期データのセットアップが完了しました！'))
        self.stdout.write('')
        self.stdout.write('管理画面にログイン:')
        self.stdout.write('  URL: http://localhost:8000/admin/')
        self.stdout.write('  ユーザー名: admin')
        self.stdout.write('  パスワード: admin123')
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('※本番環境では必ずパスワードを変更してください！'))
    
    def create_admin_user(self):
        """管理者ユーザー作成"""
        if User.objects.filter(username='admin').exists():
            self.stdout.write('  - 管理者ユーザーは既に存在します')
            return
        
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123',
            role='admin',
            first_name='システム',
            last_name='管理者'
        )
        self.stdout.write(self.style.SUCCESS('  ✓ 管理者ユーザーを作成しました'))
    
    def create_system_settings(self):
        """システム設定作成"""
        settings, created = SystemSettings.objects.get_or_create(
            singleton_id=1,
            defaults={
                'max_csv_file_size_mb': 10,
                'allowed_csv_encodings': ['utf-8', 'shift_jis', 'cp932'],
                'default_ai_model': 'gpt-4o',
                'ai_temperature': 0.7,
                'max_tokens_per_request': 4000,
                'daily_token_limit': 1000000,
                'scraping_enabled': True,
                'scraping_timeout_seconds': 15,
                'scraping_delay_seconds': 2.0,
                'respect_robots_txt': True,
                'max_pdf_file_size_mb': 20,
                'pdf_processing_enabled': True,
                'session_timeout_minutes': 60,
                'max_login_attempts': 5,
                'lockout_duration_minutes': 30,
                'enable_email_notifications': False,
                'maintenance_mode': False,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('  ✓ システム設定を作成しました'))
        else:
            self.stdout.write('  - システム設定は既に存在します')
    
    def create_default_prompts(self):
        """デフォルトプロンプトテンプレート作成"""
        
        templates = [
            {
                'name': 'デフォルト：CSV解析',
                'template_type': 'csv_analysis',
                'description': 'CSVデータを分析するプロンプト',
                'system_prompt': 'あなたはデータ分析の専門家です。CSVデータを分析し、ビジネスインサイトを提供します。',
                'user_prompt_template': '''以下のCSVデータを分析してください：

【基本統計情報】
{{basic_stats}}

【データサマリー】
{{data_summary}}

ビジネス上の洞察、傾向、推奨事項を提示してください。''',
                'is_default': True,
                'is_active': True,
            },
            {
                'name': 'デフォルト：企業情報分析',
                'template_type': 'company_analysis',
                'description': '企業Webサイトから抽出した情報を分析するプロンプト',
                'system_prompt': 'あなたは企業分析の専門家です。Webサイトの情報から企業の特徴を正確に抽出します。',
                'user_prompt_template': '''以下のWebサイト情報から企業の重要な情報を抽出して構造化してください：

タイトル: {{title}}
説明: {{meta_description}}
本文: {{main_content}}

以下の項目をJSON形式で返してください：
{
  "company_name": "企業名",
  "business_description": "事業内容の簡潔な説明",
  "industry": "業界",
  "key_services": ["主要サービス1", "主要サービス2"],
  "target_market": "ターゲット市場",
  "pain_points": ["推定される課題1", "推定される課題2"],
  "ai_summary": "企業の特徴を3-4文で要約"
}

※情報が不明な項目は空文字または空配列を返してください。''',
                'is_default': True,
                'is_active': True,
            },
            {
                'name': 'デフォルト：商品マッチング',
                'template_type': 'product_matching',
                'description': '企業と商品のマッチングを行うプロンプト',
                'system_prompt': 'あなたは商品提案の専門家です。顧客のニーズに最適な商品を選択します。',
                'user_prompt_template': '企業情報: {{company_info}}\n商品リスト: {{product_list}}',
                'is_default': True,
                'is_active': True,
            },
            {
                'name': 'デフォルト：オープニング',
                'template_type': 'script_opening',
                'description': 'トークスクリプトのオープニング部分を生成',
                'system_prompt': 'あなたは経験豊富な営業トレーナーです。効果的な商談のオープニングを作成します。',
                'user_prompt_template': '''
企業: {{company_info.company_name}}
業界: {{company_info.industry}}

信頼関係を構築するための自然で親しみやすいオープニングトークを作成してください。
''',
                'is_default': True,
                'is_active': True,
            },
            {
                'name': 'デフォルト：課題特定',
                'template_type': 'script_problem',
                'description': '顧客の課題を特定するヒアリング部分を生成',
                'system_prompt': 'あなたは経験豊富な営業トレーナーです。効果的なヒアリング手法を教えます。',
                'user_prompt_template': '''
企業: {{company_info.company_name}}
推定される課題: {{company_info.pain_points}}

顧客の課題を引き出すための質問と、課題を明確化するトークを作成してください。
''',
                'is_default': True,
                'is_active': True,
            },
            {
                'name': 'デフォルト：ソリューション提案',
                'template_type': 'script_solution',
                'description': '商品・サービスの提案部分を生成',
                'system_prompt': 'あなたは経験豊富な営業トレーナーです。価値を明確に伝える提案を作成します。',
                'user_prompt_template': '''
企業: {{company_info.company_name}}
課題: {{company_info.pain_points}}
提案商品: {{product_info}}

課題に対する解決策として商品を提案するトークを作成してください。
具体的なメリットと導入効果を含めてください。
''',
                'is_default': True,
                'is_active': True,
            },
            {
                'name': 'デフォルト：反論処理',
                'template_type': 'script_objection',
                'description': 'よくある懸念への対応を生成',
                'system_prompt': 'あなたは経験豊富な営業トレーナーです。顧客の懸念に適切に対応する方法を教えます。',
                'user_prompt_template': '''
よくある懸念点:
- 価格が高い
- 導入が複雑
- 効果が不明確

これらの懸念に対する効果的な対応トークを作成してください。
''',
                'is_default': True,
                'is_active': True,
            },
            {
                'name': 'デフォルト：クロージング',
                'template_type': 'script_closing',
                'description': '商談のクロージング部分を生成',
                'system_prompt': 'あなたは経験豊富な営業トレーナーです。自然で効果的なクロージングを作成します。',
                'user_prompt_template': '''
企業: {{company_info.company_name}}

次のステップへ進むための自然なクロージングトークを作成してください。
押し売りではなく、顧客の意思決定をサポートする表現にしてください。
''',
                'is_default': True,
                'is_active': True,
            },
            {
                'name': 'デフォルト：トークスクリプト生成（全体）',
                'template_type': 'script_generate',
                'description': '企業情報と商品情報からトークスクリプト全体を生成',
                'system_prompt': 'あなたは経験豊富な営業トレーナーです。効果的な営業トークスクリプトを作成します。',
                'user_prompt_template': '''以下の情報をもとに、営業トークスクリプトを作成してください。

【顧客情報】
企業名: {{company_info.company_name}}
業界: {{company_info.industry}}
事業内容: {{company_info.business_description}}
推定課題: {{company_info.pain_points}}

【提案商品】
{{product_info}}

【学習コンテキスト】
{{learning_context}}

上記の情報を踏まえて、実際の商談で使える具体的なトークスクリプトを作成してください。
顧客との信頼関係を築き、課題を明確化し、適切なソリューションを提案する構成にしてください。''',
                'is_default': True,
                'is_active': True,
            },
        ]
        
        created_count = 0
        for template_data in templates:
            _, created = PromptTemplate.objects.get_or_create(
                name=template_data['name'],
                defaults=template_data
            )
            if created:
                created_count += 1
        
        if created_count > 0:
            self.stdout.write(self.style.SUCCESS(f'  ✓ {created_count}個のプロンプトテンプレートを作成しました'))
        else:
            self.stdout.write('  - プロンプトテンプレートは既に存在します')

