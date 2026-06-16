import { get, post, put, del } from '@/utils/request'
import type {
  Product,
  Process,
  User,
  WorkOrder,
  WorkOrderListItem,
  CreateWorkOrderRequest,
  UpdateWorkOrderRequest
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
