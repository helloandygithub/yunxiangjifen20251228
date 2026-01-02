<template>
  <view class="agreement-page">
    <view class="header">
      <text class="title">隐私政策</text>
    </view>
    
    <scroll-view scroll-y class="content">
      <view class="section">
        <text class="section-title">一、引言</text>
        <text class="section-text">
          云享积分平台（以下简称"我们"）非常重视用户的隐私保护。本隐私政策旨在向您说明我们如何收集、使用、存储和保护您的个人信息。在使用我们的服务前，请仔细阅读本政策。
        </text>
      </view>
      
      <view class="section">
        <text class="section-title">二、我们收集的信息</text>
        <text class="section-text">
          1. 手机号码：用于账户注册和登录验证。\n
          2. 活动提交信息：您在参与活动时主动填写的信息。\n
          3. 设备信息：设备型号、操作系统版本等，用于服务优化。\n
          4. 日志信息：您使用服务时的操作记录，用于问题排查和服务改进。
        </text>
      </view>
      
      <view class="section">
        <text class="section-title">三、信息使用目的</text>
        <text class="section-text">
          1. 提供基本服务：登录验证、积分记录、商品兑换等。\n
          2. 服务优化：分析使用数据，改进产品体验。\n
          3. 安全保障：识别异常行为，保护账户安全。\n
          4. 通知推送：发送活动通知和重要信息（经您同意）。
        </text>
      </view>
      
      <view class="section">
        <text class="section-title">四、信息保护措施</text>
        <text class="section-text">
          1. 我们采用行业标准的加密技术保护您的数据传输。\n
          2. 您的个人信息存储在安全的服务器上，有严格的访问控制。\n
          3. 我们定期审查安全措施，确保数据安全。
        </text>
      </view>
      
      <view class="section">
        <text class="section-title">五、信息共享</text>
        <text class="section-text">
          我们不会将您的个人信息出售给第三方。但以下情况除外：\n
          1. 经您明确同意。\n
          2. 法律法规要求披露。\n
          3. 与合作伙伴共享必要信息以提供服务（如短信服务商发送验证码）。
        </text>
      </view>
      
      <view class="section">
        <text class="section-title">六、您的权利</text>
        <text class="section-text">
          1. 查询和更正：您可以查询和更正您的个人信息。\n
          2. 删除账号：您可以申请注销账号，我们将删除您的个人信息。\n
          3. 撤回同意：您可以随时撤回对信息收集的同意。
        </text>
      </view>
      
      <view class="section">
        <text class="section-title">七、未成年人保护</text>
        <text class="section-text">
          我们的服务主要面向成年人。如果我们发现未经监护人同意收集了未成年人信息，我们将及时删除相关数据。
        </text>
      </view>
      
      <view class="section">
        <text class="section-title">八、隐私政策更新</text>
        <text class="section-text">
          我们可能会不时更新本隐私政策。更新后的政策将在平台公布，继续使用服务即表示您同意更新后的政策。
        </text>
      </view>
      
      <view class="section">
        <text class="section-title">九、联系我们</text>
        <text class="section-text">
          如果您对本隐私政策有任何疑问，请通过平台内的反馈渠道联系我们。
        </text>
      </view>
      
      <view class="footer">
        <text>更新日期：2025年12月31日</text>
      </view>
    </scroll-view>
  </view>
</template>

<script setup>
</script>

<style lang="scss" scoped>
.agreement-page {
  min-height: 100vh;
  background: #FFFFFF;
  display: flex;
  flex-direction: column;
}

.header {
  padding: 32rpx;
  background: linear-gradient(135deg, #FF6B35 0%, #FF8C42 100%);
  
  .title {
    font-size: 36rpx;
    font-weight: bold;
    color: #FFFFFF;
  }
}

.content {
  flex: 1;
  padding: 32rpx;
}

.section {
  margin-bottom: 32rpx;
  
  .section-title {
    display: block;
    font-size: 30rpx;
    font-weight: bold;
    color: #303133;
    margin-bottom: 16rpx;
  }
  
  .section-text {
    display: block;
    font-size: 28rpx;
    color: #606266;
    line-height: 1.8;
    white-space: pre-wrap;
  }
}

.footer {
  padding: 32rpx;
  text-align: center;
  font-size: 24rpx;
  color: #909399;
}
</style>
