<template>
  <div class="admin-masters">
    <div class="page-header flex-between mb-4">
      <h1 class="page-title">{{ $t('admin.mastersTitle') }}</h1>
      <button class="add-btn" @click="openCreateModal">
        <Icon icon="mdi:plus" width="24" />
      </button>
    </div>
    
    <div v-if="loading" class="loading-state">
       <div class="spinner"></div>
    </div>

     <div v-else-if="employees.length === 0" class="empty-state">
        <div class="empty-icon">👥</div>
        <p>{{ $t('admin.noEmployees') }}</p>
     </div>

    <div v-else class="employees-list">
       <div v-for="emp in employees" :key="emp.id" class="employee-card">
          <div class="emp-header">
             <div class="emp-avatar">
               <img v-if="emp.photo_url" :src="emp.photo_url" alt="avatar" />
               <span v-else>👤</span>
             </div>
             
             <div class="emp-info">
                 <div class="emp-name">{{ emp.first_name }} {{ emp.last_name }}</div>
                 <div class="emp-role">
                   <span class="role-badge" :class="emp.role === 'admin' ? 'admin' : 'master'">
                     {{ emp.role === 'admin' ? $t('admin.adminRole') : $t('admin.masterRole') }}
                   </span>
                 </div>
                 <div class="emp-phone" v-if="emp.phone">{{ emp.phone }}</div>
             </div>
             
             <div class="emp-edit-col">
                  <div v-if="emp.role === 'master'" class="shift-indicators">
                      <Icon 
                          :icon="emp.today_shift?.opened_by_admin ? 'mdi:check-circle' : 'mdi:check-circle-outline'" 
                          class="indicator-icon"
                          :class="{ 'admin-active': emp.today_shift?.is_open && emp.today_shift?.opened_by_admin }"
                      />
                      <Icon 
                          :icon="emp.today_shift?.actual_start ? 'mdi:check-circle' : 'mdi:check-circle-outline'" 
                          class="indicator-icon"
                          :class="{ 'master-active': emp.today_shift?.is_open && emp.today_shift?.actual_start }"
                      />
                  </div>
                  <button v-if="emp.role === 'master'" class="edit-icon-btn" @click="handleEditClick(emp)">
                      <Icon icon="mdi:pencil-outline" width="22" />
                  </button>
              </div>
          </div>
          
          <div class="emp-actions mt-3" v-if="emp.role === 'master'">
                <div class="master-btns-row">
                     <button class="btn-action btn-smena" @click="handleSmenaClick(emp)">
                         <Icon icon="mdi:calendar-check" width="16" />
                         {{ $t('admin.shift') }}
                     </button>
                     <button class="btn-action btn-zapis" @click="handleZapisClick(emp)">
                         <Icon icon="mdi:calendar-plus" width="16" />
                         {{ $t('admin.booking') }}
                     </button>
                </div>
          </div>
       </div>
    </div>

    <!-- Employee Modal (Bottom Sheet - Create/Edit) -->
    <div v-if="showCreateModal" class="overlay" @click="showCreateModal = false">
      <div class="sheet h-80vh" @click.stop>
         <div class="sheet-title flex justify-between">
            <span>{{ isEditing ? $t('admin.editMaster') : $t('admin.addMaster') }}</span>
            <Icon icon="mdi:close" width="24" @click="showCreateModal = false" class="cursor-pointer" />
         </div>
        
        <form @submit.prevent="submitEmployee" class="mt-4 flex flex-col gap-4 overflow-y-auto pb-6">
          <p v-if="!isEditing" class="text-xs text-muted text-center uppercase tracking-wider font-bold">{{ $t('admin.addMasterTitle') }}</p>
          <div>
            <label class="form-label">{{ $t('admin.firstName') }} <span class="text-error">*</span></label>
            <input v-model="form.first_name" type="text" class="form-input" required />
          </div>
          <div>
            <label class="form-label">{{ $t('admin.lastName') }}</label>
            <input v-model="form.last_name" type="text" class="form-input" />
          </div>
          <div>
            <label class="form-label">{{ $t('admin.phone') }} <span class="text-error">*</span></label>
            <input v-model="form.phone" type="text" class="form-input" placeholder="+7 (___) ___-__-__" required />
          </div>
          <div>
            <label class="form-label flex gap-1 items-center">
                {{ $t('admin.telegramId') }}
                <span class="text-[10px] text-gold uppercase font-bold">(!)</span>
            </label>
            <div v-if="!isEditing" class="p-2.5 rounded-xl bg-gold/10 border border-gold/20 mb-2 flex items-start gap-2">
                <Icon icon="mdi:information-outline" width="16" class="text-gold flex-shrink-0 mt-0.5" />
                <span class="text-[11px] leading-tight text-gold font-medium">{{ $t('admin.telegramIdHint') }}</span>
            </div>
            <input v-model="form.telegram_id" type="number" class="form-input" :class="{ 'border-gold/50 bg-gold/5': !isEditing && !form.telegram_id }" :placeholder="$t('admin.telegramIdPlaceholder')" />
          </div>
          <div>
            <label class="form-label">{{ $t('admin.masterServices') }}</label>
            <div v-if="servicesList.length === 0" class="text-sm text-muted">{{ $t('admin.noServicesInSalon') }}</div>
            <div class="flex flex-col gap-2 mt-2">
                <label v-for="srv in servicesList" :key="srv.id" class="flex items-center gap-3 bg-secondary p-3 rounded-xl border border-[var(--border)] cursor-pointer">
                    <input type="checkbox" :value="srv.id" v-model="form.services" class="w-5 h-5 accent-gold border-gray-300 rounded focus:ring-gold" />
                    <div>
                        <div class="text-sm font-semibold">{{ srv.name }}</div>
                        <div class="text-xs text-muted font-mono">{{ srv.duration }} {{ $t('common.min') }} • {{ srv.price }} ₸</div>
                    </div>
                </label>
            </div>
          </div>
          
           <button type="submit" class="btn-sheet mt-4" :disabled="creating">
              {{ creating ? $t('common.saving') : $t('common.save') }}
           </button>
        </form>
      </div>
    </div>

    <!-- Open Shift Modal (Bottom Sheet) -->
    <div v-if="showShiftModal" class="overlay" @click="showShiftModal = false">
      <div class="sheet" @click.stop>
         <div class="sheet-title flex justify-between">
            <span>{{ $t('admin.openShift') }}</span>
            <Icon icon="mdi:close" width="24" @click="showShiftModal = false" class="cursor-pointer" />
         </div>
        
        <form @submit.prevent="submitShift" class="mt-4 flex flex-col gap-4 pb-6">
          <p class="text-sm font-medium">{{ $t('admin.masterRole') }}: <b>{{ activeMaster?.first_name }}</b></p>
          <div>
            <label class="form-label">{{ $t('shift.date') }} <span class="text-error">*</span></label>
            <div class="date-selector mb-4">
                <button 
                   type="button"
                   :class="['date-pill', { active: isToday(shiftForm.date) }]" 
                   @click="shiftForm.date = getLocalDateStr()"
                >{{ $t('master.today') }}</button>
                <button 
                   type="button"
                   :class="['date-pill', { active: isTomorrow(shiftForm.date) }]" 
                   @click="shiftForm.date = getLocalDateStrTomorrow()"
                >{{ $t('master.tomorrow') }}</button>
                <div class="custom-date-wrapper">
                   <button type="button" :class="['date-pill', { active: isCustomDate(shiftForm.date) }]">
                       {{ isCustomDate(shiftForm.date) ? formatDateShort(shiftForm.date) : $t('master.selectDate') }}
                   </button>
                   <input type="date" class="date-input-hidden" v-model="shiftForm.date" />
                </div>
            </div>
          </div>
          
           <button type="submit" class="btn-sheet mt-2" :disabled="creatingShift">
              {{ creatingShift ? $t('common.saving') : $t('common.continue') }}
           </button>
        </form>
      </div>
    </div>

    <!-- Booking Modal (Special Workflow) -->
    <div v-if="showBookingModal" class="overlay" @click="showBookingModal = false">
      <div class="sheet h-80vh" @click.stop>
         <div class="sheet-title flex justify-between">
            <span>{{ $t('admin.booking') }}: {{ $t('admin.step') }} {{ bookingStep }}/4</span>
            <Icon icon="mdi:close" width="24" @click="showBookingModal = false" class="cursor-pointer" />
         </div>
        
         <div class="mt-4 flex flex-col gap-4 overflow-y-auto pb-6" style="flex: 1">
           <div class="p-3 bg-secondary rounded-xl text-sm mb-1">
              <b>{{ $t('admin.masterRole') }}:</b> {{ activeMaster?.first_name }} {{ activeMaster?.last_name }}
           </div>

           <div v-if="bookingStep === 0">
              <label class="form-label mb-3">{{ $t('master.selectDate') }}</label>
              <div class="date-selector mb-4">
                  <button 
                     :class="['date-pill', { active: isToday(bookingDate) }]" 
                     @click="setBookingDate('today')"
                  >{{ $t('master.today') }}</button>
                  <button 
                     :class="['date-pill', { active: isTomorrow(bookingDate) }]" 
                     @click="setBookingDate('tomorrow')"
                  >{{ $t('master.tomorrow') }}</button>
                  <div class="custom-date-wrapper">
                     <button :class="['date-pill', { active: isCustomDate(bookingDate) }]">
                         {{ isCustomDate(bookingDate) ? formatDateShort(bookingDate) : $t('master.selectDate') }}
                     </button>
                     <input type="date" class="date-input-hidden" @change="onCustomDateChange" />
                  </div>
              </div>
              <button class="btn-sheet" @click="bookingStep = 1">{{ $t('common.continue') }}</button>
           </div>

           <div v-if="bookingStep === 1">
              <div class="p-3 mb-2 bg-[var(--gold-glow)] border border-[var(--gold)] rounded-xl text-sm flex justify-between items-center">
                 <span><b>{{ $t('shift.date') }}:</b> {{ formatDateShort(bookingDate) }}</span>
                 <span class="text-gold cursor-pointer font-bold" @click="bookingStep = 0">{{ $t('common.change') }}</span>
              </div>
              <label class="form-label mb-2">{{ $t('admin.selectService') }}</label>
               <div class="category-scroll mb-5">
                  <button 
                     :class="['date-pill', 'flex-shrink-0', { active: selectedCategory === 'all' }]"
                     @click="selectedCategory = 'all'"
                  >{{ $t('admin.allCategories') }}</button>
                 <button 
                    v-for="cat in categoriesList" :key="cat.id"
                    :class="['date-pill', 'flex-shrink-0', { active: selectedCategory === cat.id }]"
                    @click="selectedCategory = cat.id"
                 >{{ cat.name }}</button>
             </div>

             <div class="flex flex-col gap-3">
                 <div v-for="srv in filteredServices" :key="srv.id" 
                      class="service-card"
                      @click="selectService(srv)">
                    <div>
                        <div class="font-bold text-base">{{ srv.name }}</div>
                        <div class="text-xs text-muted">{{ srv.duration_minutes }} {{ $t('common.min') }}</div>
                    </div>
                    <div class="font-bold text-gold text-lg">{{ srv.total_price }} ₸</div>
                 </div>
                 <div v-if="filteredServices.length === 0" class="text-center py-4 text-muted">
                    {{ $t('admin.masterNoServicesInCategory') }}
                 </div>
             </div>
          </div>

           <div v-if="bookingStep === 3">
              <div class="p-3 bg-secondary rounded-xl text-sm mb-2 opacity-80"><b>{{ $t('services.title') }}:</b> {{ selectedService?.name }}</div>
              <label class="form-label mb-2">{{ $t('admin.selectTime', { date: $t('master.today') }) }}</label>
              <div v-if="slotsLoading" class="spinner"></div>
              <div v-else-if="slots.length === 0" class="text-muted text-center py-4">
                  {{ $t('admin.noSlots') }}
              </div>
             <div v-else class="slots-grid">
                 <div v-for="slot in slots" :key="slot.time"
                      class="slot-item"
                      :class="{ disabled: !slot.is_available, selected: bookingForm.time === slot.time }"
                      @click="if (slot.is_available) { bookingForm.time = slot.time; bookingStep = 4 }">
                     {{ slot.time }}
                 </div>
             </div>
             <button class="btn-sheet bg-secondary mt-4" @click="bookingStep = 1">{{ $t('common.back') }}</button>
          </div>

           <div v-if="bookingStep === 4">
              <form @submit.prevent="createAppointment" class="flex flex-col gap-4">
                  <div>
                     <label class="form-label">{{ $t('admin.clientName') }} *</label>
                     <input v-model="bookingForm.client_name" type="text" class="form-input" required autofocus />
                  </div>
                  <div>
                     <label class="form-label">{{ $t('admin.clientPhone') }} *</label>
                     <input v-model="bookingForm.client_phone" type="text" class="form-input" required placeholder="+7 (___) ___-__-__" />
                  </div>
                  <div class="p-3 bg-secondary rounded-xl text-sm mb-2 opacity-80">
                     <div><b>{{ $t('common.time') }}:</b> {{ formatDateShort(bookingDate) }}, {{ bookingForm.time }}</div>
                  </div>
                  <button type="submit" class="btn-sheet mt-2" :disabled="bookingLoading">
                     {{ bookingLoading ? $t('common.saving') : $t('admin.createBooking') }}
                  </button>
              </form>
              <button class="btn-sheet btn-sheet-ghost mt-2" @click="bookingStep = 3">{{ $t('common.back') }}</button>
           </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { Icon } from '@iconify/vue'
