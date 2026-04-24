<template>
  <aside
    class="absolute left-0 top-0 z-50 flex h-screen w-72.5 flex-col overflow-y-hidden bg-main duration-300 ease-linear dark:bg-bg-dark-2 lg:static lg:translate-x-0"
    :class="{ 'translate-x-0': sidebarOpen, '-translate-x-full': !sidebarOpen }"
  >
    <!-- SIDEBAR HEADER -->
    <div class="flex items-center justify-between gap-2 px-6 py-5.5 lg:py-6.5">
      <router-link to="/" class="flex items-center gap-3">
        <Icon icon="mdi:content-cut" class="text-primary" width="32" />
        <h1 class="text-2xl font-bold text-white uppercase tracking-tight">BT Salon</h1>
      </router-link>

      <button
        class="block lg:hidden text-white"
        @click.stop="emit('toggleSidebar')"
      >
        <Icon icon="mdi:arrow-left" width="24" />
      </button>
    </div>
    <!-- SIDEBAR HEADER -->

    <div class="no-scrollbar flex flex-col overflow-y-auto duration-300 ease-linear">
      <!-- Sidebar Menu -->
      <nav class="mt-5 py-4 px-4 lg:mt-9 lg:px-6">
        <!-- ОСНОВНОЕ -->
        <div class="mb-6">
          <h3 class="mb-4 ml-4 text-sm font-medium text-bodydark2 text-opacity-70 uppercase tracking-widest">Основное</h3>

          <ul class="flex flex-col gap-1.5">
            <li>
              <router-link
                to="/admin"
                class="group relative flex items-center gap-2.5 rounded-sm py-2 px-4 font-medium text-bodydark1 duration-300 ease-in-out hover:bg-bg-dark dark:hover:bg-meta-4"
                active-class="bg-bg-dark dark:bg-meta-4"
              >
                <Icon icon="mdi:view-dashboard" width="22" />
                Дашборд
              </router-link>
            </li>

            <li>
              <router-link
                to="/admin/calendar"
                class="group relative flex items-center gap-2.5 rounded-sm py-2 px-4 font-medium text-bodydark1 duration-300 ease-in-out hover:bg-bg-dark dark:hover:bg-meta-4"
                active-class="bg-bg-dark dark:bg-meta-4"
              >
                <Icon icon="mdi:calendar-month" width="22" />
                Календарь
              </router-link>
            </li>

            <li>
              <router-link
                to="/admin/appointments"
                class="group relative flex items-center gap-2.5 rounded-sm py-2 px-4 font-medium text-bodydark1 duration-300 ease-in-out hover:bg-bg-dark dark:hover:bg-meta-4"
                active-class="bg-bg-dark dark:bg-meta-4"
              >
                <Icon icon="mdi:format-list-bulleted" width="22" />
                Все записи
              </router-link>
            </li>
            
            <li>
              <router-link
                to="/admin/clients"
                class="group relative flex items-center gap-2.5 rounded-sm py-2 px-4 font-medium text-bodydark1 duration-300 ease-in-out hover:bg-bg-dark dark:hover:bg-meta-4"
                active-class="bg-bg-dark dark:bg-meta-4"
              >
                <Icon icon="mdi:account-group-outline" width="22" />
                Клиенты
              </router-link>
            </li>
          </ul>
        </div>

        <!-- САЛОН -->
        <div class="mb-6">
          <h3 class="mb-4 ml-4 text-sm font-medium text-bodydark2 text-opacity-70 uppercase tracking-widest">Салон</h3>

          <ul class="flex flex-col gap-1.5">
            <li>
              <router-link
                to="/admin/shifts"
                class="group relative flex items-center gap-2.5 rounded-sm py-2 px-4 font-medium text-bodydark1 duration-300 ease-in-out hover:bg-bg-dark dark:hover:bg-meta-4"
                active-class="bg-bg-dark dark:bg-meta-4"
              >
                <Icon icon="mdi:clock-time-four-outline" width="22" />
                Смены
              </router-link>
            </li>
            <li>
              <router-link
                to="/admin/expenses"
                class="group relative flex items-center gap-2.5 rounded-sm py-2 px-4 font-medium text-bodydark1 duration-300 ease-in-out hover:bg-bg-dark dark:hover:bg-meta-4"
                active-class="bg-bg-dark dark:bg-meta-4"
              >
                <Icon icon="mdi:cash-multiple" width="22" />
                Расходы
              </router-link>
            </li>
          </ul>
        </div>

        <!-- НАСТРОЙКИ -->
        <div>
          <h3 class="mb-4 ml-4 text-sm font-medium text-bodydark2 text-opacity-70 uppercase tracking-widest">Настройки</h3>

          <ul class="flex flex-col gap-1.5">
            <li>
              <router-link
                to="/superadmin/services"
                class="group relative flex items-center gap-2.5 rounded-sm py-2 px-4 font-medium text-bodydark1 duration-300 ease-in-out hover:bg-bg-dark dark:hover:bg-meta-4"
                active-class="bg-bg-dark dark:bg-meta-4"
              >
                <Icon icon="mdi:face-woman" width="22" />
                Услуги
              </router-link>
            </li>

            <li>
              <router-link
                to="/superadmin/masters"
                class="group relative flex items-center gap-2.5 rounded-sm py-2 px-4 font-medium text-bodydark1 duration-300 ease-in-out hover:bg-bg-dark dark:hover:bg-meta-4"
                active-class="bg-bg-dark dark:bg-meta-4"
              >
                <Icon icon="mdi:account-tie" width="22" />
                Мастера
              </router-link>
            </li>

            <li>
              <router-link
                to="/superadmin/organization"
                class="group relative flex items-center gap-2.5 rounded-sm py-2 px-4 font-medium text-bodydark1 duration-300 ease-in-out hover:bg-bg-dark dark:hover:bg-meta-4"
                active-class="bg-bg-dark dark:bg-meta-4"
              >
                <Icon icon="mdi:domain" width="22" />
                Организация
              </router-link>
            </li>
          </ul>
        </div>
      </nav>
      <!-- Sidebar Menu -->
      
      <div class="mt-auto px-6 py-10">
         <button 
           @click="logout"
           class="flex items-center gap-2.5 px-4 py-2 font-medium text-danger hover:bg-danger/10 rounded-sm w-full transition-colors"
         >
           <Icon icon="mdi:logout" width="22" />
           Выйти
         </button>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'
import { useRouter } from 'vue-router'
import { Icon } from '@iconify/vue'

const props = defineProps({
  sidebarOpen: Boolean
})

const emit = defineEmits(['toggleSidebar'])
const router = useRouter()

const logout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  router.push('/login')
}
</script>

<style scoped>
.w-72.5 {
  width: 18.125rem;
}
.py-5.5 {
  padding-top: 1.375rem;
  padding-bottom: 1.375rem;
}
.no-scrollbar::-webkit-scrollbar {
  display: none;
}
</style>
