<template>
  <div class="master-layout-wrapper" :style="cssVars">
    <!-- Master Header -->
    <div class="header">
      <div class="header-top">
        <div>
          <div class="header-greeting">Управление (Мастер)</div>
          <div class="header-name header-font">{{ authStore.organizationName }}</div>
        </div>
        <div class="header-actions">
           <button class="icon-btn lang-btn" @click="toggleLang" style="margin-right: 8px">
             {{ locale === 'ru' ? 'ҚЗ' : 'РУ' }}
           </button>
           <div class="master-badge">
             <Icon icon="mdi:shield-check" width="14" />
             STAFF
           </div>
        </div>
      </div>
    </div>

    <router-view class="main-content"></router-view>
    
    <nav class="bottom-nav">
      <router-link to="/master" exact class="nav-item">
        <Icon icon="mdi:view-dashboard-outline" width="24" :class="{'active-icon': $route.path === '/master'}" />
        <span>Главная</span>
      </router-link>

      <router-link to="/master/bookings" class="nav-item">
        <Icon icon="mdi:calendar-check-outline" width="24" :class="{'active-icon': $route.path === '/master/bookings'}" />
        <span>Записи</span>
      </router-link>

      <router-link to="/master/income" class="nav-item">
        <Icon icon="mdi:wallet-outline" width="24" :class="{'active-icon': $route.path === '/master/income'}" />
        <span>Доход</span>
      </router-link>
      
      <router-link to="/master/profile" class="nav-item">
        <Icon icon="mdi:account-circle-outline" width="24" :class="{'active-icon': $route.path === '/master/profile'}" />
        <span>Профиль</span>
      </router-link>

      <button @click="exitApp" class="nav-item border-none bg-transparent cursor-pointer">
        <Icon icon="mdi:exit-to-app" width="24" />
        <span>Выход</span>
      </button>
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
    '--gold': color
  }
})

const exitApp = () => {
  if (window.Telegram?.WebApp) {
    window.Telegram.WebApp.close()
  } else {
    alert("This action works inside Telegram")
  }
}
</script>

<style scoped>
.master-layout-wrapper {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background: var(--tg-bg);
  padding: calc(var(--tg-safe-top, 0px) + 16px) 16px 12px;
  border-bottom: 1px solid var(--border);
  position: sticky; 
  top: 0; 
  z-index: 100;
  transition: padding-top 0.3s ease;
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

.master-badge {
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
