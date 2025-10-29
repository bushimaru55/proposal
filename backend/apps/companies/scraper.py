"""
企業Webサイトのスクレイピング機能
"""
import requests
from bs4 import BeautifulSoup
import trafilatura
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
import time
import logging

logger = logging.getLogger(__name__)


class CompanyScraper:
    """企業Webサイトのスクレイピング"""
    
    def __init__(self, url, timeout=15, delay=2.0):
        self.url = url
        self.domain = urlparse(url).netloc
        self.timeout = timeout
        self.delay = delay
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; ProposalBot/1.0)',
            'Accept': 'text/html,application/xhtml+xml',
            'Accept-Language': 'ja,en;q=0.9',
        }
    
    def check_robots_txt(self):
        """robots.txtの確認"""
        try:
            rp = RobotFileParser()
            rp.set_url(f"https://{self.domain}/robots.txt")
            rp.read()
            
            can_scrape = rp.can_fetch("*", self.url)
            if not can_scrape:
                logger.warning(f"robots.txt でアクセスが禁止されています: {self.url}")
            return can_scrape
        except Exception as e:
            logger.warning(f"robots.txt の確認に失敗: {e}")
            return True  # 確認できない場合は許可と見なす
    
    def fetch_page(self):
        """ページの取得"""
        try:
            response = requests.get(
                self.url,
                headers=self.headers,
                timeout=self.timeout,
                allow_redirects=True
            )
            response.raise_for_status()
            response.encoding = response.apparent_encoding  # 文字化け対策
            return response.text
        except requests.exceptions.RequestException as e:
            logger.error(f"ページ取得エラー: {e}")
            raise
    
    def extract_with_trafilatura(self, html):
        """trafilaturaでメインコンテンツ抽出"""
        try:
            content = trafilatura.extract(
                html,
                include_links=False,
                include_images=False,
                include_tables=True,
                output_format='txt'
            )
            return content or ""
        except Exception as e:
            logger.error(f"trafilatura抽出エラー: {e}")
            return ""
    
    def extract_with_beautifulsoup(self, html):
        """BeautifulSoupで構造化データ抽出"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # タイトル
            title = ""
            if soup.find('title'):
                title = soup.find('title').text.strip()
            
            # メタディスクリプション
            meta_desc = ""
            meta_tag = soup.find('meta', {'name': 'description'}) or \
                      soup.find('meta', {'property': 'og:description'})
            if meta_tag and meta_tag.get('content'):
                meta_desc = meta_tag['content'].strip()
            
            # 見出し抽出（企業の特徴把握）
            headings = []
            for h_tag in soup.find_all(['h1', 'h2', 'h3']):
                text = h_tag.get_text().strip()
                if text:
                    headings.append(text)
            
            return {
                'title': title,
                'meta_description': meta_desc,
                'headings': headings[:10],  # 上位10個
            }
        except Exception as e:
            logger.error(f"BeautifulSoup抽出エラー: {e}")
            return {}
    
    def scrape(self):
        """完全なスクレイピング実行"""
        
        # 1. robots.txt確認
        if not self.check_robots_txt():
            return {
                'status': 'failed',
                'error': 'robots.txtでアクセスが禁止されています'
            }
        
        # 2. 礼儀正しく待機
        time.sleep(self.delay)
        
        # 3. ページ取得
        try:
            html = self.fetch_page()
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }
        
        # 4. コンテンツ抽出
        main_content = self.extract_with_trafilatura(html)
        structured_data = self.extract_with_beautifulsoup(html)
        
        # 5. 結果の統合
        result = {
            'status': 'success' if main_content else 'partial',
            'url': self.url,
            'domain': self.domain,
            'title': structured_data.get('title', ''),
            'meta_description': structured_data.get('meta_description', ''),
            'main_content': main_content,
            'headings': structured_data.get('headings', []),
        }
        
        return result


def extract_domain(url):
    """URLからドメインを抽出"""
    parsed = urlparse(url)
    return parsed.netloc

