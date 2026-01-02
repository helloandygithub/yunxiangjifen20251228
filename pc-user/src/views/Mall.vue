<template>
  <div class="mall-page">
    <div class="container">
      <!-- 页面标题 -->
      <div class="page-header">
        <h1>积分商城</h1>
        <p class="subtitle">用积分兑换心仪好礼，数码产品、生活用品应有尽有</p>
      </div>

      <!-- 用户积分信息 -->
      <div class="user-points-card" v-if="userStore.isLoggedIn">
        <div class="points-info">
          <div class="points-icon">
            <el-icon><Coin /></el-icon>
          </div>
          <div class="points-content">
            <div class="points-label">我的积分</div>
            <div class="points-value">{{ userStore.user?.points_balance || userStore.user?.points || 0 }}</div>
          </div>
        </div>
        <el-button type="primary" @click="$router.push('/user')">
          查看明细
          <el-icon><ArrowRight /></el-icon>
        </el-button>
      </div>

      <!-- 分类筛选 -->
      <div class="category-filter">
        <div class="filter-label">商品分类</div>
        <div class="filter-buttons">
          <button 
            :class="['filter-btn', { active: category === 'all' }]"
            @click="category = 'all'; handleCategoryChange()"
          >全部商品</button>
          <button 
            :class="['filter-btn', { active: category === 'digital' }]"
            @click="category = 'digital'; handleCategoryChange()"
          >数码产品</button>
          <button 
            :class="['filter-btn', { active: category === 'life' }]"
            @click="category = 'life'; handleCategoryChange()"
          >生活用品</button>
          <button 
            :class="['filter-btn', { active: category === 'virtual' }]"
            @click="category = 'virtual'; handleCategoryChange()"
          >虚拟权益</button>
          <button 
            :class="['filter-btn', { active: category === 'gift' }]"
            @click="category = 'gift'; handleCategoryChange()"
          >礼品卡券</button>
        </div>
      </div>

      <!-- 商品网格 -->
      <div class="products-grid" v-loading="loading">
        <div class="product-card" v-for="item in products" :key="item.id" @click="goToDetail(item.id)">
          <div class="product-cover">
            <img v-if="item.image_url" :src="item.image_url" />
            <div v-else class="cover-placeholder">
              <div class="placeholder-icon">🎁</div>
            </div>
            <el-tag v-if="item.stock <= 0" class="stock-tag sold-out">已售罄</el-tag>
            <el-tag v-else-if="item.stock < 10" class="stock-tag low-stock">仅剩{{ item.stock }}件</el-tag>
          </div>
          <div class="product-content">
            <h3>{{ item.name }}</h3>
            <p class="product-desc">{{ item.description || '精选好物，积分兑换' }}</p>
            <div class="product-footer">
              <div class="product-price">
                <span class="price-points">{{ item.price_points }}</span>
                <span class="price-unit">积分</span>
              </div>
              <el-button 
                type="primary" 
                size="small" 
                :disabled="item.stock <= 0"
                @click.stop="handleExchange(item)"
              >
                {{ item.stock <= 0 ? '已售罄' : '立即兑换' }}
              </el-button>
            </div>
          </div>
        </div>
        
        <el-empty v-if="!loading && products.length === 0" description="暂无商品" />
      </div>

      <!-- 分页 -->
      <el-pagination
        v-if="total > 0"
        v-model:current-page="page"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next"
        @current-change="fetchProducts"
        class="pagination"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Coin, ArrowRight } from '@element-plus/icons-vue'
import request from '@/utils/request'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const products = ref([])
const category = ref('all')
const page = ref(1)
const pageSize = ref(16)
const total = ref(0)

