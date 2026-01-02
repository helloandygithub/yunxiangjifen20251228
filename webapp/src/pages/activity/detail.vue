<template>
  <view class="page-activity-detail">
    <!-- 导航栏 -->
    <view class="nav-bar safe-area-top">
      <view class="nav-back" @tap="goBack">
        <text>←</text>
      </view>
      <text class="nav-title">活动详情</text>
    </view>
    
    <view v-if="loading" class="loading">
      <text>加载中...</text>
    </view>

    <template v-else-if="activity">
      <!-- 封面图 -->
      <view class="cover-section">
        <image 
          v-if="activity.cover_image" 
          :src="activity.cover_image" 
          class="cover-image" 
          mode="aspectFill"
        />
        <view v-else class="cover-placeholder">
          <text>🎯</text>
        </view>
      </view>
      
      <!-- 标题和积分卡片 -->
      <view class="title-card card">
        <view class="title-row">
          <text class="activity-title">{{ activity.title }}</text>
          <view class="status-tag">进行中</view>
        </view>
        <view class="points-banner">
          <text class="points-icon">💰</text>
          <text class="points-value">+{{ activity.reward_points || 0 }}</text>
          <text class="points-label">积分奖励</text>
        </view>
      </view>
      
      <!-- 活动说明 -->
      <view class="section-card card">
        <view class="section-title">活动说明</view>
        <text class="section-desc">{{ activity.description }}</text>
        <text class="section-detail">
          参与本次活动，完成任务即可获得积分奖励。活动期间每位用户{{ frequencyText[activity.frequency_type] }}，提交内容需真实有效。我们将在3个工作日内完成审核，审核通过后积分将自动发放至您的账户。
        </text>
      </view>
      
      <!-- 参与要求 -->
      <view class="section-card card">
        <view class="section-title">参与要求</view>
        <view class="requirements-list">
          <view class="requirement-item">
            <text class="dot">•</text>
            <text>必须是企业在职员工</text>
          </view>
          <view class="requirement-item">
            <text class="dot">•</text>
            <text>提交内容需符合活动主题</text>
          </view>
          <view class="requirement-item">
            <text class="dot">•</text>
            <text>内容需原创，不得抄袭</text>
          </view>
          <view class="requirement-item">
            <text class="dot">•</text>
            <text>每人仅可提交一次</text>
          </view>
        </view>
      </view>

      <!-- 提交内容 -->
      <view class="section-card card" v-if="canSubmit">
        <view class="section-title">提交内容</view>
        
        <!-- 文字说明 -->
        <view class="form-group">
          <view class="form-label">
            <text class="label-icon">📝</text>
            <text>文字说明</text>
          </view>
          <textarea
            v-model="formData.content"
            placeholder="请输入活动相关内容..."
            class="form-textarea"
          />
        </view>
        
        <!-- 上传附件 -->
        <view class="form-group">
          <view class="form-label">
            <text class="label-icon">📎</text>
            <text>上传附件</text>
          </view>
          <view class="upload-area">
            <view 
              v-if="formData.attachment" 
              class="preview-image"
              @tap="previewImage(formData.attachment)"
            >
              <image :src="formData.attachment" mode="aspectFill" />
              <view class="remove-btn" @tap.stop="removeImage('attachment')">×</view>
            </view>
            <view v-else class="upload-box" @tap="chooseImage('attachment')">
              <text class="upload-icon">↑</text>
              <text class="upload-text">点击上传图片或文件</text>
              <text class="upload-hint">支持 JPG、PNG、PDF 格式</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 状态提示 -->
      <view v-if="!canSubmit" class="status-card card">
        <text class="status-icon">
          {{ activity.user_status === 'pending' ? '⏳' : '✅' }}
        </text>
        <text class="status-text">{{ statusMessage }}</text>
      </view>
    </template>

    <!-- 底部按钮 -->
    <view class="footer safe-area-bottom" v-if="activity && canSubmit">
      <view 
        :class="['submit-btn', { disabled: submitting }]"
        @tap="handleSubmit"
      >
        <text>{{ submitting ? '提交中...' : '提交参与' }}</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { get, post } from '@/utils/request'

const userStore = useUserStore()
const activityId = ref(null)
const loading = ref(true)
const submitting = ref(false)
const activity = ref(null)
const formData = ref({
  content: '',
  attachment: ''
})

const frequencyText = {
  once: '仅可参与一次',
  daily: '每日可参与一次',
  unlimited: '可无限参与'
}

const goBack = () => {
  uni.navigateBack()
}

const canSubmit = computed(() => {
  return activity.value?.user_status === 'available'
})

const statusMessage = computed(() => {
  const status = activity.value?.user_status
  if (status === 'pending') return '您的提交正在审核中，请耐心等待'
  if (status === 'completed') return '您已完成该活动'
  if (status === 'limit_reached') return '今日参与次数已达上限'
  return ''
})