import { useI18n } from 'vue-i18n'
import api from '@/api'

const { t, locale } = useI18n()
const employees = ref([])
const loading = ref(false)

// Helper functions (defined before use)
const getLocalDateStr = () => {
    const tzOffset = new Date().getTimezoneOffset()
    return new Date(new Date().getTime() - (tzOffset * 60 * 1000)).toISOString().split('T')[0]
}

const getLocalDateStrTomorrow = () => {
    const tom = new Date()
    const tzOffset = tom.getTimezoneOffset()
    tom.setDate(tom.getDate() + 1)
    return new Date(tom.getTime() - (tzOffset * 60 * 1000)).toISOString().split('T')[0]
}

const isToday = (d) => d === getLocalDateStr()
const isTomorrow = (d) => {
    const tom = new Date()
    tom.setDate(tom.getDate() + 1)
    return d === tom.toISOString().split('T')[0]
}
const isCustomDate = (d) => !isToday(d) && !isTomorrow(d)

const formatDateShort = (d) => {
    if (!d) return ''
    const currentLocale = locale.value === 'kz' ? 'kk-KZ' : 'ru-RU'
    return new Date(d).toLocaleDateString(currentLocale, { day: 'numeric', month: 'short' })
}

const showCreateModal = ref(false)
const creating = ref(false)
const isEditing = ref(false)
const editingId = ref(null)

