from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    app_title: str = "ShareSlide API"
    app_description: str = "股票数据可视化展示系统的API接口"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # 数据缓存设置
    cache_dir: str = "cache"
    reveal_output_dir: str = "reveal"
    
    # API 设置
    api_prefix: str = "/api"
    cors_origins: list = ["*"]  # 生产环境中应指定具体域名
    
    # AkShare 设置
    akshare_timeout: int = 30
    
    class Config:
        env_file = ".env"


settings = Settings()