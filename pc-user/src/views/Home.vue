<template>
  <div class="home">
    <!-- Hero Section -->
    <div class="hero">
      <div class="container">
        <div class="hero-content">
          <div class="hero-text">
            <p class="welcome-text">欢迎回来，数字化先锋</p>
            <h1 class="hero-title">推广数字化产品 赚取丰厚积分</h1>
            <p class="hero-desc">
              参与云服务器、云数据库、SaaS等产品推广活动，轻松获得积分奖励
            </p>
            <div class="hero-stats">
              <div class="stat-card">
                <div class="stat-icon blue">
                  <el-icon><Document /></el-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-label">已完成任务</div>
                  <div class="stat-value">{{ userStats.completedTasks || 0 }}</div>
                </div>
              </div>
              <div class="stat-card">
                <div class="stat-icon orange">
                  <el-icon><Coin /></el-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-label">累计获得积分</div>
                  <div class="stat-value">{{ formatNumber(userStats.totalPoints || 0) }}</div>
                </div>
              </div>
            </div>
            <div class="hero-actions">
              <el-button type="primary" size="large" class="btn-primary" @click="$router.push('/activities')">
                前往活动专区
                <el-icon><ArrowRight /></el-icon>
              </el-button>
              <el-button size="large" class="btn-secondary" @click="$router.push('/mall')">
                浏览积分商城
              </el-button>
            </div>
          </div>
          <div class="hero-card">
            <div class="points-card">
              <div class="card-label">今日可获积分</div>
              <div class="card-points">+{{ formatNumber(userStats.todayAvailable || 0) }}</div>
              <div class="card-subtitle">积分</div>
            </div>
            <div class="hot-activities">
              <div class="hot-title">热门活动</div>
              <div class="hot-list">
                <div class="hot-item">
                  <span class="hot-dot"></span>
                  <span class="hot-text">腾讯云服务器推广 +500积分</span>
                  <el-icon class="hot-arrow"><ArrowRight /></el-icon>
                </div>
                <div class="hot-item">
                  <span class="hot-dot"></span>
                  <span class="hot-text">阿里云数据库推荐 +450积分</span>
                  <el-icon class="hot-arrow"><ArrowRight /></el-icon>
                </div>
                <div class="hot-item">
                  <span class="hot-dot"></span>
                  <span class="hot-text">企业微信推荐 +300积分</span>
                  <el-icon class="hot-arrow"><ArrowRight /></el-icon>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 快速导航 -->
    <div class="section quick-nav-section">
      <div class="container">
        <div class="section-header">
          <h2>快速导航</h2>
          <p class="section-subtitle">一键进入核心功能区域</p>
        </div>
        <div class="quick-nav">
          <div class="nav-card orange" @click="$router.push('/activities')">
            <div class="nav-icon">
              <el-icon><Trophy /></el-icon>
            </div>
            <div class="nav-content">
              <h3>活动专区</h3>
              <p>参与推广赚积分</p>
            </div>
            <div class="nav-link">
              查看活动
              <el-icon><ArrowRight /></el-icon>
            </div>
          </div>
          <div class="nav-card blue" @click="$router.push('/mall')">
            <div class="nav-icon">
              <el-icon><ShoppingBag /></el-icon>
            </div>
            <div class="nav-content">
              <h3>积分商城</h3>
              <p>兑换数码好礼</p>
            </div>
            <div class="nav-link">
              前往商城
              <el-icon><ArrowRight /></el-icon>
            </div>
          </div>
          <div class="nav-card gray" @click="$router.push('/user')">
            <div class="nav-icon">
              <el-icon><User /></el-icon>
            </div>
            <div class="nav-content">
              <h3>我的积分</h3>
              <p>查看积分明细</p>
            </div>
            <div class="nav-link">
              查看详情
              <el-icon><ArrowRight /></el-icon>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 热门活动 -->
    <div class="section activities-section">
      <div class="container">
        <div class="section-header">
          <h2>热门活动</h2>
          <p class="section-subtitle">精选推荐，轻松参与赚取积分</p>
          <el-button text class="view-more-btn" @click="$router.push('/activities')">
            查看全部活动
            <el-icon><ArrowRight /></el-icon>
          </el-button>
        </div>
        
        <div class="activities-grid" v-loading="loading">
          <div class="activity-card" v-for="item in activities.slice(0, 3)" :key="item.id" @click="goToActivity(item.id)">
            <div class="activity-cover">
              <img v-if="item.cover_image" :src="item.cover_image" />
              <div v-else class="cover-placeholder">
                <div class="placeholder-icon">🎯</div>
              </div>
              <el-tag class="activity-status">进行中</el-tag>
            </div>
            <div class="activity-content">
              <div class="activity-tag">云服务器</div>
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
      </div>
    </div>
    
    <!-- Footer -->
    <footer class="footer">
      <div class="container">
        <div class="footer-content">
          <div class="footer-section">
            <div class="footer-logo">
              <div class="logo-icon">云</div>
              <span>云享积分</span>
            </div>
            <p class="footer-desc">企业数字化产品推广平台<br/>推广云服务，赚取积分</p>
          </div>
          
          <div class="footer-section">
            <h4>快速链接</h4>
            <ul>
              <li><a href="#" @click.prevent="$router.push('/')">关于我们</a></li>
              <li><a href="#" @click.prevent="$router.push('/activities')">活动规则</a></li>
              <li><a href="#" @click.prevent="$router.push('/mall')">积分规则</a></li>
              <li><a href="#">合作伙伴</a></li>
            </ul>
          </div>
          
          <div class="footer-section">
            <h4>帮助支持</h4>
            <ul>
              <li><a href="#">常见问题</a></li>
              <li><a href="#">使用指南</a></li>
              <li><a href="#">联系客服</a></li>
              <li><a href="#">意见反馈</a></li>
            </ul>
          </div>
          
          <div class="footer-section">
            <h4>关注我们</h4>
            <p class="contact-info">企业微信：yunxiangjifen</p>
            <p class="contact-info">服务热线：400-888-8888</p>
            <p class="contact-info">工作时间：9:00-18:00</p>
          </div>
        </div>
        
        <div class="footer-bottom">
          <p>© 2025 云享积分平台 版权所有 | ICP备案号：京ICP备12345678号</p>
        </div>
      </div>
    </footer>
    
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import request from '@/utils/request'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const activities = ref([])
const products = ref([])
const userStats = ref({
  completedTasks: 0,
  totalPoints: 0,
  todayAvailable: 0
})

