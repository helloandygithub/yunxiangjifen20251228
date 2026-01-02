# SSL证书配置指南

**更新时间：** 2025-12-31

---

## 📥 步骤1：下载腾讯云SSL证书

### 1.1 在腾讯云控制台下载证书

**选择格式：** `Nginx（适用大部分场景）（pem文件、crt文件、key文件）`

下载后得到压缩包，解压后包含：
- `cloudexp.top.pem` 或 `cloudexp.top_bundle.crt`
- `cloudexp.top.key`

---

## 📂 步骤2：准备证书文件

### 2.1 创建本地ssl目录

```bash
cd /Users/kongkevin/云享积分20251228
mkdir -p nginx/ssl
```

### 2.2 复制证书文件

```bash
# 假设证书解压在Downloads目录
# 复制证书文件（.pem 或 _bundle.crt）
cp ~/Downloads/cloudexp.top_nginx/cloudexp.top.pem \
   nginx/ssl/fullchain.pem

# 或者如果是 .crt 格式
cp ~/Downloads/cloudexp.top_nginx/cloudexp.top_bundle.crt \
   nginx/ssl/fullchain.pem

# 复制私钥文件
cp ~/Downloads/cloudexp.top_nginx/cloudexp.top.key \
   nginx/ssl/privkey.pem
```

### 2.3 验证文件

```bash
ls -lh nginx/ssl/
# 应该看到：
# fullchain.pem
# privkey.pem
```

---

## 🚀 步骤3：上传代码到服务器

### 3.1 上传所有文件（包括证书）

```bash
rsync -avz \
  --exclude 'node_modules' \
  --exclude '.git' \
  --exclude '*.pyc' \
  --exclude '__pycache__' \
  --exclude 'dist' \
  --exclude '.DS_Store' \
  /Users/kongkevin/云享积分20251228/ \
  ubuntu@129.211.167.131:/home/ubuntu/points-platform/
```

**密码：** @A12wsxzaq

---

## 🔧 步骤4：服务器部署

### 4.1 SSH登录服务器

```bash
ssh ubuntu@129.211.167.131
```

### 4.2 检查文件

```bash
cd /home/ubuntu/points-platform
ls -lh nginx/ssl/
# 确认证书文件已上传
```

### 4.3 使用生产环境nginx配置

```bash
# 备份原配置
cp nginx/nginx.conf nginx/nginx.conf.bak

# 使用生产配置
cp nginx/nginx.prod.conf nginx/nginx.conf
```

### 4.4 检查Docker环境

```bash
# 检查Docker
docker --version

# 检查Docker Compose
docker-compose --version

# 如果未安装，执行：
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 重新登录
exit
ssh ubuntu@129.211.167.131
```

### 4.5 部署应用

```bash
cd /home/ubuntu/points-platform

# 确保.env文件存在
cp .env.production .env

# 给脚本执行权限
chmod +x deploy.sh

# 执行部署
./deploy.sh
```

---

## ✅ 步骤5：验证部署

### 5.1 检查服务状态

```bash
cd /home/ubuntu/points-platform
docker-compose -f docker-compose.prod.yml ps
```

应该看到所有服务都是 `Up` 状态：
- points_mysql
- points_redis
- points_backend
- points_nginx

### 5.2 查看日志

```bash
# 查看所有日志
docker-compose -f docker-compose.prod.yml logs -f

# 或查看特定服务
docker-compose -f docker-compose.prod.yml logs -f nginx
docker-compose -f docker-compose.prod.yml logs -f backend
```

### 5.3 测试HTTPS访问

```bash
# 在服务器上测试
curl https://cloudexp.top/health

# 应该返回成功响应
```

### 5.4 在本地浏览器测试

访问以下地址：
- https://cloudexp.top/health （健康检查）
- https://cloudexp.top/docs （API文档）
- https://cloudexp.top/admin （管理后台）
- https://cloudexp.top （用户端）

---

## 🔍 故障排查

### 问题1：证书文件不存在

**错误信息：**
```
nginx: [emerg] cannot load certificate "/etc/nginx/ssl/fullchain.pem"
```

**解决方法：**
```bash
# 检查证书文件
ls -lh /home/ubuntu/points-platform/nginx/ssl/

# 如果文件不存在，重新上传
```

### 问题2：端口被占用

**错误信息：**
```
Error starting userland proxy: listen tcp4 0.0.0.0:80: bind: address already in use
```

**解决方法：**
```bash
# 查看占用80端口的进程
sudo netstat -tulpn | grep :80

# 停止占用的进程
sudo kill -9 <PID>

# 或者停止nginx
sudo systemctl stop nginx
```

### 问题3：Docker权限问题

**错误信息：**
```
permission denied while trying to connect to the Docker daemon socket
```

**解决方法：**
```bash
# 添加用户到docker组
sudo usermod -aG docker ubuntu

# 重新登录
exit
ssh ubuntu@129.211.167.131
```

### 问题4：SSL证书错误

**浏览器提示：** "您的连接不是私密连接"

**可能原因：**
1. 证书文件路径错误
2. 证书文件权限问题
3. 域名不匹配

**解决方法：**
```bash
# 检查证书内容
openssl x509 -in nginx/ssl/fullchain.pem -text -noout

# 检查证书域名
openssl x509 -in nginx/ssl/fullchain.pem -noout -subject

# 检查文件权限
chmod 644 nginx/ssl/fullchain.pem
chmod 600 nginx/ssl/privkey.pem
```

---

## 📊 部署完成检查清单

- [ ] 证书文件已下载并复制到 nginx/ssl/
- [ ] 代码已上传到服务器
- [ ] Docker和Docker Compose已安装
- [ ] .env文件已配置
- [ ] deploy.sh已执行成功
- [ ] 所有Docker容器运行正常
- [ ] HTTPS可以正常访问
- [ ] API健康检查通过
- [ ] 管理后台可以访问
- [ ] 用户端可以访问

---

## 🎯 下一步

部署完成后：

1. **配置微信小程序服务器域名**
   - 访问微信公众平台
   - 配置 https://cloudexp.top

2. **构建并上传小程序**
   ```bash
   cd /Users/kongkevin/云享积分20251228/webapp
   npm run build:mp-weixin
   ```

3. **提交审核**
   - 使用微信开发者工具上传
   - 在微信公众平台提交审核

---

## 📞 常用命令

```bash
# 查看服务状态
docker-compose -f docker-compose.prod.yml ps

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f

# 重启服务
docker-compose -f docker-compose.prod.yml restart

# 停止服务
docker-compose -f docker-compose.prod.yml down

# 重新部署
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d
```

---

**准备好了就开始吧！🚀**
