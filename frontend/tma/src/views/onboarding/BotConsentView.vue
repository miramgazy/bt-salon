<template>
  <div class="onboarding-page">
    <div class="card">
      <h1 class="card-title">{{ t('onboarding.consent.title') }}</h1>
      <p class="card-hint">{{ t('onboarding.consent.hint') }}</p>

      <!-- Error -->
      <div v-if="error" class="alert alert--error">{{ error }}</div>


      <!-- Bot icon -->
      <div class="bot-icon">
        <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
        </svg>
      </div>

      <div class="actions">
        <!-- Allow button -->
        <button
          class="btn-primary"
          @click="handleAllow"
          :disabled="loading || waitingForBot"
        >
          <svg v-if="loading" class="spin" fill="none" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" class="opacity-25"/>
            <path fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" class="opacity-75"/>
          </svg>
          <span>{{ loading ? t('common.loading') : t('onboarding.consent.allow') }}</span>
        </button>

        <!-- Decline button -->
        <button
          class="btn-secondary"
          @click="handleDecline"
          :disabled="loading || waitingForBot"
        >
          {{ t('onboarding.consent.decline') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import telegramService from '@/services/telegram'

const { t } = useI18n()
const router = useRouter()
const auth = useAuthStore()

const loading = ref(false)
const error = ref('')

function goNext() {
  router.push('/')
}

async function handleAllow() {
  loading.value = true
  error.value = ''
  try {
    await auth.updateProfile({ is_bot_subscribed: true })
    goNext()
  } catch (err) {
    console.error('handleAllow error:', err)
    error.value = err.response?.data?.detail || 'Произошла ошибка'
  } finally {
    loading.value = false
  }
}

async function handleDecline() {
  loading.value = true
  error.value = ''
  try {
    // Save explicit decline (false) so we don't ask again
    await auth.updateProfile({ is_bot_subscribed: false })
    goNext()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Произошла ошибка'
  } finally {
    loading.value = false
  }
}

onUnmounted(() => { stopPolling() })
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
.card {
  background: #fff;
  border-radius: 24px;
  box-shadow: 0 25px 60px rgba(0, 0, 0, 0.2);
  max-width: 420px;
  width: 100%;
  padding: 32px 24px;
}
.card-title {
  font-size: 22px;
  font-weight: 700;
  color: #111827;
  margin-bottom: 8px;
  text-align: center;
}
.card-hint {
  font-size: 13px;
  color: #6b7280;
  text-align: center;
  margin-bottom: 20px;
}
.bot-icon {
  width: 72px;
  height: 72px;
  background: #ede9fe;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 24px;
}
.bot-icon svg { width: 36px; height: 36px; color: #667eea; }
.alert {
  padding: 12px 16px;
  border-radius: 10px;
  font-size: 13px;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.alert--error { background: #fef2f2; border: 1px solid #fecaca; color: #b91c1c; }
.alert--info  { background: #ede9fe; border: 1px solid #c4b5fd; color: #5b21b6; }
.alert svg { width: 16px; height: 16px; flex-shrink: 0; }
.actions { display: flex; flex-direction: column; gap: 12px; }
.btn-primary {
  width: 100%;
  background: #667eea;
  color: #fff;
  border: none;
  border-radius: 14px;
  padding: 16px;
  font-size: 15px;
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
.btn-primary:disabled { background: #d1d5db; cursor: not-allowed; }
.btn-primary svg { width: 18px; height: 18px; }
.btn-secondary {
  width: 100%;
  background: #f3f4f6;
  color: #374151;
  border: none;
  border-radius: 14px;
  padding: 16px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-secondary:hover { background: #e5e7eb; }
.btn-secondary:active { transform: scale(0.97); }
.btn-secondary:disabled { opacity: 0.5; cursor: not-allowed; }
.spin { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
