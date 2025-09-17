from pydantic import BaseModel
from dotenv import load_dotenv
import os
load_dotenv()
class Settings(BaseModel):
    LAW_OC: str = os.getenv("LAW_OC", "test")
    COURTLISTENER_TOKEN: str | None = os.getenv("COURTLISTENER_TOKEN")
    EMBED_MODEL: str = os.getenv("EMBED_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    USE_OLLAMA: bool = os.getenv("USE_OLLAMA", "false").lower() == "true"
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.1")
    DB_URL: str = os.getenv("DB_URL", "mysql+pymysql://app:app1234@localhost:3306/ai_legal_sim?charset=utf8mb4")
settings = Settings()
