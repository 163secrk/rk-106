<script setup lang="ts">
import { ref, reactive, computed, onMounted, h, watch } from 'vue'
import {
  NCard,
  NIcon,
  NDataTable,
  NTag,
  NSpace,
  NEmpty,
  NButton,
  NModal,
  useMessage,
  useDialog,
  NSelect,
  NStatistic,
  NDescriptions,
  NDescriptionsItem,
  NTabs,
  NTabPane,
  NAlert,
  NTimeline,
  NTimelineItem,
  NDivider,
  NSpin,
  NTooltip
} from 'naive-ui'
import type { SelectOption, DataTableColumns } from 'naive-ui'
import {
  CashOutline,
  RefreshOutline,
  CheckmarkCircleOutline,
  CreateOutline,
  EyeOutline,
  DocumentTextOutline,
  TimeOutline,
  PersonOutline,
  LayersOutline,
  ShieldCheckmarkOutline,
  AlertCircleOutline,
  SyncOutline,
  FileTrayOutline
} from '@vicons/ionicons5'
import {
  getSalarySummary,
  getSalaryFilterOptions,
  getWorkReportTrace,
  getSalarySettlements,
  getSalarySettlementDetail,
  createSalarySettlement
} from '@/api/workOrder'
import type {
  SalarySummaryGrouped,
  SalaryFilterOptions,
  WorkReportTraceData,
  WorkReportTraceChainItem,
  SalarySettlement,
  SalarySettlementFull
} from '@/types'

const message = useMessage()
const dialog = useDialog()

const loading = ref(false)
const salaryData = ref<SalarySummaryGrouped[]>([])
const filterOptions = ref<SalaryFilterOptions | null>(null)
const settlements = ref<SalarySettlement[]>([])
const settlementsLoading = ref(false)

const filterForm = reactive({
  month: '' as string,
  worker_id: 0 as number,
  work_order_id: 0 as number,
  process_id: 0 as number
})

const activeTab = ref<'summary' | 'history'>('summary')

const traceModalVisible = ref(false)
const traceLoading = ref(false)
const traceData = ref<WorkReportTraceData | null>(null)
const currentTraceReportId = ref<number | null>(null)

const settlementModalVisible = ref(false)
const settlementLoading = ref(false)
const settlementDetail = ref<SalarySettlementFull | null>(null)

const monthOptions = computed<SelectOption[]>(() => {
  if (!filterOptions.value) return []
  return [
    { label: '全部月份', value: '' },
    ...filterOptions.value.months.map(m => ({ label: `${m}月`, value: m }))
  ]
})

const workerOptions = computed<SelectOption[]>(() => {
  if (!filterOptions.value) return []
  return [
    { label: '全部工人', value: 0 },
    ...filterOptions.value.workers.map(w => ({ label: w.name, value: w.id }))
  ]
})

const workOrderOptions = computed<SelectOption[]>(() => {
  if (!filterOptions.value) return []
  return [
    { label: '全部工单', value: 0 },
    ...filterOptions.value.work_orders.map(w => ({ label: w.order_no, value: w.id }))
  ]
})

const processOptions = computed<SelectOption[]>(() => {
  if (!filterOptions.value) return []
  return [
    { label: '全部工序', value: 0 },
    ...filterOptions.value.processes.map(p => ({ label: p.name, value: p.id }))
  ]
})

const totalSalary = computed(() => {
  return salaryData.value.reduce((sum, d) => sum + d.total_amount, 0)
})

const totalPassedQuantity = computed(() => {
  return salaryData.value.reduce((sum, d) => sum + d.total_passed, 0)
})

const workerCount = computed(() => {
  return salaryData.value.length
})

const totalReportCount = computed(() => {
  return salaryData.value.reduce((sum, d) => sum + d.report_count, 0)
})

interface FlatSalaryRow {
  rowKey: string
  worker_id: number
  worker_name: string
  settlement_month: string
  work_order_no: string
  process_name: string
  total_passed: number
  unit_price: number
  subtotal: number
  final_amount: number
  report_ids: number[]
  isSummaryRow: boolean
  isDetailRow: boolean
  parentWorkerId?: number
  total_amount?: number
  report_count?: number
}

