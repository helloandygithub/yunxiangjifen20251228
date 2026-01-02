<template>
  <view class="custom-tabbar">
    <view 
      v-for="(item, index) in tabs" 
      :key="index" 
      :class="['tab-item', { active: currentTab === index }]"
      @tap="switchTab(index)"
    >
      <view class="tab-icon">{{ item.icon }}</view>
      <text class="tab-text">{{ item.text }}</text>
    </view>
  </view>
</template>

<script setup>
import { ref, watch } from 'vue'

const tabs = [
  { icon: '🏠', text: '首页', path: '/pages/index/index' },
  { icon: '🛍️', text: '商城', path: '/pages/mall/index' },
  { icon: '👤', text: '我的', path: '/pages/user/index' }
]

const currentTab = ref(0)

const getCurrentTabIndex = () => {
  const pages = getCurrentPages()
  if (pages.length > 0) {
    const currentPage = pages[pages.length - 1]
    const path = '/' + currentPage.route
    const index = tabs.findIndex(t => t.path === path)
    return index >= 0 ? index : 0
  }
  return 0
}

currentTab.value = getCurrentTabIndex()

const switchTab = (index) => {
  if (currentTab.value === index) return
  currentTab.value = index
  uni.switchTab({ url: tabs[index].path })
}
</script>

<style lang="scss" scoped>
.custom-tabbar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 110rpx;
  background: #fff;
  display: flex;
  justify-content: space-around;
  align-items: center;
  box-shadow: 0 -4rpx 20rpx rgba(0, 0, 0, 0.06);
  padding-bottom: env(safe-area-inset-bottom);
  z-index: 999;
  
  .tab-item {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 12rpx 0;
    transition: all 0.2s;
    
    .tab-icon {
      font-size: 44rpx;
      margin-bottom: 4rpx;
      transition: transform 0.2s;
    }
    
    .tab-text {
      font-size: 22rpx;
      color: #999;
    }
    
    &.active {
      .tab-icon {
        transform: scale(1.1);
      }
      .tab-text {
        color: #667EEA;
        font-weight: 600;
      }
    }
  }
}
</style>
