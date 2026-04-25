<script setup>
import { onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'
import { getStoredLocale } from './i18n/index'
import { useI18n } from 'vue-i18n'

const auth = useAuthStore()
const router = useRouter()
const { locale } = useI18n()

/**
 * After successful login, determine where to redirect the user:
 */
function navigateAfterAuth() {
  // 1. Mandatory Onboarding Checks
  if (!auth.isOnboarded) {
    router.replace('/onboarding/welcome')
    return
  }
  if (auth.needsConsent) {
    router.replace('/onboarding/consent')
    return
  }

  // 2. Explicit User Mode Choice (activeRole)
  // If the user already explicitly switched to a mode (e.g., switched to Client mode while being an Owner), respect it.
  if (auth.activeRole) {
    if (auth.activeRole === 'admin' && auth.isAdmin) {
      router.replace('/admin')
      return
    }
    if (auth.activeRole === 'owner' && auth.isOwner) {
      router.replace('/owner')
      return
    }
    if (auth.activeRole === 'master' && auth.isMaster) {
      router.replace('/master')
      return
    }
    if (auth.activeRole === 'client') {
      router.replace('/')
      return
    }
  }

  // 3. Auto-Detection by Physical Role
  // If it's the first time or no preference, send to management panel immediately if they are staff.
  if (auth.role === 'admin') {
    router.replace('/admin')
    return
  }
  if (auth.role === 'owner') {
    router.replace('/owner')
    return
  }
  if (auth.role === 'master') {
    router.replace('/master')
    return
  }

  // 4. Default to Client
  router.replace('/')
}

const applyThemeFromBot = () => {
  const root = document.documentElement
  if (window.Telegram && window.Telegram.WebApp) {
    const webApp = window.Telegram.WebApp
    
    // Set Header and Background colors to match theme
    webApp.setHeaderColor(webApp.themeParams.header_bg_color || 'bg_color')
    webApp.setBackgroundColor(webApp.themeParams.bg_color || 'bg_color')

    if (auth.organizationSettings?.design_color) {
      root.style.setProperty('--gold', auth.organizationSettings.design_color)
    }
  }
}

watch(() => auth.organizationSettings, applyThemeFromBot, { deep: true })

const initTma = async () => {
  const storedLocale = getStoredLocale()
  if (storedLocale) locale.value = storedLocale

  if (window.Telegram && window.Telegram.WebApp) {
    const webApp = window.Telegram.WebApp
    webApp.ready()
    webApp.expand()

    const initData = webApp.initData
    const organizationId = webApp.initDataUnsafe?.start_param || null

    if (initData) {
      const ok = await auth.login(initData, organizationId)
      if (ok) {
        applyThemeFromBot()
        await navigateAfterAuth() // Wait for redirect to be triggered
      }
      auth.loading = false // Only now stop loading
    } else {
      auth.loading = false
    }
  } else {
    auth.restoreAuth()
    if (auth.isAuthenticated) {
      await auth.fetchCurrentUser()
      applyThemeFromBot()
      await navigateAfterAuth()
    } else {
      router.replace('/onboarding/welcome')
    }
    auth.loading = false
  }
}

onMounted(() => {
  initTma()
})
</script>

<template>
  <div class="tma-container">
    <div v-if="auth.loading" class="loading-overlay">
      <div class="spinner"></div>
      <div style="margin-top: 16px; color: var(--muted); font-size: 13px;">{{ $t('common.loading') }}...</div>
    </div>
    <div v-else-if="auth.error" class="error-banner">
      <div class="card glass" style="border-color: #ef4444; padding: 24px;">
        <div style="font-size: 40px; margin-bottom: 12px;">⚠️</div>
        <div style="color: #ef4444; font-weight: 600;">{{ auth.error }}</div>
        <button class="btn-secondary" style="margin-top: 20px; width: 100%" @click="initTma">Попробовать снова</button>
      </div>
    </div>
    <router-view v-else v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
  </div>
</template>

<style>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.error-banner {
  padding: 32px 16px;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
