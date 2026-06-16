<script setup lang="ts">
import { ref, reactive, computed, onMounted, h } from 'vue'
import {
  NCard,
  NIcon,
  NDataTable,
  NTag,
  NSpace,
  NEmpty,
  NDescriptions,
  NDescriptionsItem,
  NButton,
  useMessage,
  NSelect,
  NDatePicker,
  NStatistic
} from 'naive-ui'
import type { SelectOption } from 'naive-ui'
import {
  CashOutline,
  RefreshOutline,
  CheckmarkCircleOutline,
  TimeOutline,
  AlertCircleOutline
} from '@vicons/ionicons5'
import { getWorkReports, getWorkers } from '@/api/workOrder'
import type { WorkReport, User } from '@/types'

const message = useMessage()

const loading = ref(false)
const workReports = ref<WorkReport[]>([])
const workers = ref<User[]>([])

const filterForm = reactive({
  worker_id: null as number | null,
  date_range: null as [number, number] | null
})

const workerOptions = computed<SelectOption[]>(() => {
  return [
    { label: '全部工人', value: null },
    ...workers.value.map(w => ({ label: w.name, value: w.id }))
  ]
})

const filteredReports = computed(() => {
  let result = workReports.value.filter(r => r.status === 'passed')

  if (filterForm.worker_id) {
    result = result.filter(r => r.worker === filterForm.worker_id)
  }

  if (filterForm.date_range) {
    const [start, end] = filterForm.date_range
    result = result.filter(r => {
      const reportTime = new Date(r.created_at).getTime()
      return reportTime >= start && reportTime <= end
    })
  }

  return result
})

const workerSalaryData = computed(() => {
  const salaryMap = new Map<number, {
    worker_id: number
    worker_name: string
    total_passed: number
    total_amount: number
    details: WorkReport[]
  }>()

  for (const report of filteredReports.value) {
    const workerId = report.worker
    if (!salaryMap.has(workerId)) {
      salaryMap.set(workerId, {
        worker_id: workerId,
        worker_name: report.worker_name,
        total_passed: 0,
        total_amount: 0,
        details: []
      })
    }
    const data = salaryMap.get(workerId)!
    data.total_passed += report.passed_quantity
    data.total_amount += report.salary_amount || 0
    data.details.push(report)
  }

  return Array.from(salaryMap.values())
})

const totalSalary = computed(() => {
  return workerSalaryData.value.reduce((sum, d) => sum + d.total_amount, 0)
})

const totalPassedQuantity = computed(() => {
  return workerSalaryData.value.reduce((sum, d) => sum + d.total_passed, 0)
})

const workerCount = computed(() => {
  return workerSalaryData.value.length
})

const salaryColumns = [
  {
    title: '工人姓名',
    key: 'worker_name',
    width: 120
  },
  {
    title: '合格总件数',
    key: 'total_passed',
    width: 120,
    render: (row: any) => {
      return h(NTag, { type: 'success', size: 'large' }, { default: () => `${row.total_passed} 件` })
    }
  },
  {
    title: '工资金额',
    key: 'total_amount',
    width: 150,
    render: (row: any) => {
      return h('span', { style: 'color: #10b981; font-weight: 600; font-size: 16px;' }, `¥${row.total_amount.toFixed(2)}`)
    }
  }
]

const detailColumns = [
  {
    title: '工单号',
    key: 'work_order_no',
    width: 160
  },
  {
    title: '工序',
    key: 'process_name',
    width: 120
  },
  {
    title: '报工数量',
    key: 'quantity',
    width: 100
  },
  {
    title: '合格数量',
    key: 'passed_quantity',
    width: 100,
    render: (row: WorkReport) => {
      return h(NTag, { type: 'success', size: 'small' }, { default: () => `${row.passed_quantity} 件` })
    }
  },
  {
    title: '返工数量',
    key: 'rework_quantity',
    width: 100,
    render: (row: WorkReport) => {
      if (row.rework_quantity === 0) return '-'
      return h(NTag, { type: 'warning', size: 'small' }, { default: () => `${row.rework_quantity} 件` })
    }
  },
  {
    title: '报废数量',
    key: 'scrapped_quantity',
    width: 100,
    render: (row: WorkReport) => {
      if (row.scrapped_quantity === 0) return '-'
      return h(NTag, { type: 'error', size: 'small' }, { default: () => `${row.scrapped_quantity} 件` })
    }
  },
  {
    title: '质检时间',
    key: 'inspection_time',
    width: 180,
    render: (row: WorkReport) => row.inspection_time ? new Date(row.inspection_time).toLocaleString('zh-CN') : '-'
  }
]

