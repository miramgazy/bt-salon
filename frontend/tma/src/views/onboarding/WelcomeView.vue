<template>
  <div class="onboarding-page">
    <!-- Language selection modal (first visit) -->
    <div v-if="showLanguageModal" class="modal-overlay">
      <div class="modal-card">
        <p class="modal-title">{{ t('language.selectLanguage') }}</p>
        <div class="modal-buttons">
          <button class="btn-lang btn-lang--primary" @click="selectLanguage('kz')">
            {{ t('language.kz') }}
          </button>
          <button class="btn-lang btn-lang--secondary" @click="selectLanguage('ru')">
            {{ t('language.ru') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Main welcome card -->
    <div class="welcome-card">
      <!-- Icon -->
      <div class="welcome-icon">
        <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M14.121 14.121L19 19m-7-7l7-7m-7 7l-2.879 2.879M12 12L9.121 9.121m0 0L4 4m5.121 5.121L4 9m5.121.121V4M12 12l2.879 2.879" />
        </svg>
      </div>

      <!-- Title -->
      <h1 class="welcome-title">{{ t('welcome.title') }}</h1>

      <!-- Description -->
      <div class="welcome-desc">
        <p>
          {{ t('welcome.introPrefix') }}
          <span class="org-name">{{ auth.organizationName || t('common.ourService') }}</span>
          {{ t('welcome.introSuffix') }}
        </p>
        <p>{{ t('welcome.introSecond') }}</p>
      </div>

      <!-- Continue button -->
      <button class="btn-primary" @click="handleContinue">
        <span>{{ t('common.continue') }}</span>
        <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import { getStoredLocale, setStoredLocale } from '@/i18n/index'

const { t, locale } = useI18n()
const router = useRouter()
const auth = useAuthStore()

const showLanguageModal = ref(false)

onMounted(() => {
  const stored = getStoredLocale()
  if (!stored) {
    showLanguageModal.value = true
  } else {
    locale.value = stored
  }
})

watch(locale, (newLocale) => {
  setStoredLocale(newLocale)
  // Persist to backend if authenticated
  if (auth.isAuthenticated) {
    auth.updateProfile({ language: newLocale }).catch(() => {})
  }
})

function selectLanguage(code) {
  locale.value = code
  setStoredLocale(code)
  showLanguageModal.value = false
  if (auth.isAuthenticated) {
    auth.updateProfile({ language: code }).catch(() => {})
  }
}

function handleContinue() {
  if (showLanguageModal.value) return
  router.push('/onboarding/phone')
}
</script>

<style scoped>
.onboarding-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 50;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  background: rgba(0, 0, 0, 0.5);
}
.modal-card {
  background: #fff;
  border-radius: 24px;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.25);
  max-width: 340px;
  width: 100%;
  padding: 24px;
  text-align: center;
}
.modal-title {
  font-size: 16px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 16px;
}
.modal-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.btn-lang {
  width: 100%;
  padding: 14px 16px;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-lang:active { transform: scale(0.96); }
.btn-lang--primary { background: #667eea; color: #fff; }
.btn-lang--primary:hover { background: #5a6fd6; }
.btn-lang--secondary { background: #f3f4f6; color: #1f2937; }
.btn-lang--secondary:hover { background: #e5e7eb; }

/* Welcome card */
.welcome-card {
  background: #fff;
  border-radius: 24px;
  box-shadow: 0 25px 60px rgba(0, 0, 0, 0.2);
  max-width: 420px;
  width: 100%;
  padding: 32px 24px;
  text-align: center;
}
.welcome-icon {
  width: 80px;
  height: 80px;
  background: #ede9fe;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 24px;
}
.welcome-icon svg {
  width: 40px;
  height: 40px;
  color: #667eea;
}
.welcome-title {
  font-size: 28px;
  font-weight: 700;
  color: #111827;
  margin-bottom: 16px;
}
.welcome-desc {
  color: #6b7280;
  font-size: 15px;
  line-height: 1.6;
  margin-bottom: 32px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.org-name {
  font-weight: 600;
  color: #667eea;
}
.btn-primary {
  width: 100%;
  background: #667eea;
  color: #fff;
  border: none;
  border-radius: 14px;
  padding: 16px 24px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.2s;
}
.btn-primary:hover { background: #5a6fd6; }
.btn-primary:active { transform: scale(0.97); }
.btn-primary svg { width: 18px; height: 18px; }
</style>
