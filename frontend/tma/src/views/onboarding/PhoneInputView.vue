<template>
  <div class="onboarding-page">
    <div class="card">
      <!-- Title -->
      <h1 class="card-title">{{ t('onboarding.phone.title') }}</h1>
      <p class="card-hint">{{ t('onboarding.phone.hint') }}</p>

      <!-- Error -->
      <div v-if="error" class="alert alert--error">{{ error }}</div>

      <!-- Waiting for contact spinner -->
      <div v-if="waitingForContact" class="alert alert--info">
        <svg class="spin" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
        </svg>
        <span>{{ t('onboarding.phone.waitingContact') }}</span>
      </div>

      <div class="fields">
        <!-- Telegram share button -->
        <div v-if="isInTelegram && !phone && !waitingForContact">
          <button class="btn-primary" @click="requestContact" :disabled="waitingForContact">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
            </svg>
            <span>{{ t('onboarding.phone.sharePhone') }}</span>
          </button>
          <div class="divider">
            <span>{{ t('common.or') }}</span>
          </div>
        </div>

        <!-- Manual phone input -->
        <div>
          <label class="input-label">
            {{ t('onboarding.phone.phoneLabel') }} <span class="required">*</span>
          </label>
          <input
            v-model="phone"
            type="tel"
            :placeholder="t('onboarding.phone.placeholder')"
            class="input-field"
            @input="formatPhone"
          />
          <p class="input-hint">{{ t('onboarding.phone.formatHint') }}</p>
        </div>

        <!-- Continue button -->
        <button
          class="btn-primary"
          @click="handleContinue"
          :disabled="saving || !phone"
        >
          <svg v-if="saving" class="spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
          </svg>
          <span>{{ saving ? t('common.saving') : t('common.continue') }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import telegramService from '@/services/telegram'

const { t } = useI18n()
const router = useRouter()
const auth = useAuthStore()

const phone = ref('')
const saving = ref(false)
const error = ref('')
const isInTelegram = ref(false)
const waitingForContact = ref(false)

let contactRequestedEventHandler = null
let mainButtonClickHandler = null
let autoContinueTriggered = false
let pollingInterval = null
let pollingAttempts = 0
const MAX_POLLING_ATTEMPTS = 5
const POLLING_INTERVAL = 4000

let socket = null

// ── Helpers ────────────────────────────────────────────────────

function normalizePhoneValue(value) {
  const raw = String(value || '').replace(/[^\d+]/g, '')
  const digits = raw.replace(/\D/g, '')
  if (!digits) return ''
  if (digits.startsWith('7')) return `+${digits}`
  if (digits.startsWith('8')) return `+7${digits.slice(1)}`
  return `+7${digits}`
}

async function fetchPhoneFromBackend() {
  try {
    await auth.fetchCurrentUser()
    return auth.user?.phone || ''
  } catch {
    return ''
  }
}

// ── Polling ────────────────────────────────────────────────────

function stopPhonePolling() {
  if (pollingInterval) { clearInterval(pollingInterval); pollingInterval = null }
  pollingAttempts = 0
}

function startPhonePolling() {
  stopPhonePolling()
  pollingAttempts = 0

  const checkPhone = async () => {
    if (phone.value) { stopPhonePolling(); return }
    pollingAttempts++
    if (pollingAttempts > MAX_POLLING_ATTEMPTS) {
      stopPhonePolling()
      if (!phone.value && waitingForContact.value) {
        waitingForContact.value = false
        error.value = t('onboarding.phone.phoneNotReceived')
      }
      return
    }
    const fromBackend = await fetchPhoneFromBackend()
    if (fromBackend) {
      stopPhonePolling()
      phone.value = normalizePhoneValue(fromBackend)
      error.value = ''
      waitingForContact.value = false
      if (!autoContinueTriggered && !saving.value) {
        autoContinueTriggered = true
        setTimeout(() => handleContinue(), 500)
      }
    }
  }

  checkPhone()
  pollingInterval = setInterval(checkPhone, POLLING_INTERVAL)
}

// ── WebSocket ──────────────────────────────────────────────────

function connectWebSocket() {
  if (socket) return
  
  const userId = auth.user?.id
  if (!userId) {
    startPhonePolling()
    return
  }
  
  const baseUrl = import.meta.env.VITE_API_BASE_URL || ''
  let wsUrl = ''
  
  if (baseUrl.includes('://')) {
    const url = new URL(baseUrl)
    const protocol = url.protocol === 'https:' ? 'wss:' : 'ws:'
    wsUrl = `${protocol}//${url.host}/ws/user_updates/${userId}/`
  } else {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    wsUrl = `${protocol}//${window.location.host}/ws/user_updates/${userId}/`
  }
  
  try {
    socket = new WebSocket(wsUrl)
    
    socket.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.message?.event === 'phone_updated') {
        const normalized = normalizePhoneValue(data.message.phone)
        if (normalized) {
          phone.value = normalized
          waitingForContact.value = false
          if (socket) { socket.close(); socket = null }
          if (!autoContinueTriggered && !saving.value) {
            autoContinueTriggered = true
            setTimeout(() => handleContinue(), 500)
          }
        }
      }
    }
    
    socket.onerror = () => {
      console.warn('WS connection failed, falling back to polling')
      startPhonePolling()
    }
    
    socket.onclose = () => {
      socket = null
    }

    // Set a timeout for WS just in case
    setTimeout(() => {
      if (waitingForContact.value && !phone.value && !pollingInterval) {
        startPhonePolling()
      }
    }, 5000)

  } catch (err) {
    startPhonePolling()
  }
}

// ── Lifecycle ──────────────────────────────────────────────────

