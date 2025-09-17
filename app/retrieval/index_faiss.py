import os, faiss, numpy as np
from sqlalchemy import text
from app.db import engine
INDEX_PATH = "data/index/cases.faiss"
def load_vectors():
    with engine.begin() as conn:
        rows = conn.execute(text("SELECT ref_id, vector, dim FROM embeddings WHERE ref_table='cases' ORDER BY id")).fetchall()
    ids, vecs = [], []
    for rid, blob, dim in rows:
        v = np.frombuffer(blob, dtype=np.float32).reshape((dim,))
        ids.append(int(rid)); vecs.append(v)
    if not vecs: return None, None
    return np.vstack(vecs), np.array(ids, dtype=np.int64)
def build_index():
    X, ids = load_vectors()
    os.makedirs("data/index", exist_ok=True)
    if X is None: print("No vectors to index."); return
    index = faiss.IndexFlatIP(X.shape[1]); index.add(X)
    faiss.write_index(index, INDEX_PATH)
    with open(INDEX_PATH+".ids","wb") as f: f.write(ids.tobytes())
    print(f"Index built: {INDEX_PATH}")
if __name__ == "__main__": build_index()
