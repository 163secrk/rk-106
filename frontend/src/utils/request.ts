import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig, InternalAxiosRequestConfig } from 'axios'
import { useUserStore } from '@/stores/user'
import type { ApiResponse } from '@/types'

const service: AxiosInstance = axios.create({
  baseURL: '/api',
  timeout: 10000
})

service.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const userStore = useUserStore()
    if (userStore.token) {
      config.headers.Authorization = `Bearer ${userStore.token}`
    }
    return config
  },
  (error: unknown) => {
    return Promise.reject(error)
  }
)

service.interceptors.response.use(
  // @ts-ignore: 响应拦截器返回 data 部分而非完整 AxiosResponse
  (response) => {
    const res = response.data as ApiResponse<unknown>
    if (res.code === 200) {
      return res.data
    }
    if (res.code === 401) {
      const userStore = useUserStore()
      userStore.logout()
      window.location.href = '/#/login'
    }
    return Promise.reject(new Error(res.message || '请求失败'))
  },
  (error: any) => {
    if (error.response && error.response.data && error.response.data.message) {
      return Promise.reject(new Error(error.response.data.message))
    }
    if (error.message) {
      return Promise.reject(new Error(error.message))
    }
    return Promise.reject(new Error('网络请求失败，请检查网络连接'))
  }
)

export function get<T = unknown>(url: string, config?: AxiosRequestConfig): Promise<T> {
  return service.get(url, config) as unknown as Promise<T>
}

export function post<T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
  return service.post(url, data, config) as unknown as Promise<T>
}

export function put<T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
  return service.put(url, data, config) as unknown as Promise<T>
}

export function del<T = unknown>(url: string, config?: AxiosRequestConfig): Promise<T> {
  return service.delete(url, config) as unknown as Promise<T>
}

export default service
