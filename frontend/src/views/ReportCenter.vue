<script setup lang="ts">
import { ref, reactive, computed, onMounted, h } from 'vue'
import {
  NCard,
  NButton,
  NIcon,
  NDataTable,
  NTag,
  NProgress,
  NModal,
  NForm,
  NFormItem,
  NInputNumber,
  NInput,
  NSpace,
  NEmpty,
  NTabs,
  NTabPane,
  NDescriptions,
  NDescriptionsItem,
  NAlert,
  useMessage
} from 'naive-ui'
import type { FormInst, FormRules } from 'naive-ui'
import {
  ClipboardOutline,
  CheckmarkCircleOutline,
  TimeOutline,
  AlertCircleOutline,
  SendOutline,
  EyeOutline,
  DocumentTextOutline,
  RefreshOutline
} from '@vicons/ionicons5'
import {
  getWorkerWorkOrders,
  getWorkReports,
  createWorkReport
} from '@/api/workOrder'
import type {
  WorkerWorkOrder,
  WorkerWorkOrderProcess,
  WorkReport,
  CreateWorkReportRequest
} from '@/types'

const message = useMessage()

const loading = ref(false)
const workerWorkOrders = ref<WorkerWorkOrder[]>([])
const workReports = ref<WorkReport[]>([])

const showReportModal = ref(false)
const selectedWorkOrder = ref<WorkerWorkOrder | null>(null)
const selectedProcess = ref<WorkerWorkOrderProcess | null>(null)

const reportFormRef = ref<FormInst | null>(null)

const reportForm = reactive({
  work_order_id: null as number | null,
  work_order_process_id: null as number | null,
  quantity: null as number | null,
  remark: ''
})

const reportFormRules: FormRules = {
  quantity: [
    {
      required: true,
      type: 'number',
      message: '请输入报工数量',
      trigger: 'blur'
    },
    {
      type: 'number',
      min: 1,
      message: '报工数量必须大于0',
      trigger: 'blur'
    }
  ]
}

const expandedRowKeys = ref<number[]>([])

const currentRemaining = computed(() => {
  if (!selectedProcess.value) return 0
  return selectedProcess.value.remaining
})

const currentTotalQuantity = computed(() => {
  if (!selectedWorkOrder.value) return 0
  return selectedWorkOrder.value.quantity
})

const currentProgressPercent = computed(() => {
  if (!selectedProcess.value) return 0
  return selectedProcess.value.progress_percent
})

const currentTotalReported = computed(() => {
  if (!selectedProcess.value) return 0
  return selectedProcess.value.total_reported
})

const isOverLimit = computed(() => {
  if (!reportForm.quantity || !selectedProcess.value) return false
  return reportForm.quantity > selectedProcess.value.remaining
})

const workOrderColumns = [
  {
    type: 'expand' as const
  },
  {
    title: '工单号',
    key: 'order_no',
    width: 160
  },
  {
    title: '产品名称',
    key: 'product_name'
  },
  {
    title: '产品规格',
    key: 'product_spec'
  },
  {
    title: '生产数量',
    key: 'quantity',
    width: 100
  },
  {
    title: '截止日期',
    key: 'deadline',
    width: 120
  },
  {
    title: '状态',
    key: 'status_name',
    width: 100,
    render: (row: WorkerWorkOrder) => {
      const typeMap: Record<string, string> = {
        pending: 'default',
        in_progress: 'info',
        completed: 'success'
      }
      return h(NTag, { type: typeMap[row.status] as any }, { default: () => row.status_name })
    }
  },
  {
    title: '操作',
    key: 'action',
    width: 120,
    render: (row: WorkerWorkOrder) => {
      return h(
        NSpace,
        { size: 8 },
        {
          default: () => [
            h(
              NButton,
              {
                size: 'small',
                type: 'primary',
                onClick: () => handleViewProcesses(row)
              },
              { default: () => '选择工序' }
            )
          ]
        }
      )
    }
  }
]

