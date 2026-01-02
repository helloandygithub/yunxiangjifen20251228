from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
import models
import schemas
from utils import get_current_user, generate_order_no

router = APIRouter(prefix="/mall", tags=["积分商城"])


@router.get("/products", response_model=schemas.ResponseBase)
async def get_products(
    category: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    """获取商品列表"""
    query = db.query(models.Product).filter(models.Product.is_active == True)
    
    if category:
        query = query.filter(models.Product.type == category)
    
    total = query.count()
    products = query.order_by(models.Product.sort_order.desc(), models.Product.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    items = [schemas.ProductResponse.model_validate(p) for p in products]
    
    return schemas.ResponseBase(
        data=schemas.PaginatedResponse(
            total=total, page=page, page_size=page_size, items=items
        )
    )


@router.get("/products/{product_id}", response_model=schemas.ResponseBase)
async def get_product_detail(
    product_id: int,
    db: Session = Depends(get_db)
):
    """获取商品详情"""
    product = db.query(models.Product).filter(
        models.Product.id == product_id,
        models.Product.is_active == True
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在或已下架")
    
    return schemas.ResponseBase(data=schemas.ProductResponse.model_validate(product))


@router.post("/redeem", response_model=schemas.ResponseBase)
async def redeem_product(
    request: schemas.RedeemRequest,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    """积分兑换商品"""
    product = db.query(models.Product).filter(
        models.Product.id == request.product_id,
        models.Product.status == 'active'
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在或已下架")
    
    if product.stock <= 0:
        raise HTTPException(status_code=400, detail="商品库存不足")
    
    if user.points_balance < product.points_cost:
        raise HTTPException(status_code=400, detail="积分不足")
    
    # 扣除积分
    user.points_balance -= product.points_cost
    
    # 减少库存
    product.stock -= 1
    
    # 创建订单
    order = models.Order(
        user_id=user.id,
        product_id=product.id,
        order_no=generate_order_no(),
        points_cost=product.points_cost,
        shipping_address=request.shipping_address if product.type == 'physical' else None,
        status=models.OrderStatus.pending
    )
    db.add(order)
    
    # 记录积分变动
    log = models.PointsLog(
        user_id=user.id,
        points=-product.points_cost,
        type='redeem',
        remark=f"兑换商品: {product.name}"
    )
    db.add(log)
    
    db.commit()
    db.refresh(order)
    
    return schemas.ResponseBase(
        message="兑换成功",
        data=schemas.OrderResponse.model_validate(order)
    )
