#!/bin/bash
# SSL证书申请和配置脚本

set -e

echo "============================================"
echo "SSL证书申请和配置"
echo "============================================"
echo ""

DOMAIN="cloudexp.top"
EMAIL="admin@cloudexp.top"  # 请修改为实际邮箱

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then 
    echo "请使用 sudo 运行此脚本"
    exit 1
fi

# 安装certbot
echo "[1/5] 安装certbot..."
apt update
apt install -y certbot
echo "✓ certbot安装完成"
echo ""

# 停止nginx（如果正在运行）
echo "[2/5] 停止nginx..."
docker-compose -f docker-compose.prod.yml stop nginx || true
echo "✓ nginx已停止"
echo ""

# 申请证书
echo "[3/5] 申请SSL证书..."
certbot certonly --standalone \
    -d ${DOMAIN} \
    -d www.${DOMAIN} \
    --email ${EMAIL} \
    --agree-tos \
    --non-interactive

echo "✓ SSL证书申请成功"
echo ""

# 复制证书到项目目录
echo "[4/5] 复制证书..."
mkdir -p nginx/ssl
cp /etc/letsencrypt/live/${DOMAIN}/fullchain.pem nginx/ssl/
cp /etc/letsencrypt/live/${DOMAIN}/privkey.pem nginx/ssl/
chown -R $(whoami):$(whoami) nginx/ssl
echo "✓ 证书复制完成"
echo ""

# 更新nginx配置启用HTTPS
echo "[5/5] 更新nginx配置..."
cat > nginx/nginx.conf << 'NGINX_EOF'
worker_processes auto;

events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    sendfile        on;
    keepalive_timeout  65;
    client_max_body_size 20M;

    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;

    # 后端 API
    upstream backend {
        server backend:8000;
    }

    # HTTP重定向到HTTPS
    server {
        listen 80;
        server_name cloudexp.top www.cloudexp.top;
        return 301 https://$server_name$request_uri;
    }

    # HTTPS配置
    server {
        listen 443 ssl http2;
        server_name cloudexp.top www.cloudexp.top;

        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;

        # 用户端 H5
        location / {
            root /usr/share/nginx/html/webapp;
            index index.html;
            try_files $uri $uri/ /index.html;
        }

        # 管理后台
        location /admin {
            alias /usr/share/nginx/html/admin;
            index index.html;
            try_files $uri $uri/ /admin/index.html;
        }

        # API 代理
        location /api {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_connect_timeout 60s;
            proxy_read_timeout 60s;
        }

        # API 文档
        location /docs {
            proxy_pass http://backend/docs;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        location /openapi.json {
            proxy_pass http://backend/openapi.json;
        }

        # 健康检查
        location /health {
            proxy_pass http://backend/health;
        }
    }
}
NGINX_EOF

echo "✓ nginx配置已更新"
echo ""

# 重启nginx
echo "重启nginx..."
docker-compose -f docker-compose.prod.yml up -d nginx
echo "✓ nginx已重启"
echo ""

echo "============================================"
echo "SSL证书配置完成！"
echo "============================================"
echo ""
echo "证书位置："
echo "  - /etc/letsencrypt/live/${DOMAIN}/fullchain.pem"
echo "  - /etc/letsencrypt/live/${DOMAIN}/privkey.pem"
echo ""
echo "访问地址："
echo "  - https://cloudexp.top"
echo "  - https://www.cloudexp.top"
echo ""
echo "证书有效期：90天"
echo "自动续期命令："
echo "  sudo certbot renew"
echo ""
echo "建议添加定时任务自动续期："
echo "  sudo crontab -e"
echo "  添加：0 3 1 * * certbot renew --quiet && docker-compose -f /home/ubuntu/points-platform/docker-compose.prod.yml restart nginx"
echo ""
