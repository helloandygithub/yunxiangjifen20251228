# 云享积分平台 - 最终部署检查清单

**更新时间：** 2025-12-31 19:34

---

## ✅ 已完成（100%就绪）

### 基础设施
- [x] 腾讯云服务器：129.211.167.131
- [x] 域名：cloudexp.top
- [x] 域名备案：已完成（正常）
- [x] DNS配置：A记录已指向服务器
- [x] 腾讯云API密钥：已配置
- [x] 短信服务：完全配置（AppID/签名/模板）

### 开发完成
- [x] 后端API开发
- [x] 管理后台开发
- [x] 用户端PC开发
- [x] 小程序UI更新

### 部署准备
- [x] 生产环境配置文件（.env.production）
- [x] 部署指南文档
- [x] 一键部署脚本
- [x] SSL配置脚本
- [x] COS配置指南

---

## 🚀 立即执行（今晚完成）

### 1. 等待DNS完全生效（10-30分钟）

```bash
# 在本地测试DNS是否生效
dig cloudexp.top
# 应该返回：129.211.167.131

# 或使用
ping cloudexp.top
# 应该能ping通 129.211.167.131
```

**当前状态：** DNS正在传播中，请等待10-30分钟

---

### 2. 创建COS存储桶（5分钟）

访问：https://console.cloud.tencent.com/cos5

**配置参数：**
- **名称**：yunxiang-points
- **地域**：广州（ap-guangzhou）
- **访问权限**：私有读写

**创建后获取：**
- 存储桶名称：yunxiang-points-1356235803
- 访问域名：yunxiang-points-1356235803.cos.ap-guangzhou.myqcloud.com

**更新.env.production：**
```bash
COS_BUCKET=yunxiang-points-1356235803
COS_DOMAIN=yunxiang-points-1356235803.cos.ap-guangzhou.myqcloud.com
```

详细步骤参考：`COS_SETUP_GUIDE.md`

---

### 3. 上传代码到服务器（5分钟）

```bash
# 在本地执行
rsync -avz \
  --exclude 'node_modules' \
  --exclude '.git' \
  --exclude '*.pyc' \
  --exclude '__pycache__' \
  /Users/kongkevin/云享积分20251228/ \
  ubuntu@129.211.167.131:/home/ubuntu/points-platform/
```

**输入密码：** @A12wsxzaq

---

### 4. 服务器初始化（10分钟）

```bash
# SSH登录服务器
ssh ubuntu@129.211.167.131

# 检查Docker是否安装
docker --version
docker-compose --version

# 如果未安装，执行：
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 重新登录使docker组生效
exit
ssh ubuntu@129.211.167.131
```

---

### 5. 部署应用（10分钟）

```bash
# 在服务器上执行
cd /home/ubuntu/points-platform

# 确保.env文件存在
cp .env.production .env

# 编辑.env，更新COS配置（如果已创建）
nano .env

# 给脚本执行权限
chmod +x deploy.sh

# 执行部署
./deploy.sh
```

---

### 6. 申请SSL证书（10分钟）

**前提：** DNS必须完全生效（能ping通cloudexp.top）

```bash
# 在服务器上执行
cd /home/ubuntu/points-platform
sudo chmod +x setup_ssl.sh
sudo ./setup_ssl.sh
```

**如果遇到错误：**
- 检查DNS是否生效：`ping cloudexp.top`
- 检查80端口是否开放：`sudo ufw status`
- 查看详细日志

---

### 7. 验证部署（5分钟）

**访问以下地址测试：**

| 服务 | 地址 | 预期结果 |
|------|------|---------|
| 健康检查 | http://cloudexp.top/health | 返回OK |
| API文档 | http://cloudexp.top/docs | 显示API文档 |
| 管理后台 | http://cloudexp.top/admin | 显示登录页 |
| 用户端 | http://cloudexp.top | 显示首页 |

**HTTPS访问（SSL配置后）：**
- https://cloudexp.top
- https://www.cloudexp.top

---

## 📱 小程序配置（明天执行）

### 1. 配置服务器域名

在微信公众平台 → 开发 → 开发管理 → 开发设置：

