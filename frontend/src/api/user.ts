import { post, get } from '@/utils/request'
import type { LoginRequest, LoginResponseData, UserInfo, UserRole } from '@/types'

export function loginApi(data: LoginRequest): Promise<LoginResponseData> {
  return post<LoginResponseData>('/login/', data)
}

export function getUserInfoApi(): Promise<{ userInfo: UserInfo; roles: UserRole[] }> {
  return get<{ userInfo: UserInfo; roles: UserRole[] }>('/userinfo/')
}
