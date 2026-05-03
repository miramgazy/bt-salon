<template>
  <div class="mx-auto max-w-[85rem]">
    <!-- Breadcrumb -->
    <div class="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <h2 class="text-title-md2 font-bold text-black dark:text-white">Календарь бронирований</h2>
      <nav>
        <ol class="flex items-center gap-2">
          <li><router-link class="font-medium" to="/admin/calendar">Dashboard /</router-link></li>
          <li class="font-medium text-primary">Календарь</li>
        </ol>
      </nav>
    </div>

    <div v-if="loading && !calendarDays.length" class="flex h-60 items-center justify-center rounded-sm border border-stroke bg-white shadow-default dark:border-strokedark dark:bg-bg-dark-2">
      <div class="h-16 w-16 animate-spin rounded-full border-4 border-solid border-primary border-t-transparent"></div>
    </div>

    <div v-else class="rounded-sm border border-stroke bg-white shadow-default dark:border-strokedark dark:bg-bg-dark-2">
      <!-- Calendar Header -->
      <div class="flex flex-wrap items-center justify-between border-b border-stroke py-4 px-4 dark:border-strokedark sm:px-6 xl:px-7.5">
        <div class="flex items-center gap-4">
          <button @click="previousMonth" class="flex h-8 w-8 items-center justify-center rounded border border-stroke hover:bg-gray-100 dark:border-strokedark dark:hover:bg-meta-4 transition-colors">
            <Icon icon="mdi:chevron-left" width="20" />
          </button>
          <div class="flex items-center gap-2">
            <select v-model="selectedMonth" @change="onDateChange" class="bg-transparent font-bold text-black dark:text-white outline-none cursor-pointer hover:text-primary transition-colors">
              <option v-for="(month, index) in months" :key="index" :value="index">{{ month }}</option>
            </select>
            <select v-model="selectedYear" @change="onDateChange" class="bg-transparent font-bold text-black dark:text-white outline-none cursor-pointer hover:text-primary transition-colors">
              <option v-for="year in yearRange" :key="year" :value="year">{{ year }}</option>
            </select>
          </div>
          <button @click="nextMonth" class="flex h-8 w-8 items-center justify-center rounded border border-stroke hover:bg-gray-100 dark:border-strokedark dark:hover:bg-meta-4 transition-colors">
            <Icon icon="mdi:chevron-right" width="20" />
          </button>
        </div>
        <div class="flex items-center gap-3">
          <button @click="fetchAll" class="text-body hover:text-primary transition-colors" title="Обновить">
            <Icon icon="mdi:refresh" width="20" :class="{'animate-spin': loading}" />
          </button>
          <button @click="openCreateModal(null)" class="rounded bg-primary py-2 px-4 text-sm font-medium text-white hover:bg-opacity-90">
            <Icon icon="mdi:plus" class="inline mr-1" width="16" /> Новая запись
          </button>
        </div>
      </div>

      <!-- Calendar Grid -->
      <div class="p-4 sm:p-6 xl:p-7.5">
        <div class="grid grid-cols-7 border-t border-l border-stroke dark:border-strokedark">
          <!-- Weekday headers -->
          <div v-for="day in weekDays" :key="day"
            class="flex h-10 items-center justify-center border-r border-b border-stroke bg-gray-2 text-xs font-bold uppercase tracking-wider text-body dark:border-strokedark dark:bg-meta-4 dark:text-bodydark">
            {{ day }}
          </div>

          <!-- Day cells -->
          <div
            v-for="day in calendarDays"
            :key="day.dateStr"
            class="relative border-r border-b border-stroke dark:border-strokedark transition-all cursor-pointer select-none flex flex-col"
            :class="[
              'h-[130px] sm:h-[150px]',
              day.isOtherMonth ? 'bg-gray-100/30 dark:bg-meta-4/10' : 'hover:bg-gray-50/70 dark:hover:bg-meta-4/20',
              day.isToday ? 'bg-primary/5 dark:bg-primary/10' : ''
            ]"
            @click="openDayModal(day)"
            @dblclick.stop="openCreateModal(day.dateStr)"
          >
            <div class="flex justify-between items-start p-2 shrink-0">
              <span
                class="inline-flex h-6 w-6 items-center justify-center text-sm font-semibold"
                :class="[
                  day.isToday ? 'rounded-full bg-primary text-white' : 'text-black dark:text-white',
                  day.isOtherMonth ? 'opacity-30' : ''
                ]"
              >
                {{ day.dayNumber }}
              </span>
              <span v-if="day.totalCount > 0" class="text-[10px] font-bold text-primary bg-primary/10 px-1.5 py-0.5 rounded">
                {{ day.totalCount }}
              </span>
            </div>
 
            <!-- Per-master blocks -->
            <div class="px-1.5 pb-1.5 flex-1 overflow-y-auto custom-scrollbar flex flex-col gap-1">
              <div
                v-for="ms in day.masterSummaries"
                :key="ms.master.id"
                class="rounded px-1.5 py-1 border shrink-0"
                :style="{ borderColor: ms.master.color, backgroundColor: ms.master.color + '15' }"
              >
                <div class="flex items-center justify-between gap-1 mb-1">
                  <span class="text-[10px] font-bold truncate" :style="{ color: ms.master.color }">
                    {{ ms.master.first_name }}
                  </span>
                  <span class="text-[10px] font-semibold shrink-0" :style="{ color: ms.master.color }">
                    {{ ms.count }}
                  </span>
                </div>
                <!-- Utilization bar -->
                <div class="h-1 rounded-full bg-black/10 overflow-hidden">
                  <div
                    class="h-1 rounded-full transition-all duration-500"
                    :style="{ width: ms.utilization + '%', backgroundColor: ms.master.color }"
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Day View Modal (single click) -->
    <div v-if="showDayModal && selectedDay" class="fixed inset-0 z-[9998] flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm" @click.self="showDayModal = false">
      <div class="w-full max-w-[95%] xl:max-w-[1200px] rounded-xl bg-white dark:bg-bg-dark-2 shadow-2xl overflow-hidden h-[85vh] flex flex-col">
        <!-- Modal Header -->
        <div class="flex items-center justify-between border-b border-stroke px-6 py-4 dark:border-strokedark shrink-0">
          <div>
            <h3 class="text-xl font-bold text-black dark:text-white">{{ formatDateFull(selectedDay.dateStr) }}</h3>
            <p class="text-sm text-body">{{ selectedDay.totalCount }} записей на этот день</p>
          </div>
          <div class="flex items-center gap-3">
            <button @click="openShiftModal(selectedDay.dateStr)" class="flex items-center gap-1 rounded border border-stroke py-1.5 px-3 text-sm font-medium text-black dark:text-white hover:bg-gray-100 dark:hover:bg-meta-4 transition-colors">
              <Icon icon="mdi:calendar-clock" width="16" /> Открыть смену
            </button>
            <button @click="openCreateModal(selectedDay.dateStr)" class="flex items-center gap-1 rounded bg-primary py-1.5 px-3 text-sm font-medium text-white hover:bg-opacity-90">
              <Icon icon="mdi:plus" width="16" /> Новая запись
            </button>
            <button @click="showDayModal = false" class="text-body hover:text-danger">
              <Icon icon="mdi:close" width="24" />
            </button>
          </div>
        </div>
        
        <!-- Modal Body: Draggable Grid -->
        <div class="overflow-hidden flex-1 relative flex flex-col bg-gray-50 dark:bg-meta-4">
          <div v-if="selectedDay.masterSchedules.length === 0" class="flex flex-col items-center justify-center py-16 text-center h-full">
            <Icon icon="mdi:calendar-blank-outline" width="48" class="text-body mb-3" />
            <p class="text-body">На этот день нет открытых смен или записей</p>
          </div>

          <div v-else class="flex-1 overflow-auto custom-scrollbar relative p-4 sm:p-6">
            <div class="flex flex-col gap-6">
              
              <!-- Masters Rows -->
              <div 
                v-for="ms in selectedDay.masterSchedules" 
                :key="ms.master.id" 
                class="flex flex-col md:flex-row gap-4 bg-white dark:bg-bg-dark-2 rounded-xl border border-stroke dark:border-strokedark p-4 shadow-sm"
              >
                <!-- Master Info -->
                <div class="w-full md:w-[180px] shrink-0 border-b md:border-b-0 md:border-r border-stroke dark:border-strokedark pb-4 md:pb-0 pr-0 md:pr-4 flex items-center md:items-start justify-between md:flex-col"
                  :class="{'bg-warning/5': ms.master.is_virtual}">
                  <div class="flex items-center gap-3">
                    <div class="h-12 w-12 rounded-full flex items-center justify-center text-white text-lg font-bold shrink-0 shadow-sm"
                      :style="{ backgroundColor: ms.master.is_virtual ? '#FF9C00' : ms.master.color }">
                      <Icon v-if="ms.master.is_virtual" icon="mdi:account-group" width="24" />
                      <span v-else>{{ ms.master.first_name[0] }}</span>
                    </div>
                    <div>
                      <h4 class="font-bold text-black dark:text-white">{{ ms.master.first_name }}</h4>
                      <p v-if="ms.shift" class="text-xs text-body mt-0.5">
                        <Icon icon="mdi:clock-outline" class="inline" /> {{ ms.shift.work_start?.slice(0,5) }} - {{ ms.shift.work_end?.slice(0,5) }}
                      </p>
                      <p v-else-if="!ms.master.is_virtual" class="text-xs text-warning mt-0.5">Смена закрыта</p>
                      <p v-if="ms.master.is_virtual" class="text-[10px] uppercase font-bold text-warning-600 mt-0.5">Очередь</p>
                    </div>
                  </div>
                </div>

                <!-- Slots Flex Container -->
                <div class="flex-1">
                  <div v-if="!ms.shift" class="text-sm text-body italic py-2">Нет смены на этот день</div>
                  <div v-else class="flex flex-wrap gap-2">
                    
                    <!-- Render each slot -->
                    <div 
                      v-for="slot in ms.slots" 
                      :key="ms.master.id + slot.time"
                      class="relative w-[82px] h-[40px] rounded-lg border transition-colors flex items-center justify-center"
                      :class="[
                        draggedOverSlot === ms.master.id + slot.time ? 'bg-primary/20 border-primary border-dashed' : 'border-stroke dark:border-strokedark bg-gray-50 dark:bg-meta-4',
                        hasAppt(ms.appointments, slot.time) ? 'border-transparent bg-transparent' : 'hover:border-primary/50 cursor-pointer',
                        slot.isLunch && !hasAppt(ms.appointments, slot.time) ? 'bg-warning/20 border-warning/30' : ''
                      ]"
                      :title="slot.isLunch ? 'Обеденный перерыв' : ''"
                      @dragover.prevent="onDragOver(ms.master.id + slot.time)"
                      @dragleave="onDragLeave"
                      @drop="onDrop(slot, ms.master.id)"
                      @click="handleSlotClick(ms, slot)"
                    >
                      <!-- Empty Slot State -->
                      <span v-if="!hasAppt(ms.appointments, slot.time)" class="text-[10px] font-medium text-body pointer-events-none">
                        {{ slot.time }}
                      </span>
                      
                      <!-- Appointment Card (if any starts in this slot) -->
                      <div 
                        v-if="hasAppt(ms.appointments, slot.time)"
                        :style="{ 
                          borderColor: getApptAt(ms.appointments, slot.time).appointment_type === 'combo_sub' ? '#FF9C00' : ms.master.color + '90', 
                          backgroundColor: getApptAt(ms.appointments, slot.time).appointment_type === 'combo_sub' ? '#FF9C0020' : ms.master.color + '20' 
                        }"
                        class="absolute inset-0 z-10 rounded-lg p-1 shadow-sm text-xs cursor-grab active:cursor-grabbing overflow-hidden border transition-all duration-200 hover:shadow-md flex flex-col justify-center group/card"
                        :class="[
                          isRelated(getApptAt(ms.appointments, slot.time)) ? 'ring-2 ring-primary ring-offset-1 z-20 shadow-lg scale-[1.02] !bg-primary/20' : '',
                          isForgotten(getApptAt(ms.appointments, slot.time), ms.master) ? 'animate-wobble border-danger border-2' : ''
                        ]"
                        draggable="true"
                        @dragstart="onDragStart($event, getApptAt(ms.appointments, slot.time), ms.master.id)"
                        @click.stop="openEditModal(getApptAt(ms.appointments, slot.time))"
                        @mouseenter="handleApptMouseEnter(getApptAt(ms.appointments, slot.time))"
                        @mouseleave="activeComboParentId = null"
                      >
                        <!-- Delete button -->
                        <button
                          class="absolute top-0.5 right-0.5 z-20 text-danger/60 hover:text-danger opacity-0 group-hover/card:opacity-100 transition-opacity"
                          @click.stop="deleteAppt(getApptAt(ms.appointments, slot.time))"
                          title="Удалить запись"
                        >
                          <Icon icon="mdi:trash-can-outline" width="11" />
                        </button>
                        
                        <div class="flex items-center gap-1 mb-0.5">
                          <Icon v-if="getApptAt(ms.appointments, slot.time).is_combo" 
                                icon="mdi:link-variant" 
                                :class="getApptAt(ms.appointments, slot.time).appointment_type === 'combo_sub' ? 'text-warning' : 'text-primary'"
                                width="10" />
                          <Icon v-if="getApptAt(ms.appointments, slot.time).client_confirmation === 'yes'" 
                                icon="mdi:check-circle" 
                                class="text-success" 
                                width="10" />
                          <p class="font-bold text-black dark:text-white truncate text-[9px] leading-tight">{{ formatTime(getApptAt(ms.appointments, slot.time).start_time) }}</p>
                        </div>
                        <p class="font-medium truncate text-[9px] text-body leading-tight" v-if="getApptAt(ms.appointments, slot.time).client_detail?.full_name">
                          {{ getApptAt(ms.appointments, slot.time).client_detail.full_name }}
                        </p>
                        <p class="truncate text-[8px] opacity-70 leading-tight">
                          {{ getApptAt(ms.appointments, slot.time).display_title }}
                        </p>
                      </div>
 
                    </div>
 
                  </div>
                </div>
              </div>

            </div>
          </div>
        </div>
      </div>
    </div>

    <AppointmentCreateModal
      :show="showCreateModal"
      :date="createModalDate"
      :prefilledMasterId="prefilledMasterId"
      :prefilledTime="prefilledTime"
      @close="showCreateModal = false"
      @success="onBookingSuccess"
    />

    <!-- Edit Appointment Modal -->
    <AppointmentEditModal
      :show="showEditModal"
      :appointment="editModalAppt"
      @close="showEditModal = false"
      @success="onBookingSuccess"
    />

    <!-- Quick Shift Modal -->
    <QuickShiftModal
      :show="showShiftModal"
      :date="shiftModalDate"
      @close="showShiftModal = false"
      @success="onShiftSuccess"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { Icon } from '@iconify/vue'
