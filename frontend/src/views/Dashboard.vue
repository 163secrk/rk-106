<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import {
  NCard,
  NGrid,
  NGi,
  NStatistic,
  NIcon,
  NSpin,
  NProgress,
  NEmpty
} from 'naive-ui'
import {
  DocumentTextOutline,
  ShieldCheckmarkOutline,
  ConstructOutline,
  WalletOutline
} from '@vicons/ionicons5'
import * as echarts from 'echarts/core'
import { BarChart, PieChart, LineChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

echarts.use([
  BarChart,
  PieChart,
  LineChart,
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
  CanvasRenderer
])
import { getDashboardStats } from '@/api/dashboard'
import type { DashboardStats } from '@/types'

const loading = ref(true)
const stats = ref<DashboardStats | null>(null)

let yieldChart: echarts.ECharts | null = null
let scrapChart: echarts.ECharts | null = null
let trendChart: echarts.ECharts | null = null
let refreshTimer: ReturnType<typeof setInterval> | null = null

const fetchStats = async () => {
  try {
    const data = await getDashboardStats()
    stats.value = data
    await nextTick()
    renderCharts()
  } catch {
  } finally {
    loading.value = false
  }
}

const formatSalary = (val: number) => {
  return val.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const renderYieldChart = () => {
  const el = document.getElementById('yield-chart')
  if (!el || !stats.value) return
  if (!yieldChart) {
    yieldChart = echarts.init(el)
  }
  const data = stats.value.process_yield
  yieldChart.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params: any) => {
        const p = params[0]
        const item = data[p.dataIndex]
        return `${item.name}<br/>良品率: ${item.yield_rate}%<br/>合格: ${item.passed} / 总数: ${item.total}`
      }
    },
    grid: { top: 20, bottom: 40, left: 60, right: 20 },
    xAxis: {
      type: 'category',
      data: data.map(d => d.name),
      axisLabel: { fontSize: 12, color: '#64748b', rotate: data.length > 6 ? 30 : 0 }
    },
    yAxis: {
      type: 'value',
      max: 100,
      axisLabel: { formatter: '{value}%', fontSize: 12, color: '#64748b' },
      splitLine: { lineStyle: { type: 'dashed', color: '#e2e8f0' } }
    },
    series: [{
      type: 'bar',
      data: data.map(d => d.yield_rate),
      barWidth: data.length > 6 ? 24 : 36,
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: (params: any) => {
          const val = params.value
          if (val >= 95) return '#22c55e'
          if (val >= 80) return '#f59e0b'
          return '#ef4444'
        }
      },
      label: {
        show: true,
        position: 'top',
        formatter: '{c}%',
        fontSize: 11,
        color: '#334155'
      }
    }]
  }, true)
}

const renderScrapChart = () => {
  const el = document.getElementById('scrap-chart')
  if (!el || !stats.value) return
  if (!scrapChart) {
    scrapChart = echarts.init(el)
  }
  const data = stats.value.product_scrap
  const pieData = data.map(d => ({ name: d.name, value: d.scrapped }))
  const colorPalette = ['#ef4444', '#f97316', '#f59e0b', '#eab308', '#84cc16', '#22c55e', '#06b6d4', '#3b82f6']
  scrapChart.setOption({
    tooltip: {
      trigger: 'item',
      formatter: (params: any) => {
        const item = data[params.dataIndex]
        return `${item.name}<br/>报废: ${item.scrapped}件<br/>报废率: ${item.scrap_rate}%<br/>总数: ${item.total}`
      }
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'center',
      textStyle: { fontSize: 12, color: '#64748b' }
    },
    color: colorPalette,
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['35%', '50%'],
      avoidLabelOverlap: true,
      label: {
        show: true,
        formatter: '{b}\n{d}%',
        fontSize: 11,
        color: '#334155'
      },
      emphasis: {
        label: { show: true, fontWeight: 'bold', fontSize: 14 }
      },
      data: pieData
    }]
  }, true)
}

