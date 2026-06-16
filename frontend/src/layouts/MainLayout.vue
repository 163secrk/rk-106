<script setup lang="ts">
import { ref, computed, h } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  NLayout,
  NLayoutSider,
  NLayoutHeader,
  NLayoutContent,
  NMenu,
  NButton,
  NDropdown,
  NAvatar,
  NIcon,
  NSpace,
  NBreadcrumb,
  NBreadcrumbItem,
  NTag
} from 'naive-ui'
import { useUserStore } from '@/stores/user'
import { menuConfig, filterMenuByRoles } from '@/config/menu'
import {
  HomeOutline,
  SettingsOutline,
  DocumentTextOutline,
  ClipboardOutline,
  ShieldOutline,
  CashOutline,
  CogOutline,
  LogOutOutline,
  PersonOutline,
  MenuOutline,
  ChevronBackOutline,
  ChevronForwardOutline
} from '@vicons/ionicons5'
import type { MenuOption, DropdownOption } from 'naive-ui'
import type { RoleType } from '@/types'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const collapsed = ref(false)

const iconMap: Record<string, unknown> = {
  HomeOutline,
  SettingsOutline,
  DocumentTextOutline,
  ClipboardOutline,
  ShieldOutline,
  CashOutline,
  CogOutline
}

const isWorker = computed(() => userStore.roleCode === 'worker')

const userRoleCodes = computed<RoleType[]>(() => {
  return userStore.roles.map(role => role.code)
})

const filteredMenus = computed(() => {
  return filterMenuByRoles(menuConfig, userRoleCodes.value)
})

const menuOptions = computed<MenuOption[]>(() => {
  return filteredMenus.value.map(menu => ({
    label: menu.label,
    key: menu.path,
    icon: () => {
      const IconComponent = iconMap[menu.icon]
      return IconComponent ? h(NIcon, null, { default: () => h(IconComponent) }) : null
    }
  }))
})

const dropdownOptions: DropdownOption[] = [
  {
    label: '个人设置',
    key: 'profile',
    icon: () => h(NIcon, null, { default: () => h(PersonOutline) })
  },
  {
    label: '退出登录',
    key: 'logout',
    icon: () => h(NIcon, null, { default: () => h(LogOutOutline) })
  }
]

const activeKey = computed(() => route.path)

const breadcrumbItems = computed(() => {
  const items = [{ label: '首页', key: 'home' }]
  const currentMenu = menuConfig.find(m => m.path === route.path)
  if (currentMenu) {
    items.push({ label: currentMenu.label, key: currentMenu.key })
  }
  return items
})

const userDisplayName = computed(() => {
  return userStore.userInfo?.name || userStore.userInfo?.username || '用户'
})

const roleTagType = computed<'error' | 'info' | 'success' | 'warning'>(() => {
  switch (userStore.roleCode) {
    case 'admin':
      return 'error'
    case 'team_leader':
      return 'info'
    case 'worker':
      return 'success'
    case 'inspector':
      return 'warning'
    default:
      return 'info'
  }
})

const roleName = computed(() => {
  if (userStore.roles.length > 0) {
    return userStore.roles[0].name
  }
  return '未知角色'
})

function handleMenuSelect(key: string): void {
  router.push(key)
}

function handleDropdownSelect(key: string | number): void {
  if (key === 'logout') {
    userStore.logout()
    router.push('/login')
  }
}

function toggleCollapse(): void {
  collapsed.value = !collapsed.value
}
</script>

