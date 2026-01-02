from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import Optional
import schemas
from utils import get_current_user
from utils.cos import upload_file_to_cos, generate_upload_presigned_url
import models

router = APIRouter(prefix="/upload", tags=["文件上传"])

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp", "pdf"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("", response_model=schemas.ResponseBase)
async def upload_file(
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user)
):
    """上传文件到腾讯云COS"""
    # 检查文件扩展名
    if file.filename:
        ext = file.filename.split('.')[-1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail="不支持的文件类型")
    
    # 读取文件内容
    content = await file.read()
    
    # 检查文件大小
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="文件大小超过限制(10MB)")
    
    # 上传到COS
    try:
        url = upload_file_to_cos(content, file.filename, file.content_type)
        return schemas.ResponseBase(
            message="上传成功",
            data={"url": url}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


@router.get("/presign", response_model=schemas.ResponseBase)
async def get_presigned_url(
    filename: str,
    content_type: Optional[str] = None,
    current_user: models.User = Depends(get_current_user)
):
    """获取预签名上传URL（前端直传）"""
    # 检查文件扩展名
    ext = filename.split('.')[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="不支持的文件类型")
    
    try:
        result = generate_upload_presigned_url(filename, content_type)
        return schemas.ResponseBase(data=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取上传地址失败: {str(e)}")
