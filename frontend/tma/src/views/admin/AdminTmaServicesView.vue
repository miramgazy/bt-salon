<template>
  <div class="admin-services">
    <Transition name="fade">
      <div v-if="successMsg" class="success-toast">
        <Icon icon="mdi:check-circle" width="24" />
        <span>{{ successMsg }}</span>
      </div>
    </Transition>
    <div class="page-header flex-between mb-4">
      <h1 class="page-title">{{ $t('services.title') }}</h1>
      <button class="add-btn" @click="showTypeSelector = true">
        <Icon icon="mdi:plus" width="24" />
      </button>
    </div>

    <!-- Category Filter Row -->
    <div class="category-scroll mb-6">
         <button 
            :class="['date-pill', 'flex-shrink-0', { active: selectedCategory === 'all' }]"
            @click="selectedCategory = 'all'"
         >{{ $t('admin.allCategories') }}</button>
        <button 
           v-for="cat in categories" :key="cat.id"
           :class="['date-pill', 'flex-shrink-0', { active: selectedCategory === cat.id }]"
           @click="selectedCategory = cat.id"
        >{{ cat.name }}</button>
    </div>
    
    <div v-if="loading" class="loading-state">
       <div class="spinner"></div>
    </div>

     <div v-else-if="services.length === 0" class="empty-state">
       <div class="empty-icon">✂️</div>
       <p>{{ $t('services.empty') }}</p>
    </div>

    <div v-else class="services-list mt-4">
       <div v-for="srv in filteredServices" :key="srv.id" class="service-card">
          <div class="service-card-content">
             <div class="service-top-row">
                 <div class="service-actions flex items-center gap-2">
                    <span v-if="srv.is_combo" class="combo-badge-mini">
                       <Icon icon="mdi:link-variant" width="10" />
                    </span>
                    <button class="edit-icon-btn" @click.stop="openEditModal(srv)">
                       <Icon icon="mdi:pencil-outline" width="22" />
                    </button>
                 </div>
                 <div class="service-name">{{ srv.name }}</div>
             </div>
             <div class="service-details-row">
                 <div class="service-meta">
                    <Icon icon="mdi:clock-outline" width="14" /> {{ srv.duration_minutes }} {{ $t('services.minutes') }}
                 </div>
                <div class="service-price">
                   {{ srv.total_price }} ₸
                </div>
             </div>
             
             <div class="service-actions-row mt-3">
                <div class="master-btns-row">
                    <button class="btn-action btn-zapis" @click.stop="startBooking(srv)">
                       <Icon icon="mdi:calendar-plus" width="16" />
                       {{ $t('admin.booking') }}
                    </button>
                </div>
             </div>
          </div>
       </div>
    </div>

    <!-- Create Service Modal (Bottom Sheet) -->
    <div v-if="showCreateModal" class="overlay" @click="showCreateModal = false">
      <div class="sheet h-80vh" @click.stop>
         <div class="sheet-title flex justify-between">
            <span>{{ isEditing ? $t('common.change') : $t('services.title') }}</span>
            <Icon icon="mdi:close" width="24" @click="showCreateModal = false" class="cursor-pointer" />
        </div>
        
        <form @submit.prevent="submitService" class="mt-4 flex flex-col gap-4 overflow-y-auto pb-6">
          <div>
            <label class="form-label">{{ $t('admin.serviceName') }} <span class="text-error">*</span></label>
            <input v-model="form.name" type="text" class="form-input" required />
          </div>
          <div>
            <label class="form-label flex-between">
               {{ $t('admin.category') }} <span class="text-error">*</span>
               <span class="text-xs text-gold cursor-pointer" @click="openCategoryModal">{{ $t('admin.newCategory') }}</span>
            </label>
            <select v-model="form.category" class="form-input" required>
              <option value="" disabled>{{ $t('admin.selectCategory') }}</option>
              <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
            </select>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="form-label">{{ $t('admin.durationMin') }} <span class="text-error">*</span></label>
              <input v-model="form.duration_minutes" type="number" class="form-input" required />
            </div>
            <div>
              <label class="form-label">{{ $t('admin.basePrice') }} <span class="text-error">*</span></label>
              <input v-model="form.base_price" type="number" class="form-input" required />
            </div>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="form-label">{{ $t('admin.marginType') }}</label>
              <select v-model="form.margin_type" class="form-input">
                <option value="fixed">{{ $t('admin.fixed') }}</option>
                <option value="percent">{{ $t('admin.percent') }}</option>
              </select>
            </div>
            <div>
              <label class="form-label">{{ $t('admin.marginSize') }}</label>
              <input v-model="form.margin_value" type="number" class="form-input" />
            </div>
          </div>
          
          <div class="total-price-box mt-2">
            <span class="text-muted">{{ $t('admin.totalForClient') }}:</span>
            <span class="text-gold bold text-lg">{{ computedTotal }} ₸</span>
          </div>

          <button type="submit" class="btn-sheet mt-2" :disabled="creating">
             {{ creating ? $t('common.saving') : $t('common.save') }}
          </button>
        </form>
      </div>
    </div>

    <!-- Service Type Selector -->
    <div v-if="showTypeSelector" class="overlay" @click="showTypeSelector = false">
       <div class="sheet" @click.stop>
          <div class="sheet-title mb-6 text-center">{{ $t('admin.selectServiceType') || 'Выберите тип услуги' }}</div>
          <div class="type-grid">
             <button class="type-btn" @click="openCreateModal(); showTypeSelector = false">
                <div class="type-icon-box">
                   <Icon icon="mdi:content-cut" width="32" />
                </div>
                <span>{{ $t('admin.singleService') || 'Обычная' }}</span>
             </button>
             <button class="type-btn type-btn-combo" @click="openComboModal(); showTypeSelector = false">
                <div class="type-icon-box">
                   <Icon icon="mdi:link-variant" width="32" />
                </div>
                <span>{{ $t('admin.comboService') || 'Комбо' }}</span>
             </button>
          </div>
          <button class="btn-sheet btn-sheet-ghost mt-6" @click="showTypeSelector = false">{{ $t('common.close') }}</button>
       </div>
    </div>

    <!-- Combo Service Modal (Bottom Sheet) -->
    <div v-if="showComboModal" class="overlay" @click="showComboModal = false">
      <div class="sheet h-80vh" @click.stop>
         <div class="sheet-title flex justify-between">
            <span>{{ isEditing ? $t('common.change') : 'Создание комбо' }}</span>
            <Icon icon="mdi:close" width="24" @click="showComboModal = false" class="cursor-pointer" />
        </div>
        
        <form @submit.prevent="submitCombo" class="mt-4 flex flex-col gap-4 overflow-y-auto pb-6">
          <div>
            <label class="form-label">Название комбо <span class="text-error">*</span></label>
            <input v-model="comboForm.name" type="text" class="form-input" required />
          </div>
          <div>
            <label class="form-label">{{ $t('admin.category') }} <span class="text-error">*</span></label>
            <select v-model="comboForm.category" class="form-input" required>
              <option value="" disabled>{{ $t('admin.selectCategory') }}</option>
              <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
            </select>
          </div>

          <div class="combo-items-section">
            <label class="form-label flex-between mb-2">
               Состав комбо
               <span class="text-xs text-gold bold" @click="addComboItem">+ Добавить</span>
            </label>
            <div class="space-y-3">
               <div v-for="(item, idx) in selectedSubServices" :key="idx" class="combo-item-row flex items-center gap-2">
                  <select v-model="item.id" class="form-input flex-1">
                     <option value="" disabled>Услуга...</option>
                     <option v-for="s in services.filter(x => !x.is_combo)" :key="s.id" :value="s.id">{{ s.name }}</option>
                  </select>
                  <div class="flex items-center">
                     <label :class="['main-star-btn', { active: mainIndex === idx }]">
                        <input type="radio" :value="idx" v-model="mainIndex" class="sr-only" />
                        <Icon :icon="mainIndex === idx ? 'mdi:star' : 'mdi:star-outline'" 
                              :class="mainIndex === idx ? 'text-gold' : 'text-muted'" 
                              width="24" />
                     </label>
                  </div>
                  <button type="button" @click="removeComboItem(idx)" class="remove-btn">
                     <Icon icon="mdi:close" width="18" />
                  </button>
               </div>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4 bg-secondary p-3 rounded-xl text-xs">
             <div>
                <div class="text-muted mb-1">Сумма услуг:</div>
                <div class="bold">{{ comboSumPrice }} ₸</div>
             </div>
             <div>
                <div class="text-muted mb-1">Длительность:</div>
                <div class="bold">{{ comboSumDuration }} мин</div>
             </div>
          </div>

          <div>
            <label class="form-label">Цена комбо (₸)</label>
            <input v-model="comboForm.total_price" type="number" class="form-input text-lg bold text-gold" required />
          </div>

          <div v-if="comboDiscount > 0">
             <label class="form-label mb-2">Стратегия скидки</label>
             <div class="flex gap-2">
                <button 
                  v-for="s in ['owner_only', 'master_only', 'equal_split']" :key="s"
                  type="button"
                  class="strat-pill"
                  :class="{ active: comboForm.discount_strategy === s }"
                  @click="comboForm.discount_strategy = s"
                >
                  {{ s === 'owner_only' ? 'Салон' : s === 'master_only' ? 'Мастер' : '50/50' }}
                </button>
             </div>
          </div>

          <button type="submit" class="btn-sheet mt-2" :disabled="creating">
             {{ creating ? $t('common.saving') : $t('common.save') }}
          </button>
        </form>
      </div>
    </div>

    <!-- Category Create Modal -->
    <div v-if="showCategoryModal" class="overlay" style="z-index: 1010" @click="showCategoryModal = false">
       <div class="sheet" @click.stop>
          <div class="sheet-title mb-4">{{ $t('admin.createCategoryTitle') }}</div>
          <input v-model="newCategory" type="text" class="form-input mb-4" :placeholder="$t('admin.categoryPlaceholder')" />
          <button class="btn-sheet mb-2" @click="createCategory" :disabled="!newCategory.trim() || savingCat">
            {{ savingCat ? $t('common.saving') : $t('common.save') }}
          </button>
          <button class="btn-sheet btn-sheet-ghost" @click="showCategoryModal = false">{{ $t('common.close') }}</button>
       </div>
    </div>

    <!-- Booking Modal (Wizard Step 2-4) -->
    <div v-if="showBookingModal" class="overlay" @click="showBookingModal = false">
      <div class="sheet h-80vh" @click.stop>
        <div class="sheet-title flex justify-between">
            <span>{{ $t('admin.booking') }}: {{ $t('admin.step') }} {{ bookingStep }}/4</span>
            <Icon icon="mdi:close" width="24" @click="showBookingModal = false" class="cursor-pointer" />
        </div>
        
        <div class="mt-4 flex flex-col gap-4 overflow-y-auto pb-6" style="flex: 1">
          <div class="p-3 bg-secondary rounded-xl text-sm mb-1">
             <b>{{ $t('common.service') }}:</b> {{ activeService?.name }}
          </div>

          <!-- Step 0: Date Selection -->
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
             <button class="btn-sheet" @click="bookingStep = 2">{{ $t('admin.next') }}</button>
          </div>

          <!-- Step 2: Masters -->
          <div v-if="bookingStep === 2">
             <div class="p-3 mb-2 bg-[var(--gold-glow)] border border-[var(--gold)] rounded-xl text-sm flex justify-between items-center">
                <span><b>{{ $t('admin.date') }}:</b> {{ formatDateShort(bookingDate) }}</span>
                <span class="text-gold cursor-pointer font-bold" @click="bookingStep = 0">{{ $t('common.change') }}</span>
             </div>
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
                     {{ $t('admin.noMastersToday') }}
                 </div>
             </div>
          </div>

          <!-- Step 3: Slots -->
          <div v-if="bookingStep === 3">
             <label class="form-label mb-2">{{ $t('admin.selectTimeToday') }}</label>
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
             <button class="btn-sheet bg-secondary mt-4" @click="bookingStep = 2">{{ $t('common.back') }}</button>
          </div>

          <!-- Step 4: Client Info -->
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
                    <div><b>{{ $t('common.time') }}:</b> {{ $t('master.today') }}, {{ bookingForm.time }}</div>
                 </div>
                 <button type="submit" class="btn-sheet mt-2" :disabled="bookingLoading">
                    {{ bookingLoading ? $t('admin.creating') : $t('admin.createBtn') }}
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

