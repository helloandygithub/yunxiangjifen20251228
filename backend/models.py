from sqlalchemy import (
    Column, BigInteger, String, Integer, Boolean, Text, 
    DateTime, Enum, JSON, ForeignKey
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class UserStatus(enum.Enum):
    active = "active"
    inactive = "inactive"


class ActivityStatus(enum.Enum):
    draft = "draft"
    active = "active"
    ended = "ended"


class AuditType(enum.Enum):
    auto = "auto"
    manual = "manual"


class FrequencyType(enum.Enum):
    once = "once"
    daily = "daily"
    unlimited = "unlimited"


class SubmissionStatus(enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class ProductType(enum.Enum):
    virtual = "virtual"
    physical = "physical"


class OrderStatus(enum.Enum):
    pending = "pending"
    shipped = "shipped"
    completed = "completed"
    cancelled = "cancelled"


class PointsLogType(enum.Enum):
    earn = "earn"
    spend = "spend"
    refund = "refund"
    adjust = "adjust"


class AdminRole(enum.Enum):
    super_admin = "super_admin"
    admin = "admin"
    auditor = "auditor"


# 用户表
class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    phone = Column(String(20), unique=True, nullable=True, index=True)  # Allow null for WeChat-only users initially
    wx_openid = Column(String(64), unique=True, nullable=True, index=True)
    wx_unionid = Column(String(64), unique=True, nullable=True, index=True)
    nickname = Column(String(64), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    points_balance = Column(Integer, default=0)
    fingerprint_hash = Column(String(255))
    referrer_id = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    invite_code = Column(String(20), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    submissions = relationship("ActivitySubmission", back_populates="user")
    orders = relationship("Order", back_populates="user")
    points_logs = relationship("PointsLog", back_populates="user")
    referrer = relationship("User", remote_side=[id])


# 管理员表
class Admin(Base):
    __tablename__ = "admins"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(AdminRole), default=AdminRole.auditor)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())


# 活动配置表
class Activity(Base):
    __tablename__ = "activities"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    cover_image = Column(String(500))
    status = Column(Enum(ActivityStatus), default=ActivityStatus.draft)
    audit_type = Column(Enum(AuditType), default=AuditType.manual)
    frequency_type = Column(Enum(FrequencyType), default=FrequencyType.once)
    max_participations = Column(Integer, default=1)
    form_schema = Column(JSON, nullable=False)
    reward_points = Column(Integer, default=0)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    submissions = relationship("ActivitySubmission", back_populates="activity")


# 提交记录表
class ActivitySubmission(Base):
    __tablename__ = "activity_submissions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    activity_id = Column(BigInteger, ForeignKey("activities.id"), nullable=False)
    submission_data = Column(JSON, nullable=False)
    status = Column(Enum(SubmissionStatus), default=SubmissionStatus.pending)
    granted_points = Column(Integer, default=0)
    audit_remark = Column(String(500))
    auditor_id = Column(BigInteger)
    audited_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="submissions")
    activity = relationship("Activity", back_populates="submissions")


# 积分流水表
class PointsLog(Base):
    __tablename__ = "points_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    points = Column(Integer, nullable=False)
    balance_after = Column(Integer, nullable=False)
    type = Column(Enum(PointsLogType), nullable=False)
    source = Column(String(50), nullable=False)
    reference_id = Column(BigInteger)
    remark = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="points_logs")


# 商品表
class Product(Base):
    __tablename__ = "products"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    type = Column(Enum(ProductType), default=ProductType.virtual)
    price_points = Column(Integer, nullable=False)
    stock = Column(Integer, default=0)
    image_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    orders = relationship("Order", back_populates="product")


# 订单表
class Order(Base):
    __tablename__ = "orders"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    order_no = Column(String(32), unique=True, nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    product_id = Column(BigInteger, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=1)
    points_cost = Column(Integer, nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.pending)
    delivery_info = Column(JSON)
    shipping_info = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="orders")
    product = relationship("Product", back_populates="orders")
