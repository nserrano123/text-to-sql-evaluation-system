"""Application configuration"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Supabase Configuration
    supabase_url: str
    supabase_key: str
    supabase_service_role_key: str = ""
    
    # FastAPI Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True
    
    # CORS Configuration
    allowed_origins: str = "http://localhost:3000"
    
    # Chart Generation
    charts_output_dir: str = "./charts"
    charts_dpi: int = 300
    
    # Export Configuration
    export_output_dir: str = "./exports"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse allowed origins string into list"""
        return [origin.strip() for origin in self.allowed_origins.split(",")]


# Global settings instance
settings = Settings()
