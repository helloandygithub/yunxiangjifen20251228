<template>
  <view class="page-order-detail">
    <!-- 导航栏 -->
    <view class="nav-bar safe-area-top">
      <view class="nav-back" @tap="goBack">
        <text>←</text>
      </view>
      <text class="nav-title">订单详情</text>
    </view>
    
    <view v-if="loading" class="loading">
      <text>加载中...</text>
    </view>

    <template v-else-if="order">
      <!-- 订单状态时间线 -->
      <view class="status-card card">
        <view class="card-header">
          <text class="card-title">订单状态</text>
        </view>
        <view class="timeline">
          <view :class="['timeline-item', { active: true }]">
            <view class="timeline-icon icon-pending">
              <text>📦</text>
            </view>
            <view class="timeline-content">
              <text class="timeline-title">待发货</text>
              <text class="timeline-time">{{ formatDate(order.created_at) }}</text>
            </view>
          </view>
          <view :class="['timeline-item', { active: order.status !== 'pending' }]">
            <view class="timeline-icon icon-shipped">
              <text>🚚</text>
            </view>
            <view class="timeline-content">
              <text class="timeline-title">已发货</text>
              <text class="timeline-time" v-if="order.shipped_at">{{ formatDate(order.shipped_at) }}</text>
            </view>
          </view>
          <view :class="['timeline-item', { active: order.status === 'completed' }]">
            <view class="timeline-icon icon-completed">
              <text>✅</text>
            </view>
            <view class="timeline-content">
              <text class="timeline-title">已完成</text>
              <text class="timeline-time" v-if="order.completed_at">{{ formatDate(order.completed_at) }}</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 商品信息 -->
      <view class="product-card card">
        <view class="card-header">
          <text class="card-title">商品信息</text>
        </view>
        <view class="product-content">
          <view class="product-image">
            <text>🎁</text>
          </view>
          <view class="product-info">
            <text class="product-name">{{ order.product_name }}</text>
            <view class="product-points">
              <text class="points-icon">💰</text>
              <text class="points-value">{{ order.points_cost }} 积分</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 虚拟商品信息 -->
      <view v-if="order.product_type === 'virtual' && order.shipping_info && order.status !== 'pending'" class="virtual-card card">
        <view class="card-header">
          <text class="card-title">虚拟商品信息</text>
        </view>
        <view class="info-row" v-if="order.shipping_info.code">
          <text class="info-label">兑换码</text>
          <view class="info-value-row">
            <text class="info-code">{{ order.shipping_info.code }}</text>
            <view class="copy-btn" @tap="copyCode">📋</view>
          </view>
        </view>
        <view class="info-row" v-if="order.shipping_info.instructions">
          <text class="info-label">使用说明</text>
          <text class="info-value">{{ order.shipping_info.instructions }}</text>
        </view>
      </view>

      <!-- 物流信息 -->
      <view v-if="order.product_type === 'physical' && order.status !== 'pending' && order.shipping_info" class="shipping-card card">
        <view class="card-header">
          <text class="card-title">物流信息</text>
        </view>
        <view class="info-row">
          <text class="info-label">快递公司</text>
          <text class="info-value">{{ order.shipping_info.company || '-' }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">运单号</text>
          <view class="info-value-row">
            <text class="info-code">{{ order.shipping_info.tracking_no || '-' }}</text>
            <view class="copy-btn" @tap="copyTracking" v-if="order.shipping_info.tracking_no">📋</view>
          </view>
        </view>
      </view>

      <!-- 收货地址 -->
      <view v-if="order.product_type === 'physical' && order.delivery_info" class="address-card card">
        <view class="card-header">
          <text class="card-title">收货地址</text>
        </view>
        <view class="address-content">
          <text class="address-name">{{ order.delivery_info.name }} {{ formatPhone(order.delivery_info.phone) }}</text>
          <text class="address-detail">{{ order.delivery_info.address }}</text>
        </view>
      </view>

      <!-- 订单信息 -->
      <view class="order-card card">
        <view class="card-header">
          <text class="card-title">订单信息</text>
        </view>
        <view class="info-row">
          <text class="info-label">订单编号</text>
          <text class="info-value">{{ order.order_no }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">创建时间</text>
          <text class="info-value">{{ formatDate(order.created_at) }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">消耗积分</text>
          <text class="info-value points">{{ order.points_cost }}</text>
        </view>
      </view>
    </template>

    <!-- 底部按钮 -->
    <view class="footer safe-area-bottom" v-if="order && order.status === 'shipped' && order.product_type === 'physical'">
      <view class="confirm-btn" @tap="confirmReceipt">
        <text>{{ confirming ? '处理中...' : '确认收货' }}</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { get, post } from '@/utils/request'

const orderId = ref(null)
const loading = ref(true)
const confirming = ref(false)
const order = ref(null)

const goBack = () => {
  uni.navigateBack()
}

const formatDate = (date) => {
  if (!date) return ''
  const d = new Date(date)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

const formatPhone = (phone) => {
  if (!phone) return ''
  return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
}

const fetchOrder = async () => {
  loading.value = true
  try {
    const res = await get(`/user/orders/${orderId.value}`)
    if (res.code === 0) {
      order.value = res.data
    } else {
      uni.showToast({ title: res.message || '获取订单失败', icon: 'none' })
    }
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const copyCode = () => {
  if (!order.value?.shipping_info?.code) return
  uni.setClipboardData({
    data: order.value.shipping_info.code,
    success: () => {
      uni.showToast({ title: '已复制', icon: 'success' })
    }
  })
}

const copyTracking = () => {
  if (!order.value?.shipping_info?.tracking_no) return
  uni.setClipboardData({
    data: order.value.shipping_info.tracking_no,
    success: () => {
      uni.showToast({ title: '已复制', icon: 'success' })
    }
  })
}

const confirmReceipt = async () => {
  if (confirming.value) return
  
  try {
    await uni.showModal({
      title: '确认收货',
      content: '确认已收到商品吗？'
    })
  } catch {
    return
  }
  
  confirming.value = true
  try {
    const res = await post(`/user/orders/${orderId.value}/confirm`)
    if (res.code === 0) {
      uni.showToast({ title: '确认成功', icon: 'success' })
      fetchOrder()
    } else {
      uni.showToast({ title: res.message || '确认失败', icon: 'none' })
    }
  } catch (error) {
    console.error(error)
  } finally {
    confirming.value = false
  }
}

onMounted(() => {
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1]
  orderId.value = currentPage.options?.id
  
  if (orderId.value) {
    fetchOrder()
  }
})
</script>

<style lang="scss" scoped>
.page-order-detail {
  min-height: 100vh;
  background: #FFF9F0;
  padding-bottom: 180rpx;
}

.nav-bar {
  display: flex;
  align-items: center;
  padding: 24rpx 32rpx;
  background: #fff;
  
  .nav-back {
    width: 60rpx;
    height: 60rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 40rpx;
    color: #333;
  }
  
  .nav-title {
    flex: 1;
    text-align: center;
    font-size: 34rpx;
    font-weight: 600;
    color: #333;
    margin-right: 60rpx;
  }
}

.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 100rpx 0;
  color: #999;
}

.card {
  background: #fff;
  margin: 24rpx 32rpx;
  border-radius: 16rpx;
  padding: 28rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.04);
  
  .card-header {
    margin-bottom: 24rpx;
    
    .card-title {
      font-size: 30rpx;
      font-weight: 600;
      color: #333;
    }
  }
}

.timeline {
  .timeline-item {
    display: flex;
    align-items: flex-start;
    padding: 16rpx 0;
    position: relative;
    
    &:not(:last-child)::after {
      content: '';
      position: absolute;
      left: 32rpx;
      top: 80rpx;
      width: 2rpx;
      height: calc(100% - 40rpx);
      background: #eee;
    }
    
    &.active {
      .timeline-icon {
        background: #FFF4E6;
      }
      
      .timeline-title {
        color: #333;
        font-weight: 500;
      }
      
      &::after {
        background: #F5A623;
      }
    }
    
    .timeline-icon {
      width: 64rpx;
      height: 64rpx;
      border-radius: 50%;
      background: #f5f5f5;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 28rpx;
      margin-right: 20rpx;
      flex-shrink: 0;
    }
    
    .timeline-content {
      flex: 1;
      padding-top: 8rpx;
      
      .timeline-title {
        display: block;
        font-size: 28rpx;
        color: #999;
      }
      
      .timeline-time {
        display: block;
        font-size: 24rpx;
        color: #F5A623;
        margin-top: 4rpx;
      }
    }
  }
}

.product-content {
  display: flex;
  align-items: center;
  
  .product-image {
    width: 120rpx;
    height: 120rpx;
    background: #FFF4E6;
    border-radius: 12rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 48rpx;
    margin-right: 20rpx;
  }
  
  .product-info {
    flex: 1;
    
    .product-name {
      display: block;
      font-size: 30rpx;
      font-weight: 500;
      color: #333;
      margin-bottom: 8rpx;
    }
    
    .product-points {
      display: flex;
      align-items: center;
      
      .points-icon {
        font-size: 24rpx;
        margin-right: 8rpx;
      }
      
      .points-value {
        font-size: 28rpx;
        color: #F5A623;
        font-weight: 500;
      }
    }
  }
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16rpx 0;
  border-bottom: 1rpx solid #f5f5f5;
  
  &:last-child {
    border-bottom: none;
  }
  
  .info-label {
    font-size: 28rpx;
    color: #999;
  }
  
  .info-value {
    font-size: 28rpx;
    color: #333;
    
    &.points {
      color: #F5A623;
      font-weight: 600;
    }
  }
  
  .info-value-row {
    display: flex;
    align-items: center;
    
    .info-code {
      font-size: 28rpx;
      color: #333;
      margin-right: 16rpx;
    }
    
    .copy-btn {
      font-size: 28rpx;
      padding: 8rpx;
    }
  }
}

.address-content {
  .address-name {
    display: block;
    font-size: 28rpx;
    color: #333;
    font-weight: 500;
    margin-bottom: 8rpx;
  }
  
  .address-detail {
    display: block;
    font-size: 26rpx;
    color: #666;
    line-height: 1.5;
  }
}

.footer {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 24rpx 32rpx;
  background: #fff;
  box-shadow: 0 -4rpx 16rpx rgba(0, 0, 0, 0.05);
  
  .confirm-btn {
    height: 88rpx;
    background: #F5A623;
    border-radius: 44rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-size: 32rpx;
    font-weight: 500;
  }
}
</style>
