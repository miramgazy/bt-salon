<template>
  <div v-if="show" class="fixed inset-0 z-[10000] flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm" @click.self="$emit('close')">
    <div class="w-full max-w-2xl rounded-xl bg-white p-6 shadow-2xl dark:bg-bg-dark-2 md:p-8 overflow-y-auto max-h-[90vh]">
      <div class="flex justify-between items-center mb-6">
        <div>
          <h3 class="text-xl font-bold text-black dark:text-white">Открыть смену</h3>
          <div class="mt-2 flex items-center gap-2">
            <span class="text-xs font-medium text-body uppercase">Дата:</span>
            <input 
              v-model="modalDate" 
              type="date" 
              class="rounded border border-stroke bg-gray-50 py-1 px-2 text-sm text-black outline-none focus:border-primary dark:border-strokedark dark:bg-meta-4 dark:text-white"
            />
          </div>
        </div>
        <button @click="$emit('close')" class="text-body hover:text-danger px-2 transition-colors">
          <Icon icon="mdi:close" width="24" />
        </button>
      </div>

      <div v-if="loading" class="flex h-40 items-center justify-center">
        <Icon icon="mdi:loading" class="animate-spin text-primary" width="40" />
      </div>

      <div v-else>
        <div class="max-h-96 overflow-y-auto mb-8 pr-2 custom-scrollbar">
          <div 
            v-for="master in masters" 
            :key="master.id"
            class="mb-4 rounded-lg border border-stroke p-4 transition-all dark:border-strokedark"
            :class="{'bg-primary/5 border-primary ring-1 ring-primary/20': selections[master.id]?.selected}"
          >
            <div class="flex items-center justify-between mb-3">
              <label class="flex cursor-pointer items-center font-bold text-black dark:text-white">
                <input 
                  type="checkbox" 
                  v-model="selections[master.id].selected"
                  class="mr-3 h-5 w-5 rounded border-stroke text-primary focus:ring-primary dark:border-strokedark"
                />
                {{ master.first_name }} {{ master.last_name }}
              </label>
              <div v-if="selections[master.id].selected" class="flex gap-2">
                 <Icon icon="mdi:check-circle" class="text-primary" width="20" />
              </div>
            </div>

            <div v-if="selections[master.id].selected" class="grid grid-cols-1 md:grid-cols-2 gap-4 animate-fadeIn">
              <div class="grid grid-cols-2 gap-2">
                <div>
                  <label class="text-[10px] uppercase font-bold text-body block mb-1">Начало</label>
                  <input v-model="selections[master.id].work_start" type="time" class="w-full rounded border border-stroke bg-gray-50 py-1.5 px-3 text-sm text-black focus:border-primary dark:border-strokedark dark:bg-meta-4 dark:text-white" />
                </div>
                <div>
                  <label class="text-[10px] uppercase font-bold text-body block mb-1">Конец</label>
                  <input v-model="selections[master.id].work_end" type="time" class="w-full rounded border border-stroke bg-gray-50 py-1.5 px-3 text-sm text-black focus:border-primary dark:border-strokedark dark:bg-meta-4 dark:text-white" />
                </div>
              </div>
              <div class="grid grid-cols-2 gap-2">
                <div>
                  <label class="text-[10px] uppercase font-bold text-body block mb-1">Обед нач.</label>
                  <input v-model="selections[master.id].lunch_start" type="time" class="w-full rounded border border-stroke bg-gray-50 py-1.5 px-3 text-sm text-black focus:border-primary dark:border-strokedark dark:bg-meta-4 dark:text-white" />
                </div>
                <div>
                  <label class="text-[10px] uppercase font-bold text-body block mb-1">Обед кон.</label>
                  <input v-model="selections[master.id].lunch_end" type="time" class="w-full rounded border border-stroke bg-gray-50 py-1.5 px-3 text-sm text-black focus:border-primary dark:border-strokedark dark:bg-meta-4 dark:text-white" />
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="flex gap-3 mt-auto">
          <button
            @click="$emit('close')"
            class="flex-1 rounded border border-stroke py-3 px-6 text-center font-medium text-black transition hover:bg-gray-100 dark:border-strokedark dark:text-white dark:hover:bg-meta-4"
          >
            Отмена
          </button>
          <button
            @click="submit"
            :disabled="saving || !hasSelected"
            class="flex-1 rounded bg-primary py-3 px-6 text-center font-medium text-white transition hover:bg-opacity-90 active:scale-[0.98] disabled:opacity-50"
          >
            <Icon v-if="saving" icon="mdi:loading" class="animate-spin inline mr-2" />
            <Icon v-else icon="mdi:calendar-check" class="inline mr-2" width="20" />
            {{ saving ? 'Сохранение...' : 'Открыть смену' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { Icon } from '@iconify/vue'
import api from '../../api'

const props = defineProps({
  show: Boolean,
  date: String
})

const emit = defineEmits(['close', 'success'])

const loading = ref(true)
const saving = ref(false)
const masters = ref([])
const selections = reactive({})
const orgSettings = ref(null)
const modalDate = ref('')

const hasSelected = computed(() => {
  return Object.values(selections).some(s => s.selected)
})

const initMasterSelections = () => {
  masters.value.forEach(m => {
    if (!selections[m.id]) {
      selections[m.id] = {
        selected: false,
        work_start: orgSettings.value?.work_start?.slice(0, 5) || '10:00',
        work_end: orgSettings.value?.work_end?.slice(0, 5) || '20:00',
        lunch_start: orgSettings.value?.lunch_start?.slice(0, 5) || '13:00',
        lunch_end: orgSettings.value?.lunch_end?.slice(0, 5) || '14:00',
        comment: ''
      }
    }
  })
}

const fetchData = async () => {
  try {
    loading.value = true
    const [mRes, oRes] = await Promise.all([
      api.get('/api/masters/'),
      api.get('/api/organization/')
    ])
    masters.value = (mRes.data.results || mRes.data || []).filter(m => m.is_active)
    orgSettings.value = oRes.data
    initMasterSelections()
  } catch (err) {
    console.error('Failed to fetch data for quick shift:', err)
  } finally {
    loading.value = false
  }
}

const submit = async () => {
  try {
    saving.value = true
    const selectedShifts = []
    
    Object.keys(selections).forEach(masterId => {
      if (selections[masterId].selected) {
        selectedShifts.push({
          master_id: masterId,
          work_start: selections[masterId].work_start,
          work_end: selections[masterId].work_end,
          lunch_start: selections[masterId].lunch_start,
          lunch_end: selections[masterId].lunch_end,
          comment: selections[masterId].comment
        })
      }
    })

    if (selectedShifts.length === 0) return

    await api.post('/api/masters/shifts/open/', {
      date: modalDate.value,
      shifts: selectedShifts
    })
    
    emit('success')
    emit('close')
  } catch (err) {
    console.error('Failed to open shifts:', err)
    alert('Ошибка при открытии смен. Возможно, смена уже открыта.')
  } finally {
    saving.value = false
  }
}

watch(() => props.show, (newVal) => {
  if (newVal) {
    modalDate.value = props.date || new Date().toISOString().split('T')[0]
    fetchData()
  }
})

onMounted(() => {
  if (props.show) fetchData()
})
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
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
.animate-fadeIn {
  animation: fadeIn 0.3s ease-out;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-5px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
