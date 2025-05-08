# app/services/scholar_api.py
import logging
import requests
import json
import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

class ScholarService:
    """
    arXiv, CrossRef, SemanticScholar 등의 API를 사용하여 학술 정보를 검색하는 서비스
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # API 키 로드
        self.semantic_scholar_api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY", "")
        self.crossref_email = os.getenv("CROSSREF_EMAIL", "")
        
        # API 엔드포인트
        self.arxiv_api_url = "http://export.arxiv.org/api/query"
        self.crossref_api_url = "https://api.crossref.org/works"
        self.semantic_scholar_api_url = "https://api.semanticscholar.org/graph/v1/paper/search"
        
        # 내부 DB 파일 경로
        self.internal_db_path = os.getenv("INTERNAL_DB_PATH", "data/internal_papers.json")
        
        # 내부 DB 로드
        self.internal_db = self.load_internal_db()
    
    def load_internal_db(self) -> List[Dict[str, Any]]:
        """
        내부 DB 파일을 로드합니다. 파일이 없으면 샘플 데이터를 반환합니다.
        """
        try:
            if os.path.exists(self.internal_db_path):
                with open(self.internal_db_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                self.logger.warning(f"내부 DB 파일을 찾을 수 없습니다: {self.internal_db_path}")
                # 샘플 데이터 반환
                return [
                    {
                        "title": "광촉매를 이용한 미세플라스틱 분해 연구",
                        "authors": "김지원, 이하늘",
                        "year": "2023",
                        "abstract": "본 연구는 TiO2 기반 광촉매를 활용하여 해양 미세플라스틱을 효과적으로 분해할 수 있는 방법을 탐구하였다.",
                        "source": "제65회 한국과학전람회",
                        "keywords": ["광촉매", "미세플라스틱", "환경오염", "해양생태계"],
                        "type": "internal"
                    },
                    {
                        "title": "기후변화가 제주도 감귤 생산에 미치는 영향 분석",
                        "authors": "박민준, 정소율",
                        "year": "2022",
                        "abstract": "제주도 지역의 10년간 기후 데이터와 감귤 생산량 데이터를 분석하여 온도 상승이 과실 품질과 수확량에 미치는 영향을 조사하였다.",
                        "source": "제64회 전국과학전람회",
                        "keywords": ["기후변화", "농업", "감귤", "생산량 분석"],
                        "type": "internal"
                    },
                    {
                        "title": "머신러닝을 활용한 식물 질병 조기 진단 시스템 개발",
                        "authors": "최준호, 이민지",
                        "year": "2023",
                        "abstract": "컴퓨터 비전과 딥러닝 기술을 활용하여 작물 잎의 이미지만으로 질병을 조기에 진단할 수 있는 모바일 애플리케이션을 개발하였다.",
                        "source": "2023 청소년과학탐구대회",
                        "keywords": ["머신러닝", "식물병리학", "스마트팜", "컴퓨터 비전"],
                        "type": "internal"
                    }
                ]
        except Exception as e:
            self.logger.error(f"내부 DB 로드 중 오류 발생: {str(e)}")
            return []
    
    def search_internal_db(self, topic: str, keywords: List[str]) -> List[Dict[str, Any]]:
        """
        내부 DB에서 주제와 키워드에 맞는 논문을 검색합니다.
        """
        try:
            results = []
            
            # 키워드와 주제를 소문자로 변환
            topic_lower = topic.lower()
            keywords_lower = [k.lower() for k in keywords]
            
            for paper in self.internal_db:
                # 제목이나 초록에 주제가 포함되거나 키워드가 일치하는 경우 결과에 추가
                title_lower = paper["title"].lower()
                abstract_lower = paper["abstract"].lower()
                paper_keywords_lower = [k.lower() for k in paper["keywords"]]
                
                if (topic_lower in title_lower or topic_lower in abstract_lower or
                    any(k in title_lower or k in abstract_lower for k in keywords_lower) or
                    any(k in paper_keywords_lower for k in keywords_lower)):
                    results.append(paper)
            
            return results
        except Exception as e:
            self.logger.error(f"내부 DB 검색 중 오류 발생: {str(e)}")
            return []
    
    def search_arxiv(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        arXiv API를 통해 논문을 검색합니다.
        """
        try:
            # arXiv API 요청 파라미터
            params = {
                'search_query': f'all:{query}',
                'start': 0,
                'max_results': max_results,
                'sortBy': 'relevance',
                'sortOrder': 'descending'
            }
            
            # arXiv API 호출
            response = requests.get(self.arxiv_api_url, params=params)
            
            if response.status_code != 200:
                self.logger.error(f"arXiv API 호출 실패: {response.status_code}")
                return []
            
            # XML 응답 처리 (실제 구현에서는 XML 파싱 라이브러리 사용 필요)
            # 여기서는 단순화를 위해 샘플 데이터 반환
            return [
                {
                    "title": f"arXiv: {query}에 관한 최신 연구 동향",
                    "authors": "Smith et al.",
                    "year": "2023",
                    "abstract": f"This paper reviews recent advances in {query} research, focusing on methodological approaches and key findings.",
                    "source": "arXiv:2301.12345",
                    "url": f"https://arxiv.org/abs/2301.12345",
                    "keywords": ["literature review", "methodology", query],
                    "type": "external"
                }
            ]
        except Exception as e:
            self.logger.error(f"arXiv API 검색 중 오류 발생: {str(e)}")
            return []
    
    def search_crossref(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        CrossRef API를 통해 논문을 검색합니다.
        """
        try:
            # CrossRef API 요청 파라미터
            params = {
                'query': query,
                'rows': max_results,
                'sort': 'relevance',
                'order': 'desc'
            }
            
            # 이메일이 설정된 경우 추가
            if self.crossref_email:
                params['mailto'] = self.crossref_email
            
            # CrossRef API 호출
            response = requests.get(self.crossref_api_url, params=params)
            
            if response.status_code != 200:
                self.logger.error(f"CrossRef API 호출 실패: {response.status_code}")
                return []
            
            # JSON 응답 처리
            data = response.json()
            
            # 여기서는 단순화를 위해 샘플 데이터 반환
            return [
                {
                    "title": f"CrossRef: {query}의 실험적 분석",
                    "authors": "Johnson et al.",
                    "year": "2022",
                    "abstract": f"An experimental analysis of {query} demonstrating significant improvements in efficiency and performance compared to conventional methods.",
                    "source": "Journal of Scientific Research",
                    "url": "https://doi.org/10.1234/example.5678",
                    "keywords": ["experimental analysis", "efficiency", "performance"],
                    "type": "external"
                }
            ]
        except Exception as e:
            self.logger.error(f"CrossRef API 검색 중 오류 발생: {str(e)}")
            return []
    
    def search_semantic_scholar(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Semantic Scholar API를 통해 논문을 검색합니다.
        """
        try:
            # Semantic Scholar API 요청 파라미터
            params = {
                'query': query,
                'limit': max_results,
                'fields': 'title,authors,year,abstract,venue,url,keywords'
            }
            
            # 헤더 설정
            headers = {}
            if self.semantic_scholar_api_key:
                headers['x-api-key'] = self.semantic_scholar_api_key
            
            # Semantic Scholar API 호출
            response = requests.get(self.semantic_scholar_api_url, params=params, headers=headers)
            
            if response.status_code != 200:
                self.logger.error(f"Semantic Scholar API 호출 실패: {response.status_code}")
                return []
            
            # 여기서는 단순화를 위해 샘플 데이터 반환
            return [
                {
                    "title": f"Semantic Scholar: {query}에 대한 체계적 문헌 고찰",
                    "authors": "Zhang et al.",
                    "year": "2023",
                    "abstract": f"A systematic review of literature on {query}, synthesizing findings from 50 recent studies and identifying key research gaps.",
                    "source": "Annual Review of Science",
                    "url": "https://doi.org/10.5678/review.1234",
                    "keywords": ["systematic review", "research gaps", "literature synthesis"],
                    "type": "external"
                }
            ]
        except Exception as e:
            self.logger.error(f"Semantic Scholar API 검색 중 오류 발생: {str(e)}")
            return []
    
    def search_external_api(self, topic: str, keywords: List[str]) -> List[Dict[str, Any]]:
        """
        외부 API(arXiv, CrossRef, SemanticScholar)를 통해 논문을 검색합니다.
        """
        try:
            # 검색 쿼리 생성
            query = topic
            if keywords:
                query += " " + " ".join(keywords[:3])  # 최대 3개 키워드 사용
            
            # 각 API로 검색
            arxiv_results = self.search_arxiv(query, max_results=2)
            crossref_results = self.search_crossref(query, max_results=2)
            semantic_scholar_results = self.search_semantic_scholar(query, max_results=2)
            
            # 결과 통합
            all_results = arxiv_results + crossref_results + semantic_scholar_results
            
            return all_results
        except Exception as e:
            self.logger.error(f"외부 API 검색 중 오류 발생: {str(e)}")
            return []
    
    def get_topic_info(self, topic: str, keywords: List[str]) -> Dict[str, str]:
        """
        주제에 대한 정의, 과학적/사회적 이슈, 해결/분석 사례 정보를 생성합니다.
        실제 구현에서는 LLM API를 호출하거나 추가 처리가 필요합니다.
        """
        try:
            # 여기서는 단순화를 위해 정적 텍스트 반환
            return {
                "definition": f"""
                {topic}은(는) 현대 과학 연구에서 중요한 주제로, 다양한 분야에서 활발히 연구되고 있습니다. 
                
                이 주제는 기본적으로 [주제에 대한 상세 정의와 배경 설명]을 다루며, 최근에는 [최신 연구 동향이나 변화된 관점]으로 그 중요성이 더욱 부각되고 있습니다.
                
                {topic}에 대한 연구는 [관련 학문 분야]에서 특히 중요하게 다뤄지며, [주요 이론이나 개념] 등의 핵심 이론을 바탕으로 발전해왔습니다.
                """,
                
                "issues": f"""
                {topic}과(와) 관련된 주요 과학적 이슈:
                
                1. [이슈 1]: [상세 설명 및 현재 상황]
                2. [이슈 2]: [상세 설명 및 현재 상황]
                3. [이슈 3]: [상세 설명 및 현재 상황]
                
                {topic}과(와) 관련된 주요 사회적 이슈:
                
                1. [사회적 이슈 1]: [사회적 영향 및 중요성]
                2. [사회적 이슈 2]: [사회적 영향 및 중요성]
                3. [사회적 이슈 3]: [사회적 영향 및 중요성]
                
                이러한 이슈들은 [이슈들의 상호연관성이나 영향관계]와 같은 복합적인 관계를 형성하고 있어 통합적인 접근이 필요합니다.
                """,
                
                "cases": f"""
                {topic}에 관한 주요 연구 및 해결 사례:
                
                1. [사례 연구 1]:
                   - 연구자/기관: [연구자/기관명]
                   - 주요 방법론: [사용된 방법론]
                   - 주요 발견: [중요한 연구 결과]
                   - 한계점: [연구의 한계]
                
                2. [사례 연구 2]:
                   - 연구자/기관: [연구자/기관명]
                   - 주요 방법론: [사용된 방법론]
                   - 주요 발견: [중요한 연구 결과]
                   - 한계점: [연구의 한계]
                
                3. [사례 연구 3]:
                   - 연구자/기관: [연구자/기관명]
                   - 주요 방법론: [사용된 방법론]
                   - 주요 발견: [중요한 연구 결과]
                   - 한계점: [연구의 한계]
                
                현재 진행 중인 주요 연구 방향:
                - [연구 방향 1]: [상세 설명]
                - [연구 방향 2]: [상세 설명]
                - [연구 방향 3]: [상세 설명]
                """
            }
        except Exception as e:
            self.logger.error(f"주제 정보 생성 중 오류 발생: {str(e)}")
            return {
                "definition": "정의 정보를 생성하는 도중 오류가 발생했습니다.",
                "issues": "이슈 정보를 생성하는 도중 오류가 발생했습니다.",
                "cases": "사례 정보를 생성하는 도중 오류가 발생했습니다."
            }
