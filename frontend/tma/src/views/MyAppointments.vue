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
             <h3 class="apt-service">{{ apt.service_detail?.name }}</h3>
             <div class="apt-master">{{ $t('tma.masters') }}: {{ apt.master_detail?.first_name }}</div>
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
          <div class="apt-price">{{ apt.service_detail?.total_price }} ₸</div>
        </div>
        
         <button v-if="['pending', 'confirmed'].includes(apt.status.toLowerCase())" 
                 class="btn-cancel" 
                 @click="cancelApt(apt.id)">
           {{ $t('tma.cancelApt') }}
         </button>
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
    appointments.value = res.data.results || res.data
  } catch (err) {
    console.error('Fetch appointments error:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchAppointments()
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
    'pending': t('appointments.statuses.pending'),
    'confirmed': t('appointments.statuses.confirmed'),
    'cancelled': t('appointments.statuses.cancelled'),
    'done': t('appointments.statuses.done')
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

.apt-details {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
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

.btn-cancel {
  width: 100%;
  padding: 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  color: #e05252;
  border-radius: var(--radius-sm);
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
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
</style>
