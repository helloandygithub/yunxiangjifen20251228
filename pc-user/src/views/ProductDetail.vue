<template>
  <div class="product-detail-page">
    <div class="container" v-loading="loading">
      <div v-if="product" class="detail-content">
        <!-- 面包屑导航 -->
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item :to="{ path: '/mall' }">积分商城</el-breadcrumb-item>
            <el-breadcrumb-item>商品详情</el-breadcrumb-item>
          </el-breadcrumb>
        </div>

        <!-- 商品主要信息 -->
        <div class="product-main">
          <div class="product-gallery">
            <div class="main-image">
              <img v-if="product.image_url" :src="product.image_url" />
              <div v-else class="image-placeholder">
                <div class="placeholder-icon">🎁</div>
              </div>
            </div>
          </div>

          <div class="product-info">
            <div class="product-category">{{ product.category || '数码产品' }}</div>
            <h1 class="product-title">{{ product.name }}</h1>
            <p class="product-subtitle">{{ product.description || '精选好物，积分兑换' }}</p>
            
            <div class="product-price-card">
              <div class="price-label">兑换价格</div>
              <div class="price-value">
                <span class="price-points">{{ product.price_points }}</span>
                <span class="price-unit">积分</span>
              </div>
              <div class="stock-info">
                <el-icon><Box /></el-icon>
                <span v-if="product.stock > 0">库存充足（剩余{{ product.stock }}件）</span>
                <span v-else class="sold-out">已售罄</span>
              </div>
            </div>

            <!-- 收货信息表单 -->
            <div v-if="product.type === 'physical'" class="address-section">
              <h3 class="section-title">收货信息</h3>
              <el-form :model="addressForm" label-width="80px" class="address-form">
                <el-form-item label="收货人" required>
                  <el-input v-model="addressForm.name" placeholder="请输入收货人姓名" />
                </el-form-item>
                <el-form-item label="手机号" required>
                  <el-input v-model="addressForm.phone" placeholder="请输入手机号" />
                </el-form-item>
                <el-form-item label="收货地址" required>
                  <el-input v-model="addressForm.address" type="textarea" :rows="3" placeholder="请输入详细地址" />
                </el-form-item>
              </el-form>
            </div>

            <!-- 兑换按钮 -->
            <div class="action-buttons">
              <el-button
                type="primary"
                size="large"
                :disabled="product.stock <= 0"
                :loading="submitting"
                @click="handleRedeem"
                class="redeem-btn"
              >
                <el-icon><ShoppingCart /></el-icon>
                {{ product.stock <= 0 ? '已售罄' : '立即兑换' }}
              </el-button>
            </div>
          </div>
        </div>

        <!-- 商品详情 -->
        <div class="product-details">
          <div class="details-tabs">
            <div class="tab-header">
              <div :class="['tab-item', { active: activeTab === 'detail' }]" @click="activeTab = 'detail'">
                商品详情
              </div>
              <div :class="['tab-item', { active: activeTab === 'rules' }]" @click="activeTab = 'rules'">
                兑换规则
              </div>
            </div>
            <div class="tab-content">
              <div v-if="activeTab === 'detail'" class="detail-content-text">
                <p>{{ product.description || '暂无详细描述' }}</p>
                <p>本商品为精选优质产品，使用积分即可兑换。兑换成功后，我们会尽快为您安排发货。</p>
              </div>
              <div v-if="activeTab === 'rules'" class="rules-content">
                <p>1. 兑换前请确保积分余额充足</p>
                <p>2. 实物商品需填写收货地址，虚拟商品将发送至账户</p>
                <p>3. 兑换成功后不支持退换</p>
                <p>4. 商品将在3-7个工作日内发货</p>
                <p>5. 如有问题请联系客服</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 推荐商品 -->
        <div class="recommend-section">
          <h2 class="section-title">相关推荐</h2>
          <div class="recommend-grid">
            <div class="recommend-item" v-for="i in 4" :key="i" @click="$router.push('/mall')">
              <div class="recommend-cover"></div>
              <div class="recommend-info">
                <div class="recommend-name">推荐商品 {{ i }}</div>
                <div class="recommend-price">{{ 1000 + i * 100 }} 积分</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Box, ShoppingCart } from '@element-plus/icons-vue'
import request from '@/utils/request'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const loading = ref(true)
const submitting = ref(false)
const product = ref(null)
const activeTab = ref('detail')

const addressForm = reactive({
  name: '',
  phone: '',
  address: ''
})