**request合法域名：**
```
https://cloudexp.top
```

**uploadFile合法域名：**
```
https://cloudexp.top
```

**downloadFile合法域名：**
```
https://cloudexp.top
```

### 2. 更新小程序API地址

修改 `webapp/src/utils/request.js`：
```javascript
const BASE_URL = 'https://cloudexp.top/api'
```

### 3. 重新构建并上传

```bash
# 在本地执行
cd /Users/kongkevin/云享积分20251228/webapp
npm run build:mp-weixin

# 使用微信开发者工具上传代码
# 版本号：1.0.0
# 版本描述：正式版本
```

### 4. 提交审核

1. 微信公众平台 → 版本管理
2. 提交审核
3. 等待审核通过（1-2天）
4. 发布上线

---

## 🔧 常用命令

### 查看服务状态
```bash
cd /home/ubuntu/points-platform
docker-compose -f docker-compose.prod.yml ps
```

### 查看日志
```bash
# 所有服务
docker-compose -f docker-compose.prod.yml logs -f

# 特定服务
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f nginx
```

### 重启服务
```bash
docker-compose -f docker-compose.prod.yml restart
```

### 停止服务
```bash
docker-compose -f docker-compose.prod.yml down
```

---

## ⚠️ 故障排查

### DNS未生效
```bash
# 检查DNS
dig cloudexp.top
nslookup cloudexp.top

# 等待时间：10-30分钟
```

### SSL证书申请失败
```bash
# 检查80端口
sudo netstat -tulpn | grep :80

# 检查防火墙
sudo ufw status

# 查看certbot日志
sudo tail -f /var/log/letsencrypt/letsencrypt.log
```

### 服务无法启动
```bash
# 查看详细日志
docker-compose -f docker-compose.prod.yml logs

# 检查端口占用
sudo netstat -tulpn | grep :80
sudo netstat -tulpn | grep :3306

# 检查磁盘空间
df -h
```

### 数据库连接失败
```bash
# 进入MySQL容器
docker exec -it points_mysql bash
mysql -u points_user -p

# 检查数据库
show databases;
use points_platform;
show tables;
```

---

## 📊 部署时间线

| 时间 | 任务 | 预计耗时 |
|------|------|---------|
| **今晚** | | |
| 19:30 | 等待DNS生效 | 10-30分钟 |
| 20:00 | 创建COS存储桶 | 5分钟 |
| 20:05 | 上传代码 | 5分钟 |
| 20:10 | 服务器初始化 | 10分钟 |
| 20:20 | 部署应用 | 10分钟 |
| 20:30 | 申请SSL证书 | 10分钟 |
| 20:40 | 验证测试 | 10分钟 |
| **20:50** | **部署完成** | |
| | | |
| **明天** | | |
| 上午 | 配置小程序域名 | 10分钟 |
| 上午 | 更新并上传小程序 | 30分钟 |
| 上午 | 提交审核 | 5分钟 |
| 1-2天后 | 审核通过，发布上线 | - |

---

## ✅ 最终检查

部署完成后，确认以下项目：

- [ ] 网站可以通过 https://cloudexp.top 访问
- [ ] 管理后台可以登录
- [ ] API文档可以访问
- [ ] 用户可以注册登录
- [ ] 短信验证码可以发送
- [ ] 图片可以上传（COS）
- [ ] 所有功能正常
- [ ] SSL证书有效
- [ ] 小程序已提交审核

---

## 📞 支持信息

**服务器信息：**
- IP: 129.211.167.131
- 用户: ubuntu
- 密码: @A12wsxzaq

**域名：** cloudexp.top

**文档位置：**
- 部署指南：`DEPLOYMENT_GUIDE.md`
- 部署状态：`DEPLOYMENT_STATUS.md`
- COS配置：`COS_SETUP_GUIDE.md`
- DNS配置：`DNS_CONFIG.md`

---

## 🎉 预计完成时间

**今晚（2025-12-31）：** 完成服务器部署和SSL配置
**明天（2025-01-01）：** 完成小程序配置和提交审核
**2-3天后：** 小程序审核通过，正式上线

---

**准备好了就开始吧！祝部署顺利！🚀**
