# app/services/web_extractor.py
import logging
import os
import re
import requests
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
import json
from urllib.parse import urlparse, urljoin
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

class WebExtractorService:
    """
    웹 페이지에서 정보를 추출하는 서비스
    ExtractURL, WebSearchRanked API를 사용하여 웹 콘텐츠 추출 및 처리
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # API 키 로드
        self.extracturl_api_key = os.getenv("EXTRACTURL_API_KEY", "")
        self.websearchranked_api_key = os.getenv("WEBSEARCHRANKED_API_KEY", "")
        
        # API 엔드포인트
        self.extracturl_api_url = "https://api.extractapi.com/v1/extract"
        self.websearchranked_api_url = "https://api.websearchapi.com/v1/search"
        
        # 사용자 에이전트 설정
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        
        # 캐시 디렉토리 설정
        self.cache_dir = "data/cache"
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def clean_html(self, html_text: str) -> str:
        """
        HTML에서 태그와 불필요한 공백을 제거합니다.
        """
        # BeautifulSoup을 사용하여 HTML 파싱
        soup = BeautifulSoup(html_text, 'html.parser')
        
        # 스크립트, 스타일, 헤드 등 불필요한 태그 제거
        for element in soup(['script', 'style', 'head', 'iframe', 'nav', 'footer']):
            element.decompose()
        
        # 텍스트 추출 및 정리
        text = soup.get_text(separator=' ')
        
        # 여러 줄의 공백 제거
        text = re.sub(r'\n+', '\n', text)
        text = re.sub(r' +', ' ', text)
        
        return text.strip()
    
    def extract_content_from_url(self, url: str, cache: bool = True) -> Dict[str, Any]:
        """
        URL에서 콘텐츠를 추출합니다.
        """
        try:
            # 캐시 파일 경로
            cache_file = os.path.join(self.cache_dir, f"{hash(url)}.json")
            
            # 캐시가 있는 경우 캐시에서 로드
            if cache and os.path.exists(cache_file):
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        self.logger.info(f"캐시에서 URL 콘텐츠 로드: {url}")
                        return json.load(f)
                except Exception as e:
                    self.logger.warning(f"캐시 로드 실패, 새로 추출합니다: {str(e)}")
            
            # ExtractURL API가 설정된 경우
            if self.extracturl_api_key:
                params = {
                    "apikey": self.extracturl_api_key,
                    "url": url,
                    "user_agent": self.user_agent
                }
                
                response = requests.get(self.extracturl_api_url, params=params)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # 결과 캐시에 저장
                    if cache:
                        with open(cache_file, 'w', encoding='utf-8') as f:
                            json.dump(result, f, ensure_ascii=False, indent=2)
                    
                    return result
                else:
                    self.logger.error(f"ExtractURL API 호출 실패: {response.status_code}")
            
            # API 사용 불가능한 경우 직접 추출
            self.logger.info(f"직접 URL 콘텐츠 추출: {url}")
            
            headers = {
                "User-Agent": self.user_agent
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # HTML 파싱
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 메타데이터 추출
            title = soup.title.string if soup.title else "제목 없음"
            
            # 메타 설명 추출
            description = ""
            meta_desc = soup.find("meta", attrs={"name": "description"})
            if meta_desc and "content" in meta_desc.attrs:
                description = meta_desc["content"]
            
            # 주요 콘텐츠 추출
            main_content = self.clean_html(response.text)
            
            # 이미지 URL 추출
            images = []
            for img in soup.find_all("img", src=True):
                img_url = img["src"]
                if not img_url.startswith(('http://', 'https://')):
                    img_url = urljoin(url, img_url)
                images.append(img_url)
            
            # 링크 추출
            links = []
            for link in soup.find_all("a", href=True):
                href = link["href"]
                if not href.startswith(('http://', 'https://')):
                    href = urljoin(url, href)
                links.append({
                    "url": href,
                    "text": link.get_text(strip=True)
                })
            
            result = {
                "url": url,
                "title": title,
                "description": description,
                "content": main_content,
                "images": images[:10],  # 최대 10개 이미지만 저장
                "links": links[:20]     # 최대 20개 링크만 저장
            }
            
            # 결과 캐시에 저장
            if cache:
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
            
            return result
            
        except Exception as e:
            self.logger.error(f"URL 콘텐츠 추출 중 오류 발생: {str(e)}")
            return {
                "url": url,
                "title": "오류",
                "description": f"콘텐츠 추출 중 오류 발생: {str(e)}",
                "content": "",
                "images": [],
                "links": []
            }
    
    def search_web(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """
        웹 검색을 수행합니다.
        """
        try:
            # 캐시 파일 경로
            cache_file = os.path.join(self.cache_dir, f"search_{hash(query)}_{num_results}.json")
            
            # 캐시가 있는 경우 캐시에서 로드
            if os.path.exists(cache_file):
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        self.logger.info(f"캐시에서 검색 결과 로드: {query}")
                        return json.load(f)
                except Exception as e:
                    self.logger.warning(f"캐시 로드 실패, 새로 검색합니다: {str(e)}")
            
            # WebSearchRanked API가 설정된 경우
            if self.websearchranked_api_key:
                params = {
                    "apikey": self.websearchranked_api_key,
                    "q": query,
                    "num": num_results,
                    "output": "json"
                }
                
                response = requests.get(self.websearchranked_api_url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    results = []
                    
                    for item in data.get("results", []):
                        results.append({
                            "title": item.get("title", ""),
                            "url": item.get("url", ""),
                            "description": item.get("description", ""),
                            "source": urlparse(item.get("url", "")).netloc
                        })
                    
                    # 결과 캐시에 저장
                    with open(cache_file, 'w', encoding='utf-8') as f:
                        json.dump(results, f, ensure_ascii=False, indent=2)
                    
                    return results
                else:
                    self.logger.error(f"WebSearchRanked API 호출 실패: {response.status_code}")
            
            # API 사용 불가능한 경우 샘플 결과 반환
            self.logger.warning("WebSearchRanked API 키가 설정되지 않음, 샘플 결과 반환")
            
            sample_results = [
                {
                    "title": f"{query}에 관한 최신 연구 - 사이언스 저널",
                    "url": "https://example.com/science/article1",
                    "description": f"{query}에 관한 최신 연구 결과와 분석 자료를 제공합니다. 이 연구는 새로운 방법론을 통해 기존의 한계를 극복하고자 합니다.",
                    "source": "example.com"
                },
                {
                    "title": f"{query} 문제 해결을 위한 혁신적 접근법",
                    "url": "https://example.org/innovation/article2",
                    "description": f"{query} 관련 문제를 해결하기 위한 새로운 접근법과 사례 연구를 소개합니다. 여러 분야의 전문가들이 협력하여 개발한 솔루션입니다.",
                    "source": "example.org"
                },
                {
                    "title": f"{query}의 사회적 영향과 미래 전망",
                    "url": "https://example.net/social-impact/article3",
                    "description": f"{query}가 사회에 미치는 영향과 앞으로의 발전 방향에 대한 분석입니다. 전문가들의 인터뷰와 데이터 기반 예측을 포함합니다.",
                    "source": "example.net"
                }
            ]
            
            # 요청된 결과 수에 맞게 샘플 결과 조정
            sample_results = sample_results[:num_results]
            
            # 결과 캐시에 저장
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(sample_results, f, ensure_ascii=False, indent=2)
            
            return sample_results
            
        except Exception as e:
            self.logger.error(f"웹 검색 중 오류 발생: {str(e)}")
            return [
                {
                    "title": "검색 오류",
                    "url": "",
                    "description": f"검색 중 오류가 발생했습니다: {str(e)}",
                    "source": ""
                }
            ]
    
    def extract_keywords_from_url(self, url: str) -> List[str]:
        """
        URL에서 키워드를 추출합니다.
        """
        try:
            content = self.extract_content_from_url(url)
            
            # 메타 키워드 추출
            meta_keywords = []
            
            # HTML에서 meta 태그 키워드 추출
            soup = BeautifulSoup(requests.get(url).text, 'html.parser')
            meta_tag = soup.find("meta", attrs={"name": "keywords"})
            if meta_tag and "content" in meta_tag.attrs:
                meta_keywords = [k.strip() for k in meta_tag["content"].split(",")]
            
            # 콘텐츠에서 자주 등장하는 단어 추출
            if "content" in content and content["content"]:
                text = content["content"]
                
                # 불용어 목록 (실제 구현에서는 더 많은 단어 필요)
                stop_words = ['은', '는', '이', '가', '을', '를', '에', '의', '과', '와', '이다', '있다', 
                             'the', 'a', 'an', 'is', 'are', 'was', 'were', 'in', 'on', 'at', 'to', 'and', 'or']
                
                # 단어 토큰화 및 빈도 계산
                words = re.findall(r'\b\w+\b', text.lower())
                word_freq = {}
                
                for word in words:
                    if word not in stop_words and len(word) > 2:
                        if word in word_freq:
                            word_freq[word] += 1
                        else:
                            word_freq[word] = 1
                
                # 빈도 기준으로 정렬하여 상위 키워드 추출
                sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
                content_keywords = [word for word, freq in sorted_words[:10]]
                
                # 메타 키워드와 콘텐츠 키워드 통합
                all_keywords = meta_keywords + content_keywords
                
                # 중복 제거
                unique_keywords = list(dict.fromkeys(all_keywords))
                
                return unique_keywords[:10]  # 최대 10개 키워드 반환
            
            return meta_keywords
            
        except Exception as e:
            self.logger.error(f"URL에서 키워드 추출 중 오류 발생: {str(e)}")
            return []
    
    def extract_main_text_sections(self, url: str) -> List[Dict[str, str]]:
        """
        URL에서 주요 텍스트 섹션을 추출합니다.
        """
        try:
            content = self.extract_content_from_url(url)
            
            if "content" not in content or not content["content"]:
                return []
            
            # HTML 파싱
            soup = BeautifulSoup(requests.get(url).text, 'html.parser')
            
            # 헤딩 태그 찾기
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            
            sections = []
            
            for heading in headings:
                # 헤딩 텍스트 추출
                heading_text = heading.get_text(strip=True)
                
                # 다음 헤딩 또는 문서 끝까지의 콘텐츠 추출
                section_content = []
                current = heading.next_sibling
                
                while current and (not current.name or current.name not in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                    if isinstance(current, str) and current.strip():
                        section_content.append(current.strip())
                    elif current.name and current.get_text(strip=True):
                        if current.name in ['p', 'div', 'section', 'article']:
                            section_content.append(current.get_text(strip=True))
                    current = current.next_sibling
                
                if section_content:
                    sections.append({
                        "heading": heading_text,
                        "content": " ".join(section_content)
                    })
            
            # 헤딩이 없는 경우 전체 콘텐츠를 하나의 섹션으로 처리
            if not sections:
                main_content = content["content"]
                paragraphs = re.split(r'\n{2,}', main_content)
                
                for i, paragraph in enumerate(paragraphs):
                    if paragraph.strip():
                        sections.append({
                            "heading": f"섹션 {i+1}",
                            "content": paragraph.strip()
                        })
            
            return sections
            
        except Exception as e:
            self.logger.error(f"URL에서 텍스트 섹션 추출 중 오류 발생: {str(e)}")
            return []
    
    def extract_tables_from_url(self, url: str) -> List[Dict[str, Any]]:
        """
        URL에서 테이블 데이터를 추출합니다.
        """
        try:
            # HTML 파싱
            response = requests.get(url, headers={"User-Agent": self.user_agent})
            soup = BeautifulSoup(response.text, 'html.parser')
            
            tables = []
            
            for i, table in enumerate(soup.find_all('table')):
                rows = []
                
                # 테이블 캡션 추출
                caption = table.find('caption')
                table_title = caption.get_text(strip=True) if caption else f"테이블 {i+1}"
                
                # 헤더 추출
                headers = []
                th_elements = table.find_all('th')
                
                if th_elements:
                    for th in th_elements:
                        headers.append(th.get_text(strip=True))
                
                # 행 추출
                for tr in table.find_all('tr'):
                    cells = []
                    for td in tr.find_all(['td', 'th']):
                        cells.append(td.get_text(strip=True))
                    
                    if cells:
                        rows.append(cells)
                
                # 헤더가 없는 경우 첫 번째 행을 헤더로 사용
                if not headers and rows:
                    headers = rows[0]
                    rows = rows[1:]
                
                tables.append({
                    "title": table_title,
                    "headers": headers,
                    "rows": rows
                })
            
            return tables
            
        except Exception as e:
            self.logger.error(f"URL에서 테이블 추출 중 오류 발생: {str(e)}")
            return []
