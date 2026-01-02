<template>
  <view class="page-product-detail">
    <view v-if="loading" class="loading">
      <text>加载中...</text>
    </view>

    <template v-else-if="product">
      <image 
        v-if="product.image_url" 
        :src="product.image_url" 
        class="product-image" 
        mode="aspectFill"
        @tap="previewImage"
      />
      <view v-else class="product-image product-placeholder">
        <text>🎁</text>
      </view>

      <view class="product-content card">
        <text class="product-name">{{ product.name }}</text>
        
        <view class="product-meta">
          <view class="meta-item">
            <text class="label">所需积分</text>
            <text class="value points">{{ product.price_points }}</text>
          </view>
          <view class="meta-item">
            <text class="label">商品类型</text>
            <text class="value">{{ product.type === 'virtual' ? '虚拟商品' : '实物商品' }}</text>
          </view>
          <view class="meta-item">
            <text class="label">库存</text>
            <text :class="['value', { 'sold-out': product.stock <= 0 }]">
              {{ product.stock > 0 ? product.stock : '已售罄' }}
            </text>
          </view>
        </view>

        <view class="divider"></view>

        <view class="product-desc">
          <text class="desc-title">商品说明</text>
          <text class="desc-content">{{ product.description || '暂无说明' }}</text>
        </view>
      </view>

      <!-- 实物商品收货地址 -->
      <view v-if="product.type === 'physical'" class="address-card card">
        <text class="card-title">收货地址</text>
        
        <view class="form-group">
          <view class="form-label required">收货人</view>
          <input 
            v-model="addressForm.name" 
            class="form-input" 
            placeholder="请输入收货人姓名"
          />
        </view>
        
        <view class="form-group">
          <view class="form-label required">手机号</view>
          <input 
            v-model="addressForm.phone" 
            class="form-input" 
            type="number"
            placeholder="请输入手机号"
          />
        </view>
        
        <view class="form-group">
          <view class="form-label required">收货地址</view>
          <textarea 
            v-model="addressForm.address" 
            class="form-textarea" 
            placeholder="请输入详细收货地址"
          />
        </view>
      </view>
    </template>

    <view class="footer safe-area-bottom" v-if="product">
      <view class="footer-left" @tap="handlePointsClick">
        <text class="my-points" v-if="isLoggedIn">我的积分: {{ userStore.userInfo?.points_balance || 0 }}</text>
        <text class="my-points login-hint" v-else>登录查看积分</text>
      </view>
      <view 
        :class="['btn', canRedeem ? 'btn-primary' : 'btn-disabled']"
        @tap="handleRedeem"
      >
        <text>{{ redeemBtnText }}</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useUserStore } from '@/stores/user'
import { get, post } from '@/utils/request'

const userStore = useUserStore()

const isLoggedIn = computed(() => userStore.isLoggedIn)

const productId = ref(null)
const loading = ref(true)
const submitting = ref(false)
const product = ref(null)

const addressForm = reactive({
  name: '',
  phone: '',
  address: ''
})

const canRedeem = computed(() => {
  if (!product.value) return false
  if (product.value.stock <= 0) return false
  if (!isLoggedIn.value) return false
  if ((userStore.userInfo?.points_balance || 0) < product.value.price_points) return false
  return true
})

const redeemBtnText = computed(() => {
  if (!product.value) return '兑换'
  if (product.value.stock <= 0) return '已售罄'
  if (!isLoggedIn.value) return '登录后兑换'
  if ((userStore.userInfo?.points_balance || 0) < product.value.price_points) return '积分不足'
  if (submitting.value) return '兑换中...'
  return '立即兑换'
})

