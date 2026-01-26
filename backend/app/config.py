"""
Configuration management using Pydantic Settings
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    database_url: str = "sqlite:///./exam_checker.db"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # API Keys
    google_cloud_vision_api_key: Optional[str] = ""
    mathpix_app_id: Optional[str] = None
    mathpix_app_key: Optional[str] = None
    gemini_api_key: Optional[str] = "AIzaSyBXEeC0uLaS6QGDCqMpgNXoG4CJMnhXyHE"
    claude_api_key: Optional[str] = None
    
    # Storage
    storage_type: str = "local"  # local, s3, gcs
    upload_dir: str = "./uploads"
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    s3_bucket_name: Optional[str] = None
    gcs_bucket_name: Optional[str] = None
    google_application_credentials: Optional[str] = None
    
    # Application
    secret_key: str = "dev-secret-key-change-in-production"
    debug: bool = True
    backend_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:8501"
    
    # OCR Settings
    ocr_confidence_threshold: float = 0.70
    dpi_setting: int = 300
    
    # Evaluation
    use_claude: bool = False  # False = Gemini, True = Claude
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
