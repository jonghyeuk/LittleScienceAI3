# frontend/dashboard.py
import streamlit as st
from streamlit_extras.colored_header import colored_header
from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_extras.stateful_button import button
import streamlit.components.v1 as components
import streamlit_antd_components as sac
import time
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
import base64
from io import BytesIO

# 페이지 설정
st.set_page_config(
    page_title="LittleScienceAI 도우미",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일 정의
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E88E5;
        margin-bottom: 1rem;
    }
    .sub-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #0D47A1;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .box-container {
        background-color: #F5F7FA;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        border-left: 4px solid #1E88E5;
    }
    .info-box {
        background-color: #E3F2FD;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
    }
    .fade-text {
        color: #757575;
    }
    .highlight-text {
        color: #0D47A1;
        font-weight: 600;
    }
    .paper-card {
        background-color: white;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        transition: transform 0.3s;
    }
    .paper-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .step-container {
        border-left: 2px solid #1E88E5;
        padding-left: 20px;
        margin-left: 10px;
    }
    .step-item {
        margin-bottom: 15px;
    }
    .step-number {
        background-color: #1E88E5;
        color: white;
        width: 25px;
        height: 25px;
        border-radius: 50%;
        display: inline-flex;
        justify-content: center;
        align-items: center;
        margin-right: 10px;
    }
    .typing-effect {
        overflow: hidden;
        border-right: .15em solid orange;
        white-space: nowrap;
        letter-spacing: .10em;
        animation: 
            typing 3.5s steps(40, end),
            blink-caret .75s step-end infinite;
    }
    @keyframes typing {
        from { width: 0 }
        to { width: 100% }
    }
    @keyframes blink-caret {
        from, to { border-color: transparent }
        50% { border-color: orange; }
    }
