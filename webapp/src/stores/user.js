import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { post, get } from '@/utils/request'

export const useUserStore = defineStore('user', () => {
  const token = ref(uni.getStorageSync('token') || '')
  const storedUser = uni.getStorageSync('userInfo')
  const userInfo = ref(storedUser ? JSON.parse(storedUser) : null)

  const isLoggedIn = computed(() => !!token.value)

  const login = async (phone, code, referrerCode = '') => {
    const res = await post('/auth/login', { phone, code, referrer_code: referrerCode })
    token.value = res.data.token
    userInfo.value = res.data.user
    uni.setStorageSync('token', token.value)
    uni.setStorageSync('userInfo', JSON.stringify(res.data.user))
    return res
  }

  const fetchUserInfo = async () => {
    if (!token.value) return
    try {
      const res = await get('/user/info')
      userInfo.value = res.data
      uni.setStorageSync('userInfo', JSON.stringify(res.data))
    } catch (error) {
      console.error('获取用户信息失败', error)
    }
  }

  const logout = () => {
    token.value = ''
    userInfo.value = null
    uni.removeStorageSync('token')
    uni.removeStorageSync('userInfo')
  }

  const setUser = (user) => {
    userInfo.value = user
    uni.setStorageSync('userInfo', JSON.stringify(user))
  }

  const checkLogin = () => {
    if (!token.value) {
      uni.navigateTo({ url: '/pages/login/index' })
      return false
    }
    return true
  }

  return {
    token,
    userInfo,
    isLoggedIn,
    login,
    fetchUserInfo,
    logout,
    setUser,
    checkLogin
  }
})