async function loadWorkReports() {
  try {
    workReports.value = await getWorkReports()
  } catch (err: any) {
    message.error('加载报工记录失败')
  }
}

async function loadWorkers() {
  try {
    workers.value = await getWorkers()
  } catch (err: any) {
    message.error('加载工人列表失败')
  }
}

async function loadData() {
  loading.value = true
  try {
    await Promise.all([loadWorkReports(), loadWorkers()])
  } finally {
    loading.value = false
  }
}

function handleResetFilter() {
  filterForm.worker_id = null
  filterForm.date_range = null
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">工资结算</h1>
      <p class="page-desc">计件工资核算、工资条和薪资发放（按合格件数计费）</p>
    </div>

    <n-card class="content-card" :bordered="false">
      <div class="card-header">
        <div class="card-title">
          <n-icon size="20" color="#10b981">
            <cash-outline />
          </n-icon>
          <span>工资汇总</span>
        </div>
        <n-space>
          <n-button size="small" @click="handleResetFilter">
            重置筛选
          </n-button>
          <n-button size="small" :loading="loading" @click="loadData">
            <template #icon>
              <n-icon>
                <refresh-outline />
              </n-icon>
            </template>
            刷新
          </n-button>
        </n-space>
      </div>

      <div class="filter-bar">
        <n-select
          v-model:value="filterForm.worker_id"
          :options="workerOptions"
          placeholder="选择工人"
          style="width: 200px"
          clearable
        />
        <n-date-picker
          v-model:value="filterForm.date_range"
          type="daterange"
          placeholder="选择日期范围"
          clearable
        />
      </div>

      <n-alert type="info" class="info-alert">
        <template #icon>
          <n-icon>
            <alert-circle-outline />
          </n-icon>
        </template>
        工资按<strong>合格件数</strong>计算，返工和报废不计费。返工后重新质检合格的部分按合格件数计费。
      </n-alert>

      <div class="stats-row">
        <n-statistic label="工人数量" :value="workerCount" />
        <n-statistic label="合格总件数" :value="totalPassedQuantity" suffix="件" />
        <n-statistic label="工资总额" :value="totalSalary" prefix="¥" :precision="2" />
      </div>

      <n-data-table
        v-if="workerSalaryData.length > 0"
        :columns="salaryColumns"
        :data="workerSalaryData"
        :loading="loading"
        :row-key="(row) => row.worker_id"
        striped
      >
        <template #expanded="{ row }">
          <div class="expanded-content">
            <h4 class="section-title">工资明细 - {{ row.worker_name }}</h4>
            <n-data-table
              :columns="detailColumns"
              :data="row.details"
              :row-key="(r) => r.id"
              :row-class-name="(r) => r.scrapped_quantity > 0 ? 'scrap-row' : 'normal-row'"
              size="small"
              striped
            />
          </div>
        </template>
      </n-data-table>

      <n-empty v-else description="暂无工资数据" />
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
}

.content-card :deep(.n-card__content) {
  padding: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #334155;
}

.filter-bar {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.info-alert {
  margin-bottom: 20px;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 24px;
  padding: 20px;
  background: #f8fafc;
  border-radius: 8px;
}

.expanded-content {
  padding: 16px;
  background: #f8fafc;
  border-radius: 8px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #475569;
  margin: 0 0 12px 0;
}

.scrap-row {
  background: #fef2f2 !important;
}

.normal-row {
  background: white !important;
}
</style>
