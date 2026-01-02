from qcloud_cos import CosConfig, CosS3Client
from config import settings
import uuid
from datetime import datetime


def get_cos_client():
    config = CosConfig(
        Region=settings.COS_REGION,
        SecretId=settings.COS_SECRET_ID,
        SecretKey=settings.COS_SECRET_KEY,
    )
    return CosS3Client(config)


def upload_file_to_cos(file_content: bytes, filename: str, content_type: str = None) -> str:
    """上传文件到腾讯云COS"""
    client = get_cos_client()
    
    # 生成唯一文件名
    ext = filename.split('.')[-1] if '.' in filename else ''
    date_path = datetime.now().strftime("%Y/%m/%d")
    unique_name = f"{uuid.uuid4().hex}.{ext}" if ext else uuid.uuid4().hex
    key = f"uploads/{date_path}/{unique_name}"
    
    # 上传
    client.put_object(
        Bucket=settings.COS_BUCKET,
        Body=file_content,
        Key=key,
        ContentType=content_type
    )
    
    # 返回访问URL
    if settings.COS_DOMAIN:
        return f"https://{settings.COS_DOMAIN}/{key}"
    return f"https://{settings.COS_BUCKET}.cos.{settings.COS_REGION}.myqcloud.com/{key}"


def generate_upload_presigned_url(filename: str, content_type: str = None) -> dict:
    """生成预签名上传URL，用于前端直传"""
    client = get_cos_client()
    
    ext = filename.split('.')[-1] if '.' in filename else ''
    date_path = datetime.now().strftime("%Y/%m/%d")
    unique_name = f"{uuid.uuid4().hex}.{ext}" if ext else uuid.uuid4().hex
    key = f"uploads/{date_path}/{unique_name}"
    
    url = client.get_presigned_url(
        Method='PUT',
        Bucket=settings.COS_BUCKET,
        Key=key,
        Expired=600  # 10分钟有效期
    )
    
    # 访问URL
    if settings.COS_DOMAIN:
        access_url = f"https://{settings.COS_DOMAIN}/{key}"
    else:
        access_url = f"https://{settings.COS_BUCKET}.cos.{settings.COS_REGION}.myqcloud.com/{key}"
    
    return {
        "upload_url": url,
        "access_url": access_url,
        "key": key
    }
