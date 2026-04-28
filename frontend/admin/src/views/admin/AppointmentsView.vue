<template>
  <div class="mx-auto max-w-screen-2xl">
    <!-- Filters Card -->
    <div class="mb-6 rounded-sm border border-stroke bg-white p-4 shadow-default dark:border-strokedark dark:bg-bg-dark-2 md:p-6">
      <div class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
        <!-- Date Range From -->
        <div>
          <label class="mb-2.5 block text-black dark:text-white">Дата с</label>
          <input
            type="date"
            v-model="filters.dateFrom"
            class="w-full rounded border-[1.5px] border-stroke bg-transparent py-2 px-4 font-medium outline-none transition focus:border-primary active:border-primary dark:border-strokedark dark:bg-meta-4 dark:focus:border-primary text-black dark:text-white"
          />
        </div>

        <!-- Date Range To -->
        <div>
          <label class="mb-2.5 block text-black dark:text-white">Дата по</label>
          <input
            type="date"
            v-model="filters.dateTo"
            class="w-full rounded border-[1.5px] border-stroke bg-transparent py-2 px-4 font-medium outline-none transition focus:border-primary active:border-primary dark:border-strokedark dark:bg-meta-4 dark:focus:border-primary text-black dark:text-white"
          />
        </div>

        <!-- Date Presets -->
        <div>
          <label class="mb-2.5 block text-black dark:text-white">Период</label>
          <select
            v-model="activePreset"
            @change="applyPreset"
            class="w-full rounded border-[1.5px] border-stroke bg-transparent py-2 px-4 font-medium outline-none transition focus:border-primary active:border-primary dark:border-strokedark dark:bg-meta-4 dark:focus:border-primary text-black dark:text-white"
          >
            <option value="today">Сегодня</option>
            <option value="this_week">Текущая неделя</option>
            <option value="last_week">Прошлая неделя</option>
            <option value="this_month">Текущий месяц</option>
            <option value="last_month">Прошлый месяц</option>
            <option value="this_half_year">Текущее полугодие</option>
            <option value="this_year">Текущий год</option>
            <option value="last_year">Прошлый год</option>
            <option value="custom">Произвольно</option>
          </select>
        </div>

        <!-- Master Filter -->
        <div>
          <label class="mb-2.5 block text-black dark:text-white">Мастер</label>
          <select
            v-model="filters.masterId"
            class="w-full rounded border-[1.5px] border-stroke bg-transparent py-2 px-4 font-medium outline-none transition focus:border-primary active:border-primary dark:border-strokedark dark:bg-meta-4 dark:focus:border-primary text-black dark:text-white"
          >
            <option value="">Все мастера</option>
            <option v-for="master in masters" :key="master.id" :value="master.id">
              {{ master.first_name }} {{ master.last_name }}
            </option>
          </select>
        </div>

        <!-- Service Filter -->
        <div>
          <label class="mb-2.5 block text-black dark:text-white">Услуга</label>
          <select
            v-model="filters.serviceId"
            class="w-full rounded border-[1.5px] border-stroke bg-transparent py-2 px-4 font-medium outline-none transition focus:border-primary active:border-primary dark:border-strokedark dark:bg-meta-4 dark:focus:border-primary text-black dark:text-white"
          >
            <option value="">Все услуги</option>
            <option v-for="service in services" :key="service.id" :value="service.id">
              {{ service.name }}
            </option>
          </select>
        </div>
        
        <div class="flex items-end">
            <button 
                @click="fetchAppointments"
                class="flex justify-center rounded bg-primary py-2 px-6 font-medium text-white hover:bg-opacity-90 transition-all w-full md:w-auto"
            >
                <Icon icon="mdi:magnify" class="mr-2" width="20" />
                Применить
            </button>
        </div>
      </div>
    </div>

    <!-- Table Card -->
    <div class="rounded-sm border border-stroke bg-white px-5 pt-6 pb-2.5 shadow-default dark:border-strokedark dark:bg-bg-dark-2 sm:px-7.5 xl:pb-1">
      <div class="flex items-center justify-between mb-4">
        <h4 class="text-xl font-bold text-black dark:text-white">Список записей ({{ totalCount }})</h4>
        <div class="flex items-center gap-2">
          <span class="text-sm text-body">Строк на странице:</span>
          <select 
            v-model="pageSize" 
            @change="handlePageSizeChange"
            class="rounded border border-stroke bg-transparent py-1 px-2 outline-none focus:border-primary dark:border-strokedark dark:bg-meta-4 text-sm"
          >
            <option :value="20">20</option>
            <option :value="50">50</option>
          </select>
        </div>
      </div>

      <div class="max-w-full overflow-x-auto">
        <table class="w-full table-auto">
          <thead>
            <tr class="bg-gray-2 text-left dark:bg-meta-4">
              <th class="min-w-[120px] py-4 px-4 font-medium text-black dark:text-white xl:pl-11">Дата</th>
              <th class="min-w-[100px] py-4 px-4 font-medium text-black dark:text-white">Время</th>
              <th class="min-w-[150px] py-4 px-4 font-medium text-black dark:text-white">Услуга</th>
              <th class="min-w-[150px] py-4 px-4 font-medium text-black dark:text-white">Клиент</th>
              <th class="min-w-[120px] py-4 px-4 font-medium text-black dark:text-white">Стоимость</th>
              <th class="py-4 px-4 font-medium text-black dark:text-white">Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="appt in appointments" :key="appt.id" class="border-b border-[#eee] dark:border-strokedark">
              <td class="py-5 px-4 pl-9 xl:pl-11">
                <h5 class="font-medium text-black dark:text-white">{{ formatDateShort(appt.start_time) }}</h5>
              </td>
              <td class="py-5 px-4">
                <p class="text-black dark:text-white">{{ formatTimeSlot(appt.start_time) }}</p>
              </td>
              <td class="py-5 px-4">
                <div class="flex items-center gap-2">
                  <Icon v-if="appt.is_combo" icon="mdi:link-variant" class="text-primary" width="16" />
                  <p class="text-black dark:text-white">{{ appt.display_title || appt.service_detail?.name || '---' }}</p>
                </div>
                <p class="text-xs text-body">{{ appt.master_detail?.first_name }}</p>
              </td>
              <td class="py-5 px-4">
                <p class="text-black dark:text-white font-medium">{{ appt.client_detail?.full_name }}</p>
                <p class="text-xs text-body">{{ appt.client_detail?.phone }}</p>
              </td>
              <td class="py-5 px-4">
                <p class="text-success font-bold">{{ appt.service_detail?.total_price }} ₸</p>
              </td>
              <td class="py-5 px-4">
                <div class="flex items-center space-x-3.5">
                  <button @click="openEdit(appt)" class="hover:text-primary transition-colors" title="Редактировать">
                    <Icon icon="mdi:pencil-outline" width="20" />
                  </button>
                  <button @click="confirmDelete(appt)" class="hover:text-danger transition-colors" title="Удалить">
                    <Icon icon="mdi:trash-can-outline" width="20" />
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="appointments.length === 0 && !loading">
                <td colspan="6" class="py-10 text-center text-body italic">Записей не найдено</td>
            </tr>
            <tr v-if="loading">
                <td colspan="6" class="py-10 text-center">
                    <Icon icon="mdi:loading" class="animate-spin text-primary mx-auto" width="40" />
                </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="flex items-center justify-center gap-2 py-6">
        <div class="flex items-center gap-1">
          <button 
            v-for="page in visiblePages" 
            :key="page"
            @click="changePage(page)"
            class="flex h-9 w-9 items-center justify-center rounded border border-stroke font-medium transition-all hover:bg-primary hover:text-white dark:border-strokedark"
            :class="currentPage === page ? 'bg-primary text-white border-primary' : 'text-body dark:text-white'"
          >
            {{ page }}
          </button>
          
          <button 
            v-if="hasMorePages"
            @click="changePage(visiblePages[visiblePages.length - 1] + 1)"
            class="flex h-9 w-9 items-center justify-center rounded border border-stroke text-body transition-all hover:bg-primary hover:text-white dark:border-strokedark dark:text-white"
            title="Следующие страницы"
          >
            >>
          </button>
        </div>
      </div>
    </div>

    <!-- Edit Modal -->
    <AppointmentEditModal
      :show="showEditModal"
      :appointment="selectedAppt"
      @close="showEditModal = false"
      @success="fetchAppointments"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch, computed } from 'vue'
