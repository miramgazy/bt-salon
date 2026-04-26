<template>
  <div class="home-view">
    <!-- ══ SUCCESS ══ -->
    <div v-if="state.showSuccess" class="success fade-up">
      <div class="success-icon">✨</div>
      <div class="success-title header-font">{{ $t('tma.confirmTitle') }}</div>
      <div class="success-sub">{{ $t('tma.confirmSub') }}</div>
      <button class="btn-secondary" style="margin-top: 40px; width: 100%" @click="goHome">{{ $t('tma.goHome') }}</button>
    </div>

    <!-- ══ HOME PAGE ══ -->
    <div v-else-if="state.page === 'home'" class="fade-up">

      <!-- Tabs -->
      <div class="tabs">
        <label class="tab" :class="{ active: state.activeTab === 'services' }" @click="state.activeTab = 'services'">
          <span class="tab-icon">✨</span>
          {{ $t('tma.services') }}
        </label>
        <label class="tab" :class="{ active: state.activeTab === 'masters' }" @click="state.activeTab = 'masters'">
          <span class="tab-icon">👤</span>
          {{ $t('tma.masters') }}
        </label>
      </div>

      <!-- Dynamic Filters Panel -->
      <div class="filters-panel">
        <div class="panel-main">
          <button 
            :class="['filter-toggle', { active: isFilterMode }]" 
            @click="toggleFilterMode"
          >
            <Icon :icon="isFilterMode ? 'mdi:filter-off-outline' : 'mdi:filter-variant'" width="20" />
          </button>

          <TransitionGroup name="panel-slide" tag="div" class="panel-content">
            <!-- Default: Date Selector -->
            <div v-if="!isFilterMode" key="dates" class="date-selector-compact">
              <button 
                :class="['date-pill', { active: state.selectedDate === todayStr }]" 
                @click="state.selectedDate = todayStr"
              >{{ $t('tma.today') }}</button>
              <button 
                :class="['date-pill', { active: state.selectedDate === tomorrowStr }]" 
                @click="state.selectedDate = tomorrowStr"
              >{{ $t('tma.tomorrow') }}</button>
              <div :class="['date-pill custom-date-wrapper', { active: state.selectedDate !== todayStr && state.selectedDate !== tomorrowStr }]">
                 <Icon icon="mdi:calendar-month-outline" width="16" />
                 <input type="date" v-model="state.selectedDate" class="date-input-hidden" :min="todayStr" />
                 <span>{{ (state.selectedDate !== todayStr && state.selectedDate !== tomorrowStr) ? formatDateShort(state.selectedDate) : $t('master.date') }}</span>
              </div>
            </div>

            <!-- Active Filters Mode -->
            <div v-else key="filters" class="active-filters-row">
              <!-- Compact Date -->
              <div :class="['compact-btn', { active: state.selectedDate !== todayStr && state.selectedDate !== tomorrowStr }]">
                <Icon icon="mdi:calendar-edit" width="20" />
                <input type="date" v-model="state.selectedDate" class="date-input-hidden" :min="todayStr" />
              </div>

              <!-- Categories Toggle -->
              <button 
                :class="['compact-btn', { active: activeFilterPanel === 'category' }]"
                @click="toggleFilterPanel('category')"
              >
                <Icon icon="mdi:tag-outline" width="20" />
              </button>

              <!-- Search Toggle -->
              <button 
                :class="['compact-btn', { active: activeFilterPanel === 'search' }]"
                @click="toggleFilterPanel('search')"
              >
                <Icon icon="mdi:magnify" width="20" />
              </button>

              <!-- Reset -->
              <button class="compact-btn text-error" @click="resetMastersFilters" v-if="hasActiveMastersFilters">
                <Icon icon="mdi:filter-remove-outline" width="20" />
              </button>
            </div>
          </TransitionGroup>
        </div>

        <!-- Expandable Panels -->
        <Transition name="panel-expand">
          <div v-if="isFilterMode && activeFilterPanel === 'category'" class="expanded-panel">
            <div class="category-scroll">
              <button 
                :class="['pill', { active: !state.masterFilter }]" 
                @click="state.masterFilter = null"
              >{{ $t('tma.all') }}</button>
              <button 
                v-for="cat in categories" :key="cat.id"
                :class="['pill', { active: state.masterFilter === cat.id }]" 
                @click="state.masterFilter = cat.id"
              >{{ cat.name }}</button>
            </div>
          </div>
        </Transition>

        <Transition name="panel-expand">
          <div v-if="isFilterMode && activeFilterPanel === 'search'" class="expanded-panel">
            <input 
              v-model="masterSearchQuery" 
              type="text" 
              class="filter-input" 
              :placeholder="$t('admin.searchPlaceholder', 'Поиск мастера...')"
            />
          </div>
        </Transition>
      </div>

      <!-- Loading State -->
      <div v-if="loading" style="text-align:center; padding: 60px;">
        <div class="spinner"></div>
      </div>

      <!-- Services tab -->
      <template v-else-if="state.activeTab === 'services'">
        <div class="section-title header-font" style="margin-bottom: 12px; font-size: 20px;">
          {{ $t('tma.serviceCategories') }}
        </div>
        <div class="cat-grid">
          <div v-for="cat in categories" :key="cat.id" class="cat-tile" @click="handleCatClick(cat)">
            <div class="cat-tile-icon">🏷️</div>
            <div class="cat-tile-name">{{ cat.name }}</div>
          </div>
        </div>
      </template>

      <!-- Masters tab -->
      <template v-else-if="state.activeTab === 'masters'">
        <!-- Filter pills removed (integrated into filters-panel) -->
        <div class="master-grid">
          <div v-for="m in filteredMasters" :key="m.id" 
               :class="['master-card', { 'is-self': isSelf(m) }]" 
               @click="!isSelf(m) && handleMasterFirstSelect(m)">
            <div class="master-photo">
               <img v-if="m.photo_url" :src="m.photo_url" />
               <span v-else>👤</span>
            </div>
            <div class="master-info">
              <div class="master-name">{{ m.first_name }} {{ m.last_name }} <span v-if="isSelf(m)" class="self-badge">({{ $t('tma.itIsYou', 'Это вы') }})</span></div>
              <div class="master-rating">★ 5.0</div>
            </div>
            <div class="flex items-center gap-2">
                <button class="info-trigger" @click.stop="openProfile(m)">
                    <Icon icon="mdi:information-outline" width="22" />
                </button>
                <Icon v-if="!isSelf(m)" icon="mdi:chevron-right" width="24" :style="{ color: 'var(--muted)' }" />
            </div>
          </div>
        </div>
      </template>
    </div>

    <!-- ══ SERVICE LIST ══ -->
    <div v-else-if="state.page === 'service-list'" class="fade-up">
      <div class="page-header">
        <button class="back-btn" @click="goHome">
            <Icon icon="mdi:arrow-left" width="20" />
        </button>
        <div class="page-title header-font">{{ state.selectedMaster ? state.selectedMaster.first_name + " " + state.selectedMaster.last_name : state.selectedCat?.name }}</div>
      </div>
      <div class="service-list">
        <div v-for="svc in catServices" :key="svc.id" class="service-card" @click="handleServiceSelect(svc)">
          <div class="service-info">
            <div class="service-name">{{ svc.name }}</div>
            <div class="service-meta">⏱ {{ svc.duration_minutes }} {{ $t('tma.minutes') }}</div>
          </div>
          <div class="service-price">{{ svc.total_price }} ₸</div>
        </div>
      </div>
    </div>

    <!-- ══ MASTER SELECT ══ -->
    <div v-else-if="state.page === 'master-select'" class="fade-up">
      <div class="page-header">
        <button class="back-btn" @click="state.page = 'service-list'">
            <Icon icon="mdi:arrow-left" width="20" />
        </button>
        <div class="page-title header-font">{{ $t('tma.chooseMaster') }}</div>
      </div>
      
      <div v-if="state.selectedService" class="card glass" style="margin-bottom: 20px; border-left: 4px solid var(--gold);">
        <div style="font-size: 10px; text-transform: uppercase; letter-spacing: 1px; color: var(--gold); font-weight: 800; margin-bottom: 4px;">{{ $t('admin.serviceDetails') }}</div>
        <div style="font-weight: 600;">{{ state.selectedService.name }}</div>
        <div style="font-size: 13px; color: var(--muted); margin-top: 2px;">{{ state.selectedService.total_price }} ₸ • {{ state.selectedService.duration_minutes }} {{ $t('tma.minutes') }}</div>
      </div>

      <div class="master-grid">
        <div v-for="m in masterOptions" :key="m.id" 
             :class="['master-card', { 'is-self': isSelf(m) }]" 
             @click="!isSelf(m) && handleMasterSelect(m)">
            <div class="master-photo">
               <img v-if="m.photo_url" :src="m.photo_url" />
               <span v-else>👤</span>
            </div>
            <div class="master-info">
              <div class="master-name">{{ m.first_name }} {{ m.last_name }} <span v-if="isSelf(m)" class="self-badge">({{ $t('tma.itIsYou') }})</span></div>
              <div class="master-rating">★ 5.0 • {{ $t('tma.availableToday') }}</div>
            </div>
            <div class="flex items-center gap-2">
                <button class="info-trigger" @click.stop="openProfile(m)">
                    <Icon icon="mdi:information-outline" width="22" />
                </button>
                <button v-if="!isSelf(m)" class="status-badge confirmed" style="border: none; cursor: pointer;">{{ $t('common.select') }}</button>
            </div>
        </div>
      </div>
    </div>

    <!-- ══ SLOTS ══ -->
    <div v-else-if="state.page === 'slots'" class="fade-up">
      <div class="page-header">
        <button class="back-btn" @click="state.selectedService ? (state.selectedCat ? (state.page = 'master-select') : (state.page = 'service-list')) : (state.page = 'home')">
            <Icon icon="mdi:arrow-left" width="20" />
        </button>
        <div class="page-title header-font">{{ $t('tma.chooseTime') }}</div>
      </div>

      <div class="page-header" style="margin-bottom: 24px;">
        <div class="date-chip" :class="{ active: state.selectedDate === todayStr }" @click="state.selectedDate = todayStr">{{ $t('tma.today') }}</div>
        <div class="date-chip" :class="{ active: state.selectedDate === tomorrowStr }" @click="state.selectedDate = tomorrowStr">{{ $t('tma.tomorrow') }}</div>
        <input type="date" class="date-input" v-model="state.selectedDate" :min="todayStr" />
      </div>

      <div v-if="slotsLoading" style="text-align:center; padding: 40px;">
         <div class="spinner"></div>
      </div>
      
      <div v-else-if="shiftClosed" class="card glass fade-up" style="text-align: center; border-color: #ef4444; padding: 32px 20px;">
         <div style="font-size: 40px; margin-bottom: 16px">🚫</div>
         <div style="font-weight: 700; font-size: 18px; margin-bottom: 8px;">{{ $t('tma.shiftNotStarted') }}</div>
         <div style="color: var(--muted); font-size: 14px;">{{ $t('tma.masterNotWorkingYet') }}</div>
      </div>

      <div v-else-if="slots.length === 0" style="text-align:center; padding: 40px; color: var(--muted)">
         <Icon icon="mdi:calendar-blank" width="48" style="opacity: 0.2; margin-bottom: 12px" />
         <div>{{ $t('tma.noSlots') }}</div>
      </div>

      <div v-else class="slot-grid">
        <div v-for="s in slots" :key="s.time" 
             class="slot" 
             :class="{ selected: state.selectedSlot === s.time, busy: !s.is_available }" 
             @click="s.is_available ? handleSlotSelect(s.time) : null">
          {{ s.time }}
        </div>
      </div>
    </div>

    <!-- ══ CONFIRMATION MODAL ══ -->
    <div v-if="state.showModal && state.selectedService && state.selectedMaster && state.selectedSlot" 
         class="modal-overlay" @click.self="state.showModal = false">
       <div class="modal">
        <div class="modal-title header-font">{{ $t('tma.confirmBooking') }}</div>
        
        <div class="card glass" style="margin-bottom: 24px; text-align: left;">
             <div class="modal-row">
               <span class="modal-label">{{ $t('services.title') }}</span>
               <span class="modal-value">{{ state.selectedService.name }}</span>
             </div>
             <div class="modal-row">
               <span class="modal-label">{{ $t('tma.masters') }}</span>
               <span class="modal-value">{{ state.selectedMaster.first_name }} {{ state.selectedMaster.last_name }}</span>
             </div>
             <div class="modal-row">
               <span class="modal-label">{{ $t('common.time') }}</span>
               <span class="modal-value">{{ state.selectedDate }}, {{ state.selectedSlot }}</span>
             </div>
             <div class="modal-row" style="border-bottom: none; margin-top: 12px;">
               <span class="modal-label" style="font-size: 16px; color: var(--text); font-weight: 700;">{{ $t('tma.total') }}</span>
               <span class="modal-value gold header-font" style="font-size: 22px;">{{ state.selectedService.total_price }} ₸</span>
             </div>
         </div>
         
         <button class="btn-confirm" @click="handleConfirm">
           {{ $t('tma.book') }}
         </button>
         <button class="btn-secondary" style="margin-top: 12px; width: 100%" @click="state.showModal = false">
           {{ $t('common.cancel') }}
         </button>
      </div>
    </div>
    
    <!-- ══ MASTER PROFILE MODAL ══ -->
    <div v-if="state.showProfileModal && state.profileMaster" 
         class="modal-overlay" @click.self="state.showProfileModal = false">
       <div class="modal h-80vh">
          <div class="modal-header-actions">
            <div class="modal-title header-font">{{ $t('tma.masterProfile') }}</div>
            <button class="close-modal-btn" @click="state.showProfileModal = false">
                <Icon icon="mdi:close" width="24" />
            </button>
          </div>
          
          <div class="modal-scroll-content">
             <div class="profile-hero">
                <div class="profile-photo-large">
                   <img v-if="state.profileMaster.photo_url" :src="state.profileMaster.photo_url" />
                   <span v-else>👤</span>
                </div>
                <div class="profile-basic-info">
                   <div class="profile-name header-font">{{ state.profileMaster.first_name }} {{ state.profileMaster.last_name }}</div>
                   <div class="master-rating">★ 5.0 • 120+ записей</div>
                </div>
             </div>
             
             <div v-if="state.profileMaster.bio" class="profile-section">
                <div class="section-label">{{ $t('tma.aboutMaster') }}</div>
                <div class="profile-bio markdown-content" v-html="renderedBio"></div>
             </div>
             
             <div class="profile-section">
                <div class="section-label">{{ $t('services.title') }}</div>
                <div class="profile-services-list">
                   <div v-for="s_id in state.profileMaster.services" :key="s_id" class="mini-service-tag">
                      {{ services.find(sx => sx.id === s_id)?.name || 'Услуга' }}
                   </div>
                </div>
             </div>
          </div>
          
          <div class="modal-footer">
             <button class="btn-confirm" @click="selectFromProfile">
               {{ $t('common.select') }}
             </button>
          </div>
       </div>
    </div>

  </div>
