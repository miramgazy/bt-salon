<template>
  <button
    @click="toggleDarkMode"
    class="relative h-7 w-12 rounded-full bg-stroke transition-colors duration-300 ease-in-out dark:bg-primary-dark"
    aria-label="Toggle Dark Mode"
  >
    <div
      class="absolute left-1 top-1 flex h-5 w-5 transform items-center justify-center rounded-full bg-white transition-transform duration-300 ease-in-out dark:translate-x-5"
    >
      <Icon
        v-if="!isDark"
        icon="mdi:white-balance-sunny"
        class="text-warning"
        width="14"
      />
      <Icon
        v-else
        icon="mdi:moon-waning-crescent"
        class="text-primary"
        width="14"
      />
    </div>
  </button>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Icon } from '@iconify/vue'

const isDark = ref(false)

const toggleDarkMode = () => {
  isDark.value = !isDark.value
  updateTheme()
}

const updateTheme = () => {
  if (isDark.value) {
    document.documentElement.classList.add('dark')
    localStorage.setItem('theme', 'dark')
  } else {
    document.documentElement.classList.remove('dark')
    localStorage.setItem('theme', 'light')
  }
}

onMounted(() => {
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme === 'dark' || (!savedTheme && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    isDark.value = true
  } else {
    isDark.value = false
  }
  updateTheme()
})
</script>
