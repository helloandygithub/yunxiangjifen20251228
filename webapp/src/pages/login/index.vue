<template>
  <view class="login-container">
    <!-- Logo和标题 -->
    <view class="header">
      <view class="logo">
        <text class="logo-icon">🎁</text>
      </view>
      <view class="app-name">云享积分</view>
      <view class="app-desc">参与活动，赚取积分</view>
    </view>

    <!-- 三个图标装饰 -->
    <view class="icons-row">
      <view class="icon-item">
        <text>🎁</text>
      </view>
      <view class="icon-item active">
        <text>🎁</text>
      </view>
      <view class="icon-item">
        <text>🛡️</text>
      </view>
    </view>
    <view class="security-text">安全登录，开启积分之旅</view>

    <!-- 微信一键登录 -->
    <view class="form">
      <view class="form-label">邀请码 (选填)</view>
      <view class="input-wrapper">
        <input 
          v-model="form.referrerCode" 
          class="input-field" 
          placeholder="有邀请码请填写"
        />
      </view>

      <!-- 微信手机号快捷登录按钮 -->
      <button 
        class="wx-login-btn"
        open-type="getPhoneNumber"
        @getphonenumber="handleWxLogin"
        :loading="loading"
        :disabled="loading"
      >
        <text class="wx-icon">📱</text>
        <text>{{ loading ? '登录中...' : '微信快捷登录' }}</text>
      </button>

      <!-- 切换到短信验证码登录 -->
      <view class="switch-login" @tap="showSmsLogin = !showSmsLogin">
        <text>{{ showSmsLogin ? '返回微信登录' : '使用短信验证码登录' }}</text>
      </view>

      <!-- 短信验证码登录表单（可选） -->
      <view v-if="showSmsLogin" class="sms-form">
        <view class="form-label">手机号码</view>
        <view class="input-wrapper">
          <text class="country-code">📞 +86</text>
          <input 
            v-model="form.phone" 
            type="number" 
            placeholder="请输入手机号"
            maxlength="11"
            class="input-field"
          />
        </view>

        <view class="form-label">验证码</view>
        <view class="input-wrapper code-wrapper">
          <text class="code-icon">💬</text>
          <input 
            v-model="form.code" 
            type="number" 
            placeholder="请输入验证码"
            maxlength="6"
            class="input-field"
          />
          <button 
            class="code-btn" 
            :disabled="countdown > 0"
            @click="sendCode"
          >
            {{ countdown > 0 ? `${countdown}s` : '获取验证码' }}
          </button>
        </view>

        <view 
          :class="['btn', 'btn-primary', 'login-btn', { 'btn-disabled': !canLogin || loading }]"
          @tap="handleSmsLogin"
        >
          <text>{{ loading ? '登录中...' : '登录 / 注册' }}</text>
        </view>
      </view>

      <view class="agreement">
        <text>登录即表示同意</text>
        <text class="link">《用户协议》</text>
        <text>和</text>
        <text class="link">《隐私政策》</text>
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
const showSmsLogin = ref(false)
let timer = null

const form = reactive({
  phone: '',
  code: '',
  referrerCode: ''
})

const isPhoneValid = computed(() => /^1[3-9]\d{9}$/.test(form.phone))
const canLogin = computed(() => isPhoneValid.value && form.code.length >= 4)

// 微信一键登录
const handleWxLogin = async (e) => {
  if (e.detail.errMsg !== 'getPhoneNumber:ok') {
    uni.showToast({ title: '需要授权手机号才能登录', icon: 'none' })
    return
  }

  loading.value = true
  try {
    // 调用后端微信登录接口
    const res = await post('/auth/wx-login', {
      code: e.detail.code,
      referrer_code: form.referrerCode || undefined
    })

    if (res.data?.access_token) {
      // 保存token和用户信息
      uni.setStorageSync('token', res.data.access_token)
      userStore.setUser(res.data.user)
      
      uni.showToast({ title: '登录成功', icon: 'success' })
      
      setTimeout(() => {
        uni.switchTab({ url: '/pages/index/index' })
      }, 1000)
    }
  } catch (error) {
    console.error('微信登录失败:', error)
    uni.showToast({ 
      title: error.message || '登录失败，请重试', 
      icon: 'none' 
    })
  } finally {
    loading.value = false
  }
}

// 发送短信验证码
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