const fetchActivity = async () => {
  loading.value = true
  try {
    const res = await get(`/activities/${activityId.value}`)
    activity.value = res.data
    
    // 初始化表单数据
    if (activity.value.form_schema) {
      activity.value.form_schema.forEach(field => {
        formData.value[field.key] = ''
      })
    }
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const chooseImage = async (key) => {
  try {
    const res = await uni.chooseImage({
      count: 1,
      sizeType: ['compressed'],
      sourceType: ['album', 'camera']
    })
    
    uni.showLoading({ title: '上传中...' })
    
    // 这里应该上传到COS，暂时使用本地路径
    formData.value[key] = res.tempFilePaths[0]
    
    uni.hideLoading()
  } catch (error) {
    console.error(error)
  }
}

const removeImage = (key) => {
  formData.value[key] = ''
}

const previewImage = (url) => {
  uni.previewImage({
    urls: [url]
  })
}

const validateForm = () => {
  for (const field of activity.value.form_schema) {
    if (field.required && !formData.value[field.key]) {
      uni.showToast({
        title: `请填写${field.label}`,
        icon: 'none'
      })
      return false
    }
  }
  return true
}

const handleSubmit = async () => {
  if (submitting.value) return
  
  // 检查登录状态
  if (!userStore.isLoggedIn) {
    uni.showModal({
      title: '提示',
      content: '请先登录后再参与活动',
      confirmText: '去登录',
      success: (res) => {
        if (res.confirm) {
          uni.navigateTo({ url: '/pages/login/index' })
        }
      }
    })
    return
  }
  
  if (!validateForm()) return
  
  submitting.value = true
  try {
    await post(`/activities/${activityId.value}/submit`, {
      submission_data: formData.value
    })
    
    uni.showToast({
      title: '提交成功',
      icon: 'success'
    })
    
    setTimeout(() => {
      uni.navigateBack()
    }, 1500)
  } catch (error) {
    console.error(error)
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1]
  activityId.value = currentPage.options?.id
  
  if (activityId.value) {
    fetchActivity()
  }
})
</script>

<style lang="scss" scoped>
.page-activity-detail {
  min-height: 100vh;
  background: #FFF9F0;
  padding-bottom: 160rpx;
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
  padding: 100rpx 0;
  text-align: center;
  color: #999;
}

.cover-section {
  .cover-image,
  .cover-placeholder {
    width: 100%;
    height: 400rpx;
  }
  
  .cover-placeholder {
    background: linear-gradient(135deg, #FFE4C4 0%, #FFDAB9 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 120rpx;
  }
}

.card {
  background: #fff;
  margin: 24rpx 32rpx;
  border-radius: 16rpx;
  padding: 28rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.04);
}

.title-card {
  margin-top: -40rpx;
  position: relative;
  
  .title-row {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 20rpx;
    
    .activity-title {
      flex: 1;
      font-size: 36rpx;
      font-weight: bold;
      color: #333;
      margin-right: 20rpx;
    }
    
    .status-tag {
      background: #F5A623;
      color: #fff;
      padding: 8rpx 20rpx;
      border-radius: 20rpx;
      font-size: 24rpx;
      flex-shrink: 0;
    }
  }
  
  .points-banner {
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #FFF4E6 0%, #FFECD2 100%);
    border-radius: 12rpx;
    padding: 24rpx;
    
    .points-icon {
      font-size: 36rpx;
      margin-right: 12rpx;
    }
    
    .points-value {
      font-size: 40rpx;
      font-weight: bold;
      color: #F5A623;
      margin-right: 12rpx;
    }
    
    .points-label {
      font-size: 28rpx;
      color: #F5A623;
    }
  }
}

.section-card {
  .section-title {
    font-size: 32rpx;
    font-weight: 600;
    color: #333;
    margin-bottom: 20rpx;
  }
  
  .section-desc {
    display: block;
    font-size: 28rpx;
    color: #333;
    margin-bottom: 16rpx;
  }
  
  .section-detail {
    display: block;
    font-size: 26rpx;
    color: #666;
    line-height: 1.8;
  }
}

.requirements-list {
  .requirement-item {
    display: flex;
    align-items: flex-start;
    margin-bottom: 16rpx;
    font-size: 28rpx;
    color: #666;
    
    &:last-child {
      margin-bottom: 0;
    }
    
    .dot {
      color: #F5A623;
      margin-right: 12rpx;
      font-weight: bold;
    }
  }
}

.form-group {
  margin-bottom: 32rpx;
  
  &:last-child {
    margin-bottom: 0;
  }
  
  .form-label {
    display: flex;
    align-items: center;
    font-size: 28rpx;
    color: #333;
    margin-bottom: 16rpx;
    
    .label-icon {
      margin-right: 8rpx;
    }
  }
  
  .form-textarea {
    width: 100%;
    height: 200rpx;
    background: #f9f9f9;
    border: 1rpx solid #eee;
    border-radius: 12rpx;
    padding: 20rpx;
    font-size: 28rpx;
    box-sizing: border-box;
  }
}

.upload-area {
  .upload-box {
    border: 2rpx dashed #ddd;
    border-radius: 12rpx;
    padding: 48rpx;
    display: flex;
    flex-direction: column;
    align-items: center;
    
    .upload-icon {
      font-size: 48rpx;
      color: #999;
      margin-bottom: 16rpx;
    }
    
    .upload-text {
      font-size: 28rpx;
      color: #666;
      margin-bottom: 8rpx;
    }
    
    .upload-hint {
      font-size: 24rpx;
      color: #999;
    }
  }
  
  .preview-image {
    position: relative;
    width: 200rpx;
    height: 200rpx;
    
    image {
      width: 100%;
      height: 100%;
      border-radius: 12rpx;
    }
    
    .remove-btn {
      position: absolute;
      top: -16rpx;
      right: -16rpx;
      width: 40rpx;
      height: 40rpx;
      background: #F56C6C;
      color: #fff;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 28rpx;
    }
  }
}

.status-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60rpx 40rpx;
  
  .status-icon {
    font-size: 80rpx;
    margin-bottom: 24rpx;
  }
  
  .status-text {
    font-size: 28rpx;
    color: #999;
    text-align: center;
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
  
  .submit-btn {
    height: 88rpx;
    background: #F5A623;
    border-radius: 44rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-size: 32rpx;
    font-weight: 500;
    
    &.disabled {
      opacity: 0.6;
    }
  }
}
</style>
