# app/agents/query_agent.py
import logging
import os
import json
import re  # 추가된 import
from typing import List, Dict, Any, Optional
import requests
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

class QueryAgent:
    """
    LLM(Language Model)을 활용한 쿼리 처리 에이전트
    LangChain 또는 커스텀 에이전트를 사용하여 사용자 쿼리 처리
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # API 키 로드
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.llama_api_key = os.getenv("LLAMA_API_KEY", "")
        self.claude_api_key = os.getenv("CLAUDE_API_KEY", "")
        
        # API 엔드포인트
        self.openai_api_url = "https://api.openai.com/v1/completions"
        self.llama_api_url = "https://api.llama.com/v1/completions"  # 가상 URL
        self.claude_api_url = "https://api.claude.ai/v1/completions"  # 가상 URL
        
        # 캐시 디렉토리 설정
        self.cache_dir = "data/cache"
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # 사용할 LLM 선택
        self.available_llms = []
        if self.openai_api_key:
            self.available_llms.append("openai")
        if self.llama_api_key:
            self.available_llms.append("llama")
        if self.claude_api_key:
            self.available_llms.append("claude")
        
        if not self.available_llms:
            self.logger.warning("사용 가능한 LLM이 없습니다. 기본 텍스트 생성 기능만 사용됩니다.")
    
    def call_llm_api(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """
        사용 가능한 LLM API를 호출합니다.
        """
        if not self.available_llms:
            self.logger.warning("사용 가능한 LLM이 없습니다. 샘플 응답을 반환합니다.")
            return self.generate_sample_response(prompt)
        
        # 사용할 LLM 선택
        llm = self.available_llms[0]
        
        try:
            if llm == "openai":
                headers = {
                    "Authorization": f"Bearer {self.openai_api_key}",
                    "Content-Type": "application/json"
                }
                
                data = {
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {"role": "system", "content": "You are a helpful AI assistant specialized in academic research."},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": max_tokens,
                    "temperature": temperature
                }
                
                response = requests.post("https://api.openai.com/v1/chat/completions", 
                                        headers=headers, json=data)
                
                if response.status_code == 200:
                    return response.json()["choices"][0]["message"]["content"]
                else:
                    self.logger.error(f"OpenAI API 호출 실패: {response.status_code}")
                    return self.generate_sample_response(prompt)
            
            elif llm == "llama" or llm == "claude":
                # 실제 API가 없으므로 샘플 응답 반환
                self.logger.info(f"{llm.capitalize()} API 구현되지 않음, 샘플 응답 반환")
                return self.generate_sample_response(prompt)
        
        except Exception as e:
            self.logger.error(f"LLM API 호출 중 오류 발생: {str(e)}")
            return self.generate_sample_response(prompt)
    
    def generate_sample_response(self, prompt: str) -> str:
        """
        LLM API가 없을 때 사용할 샘플 응답을 생성합니다.
        """
        # 프롬프트에서 주요 키워드 추출
        words = prompt.lower().split()
        keywords = [word for word in words if len(word) > 4 and word not in ["about", "what", "which", "where", "when", "write", "explain", "describe", "create"]]
        
        if "introduction" in prompt.lower() or "서론" in prompt:
            return f"""
            # 서론
            
            이 주제는 현대 과학 연구에서 중요한 위치를 차지하고 있습니다. 특히 최근 몇 년간 이 분야의 연구는 급속도로 발전해왔으며, 다양한 응용 가능성을 보여주고 있습니다.
            
            기존 연구들은 주로 전통적인 접근법에 초점을 맞추어 왔으나, 이는 몇 가지 한계점을 드러내고 있습니다. 본 연구는 이러한 한계를 극복하기 위해 새로운 관점에서 이 주제를 탐구하고자 합니다.
            
            본 연구의 주요 목적은 (1) 현재 이 분야의 주요 이슈를 분석하고, (2) 혁신적인 접근법을 제안하며, (3) 실제 적용 가능한 해결책을 모색하는 것입니다. 이를 통해 이 분야의 학문적 발전에 기여하고자 합니다.
            """
        
        elif "methods" in prompt.lower() or "methodology" in prompt.lower() or "연구 방법" in prompt:
            return f"""
            # 연구 방법
            
            ## 연구 설계
            본 연구는 혼합적 연구 방법론을 채택하여 정량적 분석과 정성적 분석을 병행하였습니다. 이러한 접근은 연구 주제의 다면적 특성을 고려할 때 가장 적합하다고 판단하였습니다.
            
            ## 데이터 수집
            본 연구에서는 두 가지 주요 데이터 소스를 활용하였습니다. 첫째, 공개 데이터베이스에서 추출한 2차 데이터를 분석하였습니다. 둘째, 해당 분야 전문가 30명을 대상으로 심층 인터뷰를 진행하여 1차 데이터를 수집하였습니다.
            
            ## 분석 방법
            수집된 데이터는 통계 소프트웨어를 사용하여 분석하였으며, 주요 통계적 기법으로는 회귀분석, 요인분석, 그리고 군집분석이 활용되었습니다. 질적 데이터의 경우 주제별 코딩을 통해 분석하였습니다.
            
            ## 윤리적 고려사항
            본 연구는 모든 참여자로부터 사전 동의를 얻었으며, 연구윤리위원회의 승인을 받아 진행되었습니다. 참여자의 개인정보는 철저히 보호되었으며, 모든 데이터는 익명화 처리하였습니다.
            """
        
        elif "results" in prompt.lower() or "findings" in prompt.lower() or "연구 결과" in prompt:
            return f"""
            # 연구 결과
            
            ## 주요 발견 1
            분석 결과, 연구 대상의 핵심 특성에 있어 통계적으로 유의미한 패턴이 발견되었습니다. 특히 변수 A와 변수 B 사이에는 강한 상관관계(r=0.78, p<0.001)가 확인되었습니다.
            
            ## 주요 발견 2
            질적 분석에서는 세 가지 주요 주제가 도출되었습니다: (1) 환경적 요인의 중요성, (2) 사회적 맥락의 영향, 그리고 (3) 개인적 특성의 역할입니다. 이 중 환경적 요인이 가장 두드러진 주제로 나타났습니다.
            
            ## 주요 발견 3
            기존 이론과 달리, 본 연구에서는 새로운 관점에서의 해석 가능성이 제시되었습니다. 이는 현재 학계의 지배적 패러다임에 도전하는 결과로서, 추가적인 검증이 필요합니다.
            
            이러한 결과는 기존 연구와 일부 일치하면서도, 몇 가지 중요한 차이점을 보여줍니다. 이러한 차이는 연구 방법론의 차이와 분석 대상의 특수성에서 기인한 것으로 판단됩니다.
            """
        
        elif "conclusion" in prompt.lower() or "결론" in prompt:
            return f"""
            # 결론 및 제언
            
            본 연구는 이 분야의 주요 연구 질문을 탐구하였습니다. 연구 결과를 종합하면, 첫째, 이 현상은 다양한 요인들의 복합적 상호작용에 의해 발생함을 확인하였습니다. 둘째, 기존에 간과되었던 요인 X의 중요성이 드러났습니다. 셋째, 맥락 특이적 접근의 필요성이 확인되었습니다.
            
            이러한 발견은 학문적으로는 이론 확장에 기여하며, 실용적으로는 관련 정책 및 프로그램 개발에 중요한 시사점을 제공합니다. 특히 현장 실무자들에게 구체적인 가이드라인을 제시할 수 있을 것입니다.
            
            본 연구의 한계점으로는 표본의 대표성 문제와 종단적 데이터의 부재를 들 수 있습니다. 이를 보완하기 위해 향후 연구에서는 더 다양한 집단을 대상으로 한 장기적 연구와, 실험적 설계를 통한 인과관계 검증이 필요합니다.
            """
        
        else:
            # 일반적인 응답
            return f"""
            이 주제에 관한 연구는 매우 중요한 학술적 가치를 지니고 있습니다. 특히 최근의 기술적, 사회적 변화를 고려할 때 이 분야에 대한 심층적 이해는 더욱 필요해지고 있습니다.
            
            주요 연구 방향으로는 (1) 이론적 기반 확장, (2) 실증적 데이터 분석, (3) 학제간 접근법 개발 등이 있습니다. 이러한 다양한 접근을 통해 더욱 포괄적인 이해가 가능할 것입니다.
            
            향후 연구에서는 새로운 방법론의 적용과 더불어, 다양한 맥락에서의 교차 검증이 필요합니다. 이를 통해 더욱 견고하고 일반화 가능한 결과를 도출할 수 있을 것입니다.
            
            주의: 이 내용은 자동 생성된 샘플 텍스트입니다. 실제 연구나 학술 목적으로 사용하기 위해서는 추가적인 검증과 전문가의 검토가 필요합니다.
            """
    
    def generate_paper_content(self, topic: str, paper_info: Dict[str, Any]) -> Dict[str, str]:
        """
        선택한 논문을 바탕으로 논문 형식의 자료를 생성합니다.
        """
        try:
            # 캐시 파일 경로
            cache_key = f"{topic}_{paper_info.get('title', '')[:30]}"
            cache_file = os.path.join(self.cache_dir, f"paper_content_{hash(cache_key)}.json")
            
            # 캐시가 있는 경우 캐시에서 로드
            if os.path.exists(cache_file):
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        self.logger.info(f"캐시에서 논문 내용 로드: {cache_key}")
                        return json.load(f)
                except Exception as e:
                    self.logger.warning(f"캐시 로드 실패, 새로 생성합니다: {str(e)}")
            
            # 서론 생성
            introduction_prompt = f"""
            다음 주제와 논문 정보를 바탕으로 학술 논문의 서론을 작성해주세요. 한국어로 작성하되, 학술적인 어조를 유지해주세요.
            
            주제: {topic}
            참고 논문 제목: {paper_info.get('title', '')}
            참고 논문 저자: {paper_info.get('authors', '')}
            참고 논문 초록: {paper_info.get('abstract', '')}
            참고 논문 키워드: {', '.join(paper_info.get('keywords', []))}
            
            서론에는 다음 내용을 포함해주세요:
            1. 연구 배경 및 중요성
            2. 기존 연구의 한계점
            3. 본 연구의 목적과 연구 질문
            4. 연구의 의의 및 기대효과
            
            형식은 '# 서론'으로 시작하고, 2-3 단락으로 구성해주세요.
            """
            
            introduction = self.call_llm_api(introduction_prompt, max_tokens=800)
            
            # 연구 방법 생성
            methods_prompt = f"""
            다음 주제와 논문 정보를 바탕으로 학술 논문의 연구 방법 섹션을 작성해주세요. 한국어로 작성하되, 학술적인 어조를 유지해주세요.
            
            주제: {topic}
            참고 논문 제목: {paper_info.get('title', '')}
            참고 논문 키워드: {', '.join(paper_info.get('keywords', []))}
            
            연구 방법 섹션에는 다음 내용을 포함해주세요:
            1. 연구 설계 (연구 접근법, 설계 유형)
            2. 데이터 수집 방법 (표본 추출, 도구, 절차)
            3. 분석 방법 (통계적 기법, 질적 분석 방법)
            4. 윤리적 고려사항
            
            형식은 '# 연구 방법'으로 시작하고, 각 하위 섹션은 '## 섹션 제목'으로 구분해주세요.
            """
            
            methods = self.call_llm_api(methods_prompt, max_tokens=800)
            
            # 연구 결과 생성
            results_prompt = f"""
            다음 주제와 논문 정보를 바탕으로 학술 논문의 연구 결과 섹션을 작성해주세요. 한국어로 작성하되, 학술적인 어조를 유지해주세요.
            
            주제: {topic}
            참고 논문 제목: {paper_info.get('title', '')}
            참고 논문 키워드: {', '.join(paper_info.get('keywords', []))}
            
            연구 결과 섹션에는 다음 내용을 포함해주세요:
            1. 주요 연구 결과 및 발견 (3가지 이상)
            2. 통계적 분석 결과 (가상의 데이터 기반)
            3. 결과에 대한 해석
            
            형식은 '# 연구 결과'로 시작하고, 각 주요 발견은 '## 주요 발견 X'와 같은 형식으로 구분해주세요.
            """
            
            results = self.call_llm_api(results_prompt, max_tokens=800)
            
            # 결론 생성
            conclusion_prompt = f"""
            다음 주제와 논문 정보를 바탕으로 학술 논문의 결론 및 제언 섹션을 작성해주세요. 한국어로 작성하되, 학술적인 어조를 유지해주세요.
            
            주제: {topic}
            참고 논문 제목: {paper_info.get('title', '')}
            참고 논문 키워드: {', '.join(paper_info.get('keywords', []))}
            
            결론 및 제언 섹션에는 다음 내용을 포함해주세요:
            1. 주요 연구 결과 요약
            2. 이론적/실용적 의의
            3. 연구의 한계점
            4. 향후 연구 방향 제안
            
            형식은 '# 결론 및 제언'으로 시작하고, 2-3 단락으로 구성해주세요.
            """
            
            conclusion = self.call_llm_api(conclusion_prompt, max_tokens=800)
            
            # 참고문헌 생성
            references = f"""
            # 참고문헌
            
            1. {paper_info.get('authors', '')} ({paper_info.get('year', '2023')}). {paper_info.get('title', '')}. *{paper_info.get('source', '')}*.
            2. Kim, J., & Lee, S. (2022). A systematic review of research trends in {topic}. Journal of Scientific Research, 45(3), 234-251.
            3. Park, M., & Choi, H. (2023). Methodological approaches to {topic} in educational contexts. International Journal of Science Education, 18(2), 187-203.
            4. Johnson, A., & Smith, B. (2021). Recent advances in {paper_info.get('keywords', ['research'])[0]} research. Annual Review of Science, 12, 78-95.
            5. Lee, Y., & Kim, T. (2023). Application of {topic} in real-world settings: Challenges and opportunities. Applied Research Journal, 9(4), 412-428.
            """
            
            # 틈새 주제 생성
            niche_topics_prompt = f"""
            다음 주제와 논문 정보를 바탕으로 새로운 연구 틈새(niche) 주제 5가지를 제안해주세요. 각 틈새 주제는 기존 연구에서 충분히 다루어지지 않았지만 높은 연구 가치가 있는 영역이어야 합니다.
            
            주제: {topic}
            참고 논문 제목: {paper_info.get('title', '')}
            참고 논문 키워드: {', '.join(paper_info.get('keywords', []))}
            
            틈새 주제는 "XXX에 관한 연구" 형식으로 작성해주세요.
            """
            
            niche_topics_text = self.call_llm_api(niche_topics_prompt, max_tokens=400)
            
            # 텍스트에서 틈새 주제 추출
            niche_topics = []
            for line in niche_topics_text.split('\n'):
                line = line.strip()
                if line and (line.startswith('- ') or line.startswith('* ') or line.startswith('1. ') or 
                           line.startswith('2. ') or line.startswith('3. ') or line.startswith('4. ') or 
                           line.startswith('5. ')):
                    # 번호나 글머리 기호 제거
                    clean_line = re.sub(r'^[0-9-*. ]+', '', line).strip()
                    if clean_line:
                        niche_topics.append(clean_line)
            
            # 틈새 주제가 충분하지 않은 경우 추가
            if len(niche_topics) < 5:
                default_niche_topics = [
                    f"{topic}의 새로운 측정 방법론 개발에 관한 연구",
                    f"{topic}이 청소년 발달에 미치는 장기적 영향에 관한 연구",
                    f"{topic}과 관련된 윤리적 쟁점 분석 연구",
                    f"{topic}의 문화간 차이 비교 연구",
                    f"인공지능을 활용한 {topic} 분석 방법 연구"
                ]
                niche_topics.extend(default_niche_topics[:(5 - len(niche_topics))])
            
            # 최대 5개로 제한
            niche_topics = niche_topics[:5]
            
            # 면책 조항
            disclaimer = f"""
            # 중요 안내
            
            이 내용은 AI에 의해 추론된 자료로, 실제 논문이 아닙니다. 참조용으로만 활용하시기 바라며, 
            여기에 제시된 참고문헌은 실제 인용이나 학술적 활용이 불가능할 수 있습니다. 
            실제 연구를 위해서는 추가적인 문헌 조사와 검증이 필요합니다.
            """
            
            # 결과 통합
            paper_content = {
                "introduction": introduction.strip(),
                "methods": methods.strip(),
                "results": results.strip(),
                "conclusion": conclusion.strip(),
                "references": references.strip(),
                "disclaimer": disclaimer.strip(),
                "niche_topics": niche_topics
            }
            
            # 결과 캐시에 저장
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(paper_content, f, ensure_ascii=False, indent=2)
            
            return paper_content
            
        except Exception as e:
            self.logger.error(f"논문 형식 내용 생성 중 오류 발생: {str(e)}")
            
            # 오류 발생 시 기본 내용 반환
            return {
                "introduction": "# 서론\n\n서론 생성 중 오류가 발생했습니다.",
                "methods": "# 연구 방법\n\n연구 방법 생성 중 오류가 발생했습니다.",
                "results": "# 연구 결과\n\n연구 결과 생성 중 오류가 발생했습니다.",
                "conclusion": "# 결론 및 제언\n\n결론 생성 중 오류가 발생했습니다.",
                "references": "# 참고문헌\n\n참고문헌 생성 중 오류가 발생했습니다.",
                "disclaimer": "# 중요 안내\n\n이 내용은 오류로 인해 정확하지 않을 수 있습니다.",
                "niche_topics": ["오류로 인해 틈새 주제를 생성할 수 없습니다."]
            }
    
    def generate_niche_content(self, topic: str, niche_topic: str) -> Dict[str, str]:
        """
        선택한 틈새주제에 대한 연구 계획을 생성합니다.
        """
        try:
            # 캐시 파일 경로
            cache_key = f"{topic}_{niche_topic[:30]}"
            cache_file = os.path.join(self.cache_dir, f"niche_content_{hash(cache_key)}.json")
            
            # 캐시가 있는 경우 캐시에서 로드
            if os.path.exists(cache_file):
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        self.logger.info(f"캐시에서 틈새주제 내용 로드: {cache_key}")
                        return json.load(f)
                except Exception as e:
                    self.logger.warning(f"캐시 로드 실패, 새로 생성합니다: {str(e)}")
            
            # 서론 생성
            introduction_prompt = f"""
            다음 주제와 틈새주제를 바탕으로 연구 계획서의 서론을 작성해주세요. 한국어로 작성하되, 학술적인 어조를 유지해주세요.
            
            주제: {topic}
            틈새주제: {niche_topic}
            
            서론에는 다음 내용을 포함해주세요:
            1. 틈새주제의 배경 및 중요성
            2. 기존 연구의 한계점과 이 틈새주제가 왜 중요한지
            3. 연구의 목적과 주요 연구 질문
            4. 예상되는 학문적/실용적 기여
            
            형식은 '# 서론'으로 시작하고, 2-3 단락으로 구성해주세요.
            """
            
            introduction = self.call_llm_api(introduction_prompt, max_tokens=800)
            
            # 연구 방법 생성
            methods_prompt = f"""
            다음 주제와 틈새주제를 바탕으로 연구 계획서의 연구 방법 섹션을 작성해주세요. 한국어로 작성하되, 학술적인 어조를 유지해주세요.
            
            주제: {topic}
            틈새주제: {niche_topic}
            
            연구 방법 섹션에는 다음 내용을 포함해주세요:
            1. 연구 설계 (어떤 연구 방법론을 사용할 것인지)
            2. 자료 수집 방법 (어떤 데이터를 어떻게 수집할 것인지)
            3. 분석 방법 (데이터를 어떻게 분석할 것인지)
            4. 예상되는 한계점과 극복 방안
            
            형식은 '# 연구 방법'으로 시작하고, 각 하위 섹션은 '## 섹션 제목'으로 구분해주세요.
            """
            
            methods = self.call_llm_api(methods_prompt, max_tokens=800)
            
            # 예상 결과 생성
            expected_results_prompt = f"""
            다음 주제와 틈새주제를 바탕으로 연구 계획서의 예상되는 연구 결과 섹션을 작성해주세요. 한국어로 작성하되, 학술적인 어조를 유지해주세요.
            
            주제: {topic}
            틈새주제: {niche_topic}
            
            예상되는 연구 결과 섹션에는 다음 내용을 포함해주세요:
            1. 주요 예상 결과 (3가지 이상)
            2. 예상 결과의 의미와 해석
            3. 결과가 학문적/실용적으로 어떤 의미를 갖는지
            
            형식은 '# 예상되는 연구 결과'로 시작하고, 각 예상 결과는 번호를 매겨 구분해주세요.
            """
            
            expected_results = self.call_llm_api(expected_results_prompt, max_tokens=800)
            
            # 면책 조항
            disclaimer = f"""
            # 중요 안내
            
            이 내용은 AI에 의해 추론된 자료로, 실제 논문이 아닙니다. 참조용으로만 활용하시기 바라며, 
            실제 연구를 위해서는 추가적인 문헌 조사와 검증이 필요합니다.
            """
            
            # 결과 통합
            niche_content = {
                "introduction": introduction.strip(),
                "methods": methods.strip(),
                "expected_results": expected_results.strip(),
                "disclaimer": disclaimer.strip()
            }
            
            # 결과 캐시에 저장
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(niche_content, f, ensure_ascii=False, indent=2)
            
            return niche_content
            
        except Exception as e:
            self.logger.error(f"틈새주제 내용 생성 중 오류 발생: {str(e)}")
            
            # 오류 발생 시 기본 내용 반환
            return {
                "introduction": "# 서론\n\n서론 생성 중 오류가 발생했습니다.",
                "methods": "# 연구 방법\n\n연구 방법 생성 중 오류가 발생했습니다.",
                "expected_results": "# 예상되는 연구 결과\n\n예상 결과 생성 중 오류가 발생했습니다.",
                "disclaimer": "# 중요 안내\n\n이 내용은 오류로 인해 정확하지 않을 수 있습니다."
            }
