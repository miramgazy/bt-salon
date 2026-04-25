<template>
  <div class="admin-layout-wrapper" :style="cssVars">
    <!-- Admin Header -->
    <div class="header">
      <div class="header-top">
        <div>
          <div class="header-greeting">Управление (Админ)</div>
          <div class="header-name header-font">{{ authStore.organizationName || 'Организация' }}</div>
        </div>
        <div class="header-actions">
           <button class="icon-btn lang-btn" @click="toggleLang" style="margin-right: 8px">
             {{ locale === 'ru' ? 'ҚЗ' : 'РУ' }}
           </button>
           <div class="admin-badge">
             <Icon icon="mdi:shield-crown" width="14" />
             ADMIN
           </div>
        </div>
      </div>
    </div>

    <router-view class="main-content"></router-view>
    
    <nav class="bottom-nav">
      <router-link to="/admin/bookings" class="nav-item" active-class="router-link-active">
        <Icon icon="mdi:calendar-multiple-check" width="24" :class="{'active-icon': $route.path.includes('/admin/bookings')}" />
        <span>Записи</span>
      </router-link>

      <router-link to="/admin/services" class="nav-item" active-class="router-link-active">
        <Icon icon="mdi:format-list-bulleted" width="24" :class="{'active-icon': $route.path.includes('/admin/services')}" />
        <span>Услуги</span>
      </router-link>
      
      <router-link to="/admin/masters" class="nav-item" active-class="router-link-active">
        <Icon icon="mdi:account-tie" width="24" :class="{'active-icon': $route.path.includes('/admin/masters')}" />
        <span>Сотрудники</span>
      </router-link>

      <router-link to="/admin/report" class="nav-item" active-class="router-link-active">
        <Icon icon="mdi:chart-bar" width="24" :class="{'active-icon': $route.path.includes('/admin/report')}" />
        <span>Отчеты</span>
      </router-link>

      <router-link to="/admin/profile" class="nav-item" active-class="router-link-active">
        <Icon icon="mdi:account-circle" width="24" :class="{'active-icon': $route.path.includes('/admin/profile')}" />
        <span>Профиль</span>
      </router-link>
    </nav>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Icon } from '@iconify/vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()
const { locale } = useI18n()

const toggleLang = () => {
  locale.value = locale.value === 'ru' ? 'kz' : 'ru'
  localStorage.setItem('tma_locale', locale.value)
}

const cssVars = computed(() => {
  const settings = authStore.organizationSettings || {}
  const color = settings.design_color || '#c9a84c'
  return {
    '--gold': color,
    '--gold-accent': color + '22',
    '--gold-glow': color + '15'
  }
})

const exitApp = () => {
  if (window.Telegram?.WebApp) {
    window.Telegram.WebApp.close()
  } else {
    authStore.logout()
    router.push('/')
  }
}
</script>

<style scoped>
.admin-layout-wrapper {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background: var(--tg-bg);
  padding: 16px 16px 12px;
  border-bottom: 1px solid var(--border);
  position: sticky; 
  top: 0; 
  z-index: 100;
}
.header-top { display: flex; justify-content: space-between; align-items: center; }
.header-greeting { font-size: 11px; color: var(--gold); text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px; }
.header-name { font-size: 20px; font-weight: 700; color: var(--text); line-height: 1.2; }

.header-actions { display: flex; align-items: center; }
.lang-btn {
  width: 36px; height: 36px; border-radius: 50%; background: var(--bg-secondary);
  border: none; cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: all .2s; color: var(--text); font-size: 11px; font-weight: 700;
}
.lang-btn:active { background: var(--gold-accent); color: var(--gold); }

.admin-badge {
  background: var(--gold-glow);
  color: var(--gold);
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 10px;
  font-weight: 800;
  display: flex;
  align-items: center;
  gap: 4px;
  border: 1px solid var(--gold);
}

.main-content {
  flex: 1;
  overflow-y: auto;
  background-color: var(--bg-secondary);
}

.bottom-nav {
  position: fixed;
  bottom: 0; left: 0; right: 0;
  height: calc(60px + env(safe-area-inset-bottom));
  background-color: var(--tg-bg);
  display: flex;
  justify-content: space-around;
  align-items: center;
  padding-bottom: env(safe-area-inset-bottom);
  border-top: 1px solid var(--border);
  backdrop-filter: blur(10px);
  z-index: 100;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: var(--muted);
  text-decoration: none;
  font-size: 10px;
  gap: 3px;
  flex: 1;
}
.nav-item.router-link-active {
  color: var(--gold);
}
.active-icon {
  color: var(--gold);
}
</style>