import api from '../../api'
import { format, startOfMonth, endOfMonth, eachDayOfInterval, isToday, isSameMonth, getDay, addDays, subDays } from 'date-fns'
import { ru } from 'date-fns/locale'
import AppointmentCreateModal from '../../components/modals/AppointmentCreateModal.vue'
import AppointmentEditModal from '../../components/modals/AppointmentEditModal.vue'
import QuickShiftModal from '../../components/modals/QuickShiftModal.vue'

const bookings = ref([])
const masters = ref([])
const shifts = ref([])
const organization = ref(null)
const loading = ref(true)

const currentDate = ref(new Date())
const selectedMonth = ref(currentDate.value.getMonth())
const selectedYear = ref(currentDate.value.getFullYear())

const showDayModal = ref(false)
const selectedDay = ref(null)

const showCreateModal = ref(false)
const createModalDate = ref('')
const prefilledMasterId = ref('')
const prefilledTime = ref('')

// Timeline editing state
const showEditModal = ref(false)
const editModalAppt = ref(null)
const draggedAppt = ref(null)
const draggedOverSlot = ref(null)
const activeComboParentId = ref(null)

const isRelated = (appt) => {
  if (!activeComboParentId.value) return false
  const pid = appt.parent || appt.id
  return pid === activeComboParentId.value || appt.id === activeComboParentId.value
}