const showShiftModal = ref(false)
const creatingShift = ref(false)
const activeMaster = ref(null)

// Booking Workflow
const showBookingModal = ref(false)
const bookingStep = ref(0)
const selectedCategory = ref('all')
const categoriesList = ref([])
const servicesList = ref([])
const selectedService = ref(null)
const slots = ref([])
const slotsLoading = ref(false)
const bookingLoading = ref(false)
const bookingDate = ref('')
const bookingForm = ref({
    client_name: '', client_phone: '', time: ''
})

const onCustomDateChange = (e) => {
    bookingDate.value = e.target.value
}

const filteredServices = computed(() => {
    const masterServiceIds = activeMaster.value?.services_detail?.map(s => s.id) || activeMaster.value?.services || []
    let base = servicesList.value.filter(s => masterServiceIds.includes(s.id))
    if (selectedCategory.value === 'all') return base
    return base.filter(s => s.category === selectedCategory.value)
})

const form = ref({
    first_name: '',
    last_name: '',
    phone: '',
    telegram_id: null,
    services: [],
    role: 'master'
})

let lookupTimeout = null
watch(() => form.value.telegram_id, (newID) => {
    if (isEditing.value || !newID || newID.toString().length < 5) return
    
    if (lookupTimeout) clearTimeout(lookupTimeout)
    lookupTimeout = setTimeout(async () => {
        try {
            const res = await api.get('/organization/employees/lookup/', {
                params: { telegram_id: newID }
            })
            if (res.data) {
                if (res.data.first_name) form.value.first_name = res.data.first_name
                if (res.data.last_name) form.value.last_name = res.data.last_name
                if (res.data.phone) form.value.phone = res.data.phone
            }
        } catch (e) {
            console.log('User lookup: not found or error')
        }
    }, 800)
})