const fetchProduct = async () => {
  loading.value = true
  try {
    const res = await request.get(`/mall/products/${route.params.id}`)
    product.value = res.data
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const validateAddress = () => {
  if (product.value?.type !== 'physical') return true
  
  if (!addressForm.name) {
    ElMessage.error('请输入收货人')
    return false
  }
  if (!addressForm.phone || !/^1[3-9]\d{9}$/.test(addressForm.phone)) {
    ElMessage.error('请输入正确的手机号')
    return false
  }
  if (!addressForm.address) {
    ElMessage.error('请输入收货地址')
    return false
  }
  return true
}

const handleRedeem = async () => {
  if (!userStore.isLoggedIn) {
    try {
      await ElMessageBox.confirm('请先登录后再兑换商品', '提示', {
        confirmButtonText: '去登录',
        cancelButtonText: '取消'
      })
      router.push('/login')
    } catch {}
    return
  }
  
  if (!validateAddress()) return
  
  try {
    await ElMessageBox.confirm(
      `确定使用 ${product.value.price_points} 积分兑换「${product.value.name}」吗？`,
      '确认兑换',
      { confirmButtonText: '确定', cancelButtonText: '取消' }
    )
  } catch {
    return
  }
  
  submitting.value = true
  try {
    await request.post('/mall/redeem', {
      product_id: product.value.id,
      shipping_address: product.value.type === 'physical' ? 
        `${addressForm.name} ${addressForm.phone} ${addressForm.address}` : null
    })
    ElMessage.success('兑换成功')
    router.push('/user')
  } catch (error) {
    console.error(error)
  } finally {
    submitting.value = false
  }
}

onMounted(fetchProduct)
</script>

<style lang="scss" scoped>
.product-detail-page {
  min-height: calc(100vh - 64px);
  background: #FFFBF5;
  padding: 40px 0 80px;
  
  .container {
    max-width: 1200px;
    width: 100%;
    margin: 0 auto;
    padding: 0 24px;
    box-sizing: border-box;
  }
  
  .breadcrumb {
    margin-bottom: 24px;
  }
  
  .detail-content {
    background: white;
    border-radius: 16px;
    padding: 40px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  }
}

.product-main {
  display: flex;
  gap: 60px;
  margin-bottom: 60px;
  
  .product-gallery {
    width: 500px;
    flex-shrink: 0;
    
    .main-image {
      width: 100%;
      height: 500px;
      border-radius: 16px;
      overflow: hidden;
      background: linear-gradient(135deg, #F0F0F0 0%, #E0E0E0 100%);
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
      
      img {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }
      
      .image-placeholder {
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        
        .placeholder-icon {
          font-size: 120px;
          opacity: 0.3;
        }
      }
    }
  }
  
  .product-info {
    flex: 1;
    
    .product-category {
      display: inline-block;
      padding: 6px 16px;
      background: #FFF4E6;
      color: #F5A623;
      border-radius: 6px;
      font-size: 14px;
      font-weight: 500;
      margin-bottom: 16px;
    }
    
    .product-title {
      font-size: 32px;
      font-weight: 700;
      color: #333;
      margin-bottom: 12px;
      line-height: 1.4;
    }
    
    .product-subtitle {
      font-size: 16px;
      color: #666;
      line-height: 1.6;
      margin-bottom: 32px;
    }
    
    .product-price-card {
      background: linear-gradient(135deg, #FFF9F0 0%, #FFF5E6 100%);
      border-radius: 16px;
      padding: 24px;
      margin-bottom: 32px;
      
      .price-label {
        font-size: 14px;
        color: #999;
        margin-bottom: 8px;
      }
      
      .price-value {
        margin-bottom: 16px;
        
        .price-points {
          font-size: 48px;
          font-weight: 700;
          color: #F5A623;
        }
        
        .price-unit {
          font-size: 18px;
          color: #999;
          margin-left: 8px;
        }
      }
      
      .stock-info {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 14px;
        color: #666;
        
        .el-icon {
          font-size: 18px;
        }
        
        .sold-out {
          color: #FF6B6B;
        }
      }
    }
    
    .address-section {
      margin-bottom: 32px;
      
      .section-title {
        font-size: 18px;
        font-weight: 600;
        color: #333;
        margin-bottom: 20px;
      }
      
      .address-form {
        background: #FAFAFA;
        padding: 24px;
        border-radius: 12px;
      }
    }
    
    .action-buttons {
      .redeem-btn {
        width: 100%;
        background: #F5A623;
        border: none;
        color: white;
        padding: 16px;
        font-size: 18px;
        font-weight: 600;
        
        &:hover:not(:disabled) {
          background: #E09612;
        }
        
        &:disabled {
          background: #CCC;
          cursor: not-allowed;
        }
        
        .el-icon {
          margin-right: 8px;
        }
      }
    }
  }
}

.product-details {
  margin-bottom: 60px;
  
  .details-tabs {
    background: white;
    border: 1px solid #F0F0F0;
    border-radius: 12px;
    overflow: hidden;
    
    .tab-header {
      display: flex;
      border-bottom: 2px solid #F0F0F0;
      
      .tab-item {
        flex: 1;
        padding: 20px;
        text-align: center;
        font-size: 16px;
        font-weight: 600;
        color: #666;
        cursor: pointer;
        transition: all 0.2s;
        
        &:hover {
          color: #F5A623;
        }
        
        &.active {
          color: #F5A623;
          border-bottom: 2px solid #F5A623;
          margin-bottom: -2px;
        }
      }
    }
    
    .tab-content {
      padding: 32px;
      
      .detail-content-text,
      .rules-content {
        p {
          font-size: 16px;
          color: #666;
          line-height: 2;
          margin-bottom: 16px;
          
          &:last-child {
            margin-bottom: 0;
          }
        }
      }
    }
  }
}

.recommend-section {
  .section-title {
    font-size: 24px;
    font-weight: 600;
    color: #333;
    margin-bottom: 24px;
  }
  
  .recommend-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 20px;
    
    .recommend-item {
      background: white;
      border: 1px solid #F0F0F0;
      border-radius: 12px;
      overflow: hidden;
      cursor: pointer;
      transition: all 0.2s;
      
      &:hover {
        transform: translateY(-4px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
      }
      
      .recommend-cover {
        width: 100%;
        height: 150px;
        background: linear-gradient(135deg, #F0F0F0 0%, #E0E0E0 100%);
      }
      
      .recommend-info {
        padding: 16px;
        
        .recommend-name {
          font-size: 14px;
          color: #333;
          margin-bottom: 8px;
          font-weight: 500;
        }
        
        .recommend-price {
          font-size: 16px;
          color: #F5A623;
          font-weight: 600;
        }
      }
    }
  }
}
</style>
