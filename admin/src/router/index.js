import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录', public: true }
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '工作台', icon: 'Odometer' }
      },
      {
        path: 'activities',
        name: 'Activities',
        component: () => import('@/views/activities/List.vue'),
        meta: { title: '活动管理', icon: 'Trophy' }
      },
      {
        path: 'activities/create',
        name: 'ActivityCreate',
        component: () => import('@/views/activities/Edit.vue'),
        meta: { title: '创建活动', hidden: true }
      },
      {
        path: 'activities/:id/edit',
        name: 'ActivityEdit',
        component: () => import('@/views/activities/Edit.vue'),
        meta: { title: '编辑活动', hidden: true }
      },
      {
        path: 'submissions',
        name: 'Submissions',
        component: () => import('@/views/submissions/List.vue'),
        meta: { title: '审核管理', icon: 'DocumentChecked' }
      },
      {
        path: 'products',
        name: 'Products',
        component: () => import('@/views/products/List.vue'),
        meta: { title: '商品管理', icon: 'ShoppingBag' }
      },
      {
        path: 'orders',
        name: 'Orders',
        component: () => import('@/views/orders/List.vue'),
        meta: { title: '订单管理', icon: 'List' }
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('@/views/users/List.vue'),
        meta: { title: '用户管理', icon: 'User' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory('/admin/'),
  routes
})

router.beforeEach((to, from, next) => {
  document.title = `${to.meta.title || '管理后台'} - 积分活动平台`
  
  const userStore = useUserStore()
  
  if (to.meta.public) {
    next()
  } else if (!userStore.token) {
    next('/login')
  } else {
    next()
  }
})

export default router
