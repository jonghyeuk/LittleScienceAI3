# app/routes/query_router.py
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
import logging
from pydantic import BaseModel
from app.services.scholar_api import ScholarService
from app.services.web_extractor import WebExtractorService
from app.services.nlp_processor import NLPService
from app.agents.query_agent import QueryAgent

router = APIRouter(tags=["주제 검색 및 분석"])
logger = logging.getLogger(__name__)

# 요청 및 응답 모델
class TopicRequest(BaseModel):
    topic: str
    keywords: Optional[List[str]] = None

class PaperInfo(BaseModel):
    title: str
    authors: str
    year: str
    abstract: str
    source: str
    url: Optional[str] = None
    keywords: List[str]
    type: str = "external"  # "internal" 또는 "external"

class TopicAnalysisResponse(BaseModel):
    definition: str
    issues: str
    cases: str

class SimilarPapersResponse(BaseModel):
    papers: List[PaperInfo]

class PaperContentRequest(BaseModel):
    topic: str
    paper_info: PaperInfo

class PaperContentResponse(BaseModel):
    introduction: str
    methods: str
    results: str
    conclusion: str
    references: str
    disclaimer: str
    niche_topics: List[str]

class NicheContentRequest(BaseModel):
    topic: str
    niche_topic: str

class NicheContentResponse(BaseModel):
    introduction: str
    methods: str
    expected_results: str
    disclaimer: str

# 서비스 의존성
def get_scholar_service():
    return ScholarService()

def get_web_extractor_service():
    return WebExtractorService()

def get_nlp_service():
    return NLPService()

def get_query_agent():
    return QueryAgent()