const handleApptMouseEnter = (appt) => {
  if (appt.appointment_type === 'single') return
  activeComboParentId.value = appt.parent || appt.id
}

const isForgotten = (appt, master) => {
  if (!appt || appt.appointment_type !== 'combo_sub' || !master.is_virtual) return false
  if (appt.status === 'done' || appt.status === 'cancelled') return false
  const start = new Date(appt.start_time)
  const now = new Date()
  // If appointment started more than 10 minutes ago and still on virtual master
  return start < new Date(now.getTime() - 10 * 60 * 1000)
}

// Shift modal state
const showShiftModal = ref(false)
const shiftModalDate = ref('')

const openShiftModal = (dateStr) => {
  shiftModalDate.value = dateStr
  showShiftModal.value = true
}

const onShiftSuccess = () => {
  showShiftModal.value = false
  fetchAll()
}

const months = ['Январь','Февраль','Март','Апрель','Май','Июнь','Июль','Август','Сентябрь','Октябрь','Ноябрь','Декабрь']
const currentYearNum = new Date().getFullYear()
const yearRange = Array.from({ length: 3 }, (_, i) => currentYearNum + i - 1)
const weekDays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']

const currentMonthStr = computed(() => {
  return `${selectedYear.value}-${String(selectedMonth.value + 1).padStart(2, '0')}`
})