const reportColumns = [
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
    title: '状态',
    key: 'status_name',
    width: 100,
    render: (row: WorkReport) => {
      const typeMap: Record<string, string> = {
        pending: 'warning',
        passed: 'success',
        rejected: 'error'
      }
      const iconMap: Record<string, any> = {
        pending: TimeOutline,
        passed: CheckmarkCircleOutline,
        rejected: AlertCircleOutline
      }
      return h(
        NTag,
        { type: typeMap[row.status] as any },
        {
          default: () => [
            h(NIcon, { size: 14, style: 'margin-right: 4px;' }, { default: () => h(iconMap[row.status]) }),
            row.status_name
          ]
        }
      )
    }
  },
  {
    title: '质检人',
    key: 'inspector_name',
    width: 100,
    render: (row: WorkReport) => row.inspector_name || '-'
  },
  {
    title: '质检备注',
    key: 'inspection_remark',
    render: (row: WorkReport) => row.inspection_remark || '-'
  },
  {
    title: '报工时间',
    key: 'created_at',
    width: 180,
    render: (row: WorkReport) => new Date(row.created_at).toLocaleString('zh-CN')
  }
]

function handleViewProcesses(workOrder: WorkerWorkOrder) {
  selectedWorkOrder.value = workOrder
  selectedProcess.value = null
  reportForm.work_order_id = workOrder.id
  reportForm.work_order_process_id = null
  reportForm.quantity = null
  reportForm.remark = ''
  showReportModal.value = true
}

function handleSelectProcess(process: WorkerWorkOrderProcess) {
  selectedProcess.value = process
  reportForm.work_order_process_id = process.id
  reportForm.quantity = null
}

function handleQuantityChange(value: number | null) {
  reportForm.quantity = value
}

async function handleSubmitReport() {
  if (!reportForm.work_order_id || !reportForm.work_order_process_id || !reportForm.quantity) {
    message.warning('请完善报工信息')
    return
  }

  if (isOverLimit.value) {
    message.error(`超出工单数量，剩余可报${currentRemaining.value}件`)
    return
  }

  try {
    loading.value = true
    const data: CreateWorkReportRequest = {
      work_order_id: reportForm.work_order_id,
      work_order_process_id: reportForm.work_order_process_id,
      quantity: reportForm.quantity,
      remark: reportForm.remark || undefined
    }
    await createWorkReport(data)
    message.success('报工成功')
    showReportModal.value = false
    await loadData()
  } catch (err: any) {
    message.error(err.message || '报工失败')
  } finally {
    loading.value = false
  }
}

async function loadWorkerWorkOrders() {
  try {
    workerWorkOrders.value = await getWorkerWorkOrders()
  } catch (err: any) {
    message.error('加载工单列表失败')
  }
}

async function loadWorkReports() {
  try {
    workReports.value = await getWorkReports()
  } catch (err: any) {
    message.error('加载报工记录失败')
  }
}

