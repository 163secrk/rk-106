import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { UserInfo, UserRole, RoleType } from '@/types'

const TOKEN_KEY = 'token'
const USER_INFO_KEY = 'userInfo'
const ROLES_KEY = 'roles'

function getStoredUserInfo(): UserInfo | null {
  const stored = localStorage.getItem(USER_INFO_KEY)
  return stored ? (JSON.parse(stored) as UserInfo) : null
}

function getStoredRoles(): UserRole[] {
  const stored = localStorage.getItem(ROLES_KEY)
  return stored ? (JSON.parse(stored) as UserRole[]) : []
}

export const useUserStore = defineStore('user', () => {
  const token = ref<string>(localStorage.getItem(TOKEN_KEY) || '')
  const userInfo = ref<UserInfo | null>(getStoredUserInfo())
  const roles = ref<UserRole[]>(getStoredRoles())

  const isLoggedIn = computed(() => !!token.value)

  const roleCode = computed<RoleType | ''>(() => {
    if (roles.value.length > 0) {
      return roles.value[0].code
    }
    return ''
  })

  function setToken(newToken: string): void {
    token.value = newToken
    localStorage.setItem(TOKEN_KEY, newToken)
  }

  function setUserInfo(info: UserInfo): void {
    userInfo.value = info
    localStorage.setItem(USER_INFO_KEY, JSON.stringify(info))
  }

  function setRoles(newRoles: UserRole[]): void {
    roles.value = newRoles
    localStorage.setItem(ROLES_KEY, JSON.stringify(newRoles))
  }

  function login(newToken: string, info: UserInfo, newRoles: UserRole[]): void {
    setToken(newToken)
    setUserInfo(info)
    setRoles(newRoles)
  }

  function logout(): void {
    token.value = ''
    userInfo.value = null
    roles.value = []
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_INFO_KEY)
    localStorage.removeItem(ROLES_KEY)
  }

  function hasRole(roleCode: RoleType): boolean {
    return roles.value.some(role => role.code === roleCode)
  }

  function hasAnyRole(roleCodes: RoleType[]): boolean {
    return roleCodes.some(code => hasRole(code))
  }

  return {
    token,
    userInfo,
    roles,
    isLoggedIn,
    roleCode,
    setToken,
    setUserInfo,
    setRoles,
    login,
    logout,
    hasRole,
    hasAnyRole
  }
})
