export interface DashboardSummary {
  revenue: number
  owner_margin: number
  master_share: number
  appointments_count: number
  unique_clients_count: number
  prev_period: {
    revenue: number
    owner_margin: number
    appointments_count: number
    unique_clients_count: number
  }
}

export interface TimelineData {
  date: string
  revenue: number
  owner_margin: number
}

export interface MasterStats {
  master_id: number
  master_name: string
  appointments_count: number
  revenue: number
  master_share: number
  owner_margin: number
  utilization_percent: number
}

export interface ServiceStats {
  service_id: number
  service_name: string
  appointments_count: number
  revenue: number
}

export interface DashboardAppointment {
  id: number
  datetime: string
  client_name: string
  master_name: string
  services: string[]
  total_cost: number
  master_share: number
  owner_margin: number
  status: string
}

export interface DashboardFilters {
  masters: { id: number; name: string }[]
  services: { id: number; name: string }[]
}

export interface QueryParams {
  date_from?: string
  date_to?: string
  master_ids?: number[]
  service_ids?: number[]
  group_by?: 'day' | 'week' | 'month'
  page?: number
  page_size?: number
  sort_by?: string
  sort_order?: 'asc' | 'desc'
}