const setBookingDate = (type) => {
    if (type === 'today') bookingDate.value = getLocalDateStr()
    else if (type === 'tomorrow') {
        const tom = new Date()
        tom.setDate(tom.getDate() + 1)
        bookingDate.value = tom.toISOString().split('T')[0]
    }
}

const shiftForm = ref({
    date: getLocalDateStr()
})

const fetchData = async () => {
    loading.value = true
    try {
        const [empRes, srvRes] = await Promise.all([
            api.get('/organization/employees/'),
            api.get('/services/')
        ])
        employees.value = empRes.data.results || empRes.data
        servicesList.value = srvRes.data.results || srvRes.data
    } catch (e) {
        console.error(e)
    } finally {
        loading.value = false
    }
}

const openCreateModal = () => {
    isEditing.value = false
    editingId.value = null
    form.value = {
        first_name: '', last_name: '', phone: '', telegram_id: null, services: [], role: 'master'
    }
    showCreateModal.value = true
}

const openEditModal = (emp) => {
    isEditing.value = true
    editingId.value = emp.id
    form.value = {
        first_name: emp.first_name, 
        last_name: emp.last_name, 
        phone: emp.phone || '', 
        telegram_id: emp.telegram_id || null, 
        services: emp.services_detail?.map(s => s.id) || [], 
        role: emp.role
    }
    showCreateModal.value = true
}