async function loadData() {
  loading.value = true
  try {
    await Promise.all([loadWorkerWorkOrders(), loadWorkReports()])
  } finally {
    loading.value = false
  }
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

function getStatusTagType(status: string) {
  const map: Record<string, string> = {
    pending: 'warning',
    passed: 'success',
    rejected: 'error'
  }
  return map[status] || 'default'
}

function getStatusIcon(status: string) {
  const map: Record<string, any> = {
    pending: TimeOutline,
    passed: CheckmarkCircleOutline,
    rejected: AlertCircleOutline
  }
  return map[status] || TimeOutline
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">报工中心</h1>
      <p class="page-desc">查看指派工单、提交报工、跟踪质检状态</p>
    </div>

    <n-tabs default-value="pending" size="large">
      <n-tab-pane name="pending" tab="待报工工单">
        <n-card class="content-card" :bordered="false">
          <div class="card-header">
            <div class="card-title">
              <n-icon size="20" color="#3b82f6">
                <document-text-outline />
              </n-icon>
              <span>指派给我的工单</span>
            </div>
            <n-button size="small" :loading="loading" @click="loadData">
              <template #icon>
                <n-icon>
                  <refresh-outline />
                </n-icon>
              </template>
              刷新
            </n-button>
          </div>

          <n-data-table
            :columns="workOrderColumns"
            :data="workerWorkOrders"
            :loading="loading"
            v-model:expanded-row-keys="expandedRowKeys"
            :row-key="(row) => row.id"
            striped
          >
            <template #expanded="{ row }">
              <div class="expanded-content">
                <h4 class="section-title">我负责的工序</h4>
                <div class="process-list">
                  <div
                    v-for="process in row.processes"
                    :key="process.id"
                    class="process-card"
                    :class="{ active: selectedProcess?.id === process.id && selectedWorkOrder?.id === row.id }"
                    @click="handleViewProcesses(row); handleSelectProcess(process)"
                  >
                    <div class="process-header">
                      <span class="process-name">{{ process.process_name }}</span>
                      <span class="process-price">¥{{ process.process_price }}/件</span>
                    </div>
                    <div class="process-progress">
                      <div class="progress-info">
                        <span>已报 {{ process.total_reported }} / {{ row.quantity }}</span>
                        <span class="remaining">剩余 {{ process.remaining }} 件</span>
                      </div>
                      <n-progress :percentage="process.progress_percent" :stroke-width="8" />
                    </div>
                  </div>
                </div>
              </div>
            </template>
          </n-data-table>
        </n-card>
      </n-tab-pane>

      <n-tab-pane name="history" tab="我的报工记录">
        <n-card class="content-card" :bordered="false">
          <div class="card-header">
            <div class="card-title">
              <n-icon size="20" color="#10b981">
                <clipboard-outline />
              </n-icon>
              <span>报工记录</span>
            </div>
            <n-button size="small" :loading="loading" @click="loadData">
              <template #icon>
                <n-icon>
                  <refresh-outline />
                </n-icon>
              </template>
              刷新
            </n-button>
          </div>

          <n-data-table
            :columns="reportColumns"
            :data="workReports"
            :loading="loading"
            :row-key="(row) => row.id"
            striped
          />
        </n-card>
      </n-tab-pane>
    </n-tabs>

    <n-modal
      v-model:show="showReportModal"
      preset="card"
      :title="`${selectedWorkOrder?.order_no} - 报工`"
      :mask-closable="false"
      style="width: 600px"
    >
      <div v-if="selectedWorkOrder" class="report-form-container">
        <n-descriptions :column="2" bordered size="small">
          <n-descriptions-item label="工单号">
            {{ selectedWorkOrder.order_no }}
          </n-descriptions-item>
          <n-descriptions-item label="产品名称">
            {{ selectedWorkOrder.product_name }}
          </n-descriptions-item>
          <n-descriptions-item label="产品规格">
            {{ selectedWorkOrder.product_spec }}
          </n-descriptions-item>
          <n-descriptions-item label="工单总量">
            {{ selectedWorkOrder.quantity }} 件
          </n-descriptions-item>
        </n-descriptions>

        <div class="section">
          <h4 class="section-title">选择工序</h4>
          <div class="process-select-list">
            <div
              v-for="process in selectedWorkOrder.processes"
              :key="process.id"
              class="process-select-item"
              :class="{ active: selectedProcess?.id === process.id }"
              @click="handleSelectProcess(process)"
            >
              <div class="process-select-header">
                <span class="process-name">{{ process.process_name }}</span>
                <n-tag v-if="selectedProcess?.id === process.id" type="primary" size="small">已选择</n-tag>
              </div>
            </div>
          </div>
        </div>

        <div v-if="selectedProcess" class="section">
          <h4 class="section-title">报工进度</h4>
          <div class="progress-section">
            <div class="progress-stats">
              <div class="stat-item">
                <span class="stat-label">工单总量</span>
                <span class="stat-value">{{ currentTotalQuantity }} 件</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">已报工</span>
                <span class="stat-value reported">{{ currentTotalReported }} 件</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">剩余可报</span>
                <span class="stat-value remaining">{{ currentRemaining }} 件</span>
              </div>
            </div>
            <div class="progress-bar-wrapper">
              <div class="progress-bar-labels">
                <span>完成进度</span>
                <span class="progress-percent">{{ currentProgressPercent }}%</span>
              </div>
              <n-progress
                :percentage="currentProgressPercent"
                :stroke-width="16"
                :show-indicator="false"
                color="#3b82f6"
                rail-color="#e2e8f0"
              />
            </div>
          </div>
        </div>

        <n-form
          ref="reportFormRef"
          :model="reportForm"
          :rules="reportFormRules"
          label-placement="top"
        >
          <div v-if="selectedProcess" class="section">
            <h4 class="section-title">填报数量</h4>

            <n-alert
              v-if="isOverLimit"
              type="error"
              class="limit-alert"
            >
              <template #icon>
                <n-icon>
                  <alert-circle-outline />
                </n-icon>
              </template>
              超出工单数量，剩余可报 {{ currentRemaining }} 件
            </n-alert>

            <div class="quantity-input-wrapper">
              <n-form-item path="quantity" :show-label="false">
                <n-input-number
                  v-model:value="reportForm.quantity"
                  :min="1"
                  :max="currentRemaining"
                  size="large"
                  class="big-input"
                  placeholder="请输入报工数量"
                  @update:value="handleQuantityChange"
                />
              </n-form-item>
              <span class="unit-label">件</span>
            </div>

            <div class="quick-buttons">
              <n-button
                size="small"
                @click="reportForm.quantity = Math.min(10, currentRemaining)"
              >
                +10
              </n-button>
              <n-button
                size="small"
                @click="reportForm.quantity = Math.min(50, currentRemaining)"
              >
                +50
              </n-button>
              <n-button
                size="small"
                @click="reportForm.quantity = Math.min(100, currentRemaining)"
              >
                +100
              </n-button>
              <n-button
                size="small"
                type="primary"
                @click="reportForm.quantity = currentRemaining"
              >
                全部报完
              </n-button>
            </div>

            <n-form-item label="备注" path="remark">
              <n-input
                v-model:value="reportForm.remark"
                type="textarea"
                placeholder="可选：填写报工备注"
                :autosize="{ minRows: 2, maxRows: 4 }"
              />
            </n-form-item>
          </div>
        </n-form>

        <div class="modal-footer">
          <n-button @click="showReportModal = false">取消</n-button>
          <n-button
            type="primary"
            :loading="loading"
            :disabled="!selectedProcess || !reportForm.quantity || isOverLimit"
            @click="handleSubmitReport"
          >
            <template #icon>
              <n-icon>
                <send-outline />
              </n-icon>
            </template>
            提交报工
          </n-button>
        </div>
      </div>
    </n-modal>
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

.process-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 12px;
}

.process-card {
  background: white;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.process-card:hover {
  border-color: #93c5fd;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.1);
}

.process-card.active {
  border-color: #3b82f6;
  background: #eff6ff;
}

.process-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.process-name {
  font-weight: 600;
  color: #1e293b;
  font-size: 15px;
}

.process-price {
  color: #10b981;
  font-weight: 600;
  font-size: 14px;
}

.process-progress {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: #64748b;
}

.progress-info .remaining {
  color: #f59e0b;
  font-weight: 500;
}

.report-form-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.process-select-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.process-select-item {
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  padding: 12px 16px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.process-select-item:hover {
  border-color: #93c5fd;
}

.process-select-item.active {
  border-color: #3b82f6;
  background: #eff6ff;
}

.process-select-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.progress-section {
  background: #f8fafc;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.progress-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.stat-item {
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-label {
  font-size: 13px;
  color: #64748b;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
}

.stat-value.reported {
  color: #3b82f6;
}

.stat-value.remaining {
  color: #f59e0b;
}

.progress-bar-wrapper {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.progress-bar-labels {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: #475569;
  font-weight: 500;
}

.progress-percent {
  color: #3b82f6;
  font-weight: 600;
}

.limit-alert {
  margin-bottom: 12px;
}

.quantity-input-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
}

.big-input {
  flex: 1;
}

.big-input :deep(.n-input-number) {
  height: 60px;
  font-size: 28px;
  font-weight: 600;
}

.big-input :deep(.n-input__input-el) {
  font-size: 28px !important;
  font-weight: 600 !important;
  text-align: center;
}

.big-input :deep(.n-input__suffix),
.big-input :deep(.n-input__prefix) {
  font-size: 20px;
}

.unit-label {
  font-size: 18px;
  color: #64748b;
  font-weight: 500;
  min-width: 30px;
}

.quick-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 8px;
}
</style>