const renderTrendChart = () => {
  const el = document.getElementById('trend-chart')
  if (!el || !stats.value) return
  if (!trendChart) {
    trendChart = echarts.init(el)
  }
  const data = stats.value.daily_trend
  trendChart.setOption({
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => `${params[0].axisValue}<br/>报工: ${params[0].value}条`
    },
    grid: { top: 20, bottom: 30, left: 50, right: 20 },
    xAxis: {
      type: 'category',
      data: data.map(d => d.date),
      axisLabel: { fontSize: 11, color: '#64748b', interval: 4 }
    },
    yAxis: {
      type: 'value',
      axisLabel: { fontSize: 12, color: '#64748b' },
      splitLine: { lineStyle: { type: 'dashed', color: '#e2e8f0' } }
    },
    series: [{
      type: 'line',
      data: data.map(d => d.count),
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      lineStyle: { width: 2, color: '#3b82f6' },
      itemStyle: { color: '#3b82f6' },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(59,130,246,0.25)' },
          { offset: 1, color: 'rgba(59,130,246,0.02)' }
        ])
      }
    }]
  }, true)
}

const renderCharts = () => {
  renderYieldChart()
  renderScrapChart()
  renderTrendChart()
}

const handleResize = () => {
  yieldChart?.resize()
  scrapChart?.resize()
  trendChart?.resize()
}

onMounted(() => {
  fetchStats()
  window.addEventListener('resize', handleResize)
  refreshTimer = setInterval(fetchStats, 60000)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
  yieldChart?.dispose()
  scrapChart?.dispose()
  trendChart?.dispose()
  yieldChart = null
  scrapChart = null
  trendChart = null
})
</script>

<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">生产看板</h1>
      <p class="page-desc">实时掌握生产进度，一目了然</p>
    </div>

    <n-spin :show="loading">
      <template v-if="stats">
        <n-grid :cols="4" :x-gap="16" :y-gap="16" class="stat-grid">
          <n-gi>
            <n-card class="stat-card" hoverable>
              <div class="stat-item">
                <div class="stat-icon icon-blue">
                  <n-icon size="26"><document-text-outline /></n-icon>
                </div>
                <div class="stat-content">
                  <n-statistic label="今日报工总数" :value="stats.today_report_count" />
                  <span class="stat-sub">条</span>
                </div>
              </div>
            </n-card>
          </n-gi>
          <n-gi>
            <n-card class="stat-card" hoverable>
              <div class="stat-item">
                <div class="stat-icon icon-orange">
                  <n-icon size="26"><shield-checkmark-outline /></n-icon>
                </div>
                <div class="stat-content">
                  <n-statistic label="待质检条数" :value="stats.pending_inspection_count" />
                  <span class="stat-sub">待处理</span>
                </div>
              </div>
            </n-card>
          </n-gi>
          <n-gi>
            <n-card class="stat-card" hoverable>
              <div class="stat-item">
                <div class="stat-icon icon-green">
                  <n-icon size="26"><construct-outline /></n-icon>
                </div>
                <div class="stat-content">
                  <n-statistic label="在产工单数" :value="stats.in_progress_order_count" />
                  <span class="stat-sub">进行中</span>
                </div>
              </div>
            </n-card>
          </n-gi>
          <n-gi>
            <n-card class="stat-card" hoverable>
              <div class="stat-item">
                <div class="stat-icon icon-purple">
                  <n-icon size="26"><wallet-outline /></n-icon>
                </div>
                <div class="stat-content">
                  <n-statistic label="本月工资总额">
                    <template #prefix>¥</template>
                    <template #default>{{ formatSalary(stats.monthly_salary_total) }}</template>
                  </n-statistic>
                  <span class="stat-sub">已通过质检</span>
                </div>
              </div>
            </n-card>
          </n-gi>
        </n-grid>

        <n-grid :cols="2" :x-gap="16" :y-gap="16">
          <n-gi>
            <n-card class="chart-card" title="各工序良品率排行">
              <div id="yield-chart" class="chart-container"></div>
              <n-empty v-if="stats.process_yield.length === 0" description="暂无工序良品率数据" />
            </n-card>
          </n-gi>
          <n-gi>
            <n-card class="chart-card" title="各产品报废率">
              <div id="scrap-chart" class="chart-container"></div>
              <n-empty v-if="stats.product_scrap.length === 0" description="暂无报废数据" />
            </n-card>
          </n-gi>
        </n-grid>

        <n-card class="content-card" title="生产工单进度总览">
          <div class="progress-table" v-if="stats.order_progress.length > 0">
            <div
              v-for="order in stats.order_progress"
              :key="order.id"
              class="progress-row"
              :class="{ 'overdue-row': order.is_overdue }"
            >
              <div class="progress-info">
                <span class="order-no">{{ order.order_no }}</span>
                <span class="product-name">{{ order.product_name }}</span>
                <span class="order-qty">× {{ order.quantity }}</span>
                <span class="order-deadline">截止: {{ order.deadline }}</span>
              </div>
              <div class="progress-bar-wrap">
                <n-progress
                  type="line"
                  :percentage="order.progress"
                  :color="order.is_overdue ? '#ef4444' : '#22c55e'"
                  :rail-color="order.is_overdue ? '#fecaca' : '#dcfce7'"
                  :height="18"
                  :border-radius="4"
                  indicator-placement="inside"
                >
                  {{ order.progress }}%
                </n-progress>
              </div>
              <div class="progress-detail">
                <span class="detail-tag reported">已报 {{ order.reported_quantity }}</span>
                <span class="detail-tag pending" v-if="!order.is_overdue">待报 {{ order.quantity - order.reported_quantity > 0 ? order.quantity - order.reported_quantity : 0 }}</span>
                <span class="detail-tag overdue" v-if="order.is_overdue">超期</span>
              </div>
            </div>
          </div>
          <n-empty v-else description="暂无进行中的工单" />
        </n-card>

        <n-card class="chart-card" title="最近30天报工总量走势">
          <div id="trend-chart" class="chart-container trend-chart"></div>
        </n-card>
      </template>
    </n-spin>
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