const fetchAll = async () => {
  try {
    loading.value = true
    
    // Calculate full visible range for the calendar grid
    const startOfMonthDate = startOfMonth(currentDate.value)
    const endOfMonthDate = endOfMonth(currentDate.value)
    let gridStartDate = startOfMonthDate
    const dow = getDay(startOfMonthDate)
    if (dow !== 1) gridStartDate = subDays(startOfMonthDate, dow === 0 ? 6 : dow - 1)
    
    let gridEndDate = endOfMonthDate
    const lastDow = getDay(endOfMonthDate)
    if (lastDow !== 0) gridEndDate = addDays(endOfMonthDate, 7 - lastDow)
    
    const dateFrom = format(gridStartDate, 'yyyy-MM-dd')
    const dateTo = format(gridEndDate, 'yyyy-MM-dd')

    const [apptRes, mastersRes, shiftsRes, orgRes] = await Promise.all([
      api.get('/api/appointments/', { params: { date_from: dateFrom, date_to: dateTo, page_size: 1000 } }),
      api.get('/api/masters/'),
      api.get('/api/masters/shifts/', { params: { date_from: dateFrom, date_to: dateTo, page_size: 1000 } }),
      api.get('/api/organization/')
    ])
    bookings.value = apptRes.data.results || apptRes.data || []
    masters.value = mastersRes.data.results || mastersRes.data || []
    shifts.value = shiftsRes.data.results || shiftsRes.data || []
    organization.value = orgRes.data

    // If day modal is open, refresh selected day
    if (showDayModal.value && selectedDay.value) {
      const updatedDay = calendarDays.value.find(d => d.dateStr === selectedDay.value.dateStr)
      if (updatedDay) selectedDay.value = updatedDay
    }

  } catch (err) {
    console.error('Error fetching calendar data:', err)
    bookings.value = []
  } finally {
    loading.value = false
  }
}

