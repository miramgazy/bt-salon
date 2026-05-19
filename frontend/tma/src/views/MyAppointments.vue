<template>
  <div class="appointments-view page-p">
    <div class="page-header">
      <button class="back-btn" @click="$router.push('/')">
        <Icon icon="mdi:arrow-left" width="20" />
      </button>
       <div class="page-title header-font" style="font-size: 24px;">{{ $t('appointments.title') }}</div>
    </div>
    
    <div v-if="loading" style="text-align:center; padding: 60px;">
      <div class="spinner"></div>
    </div>

     <div v-else-if="appointments.length === 0" class="empty-state fade-up">
       <div class="empty-icon">📅</div>
       <p style="color: var(--muted); margin-bottom: 24px;">{{ $t('appointments.empty') }}</p>
       <button class="btn-primary" @click="$router.push('/')">
         {{ $t('tma.book') }}
       </button>
     </div>

    <div v-else class="appointments-list fade-up">
      <div v-for="apt in appointments" :key="apt.id" class="card apt-card glass">
        <div class="apt-header">
          <div style="flex: 1">
             <h3 class="apt-service">{{ apt.display_title || apt.service_detail?.name }}</h3>
             <div class="apt-master">{{ $t('tma.masters') }}: {{ apt.master_detail?.first_name }}</div>
             <div v-if="apt.payment_status !== 'no_payment_required'" :class="['apt-payment-badge', apt.payment_status]">
               <Icon :icon="apt.payment_status === 'paid' ? 'mdi:check-decagram' : 'mdi:clock-alert-outline'" width="14" />
               {{ $t(`tma.paymentStatus.${apt.payment_status}`) }}
             </div>
           </div>
          <div :class="['status-badge', apt.status.toLowerCase()]">
            {{ formatStatus(apt.status) }}
          </div>
        </div>
        
        <div class="apt-details">
          <div class="apt-time">
            <Icon icon="mdi:calendar-clock" width="18" :style="{ color: 'var(--gold)' }" />
            <span>{{ formatDate(apt.start_time) }}</span>
          </div>
          <div class="apt-price-row">
             <div v-if="apt.prepayment_received > 0" class="apt-prepaid text-success">
                {{ $t('admin.prepayment') }}: {{ apt.prepayment_received }} ₸
             </div>
             <div class="apt-price">{{ apt.service_detail?.total_price }} ₸</div>
          </div>
        </div>
        
         <div class="apt-actions">
           <!-- Кнопка "Оплатить" — для записей ожидающих квитанцию -->
           <button v-if="apt.payment_status === 'pending_receipt' && apt.status === 'pending'"
                   class="btn-pay"
                   @click="$router.push({ name: 'payment-instruction', params: { appointmentId: apt.id } })">
             💳 {{ $t('tma.payButton', { amount: apt.prepayment_amount_required || apt.service_detail?.prepayment_value || 0 }) }}
           </button>
           <!-- Кнопка "Подробнее" — для записей на проверке -->
           <button v-else-if="apt.payment_status === 'review'"
                   class="btn-details"
                   @click="$router.push({ name: 'payment-instruction', params: { appointmentId: apt.id } })">
             {{ $t('tma.moreDetails') }}
           </button>
           <!-- Кнопка "Отменить" — только для активных, не отменённых и не завершённых -->
           <button v-if="['pending', 'confirmed'].includes(apt.status.toLowerCase()) && apt.payment_status !== 'pending_receipt'"
                   class="btn-cancel" 
                   @click="cancelApt(apt.id)">
             {{ $t('tma.cancelApt') }}
           </button>
         </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Icon } from '@iconify/vue'
import { useAuthStore } from '../stores/auth'
import { useI18n } from 'vue-i18n'
import api from '@/api'

const auth = useAuthStore()
const { t, locale } = useI18n()
const appointments = ref([])
const loading = ref(true)

const fetchAppointments = async () => {
  try {
    loading.value = true
    const res = await api.get('/appointments/', { 
      params: { my: 'true' }
    })
    let data = res.data.results || res.data
    // Sort so that 'pending_receipt' and 'review' are always at the top, then by creation date descending
    appointments.value = data.sort((a, b) => {
      const aPriority = ['pending_receipt', 'review'].includes(a.payment_status) ? 1 : 0
      const bPriority = ['pending_receipt', 'review'].includes(b.payment_status) ? 1 : 0
      if (aPriority !== bPriority) {
        return bPriority - aPriority
      }
      return new Date(b.created_at || b.start_time) - new Date(a.created_at || a.start_time)
    })
  } catch (err) {
    console.error('Fetch appointments error:', err)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  fetchAppointments()
  if (!auth.organizationSettings) {
    await auth.fetchCurrentUser()
  }
})