import { Icon } from '@iconify/vue'
import api from '../../api'
import { 
  format, 
  startOfToday, 
  endOfToday, 
  startOfWeek, 
  endOfWeek, 
  subWeeks, 
  startOfMonth, 
  endOfMonth, 
  subMonths,
  startOfQuarter,
  startOfYear,
  endOfYear,
  subYears
} from 'date-fns'
import { ru } from 'date-fns/locale'
import AppointmentEditModal from '../../components/modals/AppointmentEditModal.vue'

const appointments = ref([])
const masters = ref([])
const services = ref([])
const loading = ref(false)

// Pagination State
const currentPage = ref(1)
const pageSize = ref(20)
const totalCount = ref(0)
const totalPages = computed(() => Math.ceil(totalCount.value / pageSize.value))

const visiblePages = computed(() => {
    const pages = []
    const start = Math.floor((currentPage.value - 1) / 12) * 12 + 1
    const end = Math.min(start + 11, totalPages.value)
    for (let i = start; i <= end; i++) {
        pages.push(i)
    }
    return pages
})

const hasMorePages = computed(() => {
    if (visiblePages.value.length === 0) return false
    return visiblePages.value[visiblePages.value.length - 1] < totalPages.value
})

const activePreset = ref('today')
const filters = reactive({
  dateFrom: format(startOfToday(), 'yyyy-MM-dd'),
  dateTo: format(endOfToday(), 'yyyy-MM-dd'),
  masterId: '',
  serviceId: ''
})

