from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime
from enum import Enum


# ============ 通用响应 ============
class ResponseBase(BaseModel):
    code: int = 0
    message: str = "success"
    data: Any = None


# ============ 用户相关 ============
class LoginRequest(BaseModel):
    phone: str = Field(..., pattern=r"^1[3-9]\d{9}$", description="手机号")
    code: str = Field(..., min_length=4, max_length=6, description="验证码")
    fingerprint: Optional[str] = None
    referrer_code: Optional[str] = None


class SendCodeRequest(BaseModel):
    phone: str = Field(..., pattern=r"^1[3-9]\d{9}$")
    captcha_token: Optional[str] = None


class WxLoginRequest(BaseModel):
    code: str = Field(..., description="微信getPhoneNumber返回的code")
    openid: Optional[str] = None
    referrer_code: Optional[str] = None


class UserProfile(BaseModel):
    id: int
    phone: Optional[str] = None
    points_balance: int
    invite_code: str
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    wx_openid: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserProfile
    openid: Optional[str] = None
    unionid: Optional[str] = None


# ============ 活动相关 ============
class FormFieldSchema(BaseModel):
    key: str
    label: str
    type: str  # text, textarea, image, file, number, select, date
    required: bool = False
    placeholder: Optional[str] = None
    options: Optional[List[str]] = None
    max_length: Optional[int] = None


class ActivityBase(BaseModel):
    title: str
    description: Optional[str] = None
    cover_image: Optional[str] = None
    audit_type: str = "manual"
    frequency_type: str = "once"
    max_participations: int = 1
    form_schema: List[FormFieldSchema]
    reward_points: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class ActivityCreate(ActivityBase):
    pass


class ActivityUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    cover_image: Optional[str] = None
    status: Optional[str] = None
    audit_type: Optional[str] = None
    frequency_type: Optional[str] = None
    max_participations: Optional[int] = None
    form_schema: Optional[List[FormFieldSchema]] = None
    reward_points: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class ActivityResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    cover_image: Optional[str]
    status: str
    audit_type: str
    frequency_type: str
    max_participations: int
    form_schema: List[dict]
    reward_points: int
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    created_at: datetime
    user_status: Optional[str] = None  # 用户参与状态

    class Config:
        from_attributes = True


# ============ 提交相关 ============
class SubmissionCreate(BaseModel):
    submission_data: dict


class SubmissionResponse(BaseModel):
    id: int
    activity_id: int
    activity_title: Optional[str] = None
    submission_data: dict
    status: str
    granted_points: int
    audit_remark: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class AuditRequest(BaseModel):
    status: str = Field(..., pattern=r"^(approved|rejected)$")
    points: Optional[int] = None
    remark: Optional[str] = None


# ============ 商品相关 ============
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    type: str = "virtual"
    price_points: int
    stock: int = 0
    image_url: Optional[str] = None
    sort_order: int = 0


class ProductCreate(ProductBase):
    pass


class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    type: str
    price_points: int
    stock: int
    image_url: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============ 订单相关 ============
class RedeemRequest(BaseModel):
    product_id: int
    quantity: int = 1
    delivery_info: Optional[dict] = None  # 实物商品需要收货地址


class OrderResponse(BaseModel):
    id: int
    order_no: str
    product_id: int
    product_name: Optional[str] = None
    quantity: int
    points_cost: int
    status: str
    delivery_info: Optional[dict]
    shipping_info: Optional[dict]
    created_at: datetime

    class Config:
        from_attributes = True


class DeliverRequest(BaseModel):
    shipping_info: dict  # 物流信息或卡密


# ============ 管理员相关 ============
class AdminLoginRequest(BaseModel):
    username: str
    password: str


class AdminResponse(BaseModel):
    id: int
    username: str
    role: str

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: int
    phone: Optional[str] = None
    points_balance: int
    invite_code: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============ 分页 ============
class PaginationParams(BaseModel):
    page: int = 1
    page_size: int = 20


class PaginatedResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[Any]


# ============ 管理员操作 ============
class PointsAdjustRequest(BaseModel):
    type: str  # 'add' or 'deduct'
    points: int
    remark: Optional[str] = None