</style>
""", unsafe_allow_html=True)

# 애니메이션 효과 함수
def typing_effect(text, container, speed=0.03):
    placeholder = container.empty()
    for i in range(len(text) + 1):
        placeholder.markdown(f"<div class='typing-effect'>{text[:i]}</div>", unsafe_allow_html=True)
        time.sleep(speed)

# 사이드바 및 앱 상태 관리
def initialize_session_state():
    if 'step' not in st.session_state:
        st.session_state.step = 1
    if 'topic' not in st.session_state:
        st.session_state.topic = ""
    if 'topic_analysis' not in st.session_state:
        st.session_state.topic_analysis = {}
    if 'papers' not in st.session_state:
        st.session_state.papers = []
    if 'selected_paper_index' not in st.session_state:
        st.session_state.selected_paper_index = 0
    if 'paper_content' not in st.session_state:
        st.session_state.paper_content = {}
    if 'niche_topics' not in st.session_state:
        st.session_state.niche_topics = []
    if 'selected_niche_index' not in st.session_state:
        st.session_state.selected_niche_index = 0
    if 'niche_content' not in st.session_state:
        st.session_state.niche_content = {}

def render_sidebar():
    with st.sidebar:
        st.image("https://via.placeholder.com/100x100.png?text=🔬", width=100)
        st.markdown("<div class='main-title'>LittleScienceAI</div>", unsafe_allow_html=True)
        st.markdown("##### 과학소논문 주제선정 도우미")
        
        add_vertical_space(2)
        
        progress = int((st.session_state.step / 8) * 100)
        st.progress(progress)
        
        add_vertical_space(1)
        
        # 단계별 상태 표시
        steps = [
            "주제 입력",
            "주제 분석",
            "관련 연구 정보",
            "유사 논문 검색",
            "논문 선택",
            "논문형식 제공",
            "틈새주제 제안",
            "PDF 다운로드"
        ]
        
        st.markdown("<div class='step-container'>", unsafe_allow_html=True)
        for i, step in enumerate(steps, 1):
            if i < st.session_state.step:
                st.markdown(f"""
                <div class='step-item'>
                    <span class='step-number'>{i}</span>
                    <span style='color: #1E88E5; text-decoration: line-through;'>{step}</span>
                    <span style='color: green;'>✓</span>
                </div>
                """, unsafe_allow_html=True)
            elif i == st.session_state.step:
                st.markdown(f"""
                <div class='step-item'>
                    <span class='step-number'>{i}</span>
                    <span style='color: #1E88E5; font-weight: bold;'>{step}</span>
                    <span style='color: orange;'>●</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class='step-item'>
                    <span class='step-number' style='background-color: #BDBDBD;'>{i}</span>
                    <span style='color: #757575;'>{step}</span>
                </div>
                """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 다음 단계로 진행
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("이전", key="prev_step2"):
            st.session_state.step = 1
            st.rerun()
    with col2:
        if st.button("다음: 과학적/사회적 이슈 확인", type="primary", key="next_step2"):
            st.session_state.step = 3
            st.rerun()

def render_step3_research_info():
    st.markdown(f"<div class='main-title'>'{st.session_state.topic}' 관련 이슈 및 연구 정보</div>", unsafe_allow_html=True)
    
    # 시뮬레이션: 실제로는 AI 생성 내용 필요
    if 'issues' not in st.session_state.topic_analysis:
        with st.spinner("관련 이슈와 연구 정보를 분석 중입니다..."):
            time.sleep(2)  # 로딩 시뮬레이션
            
            # 샘플 데이터 (실제 구현에서는 API 호출 결과로 대체)
            st.session_state.topic_analysis['issues'] = f"""
            {st.session_state.topic}과(와) 관련된 주요 과학적 이슈:
            
            1. [이슈 1]: [상세 설명 및 현재 상황]
            2. [이슈 2]: [상세 설명 및 현재 상황]
            3. [이슈 3]: [상세 설명 및 현재 상황]
            
            {st.session_state.topic}과(와) 관련된 주요 사회적 이슈:
            
            1. [사회적 이슈 1]: [사회적 영향 및 중요성]
            2. [사회적 이슈 2]: [사회적 영향 및 중요성]
            3. [사회적 이슈 3]: [사회적 영향 및 중요성]
            
            이러한 이슈들은 [이슈들의 상호연관성이나 영향관계]와 같은 복합적인 관계를 형성하고 있어 통합적인 접근이 필요합니다.
            """
            
            st.session_state.topic_analysis['cases'] = f"""
            {st.session_state.topic}에 관한 주요 연구 및 해결 사례:
            
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
    
    # 탭으로 정보 구분
    tab1, tab2 = st.tabs(["과학적/사회적 이슈", "해결/분석 사례"])
    
    with tab1:
        st.markdown("<div class='box-container'>", unsafe_allow_html=True)
        st.markdown(st.session_state.topic_analysis['issues'])
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab2:
        st.markdown("<div class='box-container'>", unsafe_allow_html=True)
        st.markdown(st.session_state.topic_analysis['cases'])
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 다음 단계로 진행
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("이전", key="prev_step3"):
            st.session_state.step = 2
            st.rerun()
    with col2:
        if st.button("다음: 유사 논문 검색", type="primary", key="next_step3"):
            st.session_state.step = 4
            st.rerun()

