<script setup lang="ts">
import { ref, reactive, computed, onMounted, h } from 'vue'
import {
  NCard,
  NButton,
  NIcon,
  NTable,
  NTag,
  NProgress,
  NModal,
  NForm,
  NFormItem,
  NInputNumber,
  NDatePicker,
  NSelect,
  NGrid,
  NGridItem,
  NSpace,
  NPopconfirm,
  NDescriptions,
  NDescriptionsItem,
  NEmpty,
  useMessage
} from 'naive-ui'
import type { FormInst, FormRules } from 'naive-ui'
import {
  AddOutline,
  CreateOutline,
  TrashOutline,
  EyeOutline,
  TimeOutline,
  PeopleOutline,
  DocumentTextOutline
} from '@vicons/ionicons5'
import {
  getWorkOrders,
  getProducts,
  getProcesses,
  getWorkers,
  getWorkOrderDetail,
  createWorkOrder,
  updateWorkOrder,
  deleteWorkOrder
} from '@/api/workOrder'
import type {
  WorkOrderListItem,
  WorkOrder,
  Product,
  Process,
  User,
  WorkOrderProcess,
  CreateWorkOrderRequest
} from '@/types'

const message = useMessage()

const loading = ref(false)
const workOrders = ref<WorkOrderListItem[]>([])
const products = ref<Product[]>([])
const processes = ref<Process[]>([])
const workers = ref<User[]>([])

const showCreateModal = ref(false)
const showDetailModal = ref(false)
const showEditModal = ref(false)

const currentDetail = ref<WorkOrder | null>(null)
const currentEditId = ref<number | null>(null)

const createFormRef = ref<FormInst | null>(null)
const editFormRef = ref<FormInst | null>(null)

const createForm = reactive({
  product: null as number | null,
  quantity: null as number | null,
  deadline: null as number | null,
  processes: [] as WorkOrderProcess[]
})

const editForm = reactive({
  product: null as number | null,
  quantity: null as number | null,
  deadline: null as number | null,
  processes: [] as WorkOrderProcess[]
})

const createRules: FormRules = {
  product: {
    required: true,
    type: 'number',
    message: '请选择产品',
    trigger: 'change',
    validator: (_rule, value) => {
      if (value === null || value === undefined) {
        return new Error('请选择产品')
      }
      return true
    }
  },
  quantity: {
    required: true,
    type: 'number',
    message: '请输入生产数量',
    trigger: 'change',
    validator: (_rule, value) => {
      if (value === null || value === undefined || value <= 0) {
        return new Error('请输入有效的生产数量')
      }
      return true
    }
  },
  deadline: {
    required: true,
    type: 'number',
    message: '请选择交付日期',
    trigger: 'change',
    validator: (_rule, value) => {
      if (value === null || value === undefined || value <= 0) {
        return new Error('请选择交付日期')
      }
      return true
    }
  }
}

const editRules: FormRules = {
  deadline: {
    required: true,
    type: 'number',
    message: '请选择交付日期',
    trigger: 'change',
    validator: (_rule, value) => {
      if (value === null || value === undefined || value <= 0) {
        return new Error('请选择交付日期')
      }
      return true
    }
  }
}

const statusConfig = {
  pending: { label: '待生产', type: 'default', color: '#94a3b8' },
  in_progress: { label: '生产中', type: 'warning', color: '#f59e0b' },
  completed: { label: '已完成', type: 'success', color: '#10b981' }
}

const pendingOrders = computed(() => workOrders.value.filter(o => o.status === 'pending'))
const inProgressOrders = computed(() => workOrders.value.filter(o => o.status === 'in_progress'))
const completedOrders = computed(() => workOrders.value.filter(o => o.status === 'completed'))

const formatDate = (dateStr: string) => {
  return dateStr.split('T')[0]
}

