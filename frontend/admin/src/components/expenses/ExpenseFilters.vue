<template>
  <div class="mb-5 rounded-sm border border-stroke bg-white p-4 shadow-default dark:border-strokedark dark:bg-bg-dark-2 md:p-5">
    <div class="flex flex-wrap items-end gap-3">
      <!-- Period -->
      <div class="w-full sm:w-auto">
        <label class="mb-1 block text-[10px] font-bold text-black dark:text-white uppercase tracking-wider">От</label>
        <input 
          type="date" 
          v-model="localFilters.date_from"
          class="w-full rounded border border-stroke bg-gray-50 py-1.5 px-3 text-sm outline-none focus:border-primary dark:border-strokedark dark:bg-meta-4 dark:text-white"
        />
      </div>
      <div class="w-full sm:w-auto">
        <label class="mb-1 block text-[10px] font-bold text-black dark:text-white uppercase tracking-wider">До</label>
        <input 
          type="date" 
          v-model="localFilters.date_to"
          class="w-full rounded border border-stroke bg-gray-50 py-1.5 px-3 text-sm outline-none focus:border-primary dark:border-strokedark dark:bg-meta-4 dark:text-white"
        />
      </div>

      <!-- Search -->
      <div class="w-full sm:w-64">
        <label class="mb-1 block text-[10px] font-bold text-black dark:text-white uppercase tracking-wider">Поиск</label>
        <input 
          type="text" 
          v-model="localFilters.search"
          placeholder="Название расхода..."
          class="w-full rounded border border-stroke bg-gray-50 py-1.5 px-3 text-sm outline-none focus:border-primary dark:border-strokedark dark:bg-meta-4 dark:text-white"
        />
      </div>

      <!-- Category Filter -->
      <div class="w-full sm:w-48">
        <label class="mb-1 block text-[10px] font-bold text-black dark:text-white uppercase tracking-wider">Статья</label>
        <select 
          v-model="localFilters.category_id"
          class="w-full rounded border border-stroke bg-gray-50 py-1.5 px-3 text-sm outline-none focus:border-primary dark:border-strokedark dark:bg-meta-4 dark:text-white"
        >
          <option value="">Все статьи</option>
          <option v-for="c in categories" :key="c?.id" :value="c?.id">
            {{ c?.name }}
          </option>
        </select>
      </div>

      <!-- Actions -->
      <div class="flex gap-2 ml-auto">
        <button 
          @click="reset"
          class="flex items-center justify-center rounded border border-stroke py-1.5 px-5 text-sm font-medium text-black hover:shadow-1 dark:border-strokedark dark:text-white"
        >
          Сбросить
        </button>
        <button 
          @click="apply"
          class="flex items-center justify-center rounded bg-primary py-1.5 px-5 text-sm font-medium text-white hover:bg-opacity-90 active:scale-95 transition-all"
        >
          Применить
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, watch } from 'vue'

const props = defineProps({
  filters: {
    type: Object,
    required: true
  },
  categories: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['apply', 'reset'])

const localFilters = reactive({ ...props.filters })

watch(() => props.filters, (newVal) => {
  Object.assign(localFilters, newVal)
}, { deep: true })

const apply = () => {
  emit('apply', { ...localFilters })
}

const reset = () => {
  emit('reset')
}
</script>