def render_step4_similar_papers():
    st.markdown(f"<div class='main-title'>'{st.session_state.topic}' 관련 유사 논문</div>", unsafe_allow_html=True)
    
    if not st.session_state.papers:
        with st.spinner("유사 논문을 검색 중입니다..."):
            time.sleep(3)  # 로딩 시뮬레이션
            
            # 샘플 데이터 (실제 구현에서는 API 호출 결과로 대체)
            st.session_state.papers = [
                {
                    "title": f"{st.session_state.topic}의 최신 연구 동향 분석",
                    "authors": "김지원, 이하늘",
                    "year": "2023",
                    "abstract": f"본 연구는 {st.session_state.topic}에 관한 최신 연구 동향을 체계적으로 분석하고, 향후 연구 방향을 제시하였다. 특히 [핵심 연구 결과]는 이 분야의 새로운 시각을 제공한다.",
                    "source": "제65회 한국과학전람회",
                    "keywords": ["최신동향", "연구방법론", "시스템적 접근"],
                    "type": "internal"
                },
                {
                    "title": f"{st.session_state.topic} 영향 평가 방법론 개발",
                    "authors": "박민준, 정소율",
                    "year": "2022",
                    "abstract": f"{st.session_state.topic}의 영향을 정량적으로 평가할 수 있는 새로운 방법론을 개발하고, 실제 사례에 적용하여 그 효과성을 검증하였다. 이 방법론은 [장점 및 차별점]의 특징을 가진다.",
                    "source": "제64회 전국과학전람회",
                    "keywords": ["방법론", "정량평가", "사례연구"],
                    "type": "internal"
                },
                {
                    "title": f"{st.session_state.topic}이 환경에 미치는 영향 연구",
                    "authors": "Johnson et al.",
                    "year": "2023",
                    "abstract": f"This study investigated the environmental impact of {st.session_state.topic}, focusing on [specific aspect]. The results demonstrate [key findings] which have significant implications for [relevant field].",
                    "source": "Environmental Science & Technology",
                    "url": "https://example.com/paper1",
                    "keywords": ["environmental impact", "sustainable development", "ecological assessment"],
                    "type": "external"
                },
                {
                    "title": f"{st.session_state.topic}에 관한 통합적 접근 방법",
                    "authors": "Zhang et al.",
                    "year": "2024",
                    "abstract": f"This paper presents an integrated approach to {st.session_state.topic}, combining [methodological approach]. Our findings suggest that [key conclusion] which contributes to the growing body of literature on this topic.",
                    "source": "Journal of Advanced Research",
                    "url": "https://example.com/paper2",
                    "keywords": ["integrated approach", "methodology", "multi-disciplinary"],
                    "type": "external"
                },
                {
                    "title": f"{st.session_state.topic}의 교육적 활용 방안",
                    "authors": "최준호, 이민지",
                    "year": "2023",
                    "abstract": f"{st.session_state.topic}을 고등학교 과학 교육에 효과적으로 활용할 수 있는 방안을 연구하고, 실제 수업에 적용한 결과를 분석하였다. 학생들의 과학적 사고력과 탐구능력 향상에 유의미한 효과가 있음을 확인하였다.",
                    "source": "2023 청소년과학탐구대회",
                    "keywords": ["과학교육", "교수학습방법", "STEAM"],
                    "type": "internal"
                }
            ]
    
    # 내부 DB와 외부 API 검색 결과 구분
    st.markdown("<div class='sub-title'>내부 DB 검색 결과</div>", unsafe_allow_html=True)
    
    internal_papers = [p for p in st.session_state.papers if p.get('type') == 'internal']
    for i, paper in enumerate(internal_papers):
        with st.expander(f"📄 {paper['title']} ({paper['year']})"):
            st.markdown(f"**저자:** {paper['authors']}")
            st.markdown(f"**초록:** {paper['abstract']}")
            st.markdown(f"**출처:** {paper['source']}")
            st.markdown(f"**키워드:** {', '.join(paper['keywords'])}")
            if st.button(f"이 논문 선택하기", key=f"select_internal_{i}"):
                st.session_state.selected_paper_index = st.session_state.papers.index(paper)
                st.session_state.step = 5
                st.rerun()
    
    st.markdown("<div class='sub-title'>외부 API 검색 결과</div>", unsafe_allow_html=True)
    
    external_papers = [p for p in st.session_state.papers if p.get('type') == 'external']
    for i, paper in enumerate(external_papers):
        with st.expander(f"🔍 {paper['title']} ({paper['year']})"):
            st.markdown(f"**저자:** {paper['authors']}")
            st.markdown(f"**초록:** {paper['abstract']}")
            st.markdown(f"**출처:** {paper['source']}")
            if 'url' in paper:
                st.markdown(f"**링크:** [{paper['source']}]({paper['url']})")
            st.markdown(f"**키워드:** {', '.join(paper['keywords'])}")
            if st.button(f"이 논문 선택하기", key=f"select_external_{i}"):
                st.session_state.selected_paper_index = st.session_state.papers.index(paper)
                st.session_state.step = 5
                st.rerun()
    
    # 키워드 기반 시각화
    st.markdown("<div class='sub-title'>주요 키워드 분석</div>", unsafe_allow_html=True)
    
    # 키워드 빈도 계산
    keyword_counts = {}
    for paper in st.session_state.papers:
        for keyword in paper['keywords']:
            if keyword in keyword_counts:
                keyword_counts[keyword] += 1
            else:
                keyword_counts[keyword] = 1
    
    # 워드클라우드 대신 막대 그래프로 시각화 (실제 구현에서는 워드클라우드 사용 가능)
    sorted_keywords = dict(sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True))
    top_keywords = {k: sorted_keywords[k] for k in list(sorted_keywords)[:8]}
    
    fig = px.bar(
        x=list(top_keywords.keys()),
        y=list(top_keywords.values()),
        labels={'x': '키워드', 'y': '논문 수'},
        color_discrete_sequence=['#1E88E5']
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=0),
        height=300
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # 다음 단계로 진행
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("이전", key="prev_step4"):
            st.session_state.step = 3
            st.rerun()
    with col2:
        if st.button("다음: 논문 선택", type="primary", key="next_step4"):
            st.session_state.step = 5
            st.rerun()