// Build maps for efficient lookup
const mastersMap = computed(() => {
  const map = {}
  masters.value.forEach(m => { map[m.id] = m })
  return map
})

const shiftsMap = computed(() => {
  const map = {}
  shifts.value.forEach(s => {
    const key = `${s.master}-${s.date}`
    map[key] = s
  })
  return map
})

const timeToMinutes = (timeStr) => {
  if (!timeStr) return 0
  if (timeStr.includes('T')) {
    const timePart = timeStr.split('T')[1].substring(0, 5)
    const [h, m] = timePart.split(':').map(Number)
    return h * 60 + m
  }
  const [h, m] = timeStr.slice(0, 5).split(':').map(Number)
  return h * 60 + m
}

const hasAppt = (appts, slotStr) => {
  return appts.some(a => {
    if(!a.start_time) return false
    const timePart = a.start_time.split('T')[1].substring(0, 5)
    return timePart === slotStr
  })
}

const getApptAt = (appts, slotStr) => {
  return appts.find(a => {
    if(!a.start_time) return false
    const timePart = a.start_time.split('T')[1].substring(0, 5)
    return timePart === slotStr
  })
}

// Drag & Drop Handlers
const onDragStart = (e, appt, masterId) => {
  draggedAppt.value = { ...appt, _fromMasterId: masterId }
  // Required for Firefox compatibility
  e.dataTransfer.setData('text/plain', appt.id)
  e.dataTransfer.effectAllowed = 'move'
}