# 엔드포인트
@router.post("/analyze_topic", response_model=TopicAnalysisResponse)
async def analyze_topic(
    request: TopicRequest,
    scholar_service: ScholarService = Depends(get_scholar_service),
    nlp_service: NLPService = Depends(get_nlp_service),
):
    """
    주제에 대한 정의, 과학적/사회적 이슈, 해결/분석 사례 정보를 제공합니다.
    """
    try:
        logger.info(f"주제 분석 요청: {request.topic}")
        
        # 키워드가 제공되지 않았을 경우 NLP 서비스로 추출
        if not request.keywords:
            keywords = nlp_service.extract_keywords(request.topic)
            logger.info(f"추출된 키워드: {keywords}")
        else:
            keywords = request.keywords
        
        # 학술 정보 검색
        scholarly_info = scholar_service.get_topic_info(request.topic, keywords)
        
        # 주제 분석 정보 생성
        analysis = {
            "definition": scholarly_info.get("definition", "정의 정보를 찾을 수 없습니다."),
            "issues": scholarly_info.get("issues", "이슈 정보를 찾을 수 없습니다."),
            "cases": scholarly_info.get("cases", "사례 정보를 찾을 수 없습니다.")
        }
        
        return TopicAnalysisResponse(**analysis)
    
    except Exception as e:
        logger.error(f"주제 분석 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"주제 분석 중 오류가 발생했습니다: {str(e)}")

@router.post("/search_papers", response_model=SimilarPapersResponse)
async def search_papers(
    request: TopicRequest,
    scholar_service: ScholarService = Depends(get_scholar_service),
    web_extractor: WebExtractorService = Depends(get_web_extractor_service),
    nlp_service: NLPService = Depends(get_nlp_service),
):
    """
    주제와 관련된 유사 논문을 내부 DB와 외부 API에서 검색합니다.
    """
    try:
        logger.info(f"논문 검색 요청: {request.topic}")
        
        # 키워드가 제공되지 않았을 경우 NLP 서비스로 추출
        if not request.keywords:
            keywords = nlp_service.extract_keywords(request.topic)
            logger.info(f"추출된 키워드: {keywords}")
        else:
            keywords = request.keywords
        
        # 내부 DB 검색
        internal_papers = scholar_service.search_internal_db(request.topic, keywords)
        logger.info(f"내부 DB에서 {len(internal_papers)}개의 논문 검색됨")
        
        # 외부 API 검색
        external_papers = scholar_service.search_external_api(request.topic, keywords)
        logger.info(f"외부 API에서 {len(external_papers)}개의 논문 검색됨")
        
        # 결과 통합
        all_papers = internal_papers + external_papers
        
        return SimilarPapersResponse(papers=all_papers)
    
    except Exception as e:
        logger.error(f"논문 검색 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"논문 검색 중 오류가 발생했습니다: {str(e)}")

@router.post("/generate_paper_content", response_model=PaperContentResponse)
async def generate_paper_content(
    request: PaperContentRequest,
    query_agent: QueryAgent = Depends(get_query_agent),
):
    """
    선택한 논문을 바탕으로 논문 형식의 자료를 생성합니다.
    """
    try:
        logger.info(f"논문 형식 자료 생성 요청: {request.topic}, 선택 논문: {request.paper_info.title}")
        
        # LLM Agent를 통한 논문 형식 컨텐츠 생성
        paper_content = query_agent.generate_paper_content(request.topic, request.paper_info.dict())
        
        return PaperContentResponse(**paper_content)
    
    except Exception as e:
        logger.error(f"논문 형식 자료 생성 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"논문 형식 자료 생성 중 오류가 발생했습니다: {str(e)}")

@router.post("/generate_niche_content", response_model=NicheContentResponse)
async def generate_niche_content(
    request: NicheContentRequest,
    query_agent: QueryAgent = Depends(get_query_agent),
):
    """
    선택한 틈새주제에 대한 연구 계획을 생성합니다.
    """
    try:
        logger.info(f"틈새주제 연구 계획 생성 요청: {request.topic}, 틈새주제: {request.niche_topic}")
        
        # LLM Agent를 통한 틈새주제 컨텐츠 생성
        niche_content = query_agent.generate_niche_content(request.topic, request.niche_topic)
        
        return NicheContentResponse(**niche_content)
    
    except Exception as e:
        logger.error(f"틈새주제 연구 계획 생성 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"틈새주제 연구 계획 생성 중 오류가 발생했습니다: {str(e)}")

@router.get("/internal_papers", response_model=List[PaperInfo])
async def get_internal_papers(
    topic: Optional[str] = Query(None, description="검색할 주제"),
    keywords: Optional[str] = Query(None, description="쉼표로 구분된 키워드"),
    scholar_service: ScholarService = Depends(get_scholar_service),
):
    """
    내부 DB에서 논문을 검색합니다.
    """
    try:
        logger.info(f"내부 DB 논문 검색 요청: 주제={topic}, 키워드={keywords}")
        
        # 키워드 처리
        keyword_list = keywords.split(",") if keywords else []
        
        # 내부 DB 검색
        papers = scholar_service.search_internal_db(topic, keyword_list)
        
        return papers
    
    except Exception as e:
        logger.error(f"내부 DB 논문 검색 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"내부 DB 논문 검색 중 오류가 발생했습니다: {str(e)}")

@router.get("/external_papers", response_model=List[PaperInfo])
async def get_external_papers(
    topic: str = Query(..., description="검색할 주제"),
    keywords: Optional[str] = Query(None, description="쉼표로 구분된 키워드"),
    scholar_service: ScholarService = Depends(get_scholar_service),
):
    """
    외부 API에서 논문을 검색합니다.
    """
    try:
        logger.info(f"외부 API 논문 검색 요청: 주제={topic}, 키워드={keywords}")
        
        # 키워드 처리
        keyword_list = keywords.split(",") if keywords else []
        
        # 외부 API 검색
        papers = scholar_service.search_external_api(topic, keyword_list)
        
        return papers
    
    except Exception as e:
        logger.error(f"외부 API 논문 검색 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"외부 API 논문 검색 중 오류가 발생했습니다: {str(e)}")

@router.post("/generate_pdf", response_model=Dict[str, str])
async def generate_pdf(
    paper_content: Dict[str, Any],
    is_niche: bool = Query(False, description="틈새주제 여부"),
):
    """
    논문 형식 내용을 PDF로 변환합니다.
    """
    try:
        logger.info(f"PDF 생성 요청: 틈새주제={is_niche}")
        
        # 실제 PDF 생성 로직 (여기서는 예시로 생략)
        pdf_url = f"/api/download/pdf/{hash(str(paper_content))}"
        
        return {"pdf_url": pdf_url, "message": "PDF가 성공적으로 생성되었습니다."}
    
    except Exception as e:
        logger.error(f"PDF 생성 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"PDF 생성 중 오류가 발생했습니다: {str(e)}")