def render_step5_paper_selection():
    st.markdown("<div class='main-title'>관심 논문 선택</div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='box-container'>
        <p>아래 목록에서 더 탐구하고 싶은 논문을 선택해 주세요. 선택한 논문을 바탕으로 논문 형식의 자료를 생성합니다.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 논문 목록 표시
    paper_options = [f"{paper['title']} ({paper['authors']}, {paper['year']})" for paper in st.session_state.papers]
    selected_option = st.selectbox("논문 선택:", options=paper_options, index=st.session_state.selected_paper_index)
    st.session_state.selected_paper_index = paper_options.index(selected_option)
    
    # 선택된 논문 정보 표시
    selected_paper = st.session_state.papers[st.session_state.selected_paper_index]
    
    st.markdown("<div class='paper-card'>", unsafe_allow_html=True)
    st.markdown(f"#### 📄 {selected_paper['title']}")
    st.markdown(f"**저자:** {selected_paper['authors']}")
    st.markdown(f"**출판년도:** {selected_paper['year']}")
    st.markdown(f"**출처:** {selected_paper['source']}")
    st.markdown(f"**초록:**")
    st.markdown(f"{selected_paper['abstract']}")
    st.markdown(f"**키워드:** {', '.join(selected_paper['keywords'])}")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 다음 단계로 진행
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("이전", key="prev_step5"):
            st.session_state.step = 4
            st.rerun()
    with col2:
        if st.button("선택한 논문으로 진행", type="primary", key="next_step5"):
            st.session_state.step = 6
            st.rerun()

def render_step6_paper_format():
    st.markdown("<div class='main-title'>논문 형식 자료</div>", unsafe_allow_html=True)
    
    if not st.session_state.paper_content:
        with st.spinner("논문 형식 자료를 생성 중입니다..."):
            time.sleep(3)  # 로딩 시뮬레이션
            
            selected_paper = st.session_state.papers[st.session_state.selected_paper_index]
            
            # 샘플 데이터 (실제 구현에서는 API 호출 결과로 대체)
            st.session_state.paper_content = {
                "introduction": f"""
                # 서론
                
                {st.session_state.topic}은(는) 현대 과학계에서 중요한 연구 주제로 부각되고 있다. 특히 {selected_paper['keywords'][0]}와(과) 
                관련하여 많은 연구자들이 관심을 보이고 있으나, 아직까지 [구체적인 연구 공백]에 대한 심층적 탐구는 
                부족한 실정이다. 본 연구는 {selected_paper['title']}에서 영감을 받아, [연구 목적과 중요성]을 규명하고자 한다.
                
                기존 연구들은 주로 [기존 연구 접근법]에 초점을 맞추어 왔으나, 이는 [한계점]이라는 한계를 보인다. 
                이에 본 연구는 [차별화된 접근법]을 통해 새로운 관점에서 {st.session_state.topic}을(를) 탐구하고자 한다. 
                특히 [핵심 연구 질문]에 대한 답을 찾는 과정에서 [예상되는 기여점]을 제공할 수 있을 것으로 기대된다.
                """,
                
                "methods": f"""
                # 연구 방법
                
                ## 연구 설계
                본 연구는 [연구 설계 개요: 정량적/정성적/혼합적 접근법]을 통해 {st.session_state.topic}에 접근하였다. 
                [연구 설계의 논리적 근거]를 바탕으로 다음과 같은 절차로 연구를 진행하였다.
                
                ## 데이터 수집
                본 연구에서는 [데이터 수집 방법]을 통해 자료를 수집하였다. 구체적으로는 [데이터 소스, 
                표본 크기, 표본 추출 방법]을 활용하였으며, [데이터 수집 기간]동안 자료를 수집했다.
                
                ## 분석 방법
                수집된 데이터는 [분석 방법론, 통계적 기법, 분석 도구]를 활용하여 분석하였다. 
                특히 [핵심 분석 절차]를 중심으로 [분석 단계별 상세 방법]에 따라 체계적으로 분석을 수행하였다.
                
                ## 윤리적 고려사항
                본 연구를 수행함에 있어 [관련 윤리적 고려사항]을 준수하였으며, 
                필요한 경우 [기관윤리위원회 승인 정보]를 획득하였다.
                """,
                
                "results": f"""
                # 연구 결과
                
                ## 주요 발견 1
                [주요 발견 1에 대한 상세 설명]
                
                ## 주요 발견 2
                [주요 발견 2에 대한 상세 설명]
                
                ## 주요 발견 3
                [주요 발견 3에 대한 상세 설명]
                
                이상의 결과들은 {st.session_state.topic}에 대한 새로운 이해를 제공하며, 특히 [중요한 통찰점]을 
                시사한다. 이는 기존의 [관련 연구 결과]와 [유사점/차이점]을 보이는데, 
                그 이유는 [결과 차이에 대한 해석]일 것으로 추정된다.
                """,
                
                "conclusion": f"""
                # 결론 및 제언
                
                본 연구는 {st.session_state.topic}에 대한 [핵심 연구 질문]을 탐구하였다. 연구 결과를 종합하면, 
                [주요 결론 1], [주요 결론 2], 그리고 [주요 결론 3]와 같은 결론을 도출할 수 있다.
                
                이러한 발견은 [학문적/실용적 의의]를 지니며, 향후 [관련 분야]에서 [영향 및 활용 방안]으로 
                활용될 수 있을 것이다. 특히 [핵심 시사점]은 [관련 이해관계자]에게 중요한 참고자료가 될 것으로 사료된다.
                
                본 연구의 한계점으로는 [연구의 한계 1], [연구의 한계 2]가 있으며, 
                이를 보완하기 위한 후속 연구로 [후속 연구 제안 1], [후속 연구 제안 2]를 제안한다.
                """,
                
                "references": f"""
                # 참고문헌
                
                1. {selected_paper['authors']} ({selected_paper['year']}). {selected_paper['title']}. *{selected_paper['source']}*.
                2. [참고문헌 2]
                3. [참고문헌 3]
                4. [참고문헌 4]
                5. [참고문헌 5]
                """,
                
                "disclaimer": f"""
                # 중요 안내
                
                이 내용은 AI에 의해 추론된 자료로, 실제 논문이 아닙니다. 참조용으로만 활용하시기 바라며, 
                여기에 제시된 참고문헌은 실제 인용이나 학술적 활용이 불가능할 수 있습니다. 
                실제 연구를 위해서는 추가적인 문헌 조사와 검증이 필요합니다.
                """
            }
            
            # 틈새 주제 생성
            st.session_state.niche_topics = [
                f"{st.session_state.topic}의 [틈새 주제 영역 1]에 관한 연구",
                f"[키워드 조합]을 활용한 {st.session_state.topic} 문제 해결 방안",
                f"{selected_paper['keywords'][0]}와(과) {st.session_state.topic}의 상관관계 분석",
                f"{st.session_state.topic}이 [관련 분야]에 미치는 장기적 영향 연구",
                f"[새로운 방법론]을 적용한 {st.session_state.topic} 탐구"
            ]
    
    # 탭으로 나누어 표시
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["서론", "연구 방법", "연구 결과", "결론 및 제언", "참고문헌"])
    
    with tab1:
        st.markdown("<div class='box-container'>", unsafe_allow_html=True)
        st.markdown(st.session_state.paper_content["introduction"])
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab2:
        st.markdown("<div class='box-container'>", unsafe_allow_html=True)
        st.markdown(st.session_state.paper_content["methods"])
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab3:
        st.markdown("<div class='box-container'>", unsafe_allow_html=True)
        st.markdown(st.session_state.paper_content["results"])
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab4:
        st.markdown("<div class='box-container'>", unsafe_allow_html=True)
        st.markdown(st.session_state.paper_content["conclusion"])
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab5:
        st.markdown("<div class='box-container'>", unsafe_allow_html=True)
        st.markdown(st.session_state.paper_content["references"])
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.warning(st.session_state.paper_content["disclaimer"])
    
    # PDF 다운로드 버튼
    pdf_data = create_pdf_buffer(st.session_state.paper_content, f"{st.session_state.topic}에 관한 연구")
    st.download_button(
        label="논문 형식 PDF 다운로드",
        data=pdf_data,
        file_name=f"{st.session_state.topic}_research_plan.pdf",
        mime="application/pdf",
    )
    
    # 다음 단계로 진행
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("이전", key="prev_step6"):
            st.session_state.step = 5
            st.rerun()
    with col2:
        if st.button("다음: 틈새주제 탐색", type="primary", key="next_step6"):
            st.session_state.step = 7
            st.rerun()

