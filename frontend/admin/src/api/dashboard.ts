import api from './index'
import type { 
  DashboardSummary, 
  TimelineData, 
  MasterStats, 
  ServiceStats, 
  DashboardAppointment, 
  DashboardFilters,
  QueryParams 
} from '../types/dashboard'

export default {
  getSummary(params: QueryParams) {
    return api.get<DashboardSummary>('/api/dashboard/summary/', { params })
  },
  
  getTimeline(params: QueryParams) {
    return api.get<{ timeline: TimelineData[] }>('/api/dashboard/timeline/', { params })
  },
  
  getByMaster(params: QueryParams) {
    return api.get<{ masters: MasterStats[] }>('/api/dashboard/by-master/', { params })
  },
  
  getByService(params: QueryParams) {
    return api.get<{ services: ServiceStats[] }>('/api/dashboard/by-service/', { params })
  },
  
  getAppointments(params: QueryParams) {
    return api.get<{ count: number; results: DashboardAppointment[] }>('/api/dashboard/appointments/', { params })
  },
  
  getFilters() {
    return api.get<DashboardFilters>('/api/dashboard/filters/')
  },

  exportAppointments(params: QueryParams) {
    return api.get('/api/dashboard/appointments/export/', { 
      params, 
      responseType: 'blob' 
    })
  }
}
