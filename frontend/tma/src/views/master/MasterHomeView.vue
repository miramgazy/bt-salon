<template>
  <div class="master-home">
    <!-- ── HEADER ── -->
    <div class="hdr">
      <div class="hdr-row">
        <div class="hdr-left">
          <div class="avatar">
            <template v-if="auth.user?.photo_url">
               <img :src="auth.user.photo_url" alt="photo" />
            </template>
            <span v-else>👤</span>
          </div>
          <div>
            <div class="hdr-sub">{{ $t('master.title') }}</div>
            <div class="hdr-name">{{ auth.user?.first_name }} {{ auth.user?.last_name }}</div>
            <div :class="['hdr-status', { 'open': shiftStatus.isOpen, 'scheduled': shiftStatus.isScheduled && !shiftStatus.isOpen }]">
              <span :class="['status-dot', { 'open': shiftStatus.isOpen, 'scheduled': shiftStatus.isScheduled && !shiftStatus.isOpen }]" />
              <template v-if="shiftStatus.isOpen">
                {{ $t('master.shiftOpened') }} · {{ shiftStatus.startTime }}
              </template>
              <template v-else-if="shiftStatus.isScheduled">
                Смена запланирована (ожидание)
              </template>
              <template v-else>
                {{ $t('master.shiftClosed') }}
              </template>
            </div>
          </div>
        </div>
        <!-- Removed redundant org name as it is in the layout header now -->
      </div>
    </div>

    <!-- ── TILES GRID ── -->
    <main class="main-content">
      <div class="tiles-grid">
        <!-- Start Shift / Status Tile -->
        <div class="tile" 
             @click="!shiftStatus.isOpen && handleStartShift()"
             :class="{ 'tile--success': shiftStatus.isOpen }">
          <div class="tile-icon">{{ shiftStatus.isOpen ? '✅' : '🏢' }}</div>
          <div class="tile-label">{{ shiftStatus.isOpen ? $t('master.shiftOpened') : $t('master.startShift') }}</div>
          <div class="tile-value" :class="{ 'text-gold': !shiftStatus.isOpen, 'text-success': shiftStatus.isOpen }">
             {{ shiftStatus.isOpen ? shiftStatus.startTime : $t('common.start') }}
          </div>
          <div v-if="!shiftStatus.isOpen" class="tile-arrow">›</div>
        </div>

        <!-- Profile Tile -->
        <router-link to="/master/profile" class="tile">
          <div class="tile-icon">👤</div>
          <div class="tile-label">Профиль</div>
          <div class="tile-value">Настройки</div>
          <div class="tile-arrow">›</div>
        </router-link>

        <!-- Income Wide Tile -->
        <router-link to="/master/income" class="tile tile--wide">
          <div class="tile-flex">
             <div>
                <div class="tile-icon">💰</div>
                <div class="tile-label">Личный доход</div>
                <div class="tile-value text-gold">{{ Number(stats.total_income).toLocaleString() }} ₸</div>
                <div class="tile-hint">За текущую неделю</div>
             </div>
             <div class="tile-right">
                <div class="tile-label">Клиентов</div>
                <div class="tile-value">{{ stats.total_clients }}</div>
                <div class="tile-arrow-static">›</div>
             </div>
          </div>
        </router-link>

        <!-- Bookings Tile -->
        <router-link to="/master/bookings" class="tile tile--wide">
           <div class="tile-flex">
              <div>
                 <div class="tile-icon">📅</div>
                 <div class="tile-label">{{ $t('master.myAppointments') }}</div>
                 <div class="tile-value">Расписание</div>
              </div>
              <div class="tile-right">
                 <div class="tile-label">Записей</div>
                 <div class="tile-value">{{ appointmentsToday }}</div>
                 <div class="tile-arrow-static">›</div>
              </div>
           </div>
        </router-link>

        <!-- Become Client Tile -->
        <div class="tile tile--wide tile--client" @click="switchToClient">
           <div class="tile-flex">
              <div class="flex items-center gap-3">
                 <div class="tile-icon m-0">🔄</div>
                 <div>
                    <div class="tile-label m-0">Перейти в режим клиента</div>
                    <div class="tile-value text-sm opacity-70">Записаться на услуги</div>
                 </div>
              </div>
              <div class="tile-arrow-static">›</div>
           </div>
        </div>
      </div>

      <div class="gold-line"></div>
    </main>

    <!-- ── MODALS ── -->
    <div v-if="sheet.show" class="overlay" @click="sheet.status !== 'loading' && (sheet.show = false)">
      <div class="sheet" @click.stop>
        <div v-if="sheet.status === 'loading'">
          <div class="loading-spin"></div>
          <div class="sheet-title">{{ $t('master.geolocating') }}</div>
          <div class="sheet-sub">Проверяем ваше местоположение, пожалуйста подождите...</div>
        </div>

        <div v-if="sheet.status === 'success'">
          <div class="sheet-icon">✅</div>
          <div class="sheet-title">{{ $t('master.shiftOpened') }}</div>
          <div class="sheet-sub text-success">
            {{ $t('master.successStart') }}<br/>
            Время начала: <strong>{{ shiftStatus.startTime }}</strong>
          </div>
          <button class="btn-sheet" @click="sheet.show = false">Отлично, за работу!</button>
        </div>

        <div v-if="sheet.status === 'fail'">
          <div class="sheet-icon">📍</div>
          <div class="sheet-title">{{ $t('master.locationError') }}</div>
          <div class="sheet-sub">
            {{ $t('master.locationHint') }}<br/><br/>
            <span class="text-error" v-if="sheet.errorMsg">{{ sheet.errorMsg }}</span>
          </div>
          <div class="sheet-actions">
            <button class="btn-sheet" @click="handleStartShift">{{ $t('master.retry') }}</button>
            <button class="btn-sheet btn-sheet-ghost" @click="sheet.show = false">{{ $t('common.close') }}</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { Icon } from '@iconify/vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import api from '@/api'