</template>

<script setup>
import { reactive, ref, onMounted, computed, watch } from 'vue'
import api from '@/api'
import { Icon } from '@iconify/vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()

const getTodayStr = () => new Date().toISOString().slice(0,10)
const getTomorrowStr = () => {
  const d = new Date(); d.setDate(d.getDate()+1);
  return d.toISOString().slice(0,10)
}

const todayStr = getTodayStr()
const tomorrowStr = getTomorrowStr()

const formatDateShort = (iso) => {
  if (!iso) return ''
  const d = new Date(iso)
  return d.toLocaleDateString([], { day: 'numeric', month: 'short' })
}

const state = reactive({
  page: 'home',
  activeTab: 'services',
  selectedDate: todayStr,
  selectedCat: null,
  selectedService: null,
  selectedMaster: null,
  selectedSlot: null,
  masterFilter: null,
  showModal: false,
  showSuccess: false,
  showProfileModal: false,
  profileMaster: null
})

const categories = ref([])
const services = ref([])
const masters = ref([])
const loading = ref(true)

const slots = ref([])
const slotsLoading = ref(false)
const shiftClosed = ref(false)

// ── Filters State ──────────────────────────────────────────────
const isFilterMode = ref(false)
const activeFilterPanel = ref(null) // 'category' or 'search'
const masterSearchQuery = ref('')

