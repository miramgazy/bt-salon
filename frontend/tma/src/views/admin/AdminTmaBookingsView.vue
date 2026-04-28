<template>
  <div class="admin-bookings">
    <div class="page-header">
      <h1 class="page-title">{{ $t('admin.bookingsTitle') }}</h1>
      <button class="add-btn" @click="checkAndOpenModal">
        <Icon icon="mdi:plus" width="24" />
      </button>
    </div>
    
    <!-- Dynamic Header / Filter Panel -->
    <div class="filters-panel">
      <div class="panel-main">
        <!-- Trigger Icon -->
        <button 
          :class="['filter-toggle', { active: isFilterMode }]" 
          @click="toggleFilterMode"
        >
          <Icon :icon="isFilterMode ? 'mdi:filter-off-outline' : 'mdi:filter-variant'" width="20" />
        </button>

        <TransitionGroup name="panel-slide" tag="div" class="panel-content">
          <!-- Default Mode: Date Selector -->
          <div v-if="!isFilterMode" key="dates" class="date-selector-compact">
            <button 
              :class="['date-pill', { active: activeTab === 'today' }]" 
              @click="setDate('today')"
            >{{ $t('master.today') }}</button>
            <button 
              :class="['date-pill', { active: activeTab === 'tomorrow' }]" 
              @click="setDate('tomorrow')"
            >{{ $t('master.tomorrow') }}</button>
            <div :class="['date-pill custom-date-wrapper', { active: activeTab === 'custom' }]">
               <Icon icon="mdi:calendar-month-outline" width="16" />
               <input type="date" v-model="selectedDate" class="date-input-hidden" @change="activeTab = 'custom'" />
               <span>{{ activeTab === 'custom' ? formatDateShort(selectedDate) : $t('master.selectDate') }}</span>
            </div>
          </div>

          <!-- Filter Mode: Compact Controls -->
          <div v-else key="filters" class="active-filters-row">
            <!-- Status Filter Toggle -->
            <button 
              :class="['compact-btn', { active: activeFilterPanel === 'status' }]"
              @click="toggleFilterPanel('status')"
            >
              <Icon icon="mdi:list-status" width="20" />
            </button>

            <!-- Master/Service Filter Toggle -->
            <button 
              :class="['compact-btn', { active: activeFilterPanel === 'master-service' }]"
              @click="toggleFilterPanel('master-service')"
            >
              <div class="icon-group">
                <Icon icon="mdi:account-tie-outline" width="18" />
                <Icon icon="mdi:content-cut" width="14" class="sub-icon" />
              </div>
            </button>

            <!-- Search Filter Toggle -->
            <button 
              :class="['compact-btn', { active: activeFilterPanel === 'search' }]"
              @click="toggleFilterPanel('search')"
            >
              <Icon icon="mdi:magnify" width="20" />
            </button>

            <!-- Clear All -->
            <button class="compact-btn text-error" @click="resetFilters" v-if="hasActiveFilters">
              <Icon icon="mdi:filter-remove-outline" width="20" />
            </button>
          </div>
        </TransitionGroup>
      </div>

        <!-- Status Filter Panel -->
      <Transition name="panel-expand">
        <div v-if="isFilterMode && activeFilterPanel === 'status'" class="expanded-panel">
          <div class="category-scroll">
            <button 
              :class="['date-pill', { active: !filters.status }]" 
              @click="filters.status = ''"
            >{{ $t('tma.all') }}</button>
            <button 
              v-for="st in ['pending', 'confirmed', 'done', 'cancelled']" :key="st"
              :class="['date-pill', { active: filters.status === st }]" 
              @click="filters.status = st"
            >{{ getStatusText(st) }}</button>
          </div>
        </div>
      </Transition>

      <!-- Expandable Filter Panels -->
      <Transition name="panel-expand">
        <div v-if="isFilterMode && activeFilterPanel === 'master-service'" class="expanded-panel">
          <div class="filter-row">
            <div class="filter-col">
              <label class="filter-label">{{ $t('admin.masterRole') }}</label>
              <select v-model="filters.masterId" class="filter-select">
                <option value="">{{ $t('admin.selectMaster') }}</option>
                <option v-for="m in mastersList" :key="m.id" :value="m.id">{{ m.first_name }}</option>
              </select>
            </div>
            <div class="filter-col">
              <label class="filter-label">{{ $t('common.service') }}</label>
              <select v-model="filters.serviceId" class="filter-select">
                <option value="">{{ $t('admin.selectService') }}</option>
                <option v-for="s in servicesList" :key="s.id" :value="s.id">{{ s.name }}</option>
              </select>
            </div>
          </div>
        </div>
      </Transition>

      <Transition name="panel-expand">
        <div v-if="isFilterMode && activeFilterPanel === 'search'" class="expanded-panel">
          <div class="filter-row">
            <input 
              v-model="filters.searchQuery" 
              type="text" 
              class="filter-input" 
              :placeholder="$t('admin.searchPlaceholder')"
            />
          </div>
        </div>
      </Transition>
    </div>

    <div v-if="loading" class="loading-state">
       <div class="spinner"></div>
    </div>

    <div v-else-if="appointments.length === 0" class="empty-state">
       <div class="empty-icon">📅</div>
       <p>{{ $t('admin.noSlots') }}</p>
    </div>

    <div v-else class="bookings-list">
       <div v-for="apt in filteredAppointments" :key="apt.id" class="booking-card" @click="openActions(apt)">
          <div class="booking-time">
             <div class="time-main">{{ formatStartTime(apt.start_time) }}</div>
             <div class="time-duration">{{ getDuration(apt.start_time, apt.end_time) }} {{ $t('common.min') }}</div>
          </div>
          <div class="booking-info">
             <div class="client-name">{{ apt.client_detail?.full_name || $t('common.offlineClient') }} <span v-if="apt.client_detail?.phone" class="client-phone">{{ apt.client_detail.phone }}</span></div>
             <div class="service-name text-gold flex items-start gap-1">
                 <Icon 
                   v-if="apt.appointment_type === 'combo_sub'" 
                   icon="mdi:subdirectory-arrow-right" 
                   width="14" 
                   class="text-primary/60 mt-1" 
                 />
                 <Icon 
                   v-else-if="apt.appointment_type === 'combo_master'" 
                   icon="mdi:layers-outline" 
                   width="14" 
                   class="text-primary mt-1" 
                 />
                 <div>
                    <div class="flex items-center gap-1">
                       <span class="font-bold">{{ apt.display_title?.split(':')[0] || apt.display_title || apt.service_detail?.name || $t('admin.selectService') }}</span>
                       <span v-if="apt.appointment_type !== 'single'" class="text-[10px] bg-primary/10 text-primary px-1 rounded">
                          {{ apt.appointment_type === 'combo_master' ? $t('admin.main') : $t('admin.sub') }}
                       </span>
                    </div>
                    <div v-if="apt.display_title?.includes(':')" class="text-xs opacity-80">
                       {{ apt.display_title.split(':')[1].trim() }}
                    </div>
                    <div class="text-muted text-[10px] mt-0.5">({{ apt.master_detail?.first_name || $t('admin.masterRole') }})</div>
                 </div>
             </div>
             <div v-if="apt.notes" class="booking-notes">
                <Icon icon="mdi:note-text-outline" width="14" />
                <span>{{ apt.notes }}</span>
             </div>
          </div>
          <div class="booking-status flex flex-col items-end gap-2">
             <span :class="['status-badge', apt.status.toLowerCase()]">{{ getStatusText(apt.status) }}</span>
             <button class="edit-apt-btn" @click.stop="openEditMode(apt)">
                <Icon icon="mdi:pencil-outline" width="18" />
             </button>
          </div>
       </div>
    </div>

    <!-- Actions Modal (Bottom Sheet) -->
    <div v-if="activeApt" class="overlay" @click="activeApt = null">
      <div class="sheet" @click.stop>
        <div class="sheet-title mb-4">{{ $t('admin.editBooking') }} #{{ activeApt.id }}</div>
        
        <div v-if="!showCancelPrompt">
          <button v-if="activeApt.status === 'pending' || activeApt.status === 'confirmed'" class="btn-sheet" @click="markAsDone">{{ $t('admin.finishService') }}</button>
          <button v-if="activeApt.status === 'pending'" class="btn-sheet bg-secondary mt-2" @click="confirmApt">{{ $t('admin.status.confirmed') }}</button>
          <button v-if="activeApt.status !== 'cancelled' && activeApt.status !== 'done'" class="btn-sheet bg-danger mt-2" @click="showCancelPrompt = true">{{ $t('admin.status.cancelled') }}</button>
          <button class="btn-sheet btn-sheet-ghost mt-4" @click="activeApt = null">{{ $t('common.close') }}</button>
        </div>
        
        <div v-else>
          <div class="mb-4">
            <label class="form-label">{{ $t('admin.cancelReasonLabel') }}</label>
            <textarea v-model="cancelReason" class="form-input" rows="3" :placeholder="$t('admin.cancelReasonPlaceholder')"></textarea>
          </div>
          <button class="btn-sheet bg-danger" :disabled="!cancelReason.trim()" @click="cancelApt">{{ $t('admin.status.cancelled') }}</button>
          <button class="btn-sheet btn-sheet-ghost mt-2" @click="showCancelPrompt = false">{{ $t('common.back') }}</button>
        </div>
      </div>
    </div>

    <!-- Edit Appointment Modal -->
    <div v-if="showEditModal" class="overlay" @click="showEditModal = false">
      <div class="sheet h-80vh" @click.stop>
        <div class="sheet-title flex justify-between">
            <span>{{ $t('admin.editBooking') }}</span>
            <Icon icon="mdi:close" width="24" @click="showEditModal = false" class="cursor-pointer" />
        </div>
        
        <div class="mt-4 flex flex-col gap-4 overflow-y-auto pb-6" style="flex: 1">
          <div class="p-4 bg-secondary rounded-2xl flex flex-col gap-2">
            <div class="flex justify-between items-center">
               <div class="text-sm text-muted">{{ $t('admin.currentTime') }}:</div>
               <div class="font-bold">{{ formatDateShort(editForm.date) }}, {{ editForm.oldTime }}</div>
            </div>
            
            <div class="mt-2">
              <label class="form-label text-xs mb-1">{{ $t('admin.masterRole') }}</label>
              <select v-model="editForm.master_id" class="filter-select bg-white" @change="refreshSlots">
                <option v-for="m in availableMasters" :key="m.id" :value="m.id">
                   {{ m.first_name }} {{ m.last_name }}
                </option>
              </select>
            </div>
          </div>

          <label class="form-label mt-2">{{ $t('admin.selectTime', { date: formatDateShort(editForm.date) }) }}</label>
          <div v-if="slotsLoading" class="spinner"></div>
          <div v-else-if="slots.length === 0" class="text-muted text-center py-4">
              {{ $t('admin.noSlots') }}
          </div>
          <div v-else class="slots-grid">
              <div v-for="slot in slots" :key="slot.time"
                   class="slot-item"
                   :class="{ disabled: !slot.is_available, selected: editForm.time === slot.time }"
                   @click="if (slot.is_available) { editForm.time = slot.time; showConfirmModal = true }">
                  {{ slot.time }}
              </div>
          </div>
        </div>
        <button class="btn-sheet btn-sheet-ghost mt-2" @click="showEditModal = false">{{ $t('common.cancel') }}</button>
      </div>
    </div>

    <!-- Confirm Modal -->
    <div v-if="showConfirmModal" class="overlay z-high" @click="showConfirmModal = false">
      <div class="sheet" @click.stop>
        <div class="confirm-icon">❓</div>
        <h3 class="sheet-title text-center">{{ $t('admin.confirmTransfer') }}</h3>
        <p class="confirm-text text-center">
          {{ $t('admin.confirmTransferText', { time: editForm.time }) }}
        </p>
        <div class="mt-6">
          <button class="btn-sheet" @click="saveAptChanges" :disabled="saving">
            {{ saving ? $t('common.saving') : $t('admin.confirmTransferBtn') }}
          </button>
          <button class="btn-sheet btn-sheet-ghost mt-2" @click="showConfirmModal = false">{{ $t('common.cancel') }}</button>
        </div>
      </div>
    </div>

    <!-- Success Feedback Overlay -->
    <Transition name="fade">
      <div v-if="successMsg" class="success-toast">
        <Icon icon="mdi:check-circle" width="24" />
        <span>{{ successMsg }}</span>
      </div>
    </Transition>
    <div v-if="showCreateModal" class="overlay" @click="showCreateModal = false">
      <div class="sheet h-80vh" @click.stop>
        <div class="sheet-title flex justify-between">
            <span>{{ $t('admin.newBooking') }} ({{ $t('admin.step') }} {{ creationStep }}/4)</span>
            <Icon icon="mdi:close" width="24" @click="showCreateModal = false" class="cursor-pointer" />
        </div>
        
        <div class="mt-4 flex flex-col gap-4 overflow-y-auto pb-6" style="flex: 1">
          <!-- Step 1: Services -->
          <div v-if="creationStep === 1">
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

             <div class="flex flex-col gap-3 mt-2">
                 <div v-for="srv in filteredServicesList" :key="srv.id" 
                      class="service-card"
                      :class="{ selected: form.service_id === srv.id }"
                      @click="form.service_id = srv.id; currentServiceDuration = srv.duration_minutes; currentServiceName = srv.name; creationStep = 2">
                    <div>
                        <div class="font-bold text-base">{{ srv.name }}</div>
                        <div class="text-sm text-muted">{{ srv.duration_minutes }} {{ $t('common.min') }}</div>
                    </div>
                    <div class="font-bold text-gold text-lg">{{ srv.total_price }} ₸</div>
                 </div>
             </div>
          </div>

          <!-- Step 2: Masters -->
          <div v-if="creationStep === 2">
             <label class="form-label mb-2">{{ $t('admin.selectMaster') }}</label>
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
                     {{ $t('admin.noMastersForService') }}
                 </div>
             </div>
             <button class="btn-sheet bg-secondary mt-4" @click="creationStep = 1">{{ $t('common.back') }}</button>
          </div>

          <!-- Step 3: Slots -->
          <div v-if="creationStep === 3">
             <label class="form-label mb-2">{{ $t('admin.selectTime', { date: formatDateShort(selectedDate) }) }}</label>
             <div v-if="slotsLoading" class="spinner"></div>
             <div v-else-if="slots.length === 0" class="text-muted text-center py-4">
                 {{ $t('admin.noSlots') }}
             </div>
             <div v-else class="slots-grid">
                 <div v-for="slot in slots" :key="slot.time"
                      class="slot-item"
                      :class="{ disabled: !slot.is_available, selected: form.time === slot.time }"
                      @click="if (slot.is_available) { form.time = slot.time; creationStep = 4 }">
                     {{ slot.time }}
                 </div>
             </div>
             <button class="btn-sheet bg-secondary mt-4" @click="creationStep = 2">{{ $t('common.back') }}</button>
          </div>

          <!-- Step 4: Client Info -->
          <div v-if="creationStep === 4">
             <form @submit.prevent="createAppointment" class="flex flex-col gap-4">
                 <div>
                    <label class="form-label">{{ $t('admin.clientName') }} <span class="text-error">*</span></label>
                    <input v-model="form.client_name" type="text" class="form-input" required autofocus />
                 </div>
                 <div>
                    <label class="form-label">{{ $t('admin.clientPhone') }} <span class="text-error">*</span></label>
                    <input v-model="form.client_phone" type="text" class="form-input" required placeholder="+7 (___) ___-__-__" />
                 </div>
                 <div>
                    <label class="form-label">{{ $t('admin.clientNotes') }}</label>
                    <textarea v-model="form.notes" class="form-input" rows="2"></textarea>
                 </div>
                  <div class="summary-card">
                     <div class="summary-item">
                        <span class="summary-label">{{ $t('common.service') }}</span>
                        <span class="summary-value">{{ currentServiceName }} ({{ currentServiceDuration }} {{ $t('common.min') }})</span>
                     </div>
                     <div class="summary-item">
                        <span class="summary-label">{{ $t('common.time') }}</span>
                        <span class="summary-value">{{ formatDateShort(selectedDate) }}, {{ form.time }}</span>
                     </div>
                  </div>
                 <button type="submit" class="btn-sheet mt-2" :disabled="creating">
                    {{ creating ? $t('admin.creating') : $t('admin.createBtn') }}
                 </button>
             </form>
             <button class="btn-sheet btn-sheet-ghost mt-2" @click="creationStep = 3">{{ $t('common.back') }}</button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { Icon } from '@iconify/vue'
