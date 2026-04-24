<template>
  <router-view></router-view>
</template>

<script setup>
</script>

<style>
/* App level transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
