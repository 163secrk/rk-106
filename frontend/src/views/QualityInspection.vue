<script setup lang="ts">
import { NCard, NIcon } from 'naive-ui'
import { ShieldCheckmarkOutline } from '@vicons/ionicons5'
</script>

<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">质检大厅</h1>
      <p class="page-desc">质量检验、缺陷记录和质量分析</p>
    </div>

    <n-card class="content-card">
      <div class="empty-state">
        <div class="empty-icon">
          <n-icon size="48" color="#cbd5e1">
            <shield-checkmark-outline />
          </n-icon>
        </div>
        <h3 class="empty-title">该模块正在建设中...</h3>
        <p class="empty-desc">质量检验、缺陷管理、质量报表分析等功能即将上线</p>
      </div>
    </n-card>
  </div>
</template>

<style scoped>
.page-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-header {
  margin-bottom: 4px;
}

.page-title {
  font-size: 22px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 6px 0;
}

.page-desc {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}

.content-card {
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  min-height: 400px;
}

.content-card :deep(.n-card__content) {
  padding: 24px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
}

.empty-icon {
  width: 96px;
  height: 96px;
  background: #f8fafc;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
}

.empty-title {
  font-size: 18px;
  font-weight: 600;
  color: #334155;
  margin: 0 0 8px 0;
}

.empty-desc {
  font-size: 14px;
  color: #94a3b8;
  margin: 0;
}
</style>
