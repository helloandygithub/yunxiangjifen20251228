from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, date
from typing import Optional
from database import get_db
import models
import schemas
from utils import get_current_user, cache_activity, get_cached_activity

router = APIRouter(prefix="/activities", tags=["活动"])


def get_user_activity_status(db: Session, user_id: int, activity: models.Activity) -> str:
    """获取用户对某活动的参与状态"""
    submissions = db.query(models.ActivitySubmission).filter(
        models.ActivitySubmission.user_id == user_id,
        models.ActivitySubmission.activity_id == activity.id
    ).all()
    
    if not submissions:
        return "available"
    
    # 检查是否有待审核的
    pending = [s for s in submissions if s.status == models.SubmissionStatus.pending]
    if pending:
        return "pending"
    
    # 根据频次类型判断
    if activity.frequency_type == models.FrequencyType.once:
        approved = [s for s in submissions if s.status == models.SubmissionStatus.approved]
        if approved:
            return "completed"
        return "available"
    
    elif activity.frequency_type == models.FrequencyType.daily:
        today = date.today()
        today_submissions = [s for s in submissions if s.created_at.date() == today]
        if len(today_submissions) >= activity.max_participations:
            return "limit_reached"
        return "available"
    
    return "available"


@router.get("", response_model=schemas.ResponseBase)
async def get_activities(
    status: Optional[str] = "active",
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    """获取活动列表（公开接口）"""
    query = db.query(models.Activity)
    
    if status:
        query = query.filter(models.Activity.status == status)
    
    total = query.count()
    activities = query.order_by(models.Activity.created_at.desc())\
        .offset((page - 1) * page_size)\
        .limit(page_size)\
        .all()
    
    # 返回活动列表，不包含用户状态（未登录用户也可访问）
    items = []
    for activity in activities:
        item = schemas.ActivityResponse.model_validate(activity)
        item.user_status = "available"  # 默认状态
        items.append(item)
    
    return schemas.ResponseBase(
        data=schemas.PaginatedResponse(
            total=total,
            page=page,
            page_size=page_size,
            items=items
        )
    )


@router.get("/{activity_id}", response_model=schemas.ResponseBase)
async def get_activity_detail(
    activity_id: int,
    db: Session = Depends(get_db)
):
    """获取活动详情（公开接口）"""
    activity = db.query(models.Activity).filter(models.Activity.id == activity_id).first()
    
    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在")
    
    response = schemas.ActivityResponse.model_validate(activity)
    response.user_status = "available"  # 未登录时默认可参与
    
    return schemas.ResponseBase(data=response)


@router.post("/{activity_id}/submit", response_model=schemas.ResponseBase)
async def submit_activity(
    activity_id: int,
    request: schemas.SubmissionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """提交活动"""
    activity = db.query(models.Activity).filter(
        models.Activity.id == activity_id,
        models.Activity.status == models.ActivityStatus.active
    ).first()
    
    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在或未开放")
    
    # 检查时间
    now = datetime.now()
    if activity.start_time and now < activity.start_time:
        raise HTTPException(status_code=400, detail="活动未开始")
    if activity.end_time and now > activity.end_time:
        raise HTTPException(status_code=400, detail="活动已结束")
    
    # 检查参与资格
    user_status = get_user_activity_status(db, current_user.id, activity)
    if user_status == "pending":
        raise HTTPException(status_code=400, detail="您有待审核的提交，请等待审核结果")
    if user_status == "completed":
        raise HTTPException(status_code=400, detail="您已完成该活动")
    if user_status == "limit_reached":
        raise HTTPException(status_code=400, detail="今日参与次数已满")
    
    # 校验表单数据
    form_schema = activity.form_schema
    submission_data = request.submission_data
    
    for field in form_schema:
        key = field.get("key")
        required = field.get("required", False)
        
        if required and (key not in submission_data or not submission_data[key]):
            raise HTTPException(
                status_code=400,
                detail=f"请填写必填项: {field.get('label', key)}"
            )
    
    # 创建提交记录
    submission = models.ActivitySubmission(
        user_id=current_user.id,
        activity_id=activity_id,
        submission_data=submission_data,
        status=models.SubmissionStatus.pending
    )
    db.add(submission)
    
    # 自动审核
    if activity.audit_type == models.AuditType.auto:
        submission.status = models.SubmissionStatus.approved
        submission.granted_points = activity.reward_points
        submission.audited_at = datetime.now()
        
        # 发放积分
        current_user.points_balance += activity.reward_points
        
        # 记录积分流水
        points_log = models.PointsLog(
            user_id=current_user.id,
            points=activity.reward_points,
            balance_after=current_user.points_balance,
            type=models.PointsLogType.earn,
            source="activity",
            reference_id=submission.id,
            remark=f"参与活动: {activity.title}"
        )
        db.add(points_log)
    
    db.commit()
    db.refresh(submission)
    
    return schemas.ResponseBase(
        message="提交成功" if activity.audit_type == models.AuditType.manual else "提交成功，积分已发放",
        data=schemas.SubmissionResponse.model_validate(submission)
    )
