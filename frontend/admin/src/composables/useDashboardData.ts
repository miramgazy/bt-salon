import { ref, reactive } from 'vue'
import dashboardApi from '../api/dashboard'

export function useDashboardData() {
  const loading = reactive({
    summary: true,
    timeline: true,
    stats: true,
    appointments: true,
    filters: true
  })

  const error = ref<string | null>(null)

  const summaryData = ref<any>(null)
  const timelineData = ref<any[]>([])
  const masterStats = ref<any[]>([])
  const serviceStats = ref<any[]>([])
  const appointments = ref<any[]>([])
  const totalAppointments = ref(0)
  
  const filterOptions = reactive({
    masters: [],
    services: []
  })

  const fetchData = async (filters: any, page = 1, pageSize = 20) => {
    error.value = null
    const params = { ...filters, page, page_size: pageSize }

    // Summary
    loading.summary = true
    dashboardApi.getSummary(params).then(res => {
      summaryData.value = res.data
      loading.summary = false
    }).catch(() => { loading.summary = false; error.value = 'Ошибка загрузки общих данных' })

    // Timeline
    loading.timeline = true
    dashboardApi.getTimeline(params).then(res => {
      timelineData.value = res.data.timeline
      loading.timeline = false
    }).catch(() => { loading.timeline = false })

    // Stats
    loading.stats = true
    Promise.all([
      dashboardApi.getByMaster(params),
      dashboardApi.getByService(params)
    ]).then(([mRes, sRes]) => {
      masterStats.value = mRes.data.masters
      serviceStats.value = sRes.data.services
      loading.stats = false
    }).catch(() => { loading.stats = false })

    // Appointments (triggered separately if needed, but included here for full refresh)
    fetchAppointments(filters, page, pageSize)
  }

  const fetchAppointments = async (filters: any, page: number, pageSize: number) => {
    loading.appointments = true
    const params = { ...filters, page, page_size: pageSize }
    try {
      const res = await dashboardApi.getAppointments(params)
      appointments.value = res.data.results
      totalAppointments.value = res.data.count
    } catch (err) {
      console.error(err)
    } finally {
      loading.appointments = false
    }
  }

  const fetchFilterOptions = async () => {
    loading.filters = true
    try {
      const res = await dashboardApi.getFilters()
      filterOptions.masters = res.data.masters
      filterOptions.services = res.data.services
    } finally {
      loading.filters = false
    }
  }

  return {
    loading,
    error,
    summaryData,
    timelineData,
    masterStats,
    serviceStats,
    appointments,
    totalAppointments,
    filterOptions,
    fetchData,
    fetchAppointments,
    fetchFilterOptions
  }
}
