<template>
  <div class="mx-auto max-w-screen-2xl p-4 md:p-6 2xl:p-8">
    <!-- Filters -->
    <DashboardFilters 
      :filters="filters" 
      :masters="filterOptions.masters" 
      :services="filterOptions.services"
      :loading="loading.filters"
      @apply="handleApplyFilters"
      @reset="handleResetFilters"
    />

    <!-- KPI Section with Skeleton -->
    <div class="mb-5">
      <div v-if="loading.summary" class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3 2xl:grid-cols-6 md:gap-5">
        <div v-for="i in 6" :key="i" class="h-28 animate-pulse rounded-sm border border-stroke bg-white dark:border-strokedark dark:bg-bg-dark-2"></div>
      </div>
      <KpiCards v-else :data="summaryData" />
    </div>

    <!-- Error Alert if any -->
    <div v-if="error" class="mb-6 rounded-lg bg-danger/10 p-4 text-danger flex items-center justify-between">
      <span>{{ error }}</span>
      <button @click="refreshAll" class="underline font-bold">Попробовать снова</button>
    </div>

    <div class="grid grid-cols-12 gap-4 md:gap-6 2xl:gap-7.5">
      <!-- Main Revenue Chart with Skeleton -->
      <div class="col-span-12 xl:col-span-8">
        <div v-if="loading.timeline" class="h-[430px] w-full animate-pulse rounded-sm border border-stroke bg-white dark:border-strokedark dark:bg-bg-dark-2"></div>
        <RevenueChart 
          v-else
          :data="timelineData" 
          :currentGroup="filters.group_by" 
          @updateGroup="handleGroupBy"
        />
      </div>

      <!-- Service Pie Chart with Skeleton -->
      <div class="col-span-12 xl:col-span-4">
        <div v-if="loading.stats" class="h-[430px] w-full animate-pulse rounded-sm border border-stroke bg-white dark:border-strokedark dark:bg-bg-dark-2"></div>
        <ServiceChart v-else :data="serviceStats" />
      </div>

      <!-- Master Performance Chart with Skeleton -->
      <div class="col-span-12 xl:col-span-12">
         <div v-if="loading.stats" class="h-[400px] w-full animate-pulse rounded-sm border border-stroke bg-white dark:border-strokedark dark:bg-bg-dark-2"></div>
         <div v-else class="grid grid-cols-12 gap-4 md:gap-6">
             <div class="col-span-12 xl:col-span-4">
                <MasterChart :data="masterStats" />
             </div>
             <div class="col-span-12 xl:col-span-8">
                <MasterWorkloadTable :data="masterStats" />
             </div>
         </div>
      </div>

      <!-- Detailed Appointments Table with Skeleton -->
      <div class="col-span-12">
        <div v-if="loading.appointments" class="h-96 w-full animate-pulse rounded-sm border border-stroke bg-white dark:border-strokedark dark:bg-bg-dark-2"></div>
        <AppointmentsTable 
          v-else
          :data="appointments" 
          :totalCount="totalAppointments"
          :currentPage="currentPage"
          :totalPages="totalPages"
          @pageChange="handlePageChange"
          @exportExcel="handleExportExcel"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useDashboardFilters } from '../../composables/useDashboardFilters'
import { useDashboardData } from '../../composables/useDashboardData'
import dashboardApi from '../../api/dashboard'

import DashboardFilters from '../../components/dashboard/DashboardFilters.vue'
import KpiCards from '../../components/dashboard/KpiCards.vue'
import RevenueChart from '../../components/dashboard/RevenueChart.vue'
import MasterChart from '../../components/dashboard/MasterChart.vue'
import ServiceChart from '../../components/dashboard/ServiceChart.vue'
import AppointmentsTable from '../../components/dashboard/AppointmentsTable.vue'
import MasterWorkloadTable from '../../components/dashboard/MasterWorkloadTable.vue'

// --- Logic ---
const { 
  filters, 
  initFromUrl, 
  applyFilters, 
  resetFilters, 
  setGroupBy 
} = useDashboardFilters()

const {
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
} = useDashboardData()

// State
const currentPage = ref(1)
const pageSize = ref(20)
const totalPages = computed(() => Math.ceil(totalAppointments.value / pageSize.value))

let debounceTimer = null

// --- Handlers ---

const refreshAll = () => {
    fetchData(filters, currentPage.value, pageSize.value)
}

const handleApplyFilters = (newFilters) => {
    applyFilters(newFilters)
    currentPage.value = 1
    
    // Debounce API calls 300ms
    if (debounceTimer) clearTimeout(debounceTimer)
    debounceTimer = setTimeout(() => {
        refreshAll()
    }, 300)
}

const handleResetFilters = () => {
    resetFilters()
    currentPage.value = 1
    refreshAll()
}

const handleGroupBy = (mode) => {
    setGroupBy(mode)
    refreshAll()
}

const handlePageChange = (page) => {
  currentPage.value = page
  fetchAppointments(filters, currentPage.value, pageSize.value)
}

const handleExportExcel = async () => {
  try {
    const res = await dashboardApi.exportAppointments({ ...filters })
    const blob = new Blob([res.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    
    // Try to extract filename from Content-Disposition header (e.g. filename*=UTF-8''...)
    const disposition = res.headers['content-disposition']
    let filename = `Записи_с_${filters.date_from}_по_${filters.date_to}.xlsx`
    
    if (disposition && disposition.includes("filename*=UTF-8''")) {
      filename = decodeURIComponent(disposition.split("filename*=UTF-8''")[1])
    } else if (disposition && disposition.includes('filename=')) {
      filename = disposition.split('filename=')[1].replace(/"/g, '')
    }
    
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    
    // Clean up
    setTimeout(() => {
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    }, 100)
  } catch (err) {
    console.error('Export failed:', err)
    alert('Ошибка при экспорте файла. Пожалуйста, попробуйте позже.')
  }
}

onMounted(async () => {
  initFromUrl()
  fetchFilterOptions()
  refreshAll()
})

// Sync page refresh if URL changes externally (optional but good)
watch(() => filters, () => {
    // refreshAll() // already handled by applyFilters
}, { deep: true })
</script>


<style scoped>
/* Any additional dashboard specific styles */
</style>