const formatDate = (iso) => {
  const d = new Date(iso)
  return d.toLocaleString(locale.value === 'kz' ? 'kk-KZ' : 'ru-RU', {
    day: 'numeric',
    month: 'long',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatStatus = (s) => {
  const map = {
    'pending': t('appointments.status.pending'),
    'confirmed': t('appointments.status.confirmed'),
    'cancelled': t('appointments.status.cancelled'),
    'done': t('appointments.status.done')
  }
  return map[s.toLowerCase()] || s
}

const cancelApt = async (id) => {
  if (!confirm(t('tma.cancelConfirm'))) return
  try {
    await api.post(`/appointments/${id}/cancel/`)
    await fetchAppointments()
  } catch (err) {
    alert(t('tma.error'))
  }
}
</script>

<style scoped>
.appointments-view {
  padding: 20px 16px 100px;
}

.apt-card {
  background: var(--card-bg);
  border: 1px solid var(--border);
  padding: 20px;
  position: relative;
  overflow: hidden;
  margin-bottom: 12px;
}

.apt-card::before {
  content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 4px;
  background: var(--gold); opacity: 0.3;
}

.apt-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.apt-service {
  font-family: var(--font-header);
  margin: 0;
  font-size: 19px;
  font-weight: 700;
  color: var(--text);
}

.apt-master {
  color: var(--gold);
  font-size: 11px;
  text-transform: uppercase;
  font-weight: 800;
  letter-spacing: 0.5px;
  margin-top: 4px;
}

.apt-payment-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 10px;
  font-weight: 700;
  margin-top: 8px;
}
.apt-payment-badge.paid {
  background: rgba(34, 160, 96, 0.1);
  color: #22a060;
}
.apt-payment-badge.pending_manual_invoice {
  background: rgba(201, 168, 76, 0.1);
  color: var(--gold);
}
.apt-payment-badge.pending_receipt {
  background: rgba(234, 179, 8, 0.1);
  color: #eab308;
}
.apt-payment-badge.review {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.apt-details {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.apt-price-row {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}
.apt-prepaid {
  font-size: 10px;
  font-weight: 700;
  margin-bottom: 2px;
}

.apt-time {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: var(--text);
  font-weight: 600;
}

.apt-price {
  font-family: var(--font-header);
  font-weight: 700;
  font-size: 18px;
  color: var(--gold);
}

.apt-actions {
  display: flex;
  gap: 8px;
  width: 100%;
}

.btn-details {
  flex: 1;
  padding: 12px;
  background: var(--gold-gradient);
  color: #000;
  border: none;
  border-radius: var(--radius-sm);
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  text-align: center;
  box-shadow: 0 4px 12px var(--gold-glow);
}

.btn-details:active {
  transform: scale(0.98);
}

.btn-pay {
  flex: 1;
  padding: 12px;
  background: var(--gold-gradient);
  color: #000;
  border: none;
  border-radius: var(--radius-sm);
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  text-align: center;
  box-shadow: 0 4px 12px var(--gold-glow);
}

.btn-pay:active {
  transform: scale(0.98);
  opacity: 0.9;
}

.btn-cancel {
  flex: 1;
  padding: 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  color: #e05252;
  border-radius: var(--radius-sm);
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  text-align: center;
}

.btn-cancel:active {
  background: rgba(224, 82, 82, 0.1);
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 20px;
  filter: grayscale(1) opacity(0.2);
}

/* Modal styles */
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,.7); z-index: 500;
  display: flex; align-items: flex-end; justify-content: center;
  backdrop-filter: blur(4px);
}
.modal {
  background: var(--bg); border-radius: 28px 28px 0 0; width: 100%; max-width: 450px;
  padding: 32px 20px 40px; border-top: 1px solid var(--border);
  box-shadow: 0 -10px 40px rgba(0,0,0,0.3);
  max-height: 90vh; display: flex; flex-direction: column;
}
.modal-header-actions {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 20px;
}
.modal-title {
  font-size: 20px; font-weight: 700; color: var(--text); font-family: var(--font-header);
}
.close-modal-btn {
  background: none; border: none; color: var(--text); cursor: pointer; display: flex; align-items: center; justify-content: center;
}
.modal-scroll-content {
  flex: 1; overflow-y: auto; padding-right: 4px;
}
.modal-scroll-content::-webkit-scrollbar { width: 4px; }
.modal-scroll-content::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }

.modal-row {
  display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid var(--border); font-size: 14px;
}
.modal-label { color: var(--muted); font-weight: 500; }
.modal-value { font-weight: 600; color: var(--text); }
.modal-value.gold { color: var(--gold); font-size: 18px; font-family: var(--font-header); }

.btn-kaspi {
  width: 100%;
  height: 54px;
  background: #FFFFFF;
  border: 1px solid #E5E5E5;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}
.btn-kaspi:active {
  transform: scale(0.98);
  background: #F9F9F9;
}
.btn-kaspi span {
  font-size: 16px;
  font-weight: 700;
  color: #000000;
}
.kaspi-logo {
  display: flex;
  align-items: center;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
.animate-spin {
  animation: spin 1s linear infinite;
}
</style>
