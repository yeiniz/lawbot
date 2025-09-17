import streamlit as st
from app.ml.classify_domain import classify
from app.retrieval.search import search_cases
from app.ml.predict_outcome import extract_outcome, knn_probability
from app.generators.draft_documents import make_draft
from app.utils.law_mappings import DOMAIN_CHECKLIST
st.set_page_config(page_title="AI 법률 시뮬레이터", layout="wide")
st.title("⚖️ AI 법률 시뮬레이터 — 프로토타입")
scenario = st.text_area("상황을 적어주세요", height=140, placeholder="예) 자율주행차가 보행자와 충돌... 소프트웨어 업데이트가 지연...")
if st.button("분석 시작", disabled=not scenario):
    with st.spinner("법률 영역 분류 중..."): labels = classify(scenario)
    st.subheader("법률 영역 분류(Top-3)"); st.write(labels)
    with st.spinner("유사 판례 검색 중..."): results, scores = search_cases(scenario, top_k=5)
    st.subheader("유사 판례 Top-5")
    for r, sc in zip(results, scores):
        _id, jur, title, court, date, url, summary = r
        st.markdown(f"**[{title or '(제목없음)'}]({url})**  "); st.caption(f"{jur} · {court} · {date} · sim={sc:.3f}")
        if summary: st.write(summary[:400] + ("..." if len(summary) > 400 else ""))
        st.divider()
    with st.spinner("판결 확률(참고) 추정 중..."):
        outs = [extract_outcome((r[-1] or "")) for r in results]; probs = knn_probability(outs)
    st.subheader("판결 확률(참고용)"); st.write(probs); st.caption("※ 실제 법률 자문이 아니며 참고용입니다.")
    st.subheader("증거 체크리스트")
    top_domain = labels[0][0] if labels else "자율주행/교통"; checklist = DOMAIN_CHECKLIST.get(top_domain, [])
    st.write("- " + "\n- ".join(checklist) if checklist else "도메인 규칙 미정")
    st.subheader("문서 초안 생성")
    if st.button("진술서 초안 만들기"):
        preds = [{"title": (r[2] or ""), "court": (r[3] or ""), "decision_date": (r[4] or ""), "url": (r[5] or "")} for r in results]
        draft = make_draft(scenario, [l for l,_ in labels], preds); st.code(draft)
        st.download_button("TXT로 저장", draft.encode("utf-8"), file_name="draft_statement.txt")
