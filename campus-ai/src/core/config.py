from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    """应用配置管理"""

    # 应用基础配置
    app_name: str = Field(default="campus-ai-service")
    app_version: str = Field(default="1.0.0")
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")

    # API配置
    api_prefix: str = Field(default="/api/v1")
    cors_origins: list[str] = Field(default=["http://localhost:3000", "http://localhost:5173"])

    # 阿里云OSS配置
    oss_endpoint: str = Field(description="阿里云OSS端点")
    oss_access_key_id: str = Field(description="阿里云AccessKey ID")
    oss_access_key_secret: str = Field(description="阿里云AccessKey Secret")
    oss_bucket_name: str = Field(default="campus-ai-models-dev")
    oss_model_prefix: str = Field(default="models/")
    oss_temp_prefix: str = Field(default="temp/")

    # Spring Boot集成配置
    spring_api_base_url: str = Field(default="http://localhost:8080/api")
    spring_api_timeout: int = Field(default=30)
    spring_auth_token: Optional[str] = Field(default=None)

    # 模型预热配置
    preload_kmeans: bool = Field(default=True)
    preload_ahp_weights: bool = Field(default=True)
    preload_lstm: bool = Field(default=False)
    model_cache_dir: str = Field(default="./models_cache")
    max_cache_size_gb: int = Field(default=5)

    # 算法参数配置
    kmeans_n_clusters: int = Field(default=5)
    ahp_consistency_threshold: float = Field(default=0.1)
    lstm_sequence_length: int = Field(default=10)
    nlp_model_name: str = Field(default="bert-base-chinese")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"

def get_settings() -> Settings:
    """获取配置实例（单例模式）"""
    return Settings()