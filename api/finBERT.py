from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

# 전역 변수로 선언하지 않고 Lazy하게 초기화
nlp = None

def get_pipeline():
    global nlp
    if nlp is None:
        tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
        model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
        nlp = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)
    return nlp

def semantic_analysis(text: str):
    pipe = get_pipeline()
    return pipe(text)
