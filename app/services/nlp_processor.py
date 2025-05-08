# app/services/nlp_processor.py
import logging
import os
import re
from typing import List, Dict, Any, Optional
import requests
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

class NLPService:
    """
    자연어 처리 기능을 제공하는 서비스
    HuggingFace Inference API 또는 자체 NLP 모델을 사용하여 텍스트 처리
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # HuggingFace API 키 로드
        self.huggingface_api_key = os.getenv("HUGGINGFACE_API_KEY", "")
        self.huggingface_api_url = "https://api-inference.huggingface.co/models/"
        
        # 기본 모델 설정
        self.keyword_extraction_model = "distilbert-base-uncased"
        self.text_generation_model = "gpt2"
        self.summarization_model = "facebook/bart-large-cnn"
        
        # LangChain이 설치되어 있는 경우 사용
        self.use_langchain = False
        try:
            import langchain
            self.use_langchain = True
        except ImportError:
            self.logger.warning("LangChain 패키지를 찾을 수 없습니다. 기본 NLP 기능만 사용합니다.")
    
    def extract_keywords(self, text: str, num_keywords: int = 5) -> List[str]:
        """
        텍스트에서 주요 키워드를 추출합니다.
        """
        try:
            # 실제 구현에서는 HuggingFace API 또는 자체 모델 사용
            # 여기서는 간단한 구현만 제공
            
            # 텍스트 전처리
            text = text.lower()
            # 한글, 영문, 숫자, 공백만 남기고 제거
            text = re.sub(r'[^\uAC00-\uD7A3a-zA-Z0-9\s]', ' ', text)
            
            # 불용어 목록 (실제 구현에서는 더 많은 단어 필요)
            stop_words = ['은', '는', '이', '가', '을', '를', '에', '의', '과', '와', '이다', '있다', 
                          'the', 'a', 'an', 'is', 'are', 'was', 'were', 'in', 'on', 'at', 'to', 'and', 'or']
            
            # 단어 토큰화 및 빈도 계산
            words = text.split()
            word_freq = {}
            
            for word in words:
                if word not in stop_words and len(word) > 1:
                    if word in word_freq:
                        word_freq[word] += 1
                    else:
                        word_freq[word] = 1
            
            # 빈도 기준으로 정렬하여 상위 키워드 추출
            sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            keywords = [word for word, freq in sorted_words[:num_keywords]]
            
            # 키워드가 충분하지 않은 경우 일반적인 연구 키워드 추가
            if len(keywords) < num_keywords:
                generic_keywords = ['연구', '분석', '효과', '방법', '시스템', '개발', '영향', '평가']
                keywords.extend(generic_keywords[:num_keywords - len(keywords)])
            
            self.logger.info(f"추출된 키워드: {keywords}")
            return keywords
            
        except Exception as e:
            self.logger.error(f"키워드 추출 중 오류 발생: {str(e)}")
            # 오류 발생 시 기본 키워드 반환
            return ['연구', '분석', '효과', '방법', '시스템']
    
    def huggingface_api_call(self, model: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        HuggingFace Inference API를 호출합니다.
        """
        try:
            headers = {"Authorization": f"Bearer {self.huggingface_api_key}"}
            api_url = f"{self.huggingface_api_url}{model}"
            
            response = requests.post(api_url, headers=headers, json=payload)
            
            if response.status_code != 200:
                self.logger.error(f"HuggingFace API 호출 실패: {response.status_code}")
                return {"error": f"API 호출 실패: {response.status_code}"}
            
            return response.json()
        except Exception as e:
            self.logger.error(f"HuggingFace API 호출 중 오류 발생: {str(e)}")
            return {"error": str(e)}
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        텍스트의 감성을 분석합니다.
        """
        try:
            # HuggingFace API를 사용하는 경우
            if self.huggingface_api_key:
                model = "distilbert-base-uncased-finetuned-sst-2-english"
                payload = {"inputs": text}
                result = self.huggingface_api_call(model, payload)
                
                if "error" in result:
                    raise Exception(result["error"])
                
                return result
            
            # 간단한 규칙 기반 감성 분석
            # 실제 구현에서는 더 정교한 방법 필요
            positive_words = ['좋은', '훌륭한', '탁월한', '우수한', '혁신적인', '효과적인', 
                             'good', 'great', 'excellent', 'innovative', 'effective']
            negative_words = ['나쁜', '부족한', '문제가 있는', '한계가 있는', '비효율적인',
                             'bad', 'poor', 'problematic', 'limited', 'inefficient']
            
            positive_count = sum(1 for word in positive_words if word in text.lower())
            negative_count = sum(1 for word in negative_words if word in text.lower())
            
            if positive_count > negative_count:
                sentiment = "positive"
                score = 0.5 + (positive_count - negative_count) * 0.1
            elif negative_count > positive_count:
                sentiment = "negative"
                score = 0.5 - (negative_count - positive_count) * 0.1
            else:
                sentiment = "neutral"
                score = 0.5
            
            # 점수는 0~1 사이로 제한
            score = max(0, min(1, score))
            
            return {
                "label": sentiment,
                "score": score
            }
            
        except Exception as e:
            self.logger.error(f"감성 분석 중 오류 발생: {str(e)}")
            return {
                "label": "neutral",
                "score": 0.5,
                "error": str(e)
            }
    
    def summarize_text(self, text: str, max_length: int = 150) -> str:
        """
        텍스트를 요약합니다.
        """
        try:
            # 텍스트가 짧은 경우 요약 불필요
            if len(text.split()) < max_length:
                return text
            
            # HuggingFace API를 사용하는 경우
            if self.huggingface_api_key:
                payload = {
                    "inputs": text,
                    "parameters": {
                        "max_length": max_length,
                        "min_length": max(30, max_length // 3),
                        "do_sample": False
                    }
                }
                result = self.huggingface_api_call(self.summarization_model, payload)
                
                if "error" not in result:
                    return result[0]["summary_text"]
            
            # 간단한 규칙 기반 요약 (실제 구현에서는 더 정교한 방법 필요)
            sentences = re.split(r'(?<=[.!?])\s+', text)
            
            # 짧은 요약의 경우 앞부분 몇 문장만 사용
            if len(sentences) <= 3:
                return ' '.join(sentences)
            
            # 첫 문장과 마지막 문장은 중요한 정보를 담고 있을 가능성이 높음
            summary = [sentences[0]]
            
            # 중간 부분에서 중요한 문장 선택 (길이 기준)
            middle_sentences = sentences[1:-1]
            selected_middle = sorted(middle_sentences, key=len, reverse=True)[:1]
            summary.extend(selected_middle)
            
            # 마지막 문장 추가
            summary.append(sentences[-1])
            
            return ' '.join(summary)
            
        except Exception as e:
            self.logger.error(f"텍스트 요약 중 오류 발생: {str(e)}")
            # 오류 발생 시 원본 텍스트의 앞부분 반환
            words = text.split()
            if len(words) > max_length:
                return ' '.join(words[:max_length]) + "..."
            return text
    
    def generate_text(self, prompt: str, max_length: int = 100) -> str:
        """
        프롬프트를 기반으로 텍스트를 생성합니다.
        """
        try:
            # HuggingFace API를 사용하는 경우
            if self.huggingface_api_key:
                payload = {
                    "inputs": prompt,
                    "parameters": {
                        "max_length": max_length,
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "do_sample": True
                    }
                }
                result = self.huggingface_api_call(self.text_generation_model, payload)
                
                if "error" not in result:
                    return result[0]["generated_text"]
            
            # 간단한 텍스트 생성 (실제 구현에서는 더 정교한 방법 필요)
            # 여기서는 프롬프트와 함께 정적 텍스트 반환
            return f"{prompt} 이 주제에 대한 추가 연구가 필요합니다. 다양한 관점에서 접근하여 심층적인 분석이 이루어져야 합니다."
            
        except Exception as e:
            self.logger.error(f"텍스트 생성 중 오류 발생: {str(e)}")
            return f"{prompt} (텍스트 생성 중 오류가 발생했습니다)"
    
    def classify_text(self, text: str, categories: List[str]) -> Dict[str, float]:
        """
        텍스트를 주어진 카테고리로 분류합니다.
        """
        try:
            # HuggingFace API를 사용하는 경우 (zero-shot 분류)
            if self.huggingface_api_key:
                model = "facebook/bart-large-mnli"
                payload = {
                    "inputs": text,
                    "parameters": {
                        "candidate_labels": categories
                    }
                }
                result = self.huggingface_api_call(model, payload)
                
                if "error" not in result:
                    scores = {}
                    for label, score in zip(result["labels"], result["scores"]):
                        scores[label] = score
                    return scores
            
            # 간단한 키워드 기반 분류 (실제 구현에서는 더 정교한 방법 필요)
            scores = {}
            text_lower = text.lower()
            
            for category in categories:
                # 카테고리 이름이 텍스트에 등장하는 횟수로 간단히 점수 계산
                category_lower = category.lower()
                count = text_lower.count(category_lower)
                scores[category] = min(1.0, count * 0.2 + 0.1)
            
            # 점수 정규화
            total_score = sum(scores.values())
            if total_score > 0:
                for category in scores:
                    scores[category] /= total_score
            
            return scores
            
        except Exception as e:
            self.logger.error(f"텍스트 분류 중 오류 발생: {str(e)}")
            # 오류 발생 시 균등한 점수 반환
            return {category: 1.0 / len(categories) for category in categories}
