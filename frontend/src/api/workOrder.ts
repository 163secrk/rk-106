import { get, post, put, del } from '@/utils/request'
import type {
  Product,
  Process,
  User,
  WorkOrder,
  WorkOrderListItem,
  CreateWorkOrderRequest,
  UpdateWorkOrderRequest,
  WorkerWorkOrder,
  WorkReport,
  CreateWorkReportRequest,
  PendingWorkOrderGroup,
  InspectorWorkReport,
  ReworkTask,
  QualityInspectionRequest,
  SalarySummaryGrouped,
  WorkReportTraceData,
  SalarySettlement,
  SalarySettlementFull,
  SalaryFilterOptions
} from '@/types'

export function getProducts(): Promise<Product[]> {
  return get<Product[]>('/products/')
}

export function getProcesses(): Promise<Process[]> {
  return get<Process[]>('/processes/')
}

export function getWorkers(): Promise<User[]> {
  return get<User[]>('/workers/')
}

export function getWorkOrders(): Promise<WorkOrderListItem[]> {
  return get<WorkOrderListItem[]>('/workorders/')
}

export function getWorkOrderDetail(id: number): Promise<WorkOrder> {
  return get<WorkOrder>(`/workorders/${id}/`)
}

export function createWorkOrder(data: CreateWorkOrderRequest): Promise<WorkOrder> {
  return post<WorkOrder>('/workorders/', data)
}

export function updateWorkOrder(id: number, data: UpdateWorkOrderRequest): Promise<WorkOrder> {
  return put<WorkOrder>(`/workorders/${id}/`, data)
}

export function deleteWorkOrder(id: number): Promise<void> {
  return del<void>(`/workorders/${id}/`)
}

export function getWorkerWorkOrders(): Promise<WorkerWorkOrder[]> {
  return get<WorkerWorkOrder[]>('/worker/workorders/')
}

export function getWorkReports(): Promise<WorkReport[]> {
  return get<WorkReport[]>('/workreports/')
}

export function getWorkReportDetail(id: number): Promise<WorkReport> {
  return get<WorkReport>(`/workreports/${id}/`)
}

export function createWorkReport(data: CreateWorkReportRequest): Promise<WorkReport> {
  return post<WorkReport>('/workreports/', data)
}

export function updateWorkReport(id: number, data: Partial<CreateWorkReportRequest>): Promise<WorkReport> {
  return put<WorkReport>(`/workreports/${id}/`, data)
}

export function deleteWorkReport(id: number): Promise<void> {
  return del<void>(`/workreports/${id}/`)
}

export function getInspectorPendingList(): Promise<PendingWorkOrderGroup[]> {
  return get<PendingWorkOrderGroup[]>('/inspector/pending/')
}

export function getInspectorHistoryList(): Promise<InspectorWorkReport[]> {
  return get<InspectorWorkReport[]>('/inspector/history/')
}

export function submitQualityInspection(id: number, data: QualityInspectionRequest): Promise<WorkReport> {
  return post<WorkReport>(`/workreports/${id}/inspect/`, data)
}

export function getWorkerReworkTasks(status?: string): Promise<ReworkTask[]> {
  const url = status ? `/worker/rework-tasks/?status=${status}` : '/worker/rework-tasks/'
  return get<ReworkTask[]>(url)
}

export function getWorkerReworkTaskDetail(id: number): Promise<ReworkTask> {
  return get<ReworkTask>(`/worker/rework-tasks/${id}/`)
}

export function getSalaryFilterOptions(): Promise<SalaryFilterOptions> {
  return get<SalaryFilterOptions>('/salary/filter-options/')
}

export function getSalarySummary(params?: {
  month?: string
  worker_id?: number
  work_order_id?: number
  process_id?: number
}): Promise<SalarySummaryGrouped[]> {
  const query = new URLSearchParams()
  if (params?.month) query.append('month', params.month)
  if (params?.worker_id) query.append('worker_id', String(params.worker_id))
  if (params?.work_order_id) query.append('work_order_id', String(params.work_order_id))
  if (params?.process_id) query.append('process_id', String(params.process_id))
  const url = query.toString() ? `/salary/summary/?${query.toString()}` : '/salary/summary/'
  return get<SalarySummaryGrouped[]>(url)
}

export function getWorkReportTrace(id: number): Promise<WorkReportTraceData> {
  return get<WorkReportTraceData>(`/workreports/${id}/trace/`)
}

export function getSalarySettlements(month?: string): Promise<SalarySettlement[]> {
  const url = month ? `/salary/settlements/?month=${month}` : '/salary/settlements/'
  return get<SalarySettlement[]>(url)
}

export function getSalarySettlementDetail(id: number): Promise<SalarySettlementFull> {
  return get<SalarySettlementFull>(`/salary/settlements/${id}/`)
}

export function createSalarySettlement(settlement_month: string): Promise<SalarySettlementFull> {
  return post<SalarySettlementFull>('/salary/settlements/create/', { settlement_month })
}
