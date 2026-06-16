export type RoleType = 'admin' | 'team_leader' | 'worker' | 'inspector'

export type WorkOrderStatus = 'pending' | 'in_progress' | 'completed'

export type WorkReportStatus = 'pending' | 'passed' | 'rejected' | 'rework'

export type ReworkTaskStatus = 'pending' | 'submitted' | 'completed'

export interface UserInfo {
  id: number
  username: string
  name: string
  role: string
}

export interface User extends UserInfo {
  role_name?: string
}

export interface UserRole {
  code: RoleType
  name: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponseData {
  token: string
  refreshToken: string
  userInfo: UserInfo
  roles: UserRole[]
}

export interface ApiResponse<T = unknown> {
  code: number
  message: string
  data: T
}

export interface MenuItem {
  key: string
  label: string
  icon: string
  path: string
  roles: RoleType[]
}

export interface Product {
  id: number
  name: string
  code: string
  spec: string
  created_at: string
}

export interface Process {
  id: number
  name: string
  code: string
  price: number
  created_at: string
}

export interface WorkOrderProcess {
  id?: number
  process_id: number
  process_name?: string
  process_price?: number
  worker_ids: number[]
  workers_info?: User[]
  reported_quantity?: number
  passed_quantity?: number
  created_at?: string
}

export interface WorkOrder {
  id: number
  order_no: string
  product: number
  product_name: string
  product_spec: string
  quantity: number
  deadline: string
  status: WorkOrderStatus
  status_name: string
  created_by: number
  created_by_name: string
  created_at: string
  updated_at: string
  has_report: boolean
  processes: WorkOrderProcess[]
  progress: number
  can_edit_product: boolean
}

export interface WorkOrderListItem {
  id: number
  order_no: string
  product_name: string
  quantity: number
  deadline: string
  status: WorkOrderStatus
  status_name: string
  created_by_name: string
  created_at: string
  progress: number
}

export interface CreateWorkOrderRequest {
  product: number
  quantity: number
  deadline: string
  processes: WorkOrderProcess[]
}

export interface UpdateWorkOrderRequest extends Partial<CreateWorkOrderRequest> {}

export interface WorkerWorkOrderProcess {
  id: number
  process_name: string
  process_price: number
  reported_quantity: number
  passed_quantity: number
  total_reported: number
  remaining: number
  progress_percent: number
}

export interface WorkerWorkOrder {
  id: number
  order_no: string
  product_name: string
  product_spec: string
  quantity: number
  deadline: string
  status: WorkOrderStatus
  status_name: string
  created_at: string
  processes: WorkerWorkOrderProcess[]
}

export interface WorkReport {
  id: number
  work_order: number
  work_order_id: number
  work_order_no: string
  work_order_process: number
  process_name: string
  process_price: number
  worker: number
  worker_name: string
  quantity: number
  passed_quantity: number
  rework_quantity: number
  scrapped_quantity: number
  status: WorkReportStatus
  status_name: string
  is_locked: boolean
  parent_report: number | null
  has_scrap: boolean
  has_passed: boolean
  salary_amount: number
  inspector: number | null
  inspector_name: string | null
  inspection_time: string | null
  inspection_remark: string
  remark: string
  created_at: string
  updated_at: string
}

export interface CreateWorkReportRequest {
  work_order_id: number
  work_order_process_id: number
  quantity: number
  remark?: string
  rework_task_id?: number
}

export interface InspectorWorkReport {
  id: number
  work_order_id: number
  work_order_no: string
  product_name: string
  process_name: string
  worker: number
  worker_name: string
  quantity: number
  passed_quantity: number
  rework_quantity: number
  scrapped_quantity: number
  status: WorkReportStatus
  status_name: string
  is_locked: boolean
  has_scrap: boolean
  has_passed: boolean
  remark: string
  created_at: string
}

export interface PendingWorkOrderGroup {
  work_order_id: number
  work_order_no: string
  product_name: string
  product_spec: string
  total_quantity: number
  reports: InspectorWorkReport[]
}

export interface ReworkTask {
  id: number
  work_report: number
  original_report_id: number
  work_order: number
  work_order_no: string
  work_order_process: number
  process_name: string
  worker: number
  worker_name: string
  quantity: number
  status: ReworkTaskStatus
  status_name: string
  original_quantity: number
  resubmitted_report: number | null
  created_at: string
  updated_at: string
}

export interface QualityInspectionRequest {
  passed_quantity: number
  rework_quantity: number
  scrapped_quantity: number
  inspection_remark?: string
}

export interface SalarySummaryDetail {
  worker_id: number
  worker_name: string
  settlement_month: string
  work_order_id: number
  work_order_no: string
  work_order_process_id: number
  process_name: string
  total_passed: number
  unit_price: number
  subtotal: number
  final_amount: number
  report_ids: number[]
}

export interface SalarySummaryGrouped {
  worker_id: number
  worker_name: string
  settlement_month: string
  total_passed: number
  total_amount: number
  report_count: number
  details: SalarySummaryDetail[]
}

export interface WorkReportTraceChainItem {
  id: number
  work_order_no: string
  process_name: string
  process_price: number
  worker_name: string
  quantity: number
  passed_quantity: number
  rework_quantity: number
  scrapped_quantity: number
  status: WorkReportStatus
  status_name: string
  inspector_name: string | null
  inspection_time: string | null
  inspection_remark: string
  remark: string
  created_at: string
  updated_at: string
  is_rework: boolean
  chain_order: number
}

export interface WorkReportTraceMain {
  id: number
  work_order_no: string
  process_name: string
  process_price: number
  worker_name: string
  quantity: number
  passed_quantity: number
  rework_quantity: number
  scrapped_quantity: number
  status: WorkReportStatus
  status_name: string
  inspector_name: string | null
  inspection_time: string | null
  inspection_remark: string
  remark: string
  created_at: string
  updated_at: string
  rework_count: number
  has_rework_chain: boolean
  subtotal: number
  final_amount: number
}

export interface WorkReportTraceData {
  main: WorkReportTraceMain
  chain: WorkReportTraceChainItem[]
}

export interface SalarySettlement {
  id: number
  settlement_month: string
  created_by: number
  created_by_name: string
  created_at: string
  total_amount: number
  total_amount_display: string
  total_workers: number
  total_reports: number
  status: string
  status_name: string
  is_final: boolean
}

export interface SalarySettlementDetail {
  id: number
  work_report_id: number
  worker_name: string
  work_order_no: string
  process_name: string
  passed_quantity: number
  unit_price: number
  unit_price_display: string
  subtotal: number
  subtotal_display: string
  final_amount: number
  final_amount_display: string
  report_created_at: string
}

export interface SalarySettlementFull extends SalarySettlement {
  details: SalarySettlementDetail[]
}

export interface SalaryFilterOptions {
  workers: { id: number; name: string }[]
  work_orders: { id: number; order_no: string }[]
  processes: { id: number; name: string }[]
  months: string[]
  current_month: string
}