const submitEmployee = async () => {
    creating.value = true
    try {
        if (isEditing.value) {
            await api.patch(`/organization/employees/${editingId.value}/`, form.value)
        } else {
            await api.post('/organization/employees/', form.value)
        }
        await fetchData()
        showCreateModal.value = false
    } catch (e) {
        alert(e.response?.data?.error || t('common.error'))
    } finally {
        creating.value = false
    }
}

const handleEditClick = (emp) => {
    openEditModal(emp)
}

const handleSmenaClick = (emp) => {
    promptOpenShift(emp)
}

const handleZapisClick = (emp) => {
    startBooking(emp)
}

const promptOpenShift = (emp) => {
    activeMaster.value = emp
    shiftForm.value.date = getLocalDateStr()
    showShiftModal.value = true
}

const submitShift = async () => {
    if (!activeMaster.value) return
    creatingShift.value = true
    try {
        await api.post('/masters/shifts/', {
            master: activeMaster.value.master_id,
            date: shiftForm.value.date,
            work_start: "09:00:00",
            work_end: "20:00:00",
            is_open: true
        })
        const d = new Date(shiftForm.value.date).toLocaleDateString()
        alert(t('admin.shiftOpened', { name: activeMaster.value.first_name, date: d }))
        showShiftModal.value = false
    } catch (e) {
        const errorMsg = e.response?.data?.message || e.response?.data?.error || e.response?.data?.non_field_errors?.[0] || t('admin.shiftError')
        alert(errorMsg)
    } finally {
        creatingShift.value = false
    }
}

const startBooking = async (emp) => {
    activeMaster.value = emp
    bookingStep.value = 0
    bookingDate.value = getLocalDateStr()
    selectedService.value = null
    bookingForm.value = { client_name: '', client_phone: '', time: '' }
    
    try {
        const [catRes, srvRes] = await Promise.all([
            api.get('/categories/'),
            api.get('/services/')
        ])
        categoriesList.value = catRes.data.results || catRes.data
        servicesList.value = srvRes.data.results || srvRes.data
        
        showBookingModal.value = true
    } catch (e) {
        alert(t('common.error'))
    }
}

const selectService = async (srv) => {
    selectedService.value = srv
    bookingStep.value = 3
    slotsLoading.value = true
    try {
        const res = await api.get(`/masters/${activeMaster.value.master_id}/available-slots/`, {
            params: { date: bookingDate.value, service_id: srv.id }
        })
        slots.value = res.data
    } catch (e) {
        console.error(e)
    } finally {
        slotsLoading.value = false
    }
}

const createAppointment = async () => {
    bookingLoading.value = true
    try {
        const start_time = new Date(`${bookingDate.value}T${bookingForm.value.time}:00`).toISOString()
        const end_time = new Date(new Date(start_time).getTime() + selectedService.value.duration_minutes * 60000).toISOString()

        await api.post('/appointments/', {
            master: activeMaster.value.master_id,
            service: selectedService.value.id,
            start_time, end_time,
            client_name: bookingForm.value.client_name,
            client_phone: bookingForm.value.client_phone
        })
        showBookingModal.value = false
        alert(t('admin.bookingSuccess'))
    } catch (e) {
        alert(t('common.error'))
    } finally {
        bookingLoading.value = false
    }
}

onMounted(() => {
    fetchData()
})
</script>

<style scoped>
* { box-sizing: border-box; }

