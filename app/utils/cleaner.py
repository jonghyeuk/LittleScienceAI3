# app/utils/cleaner.py
import logging
import os
import re
import string
import json
import html
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import unicodedata

def setup_logging(log_level=logging.INFO):
    """
    로깅 설정을 초기화합니다.
    """
    # 로그 디렉토리 생성
    log_dir = "data/logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # 현재 날짜로 로그 파일명 생성
    log_filename = os.path.join(log_dir, f"app_{datetime.now().strftime('%Y%m%d')}.log")
    
    # 로깅 형식 설정
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # 로깅 핸들러 설정
    handlers = [
        logging.StreamHandler(),  # 콘솔 출력
        logging.FileHandler(log_filename, encoding='utf-8')  # 파일 출력
    ]
    
    # 로깅 설정
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=handlers
    )
    
    # 외부 라이브러리 로그 레벨 조정
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info("로깅 설정이 완료되었습니다.")

def clean_text(text: str) -> str:
    """
    텍스트에서 불필요한 공백, 특수 문자 등을 정리합니다.
    """
    if not text:
        return ""
    
    # HTML 태그 제거
    text = re.sub(r'<[^>]+>', ' ', text)
    
    # HTML 엔티티 디코딩
    text = html.unescape(text)
    
    # 연속된 공백 제거
    text = re.sub(r'\s+', ' ', text)
    
    # 문장 앞뒤 공백 제거
    text = text.strip()
    
    # 유니코드 정규화
    text = unicodedata.normalize('NFC', text)
    
    return text

def clean_keywords(keywords: List[str]) -> List[str]:
    """
    키워드 목록을 정리합니다.
    """
    if not keywords:
        return []
    
    cleaned = []
    
    for keyword in keywords:
        # 공백 제거 및 소문자 변환
        cleaned_keyword = keyword.strip().lower()
        
        # 특수 문자 제거
        cleaned_keyword = re.sub(r'[^\w\s가-힣]', '', cleaned_keyword)
        
        # 중복 키워드가 아니고 빈 문자열이 아닌 경우에만 추가
        if cleaned_keyword and cleaned_keyword not in cleaned:
            cleaned.append(cleaned_keyword)
    
    return cleaned

def normalize_paper_info(paper: Dict[str, Any]) -> Dict[str, Any]:
    """
    논문 정보를 정규화합니다.
    """
    normalized = {}
    
    # 필수 필드 확인
    for field in ['title', 'authors', 'year', 'abstract', 'source']:
        if field in paper:
            normalized[field] = clean_text(str(paper[field]))
        else:
            # 기본값 설정
            if field == 'title':
                normalized[field] = "제목 없음"
            elif field == 'authors':
                normalized[field] = "저자 미상"
            elif field == 'year':
                normalized[field] = str(datetime.now().year)
            elif field == 'abstract':
                normalized[field] = "초록 정보가 없습니다."
            elif field == 'source':
                normalized[field] = "출처 미상"
    
    # 선택적 필드 확인
    if 'url' in paper:
        normalized['url'] = paper['url']
    
    if 'keywords' in paper:
        if isinstance(paper['keywords'], list):
            normalized['keywords'] = clean_keywords(paper['keywords'])
        elif isinstance(paper['keywords'], str):
            # 쉼표로 구분된 문자열인 경우
            keywords = [k.strip() for k in paper['keywords'].split(',')]
            normalized['keywords'] = clean_keywords(keywords)
        else:
            normalized['keywords'] = []
    else:
        normalized['keywords'] = []
    
    # 키워드가 비어있는 경우 제목에서 키워드 추출
    if not normalized['keywords']:
        # 불용어 목록
        stop_words = ['연구', '분석', '효과', '방법', '시스템', '개발', '영향', '평가', 
                     'the', 'a', 'an', 'of', 'and', 'in', 'on', 'at', 'to', 'for']
        
        # 제목에서 단어 추출
        words = re.findall(r'\b\w+\b', normalized['title'].lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 1]
        
        # 중복 제거 및 최대 5개 키워드 선택
        normalized['keywords'] = list(dict.fromkeys(keywords))[:5]
    
    # 타입 필드 설정
    if 'type' in paper:
        normalized['type'] = paper['type']
    else:
        # URL이 있으면 외부, 없으면 내부로 간주
        normalized['type'] = 'external' if 'url' in normalized else 'internal'
    
    return normalized