const formatNumber = (num) => {
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

const fetchUserStats = async () => {
  const token = localStorage.getItem('token')
  if (!token) return
  
  try {
    // 获取用户信息
    const userInfo = await request.get('/user/info')
    if (userInfo.data?.user) {
      userStats.value.totalPoints = userInfo.data.user.points_balance || 0
    }
    
    // 获取已完成任务数（通过提交记录）
    const submissions = await request.get('/user/records', { params: { type: 'submissions' } })
    if (submissions.data?.items) {
      userStats.value.completedTasks = submissions.data.items.filter(s => s.status === 'approved').length
    }
    
    // 今日可获积分（从活动列表计算）
    const activeActivities = await request.get('/activities', { params: { status: 'active', page_size: 100 } })
    if (activeActivities.data?.items) {
      userStats.value.todayAvailable = activeActivities.data.items.reduce((sum, act) => sum + (act.reward_points || 0), 0)
    }
  } catch (error) {
    console.error('获取用户统计失败:', error)
  }
}

const fetchActivities = async () => {
  loading.value = true
  try {
    const res = await request.get('/activities', { params: { status: 'active', page_size: 6 } })
    activities.value = res.data?.items || []
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const fetchProducts = async () => {
  try {
    const res = await request.get('/mall/products', { params: { page_size: 4 } })
    products.value = res.data?.items || []
  } catch (error) {
    console.error(error)
  }
}

const goToActivity = (id) => {
  router.push(`/activity/${id}`)
}

const goToProduct = (id) => {
  router.push(`/product/${id}`)
}

onMounted(() => {
  fetchUserStats()
  fetchActivities()
  fetchProducts()
})
</script>

<style lang="scss" scoped>
.home {
  min-height: calc(100vh - 64px);
  background: #FFFBF5;
}

.hero {
  background: linear-gradient(135deg, #FFF9F0 0%, #FFFBF5 100%);
  padding: 60px 0 80px;
  
  .container {
    max-width: 1200px;
    width: 100%;
    margin: 0 auto;
    padding: 0 24px;
    box-sizing: border-box;
  }
  
  .hero-content {
    display: flex;
    gap: 40px;
    align-items: flex-start;
  }
  
  .hero-text {
    flex: 1;
    min-width: 0;
    
    .welcome-text {
      color: #F5A623;
      font-size: 16px;
      margin-bottom: 16px;
    }
    
    .hero-title {
      font-size: 36px;
      font-weight: 700;
      color: #333;
      line-height: 1.3;
      margin-bottom: 20px;
    }
    
    .hero-desc {
      font-size: 16px;
      color: #666;
      line-height: 1.8;
      margin-bottom: 32px;
      max-width: 500px;
    }
    
    .hero-stats {
      display: flex;
      gap: 20px;
      margin-bottom: 32px;
      
      .stat-card {
        background: white;
        border-radius: 12px;
        padding: 20px 24px;
        display: flex;
        align-items: center;
        gap: 16px;
        flex: 1;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
        
        .stat-icon {
          width: 48px;
          height: 48px;
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 24px;
          
          &.blue {
            background: #E8F4FD;
            color: #4A90E2;
          }
          
          &.orange {
            background: #FFF4E6;
            color: #F5A623;
          }
        }
        
        .stat-info {
          flex: 1;
          
          .stat-label {
            font-size: 14px;
            color: #999;
            margin-bottom: 4px;
          }
          
          .stat-value {
            font-size: 28px;
            font-weight: 600;
            color: #333;
          }
        }
      }
    }
    
    .hero-actions {
      display: flex;
      gap: 16px;
      
      .btn-primary {
        background: #F5A623;
        border: none;
        color: white;
        padding: 12px 32px;
        font-size: 16px;
        
        &:hover {
          background: #E09612;
        }
      }
      
      .btn-secondary {
        border: 1px solid #F5A623;
        color: #F5A623;
        background: white;
        
        &:hover {
          background: #FFF9F0;
        }
      }
    }
  }
  
  .hero-card {
    width: 320px;
    flex-shrink: 0;
    
    .points-card {
      background: white;
      border-radius: 16px;
      padding: 32px;
      text-align: center;
      box-shadow: 0 4px 20px rgba(245, 166, 35, 0.1);
      margin-bottom: 20px;
      
      .card-label {
        font-size: 14px;
        color: #999;
        margin-bottom: 12px;
      }
      
      .card-points {
        font-size: 56px;
        font-weight: 700;
        color: #F5A623;
        line-height: 1;
        margin-bottom: 8px;
      }
      
      .card-subtitle {
        font-size: 14px;
        color: #999;
      }
    }
    
    .hot-activities {
      background: white;
      border-radius: 16px;
      padding: 24px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
      
      .hot-title {
        font-size: 16px;
        font-weight: 600;
        color: #333;
        margin-bottom: 16px;
      }
      
      .hot-list {
        display: flex;
        flex-direction: column;
        gap: 12px;
      }
      
      .hot-item {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 12px;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s;
        
        &:hover {
          background: #FFF9F0;
        }
        
        .hot-dot {
          width: 6px;
          height: 6px;
          border-radius: 50%;
          background: #F5A623;
          flex-shrink: 0;
        }
        
        .hot-text {
          flex: 1;
          font-size: 14px;
          color: #666;
        }
        
        .hot-arrow {
          font-size: 14px;
          color: #999;
        }
      }
    }
  }
}

.section {
  padding: 60px 0;
  
  .container {
    max-width: 1200px;
    width: 100%;
    margin: 0 auto;
    padding: 0 24px;
    box-sizing: border-box;
  }
  
  .section-header {
    margin-bottom: 40px;
    
    h2 {
      font-size: 32px;
      font-weight: 700;
      color: #333;
      margin-bottom: 8px;
    }
    
    .section-subtitle {
      font-size: 16px;
      color: #999;
    }
    
    .view-more-btn {
      float: right;
      color: #F5A623;
      font-size: 16px;
      
      &:hover {
        color: #E09612;
      }
    }
  }
}

.quick-nav-section {
  background: white;
  
  .quick-nav {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 24px;
    
    .nav-card {
      background: white;
      border-radius: 16px;
      padding: 24px;
      display: flex;
      align-items: center;
      gap: 16px;
      cursor: pointer;
      transition: all 0.3s;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
      
      &:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
      }
      
      &.orange {
        background: #FFF9F0;
        
        .nav-icon {
          background: #F5A623;
        }
      }
      
      &.blue {
        background: #F0F7FF;
        
        .nav-icon {
          background: #4A90E2;
        }
      }
      
      &.gray {
        background: #F8F9FA;
        
        .nav-icon {
          background: #666;
        }
      }
      
      .nav-icon {
        width: 56px;
        height: 56px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        color: white;
        flex-shrink: 0;
      }
      
      .nav-content {
        flex: 1;
        
        h3 {
          font-size: 18px;
          font-weight: 600;
          color: #333;
          margin-bottom: 4px;
        }
        
        p {
          font-size: 14px;
          color: #999;
        }
      }
      
      .nav-link {
        display: flex;
        align-items: center;
        gap: 4px;
        font-size: 14px;
        color: #F5A623;
        font-weight: 500;
        
        .el-icon {
          font-size: 14px;
        }
      }
    }
  }
}

.achievements-section {
  .achievements {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 24px;
    margin-bottom: 24px;
    
    .achievement-card {
      background: white;
      border-radius: 16px;
      padding: 32px;
      position: relative;
      border: 2px solid #f5f5f5;
      
      &.unlocked {
        border-color: #FFE4B3;
        background: linear-gradient(135deg, #FFFBF5 0%, white 100%);
      }
      
      .achievement-icon {
        font-size: 48px;
        margin-bottom: 16px;
      }
      
      h3 {
        font-size: 20px;
        font-weight: 600;
        color: #333;
        margin-bottom: 8px;
      }
      
      p {
        font-size: 14px;
        color: #666;
        line-height: 1.6;
        margin-bottom: 12px;
      }
      
      .achievement-date {
        font-size: 12px;
        color: #999;
        margin-bottom: 12px;
      }
      
      .achievement-tag {
        position: absolute;
        top: 24px;
        right: 24px;
      }
    }
  }
  
  .view-all-btn {
    color: #F5A623;
    font-size: 16px;
    
    &:hover {
      color: #E09612;
    }
  }
}

.activities-section {
  background: white;
  
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
  border: 2px solid #f5f5f5;
  
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
      background: #F5A623;
      border: none;
      color: white;
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
          font-weight: 400;
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

.footer {
  background: #2C2C2C;
  color: #999;
  padding: 60px 0 0;
  
  .container {
    max-width: 1200px;
    width: 100%;
    margin: 0 auto;
    padding: 0 24px;
    box-sizing: border-box;
  }
  
  .footer-content {
    display: grid;
    grid-template-columns: 2fr 1fr 1fr 1.5fr;
    gap: 60px;
    padding-bottom: 40px;
    border-bottom: 1px solid #444;
  }
  
  .footer-section {
    h4 {
      color: white;
      font-size: 16px;
      font-weight: 600;
      margin-bottom: 20px;
    }
    
    ul {
      list-style: none;
      padding: 0;
      margin: 0;
      
      li {
        margin-bottom: 12px;
        
        a {
          color: #999;
          text-decoration: none;
          font-size: 14px;
          transition: color 0.2s;
          
          &:hover {
            color: #F5A623;
          }
        }
      }
    }
    
    .footer-logo {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 16px;
      
      .logo-icon {
        width: 40px;
        height: 40px;
        background: #F5A623;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 600;
        font-size: 18px;
      }
      
      span {
        color: white;
        font-size: 20px;
        font-weight: 600;
      }
    }
    
    .footer-desc {
      font-size: 14px;
      line-height: 1.8;
      color: #999;
    }
    
    .contact-info {
      font-size: 14px;
      margin-bottom: 8px;
      color: #999;
    }
  }
  
  .footer-bottom {
    padding: 24px 0;
    text-align: center;
    
    p {
      font-size: 14px;
      color: #666;
      margin: 0;
    }
  }
}
</style>