<template>
  <n-layout class="main-layout" :class="{ 'worker-mode': isWorker }">
    <n-layout-sider
      :collapsed="collapsed"
      collapse-mode="width"
      :collapsed-width="64"
      :width="240"
      :show-trigger="false"
      class="layout-sider"
      bordered
    >
      <div class="sider-header">
        <div class="logo-area">
          <div class="logo-icon">
            <n-icon size="24" color="#2563eb">
              <settings-outline />
            </n-icon>
          </div>
          <span v-show="!collapsed" class="logo-text">Pro-Flow</span>
        </div>
      </div>

      <div class="sider-menu">
        <n-menu
          :value="activeKey"
          :options="menuOptions"
          :collapsed="collapsed"
          :collapsed-width="64"
          :collapsed-icon-size="22"
          class="custom-menu"
          inverted
          @update:value="handleMenuSelect"
        />
      </div>

      <div class="sider-footer">
        <n-button
          text
          block
          class="collapse-btn"
          @click="toggleCollapse"
        >
          <template #icon>
            <n-icon size="18">
              <chevron-back-outline v-if="!collapsed" />
              <chevron-forward-outline v-else />
            </n-icon>
          </template>
          <span v-show="!collapsed">收起菜单</span>
        </n-button>
      </div>
    </n-layout-sider>

    <n-layout class="main-content-layout">
      <n-layout-header class="layout-header" bordered>
        <div class="header-left">
          <n-button text class="menu-toggle-btn" @click="toggleCollapse">
            <template #icon>
              <n-icon size="20">
                <menu-outline />
              </n-icon>
            </template>
          </n-button>
          <n-breadcrumb class="breadcrumb">
            <n-breadcrumb-item v-for="item in breadcrumbItems" :key="item.key">
              {{ item.label }}
            </n-breadcrumb-item>
          </n-breadcrumb>
        </div>
        <div class="header-right">
          <n-dropdown
            trigger="click"
            :options="dropdownOptions"
            @select="handleDropdownSelect"
          >
            <div class="user-info">
              <n-space align="center" size="medium">
                <n-tag :type="roleTagType" size="small" round>
                  {{ roleName }}
                </n-tag>
                <span class="user-name">{{ userDisplayName }}</span>
                <n-avatar round :size="36" color="#2563eb">
                  {{ userDisplayName.charAt(0).toUpperCase() }}
                </n-avatar>
              </n-space>
            </div>
          </n-dropdown>
        </div>
      </n-layout-header>

      <n-layout-content class="layout-content">
        <router-view />
      </n-layout-content>
    </n-layout>
  </n-layout>
</template>

<style scoped>
.main-layout {
  height: 100vh;
}

.layout-sider {
  background: #1e293b;
  border-right: none !important;
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
}

.layout-sider :deep(.n-layout-sider-scroll-container) {
  background: #1e293b;
  display: flex;
  flex-direction: column;
}

.sider-header {
  padding: 20px 16px;
  border-bottom: 1px solid #334155;
}

.logo-area {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.logo-icon :deep(.n-icon) {
  color: #ffffff;
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  color: #ffffff;
  letter-spacing: 0.5px;
  white-space: nowrap;
}

.sider-menu {
  flex: 1;
  padding: 12px 8px;
  overflow-y: auto;
}

.sider-menu :deep(.custom-menu) {
  background: transparent;
  border: none;
}

.sider-menu :deep(.n-menu-item) {
  border-radius: 8px;
  margin: 2px 0;
  transition: all 0.2s ease;
  height: 44px;
}

.sider-menu :deep(.n-menu-item-content) {
  padding: 0 12px !important;
}

.sider-menu :deep(.n-menu-item .n-menu-item-content__icon) {
  color: #94a3b8;
}

.sider-menu :deep(.n-menu-item .n-menu-item-content__label) {
  color: #cbd5e1;
  font-weight: 500;
}

.sider-menu :deep(.n-menu-item:hover) {
  background: #334155;
}

.sider-menu :deep(.n-menu-item--selected) {
  background: #2563eb !important;
}

.sider-menu :deep(.n-menu-item--selected .n-menu-item-content__icon) {
  color: #ffffff !important;
}

.sider-menu :deep(.n-menu-item--selected .n-menu-item-content__label) {
  color: #ffffff !important;
}

.sider-footer {
  padding: 12px 8px;
  border-top: 1px solid #334155;
}

.collapse-btn {
  color: #94a3b8 !important;
  height: 40px;
  border-radius: 8px;
}

.collapse-btn:hover {
  background: #334155 !important;
  color: #cbd5e1 !important;
}

.main-content-layout {
  background: #f1f5f9;
}

.layout-header {
  height: 64px;
  background: #f8fafc;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  border-bottom: 1px solid #e2e8f0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.menu-toggle-btn {
  color: #475569;
}

.menu-toggle-btn:hover {
  background: #e2e8f0 !important;
}

.breadcrumb {
  font-size: 14px;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 8px;
  transition: background 0.2s ease;
}

.user-info:hover {
  background: #e2e8f0;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: #334155;
}

.layout-content {
  padding: 24px;
}

.worker-mode .sider-menu :deep(.n-menu-item) {
  height: 56px;
}

.worker-mode .sider-menu :deep(.n-menu-item-content) {
  padding: 0 16px !important;
}

.worker-mode .sider-menu :deep(.n-menu-item-content__icon) {
  font-size: 22px !important;
}

.worker-mode .sider-menu :deep(.n-menu-item-content__label) {
  font-size: 16px !important;
}

.worker-mode .collapse-btn {
  height: 48px;
}

.worker-mode .layout-header {
  height: 72px;
}

.worker-mode .layout-content {
  padding: 32px;
}
</style>