const fetchProducts = async () => {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (category.value !== 'all') {
      params.category = category.value
    }
    const res = await request.get('/mall/products', { params })
    products.value = res.data?.items || []
    total.value = res.data?.total || 0
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleCategoryChange = () => {
  page.value = 1
  fetchProducts()
}

const handleExchange = async (product) => {
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

  if (userStore.user.points < product.price_points) {
    ElMessage.warning('积分不足，无法兑换')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确认使用 ${product.price_points} 积分兑换 ${product.name}？`,
      '确认兑换',
      {
        confirmButtonText: '确认兑换',
        cancelButtonText: '取消'
      }
    )
    
    // 跳转到商品详情页进行兑换
    router.push(`/product/${product.id}`)
  } catch {}
}

const goToDetail = (id) => {
  router.push(`/product/${id}`)
}

onMounted(fetchProducts)
</script>

<style lang="scss" scoped>
.mall-page {
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
  
  .page-header {
    margin-bottom: 32px;
    
    h1 {
      font-size: 36px;
      font-weight: 700;
      color: #333;
      margin-bottom: 12px;
    }
    
    .subtitle {
      font-size: 16px;
      color: #666;
    }
  }
  
  .user-points-card {
    background: linear-gradient(135deg, #FFF9F0 0%, #FFF5E6 100%);
    border-radius: 16px;
    padding: 24px 32px;
    margin-bottom: 32px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 4px 20px rgba(245, 166, 35, 0.15);
    
    .points-info {
      display: flex;
      align-items: center;
      gap: 20px;
      
      .points-icon {
        width: 64px;
        height: 64px;
        background: linear-gradient(135deg, #F5A623 0%, #FF8C00 100%);
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 32px;
        color: white;
      }
      
      .points-content {
        .points-label {
          font-size: 14px;
          color: #999;
          margin-bottom: 8px;
        }
        
        .points-value {
          font-size: 36px;
          font-weight: 700;
          color: #F5A623;
        }
      }
    }
    
    .el-button {
      background: #F5A623;
      border: none;
      color: white;
      padding: 12px 24px;
      
      &:hover {
        background: #E09612;
      }
    }
  }
  
  .category-filter {
    background: white;
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 32px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    
    .filter-label {
      font-size: 16px;
      font-weight: 600;
      color: #333;
      margin-bottom: 16px;
    }
    
    .filter-buttons {
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
      
      .filter-btn {
        padding: 10px 24px;
        border: 1px solid #E5E7EB;
        background: white;
        border-radius: 8px;
        font-size: 14px;
        color: #666;
        cursor: pointer;
        transition: all 0.2s;
        
        &:hover {
          border-color: #F5A623;
          color: #F5A623;
        }
        
        &.active {
          background: #F5A623;
          border-color: #F5A623;
          color: white;
        }
      }
    }
  }
  
  .products-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 24px;
    margin-bottom: 40px;
  }
}

.product-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid transparent;
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
    border-color: #FFE4B3;
  }
  
  .product-cover {
    width: 100%;
    height: 220px;
    overflow: hidden;
    position: relative;
    background: linear-gradient(135deg, #F0F0F0 0%, #E0E0E0 100%);
    
    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
    
    .cover-placeholder {
      width: 100%;
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      
      .placeholder-icon {
        font-size: 80px;
        opacity: 0.3;
      }
    }
    
    .stock-tag {
      position: absolute;
      top: 12px;
      right: 12px;
      border: none;
      color: white;
      font-weight: 500;
      
      &.sold-out {
        background: #999;
      }
      
      &.low-stock {
        background: #FF6B6B;
      }
    }
  }
  
  .product-content {
    padding: 20px;
    
    h3 {
      font-size: 16px;
      font-weight: 600;
      color: #333;
      margin-bottom: 8px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    
    .product-desc {
      font-size: 14px;
      color: #999;
      margin-bottom: 16px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    
    .product-footer {
      display: flex;
      align-items: center;
      justify-content: space-between;
      
      .product-price {
        .price-points {
          font-size: 24px;
          font-weight: 700;
          color: #F5A623;
        }
        
        .price-unit {
          font-size: 14px;
          color: #999;
          margin-left: 4px;
        }
      }
      
      .el-button {
        background: #F5A623;
        border: none;
        color: white;
        
        &:hover:not(:disabled) {
          background: #E09612;
        }
        
        &:disabled {
          background: #CCC;
          cursor: not-allowed;
        }
      }
    }
  }
}

.pagination {
  display: flex;
  justify-content: center;
  
  :deep(.el-pager li.is-active) {
    background: #F5A623;
    color: white;
  }
  
  :deep(button:hover),
  :deep(.el-pager li:hover) {
    color: #F5A623;
  }
}
</style>
