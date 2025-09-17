import re
from collections import Counter
def extract_outcome(text:str|None)->str|None:
    if not text: return None
    if re.search(r"원고\s*승|인용|승소", text): return "원고승"
    if re.search(r"기각|패소|각하", text): return "피고승"
    if re.search(r"파기|환송", text): return "파기환송"
    return None
def knn_probability(similar_outcomes:list[str]):
    c=Counter([s for s in similar_outcomes if s]); total=sum(c.values()) or 1
    return {k:(c.get(k,0)+1)/(total+3) for k in ["원고승","피고승","파기환송"]}
