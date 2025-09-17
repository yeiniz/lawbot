# AI 법률 시뮬레이터 — 로컬 프로토타입
## Quickstart
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # LAW_OC 등 입력
python scripts/init_db.py
streamlit run app/ui/streamlit_app.py
