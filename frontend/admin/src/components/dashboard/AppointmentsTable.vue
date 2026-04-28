<template>
  <div class="rounded-sm border border-stroke bg-white px-5 pt-6 pb-2.5 shadow-default dark:border-strokedark dark:bg-bg-dark-2 sm:px-7.5 xl:pb-1">
    <div class="mb-6 flex flex-wrap items-center justify-between gap-4">
      <h4 class="text-xl font-bold text-black dark:text-white">Детальный список записей</h4>
      
      <button 
        @click="$emit('exportExcel')"
        class="inline-flex items-center justify-center gap-2.5 rounded-md bg-success py-2 px-4 text-center font-medium text-white hover:bg-opacity-90 active:scale-95 transition-all text-sm"
      >
        <Icon icon="mdi:microsoft-excel" width="20" />
        Экспорт в Excel
      </button>
    </div>

    <div class="max-w-full overflow-x-auto">
      <table class="w-full table-auto">
        <thead>
          <tr class="bg-gray-2 text-left dark:bg-meta-4 text-xs uppercase tracking-wider">
            <th class="min-w-[150px] py-4 px-4 font-bold text-black dark:text-white xl:pl-11">Дата/Время</th>
            <th class="min-w-[120px] py-4 px-4 font-bold text-black dark:text-white">Клиент</th>
            <th class="min-w-[120px] py-4 px-4 font-bold text-black dark:text-white">Мастер</th>
            <th class="min-w-[150px] py-4 px-4 font-bold text-black dark:text-white">Услуги</th>
            <th class="min-w-[100px] py-4 px-4 font-bold text-black dark:text-white">Стоимость</th>
            <th class="min-w-[100px] py-4 px-4 font-bold text-black dark:text-white">Доля мастера</th>
            <th class="min-w-[100px] py-4 px-4 font-bold text-black dark:text-white">Маржа</th>
            <th class="min-w-[100px] py-4 px-4 font-bold text-black dark:text-white">Статус</th>
          </tr>
        </thead>
        <tbody>
          <tr 
            v-for="appt in data" 
            :key="appt.id" 
            class="border-b border-stroke dark:border-strokedark hover:bg-gray-50 dark:hover:bg-meta-4/10"
            :class="{ 
              'opacity-50 !bg-gray-50 dark:!bg-meta-4/20': appt.status === 'cancelled',
              'bg-primary/[0.03] dark:bg-primary/[0.05]': appt.appointment_type !== 'single'
            }"
          >
            <td class="py-4 px-4 pl-9 xl:pl-11">
              <p class="text-sm font-medium text-black dark:text-white">{{ formatDate(appt.datetime) }}</p>
              <p class="text-xs text-body">{{ formatTime(appt.datetime) }}</p>
            </td>
            <td class="py-4 px-4">
              <p class="text-sm text-black dark:text-white font-medium">{{ appt.client_name }}</p>
            </td>
            <td class="py-4 px-4">
              <p class="text-sm text-black dark:text-white">{{ appt.master_name }}</p>
            </td>
            <td class="py-4 px-4">
              <div class="flex items-center gap-2">
                <Icon 
                  v-if="appt.appointment_type === 'combo_sub'" 
                  icon="mdi:subdirectory-arrow-right" 
                  class="text-primary/60 shrink-0" 
                  width="14" 
                />
                <Icon 
                  v-else-if="appt.appointment_type === 'combo_master'" 
                  icon="mdi:layers-outline" 
                  class="text-primary shrink-0" 
                  width="16" 
                />
                <p class="text-xs text-black dark:text-white truncate max-w-[150px]" :title="appt.services.join(', ')">
                  {{ appt.services.join(', ') }}
                </p>
              </div>
            </td>
            <td class="py-4 px-4">
              <p class="text-sm font-bold text-black dark:text-white">{{ formatCurrency(appt.total_cost) }}</p>
            </td>
            <td class="py-4 px-4">
              <p class="text-sm text-black dark:text-white">{{ formatCurrency(appt.master_share) }}</p>
            </td>
            <td class="py-4 px-4">
              <p class="text-sm text-success font-medium">{{ formatCurrency(appt.owner_margin) }}</p>
            </td>
            <td class="py-4 px-4">
              <span 
                class="inline-flex rounded-full py-1 px-3 text-xs font-medium"
                :class="statusClasses[appt.status] || 'bg-gray-100 text-gray-800'"
              >
                {{ statusLabels[appt.status] || appt.status }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Numeric Pagination -->
    <div class="flex flex-wrap items-center justify-between py-6 gap-4">
      <p class="text-sm text-body">
        Показано {{ data.length }} из {{ totalCount }} записей
      </p>
      
      <div v-if="totalPages > 1" class="flex items-center gap-1">
        <button 
          v-for="page in visiblePages" 
          :key="page"
          @click="$emit('pageChange', page)"
          class="flex h-9 w-9 items-center justify-center rounded border border-stroke font-medium transition-all hover:bg-primary hover:text-white dark:border-strokedark"
          :class="currentPage === page ? 'bg-primary text-white border-primary' : 'text-body dark:text-white'"
        >
          {{ page }}
        </button>
        
        <button 
          v-if="hasMorePages"
          @click="$emit('pageChange', visiblePages[visiblePages.length - 1] + 1)"
          class="flex h-9 w-9 items-center justify-center rounded border border-stroke text-body transition-all hover:bg-primary hover:text-white dark:border-strokedark dark:text-white"
          title="Следующие страницы"
        >
          >>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Icon } from '@iconify/vue'

const props = defineProps({
  data: Array,
  totalCount: Number,
  currentPage: Number,
  totalPages: Number
})

defineEmits(['pageChange', 'exportExcel'])

const visiblePages = computed(() => {
    const pages = []
    const start = Math.floor((props.currentPage - 1) / 12) * 12 + 1
    const end = Math.min(start + 11, props.totalPages)
    for (let i = start; i <= end; i++) {
        pages.push(i)
    }
    return pages
})

const hasMorePages = computed(() => {
    if (visiblePages.value.length === 0) return false
    return visiblePages.value[visiblePages.value.length - 1] < props.totalPages
})

const formatCurrency = (val) => {
  return new Intl.NumberFormat('ru-KZ', { maximumFractionDigits: 0 }).format(val) + ' ₸'
}

const formatDate = (iso) => new Date(iso).toLocaleDateString('ru-RU')
const formatTime = (iso) => new Date(iso).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })

const statusLabels = {
  pending: 'Ожидает',
  confirmed: 'Подтверждена',
  cancelled: 'Отменена',
  done: 'Завершена'
}

const statusClasses = {
  pending: 'bg-warning/10 text-warning',
  confirmed: 'bg-primary/10 text-primary',
  cancelled: 'bg-danger/10 text-danger',
  done: 'bg-success/10 text-success'
}
</script>
