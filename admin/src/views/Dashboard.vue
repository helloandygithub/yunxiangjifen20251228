<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <div class="stat-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
          <div class="stat-icon"><el-icon><User /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.userCount }}</div>
            <div class="stat-label">用户总数</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
          <div class="stat-icon"><el-icon><Trophy /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.activityCount }}</div>
            <div class="stat-label">进行中活动</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
          <div class="stat-icon"><el-icon><DocumentChecked /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.pendingCount }}</div>
            <div class="stat-label">待审核</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
          <div class="stat-icon"><el-icon><ShoppingBag /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.orderCount }}</div>
            <div class="stat-label">今日订单</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="16">
        <div class="page-card">
          <div class="card-header">
            <h3>最新提交</h3>
            <el-button type="primary" link @click="$router.push('/submissions')">查看全部</el-button>
          </div>
          <el-table :data="recentSubmissions" style="width: 100%">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="activity_title" label="活动" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="statusType[row.status]">{{ statusText[row.status] }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="提交时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="page-card">
          <div class="card-header">
            <h3>待处理订单</h3>
            <el-button type="primary" link @click="$router.push('/orders')">查看全部</el-button>
          </div>
          <el-table :data="pendingOrders" style="width: 100%">
            <el-table-column prop="order_no" label="订单号" />
            <el-table-column prop="product_name" label="商品" />
          </el-table>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/utils/api'
import dayjs from 'dayjs'

const stats = ref({
  userCount: 0,
  activityCount: 0,
  pendingCount: 0,
  orderCount: 0
})

const recentSubmissions = ref([])
const pendingOrders = ref([])

const statusType = {
  pending: 'warning',
  approved: 'success',
  rejected: 'danger'
}

const statusText = {
  pending: '待审核',
  approved: '已通过',
  rejected: '已拒绝'
}

const formatDate = (date) => dayjs(date).format('YYYY-MM-DD HH:mm')

const fetchData = async () => {
  try {
    // 获取统计数据
    const statsRes = await api.get('/admin/stats')
    if (statsRes.data) {
      stats.value = statsRes.data
    }
    
    const submissionsRes = await api.get('/admin/submissions', { params: { page_size: 5 } })
    if (submissionsRes.data?.items) {
      recentSubmissions.value = submissionsRes.data.items
    }
    
    const ordersRes = await api.get('/admin/orders', { params: { status: 'pending', page_size: 5 } })
    if (ordersRes.data?.items) {
      pendingOrders.value = ordersRes.data.items
    }
  } catch (error) {
    console.error(error)
  }
}

onMounted(fetchData)
</script>

<style lang="scss" scoped>
.stat-card {
  border-radius: 12px;
  padding: 24px;
  color: #fff;
  display: flex;
  align-items: center;
  gap: 16px;
  
  .stat-icon {
    width: 60px;
    height: 60px;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    
    .el-icon {
      font-size: 28px;
    }
  }
  
  .stat-info {
    .stat-value {
      font-size: 28px;
      font-weight: bold;
    }
    
    .stat-label {
      font-size: 14px;
      opacity: 0.9;
    }
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  
  h3 {
    font-size: 16px;
    color: #303133;
  }
}
</style>
