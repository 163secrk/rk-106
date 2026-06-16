import type { MenuItem, RoleType } from '@/types'

export const menuConfig: MenuItem[] = [
  {
    key: 'dashboard',
    label: '生产看板',
    icon: 'HomeOutline',
    path: '/dashboard',
    roles: ['admin', 'team_leader', 'worker', 'inspector']
  },
  {
    key: 'product-process',
    label: '产品工序',
    icon: 'SettingsOutline',
    path: '/product-process',
    roles: ['admin', 'team_leader']
  },
  {
    key: 'work-order',
    label: '生产工单',
    icon: 'DocumentTextOutline',
    path: '/work-order',
    roles: ['admin', 'team_leader']
  },
  {
    key: 'report-center',
    label: '报工中心',
    icon: 'ClipboardOutline',
    path: '/report-center',
    roles: ['admin', 'team_leader', 'worker']
  },
  {
    key: 'quality-inspection',
    label: '质检大厅',
    icon: 'ShieldOutline',
    path: '/quality-inspection',
    roles: ['admin', 'team_leader', 'inspector']
  },
  {
    key: 'salary-settlement',
    label: '工资结算',
    icon: 'CashOutline',
    path: '/salary-settlement',
    roles: ['admin']
  },
  {
    key: 'system-settings',
    label: '系统设置',
    icon: 'CogOutline',
    path: '/system-settings',
    roles: ['admin']
  }
]

export function filterMenuByRoles(menus: MenuItem[], roles: RoleType[]): MenuItem[] {
  return menus.filter(menu => menu.roles.some(role => roles.includes(role)))
}

export function hasMenuPermission(path: string, roles: RoleType[]): boolean {
  const menu = menuConfig.find(m => m.path === path)
  if (!menu) return true
  return menu.roles.some(role => roles.includes(role))
}
