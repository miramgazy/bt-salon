import { reactive, watch, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'

export function useDashboardFilters() {
  const router = useRouter()
  const route = useRoute()

  // Default values
  const defaultFilters = {
    date_from: new Date(new Date().setDate(new Date().getDate() - 30)).toISOString().split('T')[0],
    date_to: new Date().toISOString().split('T')[0],
    master_ids: [] as string[],
    service_ids: [] as string[],
    group_by: 'day'
  }

  // State
  const filters = reactive({ ...defaultFilters })
  const isInitialized = ref(false)

  // Initialize from URL
  const initFromUrl = () => {
    if (route.query.date_from) filters.date_from = route.query.date_from as string
    if (route.query.date_to) filters.date_to = route.query.date_to as string
    if (route.query.group_by) filters.group_by = route.query.group_by as string
    
    if (route.query.master_ids) {
      const mids = route.query.master_ids
      filters.master_ids = Array.isArray(mids) ? mids as string[] : [mids as string]
    }
    
    if (route.query.service_ids) {
      const sids = route.query.service_ids
      filters.service_ids = Array.isArray(sids) ? sids as string[] : [sids as string]
    }
    isInitialized.value = true
  }

  // Sync to URL
  const syncToUrl = () => {
    const query: any = { ...filters }
    // Clean up empty arrays/defaults to keep URL clean
    if (filters.master_ids.length === 0) delete query.master_ids
    if (filters.service_ids.length === 0) delete query.service_ids
    
    router.push({ query })
  }

  // Handle updates
  const applyFilters = (newFilters: any) => {
    Object.assign(filters, newFilters)
    syncToUrl()
  }

  const resetFilters = () => {
    Object.assign(filters, defaultFilters)
    syncToUrl()
  }

  const setGroupBy = (mode: string) => {
    filters.group_by = mode
    syncToUrl()
  }

  return {
    filters,
    isInitialized,
    initFromUrl,
    applyFilters,
    resetFilters,
    setGroupBy
  }
}
