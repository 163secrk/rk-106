<script setup lang="ts">
import { NCard, NGrid, NGi, NStatistic, NSpace, NIcon } from 'naive-ui'
import {
  DocumentTextOutline,
  TimeOutline,
  CheckmarkCircleOutline,
  TrendingUpOutline
} from '@vicons/ionicons5'
</script>

<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">生产看板</h1>
      <p class="page-desc">实时掌握生产进度，一目了然</p>
    </div>

    <n-grid :cols="4" :x-gap="20" :y-gap="20" class="stat-grid">
      <n-gi>
        <n-card class="stat-card" hoverable>
          <div class="stat-item">
            <div class="stat-icon icon-blue">
              <n-icon size="24">
                <document-text-outline />
              </n-icon>
            </div>
            <div class="stat-content">
              <n-statistic label="今日工单" :value="128" />
              <span class="stat-sub">较昨日 +12%</span>
            </div>
          </div>
        </n-card>
      </n-gi>
      <n-gi>
        <n-card class="stat-card" hoverable>
          <div class="stat-item">
            <div class="stat-icon icon-orange">
              <n-icon size="24">
                <time-outline />
              </n-icon>
            </div>
            <div class="stat-content">
              <n-statistic label="进行中" :value="42" />
              <span class="stat-sub">待处理</span>
            </div>
          </div>
        </n-card>
      </n-gi>
      <n-gi>
        <n-card class="stat-card" hoverable>
          <div class="stat-item">
            <div class="stat-icon icon-green">
              <n-icon size="24">
                <checkmark-circle-outline />
              </n-icon>
            </div>
            <div class="stat-content">
              <n-statistic label="已完成" :value="86" />
              <span class="stat-sub">完成率 67.2%</span>
            </div>
          </div>
        </n-card>
      </n-gi>
      <n-gi>
        <n-card class="stat-card" hoverable>
          <div class="stat-item">
            <div class="stat-icon icon-purple">
              <n-icon size="24">
                <trending-up-outline />
              </n-icon>
            </div>
            <div class="stat-content">
              <n-statistic label="合格率" value="98.5%" />
              <span class="stat-sub">质量优秀</span>
            </div>
          </div>
        </n-card>
      </n-gi>
    </n-grid>

    <n-card class="content-card" title="欢迎使用 Pro-Flow 工厂计件平台">
      <div class="welcome-content">
        <n-space vertical size="medium">
          <p>该模块正在建设中...</p>
          <p class="tip-text">生产数据看板、趋势图表、实时监控等功能将陆续上线</p>
        </n-space>
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

.stat-grid {
  margin-top: 0;
}

.stat-card {
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.stat-card :deep(.n-card__content) {
  padding: 20px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 52px;
  height: 52px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.icon-blue {
  background: #eff6ff;
  color: #2563eb;
}

.icon-orange {
  background: #fff7ed;
  color: #f97316;
}

.icon-green {
  background: #f0fdf4;
  color: #22c55e;
}

.icon-purple {
  background: #faf5ff;
  color: #a855f7;
}

.stat-content {
  flex: 1;
  min-width: 0;
}

.stat-content :deep(.n-statistic-label) {
  font-size: 13px;
  color: #64748b;
  margin-bottom: 4px;
}

.stat-content :deep(.n-statistic-value) {
  font-size: 24px;
  font-weight: 600;
  color: #1e293b;
}

.stat-sub {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 2px;
  display: block;
}

.content-card {
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.content-card :deep(.n-card-header) {
  padding: 20px 24px;
  border-bottom: 1px solid #f1f5f9;
  font-weight: 600;
}

.content-card :deep(.n-card__content) {
  padding: 24px;
}

.welcome-content {
  color: #64748b;
}

.tip-text {
  font-size: 13px;
  color: #94a3b8;
}
</style>
