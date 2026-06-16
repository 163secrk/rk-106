export type RoleType = 'admin' | 'team_leader' | 'worker' | 'inspector'

export type WorkOrderStatus = 'pending' | 'in_progress' | 'completed'

export type WorkReportStatus = 'pending' | 'passed' | 'rejected'

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
  work_order_no: string
  work_order_process: number
  process_name: string
  worker: number
  worker_name: string
  quantity: number
  status: WorkReportStatus
  status_name: string
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
}
