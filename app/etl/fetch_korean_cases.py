import time, requests
from bs4 import BeautifulSoup
from sqlalchemy import text
from app.db import engine
from app.config import settings

SEARCH_URL = "https://www.law.go.kr/DRF/lawSearch.do"
DETAIL_URL = "https://www.law.go.kr/DRF/lawService.do"

def to_date(s: str | None):
    if not s:
        return None
    s = s.strip().replace(".", "-")
    # "YYYY-MM-DD" 형태로 맞추기
    return s[:10] if len(s) >= 10 else None

def search_page(query: str, page: int):
    """판례 목록 검색 (prec) → 리스트와 totalCnt 반환"""
    params = {
        "OC": settings.LAW_OC,   # 예: 1119hope  (이메일 아이디 부분만!)
        "target": "prec",
        "type": "XML",
        "query": query,
        "page": page,
    }
    r = requests.get(SEARCH_URL, params=params, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml-xml")

    items = []
    for p in soup.find_all("prec"):
        pid = p.find("판례일련번호")
        if not pid:
            continue
        external_id = pid.get_text(strip=True)
        items.append({
            "external_id": external_id,
            "title": (p.find("사건명").get_text(strip=True) if p.find("사건명") else None),
            "court": (p.find("법원명").get_text(strip=True) if p.find("법원명") else None),
            "case_number": (p.find("사건번호").get_text(strip=True) if p.find("사건번호") else None),
            "decision_date": to_date(p.find("선고일자").get_text(strip=True) if p.find("선고일자") else None),
            # 상세 조회 XML 엔드포인트 URL (나중에 HTML로 보고 싶으면 type=HTML)
            "url": f"https://www.law.go.kr/DRF/lawService.do?OC={settings.LAW_OC}&target=prec&ID={external_id}&type=XML",
            "summary": "",
            "body": "",
        })

    total = soup.find("totalCnt")
    total_cnt = int(total.get_text(strip=True)) if total else None
    return items, total_cnt

def fetch_detail(external_id: str):
    """단건 상세 본문(판례내용) 조회"""
    params = {
        "OC": settings.LAW_OC,
        "target": "prec",
        "type": "XML",   # XML로 받아서 텍스트 파싱
        "ID": external_id,
    }
    r = requests.get(DETAIL_URL, params=params, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml-xml")
    body_node = soup.find("판례내용")
    body_text = body_node.get_text("\n", strip=True) if body_node else ""
    summary = body_text[:700] if body_text else ""
    return summary, body_text

def run():
    # 사건명에 "자율주행"이 잘 안 걸릴 수 있어 폭넓은 키워드로 시도
    queries = ["교통사고", "손해배상", "자율주행", "자율주행차", "자율주행자동차"]
    max_pages = 2

    saved_detail = 0
    for q in queries:
        for page in range(1, max_pages + 1):
            try:
                items, total = search_page(q, page)
                if total == 0 and page == 1:
                    print(f"[{q}] 검색 0건 → 다음 키워드로")
                    break
                if not items:
                    print(f"[{q}] page {page} 결과 없음")
                    break

                print(f"[{q}] page {page} → {len(items)}건 (total={total})")

                # 1) 기본 메타데이터 먼저 업서트
                with engine.begin() as conn:
                    for it in items:
                        conn.execute(text("""
                            INSERT INTO cases
                              (jurisdiction, external_id, title, court, case_number, decision_date, url, summary, body)
                            VALUES
                              (:jurisdiction, :external_id, :title, :court, :case_number, :decision_date, :url, :summary, :body)
                            ON DUPLICATE KEY UPDATE
                              title=VALUES(title),
                              court=VALUES(court),
                              case_number=VALUES(case_number),
                              decision_date=VALUES(decision_date),
                              url=VALUES(url)
                        """), {**it, "jurisdiction": "KR"})

                # 2) 상세 본문 조회해서 summary/body 채우기
                for it in items:
                    try:
                        summary, body = fetch_detail(it["external_id"])
                        with engine.begin() as conn:
                            conn.execute(text("""
                                UPDATE cases
                                   SET summary=:summary, body=:body
                                 WHERE external_id=:external_id
                            """), {"summary": summary, "body": body, "external_id": it["external_id"]})
                        saved_detail += 1
                        time.sleep(0.2)  # 과호출 방지
                    except Exception as e:
                        print("상세 실패:", it["external_id"], e)

                time.sleep(0.3)  # 과호출 방지
            except Exception as e:
                print("에러:", e)

    print(f"상세 저장 완료: {saved_detail}건")

if __name__ == "__main__":
    run()
