import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { post, get, setLogoutCallback } from '@/utils/request'

export const useUserStore = defineStore('user', () => {
  const token = ref(uni.getStorageSync('token') || '')
  // 只有当有 Token 时才加载 UserInfo，防止数据不一致（有User无Token）
  const storedUser = token.value ? uni.getStorageSync('userInfo') : null
  const userInfo = ref(storedUser ? JSON.parse(storedUser) : null)

  const isLoggedIn = computed(() => !!token.value)
  
  // 注册401回调，确保store状态同步清除
  setLogoutCallback(() => {
    token.value = ''
    userInfo.value = null
  })

  const login = async (phone, code, referrerCode = '') => {
    const res = await post('/auth/login', { phone, code, referrer_code: referrerCode })
    // 后端返回的是 access_token，不是 token
    token.value = res.data.access_token
    userInfo.value = res.data.user
    uni.setStorageSync('token', token.value)
    uni.setStorageSync('userInfo', JSON.stringify(res.data.user))
    return res
  }

  const fetchUserInfo = async () => {
    if (!token.value) return
    try {
      console.log('Fetching user info...')
      const res = await get('/user/info')
      console.log('User info fetched:', res)
      if (res && res.data && res.data.user) {
        userInfo.value = res.data.user
        uni.setStorageSync('userInfo', JSON.stringify(res.data.user))
      }
    } catch (error) {
      console.error('获取用户信息失败', error)
      // 如果获取用户信息失败(且不是401，因为401 request.js会处理)，可能是网络或服务端异常
      // 这里不强制登出，避免网络波动导致登出，但我们在控制台能看到错
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
