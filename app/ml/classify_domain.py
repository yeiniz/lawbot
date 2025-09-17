from transformers import pipeline
LABELS = ["민법(불법행위)","제조물책임법","도로교통법","형법","저작권법","정보통신망법","노동법","행정법","자율주행/교통","생성형 AI/저작권","메타버스/플랫폼"]
_classifier=None
def get_classifier():
    global _classifier
    if _classifier is None:
        _classifier = pipeline("zero-shot-classification", model="joeddav/xlm-roberta-large-xnli")
    return _classifier
def classify(text:str):
    clf=get_classifier(); out=clf(text, LABELS, multi_label=True)
    pairs=list(zip(out["labels"], out["scores"]))
    return sorted(pairs, key=lambda x:x[1], reverse=True)[:3]
