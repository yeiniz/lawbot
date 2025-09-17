import requests, time
from app.config import settings
from app.db import engine
from sqlalchemy import text
BASE = "https://www.courtlistener.com/api/rest/v3/opinions/"
headers = {"User-Agent":"ai-legal-sim/0.1"}
if settings.COURTLISTENER_TOKEN: headers["Authorization"] = f"Token {settings.COURTLISTENER_TOKEN}"
def run(search="autonomous vehicle", pages=1):
    next_url = f"{BASE}?search={search}&page_size=50"
    with engine.begin() as conn:
        for _ in range(pages):
            r = requests.get(next_url, headers=headers, timeout=30); r.raise_for_status(); js = r.json()
            for res in js.get("results", []):
                ext_id = str(res.get("id")); title = (res.get("caseName") or res.get("absolute_url"))
                body = res.get("plain_text") or res.get("html",""); court="US Court"
                if isinstance(res.get("court"), dict): court = res.get("court").get("name", court)
                date = res.get("dateFiled"); url = "https://www.courtlistener.com"+(res.get("absolute_url","") or "")
                sql = "INSERT INTO cases(jurisdiction, external_id, title, court, case_number, decision_date, outcome, url, cited_statutes, summary, body) VALUES('US', :eid, :title, :court, NULL, :date, NULL, :url, NULL, NULL, :body)"
                if settings.DB_URL.startswith("mysql"): sql += " ON DUPLICATE KEY UPDATE title=VALUES(title), court=VALUES(court), decision_date=VALUES(decision_date), url=VALUES(url)"
                else: sql += " ON CONFLICT(external_id) DO NOTHING"
                conn.execute(text(sql), {"eid":ext_id,"title":title,"court":court,"date":date,"url":url,"body":body})
            next_url = js.get("next"); 
            if not next_url: break
            time.sleep(0.2)
if __name__ == "__main__": run()
