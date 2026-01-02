import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/utils/api'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('admin_token') || '')
  const admin = ref(JSON.parse(localStorage.getItem('admin_info') || 'null'))

  const setToken = (newToken) => {
    token.value = newToken
    localStorage.setItem('admin_token', newToken)
  }

  const setAdmin = (info) => {
    admin.value = info
    localStorage.setItem('admin_info', JSON.stringify(info))
  }

  const login = async (username, password) => {
    const res = await api.post('/admin/login', { username, password })
    if (res.code === 0) {
      setToken(res.data.token || res.data.access_token)
      setAdmin(res.data.admin)
    }
    return res
  }

  const logout = () => {
    token.value = ''
    admin.value = null
    localStorage.removeItem('admin_token')
    localStorage.removeItem('admin_info')
  }

  return {
    token,
    admin,
    login,
    logout,
    setToken,
    setAdmin
  }
})
