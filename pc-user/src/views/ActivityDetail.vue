<template>
  <div class="activity-detail-page">
    <div class="container" v-loading="loading">
      <div v-if="activity" class="detail-content">
        <!-- 面包屑导航 -->
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item :to="{ path: '/activities' }">活动专区</el-breadcrumb-item>
            <el-breadcrumb-item>活动详情</el-breadcrumb-item>
          </el-breadcrumb>
        </div>

        <!-- 活动头部信息 -->
        <div class="activity-header">
          <div class="header-left">
            <div class="activity-cover">
              <img v-if="activity.cover_image" :src="activity.cover_image" />
              <div v-else class="cover-placeholder">
                <div class="placeholder-icon">🎯</div>
              </div>
              <el-tag class="status-tag">{{ activity.status || '进行中' }}</el-tag>
            </div>
          </div>
          
          <div class="header-right">
            <div class="category-tag">{{ activity.category || '云服务器' }}</div>
            <h1 class="activity-title">{{ activity.title }}</h1>
            <p class="activity-desc">{{ activity.description }}</p>
            
            <div class="activity-stats">
              <div class="stat-item">
                <el-icon class="stat-icon"><Coin /></el-icon>
                <div class="stat-info">
                  <div class="stat-label">奖励积分</div>
                  <div class="stat-value">+{{ activity.reward_points || 500 }}</div>
                </div>
              </div>
              <div class="stat-item">
                <el-icon class="stat-icon"><User /></el-icon>
                <div class="stat-info">
                  <div class="stat-label">参与人数</div>
                  <div class="stat-value">{{ activity.participant_count || 0 }}人</div>
                </div>
              </div>
              <div class="stat-item">
                <el-icon class="stat-icon"><Clock /></el-icon>
                <div class="stat-info">
                  <div class="stat-label">活动时间</div>
                  <div class="stat-value">长期有效</div>
                </div>
              </div>
            </div>
            
            <el-button type="primary" size="large" class="participate-btn" @click="handleParticipate">
              立即参与
              <el-icon><ArrowRight /></el-icon>
            </el-button>
          </div>
        </div>

        <!-- 活动详情 -->
        <div class="activity-body">
          <div class="main-content">
            <!-- 活动说明 -->
            <div class="section-card">
              <h2 class="section-title">活动说明</h2>
              <div class="section-content">
                <p>{{ activity.description }}</p>
                <p>参与本活动，成功推荐企业客户购买相关产品后，即可获得丰厚积分奖励。积分可用于兑换各类数码产品和礼品。</p>
              </div>
            </div>

            <!-- 参与流程 -->
            <div class="section-card">
              <h2 class="section-title">参与流程</h2>
              <div class="steps">
                <div class="step-item">
                  <div class="step-number">1</div>
                  <div class="step-content">
                    <h3>填写推广信息</h3>
                    <p>填写企业客户信息和推广详情</p>
                  </div>
                </div>
                <div class="step-item">
                  <div class="step-number">2</div>
                  <div class="step-content">
                    <h3>等待审核</h3>
                    <p>我们会在3个工作日内完成审核</p>
                  </div>
                </div>
                <div class="step-item">
                  <div class="step-number">3</div>
                  <div class="step-content">
                    <h3>获得积分</h3>
                    <p>审核通过后积分自动发放到账户</p>
                  </div>
                </div>
              </div>
            </div>

          </div>

          <!-- 侧边栏 -->
          <div class="sidebar">
            <!-- 相关活动 -->
            <div class="sidebar-card">
              <h3 class="sidebar-title">相关活动</h3>
              <div class="related-activities">
                <div class="related-item" v-for="i in 3" :key="i" @click="$router.push('/activities')">
                  <div class="related-cover"></div>
                  <div class="related-info">
                    <div class="related-name">推广活动 {{ i }}</div>
                    <div class="related-points">+500 积分</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 活动规则 -->
            <div class="sidebar-card">
              <h3 class="sidebar-title">活动规则</h3>
              <div class="rules-content">
                <p>1. 推广信息需真实有效</p>
                <p>2. 审核通过后积分自动发放</p>
                <p>3. 每个活动每月最多参与5次</p>
                <p>4. 积分有效期为1年</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 参与表单弹窗 -->
    <el-dialog 
      v-model="formDialogVisible" 
      title="填写参与信息" 
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form :model="formData" ref="formRef" label-width="100px" class="participate-form">
        <el-form-item
          v-for="field in activity?.form_schema"
          :key="field.key"
          :label="field.label"
          :required="field.required"
        >
          <el-input
            v-if="field.type === 'text'"
            v-model="formData[field.key]"
            :placeholder="field.placeholder || `请输入${field.label}`"
          />
          <el-input
            v-else-if="field.type === 'textarea'"
            v-model="formData[field.key]"
            type="textarea"
            :rows="3"
            :placeholder="field.placeholder || `请输入${field.label}`"
          />
          <el-input-number
            v-else-if="field.type === 'number'"
            v-model="formData[field.key]"
            :placeholder="field.placeholder || `请输入${field.label}`"
            style="width: 100%"
          />
          <el-upload
            v-else-if="field.type === 'image'"
            action="#"
            :auto-upload="false"
            :on-change="(file) => handleImageChange(file, field.key)"
            :show-file-list="false"
            class="image-uploader"
          >
            <img v-if="formData[field.key]" :src="formData[field.key]" class="upload-preview" />
            <div v-else class="upload-placeholder">
              <el-icon><Plus /></el-icon>
              <span>点击上传{{ field.label }}</span>
            </div>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          提交参与
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Coin, User, Clock, ArrowRight, Plus } from '@element-plus/icons-vue'
import request from '@/utils/request'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const loading = ref(true)
const submitting = ref(false)
const activity = ref(null)
const formData = reactive({})
const formRef = ref()
const formDialogVisible = ref(false)

