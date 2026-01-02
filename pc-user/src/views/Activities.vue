<template>
  <div class="activities-page">
    <div class="container">
      <div class="page-header">
        <h1 class="page-title">活动中心</h1>
        <p class="subtitle">参与企业数字化产品推广，轻松赚取积分</p>
      </div>
      
      <div class="filters">
        <div class="filter-section">
          <div class="filter-label">产品分类</div>
          <div class="filter-buttons">
            <button 
              :class="['filter-btn', { active: filters.category === '' }]"
              @click="filters.category = ''; handleFilterChange()"
            >全部</button>
            <button 
              :class="['filter-btn', { active: filters.category === '云服务器' }]"
              @click="filters.category = '云服务器'; handleFilterChange()"
            >云服务器</button>
            <button 
              :class="['filter-btn', { active: filters.category === '云数据库' }]"
              @click="filters.category = '云数据库'; handleFilterChange()"
            >云数据库</button>
            <button 
              :class="['filter-btn', { active: filters.category === 'SaaS应用' }]"
              @click="filters.category = 'SaaS应用'; handleFilterChange()"
            >SaaS应用</button>
            <button 
              :class="['filter-btn', { active: filters.category === '信创产品' }]"
              @click="filters.category = '信创产品'; handleFilterChange()"
            >信创产品</button>
            <button 
              :class="['filter-btn', { active: filters.category === '企业服务' }]"
              @click="filters.category = '企业服务'; handleFilterChange()"
            >企业服务</button>
          </div>
        </div>
        
        <div class="filter-row">
          <div class="filter-section">
            <div class="filter-label">状态：</div>
            <div class="filter-buttons">
              <button 
                :class="['filter-btn-small', { active: filters.status === '' }]"
                @click="filters.status = ''; handleFilterChange()"
              >全部</button>
              <button 
                :class="['filter-btn-small', { active: filters.status === '进行中' }]"
                @click="filters.status = '进行中'; handleFilterChange()"
              >进行中</button>
              <button 
                :class="['filter-btn-small', { active: filters.status === '即将开始' }]"
                @click="filters.status = '即将开始'; handleFilterChange()"
              >即将开始</button>
              <button 
                :class="['filter-btn-small', { active: filters.status === '已结束' }]"
                @click="filters.status = '已结束'; handleFilterChange()"
              >已结束</button>
            </div>
          </div>
          
          <div class="filter-section">
            <div class="filter-label">排序：</div>
            <div class="filter-buttons">
              <button 
                :class="['filter-btn-small', { active: filters.sort === 'latest' }]"
                @click="filters.sort = 'latest'; handleFilterChange()"
              >最新</button>
              <button 
                :class="['filter-btn-small', { active: filters.sort === 'points' }]"
                @click="filters.sort = 'points'; handleFilterChange()"
              >积分最高</button>
              <button 
                :class="['filter-btn-small', { active: filters.sort === 'popular' }]"
                @click="filters.sort = 'popular'; handleFilterChange()"
              >参与最多</button>
            </div>
          </div>
        </div>
      </div>
      
      <div class="activities-grid" v-loading="loading">
        <div class="activity-card" v-for="item in activities" :key="item.id" @click="goToDetail(item.id)">
          <div class="activity-cover">
            <img v-if="item.cover_image" :src="item.cover_image" />
            <div v-else class="cover-placeholder">
              <div class="placeholder-icon">🎯</div>
            </div>
            <el-tag :class="['activity-status', getStatusClass(item)]">{{ getStatusText(item) }}</el-tag>
          </div>
          <div class="activity-content">
            <div class="activity-tag">{{ item.category || '云服务器' }}</div>
            <h3>{{ item.title }}</h3>
            <p class="activity-desc">{{ item.description }}</p>
            <div class="activity-footer">
              <div class="activity-reward">
                <span class="reward-amount">+{{ item.reward_points || 500 }} 积分</span>
              </div>
              <div class="activity-participants">
                <el-icon><User /></el-icon>
                <span>{{ item.participant_count || 0 }}人参与</span>
              </div>
            </div>
            <el-button type="primary" class="participate-btn">
              立即参与
            </el-button>
          </div>
        </div>
        
        <el-empty v-if="!loading && activities.length === 0" description="暂无活动" />
      </div>
      
      <el-pagination
        v-if="total > 0"
        v-model:current-page="page"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next"
        @current-change="fetchActivities"
        style="margin-top: 32px; justify-content: center;"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { User } from '@element-plus/icons-vue'
