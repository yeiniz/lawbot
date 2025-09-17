import re

def clean_text(t:str)->str:
    if not t: return ''
    return re.sub(r'\s+',' ',t).strip()
