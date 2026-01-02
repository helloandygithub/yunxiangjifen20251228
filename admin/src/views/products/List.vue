<template>
  <div class="products-page">
    <div class="page-card">
      <div class="page-header">
        <h3>商品列表</h3>
        <el-button type="primary" :icon="Plus" @click="openDialog()">添加商品</el-button>
      </div>

      <el-table :data="products" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="图片" width="100">
          <template #default="{ row }">
            <el-image v-if="row.image_url" :src="row.image_url" :preview-src-list="[row.image_url]" style="width: 60px; height: 60px;" fit="cover" />
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="商品名称" min-width="150" />
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.type === 'virtual' ? 'success' : 'primary'">
              {{ row.type === 'virtual' ? '虚拟' : '实物' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="price_points" label="所需积分" width="100" />
        <el-table-column prop="stock" label="库存" width="100" />
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">
              {{ row.is_active ? '上架' : '下架' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <div class="table-actions">
              <el-button type="primary" link @click="openDialog(row)">编辑</el-button>
              <el-button type="warning" link @click="toggleStatus(row)">
                {{ row.is_active ? '下架' : '上架' }}
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

    <!-- 编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑商品' : '添加商品'" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="商品名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入商品名称" />
        </el-form-item>
        <el-form-item label="商品描述">
          <el-input v-model="form.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="商品类型" prop="type">
          <el-select v-model="form.type" style="width: 100%;">
            <el-option label="虚拟商品" value="virtual" />
            <el-option label="实物商品" value="physical" />
          </el-select>
        </el-form-item>
        <el-form-item label="所需积分" prop="price_points">
          <el-input-number v-model="form.price_points" :min="1" :max="1000000" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="库存" prop="stock">
          <el-input-number v-model="form.stock" :min="0" :max="1000000" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="图片URL">
          <el-input v-model="form.image_url" placeholder="商品图片链接" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort_order" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '@/utils/api'

const loading = ref(false)
const submitting = ref(false)
const products = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const currentId = ref(null)
const formRef = ref()

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const form = reactive({
  name: '',
  description: '',
  type: 'virtual',
  price_points: 100,
  stock: 0,
  image_url: '',
  sort_order: 0
})

const rules = {
  name: [{ required: true, message: '请输入商品名称', trigger: 'blur' }],
  type: [{ required: true, message: '请选择商品类型', trigger: 'change' }],
  price_points: [{ required: true, message: '请输入所需积分', trigger: 'blur' }]
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await api.get('/mall/products', {
      params: { page: pagination.page, page_size: pagination.pageSize }
    })
    products.value = res.data.items
    pagination.total = res.data.total
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const openDialog = (row = null) => {
  isEdit.value = !!row
  currentId.value = row?.id || null
  
  if (row) {
    Object.assign(form, row)
  } else {
    Object.assign(form, {
      name: '',
      description: '',
      type: 'virtual',
      price_points: 100,
      stock: 0,
      image_url: '',
      sort_order: 0
    })
  }
  
  dialogVisible.value = true
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    submitting.value = true
    
    if (isEdit.value) {
      await api.put(`/admin/products/${currentId.value}`, form)
      ElMessage.success('更新成功')
    } else {
      await api.post('/admin/products', form)
      ElMessage.success('添加成功')
    }
    
    dialogVisible.value = false
    fetchData()
  } catch (error) {
    console.error(error)
  } finally {
    submitting.value = false
  }
}

const toggleStatus = async (row) => {
  try {
    await api.put(`/admin/products/${row.id}`, {
      ...row,
      is_active: !row.is_active
    })
    ElMessage.success(row.is_active ? '已下架' : '已上架')
    await fetchData()
  } catch (error) {
    console.error(error)
    ElMessage.error('操作失败')
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
  
  h3 {
    margin: 0;
  }
}
</style>
