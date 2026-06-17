<script setup lang="ts">
import { ref, reactive, computed, onMounted, h } from 'vue'
import {
  NCard,
  NIcon,
  NDataTable,
  NTag,
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
  NButton,
  useMessage,
  NBadge
} from 'naive-ui'
import type { FormInst, FormRules } from 'naive-ui'
import {
  ShieldCheckmarkOutline,
  CheckmarkCircleOutline,
  TimeOutline,
  AlertCircleOutline,
  SendOutline,
  EyeOutline,
  RefreshOutline,
  CheckmarkOutline,
  CloseCircleOutline,
  ArrowRedoOutline
} from '@vicons/ionicons5'
import {
  getInspectorPendingList,
  getInspectorHistoryList,
  submitQualityInspection
} from '@/api/workOrder'
import type {
  PendingWorkOrderGroup,
  InspectorWorkReport,
  QualityInspectionRequest
} from '@/types'

const message = useMessage()

const loading = ref(false)
const pendingGroups = ref<PendingWorkOrderGroup[]>([])
const historyReports = ref<InspectorWorkReport[]>([])

const showInspectModal = ref(false)
const selectedReport = ref<InspectorWorkReport | null>(null)

const inspectFormRef = ref<FormInst | null>(null)

const inspectForm = reactive({
  passed_quantity: null as number | null,
  rework_quantity: null as number | null,
  scrapped_quantity: null as number | null,
  inspection_remark: ''
})

const expandedRowKeys = ref<number[]>([])

const reportQuantity = computed(() => {
  return selectedReport.value?.quantity || 0
})

const totalInput = computed(() => {
  return (inspectForm.passed_quantity || 0) + (inspectForm.rework_quantity || 0) + (inspectForm.scrapped_quantity || 0)
})

const quantityMismatch = computed(() => {
  if (!selectedReport.value) return false
  return totalInput.value !== reportQuantity.value
})

const inspectFormRules: FormRules = {
  passed_quantity: [
    {
      required: true,
      type: 'number',
      message: '请输入合格件数',
      trigger: 'blur'
    },
    {
      type: 'number',
      min: 0,
      message: '合格件数不能为负数',
      trigger: 'blur'
    }
  ],
  rework_quantity: [
    {
      required: true,
      type: 'number',
      message: '请输入返工件数',
      trigger: 'blur'
    },
    {
      type: 'number',
      min: 0,
      message: '返工件数不能为负数',
      trigger: 'blur'
    }
  ],
  scrapped_quantity: [
    {
      required: true,
      type: 'number',
      message: '请输入报废件数',
      trigger: 'blur'
    },
    {
      type: 'number',
      min: 0,
      message: '报废件数不能为负数',
      trigger: 'blur'
    }
  ]
}

const workOrderColumns = [
  {
    title: '工单号',
    key: 'work_order_no',
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
    title: '工单总量',
    key: 'total_quantity',
    width: 100
  },
  {
    title: '待质检数',
    key: 'pending_count',
    width: 100,
    render: (row: PendingWorkOrderGroup) => {
      return h(NBadge, { value: row.reports.length, type: 'warning' }, {
        default: () => `${row.reports.length} 条`
      })
    }
  },
  {
    title: '操作',
    key: 'action',
    width: 140,
    render: (row: PendingWorkOrderGroup) => {
      const isExpanded = expandedRowKeys.value.includes(row.work_order_id)
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
                onClick: () => {
                  if (isExpanded) {
                    expandedRowKeys.value = expandedRowKeys.value.filter(id => id !== row.work_order_id)
                  } else {
                    expandedRowKeys.value = [...expandedRowKeys.value, row.work_order_id]
                  }
                }
              },
              { default: () => isExpanded ? '收起' : '查看质检' }
            )
          ]
        }
      )
    }
  }
]

