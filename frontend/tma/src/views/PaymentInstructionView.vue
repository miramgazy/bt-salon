<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useI18n } from 'vue-i18n'
import { Icon } from '@iconify/vue'
import api from '@/api'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const { t, locale } = useI18n()

const appointmentId = route.params.appointmentId
const appointment = ref(null)
const loading = ref(true)
const error = ref(null)
const showSuccess = ref(false)
const showCancelled = ref(false)

let pollInterval = null

const fetchAppointmentDetail = async () => {
  try {
    loading.value = true
    const res = await api.get(`/appointments/${appointmentId}/`)
    appointment.value = res.data
    
    // If the payment is already confirmed or no prepayment required, redirect to success
    if (res.data.payment_status === 'paid' || res.data.status === 'confirmed') {
      showSuccess.value = true
    } else if (res.data.status === 'cancelled') {
      showCancelled.value = true
    }
  } catch (err) {
    console.error('Fetch appointment detail fail:', err)
    error.value = t('tma.error')
  } finally {
    loading.value = false
  }
}

const startStatusPolling = () => {
  if (pollInterval) clearInterval(pollInterval)
  pollInterval = setInterval(async () => {
    try {
      const pseudoId = `SA_${appointmentId}`
      const res = await api.get(`/payments/status/${pseudoId}/`)
      const newStatus = res.data.status // e.g. pending_receipt, review, paid
      
      if (appointment.value) {
        appointment.value.payment_status = newStatus
        if (newStatus === 'paid') {
          appointment.value.status = 'confirmed'
          showSuccess.value = true
          clearInterval(pollInterval)
        }
      }
    } catch (e) {
      console.error('Status poll error:', e)
    }
  }, 180000) // Poll every 3 minutes
}

onMounted(async () => {
  await fetchAppointmentDetail()
  if (!auth.organizationSettings) {
    await auth.fetchCurrentUser()
  }
  if (appointment.value && ['pending_receipt', 'review'].includes(appointment.value.payment_status)) {
    startStatusPolling()
  }
})

onUnmounted(() => {
  if (pollInterval) clearInterval(pollInterval)
})

