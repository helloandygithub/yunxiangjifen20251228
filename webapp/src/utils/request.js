// H5环境使用代理，小程序环境使用生产环境域名
const isH5 = typeof window !== 'undefined' && window.location
const BASE_URL = isH5 ? '/api' : 'https://cloudexp.top/api'

// 用于在401时清除store状态
let clearStoreCallback = null
export const setLogoutCallback = (callback) => {
  clearStoreCallback = callback
}

const request = (options) => {
  return new Promise((resolve, reject) => {
    const token = uni.getStorageSync('token')

    uni.request({
      url: BASE_URL + options.url,
      method: options.method || 'GET',
      data: options.data,
      header: {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : '',
        ...options.header
      },
      // DEBUG: 打印请求信息
      complete: () => {
        // console.log(`[Request] ${options.url}, Token: ${token ? 'Yes' : 'No'}`)
      },
      success: (res) => {
        if (res.statusCode === 200) {
          if (res.data.code === 0) {
            resolve(res.data)
          } else {
            uni.showToast({
              title: res.data.message || '请求失败',
              icon: 'none'
            })
            reject(res.data)
          }
        } else if (res.statusCode === 401) {
          console.error('[401] Unauthorized:', options.url)
          // 清除localStorage
          uni.removeStorageSync('token')
          uni.removeStorageSync('userInfo')
          // 清除Pinia store状态
          if (clearStoreCallback) {
            clearStoreCallback()
          }
          uni.reLaunch({ url: '/pages/login/index' })
          reject(res.data)
        } else {
          uni.showToast({
            title: res.data.detail || '网络错误',
            icon: 'none'
          })
          reject(res.data)
        }
      },
      fail: (err) => {
        uni.showToast({
          title: '网络连接失败',
          icon: 'none'
        })
        reject(err)
      }
    })
  })
}

export const get = (url, data) => request({ url, method: 'GET', data })
export const post = (url, data) => request({ url, method: 'POST', data })
export const put = (url, data) => request({ url, method: 'PUT', data })

export default request
