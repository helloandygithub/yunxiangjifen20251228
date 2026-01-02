<template>
  <div class="layout">
    <!-- 顶部导航 -->
    <header class="header">
      <div class="container">
        <div class="logo">
          <span class="icon">🎯</span>
          <span class="text">积分活动平台</span>
        </div>
        
        <nav class="nav">
          <router-link to="/home" class="nav-item">首页</router-link>
          <router-link to="/activities" class="nav-item">活动中心</router-link>
          <router-link to="/mall" class="nav-item">积分商城</router-link>
        </nav>
        
        <div class="user-area">
          <template v-if="userStore.isLoggedIn">
            <div class="points">
              <el-icon><Coin /></el-icon>
              <span>{{ userStore.userInfo?.points_balance || 0 }} 积分</span>
            </div>
            <el-dropdown @command="handleCommand">
              <div class="user-info">
                <el-icon><User /></el-icon>
                <span>{{ formatPhone(userStore.userInfo?.phone) }}</span>
              </div>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="user">个人中心</el-dropdown-item>
                  <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
          <el-button v-else type="primary" @click="$router.push('/login')">
            登录
          </el-button>
        </div>
      </div>
    </header>
    
    <!-- 主内容区 -->
    <main class="main">
      <router-view />
    </main>
    
    <!-- 底部 -->
    <footer class="footer">
      <div class="container">
        <p>&copy; 2025 积分活动平台. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessageBox } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()

const formatPhone = (phone) => {
  if (!phone) return ''
  return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
}

const handleCommand = async (command) => {
  if (command === 'user') {
    router.push('/user')
  } else if (command === 'logout') {
    try {
      await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
      userStore.logout()
      router.push('/home')
    } catch {}
  }
}

onMounted(() => {
  if (userStore.isLoggedIn) {
    userStore.fetchUserInfo()
  }
})
</script>

<style lang="scss" scoped>
.layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background: white;
  color: #333;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  position: sticky;
  top: 0;
  z-index: 100;
  border-bottom: 1px solid #f5f5f5;
  
  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 24px;
    height: 64px;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  
  .logo {
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 20px;
    font-weight: 600;
    cursor: pointer;
    color: #F5A623;
    
    .icon {
      font-size: 28px;
      width: 40px;
      height: 40px;
      background: linear-gradient(135deg, #FFB84D 0%, #F5A623 100%);
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
    }
    
    .text {
      color: #333;
    }
  }
  
  .nav {
    display: flex;
    gap: 8px;
    
    .nav-item {
      color: #666;
      text-decoration: none;
      font-size: 16px;
      padding: 10px 20px;
      border-radius: 8px;
      transition: all 0.3s;
      
      &:hover {
        background: #FFF9F0;
        color: #F5A623;
      }
      
      &.router-link-active {
        background: #FFF9F0;
        color: #F5A623;
        font-weight: 500;
      }
    }
  }
  
  .user-area {
    display: flex;
    align-items: center;
    gap: 24px;
    
    .points {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 8px 16px;
      background: #FFF9F0;
      border-radius: 20px;
      font-size: 14px;
      font-weight: 500;
      color: #F5A623;
    }
    
    .user-info {
      display: flex;
      align-items: center;
      gap: 8px;
      cursor: pointer;
      padding: 8px 16px;
      border-radius: 8px;
      transition: all 0.3s;
      color: #666;
      
      &:hover {
        background: #FFF9F0;
        color: #F5A623;
      }
    }
    
    :deep(.el-button--primary) {
      background: #F5A623;
      border-color: #F5A623;
      
      &:hover {
        background: #E09612;
        border-color: #E09612;
      }
    }
  }
}

.main {
  flex: 1;
  background: #f5f5f5;
}

.footer {
  background: white;
  border-top: 1px solid #e5e7eb;
  padding: 24px 0;
  text-align: center;
  color: #6b7280;
  font-size: 14px;
}
</style>
