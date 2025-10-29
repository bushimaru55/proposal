"""
商品情報処理モジュール
PDF、URL、テキストからの商品情報抽出と構造化
"""
import logging
import re
from typing import Dict, List, Optional
from urllib.parse import urlparse

import PyPDF2
import pdfplumber
import requests
from bs4 import BeautifulSoup
from openai import OpenAI

from django.conf import settings
from apps.core.utils import get_openai_api_key, is_ai_enabled

logger = logging.getLogger(__name__)


class PDFProcessor:
    """PDF処理クラス - テキスト抽出とチャンク分割"""
    
    def __init__(self, max_chunk_size: int = 2000):
        """
        Args:
            max_chunk_size: 1チャンクの最大文字数
        """
        self.max_chunk_size = max_chunk_size
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        PDFファイルからテキストを抽出
        PyPDF2とpdfplumberの両方を試し、より良い結果を返す
        
        Args:
            pdf_path: PDFファイルのパス
        
        Returns:
            抽出されたテキスト
        """
        text_pypdf2 = self._extract_with_pypdf2(pdf_path)
        text_pdfplumber = self._extract_with_pdfplumber(pdf_path)
        
        # より長いテキスト（=より良い抽出結果）を返す
        if len(text_pdfplumber) > len(text_pypdf2):
            logger.info(f"Using pdfplumber result ({len(text_pdfplumber)} chars)")
            return text_pdfplumber
        else:
            logger.info(f"Using PyPDF2 result ({len(text_pypdf2)} chars)")
            return text_pypdf2
    
    def _extract_with_pypdf2(self, pdf_path: str) -> str:
        """PyPDF2でテキスト抽出"""
        try:
            text_parts = []
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
            
            return '\n\n'.join(text_parts)
        except Exception as e:
            logger.error(f"PyPDF2 extraction failed: {e}")
            return ""
    
    def _extract_with_pdfplumber(self, pdf_path: str) -> str:
        """pdfplumberでテキスト抽出"""
        try:
            text_parts = []
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
            
            return '\n\n'.join(text_parts)
        except Exception as e:
            logger.error(f"pdfplumber extraction failed: {e}")
            return ""
    
    def split_into_chunks(self, text: str) -> List[str]:
        """
        テキストを意味のある単位でチャンクに分割
        
        Args:
            text: 分割対象のテキスト
        
        Returns:
            チャンクのリスト
        """
        # 段落で分割
        paragraphs = re.split(r'\n\s*\n', text)
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            paragraph_length = len(paragraph)
            
            # 段落が最大サイズを超える場合は文で分割
            if paragraph_length > self.max_chunk_size:
                # 現在のチャンクを保存
                if current_chunk:
                    chunks.append('\n\n'.join(current_chunk))
                    current_chunk = []
                    current_length = 0
                
                # 長い段落を文単位で分割
                sentences = re.split(r'[。.!?]\s*', paragraph)
                for sentence in sentences:
                    if not sentence:
                        continue
                    
                    sentence_length = len(sentence)
                    if current_length + sentence_length > self.max_chunk_size:
                        if current_chunk:
                            chunks.append('\n\n'.join(current_chunk))
                        current_chunk = [sentence]
                        current_length = sentence_length
                    else:
                        current_chunk.append(sentence)
                        current_length += sentence_length
            else:
                # 通常の段落処理
                if current_length + paragraph_length > self.max_chunk_size:
                    # チャンクサイズを超える場合は保存
                    if current_chunk:
                        chunks.append('\n\n'.join(current_chunk))
                    current_chunk = [paragraph]
                    current_length = paragraph_length
                else:
                    current_chunk.append(paragraph)
                    current_length += paragraph_length
        
        # 最後のチャンクを追加
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))
        
        logger.info(f"Split text into {len(chunks)} chunks")
        return chunks


class URLProcessor:
    """URL処理クラス - Webページからの情報抽出"""
    
    def __init__(self, timeout: int = 30):
        """
        Args:
            timeout: リクエストのタイムアウト秒数
        """
        self.timeout = timeout
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def fetch_content(self, url: str) -> Optional[str]:
        """
        URLからコンテンツを取得
        
        Args:
            url: 対象URL
        
        Returns:
            抽出されたテキスト、失敗時はNone
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # スクリプトとスタイルを除去
            for script in soup(['script', 'style', 'nav', 'footer', 'header']):
                script.decompose()
            
            # テキスト抽出
            text = soup.get_text(separator='\n', strip=True)
            
            # 空行を整理
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            text = '\n\n'.join(lines)
            
            logger.info(f"Fetched {len(text)} chars from {url}")
            return text
        
        except Exception as e:
            logger.error(f"Failed to fetch URL {url}: {e}")
            return None