const toggleFilterMode = () => {
  isFilterMode.value = !isFilterMode.value
  if (!isFilterMode.value) {
    resetMastersFilters()
    activeFilterPanel.value = null
  }
}

const toggleFilterPanel = (panel) => {
  if (activeFilterPanel.value === panel) activeFilterPanel.value = null
  else activeFilterPanel.value = panel
}

const resetMastersFilters = () => {
  state.masterFilter = null
  masterSearchQuery.value = ''
}

const hasActiveMastersFilters = computed(() => {
  return state.masterFilter || masterSearchQuery.value
})

const fetchData = async () => {
  try {
    loading.value = true
    console.log('HomeView: Starting fetchData...')
    
    // Attempt to fetch categories
    try {
      const catsRes = await api.get('/categories/')
      categories.value = catsRes.data.results || catsRes.data
      console.log('HomeView: Categories loaded', categories.value.length)
    } catch (e) { console.error('Cats fetch fail', e) }

    // Attempt to fetch services
    try {
      const servsRes = await api.get('/services/')
      services.value = servsRes.data.results || servsRes.data
      console.log('HomeView: Services loaded', services.value.length)
    } catch (e) { console.error('Servs fetch fail', e) }

    // Attempt to fetch masters
    try {
      const mastersRes = await api.get('/masters/')
      masters.value = mastersRes.data.results || mastersRes.data
      console.log('HomeView: Masters loaded', masters.value.length)
    } catch (e) { console.error('Masters fetch fail', e) }

    // Ensure auth is updated if missing organization info
    if (!auth.organizationSettings) {
      await auth.fetchCurrentUser()
    }
  } catch (err) {
    console.error('General Fetch error:', err)
  } finally {
    loading.value = false
    console.log('HomeView: fetchData finished')
  }
}

