<template>
  <view class="page-mall">
    <!-- 顶部橙色区域 -->
    <view class="header">
      <view class="header-bg"></view>
      <view class="header-content safe-area-top">
        <text class="page-title">积分商城</text>
        
        <!-- 积分卡片 -->
        <view class="points-card">
          <view class="points-left" @tap="handlePointsClick">
            <text class="points-label">可用积分</text>
            <view class="points-row">
              <text class="points-icon">💰</text>
              <text class="points-value" v-if="isLoggedIn">{{ formatNumber(userStore.userInfo?.points_balance || 0) }}</text>
              <text class="points-login" v-else>登录查看</text>
            </view>
          </view>
          <view class="points-btn" @tap="goToPointsDetail">
            <text>积分明细</text>
          </view>
        </view>
      </view>
    </view>

    <view class="container">
      <!-- 分类标签 -->
      <view class="category-tabs">
        <view 
          v-for="cat in categories" 
          :key="cat.value"
          :class="['category-item', { active: currentCategory === cat.value }]"
          @tap="switchCategory(cat.value)"
        >
          <text>{{ cat.label }}</text>
        </view>
      </view>

      <!-- 商品列表 -->
      <view v-if="loading" class="loading">
        <text>加载中...</text>
      </view>

      <view v-else-if="products.length === 0" class="empty">
        <text class="empty-icon">🛒</text>
        <text class="empty-text">暂无商品</text>
      </view>

      <view v-else class="product-grid">
        <view 
          v-for="item in products" 
          :key="item.id" 
          class="product-card"
          @tap="goToDetail(item)"
        >
          <view class="product-cover">
            <image 
              v-if="item.image_url" 
              :src="item.image_url" 
              class="product-image" 
              mode="aspectFill"
            />
            <view v-else class="product-placeholder">
              <text>🎁</text>
            </view>
            <view v-if="item.stock <= 20 && item.stock > 0" class="stock-tag">
              仅剩{{ item.stock }}件
            </view>
          </view>
          
          <view class="product-info">
            <text class="product-name">{{ item.name }}</text>
            <view class="product-meta">
              <view class="product-points">
                <text class="points-icon">💰</text>
                <text class="points-num">{{ item.price_points }}</text>
              </view>
              <text class="product-stock">库存{{ item.stock }}</text>
            </view>
            <view :class="['exchange-btn', { disabled: item.stock <= 0 }]">
              <text>{{ item.stock > 0 ? '立即兑换' : '已售罄' }}</text>
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

const isLoggedIn = computed(() => userStore.isLoggedIn)

const loading = ref(false)
const products = ref([])
const currentCategory = ref('all')

const categories = [
  { label: '全部', value: 'all' },
  { label: '虚拟商品', value: 'virtual' },
  { label: '实物商品', value: 'physical' }
]

const formatNumber = (num) => {
  return num?.toLocaleString() || '0'
}

const fetchProducts = async () => {
  loading.value = true
  try {
    const params = {}
    if (currentCategory.value !== 'all') {
      params.type = currentCategory.value
    }
    const res = await get('/mall/products', params)
    products.value = res.data?.items || res.data || []
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const switchCategory = (cat) => {
  currentCategory.value = cat
  fetchProducts()
}

const goToDetail = (item) => {
  uni.navigateTo({
    url: `/pages/mall/detail?id=${item.id}`
  })
}

const goToPointsDetail = () => {
  if (!isLoggedIn.value) {
    uni.navigateTo({ url: '/pages/login/index' })
    return
  }
  uni.navigateTo({ url: '/pages/user/records?type=points' })
}

const handlePointsClick = () => {
  if (!isLoggedIn.value) {
    uni.navigateTo({ url: '/pages/login/index' })
  }
}

onMounted(() => {
  fetchProducts()
  if (isLoggedIn.value) {
    userStore.fetchUserInfo()
  }
})

onShow(() => {
  // 登录态变化时刷新数据
  if (isLoggedIn.value) {
    userStore.fetchUserInfo()
  }
})
</script>

<style lang="scss" scoped>
.page-mall {
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
    height: 320rpx;
    background: linear-gradient(180deg, #F5A623 0%, #FFB84D 100%);
  }
  
  .header-content {
    position: relative;
    padding: 32rpx;
    
    .page-title {
      font-size: 36rpx;
      font-weight: bold;
      color: #fff;
      display: block;
      margin-bottom: 24rpx;
    }
  }
}

.points-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16rpx;
  padding: 32rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.1);
  
  .points-left {
    .points-label {
      display: block;
      font-size: 26rpx;
      color: #666;
      margin-bottom: 8rpx;
    }
    
    .points-row {
      display: flex;
      align-items: center;
      
      .points-icon {
        font-size: 40rpx;
        margin-right: 12rpx;
      }
      
      .points-value {
        font-size: 56rpx;
        font-weight: bold;
        color: #F5A623;
      }
      
      .points-login {
        font-size: 32rpx;
        color: #F5A623;
        text-decoration: underline;
      }
    }
  }
  
  .points-btn {
    background: #F5A623;
    color: #fff;
    padding: 16rpx 32rpx;
    border-radius: 32rpx;
    font-size: 26rpx;
    font-weight: 500;
  }
}

.container {
  padding: 24rpx 32rpx;
}

.category-tabs {
  display: flex;
  gap: 20rpx;
  margin-bottom: 24rpx;
  
  .category-item {
    padding: 16rpx 32rpx;
    border-radius: 32rpx;
    font-size: 28rpx;
    color: #666;
    background: #fff;
    
    &.active {
      background: #F5A623;
      color: #fff;
      font-weight: 500;
    }
  }
}

.loading, .empty {
  padding: 120rpx 0;
  text-align: center;
  
  .empty-icon {
    font-size: 80rpx;
    display: block;
    margin-bottom: 16rpx;
  }
  
  .empty-text {
    font-size: 28rpx;
    color: #999;
  }
}

.product-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20rpx;
}

.product-card {
  background: #fff;
  border-radius: 16rpx;
  overflow: hidden;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.05);
}

.product-cover {
  position: relative;
  height: 280rpx;
  
  .product-image {
    width: 100%;
    height: 100%;
  }
  
  .product-placeholder {
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, #FFE4C4 0%, #FFDAB9 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 60rpx;
  }
  
  .stock-tag {
    position: absolute;
    top: 16rpx;
    left: 16rpx;
    background: #FF6B6B;
    color: #fff;
    padding: 6rpx 16rpx;
    border-radius: 16rpx;
    font-size: 20rpx;
  }
}

.product-info {
  padding: 20rpx;
  
  .product-name {
    font-size: 28rpx;
    color: #333;
    font-weight: 500;
    display: block;
    margin-bottom: 16rpx;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  
  .product-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16rpx;
    
    .product-points {
      display: flex;
      align-items: center;
      
      .points-icon {
        font-size: 24rpx;
        margin-right: 6rpx;
      }
      
      .points-num {
        color: #F5A623;
        font-size: 32rpx;
        font-weight: bold;
      }
    }
    
    .product-stock {
      font-size: 22rpx;
      color: #999;
    }
  }
  
  .exchange-btn {
    width: 100%;
    height: 64rpx;
    background: #F5A623;
    border-radius: 32rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-size: 26rpx;
    font-weight: 500;
    
    &.disabled {
      background: #ccc;
    }
  }
}
</style>