const fetchActivity = async () => {
  loading.value = true
  try {
    const res = await request.get(`/activities/${route.params.id}`)
    activity.value = res.data
    
    if (activity.value.form_schema) {
      activity.value.form_schema.forEach(field => {
        formData[field.key] = ''
      })
    }
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 点击参与活动
const handleParticipate = async () => {
  // 检查登录状态
  if (!userStore.isLoggedIn) {
    try {
      await ElMessageBox.confirm('请先登录后再参与活动', '提示', {
        confirmButtonText: '去登录',
        cancelButtonText: '取消'
      })
      router.push('/login')
    } catch {}
    return
  }
  
  // 如果活动有表单，弹出表单弹窗
  if (activity.value.form_schema && activity.value.form_schema.length > 0) {
    // 重置表单数据
    activity.value.form_schema.forEach(field => {
      formData[field.key] = ''
    })
    formDialogVisible.value = true
  } else {
    // 没有表单，直接提交参与
    await submitParticipation()
  }
}

// 提交参与（无表单情况）
const submitParticipation = async () => {
  submitting.value = true
  try {
    await request.post(`/activities/${route.params.id}/submit`, {
      activity_id: activity.value.id,
      activity_name: activity.value.title
    })
    ElMessage.success('参与成功！')
    router.push('/user?tab=submissions')
  } catch (error) {
    console.error(error)
    ElMessage.error('参与失败，请重试')
  } finally {
    submitting.value = false
  }
}

const handleImageChange = (file, key) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    formData[key] = e.target.result
  }
  reader.readAsDataURL(file.raw)
}

const validateForm = () => {
  if (!activity.value.form_schema) return true
  
  for (const field of activity.value.form_schema) {
    if (field.required && !formData[field.key]) {
      ElMessage.error(`请填写${field.label}`)
      return false
    }
  }
  return true
}

// 提交表单（有表单情况）
const handleSubmit = async () => {
  if (!validateForm()) return
  
  submitting.value = true
  try {
    // 收集附件（图片类型字段）
    const attachments = []
    activity.value.form_schema.forEach(field => {
      if (field.type === 'image' && formData[field.key]) {
        attachments.push(formData[field.key])
      }
    })
    
    await request.post(`/activities/${route.params.id}/submit`, {
      activity_id: activity.value.id,
      activity_name: activity.value.title,
      submission_data: formData,
      attachments: attachments
    })
    
    formDialogVisible.value = false
    ElMessage.success('提交成功！审核通过后积分将自动发放')
    router.push('/user?tab=submissions')
  } catch (error) {
    console.error(error)
    ElMessage.error('提交失败，请重试')
  } finally {
    submitting.value = false
  }
}

onMounted(fetchActivity)
</script>

<style lang="scss" scoped>
.activity-detail-page {
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
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  }
}