onMounted(() => {
  fetchData()
})

const catServices = computed(() => {
  const baseServices = state.selectedCat 
    ? services.value.filter(s => s.category === state.selectedCat.id)
    : services.value
    
  if (state.selectedMaster) {
    return baseServices.filter(s => state.selectedMaster.services?.includes(s.id))
  }
  return baseServices
})

const masterOptions = computed(() => {
    if (!state.selectedService) return masters.value
    return masters.value.filter(m => m.services?.includes(state.selectedService.id))
})

const filteredMasters = computed(() => {
  let result = masters.value
  
  if (state.masterFilter) {
    result = result.filter(m => m.services?.some(s => {
      const svc = services.value.find(sx => sx.id === s)
      return svc && svc.category === state.masterFilter
    }))
  }

  if (masterSearchQuery.value) {
    const q = masterSearchQuery.value.toLowerCase()
    result = result.filter(m => {
      const full = (m.first_name + ' ' + (m.last_name || '')).toLowerCase()
      return full.includes(q)
    })
  }

  return result
})

const isSelf = (master) => {
  if (!auth.user || !master.user) return false
  return auth.user.id === master.user
}

const goHome = () => {
  state.page = 'home'
  state.selectedCat = null
  state.selectedService = null
  state.selectedMaster = null
  state.selectedSlot = null
  state.showSuccess = false
}

