<template>
  <view class="agreement-page">
    <view class="header">
      <text class="title">用户服务协议</text>
    </view>
    
    <scroll-view scroll-y class="content">
      <view class="section">
        <text class="section-title">一、总则</text>
        <text class="section-text">
          欢迎使用云享积分平台（以下简称"本平台"）。在使用本平台服务之前，请您仔细阅读本用户服务协议（以下简称"本协议"）。一旦您开始使用本平台服务，即表示您已充分理解并同意接受本协议的全部内容。
        </text>
      </view>
      
      <view class="section">
        <text class="section-title">二、服务内容</text>
        <text class="section-text">
          本平台为用户提供积分活动参与、积分商城兑换等服务。平台有权根据业务发展需要，随时变更、暂停或终止部分或全部服务。
        </text>
      </view>
      
      <view class="section">
        <text class="section-title">三、用户注册</text>
        <text class="section-text">
          1. 用户需使用真实手机号码进行注册。\n
          2. 用户应妥善保管账号信息，对账号下的所有行为承担责任。\n
          3. 每位用户只能注册一个账号，禁止使用多账号进行恶意刷分等违规行为。
        </text>
      </view>
      
      <view class="section">
        <text class="section-title">四、积分规则</text>
        <text class="section-text">
          1. 积分通过完成平台活动获得，每个活动的积分奖励由平台设定。\n
          2. 积分可用于商城商品兑换，兑换后积分将相应扣除。\n
          3. 平台有权对存在违规行为的账号进行积分扣除或账号封禁处理。
        </text>
      </view>
      
      <view class="section">
        <text class="section-title">五、知识产权</text>
        <text class="section-text">
          本平台的所有内容，包括但不限于文字、图片、软件、代码等，均受知识产权法保护。未经授权，用户不得复制、传播或用于商业用途。
        </text>
      </view>
      
      <view class="section">
        <text class="section-title">六、免责声明</text>
        <text class="section-text">
          1. 因不可抗力导致的服务中断，平台不承担责任。\n
          2. 用户因违规操作导致的损失，由用户自行承担。
        </text>
      </view>
      
      <view class="section">
        <text class="section-title">七、协议修改</text>
        <text class="section-text">
          本平台有权根据法律法规和业务需要修改本协议，修改后的协议将在平台公布。继续使用平台服务即视为同意修改后的协议。
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
