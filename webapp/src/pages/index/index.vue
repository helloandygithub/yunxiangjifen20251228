<template>
  <view class="page-index">
    <!-- 顶部橙色区域 -->
    <view class="header">
      <view class="header-bg"></view>
      <view class="header-content safe-area-top">
        <!-- 用户信息卡片 -->
        <view class="user-card" @tap="goToUser">
          <view class="user-left">
            <view class="avatar">
              <text>👤</text>
            </view>
            <view class="user-text">
              <text class="greeting">{{ greeting }}</text>
              <text class="username">{{ isLoggedIn && userInfo?.phone ? formatPhone(userInfo.phone) : '点击登录' }}</text>
            </view>
          </view>
          <view class="user-right">
            <text class="points-label">我的积分</text>
            <text class="points-value">{{ formatNumber(userInfo?.points_balance || 0) }}</text>
          </view>
        </view>
        
        <!-- Banner轮播 -->
        <swiper class="banner" indicator-dots autoplay circular>
          <swiper-item v-for="(item, index) in activities.slice(0, 3)" :key="index">
            <view class="banner-item" @tap="goToActivity(item)">
              <image v-if="item.cover_image" :src="item.cover_image" class="banner-img" mode="aspectFill" />
              <view v-else class="banner-placeholder">
                <text>🎯 {{ item.title }}</text>
              </view>
            </view>
          </swiper-item>
        </swiper>
      </view>
    </view>
    
    <!-- 快捷入口 -->
    <view class="quick-entry">
      <view class="entry-item" @tap="handleCheckin">
        <view class="entry-icon icon-checkin">
          <text class="iconfont">📅</text>
        </view>
        <text class="entry-text">每日签到</text>
      </view>
      <view class="entry-item" @tap="goToActivityList">
        <view class="entry-icon icon-task">
          <text class="iconfont">🎯</text>
        </view>
        <text class="entry-text">任务中心</text>
      </view>
      <view class="entry-item" @tap="handleInvite">
        <view class="entry-icon icon-invite">
          <text class="iconfont">👥</text>
        </view>
        <text class="entry-text">邀请好友</text>
      </view>
      <view class="entry-item" @tap="goToRecords('points')">
        <view class="entry-icon icon-record">
          <text class="iconfont">📊</text>
        </view>
        <text class="entry-text">积分记录</text>
      </view>
    </view>

    <!-- 热门活动 -->
    <view class="section">
      <view class="section-header">
        <text class="section-title">热门活动</text>
        <view class="more-link" @tap="goToActivityList">
          <text>查看全部</text>
          <text class="arrow">›</text>
        </view>
      </view>

      <view v-if="loading" class="loading">
        <text>加载中...</text>
      </view>

      <view v-else-if="activities.length === 0" class="empty">
        <text class="empty-icon">📭</text>
        <text class="empty-text">暂无活动</text>
      </view>

      <view v-else class="activity-list">
        <view 
          v-for="item in activities" 
          :key="item.id" 
          class="activity-card"
          @tap="goToActivity(item)"
        >
          <view class="card-cover">
            <image 
              v-if="item.cover_image" 
              :src="item.cover_image" 
              class="cover-img" 
              mode="aspectFill"
            />
            <view v-else class="cover-placeholder">
              <text>🎯</text>
            </view>
            <view :class="['status-tag', item.status === 'active' ? 'tag-active' : 'tag-ended']">
              {{ item.status === 'active' ? '进行中' : '已结束' }}
            </view>
          </view>
          
          <view class="card-content">
            <text class="card-title">{{ item.title }}</text>
            <text class="card-desc">{{ item.description || '参与活动赢取积分' }}</text>
            
            <view class="card-meta">
              <view class="meta-points">
                <text class="points-icon">💰</text>
                <text class="points-text">+{{ item.reward_points || 0 }} 积分</text>
              </view>
              <view class="meta-participants">
                <text class="participants-icon">👥</text>
                <text>{{ item.participants || 0 }}人参与</text>
              </view>
            </view>
            
            <view class="card-btn">
              <text>立即参与</text>
            </view>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useUserStore } from '@/stores/user'
