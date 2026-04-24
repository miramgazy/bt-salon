<template>
  <div class="admin-services">
    <div class="page-header flex-between mb-4">
      <h1 class="page-title">Услуги</h1>
      <button class="add-btn" @click="openCreateModal">
        <Icon icon="mdi:plus" width="24" />
      </button>
    </div>

    <!-- Category Filter Row -->
    <div class="category-scroll mb-6">
        <button 
           :class="['date-pill', 'flex-shrink-0', { active: selectedCategory === 'all' }]"
           @click="selectedCategory = 'all'"
        >Все</button>
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
       <p>Услуги пока не добавлены</p>
    </div>

    <div v-else class="services-list mt-4">
       <div v-for="srv in filteredServices" :key="srv.id" class="service-card">
          <div class="service-card-content">
             <div class="service-top-row">
                <div class="service-name">{{ srv.name }}</div>
                <div class="service-actions">
                   <button class="edit-icon-btn" @click.stop="openEditModal(srv)">
                      <Icon icon="mdi:pencil-outline" width="22" />
                   </button>
                </div>
             </div>
             <div class="service-details-row">
                <div class="service-meta">
                   <Icon icon="mdi:clock-outline" width="14" /> {{ srv.duration_minutes }} мин
                </div>
                <div class="service-price">
                   {{ srv.total_price }} ₸
                </div>
             </div>
             
             <div class="service-actions-row mt-3">
                <div class="master-btns-row">
                   <button class="btn-action btn-zapis" @click.stop="startBooking(srv)">
                      <Icon icon="mdi:calendar-plus" width="16" />
                      Запись
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
            <span>{{ isEditing ? 'Изменить услугу' : 'Новая услуга' }}</span>
            <Icon icon="mdi:close" width="24" @click="showCreateModal = false" class="cursor-pointer" />
        </div>
        
        <form @submit.prevent="submitService" class="mt-4 flex flex-col gap-4 overflow-y-auto pb-6">
          <div>
            <label class="form-label">Название услуги <span class="text-error">*</span></label>
            <input v-model="form.name" type="text" class="form-input" required />
          </div>
          <div>
            <label class="form-label flex-between">
               Категория <span class="text-error">*</span>
               <span class="text-xs text-gold cursor-pointer" @click="openCategoryModal">+ Новая</span>
            </label>
            <select v-model="form.category" class="form-input" required>
              <option value="" disabled>Выберите категорию</option>
              <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
            </select>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="form-label">Длит. (минут) <span class="text-error">*</span></label>
              <input v-model="form.duration_minutes" type="number" class="form-input" required />
            </div>
            <div>
              <label class="form-label">Базовая цена ₸ <span class="text-error">*</span></label>
              <input v-model="form.base_price" type="number" class="form-input" required />
            </div>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="form-label">Тип наценки</label>
              <select v-model="form.margin_type" class="form-input">
                <option value="fixed">Фикс (₸)</option>
                <option value="percent">Процент (%)</option>
              </select>
            </div>
            <div>
              <label class="form-label">Размер наценки</label>
              <input v-model="form.margin_value" type="number" class="form-input" />
            </div>
          </div>
          
          <div class="total-price-box mt-2">
            <span class="text-muted">Итого для клиента:</span>
            <span class="text-gold bold text-lg">{{ computedTotal }} ₸</span>
          </div>

          <button type="submit" class="btn-sheet mt-2" :disabled="creating">
             {{ creating ? 'Сохранение...' : 'Сохранить' }}
          </button>
        </form>
      </div>
    </div>

    <!-- Category Create Modal -->
    <div v-if="showCategoryModal" class="overlay" style="z-index: 1010" @click="showCategoryModal = false">
       <div class="sheet" @click.stop>
          <div class="sheet-title mb-4">Создать категорию</div>
          <input v-model="newCategory" type="text" class="form-input mb-4" placeholder="Название категории" />
          <button class="btn-sheet mb-2" @click="createCategory" :disabled="!newCategory.trim() || savingCat">
            {{ savingCat ? 'Сохранение...' : 'Сохранить категорию' }}
          </button>
          <button class="btn-sheet btn-sheet-ghost" @click="showCategoryModal = false">Отмена</button>
       </div>
    </div>

    <!-- Booking Modal (Wizard Step 2-4) -->
    <div v-if="showBookingModal" class="overlay" @click="showBookingModal = false">
      <div class="sheet h-80vh" @click.stop>
        <div class="sheet-title flex justify-between">
            <span>Запись: Шаг {{ bookingStep }}/4</span>
            <Icon icon="mdi:close" width="24" @click="showBookingModal = false" class="cursor-pointer" />
        </div>
        
        <div class="mt-4 flex flex-col gap-4 overflow-y-auto pb-6" style="flex: 1">
          <div class="p-3 bg-secondary rounded-xl text-sm mb-1">
             <b>Услуга:</b> {{ activeService?.name }}
          </div>

          <!-- Step 0: Date Selection -->
          <div v-if="bookingStep === 0">
             <label class="form-label mb-3">Выберите дату записи</label>
             <div class="date-selector mb-4">
                 <button 
                    :class="['date-pill', { active: isToday(bookingDate) }]" 
                    @click="setBookingDate('today')"
                 >Сегодня</button>
                 <button 
                    :class="['date-pill', { active: isTomorrow(bookingDate) }]" 
                    @click="setBookingDate('tomorrow')"
                 >Завтра</button>
                 <div class="custom-date-wrapper">
                    <button :class="['date-pill', { active: isCustomDate(bookingDate) }]">
                        {{ isCustomDate(bookingDate) ? formatDateShort(bookingDate) : 'Выбрать' }}
                    </button>
                    <input type="date" class="date-input-hidden" @change="onCustomDateChange" />
                 </div>
             </div>
             <button class="btn-sheet" @click="bookingStep = 2">Далее</button>
          </div>

          <!-- Step 2: Masters -->
          <div v-if="bookingStep === 2">
             <div class="p-3 mb-2 bg-[var(--gold-glow)] border border-[var(--gold)] rounded-xl text-sm flex justify-between items-center">
                <span><b>Дата:</b> {{ formatDateShort(bookingDate) }}</span>
                <span class="text-gold cursor-pointer font-bold" @click="bookingStep = 0">Изменить</span>
             </div>
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
                     Нет мастеров на сегодня.
                 </div>
             </div>
          </div>

          <!-- Step 3: Slots -->
          <div v-if="bookingStep === 3">
             <label class="form-label mb-2">Выберите время на сегодня</label>
             <div v-if="slotsLoading" class="spinner"></div>
             <div v-else-if="slots.length === 0" class="text-muted text-center py-4">
                 Доступных окон больше нет.
             </div>
             <div v-else class="slots-grid">
                 <div v-for="slot in slots" :key="slot.time"
                      class="slot-item"
                      :class="{ disabled: !slot.is_available, selected: bookingForm.time === slot.time }"
                      @click="if (slot.is_available) { bookingForm.time = slot.time; bookingStep = 4 }">
                     {{ slot.time }}
                 </div>
             </div>
             <button class="btn-sheet bg-secondary mt-4" @click="bookingStep = 2">Назад</button>
          </div>

          <!-- Step 4: Client Info -->
          <div v-if="bookingStep === 4">
             <form @submit.prevent="createAppointment" class="flex flex-col gap-4">
                 <div>
                    <label class="form-label">Имя клиента *</label>
                    <input v-model="bookingForm.client_name" type="text" class="form-input" required autofocus />
                 </div>
                 <div>
                    <label class="form-label">Телефон клиента *</label>
                    <input v-model="bookingForm.client_phone" type="text" class="form-input" required placeholder="+7 (___) ___-__-__" />
                 </div>
                 <div class="p-3 bg-secondary rounded-xl text-sm mb-2 opacity-80">
                    <div><b>Время:</b> Сегодня, {{ bookingForm.time }}</div>
                 </div>
                 <button type="submit" class="btn-sheet mt-2" :disabled="bookingLoading">
                    {{ bookingLoading ? 'Создание...' : 'Создать запись' }}
                 </button>
             </form>
             <button class="btn-sheet btn-sheet-ghost mt-2" @click="bookingStep = 3">Назад</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { Icon } from '@iconify/vue'
