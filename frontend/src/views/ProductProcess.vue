<script setup lang="ts">
import { ref, reactive, computed, onMounted, h } from 'vue'
import {
  NCard, NButton, NIcon, NDataTable, NTag, NModal, NForm, NFormItem, NInput, NInputNumber, NSelect, NSpace, NPopconfirm, NEmpty, NGrid, NGridItem, NAlert, useMessage, NBadge, NTabs, NTabPane
} from 'naive-ui'
import type { FormInst, FormRules, DataTableColumns } from 'naive-ui'
import {
  AddOutline,
  CreateOutline,
  TrashOutline,
  ReorderFourOutline,
  ConstructOutline,
  LayersOutline,
  RefreshOutline,
  ChevronUpOutline,
  ChevronDownOutline,
  SaveOutline,
  FileTrayOutline,
  SwapVerticalOutline
} from '@vicons/ionicons5'
import {
  getProducts,
  createProduct,
  updateProduct,
  deleteProduct,
  getProcesses,
  createProcess,
  updateProcess,
  deleteProcess,
  addProductProcess,
  updateProductProcess,
  deleteProductProcess,
  batchUpdateProductProcesses
} from '@/api/workOrder'
import type {
  Product,
  Process,
  ProductProcessItem
} from '@/types'

const message = useMessage()

const activeTab = ref<'products' | 'processes'>('products')

const loading = ref(false)
const products = ref<Product[]>([])
const processes = ref<Process[]>([])

const selectedProductId = ref<number | null>(null)

const showCreateProductModal = ref(false)
const showEditProductModal = ref(false)
const showCreateProcessModal = ref(false)
const showEditProcessModal = ref(false)
const showAddProcessToProductModal = ref(false)

const createProductFormRef = ref<FormInst | null>(null)
const editProductFormRef = ref<FormInst | null>(null)
const createProcessFormRef = ref<FormInst | null>(null)
const editProcessFormRef = ref<FormInst | null>(null)

const currentEditProductId = ref<number | null>(null)
const currentEditProcessId = ref<number | null>(null)

const createProductForm = reactive({
  name: '',
  code: '',
  spec: ''
})

const editProductForm = reactive({
  name: '',
  code: '',
  spec: ''
})

const createProcessForm = reactive({
  name: '',
  code: '',
  price: 0
})

const editProcessForm = reactive({
  name: '',
  code: '',
  price: 0
})

const addProcessForm = reactive({
  process_id: null as number | null,
  unit_price: 0
})

const productRules: FormRules = {
  name: {
    required: true,
    message: '请输入产品名称',
    trigger: 'blur'
  },
  code: {
    required: true,
    message: '请输入产品编号',
    trigger: 'blur'
  }
}

const processRules: FormRules = {
  name: {
    required: true,
    message: '请输入工序名称',
    trigger: 'blur'
  },
  code: {
    required: true,
    message: '请输入工序编号',
    trigger: 'blur'
  }
}

const selectedProduct = computed<Product | null>(() => {
  return products.value.find(p => p.id === selectedProductId.value) || null
})

const selectedProductProcesses = computed<ProductProcessItem[]>(() => {
  return selectedProduct.value?.processes || []
})

const availableProcessesForProduct = computed<Process[]>(() => {
  const addedProcessIds = new Set(selectedProductProcesses.value.map(p => p.process_id))
  return processes.value.filter(p => !addedProcessIds.has(p.id))
})

const productColumns: DataTableColumns<Product> = [
  {
    title: '产品名称',
    key: 'name',
    width: 160,
    render: (row) => {
      return h('div', {
        style: {
          display: 'flex',
        'align-items': 'center',
        gap: '8px',
        color: selectedProductId.value === row.id ? '#1e293b' : '#334155',
          'font-weight': selectedProductId.value === row.id ? '600' : '400'
        }
      }, [
        h(NIcon, { size: 16, color: '#3b82f6' }, { default: () => h(LayersOutline) }),
        row.name
      ])
    }
  },
  { title: '产品编号', key: 'code', width: 140 },
  { title: '规格', key: 'spec', width: 160 },
  {
    title: '工序数',
    key: 'process_count',
    width: 90,
    align: 'center',
    render: (row) => {
      const count = row.process_count || 0
      return h(NBadge, { value: count, type: count > 0 ? 'info' : 'default', showZero: true })
    }
  },
  {
    title: '操作',
    key: 'actions',
    width: 160,
    render: (row) => {
      return h(NSpace, { size: 'small' }, {
        default: () => [
          h(NButton, {
            size: 'small',
            type: 'primary',
            quaternary: true,
            onClick: () => handleSelectProduct(row.id)
          }, {
            default: () => '查看工序'
          }),
          h(NButton, {
            size: 'small',
            type: 'default',
            onClick: () => openEditProductModal(row)
          }, {
            icon: () => h(NIcon, { size: 14 }, { default: () => h(CreateOutline) })
          }),
          h(NPopconfirm, {
            positiveText: '确定',
            negativeText: '取消',
            onPositiveClick: () => handleDeleteProduct(row.id)
          }, {
            trigger: () => h(NButton, {
              size: 'small',
              type: 'error',
              quaternary: true
            }, {
              icon: () => h(NIcon, { size: 14 }, { default: () => h(TrashOutline) })
            }),
            default: () => '确定删除该产品吗？'
          })
        ]
      })
    }
  }
]