const auth = useAuthStore()
const router = useRouter()

const shiftStatus = reactive({
  isScheduled: false,
  isOpen: false,
  startTime: ''
})

const stats = reactive({
  total_income: 0,
  total_clients: 0
})

const appointmentsToday = ref(0)

const sheet = reactive({
  show: false,
  status: 'loading',
  errorMsg: ''
})

const fetchStatus = async () => {
  try {
    const now = new Date()
    const offset = now.getTimezoneOffset()
    const localNow = new Date(now.getTime() - (offset * 60 * 1000))
    const today = localNow.toISOString().split('T')[0]
    const res = await api.get('/masters/shifts/', { params: { date: today } })
    if (res.data && res.data.length > 0) {
      const shift = res.data[0]
      shiftStatus.isScheduled = shift.is_open
      if (shift.actual_start) {
        shiftStatus.isOpen = true
        shiftStatus.startTime = new Date(shift.actual_start).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
    }
  } catch (e) {
    console.error('Fetch status error', e)
  }
}

const fetchStatsSummary = async () => {
  try {
    const res = await api.get('/appointments/master-stats/')
    stats.total_income = res.data.total_income
    stats.total_clients = res.data.total_clients
  } catch (e) {
    console.error('Fetch stats error', e)
  }
}

const fetchBookingsCount = async () => {
  try {
    const now = new Date()
    const offset = now.getTimezoneOffset()
    const localNow = new Date(now.getTime() - (offset * 60 * 1000))
    const today = localNow.toISOString().split('T')[0]
    const res = await api.get('/appointments/', { params: { my: 'true', date_from: today, date_to: today } })
    appointmentsToday.value = res.data.count !== undefined ? res.data.count : (res.data.length || 0)
  } catch (e) {
    console.error('Fetch bookings error', e)
  }
}

const handleStartShift = async () => {
  sheet.show = true
  sheet.status = 'loading'
  sheet.errorMsg = ''

  if (!navigator.geolocation) {
    sheet.status = 'fail'
    sheet.errorMsg = 'Геолокация не поддерживается вашим устройством.'
    return
  }

  navigator.geolocation.getCurrentPosition(
    async (pos) => {
      try {
        const { latitude, longitude } = pos.coords
        const res = await api.post('/masters/shifts/start/', { latitude, longitude })
        if (res.data.success) {
          shiftStatus.isOpen = true
          shiftStatus.startTime = new Date(res.data.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          sheet.status = 'success'
          fetchStatsSummary()
        }
      } catch (e) {
        sheet.status = 'fail'
        sheet.errorMsg = e.response?.data?.message || 'Ошибка сервера при запуске смены.'
      }
    },
    (err) => {
      sheet.status = 'fail'
      sheet.errorMsg = 'Не удалось получить доступ к местоположению. Пожалуйста, разрешите доступ в настройках.'
    },
    { timeout: 10000 }
  )
}

const switchToClient = () => {
  auth.setRoleMode('client')
  router.push('/')
}

onMounted(() => {
  fetchStatus()
  fetchStatsSummary()
  fetchBookingsCount()
})
</script>

<style scoped>
.master-home {
  padding: 16px;
  min-height: 100vh;
}

.hdr {
  padding: 24px 0;
  border-bottom: 2px solid var(--border);
  margin-bottom: 24px;
}
.hdr-row { display: flex; justify-content: space-between; align-items: center; }
.hdr-left { display: flex; align-items: center; gap: 16px; }
.avatar { 
  width: 56px; height: 56px; border-radius: 50%; background: var(--bg-secondary);
  border: 2px solid var(--gold); display: flex; align-items: center; justify-content: center;
  overflow: hidden; box-shadow: 0 4px 10px var(--gold-glow);
}
.avatar img { width: 100%; height: 100%; object-fit: cover; }
.hdr-sub { font-size: 10px; color: var(--gold); text-transform: uppercase; font-weight: 800; letter-spacing: 1.5px; margin-bottom: 2px; }
.hdr-name { font-family: var(--font-header); font-size: 22px; font-weight: 700; color: var(--text); }
.hdr-status { font-size: 11px; color: var(--muted); display: flex; align-items: center; gap: 6px; margin-top: 4px; font-weight: 600; }
.hdr-status.open { color: #4caf7d; }
.status-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--muted); transition: all 0.3s; }
.status-dot.open { background: #4caf7d; box-shadow: 0 0 8px #4caf7d; }

.org-name { font-size: 12px; color: var(--muted); font-weight: 500; }

.tiles-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.tile { 
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: var(--radius); padding: 20px 16px; position: relative; 
  text-decoration: none; color: inherit; transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex; flex-direction: column;
}
.tile:active { transform: scale(0.97); background: var(--border); }
.tile--success { border-color: rgba(76, 175, 125, 0.5); }
.tile--wide { grid-column: 1 / -1; }
.tile--client { background: var(--gold-glow); border-color: var(--gold); }
.tile--client .tile-icon { font-size: 20px; }
.m-0 { margin: 0 !important; }
.gap-3 { gap: 12px; }

.tile-icon { font-size: 28px; margin-bottom: 12px; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1)); }
.tile-label { font-size: 10px; color: var(--muted); text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px; margin-bottom: 6px; }
.tile-value { font-family: var(--font-header); font-size: 20px; font-weight: 700; }
.tile-arrow { position: absolute; right: 16px; top: 16px; color: var(--muted); opacity: 0.5; font-size: 20px; }
.tile-flex { display: flex; justify-content: space-between; align-items: flex-end; width: 100%; }
.tile-hint { font-size: 11px; color: var(--muted); margin-top: 6px; font-weight: 500; }
.tile-right { text-align: right; }
.tile-arrow-static { font-size: 22px; color: var(--gold); margin-bottom: -4px; }

