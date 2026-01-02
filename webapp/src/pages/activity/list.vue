<template>
  <view class="page-activity-list">
    <!-- 顶部橙色区域 -->
    <view class="header">
      <view class="header-bg"></view>
      <view class="header-content safe-area-top">
        <text class="header-title">活动大厅</text>
        
        <!-- 搜索框 -->
        <view class="search-bar">
          <text class="search-icon">🔍</text>
          <input 
            class="search-input" 
            placeholder="搜索活动..." 
            v-model="searchKeyword"
            @confirm="handleSearch"
          />
        </view>
        
        <!-- 统计数据 -->
        <view class="stats-card">
          <view class="stat-item">
            <text class="stat-value">{{ activeCount }}</text>
            <text class="stat-label">进行中</text>
          </view>
          <view class="stat-divider"></view>
          <view class="stat-item">
            <text class="stat-value">{{ participatedCount }}</text>
            <text class="stat-label">已参与</text>
          </view>
          <view class="stat-divider"></view>
          <view class="stat-item">
            <text class="stat-value">{{ formatNumber(totalPoints) }}</text>
            <text class="stat-label">累计获得积分</text>
          </view>
        </view>
      </view>
    </view>
    
    <!-- 活动列表 -->
    <view class="list-container">
      <view v-if="loading" class="loading">
        <text>加载中...</text>
      </view>
      
      <view v-else-if="filteredActivities.length === 0" class="empty">
        <text class="empty-icon">📭</text>
        <text class="empty-text">暂无活动</text>
      </view>
      
      <view v-else class="activity-list">
        <view 
          v-for="item in filteredActivities" 
          :key="item.id" 
          class="activity-card"
          @tap="goToDetail(item.id)"
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
import { useUserStore } from '@/stores/user'
import { get } from '@/utils/request'

const userStore = useUserStore()
const loading = ref(false)
const activities = ref([])
const searchKeyword = ref('')

const activeCount = computed(() => {
  return activities.value.filter(a => a.status === 'active').length
})

const participatedCount = ref(0)
const totalPoints = ref(0)

const filteredActivities = computed(() => {
  if (!searchKeyword.value) return activities.value
  return activities.value.filter(a => 
    a.title.includes(searchKeyword.value) || 
    a.description?.includes(searchKeyword.value)
  )
})

const formatNumber = (num) => {
  return num?.toLocaleString() || '0'
}

const fetchActivities = async () => {
  loading.value = true
  try {
    const res = await get('/activities')
    activities.value = res.data?.items || res.data || []
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const fetchUserStats = async () => {
  if (!userStore.isLoggedIn) return
  try {
    const res = await get('/user/records', { type: 'submissions' })
    const submissions = res.data?.submissions?.items || []
    participatedCount.value = submissions.length
    totalPoints.value = submissions
      .filter(s => s.status === 'approved')
      .reduce((sum, s) => sum + (s.reward_points || 0), 0)
  } catch (error) {
    console.error(error)
  }
}

const handleSearch = () => {
  // 搜索由computed自动过滤
}

const goToDetail = (id) => {
  uni.navigateTo({ url: `/pages/activity/detail?id=${id}` })
}

onMounted(() => {
  fetchActivities()
  fetchUserStats()
})
</script>

<style lang="scss" scoped>
.page-activity-list {
  min-height: 100vh;
  background: #f5f5f5;
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
  
  .header-title {
    font-size: 36rpx;
    font-weight: bold;
    color: #fff;
    display: block;
    margin-bottom: 24rpx;
  }
}

.search-bar {
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 40rpx;
  padding: 16rpx 24rpx;
  margin-bottom: 24rpx;
  
  .search-icon {
    font-size: 32rpx;
    margin-right: 16rpx;
    opacity: 0.5;
  }
  
  .search-input {
    flex: 1;
    font-size: 28rpx;
    color: #333;
  }
}

.stats-card {
  display: flex;
  justify-content: space-around;
  align-items: center;
  background: #fff;
  border-radius: 16rpx;
  padding: 32rpx 16rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
  
  .stat-item {
    flex: 1;
    text-align: center;
    
    .stat-value {
      display: block;
      font-size: 40rpx;
      font-weight: bold;
      color: #F5A623;
      
      &.stat-login {
        color: #999;
      }
    }
    
    .stat-label {
      display: block;
      font-size: 24rpx;
      color: #999;
      margin-top: 8rpx;
    }
  }
  
  .stat-divider {
    width: 1rpx;
    height: 60rpx;
    background: #eee;
  }
}

.list-container {
  padding: 24rpx 32rpx;
}

.loading, .empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 120rpx 0;
  
  .empty-icon {
    font-size: 80rpx;
    margin-bottom: 24rpx;
  }
  
  .empty-text {
    color: #999;
    font-size: 28rpx;
  }
}

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
</style>