.activity-header {
  display: flex;
  gap: 40px;
  padding: 40px;
  background: linear-gradient(135deg, #FFF9F0 0%, #FFFBF5 100%);
  
  .header-left {
    .activity-cover {
      width: 400px;
      height: 300px;
      border-radius: 16px;
      overflow: hidden;
      position: relative;
      background: linear-gradient(135deg, #FFB84D 0%, #F5A623 100%);
      box-shadow: 0 4px 20px rgba(245, 166, 35, 0.2);
      
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
          font-size: 100px;
          opacity: 0.3;
        }
      }
      
      .status-tag {
        position: absolute;
        top: 16px;
        left: 16px;
        background: #52C41A;
        border: none;
        color: white;
        font-weight: 500;
        padding: 6px 16px;
      }
    }
  }
  
  .header-right {
    flex: 1;
    
    .category-tag {
      display: inline-block;
      padding: 6px 16px;
      background: #FFF4E6;
      color: #F5A623;
      border-radius: 6px;
      font-size: 14px;
      font-weight: 500;
      margin-bottom: 16px;
    }
    
    .activity-title {
      font-size: 32px;
      font-weight: 700;
      color: #333;
      margin-bottom: 16px;
      line-height: 1.4;
    }
    
    .activity-desc {
      font-size: 16px;
      color: #666;
      line-height: 1.8;
      margin-bottom: 32px;
    }
    
    .activity-stats {
      display: flex;
      gap: 32px;
      margin-bottom: 32px;
      
      .stat-item {
        display: flex;
        align-items: center;
        gap: 12px;
        
        .stat-icon {
          width: 48px;
          height: 48px;
          background: #FFF4E6;
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 24px;
          color: #F5A623;
        }
        
        .stat-info {
          .stat-label {
            font-size: 14px;
            color: #999;
            margin-bottom: 4px;
          }
          
          .stat-value {
            font-size: 20px;
            font-weight: 600;
            color: #333;
          }
        }
      }
    }
    
    .participate-btn {
      background: #F5A623;
      border: none;
      color: white;
      padding: 12px 32px;
      font-size: 16px;
      font-weight: 500;
      
      &:hover {
        background: #E09612;
      }
    }
  }
}

.activity-body {
  display: flex;
  gap: 32px;
  padding: 40px;
  
  .main-content {
    flex: 1;
    
    .section-card {
      background: white;
      border: 1px solid #F0F0F0;
      border-radius: 12px;
      padding: 32px;
      margin-bottom: 24px;
      
      .section-title {
        font-size: 24px;
        font-weight: 600;
        color: #333;
        margin-bottom: 24px;
        padding-bottom: 16px;
        border-bottom: 2px solid #F5A623;
      }
      
      .section-content {
        p {
          font-size: 16px;
          color: #666;
          line-height: 1.8;
          margin-bottom: 16px;
          
          &:last-child {
            margin-bottom: 0;
          }
        }
      }
    }
    
    .steps {
      display: flex;
      gap: 24px;
      
      .step-item {
        flex: 1;
        display: flex;
        gap: 16px;
        
        .step-number {
          width: 48px;
          height: 48px;
          background: linear-gradient(135deg, #F5A623 0%, #FF8C00 100%);
          color: white;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 20px;
          font-weight: 600;
          flex-shrink: 0;
        }
        
        .step-content {
          flex: 1;
          
          h3 {
            font-size: 18px;
            font-weight: 600;
            color: #333;
            margin-bottom: 8px;
          }
          
          p {
            font-size: 14px;
            color: #666;
            line-height: 1.6;
          }
        }
      }
    }
    
  }
  
  .sidebar {
    width: 300px;
    flex-shrink: 0;
    
    .sidebar-card {
      background: white;
      border: 1px solid #F0F0F0;
      border-radius: 12px;
      padding: 24px;
      margin-bottom: 24px;
      
      .sidebar-title {
        font-size: 18px;
        font-weight: 600;
        color: #333;
        margin-bottom: 20px;
        padding-bottom: 12px;
        border-bottom: 1px solid #F0F0F0;
      }
      
      .related-activities {
        .related-item {
          display: flex;
          gap: 12px;
          padding: 12px;
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.2s;
          margin-bottom: 12px;
          
          &:hover {
            background: #FFF9F0;
          }
          
          .related-cover {
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, #FFB84D 0%, #F5A623 100%);
            border-radius: 8px;
            flex-shrink: 0;
          }
          
          .related-info {
            flex: 1;
            
            .related-name {
              font-size: 14px;
              color: #333;
              margin-bottom: 6px;
              font-weight: 500;
            }
            
            .related-points {
              font-size: 14px;
              color: #F5A623;
              font-weight: 600;
            }
          }
        }
      }
      
      .rules-content {
        p {
          font-size: 14px;
          color: #666;
          line-height: 2;
          margin-bottom: 8px;
          
          &:last-child {
            margin-bottom: 0;
          }
        }
      }
    }
  }
}

// 弹窗表单样式
.participate-form {
  .image-uploader {
    .upload-preview {
      width: 200px;
      height: 150px;
      object-fit: cover;
      border-radius: 8px;
    }
    
    .upload-placeholder {
      width: 200px;
      height: 150px;
      border: 2px dashed #ddd;
      border-radius: 8px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      color: #999;
      cursor: pointer;
      transition: all 0.2s;
      
      &:hover {
        border-color: #F5A623;
        color: #F5A623;
      }
      
      .el-icon {
        font-size: 32px;
        margin-bottom: 8px;
      }
      
      span {
        font-size: 14px;
      }
    }
  }
}
</style>
