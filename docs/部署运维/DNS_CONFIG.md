# cloudexp.top DNS配置指南

## 📋 当前DNS记录

| 主机记录 | 记录类型 | 记录值 | 说明 |
|---------|---------|--------|------|
| @ | CNAME | gongzhonghao-yunshu-5cre5debcc89-1356235803.tcloudbaseapp.com | 现有记录（公众号相关） |
| _dnsauth | TXT | 202511192044332fvw5wuwoo3hhgnrd87zhk4uur6u63slhvgdaej21hyv0v8e29 | DNS验证记录 |

---

## ⚠️ 需要修改的配置

### 问题：主域名(@)已经是CNAME记录

**当前状态：**
- `@` 记录类型是 CNAME，指向腾讯云CloudBase
- 这会导致无法直接访问 cloudexp.top

**解决方案：**

### 方案1：删除现有CNAME，改为A记录（推荐）

如果不再使用CloudBase服务，建议：

1. **删除现有记录：**
   - 删除 `@` 的 CNAME 记录

2. **添加新的A记录：**

| 主机记录 | 记录类型 | 记录值 | TTL | 说明 |
|---------|---------|--------|-----|------|
| @ | A | 129.211.167.131 | 600 | 主域名 |
| www | A | 129.211.167.131 | 600 | www子域名 |
| api | A | 129.211.167.131 | 600 | API子域名（可选） |
| admin | A | 129.211.167.131 | 600 | 管理后台（可选） |

### 方案2：使用子域名（如果需要保留CloudBase）

如果需要保留现有的CloudBase服务，可以使用子域名：

| 主机记录 | 记录类型 | 记录值 | 说明 |
|---------|---------|--------|------|
| @ | CNAME | gongzhonghao-yunshu-... | 保持不变（CloudBase） |
| points | A | 129.211.167.131 | 积分平台主站 |
| www.points | A | 129.211.167.131 | 积分平台www |

访问地址变为：
- https://points.cloudexp.top
- https://www.points.cloudexp.top

---

## 🚀 推荐配置（方案1）

### 步骤1：删除现有CNAME记录

在腾讯云DNS控制台：
1. 找到 `@` 的 CNAME 记录
2. 点击删除

### 步骤2：添加A记录

添加以下记录：

```
主机记录：@
记录类型：A
记录值：129.211.167.131
TTL：600
```

```
主机记录：www
记录类型：A
记录值：129.211.167.131
TTL：600
```

### 步骤3：验证DNS生效

```bash
# 等待5-10分钟后测试
dig cloudexp.top
dig www.cloudexp.top

# 或使用
nslookup cloudexp.top
nslookup www.cloudexp.top
```

---

## 📝 SSL证书配置注意事项

配置好DNS后，需要等待DNS完全生效（通常10-30分钟），然后才能申请SSL证书。

**验证DNS生效：**
```bash
# 应该返回 129.211.167.131
ping cloudexp.top
ping www.cloudexp.top
```

**DNS生效后，在服务器上运行：**
```bash
sudo ./setup_ssl.sh
```

---

## ⚠️ 重要提醒

1. **删除CNAME前确认：** 确认不再需要CloudBase服务
2. **DNS生效时间：** 修改后需要等待5-30分钟
3. **SSL证书申请：** 必须等DNS完全生效后才能申请
4. **小程序域名：** 小程序配置的域名必须与实际访问域名一致

---

## 🔍 当前需要确认

**请确认以下问题：**

1. ❓ CloudBase服务（gongzhonghao-yunshu）是否还在使用？
   - 如果不用了 → 删除CNAME，改为A记录
   - 如果还在用 → 使用子域名方案

2. ❓ 希望使用哪个域名访问积分平台？
   - cloudexp.top（主域名）→ 需要删除现有CNAME
   - points.cloudexp.top（子域名）→ 保留现有CNAME

**请告诉我您的选择，我会提供具体的配置步骤。**