def clean_html_content(html_content: str) -> str:
    """
    HTML 콘텐츠에서 불필요한 요소를 제거하고 정리합니다.
    """
    if not html_content:
        return ""
    
    # 스크립트, 스타일 태그 제거
    html_content = re.sub(r'<script.*?</script>', '', html_content, flags=re.DOTALL)
    html_content = re.sub(r'<style.*?</style>', '', html_content, flags=re.DOTALL)
    
    # 주석 제거
    html_content = re.sub(r'<!--.*?-->', '', html_content, flags=re.DOTALL)
    
    # iframe 제거
    html_content = re.sub(r'<iframe.*?</iframe>', '', html_content, flags=re.DOTALL)
    
    # 불필요한 태그 제거
    html_content = re.sub(r'<(nav|footer|aside|header).*?</\1>', '', html_content, flags=re.DOTALL)
    
    return html_content

def extract_paragraphs(text: str) -> List[str]:
    """
    텍스트에서 단락을 추출합니다.
    """
    if not text:
        return []
    
    # 연속된 줄바꿈으로 단락 구분
    paragraphs = re.split(r'\n{2,}', text)
    
    # 빈 단락 제거 및 정리
    cleaned_paragraphs = [clean_text(p) for p in paragraphs if p.strip()]
    
    return cleaned_paragraphs

def merge_search_results(internal_results: List[Dict[str, Any]], 
                        external_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    내부 DB와 외부 API의 검색 결과를 통합합니다.
    """
    merged = []
    
    # 결과 정규화
    normalized_internal = [normalize_paper_info(paper) for paper in internal_results]
    normalized_external = [normalize_paper_info(paper) for paper in external_results]
    
    # 제목을 기준으로 중복 제거 (외부 결과 우선)
    seen_titles = set()
    
    # 외부 결과 먼저 추가
    for paper in normalized_external:
        title_lower = paper['title'].lower()
        if title_lower not in seen_titles:
            seen_titles.add(title_lower)
            merged.append(paper)
    
    # 내부 결과 추가 (중복 제외)
    for paper in normalized_internal:
        title_lower = paper['title'].lower()
        if title_lower not in seen_titles:
            seen_titles.add(title_lower)
            merged.append(paper)
    
    return merged

def save_to_cache(key: str, data: Any, cache_dir: str = "data/cache") -> bool:
    """
    데이터를 캐시에 저장합니다.
    """
    try:
        # 캐시 디렉토리 생성
        os.makedirs(cache_dir, exist_ok=True)
        
        # 캐시 파일 경로
        cache_file = os.path.join(cache_dir, f"{hash(key)}.json")
        
        # 캐시 데이터 구성
        cache_data = {
            "key": key,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        
        # JSON 파일로 저장
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        
        return True
        
    except Exception as e:
        logging.getLogger(__name__).error(f"캐시 저장 중 오류 발생: {str(e)}")
        return False

def load_from_cache(key: str, max_age_hours: int = 24, 
                   cache_dir: str = "data/cache") -> Optional[Any]:
    """
    캐시에서 데이터를 로드합니다. 지정된 시간보다 오래된 캐시는 무시합니다.
    """
    try:
        # 캐시 파일 경로
        cache_file = os.path.join(cache_dir, f"{hash(key)}.json")
        
        # 캐시 파일이 없는 경우
        if not os.path.exists(cache_file):
            return None
        
        # 캐시 데이터 로드
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        
        # 타임스탬프 확인
        cache_time = datetime.fromisoformat(cache_data["timestamp"])
        elapsed_hours = (datetime.now() - cache_time).total_seconds() / 3600
        
        # 캐시가 너무 오래된 경우
        if elapsed_hours > max_age_hours:
            return None
        
        return cache_data["data"]
        
    except Exception as e:
        logging.getLogger(__name__).error(f"캐시 로드 중 오류 발생: {str(e)}")
        return None

def clean_filename(filename: str) -> str:
    """
    파일 이름에서 사용할 수 없는 문자를 제거합니다.
    """
    # 금지된 문자 제거
    invalid_chars = r'[<>:"/\\|?*]'
    cleaned = re.sub(invalid_chars, '', filename)
    
    # 문장 끝 공백 및 마침표 제거
    cleaned = cleaned.rstrip('. ')
    
    # 빈 파일 이름인 경우 기본 이름 사용
    if not cleaned:
        cleaned = "untitled"
    
    # 최대 길이 제한
    if len(cleaned) > 100:
        cleaned = cleaned[:97] + "..."
    
    return cleaned