const loadData = async () => {
  loading.value = true
  try {
    const [orders, prods, procs, wrks] = await Promise.all([
      getWorkOrders(),
      getProducts(),
      getProcesses(),
      getWorkers()
    ])
    workOrders.value = orders
    products.value = prods
    processes.value = procs
    workers.value = wrks
  } catch (e) {
    message.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const openCreateModal = () => {
  createForm.product = null
  createForm.quantity = null
  createForm.deadline = null
  createForm.processes = []
  showCreateModal.value = true
}

const addProcessRow = (target: 'create' | 'edit') => {
  const form = target === 'create' ? createForm : editForm
  form.processes.push({
    process_id: 0,
    worker_ids: []
  })
}

const removeProcessRow = (target: 'create' | 'edit', index: number) => {
  const form = target === 'create' ? createForm : editForm
  form.processes.splice(index, 1)
}

const handleCreate = async () => {
  try {
    await createFormRef.value?.validate()
  } catch (e) {
    message.warning('请完善表单信息')
    return
  }

  try {
    if (createForm.processes.length === 0) {
      message.warning('请至少添加工序')
      return
    }
    const hasInvalidProcess = createForm.processes.some(p => !p.process_id || p.worker_ids.length === 0)
    if (hasInvalidProcess) {
      message.warning('请完善工序信息')
      return
    }

    const deadlineDate = new Date(createForm.deadline as number)
    const data: CreateWorkOrderRequest = {
      product: createForm.product as number,
      quantity: createForm.quantity as number,
      deadline: deadlineDate.toISOString().split('T')[0],
      processes: createForm.processes
    }

    await createWorkOrder(data)
    message.success('创建成功')
    showCreateModal.value = false
    await loadData()
  } catch (e) {
    message.error('创建失败')
  }
}

const openDetail = async (id: number) => {
  try {
    currentDetail.value = await getWorkOrderDetail(id)
    showDetailModal.value = true
  } catch (e) {
    message.error('获取详情失败')
  }
}

const openEdit = async (id: number) => {
  try {
    const detail = await getWorkOrderDetail(id)
    currentEditId.value = id
    currentDetail.value = detail
    editForm.product = detail.product
    editForm.quantity = detail.quantity
    editForm.deadline = new Date(detail.deadline).getTime()
    editForm.processes = detail.processes.map(p => ({
      id: p.id,
      process_id: p.process_id,
      worker_ids: p.workers_info ? p.workers_info.map(w => w.id) : []
    }))
    showEditModal.value = true
  } catch (e) {
    message.error('获取详情失败')
  }
}

const handleEdit = async () => {
  if (currentEditId.value === null) return
  try {
    await editFormRef.value?.validate()
  } catch (e) {
    message.warning('请完善表单信息')
    return
  }

  try {
    if (editForm.processes.length === 0) {
      message.warning('请至少添加工序')
      return
    }
    const hasInvalidProcess = editForm.processes.some(p => !p.process_id || p.worker_ids.length === 0)
    if (hasInvalidProcess) {
      message.warning('请完善工序信息')
      return
    }

    const deadlineDate = new Date(editForm.deadline as number)
    const data = {
      quantity: editForm.quantity as number,
      deadline: deadlineDate.toISOString().split('T')[0],
      processes: editForm.processes
    }

    await updateWorkOrder(currentEditId.value, data)
    message.success('更新成功')
    showEditModal.value = false
    await loadData()
  } catch (e) {
    message.error('更新失败')
  }
}

const handleDelete = async (id: number) => {
  try {
    await deleteWorkOrder(id)
    message.success('删除成功')
    await loadData()
  } catch (e) {
    message.error('删除失败')
  }
}

const tableColumns = [
  { title: '工单号', key: 'order_no', width: 160 },
  { title: '产品', key: 'product_name', width: 120 },
  { title: '数量', key: 'quantity', width: 80 },
  {
    title: '状态',
    key: 'status',
    width: 100,
    render: (row: WorkOrderListItem) => {
      const config = statusConfig[row.status]
      return h(NTag, { type: config.type as any }, { default: () => config.label })
    }
  },
  {
    title: '进度',
    key: 'progress',
    width: 150,
    render: (row: WorkOrderListItem) => {
      if (row.status === 'pending') {
        return h('span', { style: { color: '#94a3b8' } }, '未开始')
      }
      return h('div', { style: { display: 'flex', alignItems: 'center', gap: '8px' } }, [
        h(NProgress, {
          type: 'line',
          percentage: row.progress,
          color: statusConfig[row.status].color,
          style: { width: '80px' }
        }),
        h('span', { style: { fontSize: '12px' } }, `${row.progress}%`)
      ])
    }
  },
  { title: '交付日期', key: 'deadline', width: 120, render: (row: WorkOrderListItem) => formatDate(row.deadline) },
  { title: '创建人', key: 'created_by_name', width: 100 },
  {
    title: '操作',
    key: 'actions',
    width: 180,
    render: (row: WorkOrderListItem) => {
      return h(NSpace, { size: 'small' }, {
        default: () => [
          h(NButton, {
            size: 'small',
            type: 'default',
            onClick: () => openDetail(row.id)
          }, {
            icon: () => h(NIcon, null, { default: () => h(EyeOutline) }),
            default: () => '查看'
          }),
          h(NButton, {
            size: 'small',
            type: 'primary',
            onClick: () => openEdit(row.id)
          }, {
            icon: () => h(NIcon, null, { default: () => h(CreateOutline) }),
            default: () => '编辑'
          }),
          h(NPopconfirm, {
            positiveText: '确定',
            negativeText: '取消',
            onPositiveClick: () => handleDelete(row.id)
          }, {
            trigger: () => h(NButton, {
              size: 'small',
              type: 'error',
              disabled: row.status !== 'pending'
            }, {
              icon: () => h(NIcon, null, { default: () => h(TrashOutline) }),
              default: () => '删除'
            }),
            default: () => '确定删除该工单吗？'
          })
        ]
      })
    }
  }
]

const detailTableColumns = [
  { title: '工序', key: 'process_name' },
  {
    title: '指派工人',
    key: 'workers',
    render: (row: any) => {
      return row.workers_info?.map((w: any) => w.name).join('、') || '-'
    }
  },
  {
    title: '工价',
    key: 'process_price',
    render: (row: any) => `¥${row.process_price}`
  },
  { title: '已报工', key: 'reported_quantity' },
  { title: '已质检', key: 'passed_quantity' }
]

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="page-container">
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">生产工单</h1>
        <p class="page-desc">工单创建、派发和进度跟踪</p>
      </div>
      <n-button type="primary" size="large" @click="openCreateModal">
        <template #icon>
          <n-icon><add-outline /></n-icon>
        </template>
        创建工单
      </n-button>
    </div>

    <div class="stats-row">
      <n-card class="stat-card pending">
        <div class="stat-icon">
          <n-icon size="24"><time-outline /></n-icon>
        </div>
        <div class="stat-info">
          <div class="stat-label">待生产</div>
          <div class="stat-value">{{ pendingOrders.length }}</div>
        </div>
      </n-card>
      <n-card class="stat-card in-progress">
        <div class="stat-icon">
          <n-icon size="24"><document-text-outline /></n-icon>
        </div>
        <div class="stat-info">
          <div class="stat-label">生产中</div>
          <div class="stat-value">{{ inProgressOrders.length }}</div>
        </div>
      </n-card>
      <n-card class="stat-card completed">
        <div class="stat-icon">
          <n-icon size="24"><people-outline /></n-icon>
        </div>
        <div class="stat-info">
          <div class="stat-label">已完成</div>
          <div class="stat-value">{{ completedOrders.length }}</div>
        </div>
      </n-card>
    </div>

    <n-card class="content-card" title="待生产" v-if="pendingOrders.length > 0">
      <n-table
        :columns="tableColumns"
        :data="pendingOrders"
        :loading="loading"
        :bordered="false"
        size="medium"
      />
    </n-card>

    <n-card class="content-card" title="生产中" v-if="inProgressOrders.length > 0">
      <n-table
        :columns="tableColumns"
        :data="inProgressOrders"
        :loading="loading"
        :bordered="false"
        size="medium"
      />
    </n-card>

    <n-card class="content-card" title="已完成" v-if="completedOrders.length > 0">
      <n-table
        :columns="tableColumns"
        :data="completedOrders"
        :loading="loading"
        :bordered="false"
        size="medium"
      />
    </n-card>

    <n-card class="content-card" v-if="workOrders.length === 0 && !loading">
      <n-empty description="暂无工单数据，点击右上角创建新工单">
        <template #extra>
          <n-button type="primary" @click="openCreateModal">
            <template #icon>
              <n-icon><add-outline /></n-icon>
            </template>
            创建工单
          </n-button>
        </template>
      </n-empty>
    </n-card>

    <n-modal
      v-model:show="showCreateModal"
      preset="card"
      title="创建生产工单"
      style="width: 720px"
      :mask-closable="false"
    >
      <n-form ref="createFormRef" :model="createForm" :rules="createRules" label-placement="top">
        <n-grid :cols="2" :x-gap="20">
          <n-grid-item>
            <n-form-item label="产品" path="product">
              <n-select
                v-model:value="createForm.product"
                placeholder="请选择产品"
                :options="products.map(p => ({ label: p.name, value: p.id }))"
              />
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-form-item label="生产数量" path="quantity">
              <n-input-number
                v-model:value="createForm.quantity"
                placeholder="请输入生产数量"
                :min="1"
                style="width: 100%"
              />
            </n-form-item>
          </n-grid-item>
          <n-grid-item :span="2">
            <n-form-item label="交付截止日期" path="deadline">
              <n-date-picker
                v-model:value="createForm.deadline"
                type="date"
                placeholder="请选择交付截止日期"
                :min="Date.now()"
                style="width: 100%"
              />
            </n-form-item>
          </n-grid-item>
        </n-grid>

        <div class="section-title">
          <span>工序指派</span>
          <n-button size="small" type="primary" @click="addProcessRow('create')">
            <template #icon>
              <n-icon><add-outline /></n-icon>
            </template>
            添加工序
          </n-button>
        </div>

        <div class="process-list" v-if="createForm.processes.length > 0">
          <div
            v-for="(proc, index) in createForm.processes"
            :key="index"
            class="process-row"
          >
            <n-grid :cols="3" :x-gap="12">
              <n-grid-item :span="1">
                <n-select
                  v-model:value="proc.process_id"
                  placeholder="选择工序"
                  :options="processes.map(p => ({ label: p.name, value: p.id }))"
                />
              </n-grid-item>
              <n-grid-item :span="1">
                <n-select
                  v-model:value="proc.worker_ids"
                  multiple
                  placeholder="选择工人"
                  :options="workers.map(w => ({ label: w.name, value: w.id }))"
                  :max-tag-count="3"
                />
              </n-grid-item>
              <n-grid-item :span="1" class="process-actions">
                <n-button
                  size="small"
                  type="error"
                  quaternary
                  @click="removeProcessRow('create', index)"
                >
                  <template #icon>
                    <n-icon><trash-outline /></n-icon>
                  </template>
                  删除
                </n-button>
              </n-grid-item>
            </n-grid>
          </div>
        </div>

        <div v-else class="empty-process">
          <p>请点击上方按钮添加工序</p>
        </div>
      </n-form>

      <template #footer>
        <n-space justify="end">
          <n-button @click="showCreateModal = false">取消</n-button>
          <n-button type="primary" @click="handleCreate">创建</n-button>
        </n-space>
      </template>
    </n-modal>

    <n-modal
      v-model:show="showEditModal"
      preset="card"
      title="编辑生产工单"
      style="width: 720px"
      :mask-closable="false"
    >
      <n-form ref="editFormRef" :model="editForm" :rules="editRules" label-placement="top">
        <n-grid :cols="2" :x-gap="20">
          <n-grid-item>
            <n-form-item label="产品">
              <n-select
                v-model:value="editForm.product"
                placeholder="请选择产品"
                :options="products.map(p => ({ label: p.name, value: p.id }))"
                disabled
              />
              <p v-if="currentDetail && !currentDetail.can_edit_product" class="hint-text">
                工单已有报工记录，无法修改产品
              </p>
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-form-item label="生产数量">
              <n-input-number
                v-model:value="editForm.quantity"
                placeholder="请输入生产数量"
                :min="1"
                style="width: 100%"
                :disabled="!!(currentDetail && !currentDetail.can_edit_product)"
              />
              <p v-if="currentDetail && !currentDetail.can_edit_product" class="hint-text">
                工单已有报工记录，无法修改数量
              </p>
            </n-form-item>
          </n-grid-item>
          <n-grid-item :span="2">
            <n-form-item label="交付截止日期" path="deadline">
              <n-date-picker
                v-model:value="editForm.deadline"
                type="date"
                placeholder="请选择交付截止日期"
                style="width: 100%"
              />
            </n-form-item>
          </n-grid-item>
        </n-grid>

        <div class="section-title">
          <span>工序指派</span>
          <n-button size="small" type="primary" @click="addProcessRow('edit')">
            <template #icon>
              <n-icon><add-outline /></n-icon>
            </template>
            添加工序
          </n-button>
        </div>

        <div class="process-list" v-if="editForm.processes.length > 0">
          <div
            v-for="(proc, index) in editForm.processes"
            :key="proc.id || index"
            class="process-row"
          >
            <n-grid :cols="3" :x-gap="12">
              <n-grid-item :span="1">
                <n-select
                  v-model:value="proc.process_id"
                  placeholder="选择工序"
                  :options="processes.map(p => ({ label: p.name, value: p.id }))"
                  :disabled="!!(currentDetail && !currentDetail.can_edit_product)"
                />
              </n-grid-item>
              <n-grid-item :span="1">
                <n-select
                  v-model:value="proc.worker_ids"
                  multiple
                  placeholder="选择工人"
                  :options="workers.map(w => ({ label: w.name, value: w.id }))"
                  :max-tag-count="3"
                />
              </n-grid-item>
              <n-grid-item :span="1" class="process-actions">
                <n-button
                  size="small"
                  type="error"
                  quaternary
                  @click="removeProcessRow('edit', index)"
                >
                  <template #icon>
                    <n-icon><trash-outline /></n-icon>
                  </template>
                  删除
                </n-button>
              </n-grid-item>
            </n-grid>
          </div>
        </div>
      </n-form>

      <template #footer>
        <n-space justify="end">
          <n-button @click="showEditModal = false">取消</n-button>
          <n-button type="primary" @click="handleEdit">保存</n-button>
        </n-space>
      </template>
    </n-modal>

    <n-modal
      v-model:show="showDetailModal"
      preset="card"
      title="工单详情"
      style="width: 680px"
      v-if="currentDetail"
    >
      <n-descriptions :column="2" bordered>
        <n-descriptions-item label="工单号">{{ currentDetail.order_no }}</n-descriptions-item>
        <n-descriptions-item label="状态">
          <n-tag :type="statusConfig[currentDetail.status].type as any">
            {{ statusConfig[currentDetail.status].label }}
          </n-tag>
        </n-descriptions-item>
        <n-descriptions-item label="产品">{{ currentDetail.product_name }}</n-descriptions-item>
        <n-descriptions-item label="规格">{{ currentDetail.product_spec }}</n-descriptions-item>
        <n-descriptions-item label="生产数量">{{ currentDetail.quantity }}</n-descriptions-item>
        <n-descriptions-item label="交付日期">{{ formatDate(currentDetail.deadline) }}</n-descriptions-item>
        <n-descriptions-item label="创建人">{{ currentDetail.created_by_name }}</n-descriptions-item>
        <n-descriptions-item label="创建时间">{{ formatDate(currentDetail.created_at) }}</n-descriptions-item>
        <n-descriptions-item label="完成进度" :span="2">
          <div class="progress-row">
            <n-progress
              type="line"
              :percentage="currentDetail.progress"
              :color="statusConfig[currentDetail.status].color"
              style="width: 300px"
            />
            <span class="progress-text">{{ currentDetail.progress }}%</span>
          </div>
        </n-descriptions-item>
      </n-descriptions>

      <div class="detail-section">
        <h4 class="detail-section-title">工序详情</h4>
        <n-table
          :bordered="false"
          :data="currentDetail.processes"
          :columns="detailTableColumns"
          size="small"
        />
      </div>

      <template #footer>
        <n-space justify="end">
          <n-button @click="showDetailModal = false">关闭</n-button>
        </n-space>
      </template>
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
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
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

.stats-row {
  display: flex;
  gap: 16px;
}

.stat-card {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.stat-card :deep(.n-card__content) {
  padding: 0;
  display: flex;
  align-items: center;
  gap: 16px;
  width: 100%;
}

.stat-card.pending .stat-icon {
  background: #f1f5f9;
  color: #64748b;
}

.stat-card.in-progress .stat-icon {
  background: #fef3c7;
  color: #d97706;
}

.stat-card.completed .stat-icon {
  background: #d1fae5;
  color: #059669;
}

.stat-icon {
  width: 52px;
  height: 52px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-label {
  font-size: 14px;
  color: #64748b;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
}

.content-card {
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.content-card :deep(.n-card__header) {
  padding: 16px 24px;
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  border-bottom: 1px solid #f1f5f9;
}

.content-card :deep(.n-card__content) {
  padding: 0;
}

.content-card :deep(.n-data-table) {
  border-radius: 0;
}

.section-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 24px 0 12px 0;
  padding-top: 16px;
  border-top: 1px solid #e2e8f0;
  font-size: 14px;
  font-weight: 600;
  color: #334155;
}

.process-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.process-row {
  padding: 12px;
  background: #f8fafc;
  border-radius: 6px;
}

.process-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

.empty-process {
  padding: 32px;
  text-align: center;
  color: #94a3b8;
  background: #f8fafc;
  border-radius: 6px;
}

.hint-text {
  margin: 4px 0 0 0;
  font-size: 12px;
  color: #f59e0b;
}

.detail-section {
  margin-top: 20px;
}

.detail-section-title {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: #334155;
}

.progress-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.progress-text {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
}

:deep(.n-form-item-label) {
  font-weight: 500;
  color: #334155;
}
</style>
