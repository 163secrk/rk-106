import { createRouter, createWebHashHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useUserStore } from '@/stores/user'
import MainLayout from '@/layouts/MainLayout.vue'
import type { RoleType } from '@/types'

declare module 'vue-router' {
  interface RouteMeta {
    title?: string
    icon?: string
    requiresAuth?: boolean
    roles?: RoleType[]
  }
}

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录', requiresAuth: false }
  },
  {
    path: '/',
    component: MainLayout,
    redirect: '/dashboard',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: {
          title: '生产看板',
          icon: 'HomeOutline',
          roles: ['admin', 'team_leader', 'worker', 'inspector']
        }
      },
      {
        path: 'product-process',
        name: 'ProductProcess',
        component: () => import('@/views/ProductProcess.vue'),
        meta: {
          title: '产品工序',
          icon: 'SettingsOutline',
          roles: ['admin', 'team_leader']
        }
      },
      {
        path: 'work-order',
        name: 'WorkOrder',
        component: () => import('@/views/WorkOrder.vue'),
        meta: {
          title: '生产工单',
          icon: 'DocumentTextOutline',
          roles: ['admin', 'team_leader']
        }
      },
      {
        path: 'report-center',
        name: 'ReportCenter',
        component: () => import('@/views/ReportCenter.vue'),
        meta: {
          title: '报工中心',
          icon: 'ClipboardOutline',
          roles: ['admin', 'team_leader', 'worker']
        }
      },
      {
        path: 'quality-inspection',
        name: 'QualityInspection',
        component: () => import('@/views/QualityInspection.vue'),
        meta: {
          title: '质检大厅',
          icon: 'ShieldOutline',
          roles: ['admin', 'team_leader', 'inspector']
        }
      },
      {
        path: 'salary-settlement',
        name: 'SalarySettlement',
        component: () => import('@/views/SalarySettlement.vue'),
        meta: {
          title: '工资结算',
          icon: 'CashOutline',
          roles: ['admin']
        }
      },
      {
        path: 'system-settings',
        name: 'SystemSettings',
        component: () => import('@/views/SystemSettings.vue'),
        meta: {
          title: '系统设置',
          icon: 'CogOutline',
          roles: ['admin']
        }
      }
    ]
  },
  {
    path: '/403',
    name: 'Forbidden',
    component: () => import('@/views/Login.vue'),
    meta: { title: '无权限', requiresAuth: false }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/dashboard'
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

router.beforeEach((to, _from, next) => {
  const userStore = useUserStore()
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth !== false)

  if (requiresAuth && !userStore.isLoggedIn) {
    next({ path: '/login', query: { redirect: to.fullPath } })
    return
  }

  if (to.path === '/login' && userStore.isLoggedIn) {
    next({ path: '/dashboard' })
    return
  }

  if (requiresAuth && to.meta.roles && to.meta.roles.length > 0) {
    const userRoleCodes = userStore.roles.map(role => role.code)
    const hasPermission = to.meta.roles.some(role => userRoleCodes.includes(role))
    if (!hasPermission) {
      next({ path: '/dashboard' })
      return
    }
  }

  next()
})

export default router