const flatTableData = computed<FlatSalaryRow[]>(() => {
  const result: FlatSalaryRow[] = []
  for (const workerData of salaryData.value) {
    result.push({
      rowKey: `worker-${workerData.worker_id}`,
      worker_id: workerData.worker_id,
      worker_name: workerData.worker_name,
      settlement_month: workerData.settlement_month,
      work_order_no: '',
      process_name: '',
      total_passed: workerData.total_passed,
      unit_price: 0,
      subtotal: 0,
      final_amount: workerData.total_amount,
      report_ids: [],
      isSummaryRow: true,
      isDetailRow: false,
      total_amount: workerData.total_amount,
      report_count: workerData.report_count
    })
    for (const detail of workerData.details) {
      result.push({
        rowKey: `detail-${workerData.worker_id}-${detail.work_order_id}-${detail.work_order_process_id}`,
        worker_id: workerData.worker_id,
        worker_name: '',
        settlement_month: '',
        work_order_no: detail.work_order_no,
        process_name: detail.process_name,
        total_passed: detail.total_passed,
        unit_price: detail.unit_price,
        subtotal: detail.subtotal,
        final_amount: detail.final_amount,
        report_ids: detail.report_ids,
        isSummaryRow: false,
        isDetailRow: true,
        parentWorkerId: workerData.worker_id
      })
    }
  }
  return result
})

const salaryColumns: DataTableColumns<FlatSalaryRow> = [
  {
    title: '工人姓名',
    key: 'worker_name',
    width: 140,
    render: (row) => {
      if (row.isSummaryRow) {
        return h('div', { style: 'font-weight: 600; color: #1e293b; display: flex; align-items: center; gap: 6px;' }, [
          h(NIcon, { size: 18, color: '#3b82f6' }, { default: () => h(PersonOutline) }),
          row.worker_name
        ])
      }
      return ''
    }
  },
  {
    title: '月份',
    key: 'settlement_month',
    width: 120,
    render: (row) => {
      if (row.isSummaryRow) {
        return row.settlement_month
          ? h(NTag, { type: 'info', size: 'small' }, { default: () => `${row.settlement_month}月` })
          : h(NTag, { type: 'default', size: 'small' }, { default: () => '全部' })
      }
      return ''
    }
  },
  {
    title: '工单',
    key: 'work_order_no',
    width: 160,
    render: (row) => {
      if (row.isDetailRow) {
        return h('span', { style: 'color: #475569;' }, [
          h(NIcon, { size: 14, style: 'margin-right: 4px; vertical-align: middle;' }, { default: () => h(DocumentTextOutline) }),
          row.work_order_no
        ])
      }
      if (row.isSummaryRow && row.report_count) {
        return h('span', { style: 'color: #94a3b8; font-size: 13px;' }, `${row.report_count} 笔报工`)
      }
      return ''
    }
  },
  {
    title: '工序',
    key: 'process_name',
    width: 120,
    render: (row) => {
      if (row.isDetailRow) {
        return h(NTag, { type: 'info', size: 'small', round: true }, { default: () => row.process_name })
      }
      return ''
    }
  },
  {
    title: '合格件数',
    key: 'total_passed',
    width: 110,
    align: 'right',
    render: (row) => {
      const text = `${row.total_passed} 件`
      if (row.isSummaryRow) {
        return h(NTag, { type: 'success', size: 'medium' }, { default: () => text })
      }
      return h('span', { style: 'color: #059669;' }, text)
    }
  },
  {
    title: '单价(元)',
    key: 'unit_price',
    width: 110,
    align: 'right',
    render: (row) => {
      if (row.isSummaryRow) return h('span', { style: 'color: #94a3b8;' }, '-')
      return h('span', { style: 'font-family: monospace; color: #64748b;' }, row.unit_price.toFixed(4))
    }
  },
  {
    title: '小计(元)',
    key: 'subtotal',
    width: 120,
    align: 'right',
    render: (row) => {
      if (row.isSummaryRow) return h('span', { style: 'color: #94a3b8;' }, '-')
      return h('span', { style: 'font-family: monospace; color: #475569;' }, row.subtotal.toFixed(4))
    }
  },
  {
    title: '合计(元)',
    key: 'final_amount',
    width: 140,
    align: 'right',
    render: (row) => {
      const amount = row.isSummaryRow ? (row.total_amount ?? 0) : row.final_amount
      const content = h('div', {
        style: row.isSummaryRow
          ? 'color: #dc2626; font-weight: 700; font-size: 15px; font-family: monospace;'
          : 'color: #059669; font-weight: 600; cursor: pointer; text-decoration: underline; font-family: monospace;'
      }, `¥${amount.toFixed(2)}`)

      if (row.isDetailRow && row.report_ids.length > 0) {
        return h(NTooltip, { trigger: 'hover', placement: 'top' }, {
          default: () => `点击查看 ${row.report_ids.length} 笔报工的追溯链`,
          trigger: () => h('div', {
            onClick: () => handleShowTrace(row.report_ids[0], row)
          }, content)
        })
      }
      return content
    }
  }
]