const reportColumns = [
  {
    title: '工人姓名',
    key: 'worker_name',
    width: 120
  },
  {
    title: '工序名称',
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
    render: (row: InspectorWorkReport) => {
      const typeMap: Record<string, string> = {
        pending: 'warning',
        rework: 'info',
        passed: 'success',
        rejected: 'error'
      }
      const iconMap: Record<string, any> = {
        pending: TimeOutline,
        rework: ArrowRedoOutline,
        passed: CheckmarkCircleOutline,
        rejected: CloseCircleOutline
      }
      return h(
        NTag,
        { type: typeMap[row.status] as any, size: 'small' },
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
    title: '报工备注',
    key: 'remark',
    render: (row: InspectorWorkReport) => row.remark || '-'
  },
  {
    title: '报工时间',
    key: 'created_at',
    width: 180,
    render: (row: InspectorWorkReport) => new Date(row.created_at).toLocaleString('zh-CN')
  },
  {
    title: '操作',
    key: 'action',
    width: 120,
    render: (row: InspectorWorkReport) => {
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
                onClick: () => handleInspect(row)
              },
              { default: () => '质检' }
            )
          ]
        }
      )
    }
  }
]

const historyColumns = [
  {
    title: '工单号',
    key: 'work_order_no',
    width: 160
  },
  {
    title: '产品名称',
    key: 'product_name'
  },
  {
    title: '工序名称',
    key: 'process_name',
    width: 120
  },
  {
    title: '工人姓名',
    key: 'worker_name',
    width: 100
  },
  {
    title: '报工数量',
    key: 'quantity',
    width: 100
  },
  {
    title: '合格',
    key: 'passed_quantity',
    width: 80
  },
  {
    title: '返工',
    key: 'rework_quantity',
    width: 80
  },
  {
    title: '报废',
    key: 'scrapped_quantity',
    width: 80
  },
  {
    title: '状态',
    key: 'status_name',
    width: 100,
    render: (row: InspectorWorkReport) => {
      const typeMap: Record<string, string> = {
        passed: 'success',
        rejected: 'error',
        rework: 'info'
      }
      return h(NTag, { type: typeMap[row.status] as any, size: 'small' }, { default: () => row.status_name })
    }
  },
  {
    title: '质检时间',
    key: 'created_at',
    width: 180,
    render: (row: InspectorWorkReport) => new Date(row.created_at).toLocaleString('zh-CN')
  }
]

function handleInspect(report: InspectorWorkReport) {
  selectedReport.value = report
  inspectForm.passed_quantity = report.quantity
  inspectForm.rework_quantity = 0
  inspectForm.scrapped_quantity = 0
  inspectForm.inspection_remark = ''
  showInspectModal.value = true
}

async function handleSubmitInspection() {
  if (!selectedReport.value) return

  if (quantityMismatch.value) {
    message.error(`合格+返工+报废数量(${totalInput.value})必须等于报工数量(${reportQuantity.value})`)
    return
  }

  try {
    loading.value = true
    const data: QualityInspectionRequest = {
      passed_quantity: inspectForm.passed_quantity || 0,
      rework_quantity: inspectForm.rework_quantity || 0,
      scrapped_quantity: inspectForm.scrapped_quantity || 0,
      inspection_remark: inspectForm.inspection_remark || undefined
    }
    await submitQualityInspection(selectedReport.value.id, data)
    message.success('质检完成')
    showInspectModal.value = false
    await loadData()
  } catch (err: any) {
    message.error(err.message || '质检失败')
  } finally {
    loading.value = false
  }
}

async function loadPendingList() {
  try {
    pendingGroups.value = await getInspectorPendingList()
  } catch (err: any) {
    message.error('加载待质检列表失败')
  }
}

async function loadHistoryList() {
  try {
    historyReports.value = await getInspectorHistoryList()
  } catch (err: any) {
    message.error('加载质检历史失败')
  }
}

