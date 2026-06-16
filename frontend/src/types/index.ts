export type RoleType = 'admin' | 'team_leader' | 'worker' | 'inspector'

export interface UserInfo {
  id: number
  username: string
  name: string
  role: string
}

export interface UserRole {
  code: RoleType
  name: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponseData {
  token: string
  refreshToken: string
  userInfo: UserInfo
  roles: UserRole[]
}

export interface ApiResponse<T = unknown> {
  code: number
  message: string
  data: T
}

export interface MenuItem {
  key: string
  label: string
  icon: string
  path: string
  roles: RoleType[]
}