import api from '@/api'

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
    return new Date(d).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })
}

const showCreateModal = ref(false)
const isEditing = ref(false)
const editingId = ref(null)

const showCategoryModal = ref(false)
const newCategory = ref('')
const creating = ref(false)
const savingCat = ref(false)

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
        alert('Ошибка!')
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
        base_price: 1000, margin_type: 'fixed', margin_value: 0
    }
    showCreateModal.value = true
}

const openEditModal = (srv) => {
    isEditing.value = true
    editingId.value = srv.id
    form.value = {
        name: srv.name,
        category: srv.category,
        duration_minutes: srv.duration_minutes,
        base_price: srv.base_price,
        margin_type: srv.margin_type,
        margin_value: srv.margin_value
    }
    showCreateModal.value = true
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
    } catch (e) {
        alert(e.response?.data?.error || 'Ошибка!')
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
        alert('Запись успешно создана!')
    } catch (e) {
        alert('Ошибка!')
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

.date-pill {
  white-space: nowrap; padding: 8px 16px; border-radius: 20px;
  background: var(--bg-secondary); border: 1px solid var(--border);
  color: var(--muted); font-size: 13px; font-weight: 600; cursor: pointer; transition: all 0.2s;
}
.date-pill.active {
  background: var(--gold-gradient); color: #000; border-color: var(--gold);
  box-shadow: 0 4px 10px var(--gold-glow);
}

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
</style>