import { useI18n } from 'vue-i18n'
import api from '@/api'

const { t, locale } = useI18n()
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
const currentServiceName = ref('')
const mastersList = ref([])

// Filters states
const isFilterMode = ref(false)
const activeFilterPanel = ref(null) // 'master-service' or 'search'
const filters = ref({
    status: '',
    masterId: '',
    serviceId: '',
    searchQuery: ''
})

const showEditModal = ref(false)
const showConfirmModal = ref(false)
const saving = ref(false)
const successMsg = ref('')
const editForm = ref({
    id: null,
    master_id: '',
    service_id: '',
    date: '',
    time: '',
    oldTime: ''
})

const toggleFilterMode = () => {
    isFilterMode.value = !isFilterMode.value
    if (!isFilterMode.value) {
        resetFilters()
        activeFilterPanel.value = null
    }
}

const toggleFilterPanel = (panel) => {
    if (activeFilterPanel.value === panel) activeFilterPanel.value = null
    else activeFilterPanel.value = panel
}

const resetFilters = () => {
    filters.value = { status: '', masterId: '', serviceId: '', searchQuery: '' }
}

const hasActiveFilters = computed(() => {
    return filters.value.status || filters.value.masterId || filters.value.serviceId || filters.value.searchQuery
})

const filteredAppointments = computed(() => {
    let result = appointments.value
    
    if (filters.value.status) {
        result = result.filter(a => a.status.toLowerCase() === filters.value.status.toLowerCase())
    }
    if (filters.value.masterId) {
        result = result.filter(a => String(a.master) === String(filters.value.masterId) || a.master_detail?.id === filters.value.masterId)
    }
    if (filters.value.serviceId) {
        result = result.filter(a => String(a.service) === String(filters.value.serviceId) || a.service_detail?.id === filters.value.serviceId)
    }
    if (filters.value.searchQuery) {
        const q = filters.value.searchQuery.toLowerCase()
        result = result.filter(a => {
            const name = a.client_detail?.full_name?.toLowerCase() || ''
            const phone = a.client_detail?.phone?.toLowerCase() || ''
            const master = a.master_detail?.first_name?.toLowerCase() || ''
            return name.includes(q) || phone.includes(q) || master.includes(q)
        })
    }
    
    return result
})

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
    return t(`admin.status.${status?.toLowerCase()}`) || status
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
  const currentLocale = locale.value === 'kz' ? 'kk-KZ' : 'ru-RU'
  return new Date(iso).toLocaleTimeString(currentLocale, { hour: '2-digit', minute: '2-digit' })
}