const formatDate = (iso) => {
  if (!iso) return ''
  const d = new Date(iso)
  return d.toLocaleString(locale.value === 'kz' ? 'kk-KZ' : 'ru-RU', {
    day: 'numeric',
    month: 'long',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const openPaymentLink = () => {
  const link = auth.organizationSettings?.kaspi_payment_link
  if (!link) return
  try {
    if (window.Telegram?.WebApp && typeof window.Telegram.WebApp.openLink === 'function') {
      window.Telegram.WebApp.openLink(link)
    } else {
      window.open(link, '_blank')
    }
  } catch (err) {
    console.error('Failed to open payment link:', err)
  }
}

const cancelBooking = async () => {
  if (!confirm(t('tma.cancelConfirm'))) return
  try {
    await api.post(`/appointments/${appointmentId}/cancel/`)
    router.push('/tma-appointments')
  } catch (err) {
    alert(t('tma.error'))
  }
}

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="payment-instruction-view page-p">
    <!-- ══ SUCCESS SCREEN ══ -->
    <div v-if="showSuccess" class="success fade-up">
      <div class="success-icon">✨</div>
      <div class="success-title header-font">{{ $t('tma.confirmTitle') }}</div>
      <div class="success-sub">{{ $t('tma.confirmSub') }}</div>
      <button class="btn-primary" style="margin-top: 40px; width: 100%" @click="router.push('/tma-appointments')">
        {{ $t('appointments.title') }}
      </button>
      <button class="btn-secondary" style="margin-top: 12px; width: 100%" @click="goHome">
        {{ $t('tma.goHome') }}
      </button>
    </div>

    <!-- ══ LOADING STATE ══ -->
    <div v-else-if="loading" style="text-align: center; padding: 60px;">
      <div class="spinner"></div>
    </div>

    <!-- ══ ERROR STATE ══ -->
    <div v-else-if="error" class="empty-state fade-up">
      <div class="empty-icon">⚠️</div>
      <p style="color: var(--text-error); margin-bottom: 24px;">{{ error }}</p>
      <button class="btn-primary" @click="goHome">{{ $t('tma.goHome') }}</button>
    </div>

    <!-- ══ CANCELLED STATE ══ -->
    <div v-else-if="showCancelled" class="empty-state fade-up" style="padding: 40px 20px;">
      <div class="empty-icon" style="font-size: 64px; margin-bottom: 20px;">⌛</div>
      <div class="header-font" style="font-size: 22px; font-weight: 700; color: #ef4444; margin-bottom: 12px;">
        {{ $t('tma.timeExpiredTitle', 'Время истекло') }}
      </div>
      <p style="color: var(--muted); font-size: 14px; line-height: 1.6; margin-bottom: 30px;">
        {{ $t('tma.timeExpiredSub', 'Время ожидания предоплаты истекло (5 минут), и запись была автоматически отменена. Пожалуйста, запишитесь заново.') }}
      </p>
      <button class="btn-primary" style="width: 100%;" @click="goHome">
        {{ $t('tma.btnRebook', 'Записаться заново') }}
      </button>
    </div>

    <!-- ══ INSTRUCTION SCREEN ══ -->
    <div v-else-if="appointment" class="fade-up">
      <div class="page-header">
        <button class="back-btn" @click="router.push('/tma-appointments')">
          <Icon icon="mdi:arrow-left" width="20" />
        </button>
        <div class="page-title header-font" style="font-size: 20px;">{{ $t('tma.paymentDetails') }}</div>
      </div>

      <!-- Booking Info Card -->
      <div class="card glass text-left w-full mb-6" style="padding: 18px;">
        <div class="modal-row" style="padding-top: 0;">
          <span class="modal-label">{{ $t('tma.services') }}</span>
          <span class="modal-value font-bold" style="color: var(--text);">
            {{ appointment?.display_title || appointment?.service_detail?.name }}
          </span>
        </div>
        <div class="modal-row">
          <span class="modal-label">{{ $t('tma.masters') }}</span>
          <span class="modal-value" style="color: var(--text);">
            {{ appointment?.master_detail?.first_name }} {{ appointment?.master_detail?.last_name }}
          </span>
        </div>
        <div class="modal-row">
          <span class="modal-label">{{ $t('tma.chooseTime') }}</span>
          <span class="modal-value font-semibold" style="color: var(--text);">
            {{ formatDate(appointment?.start_time) }}
          </span>
        </div>
        <div class="modal-row" style="border-bottom: none; padding-bottom: 0;">
          <span class="modal-label">{{ $t('tma.total') }}</span>
          <span class="modal-value gold font-bold" style="color: var(--gold); font-size: 16px;">
            {{ appointment?.service_detail?.total_price }} ₸
          </span>
        </div>
      </div>

      <!-- Prepayment Instruction Block -->
      <div class="card glass text-left w-full mb-6" style="padding: 18px;">
        <h4 class="font-bold text-sm mb-3 flex items-center gap-2" style="color: var(--text);">
          <span>📋</span> {{ $t('tma.instruction.title') }}
        </h4>
        <ol class="text-xs flex flex-col gap-3" style="list-style-type: decimal; padding-left: 16px; color: var(--text); opacity: 0.9;">
          <li v-html="$t('tma.instruction.step1', { amount: appointment?.prepayment_amount_required || appointment?.service_detail?.prepayment_value || 0 })"></li>
          <li v-html="$t('tma.instruction.step2')"></li>
          <li v-html="$t('tma.instruction.step3')"></li>
          <li v-html="$t('tma.instruction.step4', { bot: auth.organizationSettings?.bot_username || 'bot' })"></li>
        </ol>
        <div class="mt-4 pt-3 border-t text-xs font-semibold" style="border-color: var(--border); color: #ef4444;" v-html="$t('tma.instruction.timeoutWarning')"></div>
      </div>

      <!-- Payment Status Block -->
      <div v-if="appointment?.payment_status === 'pending_receipt'" class="flex items-center justify-center gap-2.5 text-xs text-warning bg-warning/10 py-3 px-4 rounded-xl w-full mb-6" style="color: #eab308; background: rgba(234, 179, 8, 0.08); border: 1px solid rgba(234, 179, 8, 0.15);">
        <div class="spinner-mini animate-spin" style="border-top-color: #eab308; width: 14px; height: 14px; border-radius: 50%; border: 2px solid rgba(234, 179, 8, 0.2); border-top-color: #eab308;"></div>
        <span class="font-semibold">{{ $t('tma.waitingReceipt') }}</span>
      </div>
      
      <div v-else-if="appointment?.payment_status === 'review'" class="flex items-center justify-center gap-2.5 text-xs text-primary bg-primary/10 py-3 px-4 rounded-xl w-full mb-6" style="color: #3b82f6; background: rgba(59, 130, 246, 0.08); border: 1px solid rgba(59, 130, 246, 0.15);">
        <div class="spinner-mini animate-spin" style="border-top-color: #3b82f6; width: 14px; height: 14px; border-radius: 50%; border: 2px solid rgba(59, 130, 246, 0.2); border-top-color: #3b82f6;"></div>
        <span class="font-semibold">{{ $t('tma.reviewReceipt') }}</span>
      </div>

      <!-- Action Buttons -->
      <div class="flex flex-col gap-3.5 mt-6 w-full">
        <button class="btn-kaspi" @click="openPaymentLink">
          <span>{{ $t('tma.payButton', { amount: appointment?.prepayment_amount_required || appointment?.service_detail?.prepayment_value || 0 }) }}</span>
        </button>
        
        <div class="flex gap-3 w-full">
          <button class="btn-secondary" style="flex: 1; padding: 14px; border-radius: 12px;" @click="router.push('/tma-appointments')">
            {{ $t('tma.closeButton') }}
          </button>
          
          <button class="btn-cancel-action" style="flex: 1; padding: 14px; border-radius: 12px; background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.2); color: #ef4444; font-weight: 600; font-size: 14px; text-align: center; cursor: pointer; transition: all 0.2s;" @click="cancelBooking">
            {{ $t('tma.cancelApt') }}
          </button>
        </div>
      </div>
    </div>

    <!-- ══ FALLBACK LOADER ══ -->
    <div v-else style="text-align: center; padding: 60px;">
      <div class="spinner"></div>
    </div>
  </div>
</template>

<style scoped>
.payment-instruction-view {
  padding: 20px 16px 100px;
}

.modal-row {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid var(--border);
  font-size: 14px;
}

.modal-label {
  color: var(--muted);
  font-weight: 500;
}

.modal-value {
  font-weight: 600;
  color: var(--text);
  text-align: right;
  max-width: 60%;
}

.btn-kaspi {
  width: 100%;
  height: 54px;
  background: #F14635;
  border: none;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 12px rgba(241, 70, 53, 0.2);
}

.btn-kaspi:active {
  transform: scale(0.98);
  background: #D63425;
}

.btn-kaspi span {
  font-size: 16px;
  font-weight: 700;
  color: #FFFFFF;
}

.kaspi-logo {
  display: flex;
  align-items: center;
}

.btn-cancel-action:active {
  transform: scale(0.98);
  background: rgba(239, 68, 68, 0.15) !important;
}

.success {
  text-align: center;
  padding: 60px 20px;
}

.success-icon {
  font-size: 64px;
  margin-bottom: 20px;
  filter: drop-shadow(0 4px 10px var(--gold-glow));
}

.success-title {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 12px;
  color: var(--gold);
  font-family: var(--font-header);
}

.success-sub {
  font-size: 15px;
  color: var(--muted);
  line-height: 1.6;
}

.spinner-mini {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  border: 2px solid rgba(0,0,0,0.1);
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.animate-spin {
  animation: spin 1s linear infinite;
}
</style>
