<template>
  <view class="page-user">
    <!-- 顶部橙色区域 -->
    <view class="header">
      <view class="header-bg"></view>
      <view class="header-content safe-area-top">
        <!-- 用户信息卡片 -->
        <view class="user-card" @tap="handleUserCardClick">
          <view class="avatar">
            <text>👤</text>
          </view>
          <view class="user-info">
            <text class="username">{{ userStore.isLoggedIn ? (userStore.userInfo?.phone ? '用户' + userStore.userInfo.phone.slice(-4) : '用户') : '未登录' }}</text>
            <text class="phone">{{ userStore.isLoggedIn ? formatPhone(userStore.userInfo?.phone) : '点击登录' }}</text>
          </view>
        </view>
        
        <!-- 邀请码 -->
        <view class="invite-card">
          <view class="invite-left">
            <text class="invite-label">我的邀请码</text>
            <text class="invite-code">{{ userStore.userInfo?.invite_code || '-' }}</text>
          </view>
          <view class="invite-btn" @tap="copyInviteCode">
            <text class="btn-icon">📋</text>
            <text>复制</text>
          </view>
        </view>
      </view>
    </view>
    
    <!-- 积分统计卡片 -->
    <view class="stats-card">
      <view class="stats-main">
        <text class="stats-label">我的积分</text>
        <view class="stats-points">
          <text class="points-icon">💰</text>
          <text class="points-value">{{ formatNumber(userStore.userInfo?.points_balance || 0) }}</text>
        </view>
      </view>
      <view class="stats-row">
        <view class="stat-item" @tap="goToRecords('orders')">
          <text class="stat-value">{{ stats.orders }}</text>
          <text class="stat-label">订单数量</text>
        </view>
        <view class="stat-item" @tap="goToRecords('submissions')">
          <text class="stat-value">{{ stats.submissions }}</text>
          <text class="stat-label">活动提交</text>
        </view>
        <view class="stat-item" @tap="shareInvite">
          <text class="stat-value">{{ stats.invites }}</text>
          <text class="stat-label">邀请人数</text>
        </view>
      </view>
    </view>

    <!-- 功能菜单 -->
    <view class="menu-list">
      <view class="menu-item" @tap="goToRecords('points')">
        <view class="menu-icon icon-points">
          <text>💰</text>
        </view>
        <text class="menu-text">积分明细</text>
        <text class="menu-arrow">›</text>
      </view>
      <view class="menu-item" @tap="goToRecords('orders')">
        <view class="menu-icon icon-orders">
          <text>📦</text>
        </view>
        <text class="menu-text">我的订单</text>
        <text class="menu-arrow">›</text>
      </view>
      <view class="menu-item" @tap="goToRecords('submissions')">
        <view class="menu-icon icon-submissions">
          <text>📋</text>
        </view>
        <text class="menu-text">活动提交</text>
        <text class="menu-arrow">›</text>
      </view>
      <view class="menu-item" @tap="shareInvite">
        <view class="menu-icon icon-invite">
          <text>👥</text>
        </view>
        <text class="menu-text">邀请记录</text>
        <text class="menu-arrow">›</text>
      </view>
    </view>

    <!-- 退出登录 -->
    <!-- 退出登录 -->
    <view v-if="userStore.isLoggedIn">
      <view class="logout-btn" @tap="handleLogout">
        <text>退出登录</text>
      </view>
      
      <view class="delete-account" @tap="handleDeleteAccount">
        <text>注销账号</text>
      </view>
    </view>
  </view>
</template>



<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { get } from '@/utils/request'

const userStore = useUserStore()

const stats = reactive({
  orders: 0,
  submissions: 0,
  invites: 0
})

const formatPhone = (phone) => {
  if (!phone) return '未登录'
  return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
}

const formatNumber = (num) => {
  return num?.toLocaleString() || '0'
}

const fetchStats = async () => {
  if (!userStore.isLoggedIn) return
  try {
    const res = await get('/user/records')
    stats.orders = res.data?.orders?.items?.length || 0
    stats.submissions = res.data?.submissions?.items?.length || 0
    stats.invites = 0
  } catch (error) {
    console.error(error)
  }
}

const copyInviteCode = () => {
  if (!userStore.isLoggedIn) {
    uni.navigateTo({ url: '/pages/login/index' })
    return
  }
  if (!userStore.userInfo?.invite_code) return
  
  uni.setClipboardData({
    data: userStore.userInfo.invite_code,
    success: () => {
      uni.showToast({
        title: '邀请码已复制',
        icon: 'success'
      })
    }
  })
}

const handleUserCardClick = () => {
  if (!userStore.isLoggedIn) {
    uni.navigateTo({ url: '/pages/login/index' })
  }
}

const goToRecords = (type) => {
  uni.navigateTo({
    url: `/pages/user/records?type=${type}`
  })
}

const shareInvite = () => {
  if (!userStore.userInfo?.invite_code) return
  
  uni.showModal({
    title: '邀请好友',
    content: `我的邀请码: ${userStore.userInfo.invite_code}\n\n分享给好友，好友注册时填写即可`,
    showCancel: false
  })
}

const handleLogout = async () => {
  try {
    await uni.showModal({
      title: '提示',
      content: '确定要退出登录吗？',
      confirmColor: '#FF6B35'
    })
    
    userStore.logout()
    uni.reLaunch({ url: '/pages/login/index' })
  } catch {
    // 取消
  }
}

