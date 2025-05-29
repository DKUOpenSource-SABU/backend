from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

# 모델과 토크나이저 로드
tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")

# 파이프라인 생성
nlp = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)


def semantic_analysis(text: str):
    result = nlp(text)
    return result