const fetchProduct = async () => {
  loading.value = true
  try {
    const res = await get(`/mall/products/${productId.value}`)
    product.value = res.data
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const previewImage = () => {
  if (product.value?.image_url) {
    uni.previewImage({
      urls: [product.value.image_url]
    })
  }
}

const validateAddress = () => {
  if (product.value?.type !== 'physical') return true
  
  if (!addressForm.name) {
    uni.showToast({ title: '请输入收货人', icon: 'none' })
    return false
  }
  if (!addressForm.phone || !/^1[3-9]\d{9}$/.test(addressForm.phone)) {
    uni.showToast({ title: '请输入正确的手机号', icon: 'none' })
    return false
  }
  if (!addressForm.address) {
    uni.showToast({ title: '请输入收货地址', icon: 'none' })
    return false
  }
  return true
}

const handleRedeem = async () => {
  // 检查登录状态
  if (!userStore.isLoggedIn) {
    uni.showModal({
      title: '提示',
      content: '请先登录后再兑换商品',
      confirmText: '去登录',
      success: (res) => {
        if (res.confirm) {
          uni.navigateTo({ url: '/pages/login/index' })
        }
      }
    })
    return
  }
  
  if (!canRedeem.value || submitting.value) return
  if (!validateAddress()) return
  
  try {
    await uni.showModal({
      title: '确认兑换',
      content: `确定使用 ${product.value.price_points} 积分兑换「${product.value.name}」吗？`
    })
  } catch {
    return
  }
  
  submitting.value = true
  try {
    const data = {
      product_id: product.value.id,
      quantity: 1
    }
    
    if (product.value.type === 'physical') {
      data.delivery_info = { ...addressForm }
    }
    
    await post('/mall/redeem', data)
    
    uni.showToast({
      title: '兑换成功',
      icon: 'success'
    })
    
    userStore.fetchUserInfo()
    
    setTimeout(() => {
      uni.navigateBack()
    }, 1500)
  } catch (error) {
    console.error(error)
  } finally {
    submitting.value = false
  }
}

const handlePointsClick = () => {
  if (!isLoggedIn.value) {
    uni.navigateTo({ url: '/pages/login/index' })
  }
}

onMounted(() => {
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1]
  productId.value = currentPage.options?.id
  
  if (productId.value) {
    fetchProduct()
  }
  
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
.page-product-detail {
  min-height: 100vh;
  padding-bottom: 140rpx;
}

.product-image {
  width: 100%;
  height: 500rpx;
}

.product-placeholder {
  background: linear-gradient(135deg, #667EEA 0%, #764BA2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 120rpx;
}

.product-content {
  margin: -40rpx 24rpx 24rpx;
  position: relative;
  
  .product-name {
    font-size: 36rpx;
    font-weight: bold;
    color: #303133;
    display: block;
  }
  
  .product-meta {
    display: flex;
    margin-top: 24rpx;
    
    .meta-item {
      flex: 1;
      
      .label {
        font-size: 24rpx;
        color: #909399;
        display: block;
      }
      
      .value {
        font-size: 28rpx;
        color: #303133;
        font-weight: 500;
        margin-top: 8rpx;
        display: block;
        
        &.points {
          color: #E6A23C;
          font-size: 36rpx;
        }
        
        &.sold-out {
          color: #F56C6C;
        }
      }
    }
  }
  
  .product-desc {
    .desc-title {
      font-size: 28rpx;
      font-weight: 500;
      color: #303133;
      display: block;
      margin-bottom: 12rpx;
    }
    
    .desc-content {
      font-size: 26rpx;
      color: #606266;
      line-height: 1.6;
    }
  }
}

.address-card {
  margin: 0 24rpx 24rpx;
  
  .card-title {
    font-size: 30rpx;
    font-weight: 500;
    color: #303133;
    display: block;
    margin-bottom: 24rpx;
  }
}

.footer {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  align-items: center;
  padding: 20rpx 32rpx;
  background: #fff;
  box-shadow: 0 -4rpx 16rpx rgba(0, 0, 0, 0.05);
  
  .footer-left {
    flex: 1;
    
    .my-points {
      font-size: 26rpx;
      color: #909399;
      
      &.login-hint {
        color: #F5A623;
        text-decoration: underline;
      }
    }
  }
  
  .btn {
    width: 240rpx;
    height: 80rpx;
    font-size: 30rpx;
  }
}
</style>