const onDragOver = (slotId) => {
  if (!draggedAppt.value) return
  draggedOverSlot.value = slotId
}

const onDragLeave = () => {
  draggedOverSlot.value = null
}

const onDrop = (slot, masterId) => {
  if (!draggedAppt.value) return
  const timeStr = typeof slot === 'string' ? slot : slot.time
  draggedOverSlot.value = null
  
  // Check for lunch break
  const masterSched = selectedDay.value.masterSchedules.find(m => m.master.id === masterId)
  if (masterSched && masterSched.shift && isLunch(timeStr, masterSched.shift)) {
    alert('Это время зарезервировано под обеденный перерыв мастера. Перенос невозможен.')
    draggedAppt.value = null
    return
  }

  const appt = draggedAppt.value
  
  openEditModal({
    ...appt,
    master: masterId, // potentially moved to new row
    start_time: `${selectedDay.value.dateStr}T${timeStr}:00`
  })
  
  draggedAppt.value = null
}

const handleSlotClick = (ms, slot) => {
  if (hasAppt(ms.appointments, slot.time)) return
  if (slot.isLunch) {
    alert('Это время зарезервировано под обеденный перерыв мастера.')
    return
  }
  openCreateModalWithPrefill(ms.master.id, slot.time)
}

const isLunch = (timeStr, shift) => {
  if (!shift || !shift.lunch_start || !shift.lunch_end) return false
  const t = timeToMinutes(timeStr)
  const lStart = timeToMinutes(shift.lunch_start)
  const lEnd = timeToMinutes(shift.lunch_end)
  return t >= lStart && t < lEnd
}

const openEditModal = (appt) => {
  editModalAppt.value = appt
  showEditModal.value = true
}

const deleteAppt = async (appt) => {
  const clientName = appt.client_detail?.full_name || 'этот клиент'
  const time = formatTime(appt.start_time)
  if (!confirm(`Удалить запись на ${time} (${clientName})?\n\nЭто действие нельзя отменить.`)) return
  try {
    await api.delete(`/api/appointments/${appt.id}/`)
    await fetchAll()
  } catch (err) {
    console.error('Ошибка удаления:', err)
    alert('Не удалось удалить запись. Попробуйте снова.')
  }
}

