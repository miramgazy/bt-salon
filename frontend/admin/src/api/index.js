import axios from 'axios'
import router from '../router'

const api = axios.create({
  baseURL: '/'
})

// Request interceptor: add Authorization header
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor: handle 401 and token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        try {
          const response = await axios.post('/api/accounts/token/refresh/', {
            refresh: refreshToken
          })
          
          const newAccessToken = response.data.access
          localStorage.setItem('access_token', newAccessToken)
          
          // Retry the original request with new token
          originalRequest.headers.Authorization = `Bearer ${newAccessToken}`
          return api(originalRequest)
        } catch (refreshError) {
          // Refresh token expired or invalid
          console.error('Refresh token expired', refreshError)
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          router.push('/login')
        }
      } else {
        // No refresh token available
        router.push('/login')
      }
    }
    
    return Promise.reject(error)
  }
)

export default api
