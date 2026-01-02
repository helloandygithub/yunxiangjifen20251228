from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import (
    auth_router, activities_router, mall_router,
    user_router, admin_router, upload_router
)
from config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description="积分活动运营平台 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS配置 - 生产环境限制具体域名
ALLOWED_ORIGINS = [
    "https://cloudexp.top",
    "https://www.cloudexp.top",
] if not settings.DEBUG else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth_router, prefix="/api")
app.include_router(activities_router, prefix="/api")
app.include_router(mall_router, prefix="/api")
app.include_router(user_router, prefix="/api")
app.include_router(admin_router, prefix="/api")
app.include_router(upload_router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "积分活动运营平台 API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
