# 积分活动运营平台

基于 PRD 文档开发的积分活动运营平台，支持 PC Web 和微信小程序双端。

## 技术栈

- **后端**: Python FastAPI + SQLAlchemy + MySQL + Redis
- **管理后台**: Vue3 + Element Plus + Vite
- **用户端**: Uni-app (Vue3) - 支持 H5 和微信小程序
- **存储**: 腾讯云 COS
- **部署**: Docker Compose

## 项目结构

```
├── backend/              # FastAPI 后端
│   ├── routers/         # API 路由
│   ├── utils/           # 工具函数
│   ├── models.py        # 数据库模型
│   ├── schemas.py       # Pydantic 模型
│   ├── config.py        # 配置文件
│   └── main.py          # 入口文件
├── admin/               # Vue3 管理后台
│   └── src/
│       ├── views/       # 页面组件
│       ├── router/      # 路由配置
│       ├── stores/      # Pinia 状态
│       └── utils/       # 工具函数
├── webapp/              # Uni-app 用户端
│   └── src/
│       ├── pages/       # 页面
│       ├── stores/      # Pinia 状态
│       └── utils/       # 工具函数
└── docker-compose.yml   # Docker 编排
```

## 快速开始

### 1. 配置环境变量

```bash
cp backend/.env.example backend/.env
```

编辑 `backend/.env` 文件，配置腾讯云相关参数。

### 2. 启动开发环境

```bash
docker-compose up -d
```

### 3. 访问服务

- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs
- **管理后台**: http://localhost:3000
- **用户端 H5**: http://localhost:5173

### 4. 默认账号

管理后台登录：
- 用户名: `admin`
- 密码: `admin123456`

## 腾讯云配置

### COS 对象存储

1. 登录腾讯云控制台，创建 COS 存储桶
2. 获取 SecretId 和 SecretKey
3. 配置到 `.env` 文件

```env
COS_SECRET_ID=your-secret-id
COS_SECRET_KEY=your-secret-key
COS_REGION=ap-guangzhou
COS_BUCKET=your-bucket-name
COS_DOMAIN=your-custom-domain.com
```

### 短信服务 (可选)

1. 开通腾讯云短信服务
2. 创建签名和模板
3. 配置到 `.env` 文件

## 生产部署

### 1. 修改配置

```env
DEBUG=false
SECRET_KEY=your-production-secret-key
```

### 2. 构建镜像

```bash
docker-compose -f docker-compose.prod.yml build
```

### 3. 启动服务

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 微信小程序

1. 在 `webapp/src/manifest.json` 中配置小程序 AppID
2. 构建小程序:

```bash
cd webapp
npm run build:mp-weixin
```

3. 使用微信开发者工具导入 `dist/build/mp-weixin` 目录

## API 接口

### 用户端

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /api/auth/send-code | 发送验证码 |
| POST | /api/auth/login | 登录/注册 |
| GET | /api/activities | 活动列表 |
| GET | /api/activities/{id} | 活动详情 |
| POST | /api/activities/{id}/submit | 提交活动 |
| GET | /api/mall/products | 商品列表 |
| POST | /api/mall/redeem | 积分兑换 |
| GET | /api/user/profile | 个人信息 |
| GET | /api/user/records | 记录查询 |

### 管理端

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /api/admin/login | 管理员登录 |
| GET/POST | /api/admin/activities | 活动管理 |
| GET | /api/admin/submissions | 审核列表 |
| POST | /api/admin/submissions/{id}/audit | 审核操作 |
| GET/POST | /api/admin/products | 商品管理 |
| GET | /api/admin/orders | 订单列表 |
| POST | /api/admin/orders/{id}/deliver | 订单发货 |

## 注意事项

1. **安全配置**: 生产环境请修改默认密码和 SECRET_KEY
2. **CORS 配置**: 生产环境请配置具体的允许域名
3. **文件上传**: 需要配置腾讯云 COS 才能使用文件上传功能
4. **短信服务**: 开发环境验证码直接返回，生产环境需配置短信服务
