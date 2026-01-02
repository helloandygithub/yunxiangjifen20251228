#!/bin/bash
# 添加SSH公钥到服务器

echo "=========================================="
echo "配置SSH密钥到服务器"
echo "=========================================="
echo ""
echo "请输入服务器密码: @A12wsxzaq"
echo ""

# 读取公钥
PUBLIC_KEY=$(cat ~/.ssh/cloudexp_rsa.pub)

# 通过SSH添加公钥到服务器
ssh ubuntu@129.211.167.131 << EOF
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo '${PUBLIC_KEY}' >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
echo "SSH密钥已添加成功！"
exit
EOF

echo ""
echo "=========================================="
echo "配置完成！"
echo "=========================================="
echo ""
echo "现在可以使用密钥登录："
echo "  ssh cloudexp"
echo ""
echo "或者："
echo "  ssh -i ~/.ssh/cloudexp_rsa ubuntu@129.211.167.131"
echo ""
