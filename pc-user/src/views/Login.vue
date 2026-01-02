<template>
  <div class="login-page">
    <div class="login-box">
      <div class="logo">
        <span class="icon">🎯</span>
        <h2>积分活动平台</h2>
      </div>
      
      <el-form :model="form" :rules="rules" ref="formRef" label-width="0">
        <el-form-item prop="phone">
          <el-input
            v-model="form.phone"
            placeholder="请输入手机号"
            size="large"
            maxlength="11"
          >
            <template #prefix>
              <el-icon><Phone /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item prop="code">
          <el-input
            v-model="form.code"
            placeholder="请输入验证码"
            size="large"
            maxlength="6"
          >
            <template #prefix>
              <el-icon><Message /></el-icon>
            </template>
            <template #append>
              <el-button
                :disabled="countdown > 0"
                @click="sendCode"
                style="width: 120px;"
              >
                {{ countdown > 0 ? `${countdown}s` : '获取验证码' }}
              </el-button>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item prop="referrerCode">
          <el-input
            v-model="form.referrerCode"
            placeholder="邀请码（选填）"
            size="large"
          >
            <template #prefix>
              <el-icon><Link /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-button
          type="primary"
          size="large"
          :loading="loading"
          @click="handleLogin"
          style="width: 100%;"
        >
          登录 / 注册
        </el-button>
      </el-form>
      
      <p class="agreement">
        登录即表示同意 <a href="#">《用户协议》</a> 和 <a href="#">《隐私政策》</a>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref()
const loading = ref(false)
const countdown = ref(0)

const form = reactive({
  phone: '',
  code: '',
  referrerCode: ''
})

const rules = {
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { min: 4, message: '验证码至少4位', trigger: 'blur' }
  ]
}

const sendCode = async () => {
  if (!/^1[3-9]\d{9}$/.test(form.phone)) {
    ElMessage.error('请输入正确的手机号')
    return
  }
  
  try {
    const res = await request.post('/auth/send-code', { phone: form.phone })
    
    // 开发环境显示验证码
    if (res.data?.code) {
      ElMessage.success(`验证码: ${res.data.code}`)
    } else {
      ElMessage.success('验证码已发送')
    }
    
    countdown.value = 60
    const timer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) {
        clearInterval(timer)
      }
    }, 1000)
  } catch (error) {
    console.error(error)
  }
}

const handleLogin = async () => {
  if (!formRef.value) return
  
  try {
    const valid = await formRef.value.validate()
    if (!valid) return
    
    loading.value = true
    await userStore.login(form.phone, form.code, form.referrerCode)
    ElMessage.success('登录成功')
    router.push('/home')
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #FFF9F0 0%, #FFE4B3 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  position: relative;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: url('data:image/svg+xml,<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg"><circle cx="50" cy="50" r="2" fill="%23F5A623" opacity="0.1"/></svg>');
    background-size: 50px 50px;
  }
}

.login-box {
  width: 100%;
  max-width: 440px;
  background: white;
  border-radius: 24px;
  padding: 48px;
  box-shadow: 0 20px 60px rgba(245, 166, 35, 0.2);
  position: relative;
  z-index: 1;
  
  .logo {
    text-align: center;
    margin-bottom: 40px;
    
    .icon {
      width: 80px;
      height: 80px;
      background: linear-gradient(135deg, #F5A623 0%, #FF8C00 100%);
      border-radius: 20px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 40px;
      margin: 0 auto 20px;
      box-shadow: 0 8px 24px rgba(245, 166, 35, 0.3);
    }
    
    h2 {
      font-size: 28px;
      font-weight: 700;
      color: #333;
      margin-bottom: 8px;
    }
    
    p {
      font-size: 14px;
      color: #999;
    }
  }
  
  :deep(.el-form-item) {
    margin-bottom: 24px;
    
    .el-input__wrapper {
      padding: 12px 16px;
      border-radius: 12px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
      
      &:hover,
      &.is-focus {
        box-shadow: 0 2px 12px rgba(245, 166, 35, 0.2);
      }
    }
    
    .el-input-group__append {
      background: white;
      border: none;
      
      .el-button {
        background: #F5A623;
        border: none;
        color: white;
        font-weight: 500;
        
        &:hover:not(:disabled) {
          background: #E09612;
        }
        
        &:disabled {
          background: #E5E7EB;
          color: #999;
        }
      }
    }
  }
  
  .el-button--primary {
    background: linear-gradient(135deg, #F5A623 0%, #FF8C00 100%);
    border: none;
    padding: 14px;
    font-size: 16px;
    font-weight: 600;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(245, 166, 35, 0.3);
    
    &:hover {
      background: linear-gradient(135deg, #E09612 0%, #E67E00 100%);
      transform: translateY(-2px);
      box-shadow: 0 6px 16px rgba(245, 166, 35, 0.4);
    }
    
    &:active {
      transform: translateY(0);
    }
  }
  
  .agreement {
    text-align: center;
    margin-top: 24px;
    font-size: 12px;
    color: #999;
    line-height: 1.6;
    
    a {
      color: #F5A623;
      text-decoration: none;
      font-weight: 500;
      
      &:hover {
        text-decoration: underline;
      }
    }
  }
}
</style>
