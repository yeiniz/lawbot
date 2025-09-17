import subprocess, sys
def run(cmd): print("+", " ".join(cmd)); subprocess.check_call(cmd)
if __name__ == "__main__":
    run([sys.executable, "-c", "from app.db import init_db; init_db(); print('DB initialized')"])
    run([sys.executable, "app/etl/fetch_korean_cases.py"])
    run([sys.executable, "app/etl/fetch_courtlistener.py"])
    run([sys.executable, "app/etl/build_embeddings.py"])
    run([sys.executable, "app/retrieval/index_faiss.py"])
    print("All done.")
