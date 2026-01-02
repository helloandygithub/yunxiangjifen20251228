<template>
  <div class="activity-edit">
    <div class="page-card">
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
        v-loading="loading"
      >
        <el-form-item label="活动名称" prop="title">
          <el-input v-model="form.title" placeholder="请输入活动名称" />
        </el-form-item>

        <el-form-item label="活动描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="4"
            placeholder="请输入活动描述"
          />
        </el-form-item>

        <el-form-item label="封面图">
          <el-input v-model="form.cover_image" placeholder="请输入图片URL" />
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="审核类型" prop="audit_type">
              <el-select v-model="form.audit_type" style="width: 100%;">
                <el-option label="自动审核" value="auto" />
                <el-option label="人工审核" value="manual" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="参与频次" prop="frequency_type">
              <el-select v-model="form.frequency_type" style="width: 100%;">
                <el-option label="终身一次" value="once" />
                <el-option label="每日限次" value="daily" />
                <el-option label="不限次数" value="unlimited" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="每日最大次数" v-if="form.frequency_type === 'daily'">
              <el-input-number v-model="form.max_participations" :min="1" :max="100" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="奖励积分" prop="reward_points">
          <el-input-number v-model="form.reward_points" :min="0" :max="100000" />
          <span style="margin-left: 12px; color: #909399;">设为0则由审核时手动输入</span>
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="开始时间">
              <el-date-picker
                v-model="form.start_time"
                type="datetime"
                placeholder="选择开始时间"
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束时间">
              <el-date-picker
                v-model="form.end_time"
                type="datetime"
                placeholder="选择结束时间"
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider>动态表单配置</el-divider>

        <div class="form-schema-editor">
          <div v-for="(field, index) in form.form_schema" :key="index" class="field-item">
            <div class="field-header">
              <span class="field-title">字段 {{ index + 1 }}</span>
              <el-button type="danger" link @click="removeField(index)">
                <el-icon><Delete /></el-icon> 删除
              </el-button>
            </div>
            <div class="field-content">
              <el-form-item label="字段名" label-width="80px">
                <el-input v-model="field.key" placeholder="英文标识，如 order_no" />
              </el-form-item>
              <el-form-item label="显示名" label-width="80px">
                <el-input v-model="field.label" placeholder="中文名称" />
              </el-form-item>
              <el-form-item label="类型" label-width="80px">
                <el-select v-model="field.type" style="width: 100%;">
                  <el-option label="文本" value="text" />
                  <el-option label="多行文本" value="textarea" />
                  <el-option label="图片" value="image" />
                  <el-option label="文件" value="file" />
                  <el-option label="数字" value="number" />
                  <el-option label="下拉选择" value="select" />
                  <el-option label="日期" value="date" />
                </el-select>
              </el-form-item>
              <el-form-item label="必填" label-width="80px">
                <el-switch v-model="field.required" />
              </el-form-item>
            </div>
          </div>

          <el-button type="primary" plain @click="addField">
            <el-icon><Plus /></el-icon> 添加字段
          </el-button>
        </div>

        <el-form-item style="margin-top: 40px;">
          <el-button type="primary" size="large" @click="handleSubmit" :loading="submitting">
            {{ isEdit ? '保存修改' : '创建活动' }}
          </el-button>
          <el-button size="large" @click="$router.back()">返回</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus, Delete } from '@element-plus/icons-vue'
import api from '@/utils/api'

const route = useRoute()
const router = useRouter()

const formRef = ref()
const loading = ref(false)
const submitting = ref(false)

const isEdit = computed(() => !!route.params.id)

const form = reactive({
  title: '',
  description: '',
  cover_image: '',
  audit_type: 'manual',
  frequency_type: 'once',
  max_participations: 1,
  reward_points: 0,
  start_time: null,
  end_time: null,
  form_schema: [
    { key: 'order_no', label: '订单号', type: 'text', required: true }
  ]
})

const rules = {
  title: [{ required: true, message: '请输入活动名称', trigger: 'blur' }],
  audit_type: [{ required: true, message: '请选择审核类型', trigger: 'change' }],
  frequency_type: [{ required: true, message: '请选择参与频次', trigger: 'change' }]
}

const addField = () => {
  form.form_schema.push({
    key: '',
    label: '',
    type: 'text',
    required: false
  })
}

const removeField = (index) => {
  form.form_schema.splice(index, 1)
}

const fetchActivity = async () => {
  if (!route.params.id) return
  
  loading.value = true
  try {
    const res = await api.get(`/admin/activities`, { params: { page: 1, page_size: 100 } })
    const activity = res.data.items.find(a => a.id === parseInt(route.params.id))
    if (activity) {
      Object.assign(form, activity)
    }
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    submitting.value = true

    const data = { ...form }
    
    if (isEdit.value) {
      await api.put(`/admin/activities/${route.params.id}`, data)
      ElMessage.success('保存成功')
    } else {
      await api.post('/admin/activities', data)
      ElMessage.success('创建成功')
    }
    
    router.push('/activities')
  } catch (error) {
    console.error(error)
  } finally {
    submitting.value = false
  }
}

onMounted(fetchActivity)
</script>

<style lang="scss" scoped>
.activity-edit {
  max-width: 900px;
}
</style>