// 短信验证码登录
const handleSmsLogin = async () => {
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
</script>

<style lang="scss" scoped>
.login-container {
  min-height: 100vh;
  background: #F5F5F5;
  padding: 80rpx 48rpx 48rpx;
  display: flex;
  flex-direction: column;
}

// Logo和标题区域
.header {
  text-align: center;
  margin-bottom: 60rpx;
  
  .logo {
    width: 120rpx;
    height: 120rpx;
    background: linear-gradient(135deg, #FF6B35 0%, #FF8C42 100%);
    border-radius: 32rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 24rpx;
    box-shadow: 0 8rpx 24rpx rgba(255, 107, 53, 0.3);
    
    .logo-icon {
      font-size: 64rpx;
    }
  }
  
  .app-name {
    font-size: 48rpx;
    font-weight: bold;
    color: #303133;
    margin-bottom: 12rpx;
  }
  
  .app-desc {
    font-size: 28rpx;
    color: #909399;
  }
}

// 三个图标装饰
.icons-row {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 48rpx;
  margin-bottom: 16rpx;
  
  .icon-item {
    width: 96rpx;
    height: 96rpx;
    background: #FFF5F0;
    border-radius: 24rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 48rpx;
    transition: all 0.3s;
    
    &.active {
      background: linear-gradient(135deg, #FF6B35 0%, #FF8C42 100%);
      transform: scale(1.1);
      box-shadow: 0 8rpx 24rpx rgba(255, 107, 53, 0.3);
    }
  }
}

.security-text {
  text-align: center;
  font-size: 26rpx;
  color: #606266;
  margin-bottom: 48rpx;
}

// 表单区域
.form {
  flex: 1;
  
  .form-label {
    font-size: 28rpx;
    color: #303133;
    font-weight: 500;
    margin-bottom: 16rpx;
  }
  
  .input-wrapper {
    display: flex;
    align-items: center;
    background: #FFFFFF;
    border-radius: 16rpx;
    padding: 0 24rpx;
    margin-bottom: 32rpx;
    height: 96rpx;
    box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.05);
    
    .country-code,
    .code-icon {
      font-size: 32rpx;
      margin-right: 16rpx;
      flex-shrink: 0;
    }
    
    .input-field {
      flex: 1;
      height: 96rpx;
      font-size: 30rpx;
      border: none;
    }
    
    &.code-wrapper {
      padding-right: 0;
    }
    
    .code-btn {
      height: 96rpx;
      padding: 0 24rpx;
      background: linear-gradient(135deg, #FF6B35 0%, #FF8C42 100%);
      color: #FFFFFF;
      font-size: 26rpx;
      border-radius: 0 16rpx 16rpx 0;
      border: none;
      white-space: nowrap;
      
      &:disabled {
        background: #E4E7ED;
        color: #909399;
      }
    }
  }
  
  .login-btn {
    width: 100%;
    height: 96rpx;
    background: #C0C4CC;
    color: #FFFFFF;
    font-size: 32rpx;
    font-weight: 500;
    border-radius: 48rpx;
    margin-top: 48rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    border: none;
    
    &:not(.btn-disabled) {
      background: linear-gradient(135deg, #FF6B35 0%, #FF8C42 100%);
      box-shadow: 0 8rpx 24rpx rgba(255, 107, 53, 0.3);
    }
  }
  
  // 微信登录按钮
  .wx-login-btn {
    width: 100%;
    height: 96rpx;
    background: linear-gradient(135deg, #07C160 0%, #06AD56 100%);
    color: #FFFFFF;
    font-size: 32rpx;
    font-weight: 500;
    border-radius: 48rpx;
    margin-top: 32rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    border: none;
    box-shadow: 0 8rpx 24rpx rgba(7, 193, 96, 0.3);
    
    .wx-icon {
      margin-right: 12rpx;
      font-size: 36rpx;
    }
    
    &[disabled] {
      background: #C0C4CC;
      box-shadow: none;
    }
  }
  
  // 切换登录方式
  .switch-login {
    text-align: center;
    margin-top: 32rpx;
    font-size: 26rpx;
    color: #909399;
    
    text {
      color: #FF6B35;
    }
  }
  
  // 短信登录表单
  .sms-form {
    margin-top: 32rpx;
    padding-top: 32rpx;
    border-top: 1rpx solid #EBEEF5;
  }
  
  .agreement {
    margin-top: 32rpx;
    
    .agreement-label {
      display: flex;
      align-items: flex-start;
      font-size: 24rpx;
      color: #606266;
      
      checkbox {
        margin-right: 12rpx;
        flex-shrink: 0;
      }
      
      .agreement-text {
        flex: 1;
        line-height: 1.6;
        
        .link {
          color: #FF6B35;
        }
      }
    }
  }
}

// 底部安全提示
.footer {
  text-align: center;
  padding: 32rpx 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  
  .security-icon {
    font-size: 28rpx;
  }
  
  .footer-text {
    font-size: 24rpx;
    color: #909399;
  }
}
</style>
