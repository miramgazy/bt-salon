<template>
  <div v-if="show" class="fixed inset-0 z-[99999] flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm" @click.self="$emit('close')">
    <div class="w-full max-w-md rounded-xl bg-white dark:bg-bg-dark-2 shadow-2xl overflow-hidden flex flex-col">
       <!-- Header -->
       <div class="px-6 py-4 border-b border-stroke dark:border-strokedark flex justify-between items-center bg-gray-50 dark:bg-meta-4">
         <h3 class="font-bold text-black dark:text-white">Редактирование записи</h3>
         <button @click="$emit('close')" class="text-body hover:text-danger"><Icon icon="mdi:close" width="24" /></button>
       </div>
       
       <!-- Body -->
       <div class="p-6">
         <!-- Client Info -->
         <div class="mb-4">
            <label class="text-xs text-body mb-1 block">Клиент</label>
            <p class="font-medium text-black dark:text-white">{{ appointment?.client_detail?.full_name || 'Не указан' }}</p>
            <p class="text-sm text-body">{{ appointment?.client_detail?.phone || '' }}</p>
         </div>

         <!-- Service Info -->
         <div class="mb-6">
            <label class="text-xs text-body mb-1 block">Услуга</label>
            <p class="font-medium text-black dark:text-white">{{ appointment?.service_detail?.name || 'Не указана' }}</p>
            <p class="text-sm text-body">Длительность: {{ appointment?.service_detail?.duration_minutes }} мин.</p>
         </div>

         <!-- Time Edit -->
         <div class="mb-4 bg-gray-50 dark:bg-meta-4 p-4 rounded-lg">
            <label class="text-sm font-medium text-black dark:text-white mb-2 block">Время начала</label>
            <input 
              type="time" 
              v-model="editedTime"
              class="w-full rounded border border-stroke bg-white py-2 px-3 text-black outline-none focus:border-primary dark:border-strokedark dark:bg-bg-dark-2 dark:text-white"
            />
            <p class="text-xs text-body mt-2">
              Окончание (автоматически): <span class="font-bold text-black dark:text-white">{{ calculatedEndTime }}</span>
            </p>
         </div>
       </div>

       <!-- Footer -->
       <div class="px-6 py-4 border-t border-stroke dark:border-strokedark flex gap-3">
         <button @click="$emit('close')" class="flex-1 rounded border border-stroke py-2 text-center font-medium hover:bg-gray-100 transition-colors dark:border-strokedark dark:hover:bg-meta-4 text-black dark:text-white">Отмена</button>
         <button @click="save" :disabled="loading" class="flex-1 rounded bg-primary py-2 text-center font-medium text-white hover:bg-opacity-90 transition-colors disabled:opacity-50">
           <Icon v-if="loading" icon="mdi:loading" class="animate-spin inline mr-1" />
           Сохранить
         </button>
       </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { Icon } from '@iconify/vue'
import api from '../../api'

const props = defineProps({
  show: Boolean,
  appointment: Object
})
const emit = defineEmits(['close', 'success'])

const loading = ref(false)
const editedTime = ref('')

// Initialize local time when opened
watch(() => props.show, (val) => {
  if (val && props.appointment?.start_time) {
    if (props.appointment.start_time.includes('T')) {
      editedTime.value = props.appointment.start_time.split('T')[1].substring(0, 5)
    } else {
      editedTime.value = props.appointment.start_time.substring(0, 5)
    }
  }
})

// Calculate end time string based on start time string + service duration
const calculatedEndTime = computed(() => {
  if (!editedTime.value || !props.appointment?.service_detail?.duration_minutes) return ''
  const [hours, mins] = editedTime.value.split(':').map(Number)
  const totalMins = hours * 60 + mins + props.appointment.service_detail.duration_minutes
  const endHours = Math.floor(totalMins / 60) % 24
  const endMins = totalMins % 60
  return `${String(endHours).padStart(2, '0')}:${String(endMins).padStart(2, '0')}`
})

const save = async () => {
  if (!editedTime.value || !props.appointment) return
  
  try {
    loading.value = true
    
    // Construct new ISO datetime strings maintaining the existing date
    const datePart = props.appointment.start_time.split('T')[0] // 'YYYY-MM-DD'
    const newStart = `${datePart}T${editedTime.value}:00`
    const newEnd = `${datePart}T${calculatedEndTime.value}:00`

    await api.patch(`/api/appointments/${props.appointment.id}/`, {
      master: props.appointment.master, // the new master ID if it was dropped on another master's row
      start_time: newStart,
      end_time: newEnd
    })
    
    emit('success')
    emit('close')
  } catch (err) {
    console.error('Failed to update appointment:', err)
    alert(err.response?.data?.non_field_errors?.[0] || 'Ошибка при обновлении записи. Возможно, время пересекается с другой записью.')
  } finally {
    loading.value = false
  }
}
</script>
