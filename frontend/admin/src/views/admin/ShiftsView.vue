<template>
  <div class="mx-auto max-w-7xl">
    <!-- Breadcrumb Start -->
    <div class="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <h2 class="text-title-md2 font-bold text-black dark:text-white">
        Управление сменами
      </h2>
      <nav>
        <ol class="flex items-center gap-2">
          <li>
            <router-link class="font-medium" to="/admin/calendar">Dashboard /</router-link>
          </li>
          <li class="font-medium text-primary">Смены</li>
        </ol>
      </nav>
    </div>
    <!-- Breadcrumb End -->

    <!-- Top Controls -->
    <div class="mb-6 flex flex-wrap items-center justify-between gap-4 rounded-sm border border-stroke bg-white py-4 px-6 shadow-default dark:border-strokedark dark:bg-bg-dark-2">
      <div class="flex items-center gap-4">
        <label class="font-medium text-black dark:text-white">Выберите дату:</label>
        <input 
          v-model="selectedDate" 
          type="date" 
          class="rounded border border-stroke bg-gray-50 py-2 px-4 outline-none focus:border-primary dark:border-strokedark dark:bg-bg-dark dark:text-white" 
        />
        <button 
          @click="fetchShifts"
          class="inline-flex items-center justify-center rounded-md bg-primary py-2 px-6 text-center font-medium text-white hover:bg-opacity-90 transition-all active:scale-95"
        >
          Применить
        </button>
      </div>
      <button 
        @click="openModal"
        class="inline-flex items-center justify-center rounded-md bg-success py-2 px-6 text-center font-medium text-white hover:bg-opacity-90 transition-all active:scale-95"
      >
        <Icon icon="mdi:plus-circle" width="20" class="mr-2" />
        Открыть смену
      </button>
    </div>

    <!-- Main Table -->
    <div class="rounded-sm border border-stroke bg-white shadow-default dark:border-strokedark dark:bg-bg-dark-2">
      <div class="p-4 sm:p-6 xl:p-7.5">
        <div v-if="loading" class="flex h-40 items-center justify-center">
            <div class="h-10 w-10 animate-spin rounded-full border-4 border-solid border-primary border-t-transparent"></div>
        </div>
        
        <div v-else-if="shifts.length === 0" class="flex flex-col items-center justify-center py-20 text-center">
            <div class="mb-4 flex h-20 w-20 items-center justify-center rounded-full bg-primary/10 text-primary">
                <Icon icon="mdi:calendar-clock" width="40" />
            </div>
            <h4 class="mb-2 text-xl font-bold text-black dark:text-white">Смены не найдены</h4>
            <p class="text-body">На выбранную дату ({{ selectedDate }}) смены еще не открыты.</p>
        </div>

        <div v-else class="max-w-full overflow-x-auto">
          <table class="w-full table-auto text-left">
            <thead>
              <tr class="bg-gray-2 dark:bg-meta-4">
                <th class="py-4 px-4 font-medium text-black dark:text-white xl:pl-11">Мастер</th>
                <th class="py-4 px-4 font-medium text-black dark:text-white">Рабочее время</th>
                <th v-if="organization?.has_lunch_break" class="py-4 px-4 font-medium text-black dark:text-white">Обед</th>
                <th class="py-4 px-4 font-medium text-black dark:text-white">Комментарий</th>
                <th class="py-4 px-4 font-medium text-black dark:text-white">Статус</th>
                <th class="py-4 px-4 font-medium text-black dark:text-white">Действие</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="shift in shifts" :key="shift.id" class="border-b border-stroke dark:border-strokedark">
                <td class="py-5 px-4 pl-9 xl:pl-11">
                  <h5 class="font-medium text-black dark:text-white">{{ shift.master_name }} {{ shift.master_last_name }}</h5>
                </td>
                <td class="py-5 px-4 text-black dark:text-white">
                  {{ formatTime(shift.work_start) }} — {{ formatTime(shift.work_end) }}
                </td>
                <td v-if="organization?.has_lunch_break" class="py-5 px-4 text-black dark:text-white">
                  {{ formatTime(shift.lunch_start) }} — {{ formatTime(shift.lunch_end) }}
                </td>
                <td class="py-5 px-4 text-black dark:text-white">
                  <p class="max-w-[200px] truncate text-xs" :title="shift.comment">{{ shift.comment || '—' }}</p>
                </td>
                <td class="py-5 px-4">
                  <span v-if="shift.opened_by_admin" class="inline-flex rounded-full bg-warning/10 py-1 px-3 text-sm font-medium text-warning">
                    Админ
                  </span>
                  <span v-else class="inline-flex rounded-full bg-success/10 py-1 px-3 text-sm font-medium text-success">
                    Мастер
                  </span>
                  <span v-if="shift.actual_start" class="ml-2 inline-flex rounded-full bg-success/10 py-1 px-3 text-sm font-medium text-success" title="Мастер на месте">
                    <Icon icon="mdi:check-all" width="14" />
                  </span>
                </td>
                <td class="py-5 px-4">
                  <div class="flex items-center space-x-3.5">
                    <button @click="editShift(shift)" class="hover:text-primary transition-all hover:scale-110" title="Редактировать">
                      <Icon icon="mdi:pencil-outline" width="18" />
                    </button>
                    <button @click="confirmDelete(shift.id)" class="hover:text-danger transition-all hover:scale-110" title="Удалить">
                      <Icon icon="mdi:trash-can-outline" width="18" />
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Open Shift Modal (QuickShiftModal) -->
    <QuickShiftModal 
      :show="showModal" 
      :date="selectedDate" 
      @close="showModal = false"
      @success="fetchShifts"
    />

    <!-- Edit Single Shift Modal -->
    <div v-if="showEditModal" class="fixed inset-0 z-9999 flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm">
      <div class="w-full max-w-150 rounded-lg bg-white py-8 px-8 dark:bg-bg-dark-2 sm:px-12.5 overflow-y-auto max-h-[90vh]">
        <div class="flex justify-between items-center mb-6">
            <h3 class="text-2xl font-bold text-black dark:text-white">
              Редактировать смену
            </h3>
            <button @click="showEditModal = false" class="text-body hover:text-danger">
              <Icon icon="mdi:close" width="24" />
            </button>
        </div>

        <div class="mb-6 flex items-center gap-4 border-b border-stroke pb-4 dark:border-strokedark">
            <div class="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center text-primary">
                <Icon icon="mdi:account" width="24" />
            </div>
            <div>
                <h4 class="font-bold text-black dark:text-white">{{ editForm.master_name }}</h4>
                <p class="text-sm text-body">Смена на {{ selectedDate }}</p>
            </div>
        </div>

        <div class="grid grid-cols-2 gap-4 mb-6">
            <div>
                <label class="mb-2.5 block text-sm font-medium text-black dark:text-white">Начало работы</label>
                <input v-model="editForm.work_start" type="time" class="w-full rounded border border-stroke bg-gray-50 py-3 px-5 outline-none text-black focus:border-primary dark:border-strokedark dark:bg-meta-4 dark:text-white" />
            </div>
            <div>
                <label class="mb-2.5 block text-sm font-medium text-black dark:text-white">Конец работы</label>
                <input v-model="editForm.work_end" type="time" class="w-full rounded border border-stroke bg-gray-50 py-3 px-5 outline-none text-black focus:border-primary dark:border-strokedark dark:bg-meta-4 dark:text-white" />
            </div>
        </div>

        <div v-if="organization?.has_lunch_break" class="grid grid-cols-2 gap-4 mb-6">
            <div>
                <label class="mb-2.5 block text-sm font-medium text-black dark:text-white">Обед (с)</label>
                <input v-model="editForm.lunch_start" type="time" class="w-full rounded border border-stroke bg-gray-50 py-3 px-5 outline-none text-black focus:border-primary dark:border-strokedark dark:bg-meta-4 dark:text-white" />
            </div>
            <div>
                <label class="mb-2.5 block text-sm font-medium text-black dark:text-white">Обед (по)</label>
                <input v-model="editForm.lunch_end" type="time" class="w-full rounded border border-stroke bg-gray-50 py-3 px-5 outline-none text-black focus:border-primary dark:border-strokedark dark:bg-meta-4 dark:text-white" />
            </div>
        </div>

        <div class="mb-8">
            <label class="mb-2.5 block text-sm font-medium text-black dark:text-white">Заметка</label>
            <textarea 
                v-model="editForm.comment" 
                rows="3"
                placeholder="Комментарий к смене..."
                class="w-full rounded border border-stroke bg-gray-50 py-3 px-5 outline-none text-black focus:border-primary dark:border-strokedark dark:bg-meta-4 dark:text-white"
            ></textarea>
        </div>

        <div class="flex gap-4">
          <button
            @click="showEditModal = false"
            class="flex-1 rounded border border-stroke py-3 px-6 text-center font-medium text-black transition hover:bg-gray-100 dark:border-strokedark dark:text-white dark:hover:bg-meta-4"
          >
            Отмена
          </button>
          <button
            @click="updateShift"
            :disabled="saving"
            class="flex-1 rounded bg-primary py-3 px-6 text-center font-medium text-white transition hover:bg-opacity-90 active:scale-95 disabled:opacity-50"
          >
            <Icon icon="mdi:content-save" width="20" class="inline mr-2" />
            {{ saving ? 'Сохранение...' : 'Обновить смену' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import api from '../../api'
import { Icon } from '@iconify/vue'
import QuickShiftModal from '../../components/modals/QuickShiftModal.vue'

const loading = ref(true)
const saving = ref(false)
const showModal = ref(false)
const showEditModal = ref(false)
const selectedDate = ref(new Date().toISOString().split('T')[0])
const shifts = ref([])
const organization = ref(null)

const editForm = reactive({
    id: null,
    master_name: '',
    work_start: '',
    work_end: '',
    lunch_start: '',
    lunch_end: '',
    comment: ''
})

const fetchShifts = async () => {
    try {
        loading.value = true
        const response = await api.get('/api/masters/shifts/', {
            params: { date: selectedDate.value }
        })
        // Filter is_open=true if backend doesn't do it by default for the date
        const data = response.data.results || response.data || []
        shifts.value = data.filter(s => s.date === selectedDate.value && s.is_open)
    } catch (err) {
        console.error('Error fetching shifts:', err)
    } finally {
        loading.value = false
    }
}

const fetchOrgSettings = async () => {
    try {
        const response = await api.get('/api/organization/')
        organization.value = response.data
        if (organization.value) {
            organization.value.work_start = organization.value.work_start?.slice(0, 5)
            organization.value.work_end = organization.value.work_end?.slice(0, 5)
            organization.value.lunch_start = organization.value.lunch_start?.slice(0, 5)
            organization.value.lunch_end = organization.value.lunch_end?.slice(0, 5)
        }
    } catch (err) {
        console.error('Error fetching org settings:', err)
    }
}

const openModal = () => {
    showModal.value = true
}

const editShift = (shift) => {
    editForm.id = shift.id
    editForm.master_name = `${shift.master_name} ${shift.master_last_name}`
    editForm.work_start = formatTime(shift.work_start)
    editForm.work_end = formatTime(shift.work_end)
    editForm.lunch_start = formatTime(shift.lunch_start)
    editForm.lunch_end = formatTime(shift.lunch_end)
    editForm.comment = shift.comment || ''
    showEditModal.value = true
}

const updateShift = async () => {
    try {
        saving.value = true
        await api.patch(`/api/masters/shifts/${editForm.id}/`, {
            work_start: editForm.work_start,
            work_end: editForm.work_end,
            lunch_start: editForm.lunch_start,
            lunch_end: editForm.lunch_end,
            comment: editForm.comment
        })
        showEditModal.value = false
        fetchShifts()
    } catch (err) {
        console.error('Error updating shift:', err)
        alert('Ошибка при обновлении смены')
    } finally {
        saving.value = false
    }
}

const confirmDelete = async (id) => {
    if (confirm('Вы уверены, что хотите удалить эту смену?')) {
        try {
            await api.delete(`/api/masters/shifts/${id}/`)
            fetchShifts()
        } catch (err) {
            console.error('Error deleting shift:', err)
            alert('Ошибка при удалении смены')
        }
    }
}

const formatTime = (timeStr) => {
    if (!timeStr) return ''
    return timeStr.slice(0, 5)
}

onMounted(async () => {
    await fetchOrgSettings()
    fetchShifts()
})
</script>

<style scoped>
.text-title-md2 {
  font-size: 1.625rem;
  line-height: 2.125rem;
}
.max-w-200 {
  max-width: 50rem;
}
.animate-fadeIn {
  animation: fadeIn 0.3s ease-out;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-5px); }
  to { opacity: 1; transform: translateY(0); }
}
.custom-scrollbar::-webkit-scrollbar {
  width: 5px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #e2e8f0;
  border-radius: 10px;
}
.dark .custom-scrollbar::-webkit-scrollbar-thumb {
  background: #2e3a47;
}
</style>
