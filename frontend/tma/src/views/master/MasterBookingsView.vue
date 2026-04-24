<template>
  <div class="master-bookings">
    <div class="page-header">
      <button class="back-btn" @click="$router.push('/master')">
        <Icon icon="mdi:arrow-left" width="20" />
      </button>
      <h1 class="page-title">{{ $t('master.myAppointments', 'Мои записи') }}</h1>
    </div>
    
    <div class="date-selector">
      <button 
        :class="['date-pill', { active: activeTab === 'today' }]" 
        @click="setDate('today')"
      >{{ $t('master.today', 'Сегодня') }}</button>
      <button 
        :class="['date-pill', { active: activeTab === 'tomorrow' }]" 
        @click="setDate('tomorrow')"
      >{{ $t('master.tomorrow', 'Завтра') }}</button>
      <div :class="['date-pill custom-date-wrapper', { active: activeTab === 'custom' }]">
         <Icon icon="mdi:calendar-month-outline" width="16" />
         <input type="date" v-model="selectedDate" class="date-input-hidden" @change="activeTab = 'custom'" />
         <span>{{ activeTab === 'custom' ? formatDateShort(selectedDate) : 'Дата' }}</span>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
       <div class="spinner"></div>
    </div>

    <div v-else-if="appointments.length === 0" class="empty-state">
       <div class="empty-icon">📅</div>
       <p>{{ $t('appointments.empty') }}</p>
    </div>

    <div v-else class="bookings-list">
       <div v-for="apt in appointments" :key="apt.id" class="booking-card">
          <div class="booking-time">
             <div class="time-main">{{ formatStartTime(apt.start_time) }}</div>
             <div class="time-duration">{{ getDuration(apt.start_time, apt.end_time) }} мин</div>
          </div>
          <div class="booking-info">
             <div class="client-name">{{ apt.client_detail?.full_name || 'Клиент' }}</div>
             <div class="service-name text-gold">{{ apt.service_detail?.name || 'Услуга' }}</div>
             <div v-if="apt.notes" class="booking-notes">
                <Icon icon="mdi:note-text-outline" width="14" />
                <span>{{ apt.notes }}</span>
             </div>
          </div>
          <div class="booking-status">
             <span :class="['status-badge', apt.status.toLowerCase()]">{{ apt.status }}</span>
          </div>
       </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { Icon } from '@iconify/vue'
import api from '@/api'

const activeTab = ref('today')
const selectedDate = ref(new Date().toISOString().split('T')[0])
const appointments = ref([])
const loading = ref(false)

const setDate = (type) => {
  activeTab.value = type
  const target = new Date()
  if (type === 'tomorrow') {
    target.setDate(target.getDate() + 1)
  }
  selectedDate.value = target.toISOString().split('T')[0]
}

const fetchAppointments = async () => {
  loading.value = true
  try {
    const res = await api.get('/appointments/', {
      params: {
        my: 'true',
        date_from: selectedDate.value,
        date_to: selectedDate.value
      }
    })
    appointments.value = res.data.results || res.data
  } catch (e) {
    console.error('Fetch appointments error', e)
  } finally {
    loading.value = false
  }
}

const formatStartTime = (iso) => {
  return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const getDuration = (start, end) => {
  const diff = (new Date(end) - new Date(start)) / 60000
  return Math.round(diff)
}

const formatDateShort = (iso) => {
  if (!iso) return ''
  const d = new Date(iso)
  return d.toLocaleDateString([], { day: 'numeric', month: 'short' })
}

watch(selectedDate, () => {
  fetchAppointments()
})

onMounted(() => {
  fetchAppointments()
})
</script>

<style scoped>
.master-bookings {
  padding: 20px 16px 100px;
}
.date-selector { display: flex; gap: 10px; align-items: center; margin-bottom: 24px; padding: 4px 0; overflow-x: auto; scrollbar-width: none; }
.date-selector::-webkit-scrollbar { display: none; }

.date-pill {
  white-space: nowrap;
  padding: 8px 16px;
  border-radius: 20px;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  color: var(--muted);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}
.date-pill.active {
  background: var(--gold-gradient);
  color: #000;
  border-color: var(--gold);
  box-shadow: 0 4px 10px var(--gold-glow);
}

.custom-date-wrapper {
  display: flex;
  align-items: center;
  gap: 6px;
  position: relative;
}

.date-input-hidden {
  position: absolute;
  inset: 0;
  opacity: 0;
  cursor: pointer;
  width: 100%;
}

.bookings-list { display: flex; flex-direction: column; gap: 12px; }
.booking-card {
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: var(--radius); padding: 18px; display: flex; gap: 16px; align-items: center;
  position: relative; overflow: hidden;
}
.booking-card::before { content: ''; position: absolute; left: 0; inset: 0 0 0 0; width: 4px; background: var(--gold); opacity: 0.3; }

.booking-time { width: 64px; text-align: center; }
.time-main { font-size: 16px; font-weight: 800; color: var(--gold); font-family: var(--font-header); }
.time-duration { font-size: 10px; color: var(--muted); margin-top: 2px; font-weight: 600; }

.booking-info { flex: 1; }
.client-name { font-size: 16px; font-weight: 700; color: var(--text); margin-bottom: 2px; }
.service-name { font-size: 13px; color: var(--muted); font-weight: 500; }
.booking-notes { font-size: 11px; color: var(--muted); margin-top: 8px; display: flex; align-items: center; gap: 6px; font-style: italic; }

.loading-state, .empty-state { padding: 80px 20px; text-align: center; color: var(--muted); }
.empty-icon { font-size: 54px; margin-bottom: 16px; opacity: 0.2; }
</style>
