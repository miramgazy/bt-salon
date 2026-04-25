<script setup>
import { onMounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'
import { getStoredLocale } from './i18n/index'
import { useI18n } from 'vue-i18n'
import AuthLoader from './components/common/AuthLoader.vue'

const auth = useAuthStore()
const router = useRouter()
const { locale } = useI18n()

/**
 * After successful login, determine where to redirect the user:
 */
function navigateAfterAuth() {
  // 1. Mandatory Onboarding Checks
  if (!auth.isOnboarded) {
    return router.replace('/onboarding/welcome')
  }
  if (auth.needsConsent) {
    return router.replace('/onboarding/consent')
  }

  // 2. Explicit User Mode Choice (activeRole)
  if (auth.activeRole) {
    if (auth.activeRole === 'admin' && auth.isAdmin) {
       return router.replace('/admin')
    }
    if (auth.activeRole === 'owner' && auth.isOwner) {
       return router.replace('/owner')
    }
    if (auth.activeRole === 'master' && auth.isMaster) {
       return router.replace('/master')
    }
    if (auth.activeRole === 'client') {
       return router.replace('/')
    }
  }

  // 3. Auto-Detection by Physical Role
  if (auth.role === 'admin') {
    return router.replace('/admin')
  }
  if (auth.role === 'owner') {
    return router.replace('/owner')
  }
  if (auth.role === 'master') {
    return router.replace('/master')
  }

  // 4. Default to Client
  return router.replace('/')
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

  const startTime = Date.now()
  
  // Early navigation hint based on cached role (prevents initial jump)
  auth.restoreAuth()
  if (auth.isAuthenticated) {
     navigateAfterAuth()
  }

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
        
        const elapsed = Date.now() - startTime
        const remaining = Math.max(0, 5200 - elapsed)
        await new Promise(r => setTimeout(r, remaining))
        
        // Final navigation check (in case role changed on server)
        await navigateAfterAuth()
        await router.isReady()
        await nextTick()
      }
      auth.loading = false
    } else {
      auth.loading = false
    }
  } else {
    // Non-Telegram environment (Development/Web)
    if (auth.isAuthenticated) {
      await auth.fetchCurrentUser()
      applyThemeFromBot()
      
      const elapsed = Date.now() - startTime
      const remaining = Math.max(0, 5200 - elapsed)
      await new Promise(r => setTimeout(r, remaining))
      
      await navigateAfterAuth()
      await router.isReady()
      await nextTick()
    } else {
      await new Promise(r => setTimeout(r, 5200))
      await router.replace('/onboarding/welcome')
      await router.isReady()
      await nextTick()
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
    <transition name="fade">
      <AuthLoader v-if="auth.loading" />
    </transition>
    
    <div v-if="!auth.loading && auth.error" class="error-banner">
      <div class="card glass" style="border-color: #ef4444; padding: 24px;">
        <div style="font-size: 40px; margin-bottom: 12px;">⚠️</div>
        <div style="color: #ef4444; font-weight: 600;">{{ auth.error }}</div>
        <button class="btn-secondary" style="margin-top: 20px; width: 100%" @click="initTma">Попробовать снова</button>
      </div>
    </div>
    <router-view v-else-if="!auth.loading" v-slot="{ Component }">
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