const handleCatClick = (cat) => {
  state.selectedCat = cat
  state.selectedMaster = null // Reset master if choosing from categories
  state.page = 'service-list'
}

const handleServiceSelect = (svc) => {
  state.selectedService = svc
  if (state.selectedMaster) {
    state.page = 'slots'
  } else {
    state.page = 'master-select'
  }
}

const handleMasterSelect = (master) => {
  state.selectedMaster = master
  state.page = 'slots'
}

const handleSlotSelect = (slot) => {
  state.selectedSlot = slot
  state.showModal = true
}

const handleMasterFirstSelect = (master) => {
  state.selectedMaster = master
  state.selectedCat = null // Clear category so we show all services of this master
  state.page = 'service-list'
}

const fetchSlots = async () => {
  if (!state.selectedMaster || !state.selectedService || !state.selectedDate) return
  try {
    slotsLoading.value = true
    shiftClosed.value = false
    slots.value = []
    
    const res = await api.get(`/masters/${state.selectedMaster.id}/available-slots/`, {
      params: {
        date: state.selectedDate,
        service_id: state.selectedService.id
      }
    })
    slots.value = res.data
  } catch (err) {
    if (err.response?.status === 400 && err.response?.data?.error === 'shift_closed') {
       shiftClosed.value = true
    } else {
       console.error('Fetch slots error:', err)
    }
  } finally {
    slotsLoading.value = false
  }
}

