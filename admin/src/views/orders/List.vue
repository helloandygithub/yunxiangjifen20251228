<template>
  <div class="orders-page">
    <div class="page-card">
      <div class="filter-tabs">
        <el-radio-group v-model="filters.status" @change="fetchData">
          <el-radio-button label="">全部</el-radio-button>
          <el-radio-button label="pending">待发货</el-radio-button>
          <el-radio-button label="shipped">已发货</el-radio-button>
          <el-radio-button label="completed">已完成</el-radio-button>
        </el-radio-group>
      </div>

      <el-table :data="orders" v-loading="loading" style="width: 100%">
        <el-table-column prop="order_no" label="订单号" width="200" />
        <el-table-column prop="product_name" label="商品" min-width="150" />
        <el-table-column prop="quantity" label="数量" width="80" />
        <el-table-column prop="points_cost" label="消耗积分" width="100" />
        <el-table-column label="收货信息" min-width="200">
          <template #default="{ row }">
            <template v-if="row.delivery_info">
              <div>{{ row.delivery_info.name }} {{ row.delivery_info.phone }}</div>
              <div class="text-muted">{{ row.delivery_info.address }}</div>
            </template>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusType[row.status]">{{ statusText[row.status] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="下单时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button 
              v-if="row.status === 'pending'" 
              type="primary" 
              link 
              @click="openDeliverDialog(row)"
            >
              发货
            </el-button>
            <el-button 
              v-else-if="row.shipping_info" 
              type="info" 
              link 
              @click="showShippingInfo(row)"
            >
              查看
            </el-button>
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

    <!-- 发货弹窗 -->
    <el-dialog v-model="deliverVisible" title="订单发货" width="500px">
      <el-form ref="formRef" :model="deliverForm" label-width="100px">
        <el-alert 
          v-if="currentOrder?.product_type === 'virtual'" 
          title="虚拟商品请填写卡密或兑换码"
          type="info"
          :closable="false"
          style="margin-bottom: 20px;"
        />
        <el-form-item label="物流公司" v-if="currentOrder?.product_type !== 'virtual'">
          <el-input v-model="deliverForm.carrier" placeholder="如：顺丰、圆通" />
        </el-form-item>
        <el-form-item label="物流单号" v-if="currentOrder?.product_type !== 'virtual'">
          <el-input v-model="deliverForm.tracking_no" placeholder="快递单号" />
        </el-form-item>
        <el-form-item label="卡密/兑换码" v-if="currentOrder?.product_type === 'virtual'">
          <el-input 
            v-model="deliverForm.code" 
            type="textarea" 
            :rows="3" 
            placeholder="虚拟商品兑换码或卡密"
          />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="deliverForm.remark" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="deliverVisible = false">取消</el-button>
        <el-button type="primary" @click="handleDeliver" :loading="submitting">确认发货</el-button>
      </template>
    </el-dialog>

    <!-- 物流信息弹窗 -->
    <el-dialog v-model="shippingVisible" title="发货信息" width="400px">
      <el-descriptions :column="1" border v-if="currentOrder?.shipping_info">
        <el-descriptions-item label="物流公司">
          {{ currentOrder.shipping_info.carrier || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="物流单号">
          {{ currentOrder.shipping_info.tracking_no || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="卡密/兑换码" v-if="currentOrder.shipping_info.code">
          {{ currentOrder.shipping_info.code }}
        </el-descriptions-item>
        <el-descriptions-item label="备注" v-if="currentOrder.shipping_info.remark">
          {{ currentOrder.shipping_info.remark }}
        </el-descriptions-item>
      </el-descriptions>
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
const orders = ref([])
const deliverVisible = ref(false)
const shippingVisible = ref(false)
const currentOrder = ref(null)
const formRef = ref()

const filters = reactive({
  status: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const deliverForm = reactive({
  carrier: '',
  tracking_no: '',
  code: '',
  remark: ''
})

const statusType = {
  pending: 'warning',
  shipped: 'primary',
  completed: 'success',
  cancelled: 'info'
}

const statusText = {
  pending: '待发货',
  shipped: '已发货',
  completed: '已完成',
  cancelled: '已取消'
}

const formatDate = (date) => dayjs(date).format('YYYY-MM-DD HH:mm')

const fetchData = async () => {
  loading.value = true
  try {
    const res = await api.get('/admin/orders', {
      params: {
        status: filters.status || undefined,
        page: pagination.page,
        page_size: pagination.pageSize
      }
    })
    orders.value = res.data.items
    pagination.total = res.data.total
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const openDeliverDialog = (row) => {
  currentOrder.value = row
  Object.assign(deliverForm, {
    carrier: '',
    tracking_no: '',
    code: '',
    remark: ''
  })
  deliverVisible.value = true
}

const showShippingInfo = (row) => {
  currentOrder.value = row
  shippingVisible.value = true
}

const handleDeliver = async () => {
  submitting.value = true
  try {
    await api.post(`/admin/orders/${currentOrder.value.id}/deliver`, {
      shipping_info: {
        carrier: deliverForm.carrier,
        tracking_no: deliverForm.tracking_no,
        code: deliverForm.code,
        remark: deliverForm.remark
      }
    })
    
    ElMessage.success('发货成功')
    deliverVisible.value = false
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
  font-size: 12px;
}
</style>
