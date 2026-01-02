import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 10000
})

request.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

request.interceptors.response.use(
  response => {
    const res = response.data
    if (res.code && res.code !== 200) {
      ElMessage.error(res.message || '请求失败')
      return Promise.reject(new Error(res.message || '请求失败'))
    }
    return res
  },
  error => {
    if (error.response?.status === 401) {
      ElMessage.warning({
        message: '登录已过期，请重新登录',
        duration: 3000
      })
      localStorage.removeItem('token')
      setTimeout(() => {
        window.location.href = '/pc/login'
      }, 1500)
    } else if (error.response?.status === 403) {
      ElMessage.warning({
        message: '请先登录后再进行此操作',
        duration: 3000
      })
      setTimeout(() => {
        window.location.href = '/pc/login'
      }, 1500)
    } else {
      ElMessage.error(error.response?.data?.detail || error.message || '网络请求失败，请稍后重试')
    }
    return Promise.reject(error)
  }
)

export default request
