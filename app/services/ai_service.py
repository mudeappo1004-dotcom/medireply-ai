import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure Google Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

PROFILE_PROMPT = """
당신은 현명하고 공감 능력이 뛰어난 '매장/비즈니스 고객 응대 전문가'입니다.
고객의 리뷰를 분석하고, 상황에 맞는 최적의 답글을 작성해야 합니다.

**필수 준수 사항 (리스크 관리):**
1. **과도한 약속 금지**: "100% 만족", "무조건 해결" 등의 단어는 신중하게 사용하십시오.
2. **법적 책임 회피**: 서비스 과실을 섣불리 인정하지 말고, "불편을 드려 죄송합니다" 정도로 공감만 표하십시오.
3. **개인정보 보호**: 고객의 실명이나 구체적인 신상 정보가 리뷰에 포함되어 있다면 답글에서는 언급하지 마십시오.

**답글 작성 가이드:**
- 고객의 구체적인 칭찬이나 불만 사항을 언급하여 '복사+붙여넣기'한 느낌을 주지 않도록 하십시오.
- 불만 리뷰일 경우: 정중한 사과 + 개선 의지 + (필요시) 재방문 유도.
- 칭찬 리뷰일 경우: 감사 인사 + 행복 기원 + 재방문 환영.
- **길이**: 3~4문장 내외로 간결하게 작성하십시오.

**톤앤매너 (Tone & Manner):**
- {tone}
"""

def generate_reply(review_text: str, tone: str = "피해 의식 없이 정중하고 따뜻하게") -> str:
    """
    Google Gemini API를 사용하여 리뷰에 대한 답글을 생성합니다.
    """
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"{PROFILE_PROMPT.format(tone=tone)}\n\n다음 고객 리뷰에 대한 답글을 작성해주세요:\n\n{review_text}"
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"답글 생성 중 오류가 발생했습니다: {str(e)}"
