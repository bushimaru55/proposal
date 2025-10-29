"""
CSV分析の非同期タスク
"""
import logging
import pandas as pd
from celery import shared_task
from openai import OpenAI
from django.conf import settings

from .models import CSVUpload, Analysis
from apps.core.utils import get_openai_api_key, is_ai_enabled

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def analyze_csv_data(self, csv_upload_id: int, analysis_prompt: str = None):
    """
    CSVデータを分析してAnalysisを作成
    
    Args:
        csv_upload_id: CSVUploadのID
        analysis_prompt: カスタム分析プロンプト（オプション）
    """
    try:
        csv_upload = CSVUpload.objects.select_related('uploaded_by').get(id=csv_upload_id)
        
        logger.info(f"Analyzing CSV #{csv_upload_id}: {csv_upload.file_name}")
        
        # 1. CSVファイルを読み込み
        try:
            df = pd.read_csv(csv_upload.file.path, encoding='utf-8')
        except UnicodeDecodeError:
            # UTF-8で失敗した場合はShift-JISで試す
            df = pd.read_csv(csv_upload.file.path, encoding='shift-jis')
        
        logger.info(f"CSV loaded: {len(df)} rows, {len(df.columns)} columns")
        
        # 2. 基本統計情報を取得
        basic_stats = _get_basic_statistics(df)
        
        # 3. データサマリーを作成（AIに渡す用）
        data_summary = _create_data_summary(df)
        
        # 4. AI機能の確認
        if not is_ai_enabled():
            logger.warning("AI機能が無効です。基本統計情報のみ保存します。")
            # AI分析なしで保存
            analysis = Analysis.objects.create(
                csv_upload=csv_upload,
                analysis_result={
                    'statistics': basic_stats,
                    'summary': data_summary,
                    'ai_analysis': 'AI機能が無効のため、分析は実行されませんでした。'
                },
                status='completed'
            )
            return analysis.id
        
        # 4. AIで分析実行
        client = OpenAI(api_key=get_openai_api_key())
        
        # システム設定からプロンプトテンプレートを取得
        from apps.core.models import PromptTemplate
        
        if analysis_prompt:
            prompt = analysis_prompt
        else:
            try:
                template = PromptTemplate.objects.filter(
                    template_type='csv_analysis',
                    is_active=True
                ).order_by('-version').first()
                
                if template:
                    prompt = template.prompt_text.format(
                        data_summary=data_summary,
                        basic_stats=basic_stats
                    )
                else:
                    prompt = _get_default_analysis_prompt(data_summary, basic_stats)
            except:
                prompt = _get_default_analysis_prompt(data_summary, basic_stats)
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "あなたはデータ分析の専門家です。CSVデータを分析し、ビジネスインサイトを提供します。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        analysis_result = response.choices[0].message.content
        
        # 5. Analysisレコードを作成
        analysis = Analysis.objects.create(
            csv_upload=csv_upload,
            analysis_result=analysis_result,
            metadata={
                'row_count': len(df),
                'column_count': len(df.columns),
                'columns': list(df.columns),
                'basic_stats': basic_stats,
                'model_used': 'gpt-4o'
            },
            analyzed_by=csv_upload.uploaded_by
        )
        
        logger.info(f"Analysis completed: #{analysis.id}")
        
        return {
            'status': 'success',
            'analysis_id': analysis.id,
            'csv_upload_id': csv_upload_id
        }
    
    except CSVUpload.DoesNotExist:
        logger.error(f"CSVUpload #{csv_upload_id} not found")
        return {'status': 'error', 'message': 'CSV upload not found'}
    
    except Exception as e:
        logger.error(f"Error analyzing CSV #{csv_upload_id}: {e}")
        raise self.retry(exc=e, countdown=60 * (self.request.retries + 1))


def _get_basic_statistics(df: pd.DataFrame) -> dict:
    """
    データフレームから基本統計情報を抽出
    """
    stats = {
        'row_count': len(df),
        'column_count': len(df.columns),
        'columns': list(df.columns),
        'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
        'missing_values': df.isnull().sum().to_dict(),
        'numeric_summary': {}
    }
    
    # 数値列の統計
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 0:
        stats['numeric_summary'] = df[numeric_cols].describe().to_dict()
    
    return stats


def _create_data_summary(df: pd.DataFrame, max_rows: int = 10) -> str:
    """
    AIに渡すためのデータサマリーを作成
    """
    summary_parts = []
    
    # 列情報
    summary_parts.append(f"【データ概要】")
    summary_parts.append(f"- 行数: {len(df)}")
    summary_parts.append(f"- 列数: {len(df.columns)}")
    summary_parts.append(f"- 列名: {', '.join(df.columns)}")
    summary_parts.append("")
    
    # サンプルデータ（最初の数行）
    summary_parts.append(f"【サンプルデータ（最初の{min(max_rows, len(df))}行）】")
    summary_parts.append(df.head(max_rows).to_string())
    summary_parts.append("")
    
    # 数値列の統計
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 0:
        summary_parts.append("【数値列の基本統計】")
        summary_parts.append(df[numeric_cols].describe().to_string())
        summary_parts.append("")
    
    # カテゴリ列のユニーク値数
    categorical_cols = df.select_dtypes(include=['object']).columns
    if len(categorical_cols) > 0:
        summary_parts.append("【カテゴリ列のユニーク値数】")
        for col in categorical_cols:
            unique_count = df[col].nunique()
            summary_parts.append(f"- {col}: {unique_count}種類")
        summary_parts.append("")
    
    return '\n'.join(summary_parts)


def _get_default_analysis_prompt(data_summary: str, basic_stats: dict) -> str:
    """
    デフォルトの分析プロンプトを返す
    """
    return f"""
以下のCSVデータを分析し、営業活動に役立つインサイトを提供してください。

{data_summary}

【分析視点】
1. データの全体的な傾向・特徴
2. 注目すべき数値やパターン
3. 潜在的な課題や機会
4. 営業提案に活用できるポイント
5. データから読み取れる顧客ニーズ

以下の構造で分析結果を返してください：

## データ概要
（データの全体像を簡潔に）

## 主要な発見
1. （重要な発見1）
2. （重要な発見2）
3. （重要な発見3）

## ビジネスインサイト
（営業活動に活用できる具体的な示唆）

## 提案ポイント
（このデータを元にした提案のヒント）

## 注意点・補足
（データ解釈の際の注意点）
"""


@shared_task
def batch_analyze_csv_uploads(csv_upload_ids: list):
    """
    複数のCSVファイルを一括分析
    
    Args:
        csv_upload_ids: CSVUploadのIDリスト
    """
    results = []
    for csv_upload_id in csv_upload_ids:
        result = analyze_csv_data.delay(csv_upload_id)
        results.append({
            'csv_upload_id': csv_upload_id,
            'task_id': result.id
        })
    
    logger.info(f"Batch analysis initiated for {len(csv_upload_ids)} CSV files")
    return results


@shared_task
def cleanup_old_csv_files():
    """
    古いCSVファイルをクリーンアップ（定期実行）
    90日以上経過したファイルを削除
    """
    from django.utils import timezone
    from datetime import timedelta
    
    threshold = timezone.now() - timedelta(days=90)
    
    old_uploads = CSVUpload.objects.filter(uploaded_at__lt=threshold)
    count = old_uploads.count()
    
    # ファイルを削除
    for upload in old_uploads:
        if upload.file:
            upload.file.delete()
    
    # レコードを削除
    old_uploads.delete()
    
    if count > 0:
        logger.info(f"Cleaned up {count} old CSV files")
    
    return {'cleaned_up': count}

