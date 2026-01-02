<template>
  <view class="login-page">
    <!-- 顶部渐变背景 -->
    <view class="header-bg">
      <!-- Logo -->
      <view class="logo-box">
        <text class="logo-icon">🎁</text>
      </view>
      
      <!-- 标题 -->
      <view class="title">云享积分</view>
      <view class="subtitle">
        <text class="subtitle-icon">✨</text>
        <view class="subtitle-text">
          <text class="main-text">积分兑换</text>
          <text class="sub-text">好礼等你拿</text>
        </view>
      </view>
    </view>
    
    <!-- 登录表单卡片 -->
    <view class="form-card">
      <view class="card-title">欢迎登录</view>
      
      <!-- 邀请码（可选） -->
      <view v-if="showReferrer" class="form-group">
        <view class="form-label">邀请码 (选填)</view>
        <view class="input-box">
          <text class="input-icon">🎫</text>
          <input 
            v-model="form.referrerCode" 
            class="input-field" 
            placeholder="有邀请码请填写"
          />
        </view>
      </view>
      
      <!-- 手机号码 -->
      <view class="form-group">
        <view class="form-label">手机号码</view>
        <view class="input-box">
          <text class="input-icon">📞</text>
          <text class="country-code">+86</text>
          <view class="divider"></view>
          <input 
            v-model="form.phone" 
            type="number" 
            class="input-field" 
            placeholder="请输入手机号"
            maxlength="11"
          />
        </view>
      </view>
      
      <!-- 验证码 -->
      <view class="form-group">
        <view class="form-label">验证码</view>
        <view class="input-box code-box">
          <text class="input-icon">💬</text>
          <input 
            v-model="form.code" 
            type="number" 
            class="input-field" 
            placeholder="6位验证码"
            maxlength="6"
          />
          <button 
            class="code-btn" 
            :disabled="countdown > 0 || !isPhoneValid"
            @click="sendCode"
          >
            {{ countdown > 0 ? `${countdown}s` : '获取验证码' }}
          </button>
        </view>
      </view>
      
      <!-- 登录按钮 -->
      <button 
        class="login-btn"
        :class="{ 'disabled': !canLogin || loading }"
        @click="handleLogin"
        :loading="loading"
      >
        <text class="btn-icon">✨</text>
        <text>{{ loading ? '登录中...' : '立即登录' }}</text>
      </button>
      
      <!-- 协议勾选 -->
      <view class="agreement">
        <checkbox-group @change="onAgreementChange">
          <label class="agreement-label">
            <checkbox :checked="agreed" color="#FF6B35" />
            <text class="agreement-text">
              我已阅读并同意
              <text class="link" @tap.stop="openUserAgreement">《用户协议》</text>
              和
              <text class="link" @tap.stop="openPrivacyPolicy">《隐私政策》</text>
            </text>
          </label>
        </checkbox-group>
      </view>
      
      <!-- 安全提示 -->
      <view class="security-tip">
        <text class="security-icon">🔒</text>
        <text>安全加密 · 信息保护</text>
      </view>
    </view>
    
    <!-- 暂不登录 -->
    <view class="skip-login" @tap="skipLogin">
      <text>暂不登录，随便看看</text>
    </view>
    
    <!-- 底部特性 -->
    <view class="features">
      <view class="feature-item">
        <view class="feature-icon">🎯</view>
        <text class="feature-text">简单易用</text>
      </view>
      <view class="feature-item">
        <view class="feature-icon">🎁</view>
        <text class="feature-text">丰富奖励</text>
      </view>
      <view class="feature-item">
        <view class="feature-icon">🔐</view>
        <text class="feature-text">安全可靠</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useUserStore } from '@/stores/user'
import { post } from '@/utils/request'

const userStore = useUserStore()

const loading = ref(false)
const countdown = ref(0)
const agreed = ref(false)
const showReferrer = ref(false)
let timer = null

const form = reactive({
  phone: '',
  code: '',
  referrerCode: ''
})

const isPhoneValid = computed(() => /^1[3-9]\d{9}$/.test(form.phone))
const canLogin = computed(() => isPhoneValid.value && form.code.length >= 4 && agreed.value)

// 发送验证码
const sendCode = async () => {
  if (countdown.value > 0 || !isPhoneValid.value) return

  try {
    const res = await post('/auth/send-code', { phone: form.phone })
    
    // 开发环境显示验证码
    if (res.data?.code) {
      uni.showModal({
        title: '开发模式',
        content: `验证码: ${res.data.code}`,
        showCancel: false
      })
    }

    countdown.value = 60
    timer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) {
        clearInterval(timer)
      }
    }, 1000)

    uni.showToast({ title: '验证码已发送', icon: 'success' })
  } catch (error) {
    console.error(error)
  }
}

