<template>
  <div class="tma-layout">
    <!-- Header shared entirely? Or per page? tma-booking has header on the app level -->
    <div class="header">
      <div class="header-top">
        <div class="header-brand">
          <div v-if="auth.organizationSettings?.logo_url" class="header-logo">
            <img :src="auth.organizationSettings.logo_url" alt="logo" />
          </div>
          <div>
            <div class="header-greeting">{{ auth.organizationSettings?.greeting_text || 'Добро пожаловать!' }}</div>
            <div class="header-name header-font">{{ auth.organizationName || 'Beauty Salon' }}</div>
          </div>
        </div>
        <div class="header-actions">
          <button class="icon-btn lang-btn" @click="toggleLang">
            {{ locale === 'ru' ? 'ҚЗ' : 'РУ' }}
          </button>
          <button v-if="auth.organizationSettings?.instagram_link" class="icon-btn" @click="openLink(auth.organizationSettings.instagram_link)">
            <Icon icon="mdi:instagram" width="18" />
          </button>
          <button v-if="auth.organizationSettings?.whatsapp_number" class="icon-btn" @click="openWhatsApp">
            <Icon icon="mdi:whatsapp" width="18" />
          </button>
        </div>
      </div>
    </div>
    
    <router-view class="main-content"></router-view>
    
    <nav class="bottom-nav">
      <router-link to="/" class="nav-item">
        <Icon icon="mdi:home-outline" width="24" :class="{'active-icon': $route.path === '/'}" />
        <span>{{ $t('nav.home', 'Главная') }}</span>
      </router-link>
      
      <router-link to="/tma-appointments" class="nav-item">
        <Icon icon="mdi:calendar-clock-outline" width="24" :class="{'active-icon': $route.path === '/tma-appointments'}" />
        <span>{{ $t('nav.bookings', 'Записи') }}</span>
      </router-link>

      <router-link to="/profile" class="nav-item">
        <Icon icon="mdi:account-outline" width="24" :class="{'active-icon': $route.path === '/profile'}" />
        <span>{{ $t('nav.profile', 'Профиль') }}</span>
      </router-link>
      
      <button @click="exitApp" class="nav-item border-none bg-transparent cursor-pointer">
        <Icon icon="mdi:exit-to-app" width="24" />
        <span>{{ $t('nav.exit', 'Выход') }}</span>
      </button>
    </nav>
  </div>
</template>

<script setup>
import { useAuthStore } from '../../stores/auth'
import { Icon } from '@iconify/vue'
import { useI18n } from 'vue-i18n'

const auth = useAuthStore()
const { t, locale } = useI18n()

const toggleLang = () => {
  locale.value = locale.value === 'ru' ? 'kz' : 'ru'
  // Persist language via store/API if needed
}

const openLink = (url) => {
  if (!url) return
  if (window.Telegram?.WebApp) {
    window.Telegram.WebApp.openLink(url)
  } else {
    window.open(url, '_blank')
  }
}

const openWhatsApp = () => {
  const num = auth.organizationSettings?.whatsapp_number
  if (num) {
    const cleanNum = num.replace(/\D/g, '')
    openLink(`https://wa.me/${cleanNum}`)
  }
}

const exitApp = () => {
  if (window.Telegram?.WebApp) {
    window.Telegram.WebApp.close()
  } else {
    alert("This action works inside Telegram")
  }
}
</script>

<style scoped>
.tma-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background: var(--tg-bg);
  padding: calc(var(--tg-safe-top, 0px) + 12px) 16px;
  border-bottom: 1px solid var(--border);
  position: sticky; 
  top: 0; 
  z-index: 100;
  transition: padding-top 0.3s ease;
}

.header-top { display: flex; justify-content: space-between; align-items: center; }
.header-brand { display: flex; align-items: center; gap: 14px; }
.header-logo {
  width: 80px;
  height: 80px;
  border-radius: 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
.header-logo img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  padding: 6px;
}
.header-greeting { font-size: 12px; color: var(--gold); text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px; opacity: 0.9; margin-bottom: 2px; }
.header-name { font-size: 22px; font-weight: 800; color: var(--text); line-height: 1.1; }

.icon-btn {
  width: 36px; height: 36px; border-radius: 50%; background: var(--bg-secondary);
  border: none; cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: all .2s; color: var(--text);
}
.icon-btn:active { background: var(--gold-accent); color: var(--gold); }

.main-content {
  flex: 1;
  overflow-y: auto;
}

.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
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
  color: var(--text-hint);
  text-decoration: none;
  font-size: 10px;
  gap: 3px;
  flex: 1;
}

.nav-item span { font-weight: 500; }
.nav-item.router-link-active { color: var(--gold); }
.nav-item:active { opacity: 0.7; }
</style>