.chart-card {
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.chart-card :deep(.n-card-header) {
  padding: 16px 24px;
  border-bottom: 1px solid #f1f5f9;
  font-weight: 600;
  font-size: 15px;
  color: #1e293b;
}

.chart-card :deep(.n-card__content) {
  padding: 16px 20px;
}

.chart-container {
  width: 100%;
  height: 300px;
}

.trend-chart {
  height: 260px;
}

.content-card {
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.content-card :deep(.n-card-header) {
  padding: 16px 24px;
  border-bottom: 1px solid #f1f5f9;
  font-weight: 600;
  font-size: 15px;
  color: #1e293b;
}

.content-card :deep(.n-card__content) {
  padding: 16px 24px;
}

.progress-table {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.progress-row {
  padding: 14px 16px;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  transition: all 0.2s;
}

.progress-row:hover {
  border-color: #cbd5e1;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.progress-row.overdue-row {
  background: #fef2f2;
  border-color: #fecaca;
}

.progress-row.overdue-row:hover {
  border-color: #fca5a5;
}

.progress-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}

.order-no {
  font-weight: 600;
  font-size: 14px;
  color: #1e293b;
}

.product-name {
  font-size: 13px;
  color: #475569;
}

.order-qty {
  font-size: 13px;
  color: #64748b;
}

.order-deadline {
  font-size: 12px;
  color: #94a3b8;
  margin-left: auto;
}

.overdue-row .order-deadline {
  color: #ef4444;
  font-weight: 600;
}

.progress-bar-wrap {
  margin-bottom: 8px;
}

.progress-bar-wrap :deep(.n-progress-graph-line-indicator) {
  font-size: 11px;
  font-weight: 600;
}

.progress-detail {
  display: flex;
  gap: 8px;
}

.detail-tag {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 500;
}

.detail-tag.reported {
  background: #dcfce7;
  color: #166534;
}

.detail-tag.pending {
  background: #dbeafe;
  color: #1e40af;
}

.detail-tag.overdue {
  background: #fee2e2;
  color: #991b1b;
  font-weight: 600;
}
</style>