const formatDateShort = (d) => {
    if (!d) return ''
    const currentLocale = locale.value === 'kz' ? 'kk-KZ' : 'ru-RU'
    return new Date(d).toLocaleDateString(currentLocale, { day: 'numeric', month: 'short' })
}

const getDuration = (start, end) => {
  const diff = (new Date(end) - new Date(start)) / 60000
  return Math.round(diff)
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
    } catch (e) { alert(t('common.error')) }
}

const markAsDone = async () => {
    if (!activeApt.value) return
    try {
        await api.post(`/appointments/${activeApt.value.id}/done/`)
        activeApt.value = null
        fetchAppointments()
    } catch (e) { alert(t('common.error')) }
}

const cancelApt = async () => {
    if (!activeApt.value || !cancelReason.value.trim()) return
    try {
        await api.post(`/appointments/${activeApt.value.id}/cancel/`, {
            cancellation_reason: cancelReason.value
        })
        activeApt.value = null
        fetchAppointments()
    } catch (e) { alert(t('common.error')) }
}

const checkAndOpenModal = async () => {
    try {
        const res = await api.get('/masters/working/', { params: { date: selectedDate.value } })
        workingMasters.value = res.data
        if (workingMasters.value.length === 0) {
            alert(t('admin.noMastersWorking'))
            return
        }
        
        // Fetch services and categories
        const [sRes, cRes] = await Promise.all([
            api.get('/services/'),
            api.get('/categories/')
        ])
        servicesList.value = sRes.data.results || sRes.data
        categoriesList.value = cRes.data.results || cRes.data
        showCreateModal.value = true
    } catch (e) {
        alert(t('common.error'))
    }
}

