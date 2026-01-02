# 云享积分平台 - 生产环境部署指南

## 📋 部署前检查清单

### ✅ 已完成
- [x] 腾讯云服务器（129.211.167.131）
- [x] 腾讯云API密钥
- [x] 域名（cloudexp.top）
- [x] 短信服务配置（SDK AppID: 1401045426）
- [x] 短信签名（云抒北京信息技术有限公司）
- [x] 短信模板（ID: 2534800）

### ⏳ 待完成
- [ ] 腾讯云COS存储桶创建
- [ ] 域名DNS解析配置
- [ ] SSL证书申请和配置
- [ ] 微信小程序正式AppID
- [ ] 数据库备份策略

---

## 🚀 部署步骤

### 1. 服务器准备

```bash
# SSH登录服务器
ssh ubuntu@129.211.167.131

# 安装Docker和Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 重新登录使docker组生效
exit
ssh ubuntu@129.211.167.131
```

### 2. 上传代码

```bash
# 在本地执行
# 方式1：使用Git（推荐）
ssh ubuntu@129.211.167.131
git clone <your-repo-url> /home/ubuntu/points-platform
cd /home/ubuntu/points-platform

# 方式2：使用rsync
rsync -avz --exclude 'node_modules' --exclude '.git' \
  /Users/kongkevin/云享积分20251228/ \
  ubuntu@129.211.167.131:/home/ubuntu/points-platform/
```

### 3. 配置环境变量

```bash
# 在服务器上执行
cd /home/ubuntu/points-platform
cp .env.production .env

# 编辑.env文件，补充COS配置
nano .env
```

**需要补充的配置：**
- `COS_BUCKET`: 在腾讯云COS创建存储桶后填写
- `COS_DOMAIN`: COS自定义域名（可选）

### 4. 配置域名解析

在域名服务商（cloudexp.top）添加DNS记录：

| 类型 | 主机记录 | 记录值 | 说明 |
|------|---------|--------|------|
| A | @ | 129.211.167.131 | 主域名 |
| A | www | 129.211.167.131 | www子域名 |
| A | api | 129.211.167.131 | API子域名 |
| A | admin | 129.211.167.131 | 管理后台 |

### 5. 申请SSL证书

```bash
# 安装certbot
sudo apt update
sudo apt install certbot

# 申请证书（需要先停止nginx）
sudo certbot certonly --standalone -d cloudexp.top -d www.cloudexp.top

# 证书位置
# /etc/letsencrypt/live/cloudexp.top/fullchain.pem
# /etc/letsencrypt/live/cloudexp.top/privkey.pem

# 复制证书到项目目录
sudo mkdir -p /home/ubuntu/points-platform/nginx/ssl
sudo cp /etc/letsencrypt/live/cloudexp.top/fullchain.pem /home/ubuntu/points-platform/nginx/ssl/
sudo cp /etc/letsencrypt/live/cloudexp.top/privkey.pem /home/ubuntu/points-platform/nginx/ssl/
sudo chown -R ubuntu:ubuntu /home/ubuntu/points-platform/nginx/ssl
```

### 6. 构建前端应用

```bash
# 构建管理后台
cd /home/ubuntu/points-platform/admin
npm install
npm run build

# 构建用户端PC
cd /home/ubuntu/points-platform/pc-user
npm install
npm run build

# 构建小程序（在本地构建后上传）
# 本地执行：
cd /Users/kongkevin/云享积分20251228/webapp
npm run build:mp-weixin
# 然后使用微信开发者工具上传代码
```

### 7. 启动服务

```bash
cd /home/ubuntu/points-platform

# 使用生产配置启动
docker-compose -f docker-compose.prod.yml up -d

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f

# 检查服务状态
docker-compose -f docker-compose.prod.yml ps
```

### 8. 初始化数据库

```bash
# 数据库会自动执行 backend/init.sql
# 如需手动执行：
docker exec -it points_mysql mysql -u points_user -p points_platform < backend/init.sql
```

### 9. 验证部署

访问以下地址验证：
- 主站：http://cloudexp.top
- 管理后台：http://cloudexp.top/admin
- API文档：http://cloudexp.top/docs
- 健康检查：http://cloudexp.top/health

---

## 🔒 安全配置

### 1. 防火墙配置

```bash
# 配置UFW防火墙
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### 2. 修改SSH端口（可选）

```bash
sudo nano /etc/ssh/sshd_config
# 修改 Port 22 为其他端口，如 2222
sudo systemctl restart sshd
```

### 3. 配置自动备份

```bash
# 创建备份脚本
cat > /home/ubuntu/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/home/ubuntu/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# 备份数据库
docker exec points_mysql mysqldump -u points_user -p${MYSQL_PASSWORD} points_platform > ${BACKUP_DIR}/db_${DATE}.sql

# 备份上传文件
tar -czf ${BACKUP_DIR}/uploads_${DATE}.tar.gz /home/ubuntu/points-platform/uploads

# 删除7天前的备份
find ${BACKUP_DIR} -name "*.sql" -mtime +7 -delete
find ${BACKUP_DIR} -name "*.tar.gz" -mtime +7 -delete
EOF

chmod +x /home/ubuntu/backup.sh

# 添加定时任务（每天凌晨2点备份）
crontab -e
# 添加：0 2 * * * /home/ubuntu/backup.sh
```

---

## 📱 微信小程序配置

### 1. 配置服务器域名

在微信公众平台 → 开发 → 开发管理 → 开发设置 → 服务器域名：

**request合法域名：**
- https://cloudexp.top
- https://api.cloudexp.top

**uploadFile合法域名：**
- https://cloudexp.top

**downloadFile合法域名：**
- https://cloudexp.top

### 2. 更新小程序配置

修改 `webapp/src/utils/request.js`：
```javascript
const BASE_URL = 'https://cloudexp.top/api'
```

### 3. 提交审核

1. 微信开发者工具 → 上传代码
2. 微信公众平台 → 版本管理 → 提交审核
3. 审核通过后 → 发布

---

## 🔧 常用运维命令

```bash
# 查看日志
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f nginx

# 重启服务
docker-compose -f docker-compose.prod.yml restart backend
docker-compose -f docker-compose.prod.yml restart nginx

# 更新代码后重新部署
git pull
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d

# 进入容器
docker exec -it points_backend bash
docker exec -it points_mysql mysql -u points_user -p

# 查看资源使用
docker stats
```

---

## 📊 监控和日志

### 1. 日志位置

- Nginx日志：`/var/log/nginx/`
- Backend日志：`docker logs points_backend`
- MySQL日志：`docker logs points_mysql`

### 2. 性能监控（可选）

推荐工具：
- Grafana + Prometheus（容器监控）
- Sentry（错误追踪）
- 腾讯云监控（服务器监控）

---

## 🆘 故障排查

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
# 检查MySQL容器状态
docker ps | grep mysql

# 进入MySQL容器检查
docker exec -it points_mysql mysql -u root -p
```

### SSL证书过期
```bash
# 续期证书
sudo certbot renew

# 重启nginx
docker-compose -f docker-compose.prod.yml restart nginx
```

---

## 📞 技术支持

如遇问题，请检查：
1. 服务器日志
2. 数据库连接
3. 环境变量配置
4. 防火墙规则
5. 域名解析

---

**部署完成后记得：**
- ✅ 测试所有功能
- ✅ 配置监控告警
- ✅ 设置数据备份
- ✅ 文档归档
