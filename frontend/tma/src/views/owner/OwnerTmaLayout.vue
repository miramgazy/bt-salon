<template>
  <div class="owner-layout-wrapper" :style="cssVars">
    <!-- Header matching Admin style -->
    <div class="header">
      <div class="header-top">
        <div>
          <div class="header-greeting">Управление (Владелец)</div>
          <div class="header-name header-font">{{ authStore.organizationName || 'Организация' }}</div>
        </div>
        <div class="header-actions">
           <button class="icon-btn lang-btn" @click="toggleLang" style="margin-right: 8px">
             {{ locale === 'ru' ? 'ҚЗ' : 'РУ' }}
           </button>
           <div class="owner-badge">
             <Icon icon="mdi:shield-account" width="14" />
             OWNER
           </div>
        </div>
      </div>
    </div>

    <!-- Scrollable content -->
    <div class="main-content">
      <router-view></router-view>
    </div>
    
    <!-- Unique 2-row Bottom Nav -->
    <nav :class="['bottom-nav', { 'expanded': isExpanded }]">
      <div class="nav-container">
        <!-- Row Toggle (Left) -->
        <button class="nav-control left" @click="isExpanded = !isExpanded">
          <Icon :icon="isExpanded ? 'mdi:chevron-down' : 'mdi:chevron-up'" width="26" />
        </button>

        <!-- Nav Items Area -->
        <div class="nav-items-grid">
          <!-- Row 1 (Always Visible or Primary) -->
          <div class="nav-row row-primary" :class="{ 'hidden': isExpanded }">
            <div class="nav-item-btn" @click="setTab('overview')" :class="{ active: activeTab === 'overview' }">
              <Icon icon="mdi:view-dashboard" width="22" />
              <span>Главная</span>
            </div>
            <div class="nav-item-btn" @click="setTab('masters')" :class="{ active: activeTab === 'masters' }">
              <Icon icon="mdi:account-tie" width="22" />
              <span>Мастера</span>
            </div>
            <div class="nav-item-btn" @click="setTab('services')" :class="{ active: activeTab === 'services' }">
              <Icon icon="mdi:format-list-bulleted" width="22" />
              <span>Услуги</span>
            </div>
          </div>

          <!-- Row 2 (Revealed) -->
          <div class="nav-row row-secondary" :class="{ 'active': isExpanded }">
            <div class="nav-item-btn" @click="setTab('expenses')" :class="{ active: activeTab === 'expenses' }">
              <Icon icon="mdi:cash-multiple" width="22" />
              <span>Расходы</span>
            </div>
            <div class="nav-item-btn" @click="setTab('compare')" :class="{ active: activeTab === 'compare' }">
              <Icon icon="mdi:compare-horizontal" width="22" />
              <span>Сравнение</span>
            </div>
            <div class="nav-item-btn placeholder"></div>
          </div>
        </div>

        <!-- Profile Button (Right - Always Fixed) -->
        <button @click="setTab('profile')" class="nav-control right" :class="{ active: activeTab === 'profile' }">
          <Icon icon="mdi:account-circle" width="24" />
          <span>Профиль</span>
        </button>
      </div>
    </nav>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Icon } from '@iconify/vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()
const { locale } = useI18n()

const isExpanded = ref(false)
const activeTab = ref('overview')

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
    '--gold-glow': color + '15',
    '--border': 'var(--tg-theme-secondary-bg-color, #f0ece0)',
  }
})

const setTab = (tabId) => {
  activeTab.value = tabId
  if (tabId === 'profile') {
    router.push('/owner/profile')
  } else {
    router.push({ path: '/owner', query: { tab: tabId } })
  }
  if (isExpanded.value) isExpanded.value = false
}

const exitApp = () => {
  if (window.Telegram?.WebApp) {
    window.Telegram.WebApp.close()
  } else {
    authStore.logout()
    router.push('/')
  }
}

onMounted(() => {
    if (route.query.tab) {
        activeTab.value = route.query.tab
    }
})
</script>

<style scoped>
.owner-layout-wrapper {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: var(--tg-theme-secondary-bg-color, #f7f5f0);
}

.header {
  background: var(--tg-theme-bg-color, #fff);
  padding: calc(var(--tg-safe-top, 0px) + 16px) 16px 12px;
  border-bottom: 1px solid var(--border);
  z-index: 100;
  transition: padding-top 0.3s ease;
}
.header-top { display: flex; justify-content: space-between; align-items: center; }
.header-greeting { font-size: 11px; color: var(--gold); text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px; }
.header-name { font-size: 20px; font-weight: 700; color: var(--tg-theme-text-color, #000); line-height: 1.2; }

.header-actions { display: flex; align-items: center; }
.lang-btn {
  width: 36px; height: 36px; border-radius: 50%; background: var(--tg-theme-secondary-bg-color, #f0f0f0);
  border: none; cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: all .2s; color: var(--tg-theme-text-color, #000); font-size: 11px; font-weight: 700;
}

.owner-badge {
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
  padding-bottom: 80px;
}

/* Bottom Nav Logic */
.bottom-nav {
  position: fixed;
  bottom: 0; left: 0; right: 0;
  background-color: var(--tg-theme-bg-color, #fff);
  border-top: 1px solid var(--border);
  backdrop-filter: blur(10px);
  z-index: 1000;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  height: calc(65px + env(safe-area-inset-bottom));
}

.bottom-nav.expanded {
  height: calc(120px + env(safe-area-inset-bottom));
}

.nav-container {
  display: flex;
  height: 100%;
  align-items: flex-end;
  padding-bottom: env(safe-area-inset-bottom);
  position: relative;
}

.nav-control {
  width: 60px;
  height: 65px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  color: var(--tg-theme-hint-color, #999);
  cursor: pointer;
  z-index: 10;
}

.nav-control span { font-size: 10px; margin-top: 2px; }
.nav-control.right { color: var(--tg-theme-destructive-text-color, #ff3b30); }

.nav-items-grid {
  flex: 1;
  height: 100%;
  position: relative;
  overflow: hidden;
}

.nav-row {
  display: flex;
  justify-content: space-around;
  align-items: center;
  position: absolute;
  left: 0; right: 0;
  height: 65px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.row-primary { bottom: 0; }
.row-primary.hidden { transform: translateY(100%); opacity: 0; }

.row-secondary { bottom: 0; transform: translateY(100%); opacity: 0; }
.row-secondary.active { transform: translateY(0); opacity: 1; }

.nav-item-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: var(--tg-theme-hint-color, #999);
  text-decoration: none;
  font-size: 10px;
  gap: 3px;
  flex: 1;
  transition: color 0.2s;
  height: 65px;
  justify-content: center;
}

.nav-item-btn.active {
  color: var(--gold);
}

.nav-item-btn.placeholder { pointer-events: none; }
</style>