const settlementColumns: DataTableColumns<SalarySettlement> = [
  {
    title: '结算月份',
    key: 'settlement_month',
    width: 130,
    render: (row) => {
      return h('div', { style: 'display: flex; align-items: center; gap: 6px; font-weight: 600;' }, [
        h(NIcon, { size: 18, color: '#f59e0b' }, { default: () => h(FileTrayOutline) }),
        `${row.settlement_month}月`
      ])
    }
  },
  {
    title: '工人数量',
    key: 'total_workers',
    width: 100,
    align: 'center',
    render: (row) => h(NTag, { type: 'info', size: 'small' }, { default: () => `${row.total_workers} 人` })
  },
  {
    title: '报工笔数',
    key: 'total_reports',
    width: 100,
    align: 'center',
    render: (row) => h(NTag, { type: 'success', size: 'small' }, { default: () => `${row.total_reports} 笔` })
  },
  {
    title: '结算总金额',
    key: 'total_amount',
    width: 140,
    align: 'right',
    render: (row) => h('span', { style: 'color: #dc2626; font-weight: 700; font-family: monospace; font-size: 15px;' }, `¥${Number(row.total_amount).toFixed(2)}`)
  },
  {
    title: '状态',
    key: 'status_name',
    width: 100,
    align: 'center',
    render: (row) => {
      if (row.is_final) {
        return h(NTag, { type: 'success', round: true }, { default: () => '已锁定' })
      }
      return h(NTag, { type: 'warning', round: true }, { default: () => row.status_name })
    }
  },
  {
    title: '创建人',
    key: 'created_by_name',
    width: 100
  },
  {
    title: '创建时间',
    key: 'created_at',
    width: 180,
    render: (row) => new Date(row.created_at).toLocaleString('zh-CN')
  },
  {
    title: '操作',
    key: 'actions',
    width: 120,
    render: (row) => h(NButton, {
      size: 'small',
      type: 'primary',
      quaternary: true,
      onClick: () => handleViewSettlement(row.id)
    }, {
      icon: () => h(NIcon, { size: 14 }, { default: () => h(EyeOutline) }),
      default: () => '查看明细'
    })
  }
]

const settlementDetailColumns: DataTableColumns<any> = [
  {
    title: '工人姓名',
    key: 'worker_name',
    width: 120,
    render: (row: any) => h('div', { style: 'display: flex; align-items: center; gap: 4px;' }, [
      h(NIcon, { size: 14, color: '#3b82f6' }, { default: () => h(PersonOutline) }),
      row.worker_name
    ])
  },
  {
    title: '工单',
    key: 'work_order_no',
    width: 140
  },
  {
    title: '工序',
    key: 'process_name',
    width: 100,
    render: (row: any) => h(NTag, { type: 'info', size: 'small', round: true }, { default: () => row.process_name })
  },
  {
    title: '合格件数',
    key: 'passed_quantity',
    width: 90,
    align: 'right',
    render: (row: any) => h('span', { style: 'color: #059669;' }, `${row.passed_quantity} 件`)
  },
  {
    title: '单价',
    key: 'unit_price_display',
    width: 100,
    align: 'right',
    render: (row: any) => h('span', { style: 'font-family: monospace;' }, row.unit_price_display)
  },
  {
    title: '小计',
    key: 'subtotal_display',
    width: 110,
    align: 'right',
    render: (row: any) => h('span', { style: 'font-family: monospace; color: #475569;' }, row.subtotal_display)
  },
  {
    title: '最终金额',
    key: 'final_amount_display',
    width: 120,
    align: 'right',
    render: (row: any) => h('span', {
      style: 'color: #059669; font-weight: 600; cursor: pointer; text-decoration: underline; font-family: monospace;',
      onClick: () => handleShowTrace(row.work_report_id, null)
    }, `¥${row.final_amount_display}`)
  },
  {
    title: '报工时间',
    key: 'report_created_at',
    width: 170,
    render: (row: any) => new Date(row.report_created_at).toLocaleString('zh-CN')
  }
]

