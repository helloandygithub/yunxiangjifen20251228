from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from database import get_db
import models
import schemas
from utils import get_current_user

router = APIRouter(prefix="/user", tags=["用户端"])


@router.get("/profile", response_model=schemas.ResponseBase)
@router.get("/info", response_model=schemas.ResponseBase)
async def get_profile(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    """获取用户信息"""
    invite_count = db.query(models.User).filter(
        models.User.referrer_id == user.id
    ).count()
    
    return schemas.ResponseBase(data={
        "user": schemas.UserResponse.model_validate(user),
        "invite_count": invite_count
    })


@router.get("/records", response_model=schemas.ResponseBase)
async def get_records(
    type: str = "points",
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    """获取用户记录"""
    result = {}
    
    if type == "points":
        query = db.query(models.PointsLog).filter(models.PointsLog.user_id == user.id)
        total = query.count()
        items = query.order_by(models.PointsLog.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        result["points"] = {
            "total": total,
            "items": [schemas.PointsLogResponse.model_validate(item) for item in items]
        }
    
    elif type == "orders":
        query = db.query(models.Order).filter(models.Order.user_id == user.id)
        total = query.count()
        orders = query.order_by(models.Order.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        items = []
        for order in orders:
            item = schemas.OrderResponse.model_validate(order)
            item_dict = item.model_dump()
            item_dict["product_name"] = order.product.name if order.product else "未知商品"
            items.append(item_dict)
        result["orders"] = {"total": total, "items": items}
    
    elif type == "submissions":
        query = db.query(models.ActivitySubmission).filter(
            models.ActivitySubmission.user_id == user.id
        )
        total = query.count()
        submissions = query.order_by(models.ActivitySubmission.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        items = []
        for sub in submissions:
            item = schemas.SubmissionResponse.model_validate(sub)
            item_dict = item.model_dump()
            item_dict["activity_title"] = sub.activity.title if sub.activity else "未知活动"
            items.append(item_dict)
        result["submissions"] = {"total": total, "items": items}
    
    return schemas.ResponseBase(data=result)


@router.get("/invite-stats", response_model=schemas.ResponseBase)
async def get_invite_stats(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    """获取邀请统计"""
    invitees = db.query(models.User).filter(
        models.User.referrer_id == user.id
    ).order_by(models.User.created_at.desc()).limit(10).all()
    
    total_points = db.query(func.sum(models.PointsLog.points)).filter(
        models.PointsLog.user_id == user.id,
        models.PointsLog.type == 'invite'
    ).scalar() or 0
    
    return schemas.ResponseBase(data={
        "invite_code": user.invite_code,
        "invite_count": len(invitees),
        "total_points": total_points,
        "invitees": [
            {"phone": u.phone[:3] + "****" + u.phone[-4:], "created_at": u.created_at}
            for u in invitees
        ]
    })
