<template>
  <header
    class="sticky top-0 z-40 flex w-full bg-white drop-shadow-1 dark:bg-bg-dark-2 dark:drop-shadow-none border-b border-stroke dark:border-strokedark"
  >
    <div class="flex flex-grow items-center justify-between px-4 py-4 md:px-6 2xl:px-11">
      <div class="flex items-center gap-2 sm:gap-4 lg:hidden">
        <!-- Hamburger Toggle BTN -->
        <button
          class="z-50 block rounded-sm border border-stroke bg-white p-1.5 shadow-sm dark:border-strokedark dark:bg-bg-dark-2 lg:hidden"
          @click.stop="emit('toggleSidebar')"
        >
          <Icon icon="mdi:menu" width="24" />
        </button>
      </div>

      <div class="hidden sm:block">
        <h2 class="text-sm font-medium text-body dark:text-bodydark uppercase tracking-widest">
          BT Salon Admin
        </h2>
      </div>

      <div class="flex items-center gap-3 2xsm:gap-7">
        <ul class="flex items-center gap-2 2xsm:gap-4">
          <!-- Dark Mode Switcher -->
          <DarkModeSwitcher />
        </ul>

        <!-- User Area -->
        <div class="relative flex items-center gap-4">
          <div class="hidden text-right lg:block">
            <p class="text-sm font-medium text-black dark:text-white">Администратор</p>
            <p class="text-xs font-medium text-body dark:text-bodydark">Master Role</p>
          </div>

          <div class="h-10 w-10 rounded-full bg-primary flex items-center justify-center text-white">
             <Icon icon="mdi:account" width="24" />
          </div>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { defineEmits } from 'vue'
import { Icon } from '@iconify/vue'
import DarkModeSwitcher from '../common/DarkModeSwitcher.vue'

const emit = defineEmits(['toggleSidebar'])

</script>
