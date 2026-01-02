import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import request from '@/utils/request'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(null)

  const isLoggedIn = computed(() => !!token.value)
  
  // 兼容性属性
  const user = computed(() => userInfo.value)

  const login = async (phone, code, referrerCode = '') => {
    const res = await request.post('/auth/login', { phone, code, referrer_code: referrerCode })
    token.value = res.data.token || res.data.access_token
    userInfo.value = res.data.user
    localStorage.setItem('token', token.value)
    return res
  }

  const fetchUserInfo = async () => {
    if (!token.value) return
    try {
      const res = await request.get('/user/info')
      userInfo.value = res.data
    } catch (error) {
      console.error('获取用户信息失败', error)
    }
  }

  const logout = () => {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
  }

  return {
    token,
    userInfo,
    user,
    isLoggedIn,
    login,
    fetchUserInfo,
    logout
  }
})