import { get } from '@/utils/request'

const userStore = useUserStore()

// 使用 computed 确保响应式
const isLoggedIn = computed(() => userStore.isLoggedIn)
const userInfo = computed(() => userStore.userInfo)

const loading = ref(false)
const activities = ref([])


const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return '早上好'
  if (hour < 18) return '下午好'
  return '晚上好'
})

const formatPhone = (phone) => {
  if (!phone) return ''
  return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
}

const formatNumber = (num) => {
  return num?.toLocaleString() || '0'
}

const fetchActivities = async () => {
  loading.value = true
  try {
    const res = await get('/activities', { status: 'active' })
    activities.value = res.data?.items || res.data || []
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const goToActivity = (item) => {
  uni.navigateTo({
    url: `/pages/activity/detail?id=${item.id}`
  })
}

const goToUser = () => {
  if (!isLoggedIn.value) {
    uni.navigateTo({ url: '/pages/login/index' })
  } else {
    uni.switchTab({ url: '/pages/user/index' })
  }
}

const goToMall = () => {
  uni.switchTab({ url: '/pages/mall/index' })
}

const goToRecords = (type) => {
  if (!isLoggedIn.value) {
    uni.navigateTo({ url: '/pages/login/index' })
    return
  }
  uni.navigateTo({ url: `/pages/user/records?type=${type}` })
}

const goToActivityList = () => {
  uni.switchTab({ url: '/pages/activity/list' })
}

const handleCheckin = () => {
  if (!isLoggedIn.value) {
    uni.navigateTo({ url: '/pages/login/index' })
    return
  }
  uni.showToast({ title: '签到成功 +10积分', icon: 'success' })
}

const handleInvite = () => {
  if (!isLoggedIn.value) {
    uni.navigateTo({ url: '/pages/login/index' })
    return
  }
  const code = userInfo.value?.invite_code || ''
  uni.setClipboardData({
    data: code,
    success: () => {
      uni.showToast({ title: '邀请码已复制', icon: 'success' })
    }
  })
}

onMounted(() => {
  fetchActivities()
  if (isLoggedIn.value) {
    userStore.fetchUserInfo()
  }
})

onShow(() => {
  // 登录态变化时刷新用户数据
  if (isLoggedIn.value) {
    userStore.fetchUserInfo()
  }
})
</script>

<style lang="scss" scoped>
.page-index {
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
    height: 520rpx;
    background: linear-gradient(180deg, #F5A623 0%, #FFB84D 100%);
  }
  
  .header-content {
    position: relative;
    padding: 32rpx;
  }
}

.user-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  
  .user-left {
    display: flex;
    align-items: center;
    
    .avatar {
      width: 88rpx;
      height: 88rpx;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.3);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 40rpx;
    }
    
    .user-text {
      margin-left: 20rpx;
      
      .greeting {
        display: block;
        color: rgba(255, 255, 255, 0.9);
        font-size: 26rpx;
      }
      
      .username {
        display: block;
        color: #fff;
        font-size: 32rpx;
        font-weight: 600;
        margin-top: 4rpx;
      }
    }
  }
  
  .user-right {
    text-align: right;
    
    .points-label {
      display: block;
      color: rgba(255, 255, 255, 0.9);
      font-size: 24rpx;
    }
    
    .points-value {
      display: block;
      color: #fff;
      font-size: 48rpx;
      font-weight: bold;
      margin-top: 4rpx;
    }
  }
}

.banner {
  height: 300rpx;
  margin-top: 24rpx;
  border-radius: 16rpx;
  overflow: hidden;
  
  .banner-item {
    width: 100%;
    height: 100%;
  }
  
  .banner-img {
    width: 100%;
    height: 100%;
    border-radius: 16rpx;
  }
  
  .banner-placeholder {
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, #FFE4C4 0%, #FFDAB9 100%);
    border-radius: 16rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 32rpx;
    color: #F5A623;
    font-weight: 500;
  }
}

