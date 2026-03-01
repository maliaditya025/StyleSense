import axios from 'axios'
import { useAuthStore } from './store'

const API_URL = process.env.NEXT_PUBLIC_BACKEND_URL

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().clearAuth()
      if (typeof window !== 'undefined') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export const authApi = {
  login: (email: string, password: string) =>
    api.post('/api/login', { email, password }),
  register: (email: string, password: string, name: string) =>
    api.post('/api/register', { email, password, name }),
}

export const clothingApi = {
  upload: (formData: FormData) =>
    api.post('/api/upload-clothes', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  getCloset: () => api.get('/api/closet'),
}

export const recommendationApi = {
  generateOutfits: () => api.get('/api/generate-outfits'),
}

export default api
