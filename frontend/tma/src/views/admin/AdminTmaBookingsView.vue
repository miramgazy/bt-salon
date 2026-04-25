<template>
  <div class="admin-bookings">
    <div class="page-header">
      <h1 class="page-title">Записи салона</h1>
      <button class="add-btn" @click="checkAndOpenModal">
        <Icon icon="mdi:plus" width="24" />
      </button>
    </div>
    
    <div class="date-selector">
      <button 
        :class="['date-pill', { active: activeTab === 'today' }]" 
        @click="setDate('today')"
      >Сегодня</button>
      <button 
        :class="['date-pill', { active: activeTab === 'tomorrow' }]" 
        @click="setDate('tomorrow')"
      >Завтра</button>
      <div :class="['date-pill custom-date-wrapper', { active: activeTab === 'custom' }]">
         <Icon icon="mdi:calendar-month-outline" width="16" />
         <input type="date" v-model="selectedDate" class="date-input-hidden" @change="activeTab = 'custom'" />
         <span>{{ activeTab === 'custom' ? formatDateShort(selectedDate) : 'Выбрать' }}</span>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
       <div class="spinner"></div>
    </div>

    <div v-else-if="appointments.length === 0" class="empty-state">
       <div class="empty-icon">📅</div>
       <p>Нет записей на выбранную дату</p>
    </div>

    <div v-else class="bookings-list">
       <div v-for="apt in appointments" :key="apt.id" class="booking-card" @click="openActions(apt)">
          <div class="booking-time">
             <div class="time-main">{{ formatStartTime(apt.start_time) }}</div>
             <div class="time-duration">{{ getDuration(apt.start_time, apt.end_time) }} мин</div>
          </div>
          <div class="booking-info">
             <div class="client-name">{{ apt.client_detail?.full_name || 'Оффлайн клиент' }} <span v-if="apt.client_detail?.phone" class="client-phone">{{ apt.client_detail.phone }}</span></div>
             <div class="service-name text-gold">{{ apt.service_detail?.name || 'Услуга' }} ({{ apt.master_detail?.first_name || 'Мастер' }})</div>
             <div v-if="apt.notes" class="booking-notes">
                <Icon icon="mdi:note-text-outline" width="14" />
                <span>{{ apt.notes }}</span>
             </div>
          </div>
          <div class="booking-status">
             <span :class="['status-badge', apt.status.toLowerCase()]">{{ getStatusText(apt.status) }}</span>
          </div>
       </div>
    </div>

    <!-- Actions Modal (Bottom Sheet) -->
    <div v-if="activeApt" class="overlay" @click="activeApt = null">
      <div class="sheet" @click.stop>
        <div class="sheet-title mb-4">Управление записью #{{ activeApt.id }}</div>
        
        <div v-if="!showCancelPrompt">
          <button v-if="activeApt.status === 'pending' || activeApt.status === 'confirmed'" class="btn-sheet" @click="markAsDone">Завершить (Услуга оказана)</button>
          <button v-if="activeApt.status === 'pending'" class="btn-sheet bg-secondary mt-2" @click="confirmApt">Подтвердить</button>
          <button v-if="activeApt.status !== 'cancelled' && activeApt.status !== 'done'" class="btn-sheet bg-danger mt-2" @click="showCancelPrompt = true">Отменить</button>
          <button class="btn-sheet btn-sheet-ghost mt-4" @click="activeApt = null">Закрыть</button>
        </div>
        
        <div v-else>
          <div class="mb-4">
            <label class="form-label">Причина отмены (обязательно)</label>
            <textarea v-model="cancelReason" class="form-input" rows="3" placeholder="Укажите причину"></textarea>
          </div>
          <button class="btn-sheet bg-danger" :disabled="!cancelReason.trim()" @click="cancelApt">Подтвердить отмену</button>
          <button class="btn-sheet btn-sheet-ghost mt-2" @click="showCancelPrompt = false">Назад</button>
        </div>
      </div>
    </div>

    <!-- Create Appointment Modal -->
    <div v-if="showCreateModal" class="overlay" @click="showCreateModal = false">
      <div class="sheet h-80vh" @click.stop>
        <div class="sheet-title flex justify-between">
            <span>Новая запись (Шаг {{ creationStep }}/4)</span>
            <Icon icon="mdi:close" width="24" @click="showCreateModal = false" class="cursor-pointer" />
        </div>
        
        <div class="mt-4 flex flex-col gap-4 overflow-y-auto pb-6" style="flex: 1">
          <!-- Step 1: Services -->
          <div v-if="creationStep === 1">
             <label class="form-label mb-2">Выберите услугу</label>
             
             <div class="category-scroll mb-5">
                 <button 
                    :class="['date-pill', 'flex-shrink-0', { active: selectedCategory === 'all' }]"
                    @click="selectedCategory = 'all'"
                 >Все</button>
                 <button 
                    v-for="cat in categoriesList" :key="cat.id"
                    :class="['date-pill', 'flex-shrink-0', { active: selectedCategory === cat.id }]"
                    @click="selectedCategory = cat.id"
                 >{{ cat.name }}</button>
             </div>

             <div class="flex flex-col gap-3 mt-2">
                 <div v-for="srv in filteredServicesList" :key="srv.id" 
                      class="service-card"
                      :class="{ selected: form.service_id === srv.id }"
                      @click="form.service_id = srv.id; currentServiceDuration = srv.duration; creationStep = 2">
                    <div>
                        <div class="font-medium">{{ srv.name }}</div>
                        <div class="text-xs text-muted">{{ srv.duration }} мин</div>
                    </div>
                    <div class="font-bold text-gold">{{ srv.price }} ₸</div>
                 </div>
             </div>
          </div>

          <!-- Step 2: Masters -->
          <div v-if="creationStep === 2">
             <label class="form-label mb-2">Выберите мастера</label>
             <div class="flex flex-col gap-2">
                 <div v-for="m in filteredWorkingMasters" :key="m.id"
                      class="master-card"
                      @click="selectMaster(m.id)">
                     <div class="font-medium flex items-center gap-2">
                         <div class="emp-avatar-sm">
                             <img v-if="m.photo_url" :src="m.photo_url" alt="" />
                             <span v-else>👤</span>
                         </div>
                         {{ m.first_name }} {{ m.last_name }}
                     </div>
                 </div>
                 <div v-if="filteredWorkingMasters.length === 0" class="text-muted text-sm text-center py-4">
                     Нет мастеров, оказывающих эту услугу сегодня.
                 </div>
             </div>
             <button class="btn-sheet bg-secondary mt-4" @click="creationStep = 1">Назад</button>
          </div>

          <!-- Step 3: Slots -->
          <div v-if="creationStep === 3">
             <label class="form-label mb-2">Выберите время на {{ formatDateShort(selectedDate) }}</label>
             <div v-if="slotsLoading" class="spinner"></div>
             <div v-else-if="slots.length === 0" class="text-muted text-center py-4">
                 Доступных окон для этой услуги больше нет.
             </div>
             <div v-else class="slots-grid">
                 <div v-for="slot in slots" :key="slot.time"
                      class="slot-item"
                      :class="{ disabled: !slot.is_available, selected: form.time === slot.time }"
                      @click="if (slot.is_available) { form.time = slot.time; creationStep = 4 }">
                     {{ slot.time }}
                 </div>
             </div>
             <button class="btn-sheet bg-secondary mt-4" @click="creationStep = 2">Назад</button>
          </div>

          <!-- Step 4: Client Info -->
          <div v-if="creationStep === 4">
             <form @submit.prevent="createAppointment" class="flex flex-col gap-4">
                 <div>
                    <label class="form-label">Имя клиента <span class="text-error">*</span></label>
                    <input v-model="form.client_name" type="text" class="form-input" required autofocus />
                 </div>
                 <div>
                    <label class="form-label">Телефон клиента <span class="text-error">*</span></label>
                    <input v-model="form.client_phone" type="text" class="form-input" required placeholder="+7 (___) ___-__-__" />
                 </div>
                 <div>
                    <label class="form-label">Заметки</label>
                    <textarea v-model="form.notes" class="form-input" rows="2"></textarea>
                 </div>
                 <div class="p-3 bg-secondary rounded-xl text-sm mb-2 opacity-80">
                    <div><b>Услуга:</b> Услуга на {{ currentServiceDuration }} мин</div>
                    <div><b>Время:</b> {{ formatDateShort(selectedDate) }}, {{ form.time }}</div>
                 </div>
                 <button type="submit" class="btn-sheet mt-2" :disabled="creating">
                    {{ creating ? 'Создание...' : 'Создать запись' }}
                 </button>
             </form>
             <button class="btn-sheet btn-sheet-ghost mt-2" @click="creationStep = 3">Назад</button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { Icon } from '@iconify/vue'