const handleDeleteAccount = async () => {
  try {
    await uni.showModal({
      title: '警告',
      content: '注销账号将永久删除您的所有数据，且无法恢复。确定继续吗？',
      confirmText: '确认注销',
      confirmColor: '#F56C6C',
      cancelText: '取消'
    })
    
    // 这里应该调用后端注销接口，目前暂用退出登录模拟
    // await post('/user/delete') 
    
    uni.showToast({
      title: '账号已注销',
      icon: 'none'
    })
    
    setTimeout(() => {
      userStore.logout()
      uni.reLaunch({ url: '/pages/login/index' })
    }, 1500)
    
  } catch {
    // 取消
  }
}

onMounted(() => {
  if (userStore.isLoggedIn) {
    userStore.fetchUserInfo()
    fetchStats()
  }
})
</script>

<style lang="scss" scoped>
.page-user {
  min-height: 100vh;
  background: #F5F5F5;
  padding-bottom: 120rpx;
}

.header {
  position: relative;
  
  .header-bg {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 400rpx;
    background: linear-gradient(180deg, #F5A623 0%, #FFB84D 100%);
  }
  
  .header-content {
    position: relative;
    padding: 32rpx;
  }
}

.user-card {
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16rpx;
  padding: 32rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.1);
  
  .avatar {
    width: 100rpx;
    height: 100rpx;
    border-radius: 50%;
    background: #f5f5f5;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 48rpx;
  }
  
  .user-info {
    margin-left: 24rpx;
    
    .username {
      display: block;
      font-size: 34rpx;
      font-weight: 600;
      color: #333;
    }
    
    .phone {
      display: block;
      font-size: 26rpx;
      color: #999;
      margin-top: 8rpx;
    }
  }
}

.invite-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12rpx;
  padding: 20rpx 24rpx;
  margin-top: 24rpx;
  
  .invite-left {
    .invite-label {
      display: block;
      font-size: 24rpx;
      color: rgba(255, 255, 255, 0.8);
    }
    
    .invite-code {
      display: block;
      font-size: 32rpx;
      font-weight: 600;
      color: #F5A623;
      margin-top: 4rpx;
    }
  }
  
  .invite-btn {
    display: flex;
    align-items: center;
    background: #F5A623;
    color: #fff;
    padding: 12rpx 24rpx;
    border-radius: 24rpx;
    font-size: 26rpx;
    
    .btn-icon {
      margin-right: 8rpx;
    }
  }
}

.stats-card {
  background: #fff;
  border-radius: 16rpx;
  margin: -40rpx 32rpx 0;
  padding: 32rpx;
  position: relative;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
  
  .stats-main {
    text-align: center;
    padding-bottom: 24rpx;
    border-bottom: 1rpx solid #f5f5f5;
    
    .stats-label {
      display: block;
      font-size: 26rpx;
      color: #999;
    }
    
    .stats-points {
      display: flex;
      align-items: center;
      justify-content: center;
      margin-top: 12rpx;
      
      .points-icon {
        font-size: 40rpx;
        margin-right: 12rpx;
      }
      
      .points-value {
        font-size: 56rpx;
        font-weight: bold;
        color: #F5A623;
      }
    }
  }
  
  .stats-row {
    display: flex;
    padding-top: 24rpx;
    
    .stat-item {
      flex: 1;
      text-align: center;
      
      .stat-value {
        display: block;
        font-size: 36rpx;
        font-weight: bold;
        color: #333;
      }
      
      .stat-label {
        display: block;
        font-size: 24rpx;
        color: #999;
        margin-top: 8rpx;
      }
    }
  }
}

.menu-list {
  margin: 24rpx 32rpx;
  
  .menu-item {
    display: flex;
    align-items: center;
    background: #fff;
    border-radius: 16rpx;
    padding: 28rpx 24rpx;
    margin-bottom: 16rpx;
    box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.04);
    
    .menu-icon {
      width: 72rpx;
      height: 72rpx;
      border-radius: 16rpx;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-right: 20rpx;
      font-size: 32rpx;
      
      &.icon-points {
        background: linear-gradient(135deg, #FFF0E6 0%, #FFE4D4 100%);
      }
      
      &.icon-orders {
        background: linear-gradient(135deg, #E6F7FF 0%, #D4F0FF 100%);
      }
      
      &.icon-submissions {
        background: linear-gradient(135deg, #F0FFF4 0%, #D4FFE4 100%);
      }
      
      &.icon-invite {
        background: linear-gradient(135deg, #E8F4FD 0%, #D4EDFC 100%);
      }
    }
    
    .menu-text {
      flex: 1;
      font-size: 30rpx;
      color: #333;
    }
    
    .menu-arrow {
      font-size: 32rpx;
      color: #ccc;
    }
  }
}

.logout-btn {
  margin: 40rpx 32rpx 20rpx;
  height: 88rpx;
  background: #fff;
  border-radius: 44rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #F56C6C;
  font-size: 30rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.05);
}

.delete-account {
  text-align: center;
  padding: 20rpx;
  padding-bottom: 60rpx;
  
  text {
    font-size: 24rpx;
    color: #999;
    text-decoration: underline;
  }
}
</style>