const services = ref([])
const categories = ref([])
const loading = ref(false)
const selectedCategory = ref('all')

const getLocalDateStr = () => {
    const tzOffset = new Date().getTimezoneOffset()
    return new Date(new Date().getTime() - (tzOffset * 60 * 1000)).toISOString().split('T')[0]
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
const isEditing = ref(false)
const editingId = ref(null)

const showCategoryModal = ref(false)
const showTypeSelector = ref(false)
const showComboModal = ref(false)
const newCategory = ref('')
const creating = ref(false)
const savingCat = ref(false)
const successMsg = ref('')

const comboForm = ref({
    name: '', category: '', total_price: 0, discount_strategy: 'owner_only'
})
const selectedSubServices = ref([{ id: '', quantity: 1 }])
const mainIndex = ref(0)

const comboSumPrice = computed(() => {
    return selectedSubServices.value.reduce((acc, item) => {
        const s = services.value.find(x => x.id === item.id)
        return acc + (s ? parseFloat(s.total_price) : 0)
    }, 0)
})

const comboSumDuration = computed(() => {
    return selectedSubServices.value.reduce((acc, item) => {
        const s = services.value.find(x => x.id === item.id)
        return acc + (s ? s.duration_minutes : 0)
    }, 0)
})

const comboDiscount = computed(() => comboSumPrice.value - comboForm.value.total_price)

const form = ref({
    name: '',
    category: '',
    duration_minutes: 60,
    base_price: 1000,
    margin_type: 'fixed',
    margin_value: 0
})

// Booking Wizard States
const showBookingModal = ref(false)
const bookingStep = ref(2)
const activeService = ref(null)
const workingMasters = ref([])
const slots = ref([])
const slotsLoading = ref(false)
const bookingLoading = ref(false)
const bookingDate = ref('')
const bookingForm = ref({
    client_name: '',
    client_phone: '',
    master_id: '',
    time: ''
})

const onCustomDateChange = (e) => {
    bookingDate.value = e.target.value
}

const setBookingDate = (type) => {
    if (type === 'today') bookingDate.value = getLocalDateStr()
    else if (type === 'tomorrow') {
        const tom = new Date()
        tom.setDate(tom.getDate() + 1)
        bookingDate.value = tom.toISOString().split('T')[0]
    }
}
const filteredServices = computed(() => {
    if (selectedCategory.value === 'all') return services.value
    return services.value.filter(s => s.category === selectedCategory.value)
})

const filteredWorkingMasters = computed(() => {
    return workingMasters.value.filter(m => 
        m.services?.includes(activeService.value?.id) || 
        m.services_detail?.some(s => s.id === activeService.value?.id)
    )
})

const fetchData = async () => {
    loading.value = true
    try {
        const [resSrv, resCat] = await Promise.all([
            api.get('/services/'),
            api.get('/categories/')
        ])
        services.value = resSrv.data.results || resSrv.data
        categories.value = resCat.data.results || resCat.data
    } catch (e) {
        console.error(e)
    } finally {
        loading.value = false
    }
}

const openCategoryModal = () => {
    newCategory.value = ''
    showCategoryModal.value = true
}

const createCategory = async () => {
    savingCat.value = true
    try {
        await api.post('/categories/', { name: newCategory.value })
        const resCat = await api.get('/categories/')
        categories.value = resCat.data.results || resCat.data
        showCategoryModal.value = false
    } catch (e) {
        alert(t('common.error'))
    } finally {
        savingCat.value = false
    }
}

const computedTotal = computed(() => {
    let base = parseInt(form.value.base_price) || 0
    let m = parseInt(form.value.margin_value) || 0
    if (form.value.margin_type === 'fixed') return base + m
    return Math.round(base + (base * (m / 100)))
})

const openCreateModal = () => {
    isEditing.value = false
    editingId.value = null
    form.value = {
        name: '', category: categories.value[0]?.id || '', duration_minutes: 60,
        base_price: 1000, margin_type: 'fixed', margin_value: 0, is_combo: false
    }
    showCreateModal.value = true
}

const openComboModal = () => {
    isEditing.value = false
    editingId.value = null
    comboForm.value = {
        name: '', category: categories.value[0]?.id || '', total_price: 0, discount_strategy: 'owner_only'
    }
    selectedSubServices.value = [{ id: '', quantity: 1 }]
    mainIndex.value = 0
    showComboModal.value = true
}

const addComboItem = () => selectedSubServices.value.push({ id: '', quantity: 1 })
const removeComboItem = (idx) => selectedSubServices.value.splice(idx, 1)

const openEditModal = (srv) => {
    isEditing.value = true
    editingId.value = srv.id
    if (srv.is_combo) {
        comboForm.value = {
            name: srv.name,
            category: srv.category,
            total_price: srv.total_price,
            discount_strategy: srv.discount_strategy
        }
        selectedSubServices.value = srv.combo_items.map(i => ({ id: i.sub_service, quantity: i.quantity }))
        mainIndex.value = srv.combo_items.findIndex(i => i.is_main)
        if (mainIndex.value === -1) mainIndex.value = 0
        showComboModal.value = true
    } else {
        form.value = {
            name: srv.name,
            category: srv.category,
            duration_minutes: srv.duration_minutes,
            base_price: srv.base_price,
            margin_type: srv.margin_type,
            margin_value: srv.margin_value,
            is_combo: false
        }
        showCreateModal.value = true
    }
}

const submitCombo = async () => {
    if (selectedSubServices.value.some(i => !i.id)) {
        alert('Выберите все услуги в комбо')
        return
    }
    creating.value = true
    try {
        const payload = {
            ...comboForm.value,
            is_combo: true,
            duration_minutes: comboSumDuration.value,
            base_price: 0,
            margin_type: 'fixed',
            margin_value: 0,
            sub_services: selectedSubServices.value.map((s, idx) => ({
                sub_service: s.id,
                quantity: s.quantity || 1,
                is_main: mainIndex.value === idx
            }))
        }
        if (isEditing.value) {
            await api.patch(`/services/${editingId.value}/`, payload)
        } else {
            await api.post('/services/', payload)
        }
        await fetchData()
        showComboModal.value = false
        successMsg.value = t('common.save')
        setTimeout(() => successMsg.value = '', 3000)
    } catch (e) {
        alert(t('common.error'))
    } finally {
        creating.value = false
    }
}

const submitService = async () => {
    creating.value = true
    try {
        if (isEditing.value) {
            await api.patch(`/services/${editingId.value}/`, form.value)
        } else {
            await api.post('/services/', form.value)
        }
        await fetchData()
        showCreateModal.value = false
        successMsg.value = t('common.save')
        setTimeout(() => successMsg.value = '', 3000)
    } catch (e) {
        alert(e.response?.data?.error || t('common.error'))
    } finally {
        creating.value = false
    }
}

const startBooking = async (srv) => {
    activeService.value = srv
    bookingStep.value = 0
    bookingDate.value = getLocalDateStr()
    bookingForm.value = { client_name: '', client_phone: '', master_id: '', time: '' }
    showBookingModal.value = true
    
    try {
        const res = await api.get('/masters/working/', { params: { date: bookingDate.value } })
        workingMasters.value = res.data
    } catch (e) {
        console.error('Ошибка загрузки мастеров')
    }
}

// Watch bookingDate to refresh masters if step 0 is active or passed
watch(bookingDate, async (newVal) => {
    if (showBookingModal.value) {
        try {
            const res = await api.get('/masters/working/', { params: { date: newVal } })
            workingMasters.value = res.data
        } catch (e) { console.error(e) }
    }
})

const selectMaster = async (masterId) => {
    bookingForm.value.master_id = masterId
    bookingStep.value = 3
    slotsLoading.value = true
    try {
        const res = await api.get(`/masters/${masterId}/available-slots/`, {
            params: { date: bookingDate.value, service_id: activeService.value.id }
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
        const end_time = new Date(new Date(start_time).getTime() + activeService.value.duration_minutes * 60000).toISOString()
        
        await api.post('/appointments/', {
            master: bookingForm.value.master_id,
            service: activeService.value.id,
            start_time, end_time,
            client_name: bookingForm.value.client_name,
            client_phone: bookingForm.value.client_phone
        })
        showBookingModal.value = false
        successMsg.value = t('admin.bookingSuccess')
        setTimeout(() => successMsg.value = '', 3000)
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
.admin-services {
  padding: 20px 16px 100px;
}
.flex-between { display: flex; justify-content: space-between; align-items: center; }
.page-title { font-size: 24px; font-weight: 800; color: var(--text); }
.add-btn { background: var(--gold-gradient); border: none; border-radius: 50%; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; color: #fff; cursor: pointer; box-shadow: 0 4px 10px var(--gold-glow); }

.category-header { font-size: 15px; font-weight: 700; color: var(--muted); margin-bottom: 12px; letter-spacing: 0.5px; text-transform: uppercase; }

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
  background: var(--bg-secondary);
  border-radius: 16px;
  padding: 16px;
  margin-bottom: 12px;
  border: 1px solid var(--border);
}
.service-details-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 4px;
}
.service-actions-row {
    width: 100%;
}
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
.btn-zapis { background: rgba(59, 130, 246, 0.1); color: #3b82f6; border-color: #3b82f6; }

.service-top-row {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
}
.service-name { font-size: 16px; font-weight: 700; color: var(--text); flex: 1; }
.edit-icon-btn {
    background: var(--bg-secondary); border: 1px solid var(--border); color: var(--gold);
    display: flex; align-items: center; justify-content: center; padding: 8px; border-radius: 10px;
    cursor: pointer; transition: all 0.2s;
}
.edit-icon-btn:active { background: var(--gold-glow); }

.master-btns-row {
    display: flex; gap: 8px; width: 100%;
}

.date-selector { display: flex; gap: 8px; align-items: center; margin-bottom: 24px; overflow-x: auto; scrollbar-width: none; }
.date-selector::-webkit-scrollbar { display: none; }
.custom-date-wrapper { position: relative; }
.date-input-hidden { position: absolute; inset: 0; opacity: 0; cursor: pointer; }

.service-meta { display: flex; align-items: center; gap: 4px; font-size: 13px; color: var(--muted); }
.service-price { font-weight: 800; font-size: 17px; color: var(--gold); }

.master-card {
  padding: 12px 16px; border-radius: 12px; border: 1px solid var(--border);
  background: var(--bg-secondary); cursor: pointer; transition: all 0.2s; margin-bottom: 8px;
}
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

.empty-state { text-align: center; padding: 40px 20px; color: var(--muted); }
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

/* Modals */
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
.btn-sheet:disabled { opacity: 0.5; }
.btn-sheet-ghost { background: transparent; color: var(--muted); border: 1px solid var(--border); }

.form-label { display: block; font-size: 13px; font-weight: 600; color: var(--muted); margin-bottom: 6px; }
.form-input {
  width: 100%; padding: 12px 14px; border-radius: 12px; border: 1px solid var(--border);
  background: var(--bg-secondary); color: var(--text); font-size: 15px; outline: none;
  font-family: inherit;
}
.form-input:focus { border-color: var(--gold); }
.text-error { color: #dc2626; }
.text-gold { color: var(--gold); }
.text-muted { color: var(--muted); }
.bold { font-weight: 800; }

.total-price-box {
  background: var(--gold-glow);
  border: 1px solid var(--gold);
  padding: 12px 14px;
  border-radius: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.type-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
}
.type-btn {
    background: var(--bg-secondary); border: 2px solid var(--border); border-radius: 24px;
    padding: 20px 12px; display: flex; flex-direction: column; align-items: center; justify-content: center;
    color: var(--text); font-weight: 700; transition: all 0.2s;
    aspect-ratio: 1 / 1;
}
.type-btn:active { transform: scale(0.95); background: var(--border); }
.type-btn-combo { border-color: var(--gold); color: var(--gold); }
.type-icon-box {
    width: 56px; height: 56px; border-radius: 16px;
    background: var(--bg); display: flex; align-items: center; justify-content: center;
    margin-bottom: 12px;
}
.type-btn-combo .type-icon-box { background: var(--gold-glow); }

.sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border-width: 0;
}

.main-star-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 42px;
    height: 42px;
    border-radius: 12px;
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    transition: all 0.2s;
}
.main-star-btn.active {
    border-color: var(--gold);
    background: var(--gold-glow);
}

.combo-item-row { display: flex; gap: 8px; align-items: center; }
.remove-btn { background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 10px; width: 42px; height: 42px; display: flex; align-items: center; justify-content: center; color: var(--danger); }

.strat-pill {
    flex: 1; padding: 10px 4px; border-radius: 10px; border: 1px solid var(--border);
    background: var(--bg-secondary); color: var(--muted); font-size: 11px; font-weight: 700;
    transition: all 0.2s; text-align: center;
}
.strat-pill.active { background: var(--gold-gradient); color: #000; border-color: var(--gold); }

.combo-badge-mini {
    background: var(--gold-glow); color: var(--gold); border: 1px solid var(--gold);
    width: 20px; height: 20px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
}
</style>