// 登录
const handleLogin = async () => {
  if (!agreed.value) {
    uni.showToast({ title: '请先阅读并同意用户协议和隐私政策', icon: 'none' })
    return
  }
  if (!canLogin.value || loading.value) return

  loading.value = true
  try {
    await userStore.login(form.phone, form.code, form.referrerCode)
    
    uni.showToast({ title: '登录成功', icon: 'success' })
    
    setTimeout(() => {
      uni.switchTab({ url: '/pages/index/index' })
    }, 1000)
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 协议勾选变化
const onAgreementChange = (e) => {
  agreed.value = e.detail.value.length > 0
}

// 暂不登录
const skipLogin = () => {
  uni.switchTab({ url: '/pages/index/index' })
}

// 打开用户协议
const openUserAgreement = () => {
  uni.navigateTo({ url: '/pages/agreement/user' })
}

// 打开隐私政策
const openPrivacyPolicy = () => {
  uni.navigateTo({ url: '/pages/agreement/privacy' })
}
</script>

<style lang="scss" scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #FF8C42 0%, #FF6B35 30%, #F5F5F5 30%);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-bottom: 40rpx;
}

// 顶部背景区域
.header-bg {
  width: 100%;
  padding: 80rpx 0 120rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.logo-box {
  width: 120rpx;
  height: 120rpx;
  background: #FFFFFF;
  border-radius: 32rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.1);
  margin-bottom: 24rpx;
  
  .logo-icon {
    font-size: 64rpx;
  }
}

.title {
  font-size: 48rpx;
  font-weight: bold;
  color: #FFFFFF;
  margin-bottom: 16rpx;
}

.subtitle {
  display: flex;
  align-items: center;
  gap: 12rpx;
  
  .subtitle-icon {
    font-size: 32rpx;
  }
  
  .subtitle-text {
    display: flex;
    flex-direction: column;
    
    .main-text {
      font-size: 28rpx;
      color: #FFFFFF;
      font-weight: 500;
    }
    
    .sub-text {
      font-size: 24rpx;
      color: rgba(255, 255, 255, 0.9);
    }
  }
}

// 表单卡片
.form-card {
  width: calc(100% - 64rpx);
  background: #FFFFFF;
  border-radius: 32rpx;
  padding: 48rpx 40rpx;
  margin-top: -60rpx;
  box-shadow: 0 8rpx 40rpx rgba(0, 0, 0, 0.08);
}

.card-title {
  font-size: 36rpx;
  font-weight: bold;
  color: #303133;
  text-align: center;
  margin-bottom: 40rpx;
}

.form-group {
  margin-bottom: 32rpx;
}

.form-label {
  font-size: 28rpx;
  color: #303133;
  font-weight: 500;
  margin-bottom: 16rpx;
}

.input-box {
  display: flex;
  align-items: center;
  background: #F8F9FA;
  border-radius: 16rpx;
  padding: 0 24rpx;
  height: 96rpx;
  border: 2rpx solid transparent;
  transition: all 0.3s;
  
  &:focus-within {
    border-color: #FF6B35;
    background: #FFFFFF;
  }
  
  .input-icon {
    font-size: 32rpx;
    margin-right: 16rpx;
    flex-shrink: 0;
  }
  
  .country-code {
    font-size: 30rpx;
    color: #303133;
    font-weight: 500;
  }
  
  .divider {
    width: 2rpx;
    height: 32rpx;
    background: #DCDFE6;
    margin: 0 20rpx;
  }
  
  .input-field {
    flex: 1;
    height: 96rpx;
    font-size: 30rpx;
    border: none;
    background: transparent;
  }
  
  &.code-box {
    padding-right: 0;
  }
  
  .code-btn {
    height: 96rpx;
    padding: 0 28rpx;
    background: transparent;
    color: #FF6B35;
    font-size: 26rpx;
    font-weight: 500;
    border: none;
    white-space: nowrap;
    
    &:disabled {
      color: #C0C4CC;
    }
    
    &::after {
      border: none;
    }
  }
}

// 登录按钮
.login-btn {
  width: 100%;
  height: 96rpx;
  background: linear-gradient(135deg, #FF6B35 0%, #FF8C42 100%);
  color: #FFFFFF;
  font-size: 32rpx;
  font-weight: 500;
  border-radius: 48rpx;
  margin-top: 48rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  box-shadow: 0 8rpx 24rpx rgba(255, 107, 53, 0.3);
  
  .btn-icon {
    margin-right: 12rpx;
    font-size: 28rpx;
  }
  
  &.disabled {
    background: #E4E7ED;
    color: #909399;
    box-shadow: none;
  }
  
  &::after {
    border: none;
  }
}

// 协议
.agreement {
  margin-top: 32rpx;
  display: flex;
  justify-content: center;
  
  .agreement-label {
    display: flex;
    align-items: center;
    font-size: 24rpx;
    color: #606266;
    
    checkbox {
      transform: scale(0.75);
      margin-right: 8rpx;
    }
    
    .agreement-text {
      line-height: 1.6;
      
      .link {
        color: #FF6B35;
      }
    }
  }
}

// 安全提示
.security-tip {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 24rpx;
  font-size: 24rpx;
  color: #909399;
  
  .security-icon {
    margin-right: 8rpx;
    font-size: 24rpx;
  }
}

// 暂不登录
.skip-login {
  margin-top: 32rpx;
  font-size: 28rpx;
  color: #909399;
  
  text {
    text-decoration: underline;
  }
}

// 底部特性
.features {
  display: flex;
  justify-content: center;
  gap: 80rpx;
  margin-top: auto;
  padding-top: 60rpx;
}

.feature-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12rpx;
  
  .feature-icon {
    width: 80rpx;
    height: 80rpx;
    background: #FFF5F0;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 40rpx;
  }
  
  .feature-text {
    font-size: 24rpx;
    color: #606266;
  }
}
</style>
