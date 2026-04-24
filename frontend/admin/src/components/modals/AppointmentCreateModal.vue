<template>
  <div v-if="show" class="fixed inset-0 z-9999 flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm">
    <div class="w-full max-w-230 rounded-lg bg-white py-8 px-8 dark:bg-bg-dark-2 sm:px-12.5 overflow-y-auto max-h-[95vh]">
      <div class="flex justify-between items-center mb-6">
          <h3 class="text-2xl font-bold text-black dark:text-white">
            Новая запись на {{ formatDate(date) }}
          </h3>
          <button @click="$emit('close')" class="text-body hover:text-danger">
            <Icon icon="mdi:close" width="24" />
          </button>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div>
          <label class="mb-3 block text-sm font-medium text-black dark:text-white">
            Имя клиента <span class="text-danger">*</span>
          </label>
          <input
            v-model="clientName"
            type="text"
            placeholder="Введите имя"
            class="w-full rounded border border-stroke bg-gray-50 py-3 px-5 outline-none focus:border-primary dark:border-strokedark dark:bg-meta-4 dark:text-white"
          />
        </div>
        <div>
          <label class="mb-3 block text-sm font-medium text-black dark:text-white">
            Номер телефона
          </label>
          <input
            v-model="clientPhone"
            type="text"
            placeholder="+7 (___) ___-__-__"
            class="w-full rounded border border-stroke bg-gray-50 py-3 px-5 outline-none focus:border-primary dark:border-strokedark dark:bg-meta-4 dark:text-white"
          />
        </div>
      </div>

      <div class="mb-6">
        <div class="mb-4">
          <h4 class="font-bold text-black dark:text-white">Услуги и мастера</h4>
          <p class="text-xs text-body">Первая услуга выбирается обязательно, остальные можно добавить при необходимости.</p>
        </div>

        <div class="space-y-6">
          <div 
            v-for="(row, index) in selectedServices" 
            :key="index"
            class="rounded-lg border border-stroke p-4 dark:border-strokedark relative"
          >
            <button 
              v-if="selectedServices.length > 1"
              @click="removeServiceRow(index)"
              class="absolute -top-2 -right-2 h-6 w-6 rounded-full bg-danger text-white flex items-center justify-center hover:bg-opacity-90 shadow-md"
            >
              <Icon icon="mdi:close" width="14" />
            </button>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <label class="text-xs font-bold uppercase text-body mb-1 block">Услуга</label>
                <select 
                  v-model="row.service_id" 
                  @change="onServiceChange(index)"
                  class="w-full rounded border border-stroke bg-gray-50 py-2 px-3 text-sm outline-none focus:border-primary dark:border-strokedark dark:bg-meta-4 dark:text-white"
                >
                  <option value="">Выберите услугу</option>
                  <option v-for="s in allServices" :key="s.id" :value="s.id">
                    {{ s.name }} ({{ s.duration_minutes }} мин) — {{ s.total_price }} ₸
                  </option>
                </select>
              </div>
              <div>
                <label class="text-xs font-bold uppercase text-body mb-1 block">Мастер</label>
                <div class="flex items-center gap-2">
                  <select 
                    v-model="row.master_id" 
                    :disabled="!row.service_id"
                    class="flex-1 rounded border border-stroke bg-gray-50 py-2 px-3 text-sm outline-none focus:border-primary dark:border-strokedark dark:bg-meta-4 dark:text-white"
                  >
                    <option value="">Выберите мастера</option>
                    <option v-for="m in getFilteredMasters(row.service_id)" :key="m.id" :value="m.id">
                      {{ m.first_name }} {{ m.last_name }}
                    </option>
                  </select>
                  <button 
                    v-if="row.service_id"
                    @click="openQuickShift"
                    class="h-9 w-9 flex items-center justify-center rounded border border-stroke bg-white hover:bg-gray-50 dark:border-strokedark dark:bg-meta-4 transition-colors shrink-0"
                    title="Открыть смену"
                  >
                     <Icon icon="mdi:calendar-plus" class="text-primary" width="20" />
                  </button>
                </div>
              </div>
            </div>

            <div v-if="row.master_id" class="animate-fadeIn">
              <TimeSlotPicker 
                :master-id="row.master_id"
                :service-id="row.service_id"
                :service-duration="getDuration(row.service_id)"
                :date="date"
                v-model="row.start_time"
              />
              
              <div class="mt-4">
                <label class="text-xs font-bold uppercase text-body mb-1 block">Комментарий к услуге</label>
                <textarea
                  v-model="row.notes"
                  rows="2"
                  placeholder="Особые пожелания или детали..."
                  class="w-full rounded border border-stroke bg-gray-50 py-2 px-3 text-sm text-black outline-none focus:border-primary dark:border-strokedark dark:bg-meta-4 dark:text-white"
                ></textarea>
              </div>
            </div>
          </div>
        </div>
        <div class="mt-4 flex justify-center">
          <button 
            @click="addServiceRow"
            class="flex items-center gap-2 rounded-md border border-primary border-dashed py-2 px-4 text-sm font-medium text-primary hover:bg-primary/5 transition-all"
          >
            <Icon icon="mdi:plus-circle" width="18" /> Добавить еще одну услугу
          </button>
        </div>
      </div>

      <div v-if="availableMasters.length === 0" class="mb-6 p-4 rounded-lg bg-warning/10 border border-warning/20 flex items-center gap-3">
        <Icon icon="mdi:alert-circle-outline" class="text-warning shrink-0" width="24" />
        <p class="text-xs text-warning leading-tight">
          На указанную дату ещё нет открытых смен у мастеров. 
          Нажмите <Icon icon="mdi:calendar-plus" class="inline" /> рядом с полем мастера, чтобы открыть смену.
        </p>
      </div>

      <div class="flex gap-4">
        <button
          @click="$emit('close')"
          class="flex-1 rounded border border-stroke py-3 px-6 text-center font-medium text-black transition hover:bg-gray-100 dark:border-strokedark dark:text-white dark:hover:bg-meta-4"
        >
          Отмена
        </button>
        <button
          @click="submit"
          :disabled="loading || !isValid"
          class="flex-1 rounded bg-primary py-3 px-6 text-center font-medium text-white transition hover:bg-opacity-90 active:scale-95 disabled:opacity-50"
        >
          <Icon v-if="loading" icon="mdi:loading" class="animate-spin inline mr-2" />
          {{ loading ? 'Сохранение...' : 'Создать запись' }}
        </button>
      </div>
    </div>

    <!-- Quick Shift Modal -->
    <QuickShiftModal 
      :show="showQuickShift" 
      :date="date" 
      @close="showQuickShift = false"
      @success="fetchData"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { Icon } from '@iconify/vue'