.text-gold { color: var(--gold); }
.text-success { color: #4caf7d; }
.text-error { color: #e05252; font-size: 12px; font-weight: 500; }

/* Modal & Sheet (Enhanced) */
.overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.6); backdrop-filter: blur(4px); z-index: 500; display: flex; align-items: flex-end; }
.sheet { 
  background: var(--bg); width: 100%; border-radius: 24px 24px 0 0; 
  padding: 32px 20px 48px; text-align: center; border-top: 1px solid var(--border);
  box-shadow: 0 -10px 40px rgba(0,0,0,0.2);
}
.sheet-icon { font-size: 56px; margin-bottom: 20px; }
.sheet-title { font-family: var(--font-header); font-size: 24px; font-weight: 700; margin-bottom: 12px; }
.sheet-sub { font-size: 15px; color: var(--muted); line-height: 1.6; padding: 0 10px; }
.btn-sheet { 
  width: 100%; background: var(--gold-gradient); color: #000; border: none; padding: 16px; 
  border-radius: var(--radius-sm); font-weight: 700; font-size: 16px; margin-top: 32px;
  box-shadow: 0 4px 15px var(--gold-glow);
}
.btn-sheet-ghost { background: var(--bg-secondary); border: 1px solid var(--border); color: var(--text); margin-top: 12px; box-shadow: none; }
</style>