async function loadFilterOptions() {
  try {
    filterOptions.value = await getSalaryFilterOptions()
    if (filterOptions.value?.current_month && !filterForm.month) {
      filterForm.month = filterOptions.value.current_month
    }
  } catch (err) {
    message.error('加载筛选选项失败')
  }
}

async function loadSalarySummary() {
  loading.value = true
  try {
    const params: any = {}
    if (filterForm.month && filterForm.month !== '') params.month = filterForm.month
    if (filterForm.worker_id && filterForm.worker_id !== 0) params.worker_id = filterForm.worker_id
    if (filterForm.work_order_id && filterForm.work_order_id !== 0) params.work_order_id = filterForm.work_order_id
    if (filterForm.process_id && filterForm.process_id !== 0) params.process_id = filterForm.process_id
    salaryData.value = await getSalarySummary(params)
  } catch (err: any) {
    message.error(err.message || '加载工资数据失败')
  } finally {
    loading.value = false
  }
}

async function loadSettlements() {
  settlementsLoading.value = true
  try {
    settlements.value = await getSalarySettlements()
  } catch (err: any) {
    message.error(err.message || '加载结算单历史失败')
  } finally {
    settlementsLoading.value = false
  }
}

async function loadAll() {
  await loadFilterOptions()
  await Promise.all([loadSalarySummary(), loadSettlements()])
}

function handleResetFilter() {
  filterForm.month = filterOptions.value?.current_month || ''
  filterForm.worker_id = 0
  filterForm.work_order_id = 0
  filterForm.process_id = 0
}

async function handleShowTrace(reportId: number, _row: any) {
  currentTraceReportId.value = reportId
  traceModalVisible.value = true
  traceLoading.value = true
  traceData.value = null
  try {
    traceData.value = await getWorkReportTrace(reportId)
  } catch (err: any) {
    message.error(err.message || '加载追溯链失败')
  } finally {
    traceLoading.value = false
  }
}

async function handleViewSettlement(id: number) {
  settlementModalVisible.value = true
  settlementLoading.value = true
  settlementDetail.value = null
  try {
    settlementDetail.value = await getSalarySettlementDetail(id)
  } catch (err: any) {
    message.error(err.message || '加载结算单明细失败')
  } finally {
    settlementLoading.value = false
  }
}

function handleCreateSettlement() {
  const month = filterOptions.value?.current_month || new Date().toISOString().slice(0, 7)
  dialog.warning({
    title: '生成本月结算单',
    content: `确定要生成 ${month} 月的工资结算单吗？\n\n生成后，该月所有报工数据将进入只读状态，无法再修改或删除。请确认所有质检工作已完成。`,
    positiveText: '确认生成',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await createSalarySettlement(month)
        message.success('结算单生成成功，报工数据已锁定')
        await Promise.all([loadSalarySummary(), loadSettlements()])
      } catch (err: any) {
        message.error(err.message || '生成结算单失败')
      }
    }
  })
}

function formatDateTime(str: string | null) {
  if (!str) return '-'
  return new Date(str).toLocaleString('zh-CN')
}

function getTimelineType(item: WorkReportTraceChainItem) {
  if (item.chain_order === 0 && !item.is_rework) return 'success'
  if (item.is_rework) return 'warning'
  return 'success'
}

watch([
  () => filterForm.month,
  () => filterForm.worker_id,
  () => filterForm.work_order_id,
  () => filterForm.process_id
], () => {
  loadSalarySummary()
})

onMounted(() => {
  loadAll()
})
</script>

