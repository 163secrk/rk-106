import { get } from '@/utils/request'
import type { DashboardStats } from '@/types'

export function getDashboardStats(): Promise<DashboardStats> {
  return get<DashboardStats>('/dashboard/stats/')
}