const showEditModal = ref(false)
const selectedAppt = ref(null)

const applyPreset = () => {
    const now = new Date()
    let from, to = now
    
    switch (activePreset.value) {
        case 'today':
            from = startOfToday()
            to = endOfToday()
            break
        case 'this_week':
            from = startOfWeek(now, { weekStartsOn: 1 })
            to = endOfWeek(now, { weekStartsOn: 1 })
            break
        case 'last_week':
            const lastWeek = subWeeks(now, 1)
            from = startOfWeek(lastWeek, { weekStartsOn: 1 })
            to = endOfWeek(lastWeek, { weekStartsOn: 1 })
            break
        case 'this_month':
            from = startOfMonth(now)
            to = endOfMonth(now)
            break
        case 'last_month':
            const lastMonth = subMonths(now, 1)
            from = startOfMonth(lastMonth)
            to = endOfMonth(lastMonth)
            break
        case 'this_half_year':
            from = subMonths(startOfMonth(now), 5)
            to = endOfMonth(now)
            break
        case 'this_year':
            from = startOfYear(now)
            to = endOfYear(now)
            break
        case 'last_year':
            const lastYear = subYears(now, 1)
            from = startOfYear(lastYear)
            to = endOfYear(lastYear)
            break
        case 'custom':
            return
    }
    
    if (from && to) {
        filters.dateFrom = format(from, 'yyyy-MM-dd')
        filters.dateTo = format(to, 'yyyy-MM-dd')
    }
}

const fetchAppointments = async () => {
    try {
        loading.value = true
        const params = {
            date_from: filters.dateFrom,
            date_to: filters.dateTo,
            master_id: filters.masterId || undefined,
            service_id: filters.serviceId || undefined,
            page: currentPage.value,
            page_size: pageSize.value
        }
        const response = await api.get('/api/appointments/', { params })
        // DRF Pagination returns { count, next, previous, results }
        if (response.data.results) {
            appointments.value = response.data.results
            totalCount.value = response.data.count
        } else {
            appointments.value = response.data
            totalCount.value = response.data.length
        }
    } catch (err) {
        console.error('Failed to fetch appointments:', err)
    } finally {
        loading.value = false
    }
}

const handlePageSizeChange = () => {
    currentPage.value = 1
    fetchAppointments()
}

const changePage = (page) => {
    currentPage.value = page
    fetchAppointments()
}

const fetchData = async () => {
    try {
        const [mRes, sRes] = await Promise.all([
            api.get('/api/masters/'),
            api.get('/api/services/')
        ])
        masters.value = mRes.data.results || mRes.data
        services.value = sRes.data.results || sRes.data
    } catch (err) {
        console.error('Failed to fetch metadata:', err)
    }
}

const openEdit = (appt) => {
    selectedAppt.value = appt
    showEditModal.value = true
}

const confirmDelete = async (appt) => {
    if (!confirm(`Вы уверены, что хотите удалить запись клиента ${appt.client_detail?.full_name}?`)) {
        return
    }
    
    try {
        await api.delete(`/api/appointments/${appt.id}/`)
        fetchAppointments()
    } catch (err) {
        console.error('Failed to delete appointment:', err)
        alert('Ошибка при удалении записи.')
    }
}

const formatDateShort = (iso) => {
    if (!iso) return ''
    const datePart = iso.split('T')[0]
    return format(new Date(datePart), 'dd.MM.yyyy')
}

const formatTimeSlot = (iso) => {
    if (!iso) return ''
    if (iso.includes('T')) {
        return iso.split('T')[1].substring(0, 5)
    }
    return iso.substring(0, 5)
}

onMounted(() => {
    fetchData()
    fetchAppointments()
})

watch(() => [filters.dateFrom, filters.dateTo, filters.masterId, filters.serviceId], () => {
    currentPage.value = 1
    fetchAppointments()
})
</script>