<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">工资结算</h1>
      <p class="page-desc">按自然月计件工资核算、结算单管理和薪资追溯</p>
    </div>

    <n-tabs v-model:value="activeTab" type="line" animated size="large" class="main-tabs">
      <n-tab-pane name="summary" tab="薪资总表">
        <template #tab>
          <div style="display: flex; align-items: center; gap: 6px;">
            <n-icon :size="16"><layers-outline /></n-icon>
            薪资总表
          </div>
        </template>
      </n-tab-pane>

      <n-tab-pane name="history" tab="结算单历史">
        <template #tab>
          <div style="display: flex; align-items: center; gap: 6px;">
            <n-icon :size="16"><file-tray-outline /></n-icon>
            结算单历史
          </div>
        </template>
      </n-tab-pane>
    </n-tabs>

    <!-- 薪资总表 -->
    <div v-show="activeTab === 'summary'">
      <n-card class="content-card" :bordered="false">
        <div class="card-header">
          <div class="card-title">
            <n-icon size="20" color="#10b981">
              <cash-outline />
            </n-icon>
            <span>薪资明细</span>
          </div>
          <n-space>
            <n-button size="small" type="primary" @click="handleCreateSettlement">
              <template #icon>
                <n-icon>
                  <create-outline />
                </n-icon>
              </template>
              生成本月结算单
            </n-button>
            <n-button size="small" @click="handleResetFilter">
              重置筛选
            </n-button>
            <n-button size="small" :loading="loading" @click="loadAll">
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
            v-model:value="filterForm.month"
            :options="monthOptions"
            placeholder="选择月份"
            style="width: 160px"
            clearable
          />
          <n-select
            v-model:value="filterForm.worker_id"
            :options="workerOptions"
            placeholder="选择工人"
            style="width: 160px"
            clearable
          />
          <n-select
            v-model:value="filterForm.work_order_id"
            :options="workOrderOptions"
            placeholder="选择工单"
            style="width: 180px"
            clearable
          />
          <n-select
            v-model:value="filterForm.process_id"
            :options="processOptions"
            placeholder="选择工序"
            style="width: 160px"
            clearable
          />
        </div>

        <n-alert type="info" class="info-alert">
          <template #icon>
            <n-icon>
              <alert-circle-outline />
            </n-icon>
          </template>
          工资按<strong>合格件数 × 工序单价</strong>计算。计算过程保留<strong>四位小数</strong>，最终金额<strong>四舍五入到两位</strong>。返工后重新质检合格的部分按合格件数计费。点击绿色金额可查看完整追溯链。
        </n-alert>

        <div class="stats-row">
          <n-statistic label="工人数量" :value="workerCount" suffix="人">
            <template #prefix>
              <n-icon size="20" color="#3b82f6"><person-outline /></n-icon>
            </template>
          </n-statistic>
          <n-statistic label="报工笔数" :value="totalReportCount" suffix="笔">
            <template #prefix>
              <n-icon size="20" color="#8b5cf6"><document-text-outline /></n-icon>
            </template>
          </n-statistic>
          <n-statistic label="合格总件数" :value="totalPassedQuantity" suffix="件">
            <template #prefix>
              <n-icon size="20" color="#10b981"><checkmark-circle-outline /></n-icon>
            </template>
          </n-statistic>
          <n-statistic label="工资总额" :value="totalSalary" :precision="2">
            <template #prefix>
              <n-icon size="20" color="#f59e0b" style="margin-right: 4px;"><cash-outline /></n-icon>
              ¥
            </template>
          </n-statistic>
        </div>

        <n-spin :show="loading">
          <n-data-table
            v-if="flatTableData.length > 0"
            :columns="salaryColumns"
            :data="flatTableData"
            :row-key="(row) => row.rowKey"
            :row-class-name="(row) => row.isSummaryRow ? 'summary-row-class' : 'detail-row-class'"
            :single-line="false"
            striped
            size="medium"
          />
          <n-empty v-else description="暂无工资数据" />
        </n-spin>
      </n-card>
    </div>

    <!-- 结算单历史 -->
    <div v-show="activeTab === 'history'">
      <n-card class="content-card" :bordered="false">
        <div class="card-header">
          <div class="card-title">
            <n-icon size="20" color="#f59e0b">
              <file-tray-outline />
            </n-icon>
            <span>历史结算单</span>
          </div>
          <n-space>
            <n-button size="small" type="primary" @click="handleCreateSettlement">
              <template #icon>
                <n-icon>
                  <create-outline />
                </n-icon>
              </template>
              生成本月结算单
            </n-button>
            <n-button size="small" :loading="settlementsLoading" @click="loadSettlements">
              <template #icon>
                <n-icon>
                  <refresh-outline />
                </n-icon>
              </template>
              刷新
            </n-button>
          </n-space>
        </div>

        <n-spin :show="settlementsLoading">
          <n-data-table
            v-if="settlements.length > 0"
            :columns="settlementColumns"
            :data="settlements"
            :row-key="(row) => row.id"
            striped
            size="medium"
          />
          <n-empty v-else description="暂无结算单记录" />
        </n-spin>
      </n-card>
    </div>

    <!-- 追溯链弹窗 -->
    <n-modal
      v-model:show="traceModalVisible"
      preset="card"
      :mask-closable="false"
      style="width: 720px; max-width: 90vw;"
      title="报工追溯链"
      :segmented="{ content: true }"
    >
      <n-spin :show="traceLoading">
        <div v-if="traceData" class="trace-content">
          <div class="trace-header">
            <n-descriptions label-placement="left" :column="1" bordered size="small">
              <n-descriptions-item label="工人">
                <n-icon :size="14" style="margin-right: 4px; vertical-align: middle; color: #3b82f6;"><person-outline /></n-icon>
                {{ traceData.main.worker_name }}
              </n-descriptions-item>
              <n-descriptions-item label="工单 / 工序">
                <n-icon :size="14" style="margin-right: 4px; vertical-align: middle; color: #8b5cf6;"><document-text-outline /></n-icon>
                {{ traceData.main.work_order_no }} / {{ traceData.main.process_name }}
              </n-descriptions-item>
              <n-descriptions-item label="最终合格件数">
                <n-tag type="success" size="small">{{ traceData.main.passed_quantity }} 件</n-tag>
              </n-descriptions-item>
              <n-descriptions-item label="工序单价">
                <span style="font-family: monospace;">¥{{ traceData.main.process_price.toFixed(4) }}</span>
              </n-descriptions-item>
              <n-descriptions-item label="中间计算(4位)">
                <span style="font-family: monospace; color: #475569;">¥{{ traceData.main.subtotal.toFixed(4) }}</span>
              </n-descriptions-item>
              <n-descriptions-item label="最终金额(2位)">
                <span style="font-family: monospace; color: #dc2626; font-weight: 700; font-size: 16px;">¥{{ traceData.main.final_amount.toFixed(2) }}</span>
              </n-descriptions-item>
            </n-descriptions>
          </div>

          <n-divider style="margin: 20px 0 12px;">
            <span style="font-weight: 600; color: #475569;">完整追溯流程</span>
          </n-divider>

          <div v-if="traceData.chain.length > 0" class="trace-timeline-wrapper">
            <n-timeline>
              <n-timeline-item
                v-for="(item, idx) in traceData.chain"
                :key="item.id"
                :type="getTimelineType(item)"
                :title="`第 ${idx + 1} 次报工${item.is_rework ? '（返工重报）' : ''}`"
                :time="formatDateTime(item.created_at)"
              >
                <div class="timeline-item-content">
                  <div class="timeline-item-row">
                    <span class="timeline-label">
                      <n-icon :size="14" style="margin-right: 3px; vertical-align: middle; color: #64748b;"><document-text-outline /></n-icon>
                      报工数量：
                    </span>
                    <n-tag type="default" size="small">{{ item.quantity }} 件</n-tag>
                  </div>
                  <div class="timeline-item-row">
                    <span class="timeline-label">
                      <n-icon :size="14" style="margin-right: 3px; vertical-align: middle; color: #10b981;"><checkmark-circle-outline /></n-icon>
                      合格件数：
                    </span>
                    <n-tag type="success" size="small">{{ item.passed_quantity }} 件</n-tag>
                  </div>
                  <div class="timeline-item-row" v-if="item.rework_quantity > 0">
                    <span class="timeline-label">
                      <n-icon :size="14" style="margin-right: 3px; vertical-align: middle; color: #f59e0b;"><sync-outline /></n-icon>
                      返工件数：
                    </span>
                    <n-tag type="warning" size="small">{{ item.rework_quantity }} 件</n-tag>
                  </div>
                  <div class="timeline-item-row" v-if="item.scrapped_quantity > 0">
                    <span class="timeline-label">
                      <n-icon :size="14" style="margin-right: 3px; vertical-align: middle; color: #ef4444;"><alert-circle-outline /></n-icon>
                      报废件数：
                    </span>
                    <n-tag type="error" size="small">{{ item.scrapped_quantity }} 件</n-tag>
                  </div>
                  <div class="timeline-item-row">
                    <span class="timeline-label">
                      <n-icon :size="14" style="margin-right: 3px; vertical-align: middle; color: #0891b2;"><shield-checkmark-outline /></n-icon>
                      质检：
                    </span>
                    <span>
                      <n-tag :type="item.status === 'passed' ? 'success' : item.status === 'rework' ? 'warning' : 'error'" size="small">
                        {{ item.status_name }}
                      </n-tag>
                      <span v-if="item.inspector_name" style="margin-left: 8px; color: #64748b;">
                        质检员：{{ item.inspector_name }}
                      </span>
                      <span v-if="item.inspection_time" style="margin-left: 8px; color: #94a3b8; font-size: 12px;">
                        {{ formatDateTime(item.inspection_time) }}
                      </span>
                    </span>
                  </div>
                  <div v-if="item.inspection_remark" class="timeline-remark">
                    <span class="timeline-label">质检备注：</span>{{ item.inspection_remark }}
                  </div>
                </div>
              </n-timeline-item>
            </n-timeline>
          </div>
        </div>
      </n-spin>
    </n-modal>

    <!-- 结算单明细弹窗 -->
    <n-modal
      v-model:show="settlementModalVisible"
      preset="card"
      :mask-closable="false"
      style="width: 900px; max-width: 95vw;"
      title="结算单明细"
      :segmented="{ content: true }"
    >
      <n-spin :show="settlementLoading">
        <div v-if="settlementDetail" class="settlement-detail-content">
          <div class="settlement-stats">
            <div class="settlement-month-stat">
              <div class="stat-label">
                <n-icon size="18" color="#f59e0b" style="margin-right: 6px; vertical-align: middle;"><time-outline /></n-icon>
                结算月份
              </div>
              <div class="stat-value month-value">{{ settlementDetail.settlement_month }}月</div>
            </div>
            <n-statistic label="工人数量" :value="settlementDetail.total_workers" suffix="人" />
            <n-statistic label="报工笔数" :value="settlementDetail.total_reports" suffix="笔" />
            <div class="settlement-amount-stat">
              <div class="stat-label">结算总金额</div>
              <div class="stat-value amount-value">¥{{ Number(settlementDetail.total_amount).toFixed(2) }}</div>
            </div>
          </div>

          <div class="settlement-meta">
            <n-tag type="success" round>数据已锁定</n-tag>
            <span style="color: #64748b;">创建人：{{ settlementDetail.created_by_name }}</span>
            <span style="color: #94a3b8;">创建时间：{{ formatDateTime(settlementDetail.created_at) }}</span>
          </div>

          <n-divider style="margin: 16px 0;" />

          <n-data-table
            :columns="settlementDetailColumns"
            :data="settlementDetail.details"
            :row-key="(row: any) => row.id"
            :max-height="450"
            striped
            size="small"
          />
        </div>
      </n-spin>
    </n-modal>
  </div>