import request from '@/utils/request'

const router = useRouter()
const loading = ref(false)
const activities = ref([])
const page = ref(1)
const pageSize = ref(12)
const total = ref(0)

const filters = ref({
  category: '',
  status: '',
  sort: 'latest'
})

const fetchActivities = async () => {
  loading.value = true
  try {
    const res = await request.get('/activities', {
      params: { 
        status: 'active', 
        page: page.value, 
        page_size: pageSize.value,
        category: filters.value.category,
        ...filters.value
      }
    })
    activities.value = res.data?.items || []
    total.value = res.data?.total || 0
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleFilterChange = () => {
  page.value = 1
  fetchActivities()
}

const getStatusClass = (item) => {
  const status = item.status || '进行中'
  return status === '进行中' ? 'status-active' : status === '即将开始' ? 'status-upcoming' : 'status-ended'
}

const getStatusText = (item) => {
  return item.status || '进行中'
}

const goToDetail = (id) => {
  router.push(`/activity/${id}`)
}

onMounted(fetchActivities)
</script>

<style lang="scss" scoped>
.activities-page {
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
    margin-bottom: 40px;
    
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
  
  .filters {
    background: white;
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 32px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    
    .filter-section {
      margin-bottom: 20px;
      
      &:last-child {
        margin-bottom: 0;
      }
      
      .filter-label {
        font-size: 14px;
        color: #666;
        margin-bottom: 12px;
        font-weight: 500;
      }
      
      .filter-buttons {
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
      }
      
      .filter-btn {
        padding: 8px 20px;
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
      
      .filter-btn-small {
        padding: 6px 16px;
        border: 1px solid #E5E7EB;
        background: white;
        border-radius: 6px;
        font-size: 14px;
        color: #666;
        cursor: pointer;
        transition: all 0.2s;
        
        &:hover {
          border-color: #F5A623;
          color: #F5A623;
        }
        
        &.active {
          background: #4A90E2;
          border-color: #4A90E2;
          color: white;
        }
      }
    }
    
    .filter-row {
      display: flex;
      gap: 40px;
      align-items: center;
      
      .filter-section {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 0;
        
        .filter-label {
          margin-bottom: 0;
          white-space: nowrap;
        }
      }
    }
  }
  
  .activities-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 24px;
  }
}

.activity-card {
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
  
  .activity-cover {
    width: 100%;
    height: 200px;
    overflow: hidden;
    position: relative;
    background: linear-gradient(135deg, #FFB84D 0%, #F5A623 100%);
    
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
    
    .activity-status {
      position: absolute;
      top: 12px;
      left: 12px;
      border: none;
      color: white;
      font-weight: 500;
      
      &.status-active {
        background: #52C41A;
      }
      
      &.status-upcoming {
        background: #FFA940;
      }
      
      &.status-ended {
        background: #999;
      }
    }
  }
  
  .activity-content {
    padding: 20px;
    
    .activity-tag {
      display: inline-block;
      padding: 4px 12px;
      background: #FFF4E6;
      color: #F5A623;
      border-radius: 4px;
      font-size: 12px;
      font-weight: 500;
      margin-bottom: 12px;
    }
    
    h3 {
      font-size: 18px;
      font-weight: 600;
      color: #333;
      margin-bottom: 12px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    
    .activity-desc {
      font-size: 14px;
      color: #666;
      line-height: 1.6;
      margin-bottom: 16px;
      overflow: hidden;
      text-overflow: ellipsis;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      min-height: 44px;
    }
    
    .activity-footer {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
      
      .activity-reward {
        .reward-amount {
          color: #F5A623;
          font-weight: 600;
          font-size: 16px;
        }
      }
      
      .activity-participants {
        display: flex;
        align-items: center;
        gap: 6px;
        color: #999;
        font-size: 14px;
      }
    }
    
    .participate-btn {
      width: 100%;
      background: #F5A623;
      border: none;
      color: white;
      font-weight: 500;
      
      &:hover {
        background: #E09612;
      }
    }
  }
}

:deep(.el-pagination) {
  display: flex;
  justify-content: center;
  margin-top: 40px;
  
  .el-pager li.is-active {
    background: #F5A623;
    color: white;
  }
  
  button:hover,
  .el-pager li:hover {
    color: #F5A623;
  }
}
</style>