const openProfile = (m) => {
  state.profileMaster = m
  state.showProfileModal = true
}

const selectFromProfile = () => {
    const m = state.profileMaster
    state.showProfileModal = false
    if (state.selectedService) {
        handleMasterSelect(m)
    } else {
        handleMasterFirstSelect(m)
    }
}

const renderedBio = computed(() => {
  if (!state.profileMaster?.bio) return ''
  let html = state.profileMaster.bio
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/^### (.+)$/gm, '<h3 style="font-size: 16px; font-weight: 700; margin: 12px 0 6px;">$1</h3>')
    .replace(/^## (.+)$/gm, '<h2 style="font-size: 18px; font-weight: 700; margin: 16px 0 8px;">$1</h2>')
    .replace(/^# (.+)$/gm, '<h1 style="font-size: 20px; font-weight: 700; margin: 16px 0 8px;">$1</h1>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/^- (.+)$/gm, '<li style="margin-left: 16px;">$1</li>')
    .replace(/\n\n/g, '</p><p style="margin-bottom: 8px;">')
    .replace(/\n/g, '<br/>')
  return `<p>${html}</p>`
})

watch([() => state.selectedMaster, () => state.selectedService, () => state.selectedDate, () => state.page], () => {
    if (state.selectedMaster && ['slots'].includes(state.page)) {
        fetchSlots()
    }
})

const { t } = useI18n()

const handleConfirm = async () => {
  try {
    const start = new Date(`${state.selectedDate}T${state.selectedSlot}:00`)
    const end = new Date(start.getTime() + state.selectedService.duration_minutes * 60000)
    
    await api.post('/appointments/', {
      master: state.selectedMaster.id,
      service: state.selectedService.id,
      start_time: start.toISOString(),
      end_time: end.toISOString()
    })
    
     state.showModal = false
    state.showSuccess = true
  } catch (error) {
    alert(t('tma.error'))
    console.error(error)
  }
}
</script>

<style scoped>
.home-view { padding: 20px 16px; }

/* Tabs */
.tabs { display: flex; gap: 8px; margin-bottom: 20px; }
.tab {
  flex: 1; padding: 14px 8px; border-radius: var(--radius-sm);
  background: var(--card-bg); border: 1px solid var(--border);
  cursor: pointer; text-align: center; transition: all .2s;
  font-size: 13px; font-weight: 600; color: var(--muted);
}
.tab.active { background: var(--gold-gradient); color: #000; border-color: var(--gold); box-shadow: 0 4px 12px var(--gold-glow); }
.tab-icon { font-size: 20px; display: block; margin-bottom: 4px; }

/* Dynamic Filters Panel */
.filters-panel {
  background: var(--bg-secondary);
  border-radius: 18px;
  padding: 6px;
  margin-bottom: 20px;
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
  color: #000;
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
  background: var(--gold);
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
  background: var(--gold-accent, var(--gold-glow));
  color: var(--gold);
  border-color: var(--gold);
}

.expanded-panel {
  margin-top: 8px;
  padding: 8px;
  background: var(--tg-bg);
  border-radius: 14px;
  border: 1px solid var(--border);
}

.category-scroll {
  display: flex;
  overflow-x: auto;
  gap: 8px;
  scrollbar-width: none;
}
.category-scroll::-webkit-scrollbar { display: none; }

.pill {
  white-space: nowrap; padding: 6px 14px; border-radius: 20px;
  background: var(--bg-secondary); border: 1px solid var(--border);
  font-size: 11px; font-weight: 600; color: var(--muted); cursor: pointer;
}
.pill.active { background: var(--gold); color: #000; border-color: var(--gold); }

.filter-input {
  width: 100%;
  padding: 10px 14px;
  border-radius: 10px;
  border: 1px solid var(--border);
  background: var(--bg-secondary);
  color: var(--text);
  font-size: 14px;
  outline: none;
  font-family: inherit;
}
.filter-input:focus { border-color: var(--gold); }

.text-error { color: #dc2626; }

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

/* Legacy Date selector (removed) */
/*.date-bar styles... */


/* Category grid */
.cat-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 10px; margin-bottom: 24px; }
.cat-tile {
  background: var(--card-bg); border: 1px solid var(--border); border-radius: var(--radius-sm);
  padding: 16px 8px; text-align: center; cursor: pointer; transition: all .2s;
}
.cat-tile:active { transform: scale(0.96); border-color: var(--gold); }
.cat-tile-icon { font-size: 26px; margin-bottom: 8px; }
.cat-tile-name { font-size: 11px; color: var(--text); font-weight: 600; line-height: 1.3; }

/* Services list */
.service-list { display: flex; flex-direction: column; gap: 10px; }
.service-card {
  background: var(--card-bg); border: 1px solid var(--border); border-radius: var(--radius-sm);
  padding: 18px; cursor: pointer; transition: all .2s; display: flex; justify-content: space-between; align-items: center;
}
.service-name { font-size: 15px; font-weight: 600; margin-bottom: 4px; }
.service-meta { font-size: 12px; color: var(--muted); font-weight: 500; }
.service-price { font-size: 18px; font-weight: 700; color: var(--gold); font-family: var(--font-header); }

/* Master grid */
.master-grid { display: flex; flex-direction: column; gap: 10px; }
.master-card {
  background: var(--card-bg); border: 1px solid var(--border); border-radius: var(--radius);
  padding: 16px; display: flex; align-items: center; gap: 16px; cursor: pointer; transition: all .2s;
}
.master-photo { width: 60px; height: 60px; border-radius: 50%; background: var(--bg-secondary); display: flex; align-items: center; justify-content: center; font-size: 32px; flex-shrink: 0; border: 2px solid var(--border); overflow: hidden; }
.master-photo img { width: 100%; height: 100%; object-fit: cover; }
.master-name { font-size: 16px; font-weight: 600; color: var(--text); }
.master-rating { font-size: 12px; color: var(--gold); font-weight: 700; }

.master-card.is-self { 
  opacity: 0.7; cursor: default; background: var(--bg-secondary); border-style: dashed;
}
.self-badge { font-size: 11px; color: var(--gold); margin-left: 4px; font-weight: 700; text-transform: uppercase; }

/* Slot grid */
.slot-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: 10px; margin-bottom: 24px; }
.slot {
  padding: 12px 0; border-radius: var(--radius-sm); text-align: center;
  font-size: 14px; cursor: pointer; border: 1px solid var(--border);
  background: var(--card-bg); transition: all 0.2s; font-weight: 600;
}
.slot.busy { opacity: 0.3; cursor: not-allowed; text-decoration: line-through; }
.slot.selected { background: var(--gold); color: #000; border-color: var(--gold); box-shadow: 0 4px 10px var(--gold-glow); }

/* Modal */
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,.7); z-index: 500;
  display: flex; align-items: flex-end; justify-content: center;
  backdrop-filter: blur(4px);
}
.modal {
  background: var(--bg); border-radius: 28px 28px 0 0; width: 100%; max-width: 450px;
  padding: 32px 20px 40px; border-top: 1px solid var(--border);
  box-shadow: 0 -10px 40px rgba(0,0,0,0.3);
}
.modal-title { font-size: 24px; font-weight: 700; margin-bottom: 24px; text-align: center; font-family: var(--font-header); }
.modal-row { display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid var(--border); font-size: 14px; }
.modal-label { color: var(--muted); font-weight: 500; }
.modal-value { font-weight: 600; color: var(--text); }
.modal-value.gold { color: var(--gold); font-size: 19px; font-family: var(--font-header); }

/* Buttons */
.btn-confirm {
  width: 100%; margin-top: 24px; padding: 16px; border-radius: var(--radius-sm);
  background: var(--gold-gradient); color: #000; border: none; font-size: 16px;
  font-weight: 700; cursor: pointer; box-shadow: 0 6px 20px var(--gold-glow);
}

.success { text-align: center; padding: 60px 20px; }
.success-icon { font-size: 64px; margin-bottom: 20px; filter: drop-shadow(0 4px 10px var(--gold-glow)); }
.success-title { font-size: 28px; font-weight: 700; margin-bottom: 12px; color: var(--gold); font-family: var(--font-header); }
.success-sub { font-size: 15px; color: var(--muted); line-height: 1.6; }

/* Profile Modal Specifics */
.info-trigger {
  background: var(--bg-secondary); border: 1px solid var(--border);
  color: var(--gold); width: 36px; height: 36px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.2s;
}
.info-trigger:active { background: var(--gold-glow); transform: scale(0.9); }

.modal-header-actions { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.close-modal-btn { background: none; border: none; color: var(--muted); cursor: pointer; padding: 4px; }

.modal-scroll-content { flex: 1; overflow-y: auto; padding-right: 4px; }
.modal-scroll-content::-webkit-scrollbar { width: 4px; }
.modal-scroll-content::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }

.profile-hero { text-align: center; margin-bottom: 24px; }
.profile-photo-large {
  width: 120px; height: 120px; border-radius: 50%;
  margin: 0 auto 16px; border: 3px solid var(--gold);
  padding: 4px; background: var(--bg-secondary);
  overflow: hidden; display: flex; align-items: center; justify-content: center;
}
.profile-photo-large img { width: 100%; height: 100%; object-fit: cover; border-radius: 50%; }
.profile-photo-large span { font-size: 64px; }

.profile-name { font-size: 24px; font-weight: 700; margin-bottom: 4px; }

.profile-section { margin-bottom: 24px; }
.section-label { 
  font-size: 11px; font-weight: 800; text-transform: uppercase; 
  letter-spacing: 1px; color: var(--gold); margin-bottom: 10px;
  display: flex; align-items: center; gap: 8px;
}
.section-label::after { content: ''; flex: 1; height: 1px; background: var(--border); opacity: 0.5; }

.profile-bio { line-height: 1.6; color: var(--text); font-size: 15px; }

.profile-services-list { display: flex; flex-wrap: wrap; gap: 8px; }
.mini-service-tag { 
  background: var(--bg-secondary); border: 1px solid var(--border);
  padding: 6px 12px; border-radius: 20px; font-size: 12px; color: var(--muted);
  font-weight: 600;
}

.modal-footer { margin-top: auto; padding-top: 16px; border-top: 1px solid var(--border); }
</style>