def render_step7_niche_topics():
    st.markdown("<div class='main-title'>틈새 연구주제 제안</div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='box-container'>
        <p>아래는 정보 정리 과정에서 발견된 틈새 연구주제입니다. 
        이들은 아직 충분히 연구되지 않았거나 새로운 관점에서 접근할 수 있는 주제들입니다.</p>
        <p>관심 있는 틈새주제를 선택하시면 해당 주제에 대한 연구 계획을 제공해 드립니다.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 틈새 주제 표시 및 선택
    selected_niche = st.radio("틈새주제 선택:", st.session_state.niche_topics, index=st.session_state.selected_niche_index)
    st.session_state.selected_niche_index = st.session_state.niche_topics.index(selected_niche)
    
    if st.button("선택한 틈새주제 탐색", type="primary"):
        # 선택한 틈새주제 내용 생성
        with st.spinner("틈새주제 연구 계획을 생성 중입니다..."):
            time.sleep(2)  # 로딩 시뮬레이션
            
            # 샘플 데이터 (실제 구현에서는 API 호출 결과로 대체)
            st.session_state.niche_content = {
                "introduction": f"""
                # 서론
                
                {selected_niche}은(는) {st.session_state.topic} 연구 분야 내에서 새롭게 주목받고 있는 영역이다. 
                특히 [틈새 주제의 중요성과 배경]에 비추어볼 때, 이 주제에 대한 체계적인 탐구는 
                [기대되는 학문적/실용적 기여]를 가져올 것으로 예상된다.
                
                현재까지 {st.session_state.topic}에 관한 연구는 주로 [기존 연구 동향]에 초점을 맞추어 왔으나, 
                [틈새 주제의 차별점]에 대한 연구는 상대적으로 부족한 실정이다. 
                본 연구는 이러한 연구 공백을 메우기 위해 [연구 목적]을 설정하고, 
                [핵심 연구 질문]을 탐구하고자 한다.
                """,
                
                "methods": f"""
                # 연구 방법
                
                ## 연구 설계
                본 연구는 {selected_niche}을(를) 탐구하기 위해 [연구 설계 접근법]을 채택하였다. 
                이는 [연구 설계의 근거]를 바탕으로 선정되었으며, [연구 절차 개요]와 같은 단계로 진행될 예정이다.
                
                ## 자료 수집 방법
                {selected_niche}에 관한 자료는 [데이터 수집 방법]을 통해 수집될 것이다. 
                구체적으로는 [데이터 소스, 표본 크기, 표본 추출 방법]을 활용하여 
                [데이터 수집 기간] 동안 ", unsafe_allow_html=True)
        
        add_vertical_space(2)
        
        # 현재 주제 표시
        if st.session_state.topic:
            st.info(f"현재 주제: {st.session_state.topic}")
        
        add_vertical_space(2)
        
        # 새로 시작하기 버튼
        if st.button("새로 시작하기"):
            for key in list(st.session_state.keys()):
                if key != 'step':
                    del st.session_state[key]
            st.session_state.step = 1
            st.rerun()

# 단계별 렌더링 함수
def render_step1_topic_input():
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("<div class='main-title'>과학소논문 주제 탐색하기</div>", unsafe_allow_html=True)
        st.markdown("""
        <div class='box-container'>
            <p>안녕하세요! LittleScienceAI 도우미입니다.</p>
            <p>고등학생 수준의 과학 소논문 작성을 위한 <span class='highlight-text'>주제 선정</span>을 도와드립니다.</p>
            <p>관심 있는 과학 연구 주제를 입력해 주세요. 주제에 대한 심층 분석, 관련 논문 검색, 
            그리고 논문 형식의 자료 생성까지 원스톱으로 지원합니다.</p>
        </div>
        """, unsafe_allow_html=True)
        
        topic = st.text_input("연구 주제를 입력해 주세요:", placeholder="예: 미세플라스틱의 환경 영향, 인공지능 윤리, 세포 유전학 등")
        
        example_topics = [
            "태양광 에너지 저장 효율성 개선 방안",
            "청소년 스마트폰 의존도와 학습 능력의 상관관계",
            "미세플라스틱이 해양 생태계에 미치는 영향",
            "식물 기반 육류 대체품의 영양학적 가치 분석",
            "머신러닝을 활용한 질병 조기 진단 시스템",
            "기후변화가 지역 농업에 미치는 영향"
        ]
        
        st.markdown("<div class='sub-title'>추천 주제 예시</div>", unsafe_allow_html=True)
        
        col_a, col_b = st.columns(2)
        with col_a:
            for topic_example in example_topics[:3]:
                if st.button(f"📌 {topic_example}", key=f"example_{topic_example}"):
                    st.session_state.topic = topic_example
                    st.rerun()
        
        with col_b:
            for topic_example in example_topics[3:]:
                if st.button(f"📌 {topic_example}", key=f"example_{topic_example}"):
                    st.session_state.topic = topic_example
                    st.rerun()
        
        if st.button("주제 분석하기", type="primary"):
            if topic or st.session_state.topic:
                if topic:
                    st.session_state.topic = topic
                st.session_state.step = 2
                st.rerun()
            else:
                st.error("연구 주제를 입력하거나 추천 주제 중 하나를 선택해 주세요.")
    
    with col2:
        st.markdown("<div class='info-box'>", unsafe_allow_html=True)
        st.markdown("#### 📊 서비스 통계")
        st.markdown("- 전국 고등학생들이 많이 검색한 주제")
        
        # 가상의 통계 데이터
        popular_topics = {
            "환경과 지속가능성": 42,
            "인공지능과 기계학습": 38,
            "생명과학과 의학": 35,
            "신재생에너지": 30,
            "심리학과 행동과학": 25
        }
        
        # 막대 그래프로 시각화
        fig = px.bar(
            x=list(popular_topics.keys()),
            y=list(popular_topics.values()),
            labels={'x': '주제 분야', 'y': '검색 빈도'},
            color_discrete_sequence=['#1E88E5']
        )
        fig.update_layout(
            margin=dict(l=10, r=10, t=10, b=0),
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='info-box'>", unsafe_allow_html=True)
        st.markdown("#### 🏆 인기 과학대회")
        st.markdown("""
        - 한국청소년과학탐구대회
        - 전국과학전람회
        - 국제청소년과학경진대회
        - 한국과학창의력대회
        - 한국학생과학탐구올림픽
        """)
        st.markdown("</div>", unsafe_allow_html=True)

def render_step2_topic_analysis():
    st.markdown(f"<div class='main-title'>'{st.session_state.topic}' 주제 분석</div>", unsafe_allow_html=True)
    
    # 시뮬레이션: 실제로는 AI 생성 내용 필요
    if 'definition' not in st.session_state.topic_analysis:
        with st.spinner("주제를 심층 분석 중입니다..."):
            time.sleep(2)  # 로딩 시뮬레이션
            
            # 샘플 데이터 (실제 구현에서는 API 호출 결과로 대체)
            st.session_state.topic_analysis = {
                'definition': f"""
                {st.session_state.topic}은(는) 현대 과학 연구에서 중요한 주제로, 다양한 분야에서 활발히 연구되고 있습니다. 
                
                이 주제는 기본적으로 [주제에 대한 상세 정의와 배경 설명]을 다루며, 최근에는 [최신 연구 동향이나 변화된 관점]으로 그 중요성이 더욱 부각되고 있습니다.
                
                {st.session_state.topic}에 대한 연구는 [관련 학문 분야]에서 특히 중요하게 다뤄지며, [주요 이론이나 개념] 등의 핵심 이론을 바탕으로 발전해왔습니다.
                """,
                'history': f"""
                {st.session_state.topic} 연구의 역사적 발전 과정:
                
                - 초기 연구 (1950-1970년대): [초기 연구 내용 및 접근법]
                - 연구 발전기 (1980-2000년대): [주요 발전 내용 및 패러다임 변화]
                - 현대적 접근 (2000년대 이후): [최신 연구 동향 및 방법론]
                
                특히 [중요한 역사적 사건이나 발견]은 이 분야의 중요한 전환점이 되었습니다.
                """
            }
    
    # 주제 정의 표시
    st.markdown("<div class='sub-title'>주제 정의 및 배경</div>", unsafe_allow_html=True)
    st.markdown("<div class='box-container'>", unsafe_allow_html=True)
    st.markdown(st.session_state.topic_analysis['definition'])
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 역사적 발전 과정 표시
    st.markdown("<div class='sub-title'>역사적 발전 과정</div>", unsafe_allow_html=True)
    st.markdown("<div class='box-container'>", unsafe_allow_html=True)
    st.markdown(st.session_state.topic_analysis['history'])
    st.markdown("</div