const onBookingSuccess = () => fetchAll()

const calendarDays = computed(() => {
  const start = startOfMonth(currentDate.value)
  const end = endOfMonth(currentDate.value)
  let startDate = start
  const dow = getDay(start)
  if (dow !== 1) startDate = subDays(start, dow === 0 ? 6 : dow - 1)
  let endDate = end
  const lastDow = getDay(end)
  if (lastDow !== 0) endDate = addDays(end, 7 - lastDow)
  const days = eachDayOfInterval({ start: startDate, end: endDate })

  return days.map(date => {
    const dateStr = format(date, 'yyyy-MM-dd')

    // appointments for this day
    const dayAppts = bookings.value.filter(b => {
      if (!b.start_time) return false
      return b.start_time.split('T')[0] === dateStr
    })

    // Group by master
    const byMaster = {}
    dayAppts.forEach(appt => {
      const mid = appt.master
      if (!byMaster[mid]) byMaster[mid] = []
      byMaster[mid].push(appt)
    })

    // Build master summaries for the cell
    const masterSummaries = []
    Object.entries(byMaster).forEach(([mid, appts]) => {
      const master = mastersMap.value[mid]
      if (!master) return
      const shift = shiftsMap.value[`${mid}-${dateStr}`]
      const utilization = calcUtilization(appts, shift)
      masterSummaries.push({ master, count: appts.length, utilization })
    })

    // Also add masters with open shifts but no appointments (show in modal only)
    const shiftsToday = shifts.value.filter(s => s.date === dateStr && s.is_open)
    shiftsToday.forEach(s => {
      const mid = s.master
      if (!byMaster[mid]) {
        const master = mastersMap.value[mid]
        if (master) masterSummaries.push({ master, count: 0, utilization: 0 })
      }
    })

    // Build full schedule for modal
    const allMastersOnDay = new Set([
      ...Object.keys(byMaster).map(Number),
      ...shiftsToday.map(s => s.master)
    ])
    const masterSchedules = [...allMastersOnDay].map(mid => {
      const master = mastersMap.value[mid]
      if (!master) return null
      const appts = (byMaster[mid] || []).sort((a, b) => new Date(a.start_time) - new Date(b.start_time))
      const shift = shiftsMap.value[`${mid}-${dateStr}`]
      
      const slots = []
      if (shift && shift.work_start && shift.work_end) {
         let start = timeToMinutes(shift.work_start)
         let end = timeToMinutes(shift.work_end)
         const step = organization.value?.slot_duration || 30
         start = Math.floor(start / step) * step
         end = Math.ceil(end / step) * step
         for(let m = start; m < end; m += step) {
           const hh = String(Math.floor(m / 60)).padStart(2, '0')
           const mm = String(m % 60).padStart(2, '0')
           const timeStr = `${hh}:${mm}`
           slots.push({
             time: timeStr,
             isLunch: isLunch(timeStr, shift)
           })
         }
      }

      return { master, appointments: appts, shift, slots, utilization: calcUtilization(appts, shift) }
    }).filter(Boolean).sort((a, b) => {
      // Virtual masters always last
      if (a.master.is_virtual && !b.master.is_virtual) return 1
      if (!a.master.is_virtual && b.master.is_virtual) return -1
      return a.master.first_name.localeCompare(b.master.first_name)
    })

    return {
      date,
      dateStr,
      dayNumber: date.getDate(),
      isToday: isToday(date),
      isOtherMonth: !isSameMonth(date, currentDate.value),
      totalCount: dayAppts.length,
      masterSummaries: masterSummaries.sort((a, b) => a.master.first_name.localeCompare(b.master.first_name)),
      masterSchedules
    }
  })
})