import api from '../../api'
import TimeSlotPicker from '../calendar/TimeSlotPicker.vue'
import QuickShiftModal from './QuickShiftModal.vue'

const props = defineProps({
  show: Boolean,
  date: String, // YYYY-MM-DD
  prefilledMasterId: [Number, String],
  prefilledTime: String // ISO string or just "HH:MM"
})

const emit = defineEmits(['close', 'success'])

const clientName = ref('')
const clientPhone = ref('')
const selectedServices = ref([
  { service_id: '', master_id: '', start_time: '', notes: '' }
])

const allServices = ref([])
const availableMasters = ref([])
const loading = ref(false)
const showQuickShift = ref(false)

watch(() => props.show, (newVal) => {
  if (newVal) {
    clientName.value = ''
    clientPhone.value = ''
    selectedServices.value = [
      { 
        service_id: '', 
        master_id: props.prefilledMasterId || '', 
        start_time: props.prefilledTime 
          ? (props.prefilledTime.includes('T') ? props.prefilledTime : `${props.date}T${props.prefilledTime}:00`)
          : '',
        notes: ''
      }
    ]
    fetchData()
  }
})

const isValid = computed(() => {
  return clientName.value && 
         clientPhone.value && 
         selectedServices.value.every(s => s.service_id && s.master_id && s.start_time)
})

const fetchData = async () => {
  try {
    const [svcs, mstrs] = await Promise.all([
      api.get('/api/services/'),
      api.get('/api/masters/working/', { params: { date: props.date } })
    ])
    allServices.value = svcs.data.results || svcs.data || []
    availableMasters.value = mstrs.data
  } catch (err) {
    console.error('Error fetching data:', err)
  }
}

const addServiceRow = () => {
  selectedServices.value.push({ service_id: '', master_id: '', start_time: '', notes: '' })
}

const openQuickShift = () => {
  showQuickShift.value = true
}

const removeServiceRow = (index) => {
  selectedServices.value.splice(index, 1)
}

const getFilteredMasters = (serviceId) => {
  if (!serviceId) return availableMasters.value
  return availableMasters.value.filter(m => {
    return m.services && m.services.includes(Number(serviceId))
  })
}

const onServiceChange = (index) => {
  // Check if current master is still valid for the new service
  const row = selectedServices.value[index]
  if (row.master_id) {
    const validMasters = getFilteredMasters(row.service_id)
    if (!validMasters.find(m => m.id === Number(row.master_id))) {
      row.master_id = ''
    }
  }
}

const getDuration = (serviceId) => {
  return allServices.value.find(s => s.id === serviceId)?.duration_minutes || 0
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' })
}

const submit = async () => {
  try {
    loading.value = true
    const res = await api.post('/api/appointments/bulk-create/', {
      client_name: clientName.value,
      client_phone: clientPhone.value,
      bookings: selectedServices.value
    })
    
    if (res.data.appointment_ids && res.data.appointment_ids.length > 0) {
      if (res.data.warnings) {
        alert('Некоторые записи не были созданы:\n' + res.data.warnings.join('\n'))
      }
      emit('success')
      emit('close')
    } else {
      alert('Ошибка: Записи не были созданы. Проверьте, открыты ли смены у мастеров.')
    }
  } catch (err) {
    console.error('Error creating appointments:', err)
    const detail = err.response?.data?.error || err.response?.data?.details?.join('\n') || 'Ошибка при создании записи'
    alert(detail)
  } finally {
    loading.value = false
  }
}

watch(() => props.date, (newDate) => {
  if (newDate) fetchData()
}, { immediate: true })

onMounted(() => {
  if (props.date) fetchData()
})
</script>

<style scoped>
.max-w-230 {
  max-width: 57.5rem;
}
.animate-fadeIn {
  animation: fadeIn 0.3s ease-out;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-5px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
