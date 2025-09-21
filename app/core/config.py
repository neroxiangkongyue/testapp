# 应用配置
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite:///./english_graph.db"
    secret_key: str = "your-secret-key-here"
    
    class Config:
        env_file = ".env"

settings = Settings()