const calcUtilization = (appts, shift) => {
  if (!shift || !shift.work_start || !shift.work_end) {
    return Math.min(appts.length * 12.5, 100)
  }
  let shiftMin = timeToMinutes(shift.work_end) - timeToMinutes(shift.work_start)
  if (shift.lunch_start && shift.lunch_end) {
    shiftMin -= (timeToMinutes(shift.lunch_end) - timeToMinutes(shift.lunch_start))
  }
  if (shiftMin <= 0) return 0
  const bookedMin = appts.reduce((sum, a) => {
    if (!a.start_time || !a.end_time) return sum
    return sum + (new Date(a.end_time) - new Date(a.start_time)) / 60000
  }, 0)
  return Math.min(Math.round((bookedMin / shiftMin) * 100), 100)
}

const openDayModal = (day) => {
  selectedDay.value = day
  showDayModal.value = true
}

const openCreateModal = (dateStr) => {
  showDayModal.value = false
  createModalDate.value = dateStr || format(currentDate.value, 'yyyy-MM-dd')
  prefilledMasterId.value = ''
  prefilledTime.value = ''
  showCreateModal.value = true
}

const openCreateModalWithPrefill = (masterId, timeStr) => {
  showDayModal.value = false
  createModalDate.value = selectedDay.value.dateStr
  prefilledMasterId.value = masterId
  prefilledTime.value = timeStr
  showCreateModal.value = true
}

const formatTime = (timeStr) => {
  if (!timeStr) return ''
  if (timeStr.includes('T')) {
    return timeStr.split('T')[1].substring(0, 5)
  }
  return timeStr
}

const formatDateFull = (dateStr) => {
  if (!dateStr) return ''
  try {
    return format(new Date(dateStr), 'd MMMM yyyy', { locale: ru })
  } catch { return dateStr }
}

const statusLabel = (s) => {
  const map = { pending: 'Ожидает', confirmed: 'Подтв.', cancelled: 'Отмена', done: 'Готово' }
  return map[s] || s
}

const previousMonth = () => {
  if (selectedMonth.value === 0) { selectedYear.value--; selectedMonth.value = 11 }
  else selectedMonth.value--
  onDateChange()
}

const nextMonth = () => {
  if (selectedMonth.value === 11) { selectedYear.value++; selectedMonth.value = 0 }
  else selectedMonth.value++
  onDateChange()
}

const onDateChange = () => {
  currentDate.value = new Date(selectedYear.value, selectedMonth.value, 1)
  fetchAll()
}

watch(currentDate, (newDate) => {
  selectedMonth.value = newDate.getMonth()
  selectedYear.value = newDate.getFullYear()
}, { immediate: true })

let socket = null
const connectWebSocket = () => {
  if (socket || !organization.value?.id) return
  
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const host = window.location.host
  const url = `${protocol}//${host}/ws/appointments/${organization.value.id}/`
  
  socket = new WebSocket(url)
  
  socket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      if (data.type === 'appointment_update') {
        fetchAll()
      }
    } catch (e) {
      console.error('WS parsing error', e)
    }
  }
  
  socket.onclose = () => {
    socket = null
    setTimeout(connectWebSocket, 5000)
  }
  
  socket.onerror = (err) => {
    console.error('WS error', err)
    socket.close()
  }
}

onMounted(async () => {
  await fetchAll()
  connectWebSocket()
})
</script>

<style scoped>
.text-title-md2 {
  font-size: 1.625rem;
  line-height: 2.125rem;
}
.custom-scrollbar::-webkit-scrollbar { height: 8px; width: 8px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }
.dark .custom-scrollbar::-webkit-scrollbar-thumb { background: #475569; }

@keyframes wobble {
  0%, 100% { transform: rotate(0deg); }
  25% { transform: rotate(-1deg); }
  75% { transform: rotate(1deg); }
}
.animate-wobble {
  animation: wobble 0.3s ease-in-out infinite;
}
</style>
