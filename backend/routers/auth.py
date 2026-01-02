from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas
from utils import (
    create_access_token, generate_invite_code, generate_sms_code,
    set_sms_code, get_sms_code, delete_sms_code, check_sms_limit
)
from utils.wechat import get_phone_number, get_wx_session
from config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/send-code", response_model=schemas.ResponseBase)
async def send_sms_code(request: schemas.SendCodeRequest, db: Session = Depends(get_db)):
    """发送短信验证码"""
    phone = request.phone
    
    # 检查频率限制
    if not check_sms_limit(phone):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="发送过于频繁，请稍后再试"
        )
    
    # 生成验证码
    code = generate_sms_code()
    set_sms_code(phone, code)
    
    # 调用腾讯云短信API发送
    from utils.sms import send_sms_code
    sms_result = send_sms_code(phone, code)
    
    if not sms_result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="短信发送失败，请稍后重试"
        )
    
    return schemas.ResponseBase(message="验证码已发送")


@router.post("/login", response_model=schemas.ResponseBase)
async def login(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    """手机号登录/注册"""
    phone = request.phone
    code = request.code
    
    # 验证验证码
    cached_code = get_sms_code(phone)
    if not cached_code or cached_code != code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码错误或已过期"
        )
    
    # 删除已使用的验证码
    delete_sms_code(phone)
    
    # 查找或创建用户
    user = db.query(models.User).filter(models.User.phone == phone).first()
    
    if not user:
        # 新用户注册
        invite_code = generate_invite_code()
        while db.query(models.User).filter(models.User.invite_code == invite_code).first():
            invite_code = generate_invite_code()
        
        user = models.User(
            phone=phone,
            invite_code=invite_code,
            fingerprint_hash=request.fingerprint
        )
        
        # 处理推荐人
        if request.referrer_code:
            referrer = db.query(models.User).filter(
                models.User.invite_code == request.referrer_code
            ).first()
            if referrer:
                user.referrer_id = referrer.id
        
        db.add(user)
        db.commit()
        db.refresh(user)
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号已被禁用"
        )
    
    # 生成token
    access_token = create_access_token(
        data={"sub": str(user.id), "type": "user"}
    )
    
    return schemas.ResponseBase(
        data=schemas.TokenResponse(
            access_token=access_token,
            user=schemas.UserProfile.model_validate(user)
        )
    )


@router.post("/wx-login", response_model=schemas.ResponseBase)
async def wx_login(request: schemas.WxLoginRequest, db: Session = Depends(get_db)):
    """微信小程序一键登录"""
    # 检查微信配置
    if not settings.WX_APPID or not settings.WX_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="微信登录未配置"
        )
    
    try:
        # 通过code获取手机号
        phone = await get_phone_number(request.code)
        logger.info(f"微信登录获取手机号: {phone[:3]}****{phone[-4:]}")
    except Exception as e:
        logger.error(f"微信获取手机号失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"获取手机号失败: {str(e)}"
        )
    
    # 查找或创建用户
    user = db.query(models.User).filter(models.User.phone == phone).first()
    
    if not user:
        # 新用户注册
        invite_code = generate_invite_code()
        while db.query(models.User).filter(models.User.invite_code == invite_code).first():
            invite_code = generate_invite_code()
        
        user = models.User(
            phone=phone,
            invite_code=invite_code,
            wx_openid=request.openid if hasattr(request, 'openid') else None
        )
        
        # 处理推荐人
        if request.referrer_code:
            referrer = db.query(models.User).filter(
                models.User.invite_code == request.referrer_code
            ).first()
            if referrer:
                user.referrer_id = referrer.id
        
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"微信登录新用户注册: {phone}")
    else:
        # 更新openid（如果有）
        if hasattr(request, 'openid') and request.openid and not user.wx_openid:
            user.wx_openid = request.openid
            db.commit()
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号已被禁用"
        )
    
    # 生成token
    access_token = create_access_token(
        data={"sub": str(user.id), "type": "user"}
    )
    
    return schemas.ResponseBase(
        data=schemas.TokenResponse(
            access_token=access_token,
            user=schemas.UserProfile.model_validate(user)
        )
    )
