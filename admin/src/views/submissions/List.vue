<template>
  <div class="submissions-page">
    <div class="page-card">
      <div class="filter-tabs">
        <el-radio-group v-model="filters.status" @change="fetchData">
          <el-radio-button label="">全部</el-radio-button>
          <el-radio-button label="pending">待审核</el-radio-button>
          <el-radio-button label="approved">已通过</el-radio-button>
          <el-radio-button label="rejected">已拒绝</el-radio-button>
        </el-radio-group>
      </div>

      <el-table :data="submissions" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="activity_title" label="活动" min-width="150" />
        <el-table-column label="提交内容" min-width="200">
          <template #default="{ row }">
            <el-button type="primary" link @click="showDetail(row)">
              查看详情
            </el-button>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusType[row.status]">{{ statusText[row.status] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="granted_points" label="发放积分" width="100" />
        <el-table-column prop="created_at" label="提交时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <div class="table-actions" v-if="row.status === 'pending'">
              <el-button type="success" link @click="handleAudit(row, 'approved')">
                通过
              </el-button>
              <el-button type="danger" link @click="handleAudit(row, 'rejected')">
                拒绝
              </el-button>
            </div>
            <span v-else class="text-muted">已处理</span>
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

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailVisible" title="提交详情" width="600px">
      <div class="audit-detail" v-if="currentItem">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="活动">{{ currentItem.activity_title }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="statusType[currentItem.status]">{{ statusText[currentItem.status] }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="提交时间">{{ formatDate(currentItem.created_at) }}</el-descriptions-item>
        </el-descriptions>
        
        <h4 style="margin: 20px 0 12px;">提交数据</h4>
        <div class="submission-data" v-if="currentItem.submission_data">
          <div class="data-item" v-for="(value, key) in currentItem.submission_data" :key="key">
            <span class="label">{{ key }}:</span>
            <span class="value">
              <template v-if="isImageUrl(value)">
                <el-image :src="value" :preview-src-list="[value]" style="width: 100px; height: 100px;" fit="cover" />
              </template>
              <template v-else>{{ value }}</template>
            </span>
          </div>
        </div>
        <div v-else style="color: #909399;">无提交数据</div>
        
        <h4 style="margin: 20px 0 12px;">附件</h4>
        <div class="attachments-preview" v-if="currentItem.attachments && currentItem.attachments.length > 0">
          <el-image
            v-for="(url, index) in currentItem.attachments"
            :key="index"
            :src="url"
            :preview-src-list="currentItem.attachments"
            :initial-index="index"
            style="width: 100px; height: 100px; margin-right: 8px;"
            fit="cover"
          />
        </div>
        <div v-else style="color: #909399;">无附件</div>
      </div>
    </el-dialog>

    <!-- 审核弹窗 -->
    <el-dialog v-model="auditVisible" :title="auditStatus === 'approved' ? '审核通过' : '审核拒绝'" width="400px">
      <el-form :model="auditForm" label-width="80px">
        <el-form-item label="积分" v-if="auditStatus === 'approved'">
          <el-input-number v-model="auditForm.points" :min="0" :max="100000" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="auditForm.remark" type="textarea" :rows="3" placeholder="审核备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="auditVisible = false">取消</el-button>
        <el-button type="primary" @click="submitAudit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/utils/api'
import dayjs from 'dayjs'

const loading = ref(false)
const submitting = ref(false)
const submissions = ref([])

const filters = reactive({
  status: 'pending'
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const detailVisible = ref(false)
const auditVisible = ref(false)
const currentItem = ref(null)
const auditStatus = ref('')

const auditForm = reactive({
  points: 0,
  remark: ''
})

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

const isImageUrl = (value) => {
  if (typeof value !== 'string') return false
  return /\.(jpg|jpeg|png|gif|webp)$/i.test(value) || value.includes('cos.') || value.includes('oss.')
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await api.get('/admin/submissions', {
      params: {
        status: filters.status || undefined,
        page: pagination.page,
        page_size: pagination.pageSize
      }
    })
    submissions.value = res.data.items
    pagination.total = res.data.total
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const showDetail = (row) => {
  currentItem.value = row
  detailVisible.value = true
}

const handleAudit = (row, status) => {
  currentItem.value = row
  auditStatus.value = status
  auditForm.points = 0
  auditForm.remark = ''
  auditVisible.value = true
}

const submitAudit = async () => {
  submitting.value = true
  try {
    await api.post(`/admin/submissions/${currentItem.value.id}/audit`, {
      status: auditStatus.value,
      points: auditStatus.value === 'approved' ? auditForm.points : undefined,
      remark: auditForm.remark
    })
    
    ElMessage.success('审核成功')
    auditVisible.value = false
    fetchData()
  } catch (error) {
    console.error(error)
  } finally {
    submitting.value = false
  }
}

onMounted(fetchData)
</script>

<style lang="scss" scoped>
.filter-tabs {
  margin-bottom: 20px;
}

.text-muted {
  color: #909399;
}
</style>
