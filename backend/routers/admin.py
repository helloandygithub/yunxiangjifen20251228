from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from database import get_db
import models
import schemas
from utils import (
    get_current_admin, verify_password, create_access_token,
    clear_activity_cache
)

router = APIRouter(prefix="/admin", tags=["管理后台"])


@router.get("/stats", response_model=schemas.ResponseBase)
async def get_stats(
    db: Session = Depends(get_db),
    admin: models.Admin = Depends(get_current_admin)
):
    """获取统计数据"""
    user_count = db.query(models.User).count()
    activity_count = db.query(models.Activity).filter(models.Activity.status == 'active').count()
    pending_count = db.query(models.ActivitySubmission).filter(
        models.ActivitySubmission.status == 'pending'
    ).count()
    order_count = db.query(models.Order).filter(
        models.Order.status == 'pending'
    ).count()
    
    return schemas.ResponseBase(data={
        "userCount": user_count,
        "activityCount": activity_count,
        "pendingCount": pending_count,
        "orderCount": order_count
    })


@router.post("/login", response_model=schemas.ResponseBase)
async def admin_login(request: schemas.AdminLoginRequest, db: Session = Depends(get_db)):
    """管理员登录"""
    admin = db.query(models.Admin).filter(
        models.Admin.username == request.username
    ).first()
    
    # 开发环境简化密码验证
    if not admin or (admin.password_hash != request.password and not verify_password(request.password, admin.password_hash)):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    if not admin.is_active:
        raise HTTPException(status_code=403, detail="账号已被禁用")
    
    access_token = create_access_token(
        data={"sub": str(admin.id), "type": "admin", "role": admin.role.value}
    )
    
    return schemas.ResponseBase(
        data={
            "access_token": access_token,
            "token_type": "bearer",
            "admin": schemas.AdminResponse.model_validate(admin)
        }
    )


# ========== 活动管理 ==========
@router.get("/activities", response_model=schemas.ResponseBase)
async def get_activities(
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    admin: models.Admin = Depends(get_current_admin)
):
    """获取活动列表"""
    query = db.query(models.Activity)
    
    if status:
        query = query.filter(models.Activity.status == status)
    
    total = query.count()
    activities = query.order_by(models.Activity.created_at.desc())\
        .offset((page - 1) * page_size)\
        .limit(page_size)\
        .all()
    
    items = [schemas.ActivityResponse.model_validate(a) for a in activities]
    
    return schemas.ResponseBase(
        data=schemas.PaginatedResponse(
            total=total, page=page, page_size=page_size, items=items
        )
    )


@router.post("/activities", response_model=schemas.ResponseBase)
async def create_activity(
    request: schemas.ActivityCreate,
    db: Session = Depends(get_db),
    admin: models.Admin = Depends(get_current_admin)
):
    """创建活动"""
    activity = models.Activity(
        title=request.title,
        description=request.description,
        cover_image=request.cover_image,
        audit_type=request.audit_type,
        frequency_type=request.frequency_type,
        max_participations=request.max_participations,
        form_schema=[f.model_dump() for f in request.form_schema],
        reward_points=request.reward_points,
        start_time=request.start_time,
        end_time=request.end_time
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)
    
    return schemas.ResponseBase(
        message="创建成功",
        data=schemas.ActivityResponse.model_validate(activity)
    )


@router.put("/activities/{activity_id}", response_model=schemas.ResponseBase)
async def update_activity(
    activity_id: int,
    request: schemas.ActivityUpdate,
    db: Session = Depends(get_db),
    admin: models.Admin = Depends(get_current_admin)
):
    """更新活动"""
    activity = db.query(models.Activity).filter(models.Activity.id == activity_id).first()
    
    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在")
    
    update_data = request.model_dump(exclude_unset=True)
    
    if "form_schema" in update_data and update_data["form_schema"]:
        update_data["form_schema"] = [f.model_dump() if hasattr(f, 'model_dump') else f for f in update_data["form_schema"]]
    
    for key, value in update_data.items():
        setattr(activity, key, value)
    
    db.commit()
    db.refresh(activity)
    clear_activity_cache(activity_id)
    
    return schemas.ResponseBase(
        message="更新成功",
        data=schemas.ActivityResponse.model_validate(activity)
    )


# ========== 审核管理 ==========
@router.get("/submissions", response_model=schemas.ResponseBase)
async def get_submissions(
    status: Optional[str] = "pending",
    activity_id: Optional[int] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    admin: models.Admin = Depends(get_current_admin)
):
    """获取提交记录列表"""
    query = db.query(models.ActivitySubmission)
    
    if status:
        query = query.filter(models.ActivitySubmission.status == status)
    if activity_id:
        query = query.filter(models.ActivitySubmission.activity_id == activity_id)
    
    total = query.count()
    submissions = query.order_by(models.ActivitySubmission.created_at.desc())\
        .offset((page - 1) * page_size)\
        .limit(page_size)\
        .all()
    
    items = []
    for sub in submissions:
        item = schemas.SubmissionResponse.model_validate(sub)
        item.activity_title = sub.activity.title if sub.activity else None
        items.append(item)
    
    return schemas.ResponseBase(
        data=schemas.PaginatedResponse(
            total=total, page=page, page_size=page_size, items=items
        )
    )


