import requests
from jinja2 import Template
from app.config import settings
BASIC_TEMPLATE = Template("""[진술서 초안]
사건 개요: {{ scenario }}
핵심 쟁점: {{ issues|join(', ') }}
유사 판례:
{% for p in precedents -%}
 - {{ p.title }} ({{ p.court }}, {{ p.decision_date }})
{% endfor %}
요청 취지: {{ prayer or '추후 보완' }}
""")
def via_ollama(prompt: str) -> str:
    url = "http://localhost:11434/api/generate"
    payload = {"model": settings.OLLAMA_MODEL, "prompt": prompt, "stream": False}
    r = requests.post(url, json=payload, timeout=120); r.raise_for_status()
    return r.json().get("response","")
def make_draft(scenario:str, issues:list[str], precedents:list[dict], prayer:str|None=None, use_llm:bool=True)->str:
    base = BASIC_TEMPLATE.render(scenario=scenario, issues=issues, precedents=precedents, prayer=prayer)
    if settings.USE_OLLAMA and use_llm:
        try: return via_ollama("아래 사건에 대한 진술서 초안을 한국어로 조리있게 정리해줘. 판례는 각주 형식으로 번호 매기고, 과장 없이 중립적으로 작성.\n"+base)
        except Exception: return base
    return base
