<template>
  <div class="mb-5 rounded-sm border border-stroke bg-white p-4 shadow-sm dark:border-strokedark dark:bg-bg-dark-2 md:p-5">
    <div class="flex flex-wrap items-end gap-3">
      <!-- Date From -->
      <div class="w-full sm:w-auto">
        <label class="mb-1 block text-[10px] font-bold text-black dark:text-white uppercase tracking-wider">От</label>
        <input 
          type="date" 
          v-model="localFilters.date_from"
          class="w-full rounded border border-stroke bg-gray-50 py-1.5 px-3 text-sm outline-none focus:border-primary dark:border-strokedark dark:bg-meta-4 dark:text-white"
        />
      </div>
 
      <!-- Date To -->
      <div class="w-full sm:w-auto">
        <label class="mb-1 block text-[10px] font-bold text-black dark:text-white uppercase tracking-wider">До</label>
        <input 
          type="date" 
          v-model="localFilters.date_to"
          class="w-full rounded border border-stroke bg-gray-50 py-1.5 px-3 text-sm outline-none focus:border-primary dark:border-strokedark dark:bg-meta-4 dark:text-white"
        />
      </div>
 
      <!-- Masters Multi-select -->
      <div class="w-full sm:w-64 relative" v-click-outside="closeDropdown">
        <label class="mb-1 block text-[10px] font-bold text-black dark:text-white uppercase tracking-wider">Мастера</label>
        
        <!-- Dropdown Trigger -->
        <button 
          @click="toggleDropdown"
          type="button"
          class="flex w-full items-center justify-between rounded border border-stroke bg-gray-50 py-1.5 px-3 text-sm outline-none focus:border-primary dark:border-strokedark dark:bg-meta-4 dark:text-white group"
        >
          <span class="truncate pr-2">
            {{ selectedMastersLabel }}
          </span>
          <Icon 
            icon="mdi:chevron-down" 
            class="transition-transform duration-200" 
            :class="{ 'rotate-180': isDropdownOpen }"
            width="18" 
          />
        </button>
 
        <!-- Dropdown Menu -->
        <div 
          v-if="isDropdownOpen" 
          class="absolute left-0 mt-1 z-50 w-full rounded border border-stroke bg-white shadow-lg dark:border-strokedark dark:bg-bg-dark-2 max-h-60 overflow-y-auto custom-scrollbar"
        >
          <!-- Select All Option -->
          <label class="flex items-center gap-3 px-3 py-2 cursor-pointer hover:bg-gray-100 dark:hover:bg-meta-4 transition-colors border-b border-stroke dark:border-strokedark">
            <input 
              type="checkbox" 
              :checked="isAllSelected" 
              @change="toggleAll"
              class="h-4 w-4 rounded border-stroke text-primary focus:ring-primary accent-primary" 
            />
            <span class="text-sm font-bold text-black dark:text-white uppercase tracking-wider">Все мастера</span>
          </label>
          
          <!-- Individual Masters -->
          <div class="py-1">
            <label 
              v-for="m in masters" 
              :key="m.id"
              class="flex items-center gap-3 px-3 py-2 cursor-pointer hover:bg-gray-100 dark:hover:bg-meta-4 transition-colors"
            >
              <input 
                type="checkbox" 
                :value="m.id.toString()"
                v-model="localFilters.master_ids"
                class="h-4 w-4 rounded border-stroke text-primary focus:ring-primary accent-primary" 
              />
              <span class="text-sm text-black dark:text-white">{{ m.name }}</span>
            </label>
          </div>
        </div>
      </div>
 
      <!-- Apply Button -->
      <div class="flex gap-2 ml-auto">
        <button 
          @click="reset"
          class="flex items-center justify-center rounded border border-stroke py-1.5 px-5 text-sm font-medium text-black hover:shadow-1 dark:border-strokedark dark:text-white"
        >
          Сбросить
        </button>
        <button 
          @click="apply"
          class="flex items-center justify-center rounded bg-primary py-1.5 px-5 text-sm font-medium text-white hover:bg-opacity-90 active:scale-95 transition-all shadow-sm"
        >
          Применить
        </button>
      </div>
    </div>
  </div>
</template>
 
<script setup>
import { ref, reactive, watch, computed, onMounted, onUnmounted } from 'vue'
import { Icon } from '@iconify/vue'
 
const props = defineProps({
  filters: Object,
  masters: Array,
  services: Array
})
 
const emit = defineEmits(['apply', 'reset'])
 
const localFilters = reactive({
  date_from: props.filters.date_from,
  date_to: props.filters.date_to,
  master_ids: Array.isArray(props.filters.master_ids) ? [...props.filters.master_ids] : [],
  service_ids: Array.isArray(props.filters.service_ids) ? [...props.filters.service_ids] : []
})
 
const isDropdownOpen = ref(false)
 
// Selection Logic
const isAllSelected = computed(() => {
  if (!props.masters?.length) return false
  return localFilters.master_ids.length === props.masters.length || localFilters.master_ids.length === 0
})
 
const selectedMastersLabel = computed(() => {
  if (localFilters.master_ids.length === 0 || localFilters.master_ids.length === props.masters?.length) {
    return 'Все мастера'
  }
  
  if (localFilters.master_ids.length <= 2) {
    return props.masters
      .filter(m => localFilters.master_ids.includes(m.id.toString()))
      .map(m => m.name)
      .join(', ')
  }
  
  return `Выбрано: ${localFilters.master_ids.length}`
})
 
const toggleDropdown = () => {
  isDropdownOpen.value = !isDropdownOpen.value
}
 
const closeDropdown = () => {
  isDropdownOpen.value = false
}
 
const toggleAll = () => {
  if (localFilters.master_ids.length === props.masters.length) {
    localFilters.master_ids = []
  } else {
    localFilters.master_ids = props.masters.map(m => m.id.toString())
  }
}
 
// Click outside handling
const vClickOutside = {
  mounted(el, binding) {
    el.clickOutsideEvent = (event) => {
      if (!(el === event.target || el.contains(event.target))) {
        binding.value()
      }
    }
    document.addEventListener('click', el.clickOutsideEvent)
  },
  unmounted(el) {
    document.removeEventListener('click', el.clickOutsideEvent)
  }
}
 
// Sync local state if props change (e.g. from URL)
watch(() => props.filters, (newVal) => {
  localFilters.date_from = newVal.date_from
  localFilters.date_to = newVal.date_to
  localFilters.master_ids = Array.isArray(newVal.master_ids) ? [...newVal.master_ids] : []
  localFilters.service_ids = Array.isArray(newVal.service_ids) ? [...newVal.service_ids] : []
}, { deep: true })
 
const apply = () => {
  // If "All" is logically selected, we can send empty array to backend
  // because backend handles empty as "all".
  const finalFilters = { ...localFilters }
  if (localFilters.master_ids.length === props.masters?.length) {
    finalFilters.master_ids = []
  }
  emit('apply', finalFilters)
  isDropdownOpen.value = false
}
 
const reset = () => {
  emit('reset')
  isDropdownOpen.value = false
}
</script>
 
<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #E2E8F0;
  border-radius: 10px;
}
.dark .custom-scrollbar::-webkit-scrollbar-thumb {
  background: #2E3A47;
}
</style>