const processColumns: DataTableColumns<Process> = [
  {
    title: '工序名称',
    key: 'name',
    width: 160,
    render: (row) => {
      return h('div', { style: { display: 'flex', 'align-items': 'center', gap: '8px' } }, [
        h(NIcon, { size: 16, color: '#8b5cf6' }, { default: () => h(ConstructOutline) }),
        row.name
      ])
    }
  },
  { title: '工序编号', key: 'code', width: 140 },
  {
    title: '默认工价',
    key: 'price',
    width: 120,
    align: 'right',
    render: (row) => {
      return h('span', { style: { color: '#059669', 'font-family': 'monospace' } }, `¥${Number(row.price).toFixed(2)}`)
    }
  },
  {
    title: '操作',
    key: 'actions',
    width: 120,
    render: (row) => {
      return h(NSpace, { size: 'small' }, {
        default: () => [
          h(NButton, {
            size: 'small',
            type: 'default',
            onClick: () => openEditProcessModal(row)
          }, {
            icon: () => h(NIcon, { size: 14 }, { default: () => h(CreateOutline) })
          }),
          h(NPopconfirm, {
            positiveText: '确定',
            negativeText: '取消',
            onPositiveClick: () => handleDeleteProcess(row.id)
          }, {
            trigger: () => h(NButton, {
              size: 'small',
              type: 'error',
              quaternary: true
            }, {
              icon: () => h(NIcon, { size: 14 }, { default: () => h(TrashOutline) })
            }),
            default: () => '确定删除该工序吗？'
          })
        ]
      })
    }
  }
]

const productProcessColumns: DataTableColumns<ProductProcessItem> = [
  {
    title: '序号',
    key: 'order_index',
    width: 70,
    align: 'center',
    render: (_row, index) => {
      return h('div', {
        style: {
          display: 'flex',
          'align-items': 'center',
          'justify-content': 'center',
          gap: '4px',
          cursor: 'move'
        }
      }, [
        h(NIcon, { size: 14, color: '#94a3b8' }, { default: () => h(ReorderFourOutline) }),
        String(index + 1)
      ])
    }
  },
  {
    title: '工序名称',
    key: 'process_name',
    width: 160,
    render: (row) => {
      return h('div', { style: { display: 'flex', 'align-items': 'center', gap: '8px' } }, [
        h(NIcon, { size: 16, color: '#8b5cf6' }, { default: () => h(ConstructOutline) }),
        h('span', { style: { 'font-weight': '500' } }, row.process_name)
      ])
    }
  },
  { title: '工序编号', key: 'process_code', width: 120 },
  {
    title: '计件单价',
    key: 'unit_price',
    width: 180,
    render: (row) => {
      return h(NInputNumber, {
        value: row.unit_price,
        min: 0,
        precision: 4,
        step: 0.01,
        size: 'small',
        style: { width: '120px' },
        onUpdateValue: (value: number | null) => {
          handleUpdateUnitPrice(row.id, value || 0)
        }
      })
    }
  },
  {
    title: '默认工价',
    key: 'process_default_price',
    width: 120,
    align: 'right',
    render: (row) => {
      return h(NTag, { size: 'small', type: 'info' }, {
        default: () => `¥${Number(row.process_default_price).toFixed(2)}`
      })
    }
  },
  {
    title: '上移',
    key: 'move_up',
    width: 70,
    align: 'center',
    render: (_row, index) => {
      return h(NButton, {
        size: 'small',
        type: 'default',
        tertiary: true,
        disabled: index === 0,
        onClick: () => handleMoveProcess(index, -1)
      }, {
        icon: () => h(NIcon, { size: 14 }, { default: () => h(ChevronUpOutline) })
      })
    }
  },
  {
    title: '下移',
    key: 'move_down',
    width: 70,
    align: 'center',
    render: (_row, index) => {
      return h(NButton, {
        size: 'small',
        type: 'default',
        tertiary: true,
        disabled: index === selectedProductProcesses.value.length - 1,
        onClick: () => handleMoveProcess(index, 1)
      }, {
        icon: () => h(NIcon, { size: 14 }, { default: () => h(ChevronDownOutline) })
      })
    }
  },
  {
    title: '删除',
    key: 'delete',
    width: 70,
    align: 'center',
    render: (row) => {
      return h(NPopconfirm, {
        positiveText: '确定',
        negativeText: '取消',
        onPositiveClick: () => handleDeleteProductProcess(row.id)
      }, {
        trigger: () => h(NButton, {
          size: 'small',
          type: 'error',
          tertiary: true
        }, {
          icon: () => h(NIcon, { size: 14 }, { default: () => h(TrashOutline) })
        }),
        default: () => '确定从产品中移除该工序吗？'
      })
    }
  }
]