.admin-masters {
  padding: 20px 16px 100px;
}
.flex-between { display: flex; justify-content: space-between; align-items: center; }
.page-title { font-size: 24px; font-weight: 800; color: var(--text); }
.add-btn { background: var(--gold-gradient); border: none; border-radius: 50%; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; color: #fff; cursor: pointer; box-shadow: 0 4px 10px var(--gold-glow); }

.employee-card {
  background: var(--bg-secondary);
  border-radius: 16px;
  padding: 16px;
  margin-bottom: 12px;
  border: 1px solid var(--border);
}
.emp-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 14px;
}
.emp-avatar {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    background: var(--bg);
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    flex-shrink: 0;
    border: 1px solid var(--border);
}
.emp-avatar img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}
.emp-avatar span { font-size: 24px; }

.emp-info { 
    flex: 1; 
    display: flex;
    flex-direction: column;
    gap: 4px;
}
.emp-name { font-size: 16px; font-weight: 700; color: var(--text); }
.emp-phone { font-size: 13px; color: var(--muted); }

.emp-edit-col {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
}

.shift-indicators {
    display: flex;
    gap: 4px;
}
.indicator-icon {
    width: 20px;
    height: 20px;
    color: var(--border);
    transition: all 0.3s;
}
.indicator-icon.admin-active {
    color: #FF9800;
    filter: drop-shadow(0 0 4px rgba(255, 152, 0, 0.4));
}
.indicator-icon.master-active {
    color: #4CAF50;
    filter: drop-shadow(0 0 4px rgba(76, 175, 80, 0.4));
}

.role-badge {
    display: inline-block;
    font-size: 10px;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 12px;
    text-transform: uppercase;
    margin-top: 4px;
}
.role-badge.master { background: var(--gold-glow); color: var(--gold); border: 1px solid var(--gold); }
.role-badge.admin { background: rgba(59, 130, 246, 0.1); color: #3b82f6; border: 1px solid #3b82f6; }

.btn-action {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 4px;
    padding: 10px 0;
    border-radius: 12px;
    border-width: 1px;
    border-style: solid;
    font-size: 13px;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.2s;
    flex: 1;
}
.btn-action:active { transform: scale(0.95); }
.btn-smena { background: var(--gold-glow); color: var(--gold); border-color: var(--gold); }
.btn-zapis { background: rgba(59, 130, 246, 0.1); color: #3b82f6; border-color: #3b82f6; }

.master-btns-row {
    display: flex; gap: 8px; width: 100%;
}

.edit-icon-btn {
    background: var(--bg-secondary); border: 1px solid var(--border); color: var(--gold);
    display: flex; align-items: center; justify-content: center; padding: 8px; border-radius: 10px;
    cursor: pointer; transition: all 0.2s;
}
.edit-icon-btn:active { background: var(--gold-glow); }

.date-selector { display: flex; gap: 8px; align-items: center; margin-bottom: 24px; overflow-x: auto; scrollbar-width: none; }
.date-selector::-webkit-scrollbar { display: none; }

.custom-date-wrapper { position: relative; }
.date-input-hidden { position: absolute; inset: 0; opacity: 0; cursor: pointer; }

.date-pill {
  white-space: nowrap; padding: 8px 16px; border-radius: 20px;
  background: var(--bg-secondary); border: 1px solid var(--border);
  color: var(--muted); font-size: 13px; font-weight: 600; cursor: pointer; transition: all 0.2s;
}
.date-pill.active {
  background: var(--gold-gradient); color: #000; border-color: var(--gold);
  box-shadow: 0 4px 10px var(--gold-glow);
}

.category-scroll {
    display: flex; overflow-x: auto; gap: 8px; scrollbar-width: none;
}
.category-scroll::-webkit-scrollbar { display: none; }

.service-card {
  background: var(--bg-secondary); border-radius: 12px; padding: 12px 16px;
  margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;
  border: 1px solid var(--border); cursor: pointer;
}

.slot-item {
  padding: 12px 0; border-radius: 12px; border: 1px solid var(--border);
  text-align: center; font-size: 14px; font-weight: 600; cursor: pointer;
  background: var(--bg-secondary); transition: all 0.2s;
}
.slot-item.disabled { opacity: 0.3; cursor: not-allowed; text-decoration: line-through; }
.slot-item.selected { background: var(--gold-gradient); color: #000; border-color: var(--gold); }

.slots-grid {
    display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px;
    max-height: 300px; overflow-y: auto; padding-right: 4px;
}
.slots-grid::-webkit-scrollbar { width: 4px; }
.slots-grid::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
.btn-sheet-ghost { background: transparent; color: var(--muted); border: 1px solid var(--border); margin-top: 8px; }
</style>
