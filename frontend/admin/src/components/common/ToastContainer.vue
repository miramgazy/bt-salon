<template>
  <div class="fixed top-4 right-4 z-[99999] flex flex-col gap-3 pointer-events-none">
    <TransitionGroup name="toast">
      <div
        v-for="toast in toasts"
        :key="toast.id"
        class="pointer-events-auto min-w-[280px] max-w-md rounded-lg border p-4 shadow-xl flex items-start gap-3 backdrop-blur-sm transition-all"
        :class="{
          'bg-success/90 border-success/30 text-white': toast.type === 'success',
          'bg-danger/90 border-danger/30 text-white': toast.type === 'error',
          'bg-warning/90 border-warning/30 text-white': toast.type === 'warning',
          'bg-white/90 border-stroke text-black dark:bg-meta-4/90 dark:border-strokedark dark:text-white': toast.type === 'info'
        }"
      >
        <div class="shrink-0 mt-0.5">
          <Icon v-if="toast.type === 'success'" icon="mdi:check-circle" width="20" />
          <Icon v-else-if="toast.type === 'error'" icon="mdi:alert-circle" width="20" />
          <Icon v-else-if="toast.type === 'warning'" icon="mdi:alert" width="20" />
          <Icon v-else icon="mdi:information" width="20" />
        </div>
        
        <div class="flex-1 text-sm font-medium">
          {{ toast.message }}
        </div>

        <button @click="remove(toast.id)" class="shrink-0 opacity-70 hover:opacity-100 transition-opacity">
          <Icon icon="mdi:close" width="18" />
        </button>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup lang="ts">
import { Icon } from '@iconify/vue'
import { useToast } from '../../composables/useToast'

const { toasts, remove } = useToast()
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
.toast-enter-from {
  opacity: 0;
  transform: translateX(50px) scale(0.9);
}
.toast-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
</style>
