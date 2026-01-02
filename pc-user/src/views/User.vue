<template>
  <div class="user-page">
    <div class="container">
      <el-row :gutter="24">
        <el-col :span="6">
          <el-card class="user-card">
            <div class="avatar">👤</div>
            <div class="phone">{{ formatPhone(userStore.userInfo?.phone) }}</div>
            <div class="points">
              <span class="label">当前积分</span>
              <span class="value">{{ userStore.userInfo?.points_balance || 0 }}</span>
            </div>
            <div class="invite">
              <span class="label">邀请码</span>
              <span class="code">{{ userStore.userInfo?.invite_code }}</span>
              <el-button size="small" @click="copyInviteCode">复制</el-button>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="18">
          <el-tabs v-model="activeTab" @tab-change="handleTabChange">
            <el-tab-pane label="积分明细" name="points">
              <el-table :data="records" v-loading="loading">
                <el-table-column prop="remark" label="说明" />
                <el-table-column prop="points" label="积分" width="120">
                  <template #default="{ row }">
                    <span :style="{ color: row.points > 0 ? '#52c41a' : '#ff4d4f' }">
                      {{ row.points > 0 ? '+' : '' }}{{ row.points }}
                    </span>
                  </template>
                </el-table-column>
                <el-table-column prop="created_at" label="时间" width="180">
                  <template #default="{ row }">
                    {{ formatDate(row.created_at) }}
                  </template>
                </el-table-column>
              </el-table>
            </el-tab-pane>
            
            <el-tab-pane label="我的订单" name="orders">
              <div class="filter-bar">
                <el-radio-group v-model="orderStatus" @change="fetchRecords" size="small">
                  <el-radio-button label="">全部</el-radio-button>
                  <el-radio-button label="pending">待发货</el-radio-button>
                  <el-radio-button label="shipped">已发货</el-radio-button>
                  <el-radio-button label="completed">已完成</el-radio-button>
                </el-radio-group>
              </div>
              <el-table :data="records" v-loading="loading">
                <el-table-column prop="order_no" label="订单号" width="180" />
                <el-table-column prop="product_name" label="商品名称" />
                <el-table-column prop="points_cost" label="消耗积分" width="120" />
                <el-table-column prop="status" label="状态" width="100">
                  <template #default="{ row }">
                    <el-tag :type="statusType[row.status]">
                      {{ statusText[row.status] }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="发货信息" min-width="200">
                  <template #default="{ row }">
                    <template v-if="row.status !== 'pending' && row.shipping_info">
                      <!-- 虚拟商品 -->
                      <template v-if="row.product_type === 'virtual'">
                        <div v-if="row.shipping_info.code" class="shipping-info">
                          <span class="label">卡密：</span>
                          <span class="code">{{ row.shipping_info.code }}</span>
                          <el-button type="primary" link size="small" @click="copyText(row.shipping_info.code)">复制</el-button>
                        </div>
                        <div v-if="row.shipping_info.instructions" class="shipping-info">
                          <span class="label">说明：</span>
                          <span>{{ row.shipping_info.instructions }}</span>
                        </div>
                      </template>
                      <!-- 实物商品 -->
                      <template v-else>
                        <div v-if="row.shipping_info.company" class="shipping-info">
                          <span class="label">快递：</span>
                          <span>{{ row.shipping_info.company }}</span>
                        </div>
                        <div v-if="row.shipping_info.tracking_no" class="shipping-info">
                          <span class="label">单号：</span>
                          <span class="code">{{ row.shipping_info.tracking_no }}</span>
                          <el-button type="primary" link size="small" @click="copyText(row.shipping_info.tracking_no)">复制</el-button>
                        </div>
                      </template>
                    </template>
                    <span v-else style="color: #999;">{{ row.status === 'pending' ? '待发货' : '-' }}</span>
                  </template>
                </el-table-column>
                <el-table-column prop="created_at" label="时间" width="180">
                  <template #default="{ row }">
                    {{ formatDate(row.created_at) }}
                  </template>
                </el-table-column>
              </el-table>
            </el-tab-pane>
            
            <el-tab-pane label="活动提交" name="submissions">
              <div class="filter-bar">
                <el-radio-group v-model="submissionStatus" @change="fetchRecords" size="small">
                  <el-radio-button label="">全部</el-radio-button>
                  <el-radio-button label="pending">审核中</el-radio-button>
                  <el-radio-button label="approved">已通过</el-radio-button>
                  <el-radio-button label="rejected">未通过</el-radio-button>
                </el-radio-group>
              </div>
              <el-table :data="records" v-loading="loading">
                <el-table-column prop="id" label="ID" width="80" />
                <el-table-column prop="activity_title" label="活动名称" min-width="150" />
                <el-table-column prop="created_at" label="提交时间" width="180">
                  <template #default="{ row }">
                    {{ formatDate(row.created_at) }}
                  </template>
                </el-table-column>
                <el-table-column label="附件" width="120">
                  <template #default="{ row }">
                    <template v-if="row.attachments && row.attachments.length > 0">
                      <el-button type="primary" link @click="previewAttachments(row.attachments)">
                        查看({{ row.attachments.length }})
                      </el-button>
                    </template>
                    <span v-else style="color: #999;">无</span>
                  </template>
                </el-table-column>
                <el-table-column prop="status" label="审核状态" width="100">
                  <template #default="{ row }">
                    <el-tag :type="submissionType[row.status]">
                      {{ submissionText[row.status] }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="granted_points" label="获得积分" width="100">
                  <template #default="{ row }">
                    <span v-if="row.status === 'approved'" style="color: #52c41a;">
                      +{{ row.granted_points }}
                    </span>
                    <span v-else>-</span>
                  </template>
                </el-table-column>
              </el-table>
            </el-tab-pane>
          </el-tabs>
        </el-col>
      </el-row>
    </div>
    
    <!-- 附件预览弹窗 -->
    <el-dialog v-model="previewVisible" title="附件预览" width="600px">
      <div class="attachments-preview">
        <el-image
          v-for="(url, index) in previewImages"
          :key="index"
          :src="url"
          :preview-src-list="previewImages"
          :initial-index="index"
          fit="contain"
          style="width: 150px; height: 150px; margin: 8px;"
        />
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const userStore = useUserStore()
const activeTab = ref('points')
const loading = ref(false)
const records = ref([])
const previewVisible = ref(false)
const previewImages = ref([])
const orderStatus = ref('')
const submissionStatus = ref('')

const statusText = { pending: '待发货', shipped: '已发货', completed: '已完成' }
const statusType = { pending: 'warning', shipped: 'success', completed: 'info' }
const submissionText = { pending: '审核中', approved: '已通过', rejected: '未通过' }
const submissionType = { pending: 'warning', approved: 'success', rejected: 'danger' }

const formatPhone = (phone) => {
  if (!phone) return ''
  return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
}

const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleString('zh-CN')
}

const fetchRecords = async () => {
  loading.value = true
  try {
    const params = { type: activeTab.value }
    if (activeTab.value === 'orders' && orderStatus.value) {
      params.status = orderStatus.value
    }
    if (activeTab.value === 'submissions' && submissionStatus.value) {
      params.status = submissionStatus.value
    }
    const res = await request.get('/user/records', { params })
    let items = res.data?.[activeTab.value]?.items || []
    // 解析shipping_info JSON
    if (activeTab.value === 'orders') {
      items = items.map(item => ({
        ...item,
        shipping_info: typeof item.shipping_info === 'string' ? JSON.parse(item.shipping_info || '{}') : (item.shipping_info || {})
      }))
    }
    records.value = items
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const copyText = (text) => {
  navigator.clipboard.writeText(text)
  ElMessage.success('已复制')
}

const handleTabChange = () => {
  orderStatus.value = ''
  submissionStatus.value = ''
  fetchRecords()
}

const copyInviteCode = () => {
  const code = userStore.userInfo?.invite_code
  if (!code) return
  navigator.clipboard.writeText(code)
  ElMessage.success('邀请码已复制')
}

const previewAttachments = (attachments) => {
  previewImages.value = attachments
  previewVisible.value = true
}

onMounted(() => {
  userStore.fetchUserInfo()
  fetchRecords()
})
</script>

<style lang="scss" scoped>
.user-page {
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
}

.user-card {
  text-align: center;
  background: white;
  border-radius: 16px;
  padding: 32px 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  
  .avatar {
    width: 80px;
    height: 80px;
    background: linear-gradient(135deg, #F5A623 0%, #FF8C00 100%);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 40px;
    margin: 0 auto 16px;
    color: white;
  }
  
  .phone {
    font-size: 18px;
    font-weight: 600;
    color: #333;
    margin-bottom: 24px;
  }
  
  .points {
    padding: 24px;
    background: linear-gradient(135deg, #FFF9F0 0%, #FFF5E6 100%);
    border-radius: 12px;
    margin-bottom: 24px;
    border: 2px solid #F5A623;
    
    .label {
      display: block;
      font-size: 14px;
      color: #999;
      margin-bottom: 8px;
    }
    
    .value {
      display: block;
      font-size: 36px;
      font-weight: 700;
      color: #F5A623;
    }
  }
  
  .invite {
    padding: 16px;
    background: #FAFAFA;
    border-radius: 8px;
    
    .label {
      display: block;
      font-size: 12px;
      color: #999;
      margin-bottom: 8px;
    }
    
    .code {
      display: block;
      font-size: 20px;
      font-weight: 600;
      color: #F5A623;
      margin-bottom: 12px;
      letter-spacing: 2px;
    }
    
    .el-button {
      width: 100%;
      background: #F5A623;
      border: none;
      color: white;
      
      &:hover {
        background: #E09612;
      }
    }
  }
}

:deep(.el-tabs) {
  .el-tabs__header {
    background: white;
    border-radius: 16px 16px 0 0;
    padding: 0 24px;
    margin-bottom: 0;
  }
  
  .el-tabs__nav-wrap {
    &::after {
      background: #F0F0F0;
    }
  }
  
  .el-tabs__item {
    font-size: 16px;
    font-weight: 500;
    color: #666;
    
    &.is-active {
      color: #F5A623;
    }
    
    &:hover {
      color: #F5A623;
    }
  }
  
  .el-tabs__active-bar {
    background: #F5A623;
  }
  
  .el-tabs__content {
    background: white;
    border-radius: 0 0 16px 16px;
    padding: 24px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  }
  
  .el-table {
    .el-table__header {
      th {
        background: #FAFAFA;
        color: #333;
        font-weight: 600;
      }
    }
  }
  
  .filter-bar {
    margin-bottom: 16px;
    
    .el-radio-button__inner {
      border-color: #dcdfe6;
    }
    
    .el-radio-button__original-radio:checked + .el-radio-button__inner {
      background-color: #F5A623;
      border-color: #F5A623;
    }
  }
}

.shipping-info {
  font-size: 13px;
  line-height: 1.8;
  
  .label {
    color: #999;
  }
  
  .code {
    color: #F5A623;
    font-weight: 500;
    margin-right: 8px;
  }
}
</style>