async function loadData() {
  loading.value = true
  try {
    const [prods, procs] = await Promise.all([
      getProducts(),
      getProcesses()
    ])
    products.value = prods
    processes.value = procs
  } catch (e: any) {
      message.error(e.message || '加载数据失败')
    } finally {
      loading.value = false
    }
}

function handleSelectProduct(productId: number) {
  selectedProductId.value = productId
}

function openCreateProductModal() {
  createProductForm.name = ''
  createProductForm.code = ''
  createProductForm.spec = ''
  showCreateProductModal.value = true
}

async function handleCreateProduct() {
  try {
    await createProductFormRef.value?.validate()
  } catch (e) {
    return
  }
  try {
    await createProduct({
      name: createProductForm.name,
      code: createProductForm.code,
      spec: createProductForm.spec
    })
    message.success('产品创建成功')
    showCreateProductModal.value = false
    await loadData()
  } catch (e: any) {
    message.error(e.message || '创建失败')
  }
}

function openEditProductModal(row: Product) {
  currentEditProductId.value = row.id
  editProductForm.name = row.name
  editProductForm.code = row.code
  editProductForm.spec = row.spec
  showEditProductModal.value = true
}

async function handleEditProduct() {
  if (currentEditProductId.value === null) return
  try {
    await editProductFormRef.value?.validate()
  } catch (e) {
    return
  }
  try {
    await updateProduct(currentEditProductId.value, {
      name: editProductForm.name,
      code: editProductForm.code,
      spec: editProductForm.spec
    })
    message.success('产品更新成功')
    showEditProductModal.value = false
    await loadData()
  } catch (e: any) {
    message.error(e.message || '更新失败')
  }
}

async function handleDeleteProduct(id: number) {
  try {
    await deleteProduct(id)
    message.success('删除成功')
    if (selectedProductId.value === id) {
      selectedProductId.value = null
    }
    await loadData()
  } catch (e: any) {
    message.error(e.message || '删除失败')
  }
}

function openCreateProcessModal() {
  createProcessForm.name = ''
  createProcessForm.code = ''
  createProcessForm.price = 0
  showCreateProcessModal.value = true
}

async function handleCreateProcess() {
  try {
    await createProcessFormRef.value?.validate()
  } catch (e) {
    return
  }
  try {
    await createProcess({
      name: createProcessForm.name,
      code: createProcessForm.code,
      price: createProcessForm.price
    })
    message.success('工序创建成功')
    showCreateProcessModal.value = false
    await loadData()
  } catch (e: any) {
    message.error(e.message || '创建失败')
  }
}

function openEditProcessModal(row: Process) {
  currentEditProcessId.value = row.id
  editProcessForm.name = row.name
  editProcessForm.code = row.code
  editProcessForm.price = row.price
  showEditProcessModal.value = true
}

async function handleEditProcess() {
  if (currentEditProcessId.value === null) return
  try {
    await editProcessFormRef.value?.validate()
  } catch (e) {
    return
  }
  try {
    await updateProcess(currentEditProcessId.value, {
      name: editProcessForm.name,
      code: editProcessForm.code,
      price: editProcessForm.price
    })
    message.success('工序更新成功')
    showEditProcessModal.value = false
    await loadData()
  } catch (e: any) {
    message.error(e.message || '更新失败')
  }
}