const fetchInitialData = async () => {
    try {
        const [mRes, sRes] = await Promise.all([
            api.get('/masters/'),
            api.get('/services/')
        ])
        mastersList.value = mRes.data.results || mRes.data
        servicesList.value = sRes.data.results || sRes.data
    } catch (e) { console.error('Initial data error', e) }
}

const createAppointment = async () => {
    creating.value = true
    try {
        const start_time = new Date(`${selectedDate.value}T${form.value.time}:00`).toISOString()
        const duration = currentServiceDuration.value || 30
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
        successMsg.value = t('admin.bookingSuccess')
        setTimeout(() => successMsg.value = '', 3000)
        fetchAppointments()
    } catch (e) {
        alert(e.response?.data?.error || e.message || t('common.error'))
    } finally {
        creating.value = false
    }
}

const availableMasters = computed(() => {
    const sId = editForm.value.service_id
    if (!sId) return mastersList.value
    return mastersList.value.filter(m => 
        m.is_virtual || (m.services && m.services.includes(sId))
    )
})

const refreshSlots = async () => {
    slotsLoading.value = true
    slots.value = []
    try {
        const res = await api.get(`/masters/${editForm.value.master_id}/available-slots/`, {
            params: {
                date: editForm.value.date,
                service_id: editForm.value.service_id
            }
        })
        slots.value = res.data
    } catch (e) { console.error(e) }
    finally { slotsLoading.value = false }
}