class ProductInfoStructurer:
    """商品情報構造化クラス - AIを使用して情報を整理"""
    
    def __init__(self):
        self.client = OpenAI(api_key=get_openai_api_key())
    
    def structure_product_info(
        self,
        raw_text: str,
        product_name: str,
        source_type: str
    ) -> Dict:
        """
        生テキストを構造化された商品情報に変換
        
        Args:
            raw_text: 生のテキスト
            product_name: 商品名
            source_type: ソースタイプ（url/pdf/text）
        
        Returns:
            構造化された商品情報
        """
        try:
            prompt = f"""
以下は「{product_name}」という商品・サービスに関する情報です。
このテキストから重要な情報を抽出し、営業提案に役立つ形で構造化してください。

【元テキスト】
{raw_text[:4000]}  # 最初の4000文字のみ使用

【抽出してほしい情報】
1. 商品の概要・特徴
2. 主要な機能・スペック
3. 価格情報（あれば）
4. 対象顧客・業界
5. 導入メリット
6. 競合優位性
7. 導入事例（あれば）

JSONフォーマットで返してください：
{{
    "overview": "商品概要",
    "features": ["特徴1", "特徴2", ...],
    "specifications": {{"項目": "値", ...}},
    "pricing": "価格情報（不明な場合は空文字）",
    "target_customers": ["対象顧客1", "対象顧客2", ...],
    "benefits": ["メリット1", "メリット2", ...],
    "competitive_advantages": ["優位性1", "優位性2", ...],
    "case_studies": ["事例1", "事例2", ...]
}}
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "あなたは営業支援のための商品情報分析の専門家です。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            
            import json
            structured_info = json.loads(response.choices[0].message.content)
            
            logger.info(f"Structured product info for: {product_name}")
            return structured_info
        
        except Exception as e:
            logger.error(f"Failed to structure product info: {e}")
            return {
                "overview": raw_text[:500],
                "features": [],
                "specifications": {},
                "pricing": "",
                "target_customers": [],
                "benefits": [],
                "competitive_advantages": [],
                "case_studies": []
            }
    
    def summarize_chunks(self, chunks: List[str], product_name: str) -> str:
        """
        複数のチャンクを要約して1つのテキストにまとめる
        
        Args:
            chunks: テキストチャンクのリスト
            product_name: 商品名
        
        Returns:
            要約されたテキスト
        """
        try:
            # 各チャンクを個別に要約
            summaries = []
            for i, chunk in enumerate(chunks[:5]):  # 最初の5チャンクのみ処理
                prompt = f"""
以下は「{product_name}」に関する文書の一部です。
営業提案に必要な重要情報を抽出して簡潔にまとめてください（300文字以内）。

{chunk[:2000]}
"""
                
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "簡潔な要約の専門家"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=500
                )
                
                summary = response.choices[0].message.content.strip()
                summaries.append(summary)
            
            # 要約を結合
            combined_summary = '\n\n'.join(summaries)
            logger.info(f"Summarized {len(chunks)} chunks into {len(combined_summary)} chars")
            
            return combined_summary
        
        except Exception as e:
            logger.error(f"Failed to summarize chunks: {e}")
            return '\n\n'.join(chunks[:3])  # 失敗時は最初の3チャンクをそのまま返す


# ユーティリティ関数
def process_product_knowledge(
    source_type: str,
    content: str,
    product_name: str
) -> Dict:
    """
    商品ナレッジを処理してstructured_dataを生成
    
    Args:
        source_type: 'url', 'pdf', 'text'のいずれか
        content: URLパス、PDFパス、またはテキスト本文
        product_name: 商品名
    
    Returns:
        構造化された商品情報
    """
    try:
        # 1. ソースに応じてテキスト取得
        if source_type == 'pdf':
            processor = PDFProcessor()
            raw_text = processor.extract_text_from_pdf(content)
            
            # 長すぎる場合はチャンク分割して要約
            if len(raw_text) > 4000:
                chunks = processor.split_into_chunks(raw_text)
                structurer = ProductInfoStructurer()
                raw_text = structurer.summarize_chunks(chunks, product_name)
        
        elif source_type == 'url':
            processor = URLProcessor()
            raw_text = processor.fetch_content(content)
            
            if not raw_text:
                return {"error": "Failed to fetch URL content"}
            
            # URLも長すぎる場合は要約
            if len(raw_text) > 4000:
                pdf_processor = PDFProcessor()
                chunks = pdf_processor.split_into_chunks(raw_text)
                structurer = ProductInfoStructurer()
                raw_text = structurer.summarize_chunks(chunks, product_name)
        
        else:  # text
            raw_text = content
        
        # 2. AI構造化
        structurer = ProductInfoStructurer()
        structured_info = structurer.structure_product_info(
            raw_text, product_name, source_type
        )
        
        return structured_info
    
    except Exception as e:
        logger.error(f"Error in process_product_knowledge: {e}")
        return {
            "error": str(e),
            "overview": "処理中にエラーが発生しました"
        }