async function handleDeleteProcess(id: number) {
  try {
    await deleteProcess(id)
    message.success('删除成功')
    await loadData()
  } catch (e: any) {
    message.error(e.message || '删除失败')
  }
}

function openAddProcessToProductModal() {
  if (selectedProductId.value === null) {
    message.warning('请先选择产品')
    return
  }
  addProcessForm.process_id = null
  addProcessForm.unit_price = 0
  showAddProcessToProductModal.value = true
}

async function handleAddProcessToProduct() {
  if (!addProcessForm.process_id) {
    message.warning('请选择工序')
    return
  }
  try {
    await addProductProcess({
      product_id: selectedProductId.value!,
      process_id: addProcessForm.process_id,
      unit_price: addProcessForm.unit_price
    })
    message.success('添加工序成功')
    showAddProcessToProductModal.value = false
    await loadData()
  } catch (e: any) {
    message.error(e.message || '添加失败')
  }
}

async function handleUpdateUnitPrice(id: number, price: number) {
  try {
    await updateProductProcess(id, { unit_price: price })
  } catch (e: any) {
    message.error(e.message || '更新单价失败')
    await loadData()
  }
}

async function handleDeleteProductProcess(id: number) {
  try {
    await deleteProductProcess(id)
    message.success('移除成功')
    await loadData()
  } catch (e: any) {
    message.error(e.message || '移除失败')
  }
}

async function handleMoveProcess(index: number, direction: number) {
  if (selectedProductId.value === null) return
  const processes = [...selectedProductProcesses.value]
  const targetIndex = index + direction
  if (targetIndex < 0 || targetIndex >= processes.length) return
  const temp = processes[index]
  processes[index] = processes[targetIndex]
  processes[targetIndex] = temp
  const updateData = processes.map((p, idx) => ({
    id: p.id,
    order_index: idx,
    unit_price: p.unit_price
  }))
  try {
    await batchUpdateProductProcesses(selectedProductId.value, { processes: updateData })
    message.success('顺序已更新')
    await loadData()
  } catch (e: any) {
    message.error(e.message || '更新失败')
  }
}

