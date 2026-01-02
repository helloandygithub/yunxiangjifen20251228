<template>
  <div class="activities-page">
    <div class="page-card">
      <div class="page-header">
        <div class="filter-tabs">
          <el-radio-group v-model="filters.status" @change="fetchData">
            <el-radio-button label="">全部</el-radio-button>
            <el-radio-button label="draft">草稿</el-radio-button>
            <el-radio-button label="active">进行中</el-radio-button>
            <el-radio-button label="ended">已结束</el-radio-button>
          </el-radio-group>
        </div>
        <el-button type="primary" :icon="Plus" @click="$router.push('/activities/create')">
          创建活动
        </el-button>
      </div>

      <el-table :data="activities" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="活动名称" min-width="200" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusType[row.status]">{{ statusText[row.status] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="audit_type" label="审核类型" width="100">
          <template #default="{ row }">
            {{ row.audit_type === 'auto' ? '自动' : '人工' }}
          </template>
        </el-table-column>
        <el-table-column prop="reward_points" label="奖励积分" width="100" />
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <div class="table-actions">
              <el-button type="primary" link @click="$router.push(`/activities/${row.id}/edit`)">
                编辑
              </el-button>
              <el-button 
                v-if="row.status === 'draft'" 
                type="success" 
                link 
                @click="updateStatus(row, 'active')"
              >
                上线
              </el-button>
              <el-button 
                v-if="row.status === 'active'" 
                type="warning" 
                link 
                @click="updateStatus(row, 'ended')"
              >
                结束
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @size-change="fetchData"
          @current-change="fetchData"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/utils/api'
import dayjs from 'dayjs'

const loading = ref(false)
const activities = ref([])

const filters = reactive({
  status: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const statusType = {
  draft: 'info',
  active: 'success',
  ended: 'warning'
}

const statusText = {
  draft: '草稿',
  active: '进行中',
  ended: '已结束'
}

const formatDate = (date) => dayjs(date).format('YYYY-MM-DD HH:mm')

const fetchData = async () => {
  loading.value = true
  try {
    const res = await api.get('/admin/activities', {
      params: {
        status: filters.status || undefined,
        page: pagination.page,
        page_size: pagination.pageSize
      }
    })
    activities.value = res.data.items
    pagination.total = res.data.total
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const updateStatus = async (row, status) => {
  const statusLabel = status === 'active' ? '上线' : '结束'
  
  try {
    await ElMessageBox.confirm(
      `确定要${statusLabel}活动「${row.title}」吗？`,
      '提示',
      { type: 'warning' }
    )
    
    await api.put(`/admin/activities/${row.id}`, { status })
    ElMessage.success(`${statusLabel}成功`)
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error)
    }
  }
}

onMounted(fetchData)
</script>

<style lang="scss" scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.filter-tabs {
  flex: 1;
}
</style>
