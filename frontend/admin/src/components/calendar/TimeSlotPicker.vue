<template>
  <div class="w-full">
    <div class="mb-2 flex items-center justify-between">
      <label class="text-xs font-semibold uppercase tracking-wider text-body">
        Выберите время{{ serviceDuration > 0 ? ` (${serviceDuration} мин)` : '' }}
      </label>
      <span v-if="selectedTime" class="text-xs font-bold text-primary">
        Выбрано: {{ selectedTime }}
      </span>
    </div>
    
    <div v-if="loading" class="flex h-12 items-center justify-center rounded border border-stroke bg-gray-50 dark:border-strokedark dark:bg-meta-4">
      <div class="h-5 w-5 animate-spin rounded-full border-2 border-solid border-primary border-t-transparent"></div>
    </div>
    
    <div v-else-if="slots.length === 0" class="flex h-12 items-center justify-center rounded border border-stroke bg-gray-100 px-4 text-xs italic dark:border-strokedark dark:bg-meta-4">
      Нет доступных смен у мастера на эту дату
    </div>

    <div v-else class="relative">
      <div class="flex gap-1 overflow-x-auto pb-2 custom-scrollbar">
        <button
          v-for="slot in slots"
          :key="slot.start_iso"
          type="button"
          @click="selectSlot(slot)"
          class="flex min-w-[65px] flex-col items-center justify-center rounded-lg py-3 px-2 transition-all duration-200"
          :class="[
            slot.status === 'available' 
              ? 'bg-success/5 text-success hover:bg-success hover:text-white border border-success/20 cursor-pointer active:scale-95' 
              : slot.status === 'lunch' 
                ? 'bg-warning/30 text-warning border-2 border-dashed border-warning/40 cursor-help' 
                : 'bg-danger/10 text-danger border border-danger/20 cursor-not-allowed opacity-60',
            selectedTime === slot.time ? '!bg-primary !text-white !border-primary ring-2 ring-primary/30 ring-offset-2 dark:ring-offset-bg-dark transform scale-105 z-10' : ''
          ]"
          :title="slot.status === 'lunch' ? 'Обеденный перерыв' : (slot.status === 'busy' ? 'Время занято' : 'Свободно')"
        >
          <span class="text-xs font-bold">{{ slot.time }}</span>
          <div class="mt-1 h-1.5 w-1.5 rounded-full" :class="[
            slot.status === 'available' ? 'bg-success' : 
            slot.status === 'lunch' ? 'bg-warning' : 'bg-danger'
          ]"></div>
        </button>
      </div>
      
      <!-- Legend -->
      <div class="mt-2 flex gap-4 text-[10px] text-body">
        <div class="flex items-center gap-1">
          <div class="h-2 w-2 rounded-full bg-success"></div> Свободно
        </div>
        <div class="flex items-center gap-1">
          <div class="h-2 w-2 rounded-full bg-danger"></div> Занято
        </div>
        <div class="flex items-center gap-1">
          <div class="h-2 w-2 rounded-full bg-warning"></div> Перерыв
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import api from '../../api'

const props = defineProps({
  masterId: [Number, String],
  serviceId: [Number, String],
  serviceDuration: Number,
  date: String,
  modelValue: String
})

const emit = defineEmits(['update:modelValue', 'select'])

const slots = ref([])
const loading = ref(false)
const selectedTime = ref(props.modelValue)

const fetchSlots = async () => {
  if (!props.masterId || !props.date) return
  
  try {
    loading.value = true
    const params = { date: props.date }
    if (props.serviceId) params.service_id = props.serviceId
    
    const response = await api.get(`/api/masters/${props.masterId}/available-slots/`, { params })
    slots.value = response.data
    
    // Sync selectedTime from modelValue after slots are loaded
    if (props.modelValue && props.modelValue.includes('T')) {
      const timePart = props.modelValue.split('T')[1].substring(0, 5)
      selectedTime.value = timePart
    }
  } catch (err) {
    console.error('Error fetching slots:', err)
    slots.value = []
  } finally {
    loading.value = false
  }
}

const selectSlot = (slot) => {
  if (!slot.is_available) {
    if (slot.status === 'lunch') {
      alert('Это время выпадает на обеденный перерыв мастера.')
    } else if (slot.status === 'busy') {
      alert('Это время уже занято другой записью.')
    }
    return
  }
  selectedTime.value = slot.time
  emit('update:modelValue', slot.start_iso)
  emit('select', slot)
}

watch(() => [props.masterId, props.serviceId, props.date], fetchSlots, { immediate: true })

watch(() => props.modelValue, (newVal) => {
    if (!newVal) {
      selectedTime.value = ''
    } else if (newVal.includes('T')) {
      selectedTime.value = newVal.split('T')[1].substring(0, 5)
    }
})
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  height: 4px;
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