@router.post("/submissions/{submission_id}/audit", response_model=schemas.ResponseBase)
async def audit_submission(
    submission_id: int,
    request: schemas.AuditRequest,
    db: Session = Depends(get_db),
    admin: models.Admin = Depends(get_current_admin)
):
    """审核提交"""
    submission = db.query(models.ActivitySubmission).filter(
        models.ActivitySubmission.id == submission_id
    ).first()
    
    if not submission:
        raise HTTPException(status_code=404, detail="提交记录不存在")
    
    if submission.status != models.SubmissionStatus.pending:
        raise HTTPException(status_code=400, detail="该记录已审核")
    
    user = db.query(models.User).filter(models.User.id == submission.user_id).first()
    activity = submission.activity
    
    submission.status = request.status
    submission.audit_remark = request.remark
    submission.auditor_id = admin.id
    submission.audited_at = datetime.now()
    
    if request.status == "approved":
        # 确定积分数
        points = request.points if request.points is not None else activity.reward_points
        submission.granted_points = points
        
        if points > 0:
            # 发放积分
            user.points_balance += points
            
            # 记录流水
            points_log = models.PointsLog(
                user_id=user.id,
                points=points,
                balance_after=user.points_balance,
                type=models.PointsLogType.earn,
                source="activity_audit",
                reference_id=submission.id,
                remark=f"活动审核通过: {activity.title}"
            )
            db.add(points_log)
    
    db.commit()
    
    return schemas.ResponseBase(message="审核成功")


# ========== 订单管理 ==========
@router.get("/orders", response_model=schemas.ResponseBase)
async def get_orders(
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    admin: models.Admin = Depends(get_current_admin)
):
    """获取订单列表"""
    query = db.query(models.Order)
    
    if status:
        query = query.filter(models.Order.status == status)
    
    total = query.count()
    orders = query.order_by(models.Order.created_at.desc())\
        .offset((page - 1) * page_size)\
        .limit(page_size)\
        .all()
    
    items = []
    for order in orders:
        item = schemas.OrderResponse.model_validate(order)
        item.product_name = order.product.name if order.product else None
        items.append(item)
    
    return schemas.ResponseBase(
        data=schemas.PaginatedResponse(
            total=total, page=page, page_size=page_size, items=items
        )
    )


@router.post("/orders/{order_id}/deliver", response_model=schemas.ResponseBase)
async def deliver_order(
    order_id: int,
    request: schemas.DeliverRequest,
    db: Session = Depends(get_db),
    admin: models.Admin = Depends(get_current_admin)
):
    """订单发货"""
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    if order.status != models.OrderStatus.pending:
        raise HTTPException(status_code=400, detail="订单状态不允许发货")
    
    order.shipping_info = request.shipping_info
    order.status = models.OrderStatus.shipped
    
    db.commit()
    
    return schemas.ResponseBase(message="发货成功")


# ========== 用户管理 ==========
@router.get("/users", response_model=schemas.ResponseBase)
async def get_users(
    phone: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    admin: models.Admin = Depends(get_current_admin)
):
    """获取用户列表"""
    query = db.query(models.User)
    
    if phone:
        query = query.filter(models.User.phone.like(f"%{phone}%"))
    
    total = query.count()
    users = query.order_by(models.User.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    items = [schemas.UserResponse.model_validate(user) for user in users]
    
    return schemas.ResponseBase(
        data=schemas.PaginatedResponse(
            total=total, page=page, page_size=page_size, items=items
        )
    )


@router.post("/users/{user_id}/adjust-points", response_model=schemas.ResponseBase)
async def adjust_user_points(
    user_id: int,
    request: schemas.PointsAdjustRequest,
    db: Session = Depends(get_db),
    admin: models.Admin = Depends(get_current_admin)
):
    """调整用户积分"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    points_change = request.points if request.type == 'add' else -request.points
    
    if request.type == 'deduct' and user.points_balance < request.points:
        raise HTTPException(status_code=400, detail="用户积分不足")
    
    user.points_balance += points_change
    
    # 记录积分变动
    log = models.PointsLog(
        user_id=user_id,
        points=points_change,
        type='admin_adjust',
        remark=request.remark or f"管理员{'增加' if request.type == 'add' else '扣除'}积分"
    )
    db.add(log)
    
    db.commit()
    
    return schemas.ResponseBase(message="积分调整成功")


@router.post("/users/{user_id}/toggle-status", response_model=schemas.ResponseBase)
async def toggle_user_status(
    user_id: int,
    db: Session = Depends(get_db),
    admin: models.Admin = Depends(get_current_admin)
):
    """启用/禁用用户"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    user.is_active = not user.is_active
    db.commit()
    
    return schemas.ResponseBase(message=f"用户已{'启用' if user.is_active else '禁用'}")


# ========== 商品管理 ==========
@router.post("/products", response_model=schemas.ResponseBase)
async def create_product(
    request: schemas.ProductCreate,
    db: Session = Depends(get_db),
    admin: models.Admin = Depends(get_current_admin)
):
    """创建商品"""
    product = models.Product(**request.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    
    return schemas.ResponseBase(
        message="创建成功",
        data=schemas.ProductResponse.model_validate(product)
    )


@router.put("/products/{product_id}", response_model=schemas.ResponseBase)
async def update_product(
    product_id: int,
    request: schemas.ProductCreate,
    db: Session = Depends(get_db),
    admin: models.Admin = Depends(get_current_admin)
):
    """更新商品"""
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    
    for key, value in request.model_dump().items():
        setattr(product, key, value)
    
    db.commit()
    db.refresh(product)
    
    return schemas.ResponseBase(
        message="更新成功",
        data=schemas.ProductResponse.model_validate(product)
    )
