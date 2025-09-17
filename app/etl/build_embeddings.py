import numpy as np
from sentence_transformers import SentenceTransformer
from sqlalchemy import text
from app.db import engine
from app.config import settings
MODEL = SentenceTransformer(settings.EMBED_MODEL)
def get_texts(limit=2000):
    with engine.begin() as conn:
        rows = conn.execute(text("SELECT id, title, summary, body FROM cases WHERE body IS NOT NULL ORDER BY id DESC LIMIT :lim"), {"lim": limit}).fetchall()
    items=[]; 
    for rid,title,summary,body in rows:
        t=(title or "")+"\n"+(summary or "")+"\n"+(body or "")
        items.append((rid, t[:6000]))
    return items
def embed_and_store():
    items = get_texts()
    if not items: print("no texts"); return
    ids, texts = zip(*items)
    vecs = MODEL.encode(list(texts), normalize_embeddings=True, convert_to_numpy=True).astype("float32")
    with engine.begin() as conn:
        for rid, v in zip(ids, vecs):
            conn.execute(text("INSERT INTO embeddings(ref_table, ref_id, model, dim, vector) VALUES('cases', :rid, :model, :dim, :vec)"),
                         {"rid": rid, "model": settings.EMBED_MODEL, "dim": int(vecs.shape[1]), "vec": v.tobytes()})
    print(f"embedded {len(ids)} cases.")
if __name__ == "__main__": embed_and_store()
