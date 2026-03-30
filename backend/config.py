import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Mahabharata AI Agent"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite:///./mahabharata.db"
    
    # ChromaDB
    CHROMA_PERSIST_DIR: str = os.path.join(os.path.dirname(__file__), "vectordb", "chroma_store")
    CHROMA_COLLECTION_NAME: str = "mahabharata_knowledge"
    
    # Embedding model
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    
    # Auth
    SECRET_KEY: str = "mahabharata-secret-key-change-in-production-2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # Data paths
    DATA_DIR: str = os.path.join(os.path.dirname(__file__), "data")
    
    # Agent settings
    SIMILARITY_THRESHOLD: float = 0.35
    TOP_K_RESULTS: int = 5
    HIGH_CONFIDENCE_THRESHOLD: float = 0.70
    
    class Config:
        env_file = ".env"

settings = Settings()