.quick-entry {
  display: flex;
  justify-content: space-around;
  background: #fff;
  border-radius: 16rpx;
  padding: 32rpx 16rpx;
  margin: -60rpx 32rpx 0;
  position: relative;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
  
  .entry-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    
    .entry-icon {
      width: 88rpx;
      height: 88rpx;
      border-radius: 20rpx;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-bottom: 12rpx;
      
      .iconfont {
        font-size: 40rpx;
      }
      
      &.icon-checkin {
        background: linear-gradient(135deg, #E8F4FD 0%, #D4EDFC 100%);
      }
      
      &.icon-task {
        background: linear-gradient(135deg, #FFF0E6 0%, #FFE4D4 100%);
      }
      
      &.icon-invite {
        background: linear-gradient(135deg, #E6F7FF 0%, #D4F0FF 100%);
      }
      
      &.icon-record {
        background: linear-gradient(135deg, #F0FFF4 0%, #D4FFE4 100%);
      }
    }
    
    .entry-text {
      font-size: 24rpx;
      color: #333;
    }
  }
}

.section {
  padding: 32rpx;
  margin-top: 24rpx;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24rpx;
  
  .section-title {
    font-size: 34rpx;
    font-weight: bold;
    color: #333;
  }
  
  .more-link {
    display: flex;
    align-items: center;
    color: #999;
    font-size: 26rpx;
    
    .arrow {
      font-size: 28rpx;
      margin-left: 4rpx;
    }
  }
}

.loading, .empty {
  padding: 80rpx 0;
  text-align: center;
  color: #999;
  
  .empty-icon {
    font-size: 80rpx;
    display: block;
    margin-bottom: 16rpx;
  }
  
  .empty-text {
    font-size: 28rpx;
  }
}

.activity-list {
  .activity-card {
    background: #fff;
    border-radius: 16rpx;
    overflow: hidden;
    margin-bottom: 24rpx;
    box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.05);
  }
  
  .card-cover {
    position: relative;
    height: 320rpx;
    
    .cover-img {
      width: 100%;
      height: 100%;
    }
    
    .cover-placeholder {
      width: 100%;
      height: 100%;
      background: linear-gradient(135deg, #FFE4C4 0%, #FFDAB9 100%);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 80rpx;
    }
    
    .status-tag {
      position: absolute;
      top: 20rpx;
      right: 20rpx;
      padding: 8rpx 20rpx;
      border-radius: 20rpx;
      font-size: 22rpx;
      
      &.tag-active {
        background: #F5A623;
        color: #fff;
      }
      
      &.tag-ended {
        background: rgba(0, 0, 0, 0.5);
        color: #fff;
      }
    }
  }
  
  .card-content {
    padding: 24rpx;
    
    .card-title {
      font-size: 32rpx;
      font-weight: 600;
      color: #333;
      display: block;
      margin-bottom: 12rpx;
    }
    
    .card-desc {
      font-size: 26rpx;
      color: #999;
      display: block;
      display: -webkit-box;
      -webkit-line-clamp: 1;
      -webkit-box-orient: vertical;
      overflow: hidden;
      margin-bottom: 20rpx;
    }
    
    .card-meta {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20rpx;
      
      .meta-points {
        display: flex;
        align-items: center;
        
        .points-icon {
          font-size: 28rpx;
          margin-right: 8rpx;
        }
        
        .points-text {
          color: #F5A623;
          font-size: 28rpx;
          font-weight: 600;
        }
      }
      
      .meta-participants {
        display: flex;
        align-items: center;
        color: #999;
        font-size: 24rpx;
        
        .participants-icon {
          margin-right: 8rpx;
        }
      }
    }
    
    .card-btn {
      width: 100%;
      height: 80rpx;
      background: #F5A623;
      border-radius: 40rpx;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #fff;
      font-size: 30rpx;
      font-weight: 500;
    }
  }
}
</style>
