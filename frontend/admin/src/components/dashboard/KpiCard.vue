<template>
  <div class="rounded-sm border border-stroke bg-white py-4 px-5 shadow-default dark:border-strokedark dark:bg-bg-dark-2">
    <div class="flex h-10 w-10 items-center justify-center rounded-full bg-meta-2 dark:bg-meta-4">
      <slot name="icon"></slot>
    </div>

    <div class="mt-3 flex items-end justify-between">
      <div>
        <h4 class="text-xl font-bold text-black dark:text-white">
          {{ value }}
        </h4>
        <span class="text-xs font-medium text-body">{{ label }}</span>
      </div>

      <span
        v-if="delta !== undefined"
        class="flex items-center gap-1 text-sm font-medium"
        :class="delta >= 0 ? 'text-meta-3' : 'text-danger'"
      >
        {{ delta >= 0 ? '+' : '' }}{{ delta }}%
        <Icon 
          :icon="delta >= 0 ? 'mdi:arrow-up' : 'mdi:arrow-down'" 
          :class="delta >= 0 ? 'fill-meta-3' : 'fill-danger'" 
        />
      </span>
    </div>

    <!-- Footer Slot -->
    <div v-if="$slots.footer" class="mt-4 pt-3 border-t border-stroke dark:border-strokedark">
       <slot name="footer"></slot>
    </div>
  </div>
</template>

<script setup>
import { Icon } from '@iconify/vue'

defineProps({
  label: String,
  value: [String, Number],
  delta: Number
})
</script>
