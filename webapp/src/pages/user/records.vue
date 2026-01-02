<template>
  <view class="page-records">
    <!-- 顶部标签 -->
    <view class="tabs">
      <view 
        v-for="tab in tabs" 
        :key="tab.value" 
        :class="['tab-item', { active: currentTab === tab.value }]"
        @tap="switchTab(tab.value)"
      >
        <text>{{ tab.label }}</text>
      </view>
    </view>

    <!-- 积分明细 -->
    <view v-if="currentTab === 'points'" class="record-list">
      <view v-if="loading" class="loading">
        <text>加载中...</text>
      </view>
      <view v-else-if="records.length === 0" class="empty">
        <text class="empty-icon">💰</text>
        <text class="empty-text">暂无积分记录</text>
      </view>
      <view v-else v-for="item in records" :key="item.id" class="record-item">
        <view class="record-info">
          <text class="record-title">{{ item.remark || '积分变动' }}</text>
          <text class="record-time">{{ formatDate(item.created_at) }}</text>
        </view>
        <text :class="['record-points', item.points > 0 ? 'income' : 'expense']">
          {{ item.points > 0 ? '+' : '' }}{{ item.points }}
        </text>
      </view>
    </view>

    <!-- 订单记录 -->
    <view v-if="currentTab === 'orders'" class="record-list">
      <view v-if="loading" class="loading">
        <text>加载中...</text>
      </view>
      <view v-else-if="records.length === 0" class="empty">
        <text class="empty-icon">📦</text>
        <text class="empty-text">暂无订单</text>
      </view>
      <view v-else v-for="item in records" :key="item.id" class="order-item card" @tap="goToOrderDetail(item.id)">
        <view class="order-header">
          <text class="order-no">{{ item.order_no }}</text>
          <text :class="['order-status', `status-${item.status}`]">{{ orderStatus[item.status] }}</text>
        </view>
        <view class="order-content">
          <text class="product-name">{{ item.product_name }}</text>
          <text class="order-points">-{{ item.points_cost }} 积分</text>
        </view>
        <view class="order-footer">
          <text class="order-time">{{ formatDate(item.created_at) }}</text>
          <text class="order-arrow">查看详情 ›</text>
        </view>
      </view>
    </view>

    <!-- 提交记录 -->
    <view v-if="currentTab === 'submissions'" class="record-list">
      <view v-if="loading" class="loading">
        <text>加载中...</text>
      </view>
      <view v-else-if="records.length === 0" class="empty">
        <text class="empty-icon">📋</text>
        <text class="empty-text">暂无提交记录</text>
      </view>
      <view v-else v-for="item in records" :key="item.id" class="submission-item card">
        <view class="submission-header">
          <text class="activity-title">{{ item.activity_title }}</text>
          <text :class="['submission-status', `status-${item.status}`]">{{ submissionStatus[item.status] }}</text>
        </view>
        <view class="submission-content" v-if="item.status === 'approved'">
          <text class="granted-points">+{{ item.granted_points }} 积分</text>
        </view>
        <view class="submission-content" v-else-if="item.status === 'rejected'">
          <text class="reject-reason">{{ item.audit_remark || '未通过审核' }}</text>
        </view>
        <view class="submission-footer">
          <text class="submission-time">{{ formatDate(item.created_at) }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { get } from '@/utils/request'

const userStore = useUserStore()

const tabs = [
  { label: '积分明细', value: 'points' },
  { label: '我的订单', value: 'orders' },
  { label: '活动提交', value: 'submissions' }
]

const currentTab = ref('points')
const records = ref([])
const loading = ref(false)

const orderStatus = {
  pending: '待发货',
  shipped: '已发货',
  completed: '已完成'
}

const submissionStatus = {
  pending: '审核中',
  approved: '已通过',
  rejected: '未通过'
}

const formatDate = (date) => {
  if (!date) return ''
  const d = new Date(date)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

const fetchRecords = async () => {
  loading.value = true
  try {
    const res = await get('/user/records', { type: currentTab.value })
    records.value = res.data?.[currentTab.value]?.items || []
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const switchTab = (tab) => {
  currentTab.value = tab
  records.value = []
  fetchRecords()
}

const goToOrderDetail = (id) => {
  uni.navigateTo({
    url: `/pages/order/detail?id=${id}`
  })
}

onMounted(() => {
  // 记录页面必须登录
  if (!userStore.isLoggedIn) {
    uni.showModal({
      title: '提示',
      content: '请先登录',
      confirmText: '去登录',
      showCancel: false,
      success: () => {
        uni.navigateTo({ url: '/pages/login/index' })
      }
    })
    return
  }
  
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1]
  if (currentPage?.options?.type) {
    currentTab.value = currentPage.options.type
  }
  fetchRecords()
})
</script>

<style lang="scss" scoped>
.page-records {
  min-height: 100vh;
  background: #f5f5f5;
}

.tabs {
  display: flex;
  background: #fff;
  padding: 0 24rpx;
  border-bottom: 1rpx solid #eee;
  position: sticky;
  top: 0;
  z-index: 10;
  
  .tab-item {
    flex: 1;
    text-align: center;
    padding: 28rpx 0;
    font-size: 28rpx;
    color: #999;
    position: relative;
    
    &.active {
      color: #667EEA;
      font-weight: 600;
      
      &::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 48rpx;
        height: 6rpx;
        background: linear-gradient(135deg, #667EEA, #764BA2);
        border-radius: 3rpx;
      }
    }
  }
}

.record-list {
  padding: 24rpx;
}

.loading, .empty {
  display: flex;
  flex-direction: column;
  align-items: center;
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

.record-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 28rpx;
  background: #fff;
  border-radius: 16rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.04);
  
  .record-info {
    .record-title {
      font-size: 28rpx;
      color: #333;
      display: block;
      font-weight: 500;
    }
    .record-time {
      font-size: 24rpx;
      color: #999;
      margin-top: 8rpx;
      display: block;
    }
  }
  
  .record-points {
    font-size: 36rpx;
    font-weight: bold;
    &.income { color: #52c41a; }
    &.expense { color: #ff4d4f; }
  }
}

.card {
  background: #fff;
  border-radius: 16rpx;
  padding: 28rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.04);
}

.order-item, .submission-item {
  .order-header, .submission-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16rpx;
  }
  
  .order-no { font-size: 24rpx; color: #999; }
  .activity-title { font-size: 30rpx; font-weight: 600; color: #333; }
  
  .order-status, .submission-status {
    font-size: 24rpx;
    padding: 6rpx 16rpx;
    border-radius: 20rpx;
    
    &.status-pending { background: #fff7e6; color: #fa8c16; }
    &.status-shipped, &.status-approved { background: #f6ffed; color: #52c41a; }
    &.status-completed { background: #e6f7ff; color: #1890ff; }
    &.status-rejected { background: #fff2f0; color: #ff4d4f; }
  }
  
  .order-content, .submission-content {
    margin-bottom: 16rpx;
  }
  
  .product-name { font-size: 28rpx; color: #333; }
  .order-points { font-size: 28rpx; color: #fa8c16; margin-left: 16rpx; }
  .granted-points { font-size: 32rpx; color: #52c41a; font-weight: 600; }
  .reject-reason { font-size: 26rpx; color: #ff4d4f; }
  
  .order-footer, .submission-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    .order-time, .submission-time {
      font-size: 24rpx;
      color: #999;
    }
    
    .order-arrow {
      font-size: 24rpx;
      color: #667EEA;
    }
  }
}
</style>