async function loadData() {
  loading.value = true
  try {
    await Promise.all([loadPendingList(), loadHistoryList()])
  } finally {
    loading.value = false
  }
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

function handleQuickFill(passed: number, rework: number, scrapped: number) {
  inspectForm.passed_quantity = passed
  inspectForm.rework_quantity = rework
  inspectForm.scrapped_quantity = scrapped
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">质检大厅</h1>
      <p class="page-desc">质量检验、缺陷记录和质量分析</p>
    </div>

    <n-tabs default-value="pending" size="large">
      <n-tab-pane name="pending" tab="待质检">
        <n-card class="content-card" :bordered="false">
          <div class="card-header">
            <div class="card-title">
              <n-icon size="20" color="#f59e0b">
                <time-outline />
              </n-icon>
              <span>待质检工单</span>
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
            v-if="pendingGroups.length > 0"
            :columns="workOrderColumns"
            :data="pendingGroups"
            :loading="loading"
            v-model:expanded-row-keys="expandedRowKeys"
            :row-key="(row) => row.work_order_id"
            striped
          >
            <template #expanded="{ row }">
              <div class="expanded-content">
                <h4 class="section-title">待质检记录</h4>
                <n-data-table
                  :columns="reportColumns"
                  :data="row.reports"
                  :row-key="(r) => r.id"
                  :row-class-name="(r) => r.status === 'rework' ? 'rework-row' : ''"
                  striped
                />
              </div>
            </template>
          </n-data-table>

          <n-empty v-else description="暂无待质检记录" />
        </n-card>
      </n-tab-pane>

      <n-tab-pane name="history" tab="质检历史">
        <n-card class="content-card" :bordered="false">
          <div class="card-header">
            <div class="card-title">
              <n-icon size="20" color="#10b981">
                <shield-checkmark-outline />
              </n-icon>
              <span>质检历史记录</span>
            </div>
          </div>

          <n-data-table
            :columns="historyColumns"
            :data="historyReports"
            :loading="loading"
            :row-key="(row) => row.id"
            :row-class-name="(row) => {
              if (row.has_passed) return 'passed-row'
              if (row.has_scrap) return 'scrap-row'
              return ''
            }"
            striped
          />
        </n-card>
      </n-tab-pane>
    </n-tabs>

    <n-modal
      v-model:show="showInspectModal"
      preset="card"
      :title="`质检审核 - ${selectedReport?.worker_name}`"
      :mask-closable="false"
      style="width: 700px"
    >
      <div v-if="selectedReport" class="inspect-form-container">
        <n-descriptions :column="2" bordered size="small">
          <n-descriptions-item label="工单号">
            {{ selectedReport.work_order_no }}
          </n-descriptions-item>
          <n-descriptions-item label="产品名称">
            {{ selectedReport.product_name }}
          </n-descriptions-item>
          <n-descriptions-item label="工序名称">
            {{ selectedReport.process_name }}
          </n-descriptions-item>
          <n-descriptions-item label="工人姓名">
            {{ selectedReport.worker_name }}
          </n-descriptions-item>
          <n-descriptions-item label="报工数量">
            <n-tag type="primary" size="large">{{ selectedReport.quantity }} 件</n-tag>
          </n-descriptions-item>
          <n-descriptions-item label="报工备注">
            {{ selectedReport.remark || '-' }}
          </n-descriptions-item>
        </n-descriptions>

        <div class="section">
          <h4 class="section-title">快速填充</h4>
          <div class="quick-buttons">
            <n-button size="small" type="success" @click="handleQuickFill(selectedReport.quantity, 0, 0)">
              <template #icon>
                <n-icon>
                  <checkmark-outline />
                </n-icon>
              </template>
              全部合格
            </n-button>
            <n-button size="small" type="warning" @click="handleQuickFill(0, selectedReport.quantity, 0)">
              <template #icon>
                <n-icon>
                  <arrow-redo-outline />
                </n-icon>
              </template>
              全部返工
            </n-button>
            <n-button size="small" type="error" @click="handleQuickFill(0, 0, selectedReport.quantity)">
              <template #icon>
                <n-icon>
                  <close-circle-outline />
                </n-icon>
              </template>
              全部报废
            </n-button>
          </div>
        </div>

        <n-form
          ref="inspectFormRef"
          :model="inspectForm"
          :rules="inspectFormRules"
          label-placement="top"
        >
          <div class="section">
            <h4 class="section-title">质检结果</h4>

            <n-alert
              v-if="quantityMismatch"
              type="error"
              class="mismatch-alert"
            >
              <template #icon>
                <n-icon>
                  <alert-circle-outline />
                </n-icon>
              </template>
              数量不匹配：当前合计 {{ totalInput }} 件，报工数量 {{ reportQuantity }} 件
            </n-alert>

            <div class="quantity-grid">
              <div class="quantity-item passed">
                <div class="quantity-label">合格件数</div>
                <n-form-item path="passed_quantity" :show-label="false">
                  <n-input-number
                    v-model:value="inspectForm.passed_quantity"
                    :min="0"
                    :max="reportQuantity"
                    size="large"
                    class="big-input"
                    placeholder="合格"
                  />
                </n-form-item>
              </div>
              <div class="quantity-item rework">
                <div class="quantity-label">返工件数</div>
                <n-form-item path="rework_quantity" :show-label="false">
                  <n-input-number
                    v-model:value="inspectForm.rework_quantity"
                    :min="0"
                    :max="reportQuantity"
                    size="large"
                    class="big-input"
                    placeholder="返工"
                  />
                </n-form-item>
              </div>
              <div class="quantity-item scrapped">
                <div class="quantity-label">报废件数</div>
                <n-form-item path="scrapped_quantity" :show-label="false">
                  <n-input-number
                    v-model:value="inspectForm.scrapped_quantity"
                    :min="0"
                    :max="reportQuantity"
                    size="large"
                    class="big-input"
                    placeholder="报废"
                  />
                </n-form-item>
              </div>
            </div>

            <div class="total-check">
              <span class="total-label">合计：</span>
              <span :class="['total-value', { 'mismatch': quantityMismatch }]">
                {{ totalInput }} / {{ reportQuantity }} 件
              </span>
              <n-icon v-if="!quantityMismatch && totalInput === reportQuantity" size="20" color="#10b981">
                <checkmark-circle-outline />
              </n-icon>
            </div>

            <n-form-item label="质检备注" path="inspection_remark">
              <n-input
                v-model:value="inspectForm.inspection_remark"
                type="textarea"
                placeholder="可选：填写质检备注"
                :autosize="{ minRows: 2, maxRows: 4 }"
              />
            </n-form-item>
          </div>
        </n-form>

        <div class="modal-footer">
          <n-button @click="showInspectModal = false">取消</n-button>
          <n-button
            type="primary"
            :loading="loading"
            :disabled="quantityMismatch || totalInput !== reportQuantity"
            @click="handleSubmitInspection"
          >
            <template #icon>
              <n-icon>
                <send-outline />
              </n-icon>
            </template>
            提交质检
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

.rework-row {
  background: #eff6ff !important;
}

.passed-row {
  background: #f0fdf4 !important;
}

.scrap-row {
  background: #fef2f2 !important;
}

.inspect-form-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.quick-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.quantity-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.quantity-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px;
  border-radius: 8px;
  background: #f8fafc;
}

.quantity-item.passed {
  border: 2px solid #10b981;
  background: #f0fdf4;
}

.quantity-item.rework {
  border: 2px solid #f59e0b;
  background: #fffbeb;
}

.quantity-item.scrapped {
  border: 2px solid #ef4444;
  background: #fef2f2;
}

.quantity-label {
  font-size: 14px;
  font-weight: 600;
  color: #475569;
  text-align: center;
}

.big-input {
  width: 100%;
}

.big-input :deep(.n-input-number) {
  height: 60px;
}

.big-input :deep(.n-input__input-el) {
  font-size: 24px !important;
  font-weight: 600 !important;
  text-align: center;
}

.total-check {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px;
  background: #f8fafc;
  border-radius: 8px;
}

.total-label {
  font-size: 16px;
  font-weight: 500;
  color: #64748b;
}

.total-value {
  font-size: 24px;
  font-weight: 700;
  color: #10b981;
}

.total-value.mismatch {
  color: #ef4444;
}

.mismatch-alert {
  margin-bottom: 12px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 8px;
}
</style>