const openEditMode = async (apt) => {
    editForm.value = {
        id: apt.id,
        master_id: apt.master || apt.master_detail?.id,
        service_id: apt.service || apt.service_detail?.id,
        date: apt.start_time.split('T')[0],
        time: formatStartTime(apt.start_time),
        oldTime: formatStartTime(apt.start_time)
    }
    showEditModal.value = true
    refreshSlots()
}

const saveAptChanges = async () => {
    saving.value = true
    try {
        const start_time = new Date(`${editForm.value.date}T${editForm.value.time}:00`).toISOString()
        const apt = filteredAppointments.value.find(a => a.id === editForm.value.id)
        const duration = getDuration(apt.start_time, apt.end_time)
        const end_time = new Date(new Date(start_time).getTime() + duration * 60000).toISOString()

        await api.patch(`/appointments/${editForm.value.id}/`, {
            master: editForm.value.master_id,
            start_time,
            end_time
        })
        
        showConfirmModal.value = false
        showEditModal.value = false
        successMsg.value = t('admin.transferSuccess')
        setTimeout(() => successMsg.value = '', 3000)
        fetchAppointments()
    } catch (e) {
        alert(t('common.error') + ': ' + (e.response?.data?.error || e.message))
    } finally {
        saving.value = false
    }
}