onMounted(async () => {
  isInTelegram.value = telegramService.isInTelegram()
  const existing = await fetchPhoneFromBackend()
  if (existing) phone.value = normalizePhoneValue(existing)
})

onUnmounted(() => {
  stopPhonePolling()
  if (socket) { socket.close(); socket = null }
  const webApp = telegramService.getWebApp()
  if (webApp) {
    if (contactRequestedEventHandler) webApp.offEvent?.('contactRequested', contactRequestedEventHandler)
    if (mainButtonClickHandler) { webApp.MainButton?.offClick(mainButtonClickHandler); webApp.MainButton?.hide() }
  }
})

watch(phone, (newPhone) => {
  if (newPhone && isInTelegram.value) {
    if (waitingForContact.value) { waitingForContact.value = false; stopPhonePolling() }
    const webApp = telegramService.getWebApp()
    if (webApp?.MainButton && mainButtonClickHandler) {
      webApp.MainButton.hide()
      webApp.MainButton.offClick(mainButtonClickHandler)
      mainButtonClickHandler = null
    }
  }
})

// ── Telegram requestContact ────────────────────────────────────

async function requestContact() {
  if (!isInTelegram.value) return
  const webApp = telegramService.getWebApp()
  if (!webApp) return

  error.value = ''
  autoContinueTriggered = false

  const finishSuccess = (phoneFromBackend) => {
    const normalized = normalizePhoneValue(phoneFromBackend)
    if (!normalized) return false
    waitingForContact.value = false
    phone.value = normalized
    if (!autoContinueTriggered && !saving.value) {
      autoContinueTriggered = true
      setTimeout(() => handleContinue(), 500)
    }
    return true
  }

  const finishManual = (message) => {
    startPhonePolling()
    if (message && message.includes('отменили')) {
      waitingForContact.value = false
      error.value = message
    }
  }

  // Modern path: webApp.requestContact()
  if (typeof webApp.requestContact === 'function') {
    waitingForContact.value = true

    if (contactRequestedEventHandler) {
      webApp.offEvent?.('contactRequested', contactRequestedEventHandler)
      contactRequestedEventHandler = null
    }

    contactRequestedEventHandler = async (evt) => {
      if (evt?.status === 'cancelled') {
        finishManual('Вы отменили отправку номера. Введите телефон вручную.')
        return
      }
      if (evt?.status === 'sent') connectWebSocket()
    }
    webApp.onEvent?.('contactRequested', contactRequestedEventHandler)

    try {
      webApp.requestContact((shared) => {
        if (shared === false) finishManual('Вы отменили отправку номера. Введите телефон вручную.')
      })
    } catch {
      finishManual('Не удалось запросить номер. Введите телефон вручную.')
      return
    }

    connectWebSocket()
    return
  }

  // Fallback: MainButton with request_contact
  const mainButton = webApp.MainButton
  if (!mainButton) { finishManual('Введите телефон вручную.'); return }

  mainButton.setText('Поделиться номером')
  mainButton.setParams({ request_contact: true })
  mainButton.show()

  mainButtonClickHandler = async () => {
    waitingForContact.value = true
    error.value = ''
    connectWebSocket()
    mainButton.hide()
    mainButton.offClick(mainButtonClickHandler)
    mainButtonClickHandler = null
  }
  mainButton.onClick(mainButtonClickHandler)
}

// ── Phone formatter ────────────────────────────────────────────

function formatPhone(event) {
  let value = event.target.value.replace(/\D/g, '')
  if (value.startsWith('7')) value = '+' + value
  else if (value.startsWith('8')) value = '+7' + value.slice(1)
  else if (!value.startsWith('+')) value = '+7' + value
  phone.value = value
}

// ── Continue ───────────────────────────────────────────────────

async function handleContinue() {
  if (!phone.value) { error.value = 'Пожалуйста, укажите номер телефона'; return }

  let clean = phone.value.replace(/\D/g, '')
  
  // If user entered 10 digits (e.g. 702...), prepend 7
  if (clean.length === 10) {
    clean = '7' + clean
    phone.value = '+' + clean
  }

  if (clean.length !== 11 || (!clean.startsWith('7') && !clean.startsWith('8'))) {
    error.value = 'Введите корректный номер (например, +77001234567)'
    return
  }

  // Normalize to +7...
  if (clean.startsWith('8')) {
    clean = '7' + clean.slice(1)
    phone.value = '+' + clean
  } else if (clean.startsWith('7')) {
    phone.value = '+' + clean
  }

  saving.value = true
  error.value = ''

  try {
    await auth.updateProfile({ phone: phone.value })
    await auth.fetchCurrentUser()

    if (auth.needsConsent) {
      router.push('/onboarding/consent')
    } else {
      if (auth.currentRole === 'admin') router.push('/admin')
      else if (auth.currentRole === 'master') router.push('/master')
      else router.push('/')
    }
  } catch (err) {
    error.value = err.response?.data?.phone?.[0] || 'Не удалось сохранить номер. Попробуйте ещё раз.'
  } finally {
    saving.value = false
  }
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
.fields { display: flex; flex-direction: column; gap: 16px; }
.input-label { display: block; font-size: 13px; font-weight: 600; color: #374151; margin-bottom: 6px; }
.required { color: #ef4444; }
.input-field {
  width: 100%;
  padding: 14px 16px;
  border: 1.5px solid #d1d5db;
  border-radius: 12px;
  font-size: 16px;
  color: #111827;
  background: #fff;
  outline: none;
  transition: border-color 0.2s;
}
.input-field:focus { border-color: #667eea; }
.input-hint { font-size: 11px; color: #9ca3af; margin-top: 4px; }
.divider { text-align: center; color: #9ca3af; font-size: 13px; padding: 4px 0; }
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
.spin { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
