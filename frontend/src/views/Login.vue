<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { NForm, NFormItem, NInput, NButton, NIcon, useMessage, NSpace, NTag } from 'naive-ui'
import { LogInOutline, PersonOutline, LockClosedOutline } from '@vicons/ionicons5'
import { useUserStore } from '@/stores/user'
import { loginApi } from '@/api/user'
import type { LoginRequest } from '@/types'

const router = useRouter()
const route = useRoute()
const message = useMessage()
const userStore = useUserStore()

const loading = ref(false)

const formData: LoginRequest = reactive({
  username: '',
  password: ''
})

async function handleLogin(): Promise<void> {
  if (!formData.username || !formData.password) {
    message.warning('请输入用户名和密码')
    return
  }

  loading.value = true
  try {
    const result = await loginApi(formData)
    userStore.login(result.token, result.userInfo, result.roles)
    message.success('登录成功')
    const redirect = route.query.redirect as string
    router.push(redirect || '/dashboard')
  } catch (error) {
    const err = error as Error
    message.error(err.message || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <div class="logo-icon">
          <n-icon size="36" color="#2563eb">
            <log-in-outline />
          </n-icon>
        </div>
        <h1 class="system-title">
          <span class="title-highlight">Pro-Flow</span>
          <span class="title-sub">工厂计件平台</span>
        </h1>
        <p class="system-desc">Industrial Piece-rate Management System</p>
      </div>

      <n-form class="login-form" label-placement="top">
        <n-form-item label="账号">
          <n-input
            v-model:value="formData.username"
            placeholder="请输入账号"
            size="large"
            round
            @keyup.enter="handleLogin"
          >
            <template #prefix>
              <n-icon size="18" color="#94a3b8">
                <person-outline />
              </n-icon>
            </template>
          </n-input>
        </n-form-item>
        <n-form-item label="密码">
          <n-input
            v-model:value="formData.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            round
            show-password-on="click"
            @keyup.enter="handleLogin"
          >
            <template #prefix>
              <n-icon size="18" color="#94a3b8">
                <lock-closed-outline />
              </n-icon>
            </template>
          </n-input>
        </n-form-item>
        <n-form-item>
          <n-button
            type="primary"
            size="large"
            block
            :loading="loading"
            class="login-btn"
            @click="handleLogin"
          >
            <template #icon>
              <n-icon>
                <log-in-outline />
              </n-icon>
            </template>
            登 录
          </n-button>
        </n-form-item>
      </n-form>

      <div class="login-footer">
        <p class="test-label">测试账号</p>
        <div class="test-accounts">
          <n-space justify="center" size="small" wrap>
            <n-tag size="small" type="error">admin</n-tag>
            <n-tag size="small" type="info">leader01</n-tag>
            <n-tag size="small" type="success">worker01</n-tag>
            <n-tag size="small" type="warning">inspector01</n-tag>
          </n-space>
        </div>
        <p class="test-password">密码：123456</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  width: 100%;
  background: linear-gradient(135deg, #2c3e50 0%, #1a252f 100%);
  position: relative;
  overflow: hidden;
}

.login-container::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: 
    radial-gradient(circle at 20% 30%, rgba(37, 99, 235, 0.08) 0%, transparent 40%),
    radial-gradient(circle at 80% 70%, rgba(59, 130, 246, 0.06) 0%, transparent 40%);
  pointer-events: none;
}

.login-card {
  width: 420px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  padding: 40px 36px 32px;
  position: relative;
  z-index: 1;
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo-icon {
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
}

.system-title {
  font-size: 24px;
  font-weight: 700;
  margin: 0 0 8px 0;
  letter-spacing: 0.5px;
}

.title-highlight {
  color: #2563eb;
}

.title-sub {
  color: #1e293b;
  margin-left: 8px;
}

.system-desc {
  font-size: 12px;
  color: #94a3b8;
  margin: 0;
  letter-spacing: 1px;
  text-transform: uppercase;
}

.login-form {
  margin-bottom: 24px;
}

.login-btn {
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  background: #2563eb;
  border-color: #2563eb;
  border-radius: 8px;
}

.login-btn:hover {
  background: #1d4ed8 !important;
  border-color: #1d4ed8 !important;
}

.login-footer {
  border-top: 1px solid #e2e8f0;
  padding-top: 20px;
  text-align: center;
}

.test-label {
  font-size: 12px;
  color: #94a3b8;
  margin: 0 0 10px 0;
}

.test-accounts {
  margin-bottom: 8px;
}

.test-password {
  font-size: 13px;
  color: #64748b;
  margin: 0;
  font-weight: 500;
}
</style>