async function handleSaveAllOrder() {
  if (selectedProductId.value === null) return
  const updateData = selectedProductProcesses.value.map((p, idx) => ({
    id: p.id,
    order_index: idx,
    unit_price: p.unit_price
  }))
  try {
    await batchUpdateProductProcesses(selectedProductId.value, { processes: updateData })
    message.success('保存成功')
    await loadData()
  } catch (e: any) {
    message.error(e.message || '保存失败')
  }
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">产品工序</h1>
      <p class="page-desc">管理产品基础信息、工序列表，以及产品与工序的关联配置</p>
    </div>

    <n-tabs v-model:value="activeTab" type="line" animated size="large" class="main-tabs">
      <n-tab-pane name="products" tab="产品管理">
        <template #tab>
          <div style="display: flex; align-items: center; gap: 6px;">
            <n-icon :size="16"><layers-outline /></n-icon>
            产品管理
          </div>
        </template>
      </n-tab-pane>

      <n-tab-pane name="processes" tab="工序基础数据">
        <template #tab>
          <div style="display: flex; align-items: center; gap: 6px;">
            <n-icon :size="16"><construct-outline /></n-icon>
            工序基础数据
          </div>
        </template>
      </n-tab-pane>
    </n-tabs>

    <div v-show="activeTab === 'products'" class="products-tab">
      <n-grid :cols="5" :x-gap="20">
        <n-grid-item :span="2">
          <n-card class="content-card" :bordered="false">
            <div class="card-header">
              <div class="card-title">
                <n-icon size="20" color="#3b82f6">
                  <layers-outline />
                </n-icon>
                <span>产品列表</span>
              </div>
              <n-space>
                <n-button size="small" :loading="loading" @click="loadData">
                  <template #icon>
                    <n-icon><refresh-outline /></n-icon>
                  </template>
                  刷新
                </n-button>
                <n-button size="small" type="primary" @click="openCreateProductModal">
                  <template #icon>
                    <n-icon><add-outline /></n-icon>
                  </template>
                  新建产品
                </n-button>
              </n-space>
            </div>
            <n-spin :show="loading">
              <n-data-table
                v-if="products.length > 0"
                :columns="productColumns"
                :data="products"
                :row-key="(row) => row.id"
                :row-class-name="(row) => selectedProductId === row.id ? 'selected-row' : ''"
                size="small"
                :single-line="false"
                striped
              />
              <n-empty v-else description="暂无产品数据" />
            </n-spin>
          </n-card>
        </n-grid-item>

        <n-grid-item :span="3">
          <n-card class="content-card" :bordered="false">
            <template v-if="selectedProduct">
              <div class="card-header">
                <div class="card-title">
                  <n-icon size="20" color="#8b5cf6">
                    <construct-outline />
                  </n-icon>
                  <span>{{ selectedProduct.name }} - 工序配置</span>
                </div>
                <n-space>
                  <n-button size="small" :loading="loading" @click="loadData">
                    <template #icon>
                      <n-icon><refresh-outline /></n-icon>
                    </template>
                    刷新
                  </n-button>
                  <n-button size="small" type="primary" @click="openAddProcessToProductModal">
                    <template #icon>
                      <n-icon><add-outline /></n-icon>
                    </template>
                    添加工序
                  </n-button>
                  <n-button
                    v-if="selectedProductProcesses.length > 1"
                    size="small"
                    @click="handleSaveAllOrder">
                    <template #icon>
                      <n-icon><save-outline /></n-icon>
                    </template>
                    保存排序
                  </n-button>
                </n-space>
              </div>

              <n-alert type="info" class="info-alert">
                <template #icon>
                  <n-icon><swap-vertical-outline /></n-icon>
                </template>
                拖拽序号列可调整工序顺序，或使用上下移动按钮。设置完成后点击"保存排序"。计件单价可直接修改，失焦自动保存。
              </n-alert>

              <n-spin :show="loading">
                <n-data-table
                  v-if="selectedProductProcesses.length > 0"
                  :columns="productProcessColumns"
                  :data="selectedProductProcesses"
                  :row-key="(row) => row.id"
                  size="small"
                  :single-line="false"
                  striped
                />
                <n-empty
                  v-else
                  description="该产品暂无工序配置"
                >
                  <template #extra>
                    <n-button type="primary" @click="openAddProcessToProductModal">
                      <template #icon>
                        <n-icon><add-outline /></n-icon>
                      </template>
                      添加第一个工序
                    </n-button>
                  </template>
                </n-empty>
              </n-spin>
            </template>

            <div v-else class="empty-product-detail">
              <n-empty description="请从左侧选择产品查看工序配置" />
            </div>
          </n-card>
        </n-grid-item>
      </n-grid>
    </div>

    <div v-show="activeTab === 'processes'" class="processes-tab">
      <n-card class="content-card" :bordered="false">
        <div class="card-header">
          <div class="card-title">
            <n-icon size="20" color="#f59e0b">
              <file-tray-outline />
            </n-icon>
            <span>工序基础数据</span>
          </div>
          <n-space>
            <n-button size="small" :loading="loading" @click="loadData">
              <template #icon>
                <n-icon><refresh-outline /></n-icon>
              </template>
              刷新
            </n-button>
            <n-button size="small" type="primary" @click="openCreateProcessModal">
              <template #icon>
                <n-icon><add-outline /></n-icon>
              </template>
              新建工序
            </n-button>
          </n-space>
        </div>
        <n-spin :show="loading">
          <n-data-table
            v-if="processes.length > 0"
            :columns="processColumns"
            :data="processes"
            :row-key="(row) => row.id"
            :single-line="false"
            striped
            size="medium"
          />
          <n-empty v-else description="暂无工序数据" />
        </n-spin>
      </n-card>
    </div>

    <n-modal
      v-model:show="showCreateProductModal"
      preset="card"
      title="新建产品"
      style="width: 500px"
      :mask-closable="false"
    >
      <n-form ref="createProductFormRef" :model="createProductForm" :rules="productRules" label-placement="top">
        <n-form-item label="产品名称" path="name">
          <n-input v-model:value="createProductForm.name" placeholder="请输入产品名称" />
        </n-form-item>
        <n-form-item label="产品编号" path="code">
          <n-input v-model:value="createProductForm.code" placeholder="请输入产品编号" />
        </n-form-item>
        <n-form-item label="规格说明">
          <n-input v-model:value="createProductForm.spec" placeholder="请输入规格说明（可选）" />
        </n-form-item>
      </n-form>
      <template #footer>
        <n-space justify="end">
          <n-button @click="showCreateProductModal = false">取消</n-button>
          <n-button type="primary" @click="handleCreateProduct">创建</n-button>
        </n-space>
      </template>
    </n-modal>

    <n-modal
      v-model:show="showEditProductModal"
      preset="card"
      title="编辑产品"
      style="width: 500px"
      :mask-closable="false"
    >
      <n-form ref="editProductFormRef" :model="editProductForm" :rules="productRules" label-placement="top">
        <n-form-item label="产品名称" path="name">
          <n-input v-model:value="editProductForm.name" placeholder="请输入产品名称" />
        </n-form-item>
        <n-form-item label="产品编号" path="code">
          <n-input v-model:value="editProductForm.code" placeholder="请输入产品编号" />
        </n-form-item>
        <n-form-item label="规格说明">
          <n-input v-model:value="editProductForm.spec" placeholder="请输入规格说明（可选）" />
        </n-form-item>
      </n-form>
      <template #footer>
        <n-space justify="end">
          <n-button @click="showEditProductModal = false">取消</n-button>
          <n-button type="primary" @click="handleEditProduct">保存</n-button>
        </n-space>
      </template>
    </n-modal>

    <n-modal
      v-model:show="showCreateProcessModal"
      preset="card"
      title="新建工序"
      style="width: 500px"
      :mask-closable="false"
    >
      <n-form ref="createProcessFormRef" :model="createProcessForm" :rules="processRules" label-placement="top">
        <n-form-item label="工序名称" path="name">
          <n-input v-model:value="createProcessForm.name" placeholder="请输入工序名称" />
        </n-form-item>
        <n-form-item label="工序编号" path="code">
          <n-input v-model:value="createProcessForm.code" placeholder="请输入工序编号" />
        </n-form-item>
        <n-form-item label="默认工价(元)">
          <n-input-number
            v-model:value="createProcessForm.price"
            :min="0"
            :precision="2"
            :step="0.1"
            placeholder="请输入默认工价"
            style="width: 100%"
          />
        </n-form-item>
      </n-form>
      <template #footer>
        <n-space justify="end">
          <n-button @click="showCreateProcessModal = false">取消</n-button>
          <n-button type="primary" @click="handleCreateProcess">创建</n-button>
        </n-space>
      </template>
    </n-modal>

    <n-modal
      v-model:show="showEditProcessModal"
      preset="card"
      title="编辑工序"
      style="width: 500px"
      :mask-closable="false"
    >
      <n-form ref="editProcessFormRef" :model="editProcessForm" :rules="processRules" label-placement="top">
        <n-form-item label="工序名称" path="name">
          <n-input v-model:value="editProcessForm.name" placeholder="请输入工序名称" />
        </n-form-item>
        <n-form-item label="工序编号" path="code">
          <n-input v-model:value="editProcessForm.code" placeholder="请输入工序编号" />
        </n-form-item>
        <n-form-item label="默认工价(元)">
          <n-input-number
            v-model:value="editProcessForm.price"
            :min="0"
            :precision="2"
            :step="0.1"
            placeholder="请输入默认工价"
            style="width: 100%"
          />
        </n-form-item>
      </n-form>
      <template #footer>
        <n-space justify="end">
          <n-button @click="showEditProcessModal = false">取消</n-button>
          <n-button type="primary" @click="handleEditProcess">保存</n-button>
        </n-space>
      </template>
    </n-modal>

    <n-modal
      v-model:show="showAddProcessToProductModal"
      preset="card"
      title="向产品添加工序"
      style="width: 500px"
      :mask-closable="false"
    >
      <n-form label-placement="top">
        <n-form-item label="选择工序" required>
          <n-select
            v-model:value="addProcessForm.process_id"
            placeholder="请选择要添加的工序"
            :options="availableProcessesForProduct.map(p => ({ label: p.name + ' (' + p.code + ')', value: p.id }))"
          />
        </n-form-item>
        <n-form-item label="计件单价(元)">
          <n-input-number
            v-model:value="addProcessForm.unit_price"
            :min="0"
            :precision="4"
            :step="0.01"
            placeholder="请输入计件单价"
            style="width: 100%"
          />
        </n-form-item>
      </n-form>
      <template #footer>
        <n-space justify="end">
          <n-button @click="showAddProcessToProductModal = false">取消</n-button>
          <n-button type="primary" @click="handleAddProcessToProduct">添加</n-button>
        </n-space>
      </template>
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
  min-height: 500px;
}

.content-card :deep(.n-card__content) {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #334155;
}

.info-alert {
  margin-bottom: 16px;
}

.selected-row {
  background-color: #eff6ff !important;
}

.selected-row:hover > td {
  background-color: #dbeafe !important;
}

.empty-product-detail {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}

:deep(.n-data-table .data-table-wrapper) {
  border-radius: 6px;
  overflow: hidden;
}
</style>
