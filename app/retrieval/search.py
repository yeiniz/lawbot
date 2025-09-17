import os, numpy as np, faiss
from sentence_transformers import SentenceTransformer
from sqlalchemy import text
from app.db import engine
from app.config import settings
INDEX_PATH = "data/index/cases.faiss"
MODEL = SentenceTransformer(settings.EMBED_MODEL)
def _load_index():
    if not (os.path.exists(INDEX_PATH) and os.path.exists(INDEX_PATH+".ids")):
        raise FileNotFoundError("FAISS index not found. Run app/retrieval/index_faiss.py first.")
    with open(INDEX_PATH+".ids","rb") as f: ids = np.frombuffer(f.read(), dtype=np.int64)
    index = faiss.read_index(INDEX_PATH); return index, ids
INDEX, IDS = _load_index()
def search_cases(query: str, top_k: int = 5):
    q = MODEL.encode([query], normalize_embeddings=True, convert_to_numpy=True).astype("float32")
    D, I = INDEX.search(q, top_k)
    hit_ids = IDS[I[0]]
    id_list = ",".join(map(str, map(int, hit_ids)))
    with engine.begin() as conn:
        rows = conn.execute(text(f"SELECT id, jurisdiction, title, court, decision_date, url, summary FROM cases WHERE id IN ({id_list})")).fetchall()
    order = {int(h): r for r, h in enumerate(hit_ids)}
    rows = sorted(rows, key=lambda r: order.get(int(r[0]), 0))
    return rows, D[0].tolist()