import api from '@/api'

const activeTab = ref('today')
const selectedDate = ref(new Date().toISOString().split('T')[0])
const appointments = ref([])
const loading = ref(false)

const activeApt = ref(null)
const showCancelPrompt = ref(false)
const cancelReason = ref('')

const showCreateModal = ref(false)
const creating = ref(false)
const creationStep = ref(1)

const workingMasters = ref([])
const servicesList = ref([])
const categoriesList = ref([])
const selectedCategory = ref('all')
const slots = ref([])
const slotsLoading = ref(false)
const currentServiceDuration = ref(0)

const form = ref({
    client_name: '',
    client_phone: '',
    master_id: '',
    service_id: '',
    date: selectedDate.value,
    time: '',
    notes: ''
})

const filteredWorkingMasters = computed(() => {
    return workingMasters.value.filter(m => 
        m.services?.includes(form.value.service_id) || 
        m.services_detail?.some(s => s.id === form.value.service_id)
    )
})

const filteredServicesList = computed(() => {
    if (selectedCategory.value === 'all') return servicesList.value
    return servicesList.value.filter(s => s.category === selectedCategory.value)
})

const getStatusText = (status) => {
    const map = {
        'pending': 'Ожидает',
        'confirmed': 'Подтверждено',
        'done': 'Завершено',
        'cancelled': 'Отменено'
    }
    return map[status?.toLowerCase()] || status
}

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