watch(selectedDate, () => {
  fetchAppointments()
})

onMounted(() => {
  fetchAppointments()
  fetchInitialData()
})
</script>

<style scoped>
.admin-bookings {
  padding: 20px 16px 100px;
}
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-title { font-size: 24px; font-weight: 800; color: var(--text); }
.add-btn { background: var(--gold-gradient); border: none; border-radius: 50%; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; color: #fff; cursor: pointer; box-shadow: 0 4px 10px var(--gold-glow); }

.date-selector { display: flex; gap: 10px; align-items: center; margin-bottom: 24px; padding: 4px 0; overflow-x: auto; scrollbar-width: none; }
.date-selector::-webkit-scrollbar { display: none; }

/* Filters Panel Modernized */
.filters-panel {
  background: var(--bg-secondary);
  border-radius: 18px;
  padding: 6px;
  margin-bottom: 24px;
  border: 1px solid var(--border);
  box-shadow: 0 4px 12px rgba(0,0,0,0.03);
}

.panel-main {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-toggle {
  width: 40px;
  height: 40px;
  border-radius: 14px;
  background: var(--tg-bg);
  border: 1px solid var(--border);
  color: var(--text);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}
.filter-toggle.active {
  background: var(--gold-gradient);
  color: #fff;
  border-color: var(--gold);
}

.panel-content {
  flex: 1;
  display: flex;
  align-items: center;
  height: 40px;
  overflow: hidden;
}

.date-selector-compact {
  display: flex;
  gap: 6px;
  width: 100%;
}

.date-pill {
  white-space: nowrap;
  padding: 6px 12px;
  border-radius: 12px;
  background: var(--tg-bg);
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
}

.active-filters-row {
  display: flex;
  gap: 6px;
  width: 100%;
}

.compact-btn {
  flex: 1;
  height: 40px;
  border-radius: 12px;
  background: var(--tg-bg);
  border: 1px solid var(--border);
  color: var(--muted);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}
.compact-btn.active {
  background: var(--gold-glow);
  color: var(--gold);
  border-color: var(--gold);
}

.icon-group {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}
.sub-icon {
  position: absolute;
  bottom: -4px;
  right: -4px;
  background: var(--tg-bg);
  border-radius: 50%;
  padding: 1px;
}

.expanded-panel {
  margin-top: 8px;
  padding: 10px;
  background: var(--tg-bg);
  border-radius: 14px;
  border: 1px solid var(--border);
}

.filter-row {
  display: flex;
  gap: 10px;
}
.filter-col { flex: 1; }
.filter-label { font-size: 10px; color: var(--muted); font-weight: 700; text-transform: uppercase; margin-bottom: 4px; display: block; }
.filter-select {
  width: 100%;
  padding: 8px;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: var(--bg-secondary);
  color: var(--text);
  font-size: 12px;
  outline: none;
}

.filter-input {
  width: 100%;
  padding: 10px 14px;
  border-radius: 10px;
  border: 1px solid var(--border);
  background: var(--bg-secondary);
  color: var(--text);
  font-size: 14px;
  outline: none;
}

/* Animations */
.panel-slide-enter-active, .panel-slide-leave-active { transition: all 0.3s ease; }
.panel-slide-enter-from { opacity: 0; transform: translateX(20px); }
.panel-slide-leave-to { opacity: 0; transform: translateX(-20px); }

.panel-expand-enter-active, .panel-expand-leave-active { 
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  max-height: 100px;
  overflow: hidden;
}
.panel-expand-enter-from, .panel-expand-leave-to { 
  max-height: 0;
  opacity: 0;
  margin-top: 0;
  padding-top: 0;
  padding-bottom: 0;
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

.edit-apt-btn {
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 10px;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--muted);
    transition: all 0.2s;
}
.edit-apt-btn:active { transform: scale(0.9); background: var(--border); }

.z-high { z-index: 2000; }

.confirm-icon { font-size: 48px; margin-bottom: 16px; text-align: center; }
.confirm-text { font-size: 16px; color: var(--muted); margin-bottom: 8px; line-height: 1.5; }

.success-toast {
  position: fixed;
  top: 20px; left: 50%;
  transform: translateX(-50%);
  background: #10b981;
  color: #fff;
  padding: 12px 20px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 600;
  box-shadow: 0 4px 20px rgba(16, 185, 129, 0.4);
  z-index: 3000;
}

.flex-col { flex-direction: column; }
.items-end { align-items: flex-end; }
.flex-shrink-0 { flex-shrink: 0; }
.opacity-80 { opacity: 0.8; }

.summary-card {
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: 18px;
  border: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 20px;
}
.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.summary-label {
  font-size: 13px;
  color: var(--muted, #888);
  font-weight: 500;
}
.summary-value {
  font-size: 14px;
  font-weight: 700;
  color: var(--text);
}
</style>
