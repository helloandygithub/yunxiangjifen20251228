from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "积分活动运营平台"
    DEBUG: bool = False  # 生产环境默认关闭
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    
    # 数据库配置
    DATABASE_URL: str = "mysql+pymysql://points_user:points123456@mysql:3306/points_platform"
    
    # Redis配置
    REDIS_URL: str = "redis://redis:6379/0"
    
    # JWT配置
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天
    
    # 腾讯云COS配置
    COS_SECRET_ID: str = ""
    COS_SECRET_KEY: str = ""
    COS_REGION: str = "ap-guangzhou"
    COS_BUCKET: str = ""
    COS_DOMAIN: str = ""  # 自定义域名或CDN域名
    
    # 腾讯云短信配置
    SMS_SDK_APP_ID: str = ""
    SMS_SIGN_NAME: str = ""
    SMS_TEMPLATE_ID: str = ""
    SMS_SECRET_ID: str = ""  # 专用短信密钥ID（可选，默认使用COS密钥）
    SMS_SECRET_KEY: str = ""  # 专用短信密钥Key（可选）
    
    # 微信小程序配置
    WX_APPID: str = ""
    WX_SECRET: str = ""
    
    # 验证码配置
    SMS_CODE_EXPIRE: int = 300  # 5分钟
    SMS_CODE_LENGTH: int = 6
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
