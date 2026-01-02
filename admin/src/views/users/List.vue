<template>
  <div class="users-page">
    <div class="page-card">
      <el-form :inline="true" class="search-form">
        <el-form-item label="手机号">
          <el-input v-model="filters.phone" placeholder="搜索手机号" clearable @keyup.enter="fetchData" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchData">搜索</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="users" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="phone" label="手机号" width="150" />
        <el-table-column prop="points_balance" label="积分余额" width="120">
          <template #default="{ row }">
            <span class="points-value">{{ row.points_balance }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="invite_code" label="邀请码" width="120" />
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '正常' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="注册时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <div class="table-actions">
              <el-button type="primary" link @click="showDetail(row)">详情</el-button>
              <el-button type="warning" link @click="adjustPoints(row)">调整积分</el-button>
              <el-button 
                :type="row.is_active ? 'danger' : 'success'" 
                link 
                @click="toggleStatus(row)"
              >
                {{ row.is_active ? '禁用' : '启用' }}
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
          layout="total, prev, pager, next"
          @current-change="fetchData"
        />
      </div>
    </div>

    <!-- 用户详情弹窗 -->
    <el-dialog v-model="detailVisible" title="用户详情" width="600px">
      <el-descriptions :column="2" border v-if="currentUser">
        <el-descriptions-item label="用户ID">{{ currentUser.id }}</el-descriptions-item>
        <el-descriptions-item label="手机号">{{ currentUser.phone }}</el-descriptions-item>
        <el-descriptions-item label="积分余额">{{ currentUser.points_balance }}</el-descriptions-item>
        <el-descriptions-item label="邀请码">{{ currentUser.invite_code }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="currentUser.is_active ? 'success' : 'danger'">
            {{ currentUser.is_active ? '正常' : '禁用' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="注册时间">{{ formatDate(currentUser.created_at) }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>

    <!-- 积分调整弹窗 -->
    <el-dialog v-model="adjustVisible" title="调整积分" width="400px">
      <el-form :model="adjustForm" label-width="80px">
        <el-form-item label="当前积分">
          <span class="points-value">{{ currentUser?.points_balance }}</span>
        </el-form-item>
        <el-form-item label="调整类型">
          <el-radio-group v-model="adjustForm.type">
            <el-radio label="add">增加</el-radio>
            <el-radio label="subtract">扣减</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="积分数量">
          <el-input-number v-model="adjustForm.points" :min="1" :max="1000000" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="adjustForm.remark" type="textarea" :rows="2" placeholder="调整原因" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="adjustVisible = false">取消</el-button>
        <el-button type="primary" @click="submitAdjust" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/utils/api'
import dayjs from 'dayjs'

const loading = ref(false)
const submitting = ref(false)
const users = ref([])
const detailVisible = ref(false)
const adjustVisible = ref(false)
const currentUser = ref(null)

const filters = reactive({
  phone: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const adjustForm = reactive({
  type: 'add',
  points: 0,
  remark: ''
})

const formatDate = (date) => dayjs(date).format('YYYY-MM-DD HH:mm')

const fetchData = async () => {
  loading.value = true
  try {
    const res = await api.get('/admin/users', {
      params: {
        phone: filters.phone || undefined,
        page: pagination.page,
        page_size: pagination.pageSize
      }
    })
    if (res.data) {
      users.value = res.data.items || []
      pagination.total = res.data.total || 0
    }
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const showDetail = (row) => {
  currentUser.value = row
  detailVisible.value = true
}

const adjustPoints = (row) => {
  currentUser.value = row
  Object.assign(adjustForm, {
    type: 'add',
    points: 0,
    remark: ''
  })
  adjustVisible.value = true
}

const submitAdjust = async () => {
  if (!adjustForm.points || adjustForm.points <= 0) {
    ElMessage.warning('请输入有效的积分数量')
    return
  }

  submitting.value = true
  try {
    await api.post(`/admin/users/${currentUser.value.id}/points`, {
      type: adjustForm.type,
      points: adjustForm.points,
      remark: adjustForm.remark
    })
    ElMessage.success('积分调整成功')
    adjustVisible.value = false
    fetchData()
  } catch (error) {
    console.error(error)
    ElMessage.error('积分调整失败')
  } finally {
    submitting.value = false
  }
}

const toggleStatus = async (row) => {
  const action = row.is_active ? '禁用' : '启用'
  
  try {
    await ElMessageBox.confirm(
      `确定要${action}用户 ${row.phone} 吗？`,
      '提示',
      { type: 'warning' }
    )
    
    await api.put(`/admin/users/${row.id}/status`, {
      is_active: !row.is_active
    })
    ElMessage.success(`${action}成功`)
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error)
      ElMessage.error(`${action}失败`)
    }
  }
}

onMounted(fetchData)
</script>

<style lang="scss" scoped>
.points-value {
  color: #e6a23c;
  font-weight: bold;
}
</style>