const selectMaster = async (masterId) => {
    form.value.master_id = masterId
    creationStep.value = 3
    
    // Fetch Slots
    slotsLoading.value = true
    slots.value = []
    try {
        const res = await api.get(`/masters/${masterId}/available-slots/`, {
            params: {
                date: selectedDate.value,
                service_id: form.value.service_id
            }
        })
        slots.value = res.data
    } catch (e) {
        console.error('Slots error', e)
    } finally {
        slotsLoading.value = false
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

const openActions = (apt) => {
    activeApt.value = apt
    showCancelPrompt.value = false
    cancelReason.value = ''
}

const confirmApt = async () => {
    if (!activeApt.value) return
    try {
        await api.post(`/appointments/${activeApt.value.id}/confirm/`)
        activeApt.value = null
        fetchAppointments()
    } catch (e) { alert('Ошибка!') }
}

const markAsDone = async () => {
    if (!activeApt.value) return
    try {
        await api.post(`/appointments/${activeApt.value.id}/done/`)
        activeApt.value = null
        fetchAppointments()
    } catch (e) { alert('Ошибка!') }
}

const cancelApt = async () => {
    if (!activeApt.value || !cancelReason.value.trim()) return
    try {
        await api.post(`/appointments/${activeApt.value.id}/cancel/`, {
            cancellation_reason: cancelReason.value
        })
        activeApt.value = null
        fetchAppointments()
    } catch (e) { alert('Ошибка!') }
}

const checkAndOpenModal = async () => {
    try {
        const res = await api.get('/masters/working/', { params: { date: selectedDate.value } })
        workingMasters.value = res.data
        if (workingMasters.value.length === 0) {
            alert('На выбранную дату нет мастеров с открытой сменой! Сначала откройте смену в разделе "Сотрудники".')
            return
        }
        
        // Fetch services and categories
        const [sRes, cRes] = await Promise.all([
            api.get('/services/'),
            api.get('/categories/')
        ])
        servicesList.value = sRes.data.results || sRes.data
        categoriesList.value = cRes.data.results || cRes.data

        form.value = {
            client_name: '', client_phone: '', master_id: '', service_id: '',
            date: selectedDate.value, time: '', notes: ''
        }
        selectedCategory.value = 'all'
        creationStep.value = 1
        showCreateModal.value = true
    } catch (e) {
        alert('Ошибка при загрузке данных')
    }
}

const createAppointment = async () => {
    creating.value = true
    try {
        const start_time = new Date(`${selectedDate.value}T${form.value.time}:00`).toISOString()
        const duration = currentServiceDuration.value || auth.organizationSettings?.slot_duration || 30
        const end_time = new Date(new Date(start_time).getTime() + duration * 60000).toISOString()
        
        await api.post('/appointments/', {
            master: form.value.master_id,
            service: form.value.service_id,
            start_time,
            end_time,
            notes: form.value.notes,
            client_name: form.value.client_name,
            client_phone: form.value.client_phone
        })
        
        showCreateModal.value = false
        fetchAppointments()
    } catch (e) {
        alert(e.response?.data?.error || e.message || 'Ошибка создания записи')
    } finally {
        creating.value = false
    }
}

watch(selectedDate, () => {
  fetchAppointments()
})

onMounted(() => {
  fetchAppointments()
})
</script>

<style scoped>
.admin-bookings {
  padding: calc(var(--tg-safe-top, 0px) + 20px) 16px 100px;
  transition: padding-top 0.3s ease;
}
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-title { font-size: 24px; font-weight: 800; color: var(--text); }
.add-btn { background: var(--gold-gradient); border: none; border-radius: 50%; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; color: #fff; cursor: pointer; box-shadow: 0 4px 10px var(--gold-glow); }

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
  top: 0; left: 0; width: 100%; height: 100%;
  opacity: 0; cursor: pointer;
}

.empty-state {
  text-align: center; padding: 40px 20px; color: var(--muted);
}
.empty-icon { font-size: 48px; margin-bottom: 10px; filter: grayscale(1) opacity(0.5); }

.spinner {
  width: 32px; height: 32px;
  border: 3px solid var(--border);
  border-top-color: var(--gold);
  border-radius: 50%;
  animation: spin 1s infinite linear;
  margin: 40px auto;
}
@keyframes spin { to { transform: rotate(360deg); } }

.booking-card {
  background: var(--bg-secondary);
  border-radius: 16px;
  padding: 16px;
  margin-bottom: 12px;
  display: flex;
  gap: 16px;
  border: 1px solid var(--border);
  cursor: pointer;
}
.booking-time {
  text-align: right;
  min-width: 60px;
}
.time-main { font-size: 16px; font-weight: 700; color: var(--text); }
.time-duration { font-size: 11px; color: var(--muted); margin-top: 2px; }

.booking-info {
  flex: 1;
}
.client-name { font-size: 15px; font-weight: 600; color: var(--text); margin-bottom: 2px; }
.client-phone { font-size: 11px; color: var(--muted); margin-left: 4px; font-weight: 400; }
.service-name { font-size: 13px; font-weight: 500; }
.booking-notes {
  display: flex; align-items: flex-start; gap: 4px; margin-top: 6px; font-size: 11px; color: var(--muted);
}
.text-gold { color: var(--gold); }

.booking-status {
  display: flex;
  align-items: flex-start;
}
.status-badge {
  font-size: 10px; font-weight: 700; text-transform: uppercase; padding: 4px 8px; border-radius: 12px;
}
.status-badge.pending { background: #fef08a; color: #854d0e; }
.status-badge.confirmed { background: var(--gold-glow); color: var(--gold); border: 1px solid var(--gold); }
.status-badge.done { background: #dcfce7; color: #166534; }
.status-badge.cancelled { background: #fee2e2; color: #991b1b; }

.overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 1000;
  display: flex; align-items: flex-end; justify-content: center; backdrop-filter: blur(2px);
}
.sheet {
  background: var(--tg-bg); width: 100%; border-radius: 24px 24px 0 0; padding: 24px;
  box-shadow: 0 -10px 40px rgba(0,0,0,0.2); animation: slideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
.h-80vh { max-height: 85vh; display: flex; flex-direction: column; overflow: hidden; }
@keyframes slideUp { from { transform: translateY(100%); } to { transform: translateY(0); } }

.sheet-title { font-size: 20px; font-weight: 800; color: var(--text); }
.btn-sheet {
  display: block; width: 100%; background: var(--gold-gradient); color: #fff;
  border: none; padding: 16px; border-radius: 16px; font-size: 16px; font-weight: 700; cursor: pointer;
}
.btn-action:active {
    opacity: 0.7;
}

.category-scroll {
    display: flex;
    overflow-x: auto;
    gap: 8px;
    scrollbar-width: none; /* Firefox */
}
.category-scroll::-webkit-scrollbar {
    display: none; /* Chrome/Safari */
}

.btn-sheet.bg-secondary { background: var(--border); color: var(--text); }
.btn-sheet.bg-danger { background: #fee2e2; color: #dc2626; border: 1px solid #f87171; }
.btn-sheet-ghost { background: transparent; color: var(--muted); border: 1px solid var(--border); }

.form-label { display: block; font-size: 13px; font-weight: 600; color: var(--muted); margin-bottom: 6px; }
.form-input {
  width: 100%; padding: 12px 14px; border-radius: 12px; border: 1px solid var(--border);
  background: var(--bg-secondary); color: var(--text); font-size: 15px; outline: none;
  font-family: inherit;
}
.form-input:focus { border-color: var(--gold); }
.text-error { color: #dc2626; }

/* Custom UI Elements for Modal */
.service-card {
  padding: 12px 16px; border-radius: 12px; border: 1px solid var(--border);
  background: var(--bg-secondary); cursor: pointer; display: flex; justify-content: space-between;
  align-items: center; transition: all 0.2s;
}
.service-card:active { background: var(--bg); }
.service-card.selected { border-color: var(--gold); background: var(--gold-glow); }

.master-card {
  padding: 12px 16px; border-radius: 12px; border: 1px solid var(--border);
  background: var(--bg-secondary); cursor: pointer; transition: all 0.2s;
}
.master-card:active { background: var(--bg); }
.emp-avatar-sm {
  width: 28px; height: 28px; border-radius: 50%; background: var(--bg);
  display: flex; align-items: center; justify-content: center; overflow: hidden;
  border: 1px solid var(--border); font-size: 14px;
}
.emp-avatar-sm img { width: 100%; height: 100%; object-fit: cover; }

.slot-item {
  padding: 12px 0; border-radius: 12px; border: 1px solid var(--border);
  text-align: center; font-size: 14px; font-weight: 600; cursor: pointer;
  background: var(--bg-secondary); transition: all 0.2s;
}
.slot-item.disabled { opacity: 0.3; cursor: not-allowed; text-decoration: line-through; }
.slot-item.selected { background: var(--gold-gradient); color: #000; border-color: var(--gold); }

.slots-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
    max-height: 300px;
    overflow-y: auto;
    padding-right: 4px;
}
.slots-grid::-webkit-scrollbar {
    width: 4px;
}
.slots-grid::-webkit-scrollbar-thumb {
    background: var(--border);
    border-radius: 4px;
}
</style>