</template>

<style scoped>
.page-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
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

.main-tabs {
  margin-bottom: -16px;
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
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
  padding: 20px;
  background: #f8fafc;
  border-radius: 8px;
}

.summary-row-class {
  background-color: #f0f9ff !important;
  font-weight: 500;
}

.summary-row-class:hover > td {
  background-color: #e0f2fe !important;
}

.detail-row-class {
  background-color: #ffffff !important;
}

.detail-row-class:hover > td {
  background-color: #f8fafc !important;
}

.trace-content {
  padding: 4px;
}

.trace-header {
  margin-bottom: 8px;
}

.trace-timeline-wrapper {
  max-height: 400px;
  overflow-y: auto;
  padding-right: 8px;
}

.timeline-item-content {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 4px 0;
}

.timeline-item-row {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-wrap: wrap;
}

.timeline-label {
  color: #64748b;
  font-size: 13px;
  min-width: 80px;
}

.timeline-remark {
  padding: 8px 12px;
  background: #fffbeb;
  border-left: 3px solid #f59e0b;
  border-radius: 4px;
  font-size: 13px;
  color: #78350f;
  margin-top: 4px;
}

.timeline-remark .timeline-label {
  color: #92400e;
  font-weight: 500;
}

.settlement-detail-content {
  padding: 4px;
}

.settlement-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

.settlement-month-stat,
.settlement-amount-stat {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.stat-label {
  font-size: 13px;
  color: #64748b;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  line-height: 1.2;
}

.month-value {
  color: #1e293b;
}

.amount-value {
  color: #dc2626;
  font-weight: 700;
  font-size: 28px;
}

.settlement-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 13px;
}
</style>
