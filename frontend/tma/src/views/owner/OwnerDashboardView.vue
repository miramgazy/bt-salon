<template>
  <div class="owner-dashboard">
    <!-- Fixed Period Bar at the top -->
    <div class="fixed-period-bar">
      <div class="period-controls">
        <select class="period-select" v-model="periodId" @change="handlePeriodChange">
          <option v-for="p in periods" :key="p.id" :value="p.id">{{ p.label }}</option>
        </select>
        <div class="date-row" v-if="periodId === 'custom'">
          <input type="date" v-model="customStart" @change="handlePeriodChange" class="mini-date" />
          <span class="dash">-</span>
          <input type="date" v-model="customEnd" @change="handlePeriodChange" class="mini-date" />
        </div>
      </div>
    </div>

    <div class="main-content" v-if="!loading" style="margin-top: 60px; padding-bottom: 30px;">
      <!-- ══ OVERVIEW (ГЛАВНАЯ) ══ -->
      <div v-if="activeTab === 'overview'" class="fade-up">
        <div class="kpi-grid">
          <div class="kpi jade">
            <div class="kpi-label">Выручка</div>
            <div class="kpi-val jade">{{ formatM(data.summary.revenue) }} ₸</div>
            <div :class="['kpi-sub', deltaClass(data.summary.revenue, data.summary.prev_revenue)]">
              {{ deltaIcon(data.summary.revenue, data.summary.prev_revenue) }} 
              {{ deltaPercent(data.summary.revenue, data.summary.prev_revenue) }}% к пред.
            </div>
          </div>
          <div class="kpi crimson">
            <div class="kpi-label">Расходы</div>
            <div class="kpi-val crimson">{{ formatM(data.summary.expenses) }} ₸</div>
            <div class="kpi-sub neutral">Фикс: {{ formatM(totalFixedExp) }} · Пер: {{ formatM(totalVarExp) }}</div>
          </div>
          <div class="kpi gold">
            <div class="kpi-label">Чистая прибыль</div>
            <div :class="['kpi-val', data.summary.profit >= 0 ? 'jade' : 'crimson']">{{ formatM(data.summary.profit) }} ₸</div>
            <div :class="['kpi-sub', deltaClass(data.summary.profit, data.summary.prev_profit)]">
               {{ deltaIcon(data.summary.profit, data.summary.prev_profit) }} 
               {{ deltaPercent(data.summary.profit, data.summary.prev_profit) }}%
            </div>
          </div>
          <div class="kpi">
            <div class="kpi-label">Маржа</div>
            <div :class="['kpi-val', marginClass(data.summary.margin)]">{{ data.summary.margin }}%</div>
            <div class="kpi-sub neutral">{{ marginLabel(data.summary.margin) }}</div>
          </div>
          <!-- Extra Stats -->
          <div class="kpi" style="grid-column: 1 / -1">
             <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                   <div class="kpi-label">Средний чек</div>
                   <div class="kpi-val">{{ formatM(data.summary.avg_check) }} ₸</div>
                </div>
                <div style="text-align: right">
                   <div class="kpi-label">Клиентов</div>
                   <div class="kpi-val gold">{{ data.summary.clients_count || 0 }}</div>
                </div>
             </div>
          </div>
        </div>

        <div class="chart-card">
          <div class="chart-label">Структура маржи</div>
          <div class="gauge-wrap">
            <div class="gauge-row">
              <div class="gauge-label">Выручка</div>
              <div class="gauge-track"><div class="gauge-fill" style="width:100%; background:#22a060"></div></div>
              <div class="gauge-pct">{{ formatM(data.summary.revenue) }}</div>
            </div>
            <div class="gauge-row">
              <div class="gauge-label">Расходы</div>
              <div class="gauge-track">
                <div class="gauge-fill" :style="{ width: expPercent + '%', background:'#c0392b' }"></div>
              </div>
              <div class="gauge-pct">{{ expPercent }}%</div>
            </div>
            <div class="gauge-row">
              <div class="gauge-label">Прибыль</div>
              <div class="gauge-track">
                <div class="gauge-fill" :style="{ width: data.summary.margin + '%', background:'var(--gold)' }"></div>
              </div>
              <div class="gauge-pct">{{ data.summary.margin }}%</div>
            </div>
          </div>
        </div>

        <div class="chart-card">
          <div class="chart-label">Выручка и расходы по дням</div>
          <apexchart type="area" height="180" :options="areaChartOptions" :series="areaChartSeries"></apexchart>
        </div>

        <div class="chart-card">
          <div class="chart-label">Прибыль по дням</div>
          <apexchart type="bar" height="140" :options="profitBarOptions" :series="profitBarSeries"></apexchart>
        </div>

        <div class="chart-card">
           <div class="chart-label">Распределение выручки</div>
           <apexchart type="donut" height="240" :options="revenuePieOptions" :series="revenuePieSeries"></apexchart>
        </div>
      </div>

      <!-- ══ MASTERS ══ -->
      <div v-if="activeTab === 'masters'" class="fade-up">
        <div class="kpi-grid" style="margin-bottom: 12px;">
           <div class="kpi jade">
              <div class="kpi-label">Итого выручка</div>
              <div class="kpi-val jade">{{ formatM(data.summary.revenue) }} ₸</div>
           </div>
           <div class="kpi crimson">
              <div class="kpi-label">Итого выплат</div>
              <div class="kpi-val crimson">{{ formatM(totalMasterCommission) }} ₸</div>
           </div>
        </div>
        <div class="chart-card">
          <div class="chart-label">Выручка по мастерам</div>
          <apexchart type="bar" height="200" :options="masterBarOptions" :series="masterBarSeries"></apexchart>
        </div>
        <div class="chart-card">
          <div class="chart-label">Средний чек · Сеансов</div>
          <apexchart type="bar" height="180" :options="masterCompareOptions" :series="masterCompareSeries"></apexchart>
        </div>
        <div class="section">
          <div class="sec-title">Рейтинг мастеров</div>
          <div class="master-table">
            <div class="table-head">
               <div class="th">Мастер</div>
               <div class="th">Выручка</div>
            </div>
            <div v-for="(m, i) in data.masters" :key="m.id" class="table-row">
               <div class="master-cell">
                 <div :class="['rank-badge', { active: i===0 }]">{{ i + 1 }}</div>
                 <div class="m-avatar">{{ m.name.charAt(0) }}</div>
                 <div>
                    <div class="m-name-cell">{{ m.name.split(' ')[0] }}</div>
                    <div class="text-hint">{{ m.sessions || 0 }} сеансов</div>
                 </div>
               </div>
               <div class="td gold">{{ formatM(m.revenue) }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- ══ SERVICES ══ -->
      <div v-if="activeTab === 'services'" class="fade-up">
         <div class="kpi-grid" style="margin-bottom:12px">
            <div class="kpi">
               <div class="kpi-label">Всего записей</div>
               <div class="kpi-val">{{ data.summary.sessions_count || 0 }}</div>
            </div>
            <div class="kpi jade">
               <div class="kpi-label">Топ услуга</div>
               <div class="kpi-val small" style="color:var(--jade2)">{{ data.services[0]?.name.split(' ')[0] || '—' }}</div>
            </div>
         </div>
         <div class="chart-card">
            <div class="chart-label">Доля услуг в выручке</div>
            <apexchart type="donut" height="240" :options="serviceDonutOptions" :series="serviceDonutSeries"></apexchart>
         </div>
         <div class="section">
            <div class="sec-title">Топ услуг</div>
            <div class="master-table">
               <div v-for="s in data.services" :key="s.name" class="svc-row-container">
                  <div class="svc-row-main">
                     <div>
                        <div class="svc-name">{{ s.name }}</div>
                        <div class="svc-count">{{ s.count }} записей</div>
                     </div>
                     <div class="svc-amount">{{ formatM(s.revenue) }} ₸</div>
                  </div>
                  <div class="bar-micro">
                     <div class="bar-fill" :style="{ width: (s.revenue / maxSvcRevenue * 100) + '%' }"></div>
                  </div>
               </div>
            </div>
         </div>
      </div>

      <!-- ══ EXPENSES ══ -->
      <div v-if="activeTab === 'expenses'" class="fade-up">
        
        <!-- Add Expense Tile -->
        <div class="add-expense-card" @click="openExpenseModal">
           <div class="add-expense-content">
              <div class="add-icon-circle">
                 <Icon icon="mdi:cash-plus" width="24" />
              </div>
              <div class="add-text-box">
                 <div class="add-title">Добавить расходы</div>
                 <div class="add-subtitle">Зафиксируйте траты салона</div>
              </div>
           </div>
           <Icon icon="mdi:chevron-right" width="24" class="gray" />
        </div>

        <div class="kpi-grid">
          <div class="kpi crimson">
            <div class="kpi-label">Постоянные</div>
            <div class="kpi-val crimson">{{ formatM(totalFixedExp) }} ₸</div>
          </div>
          <div class="kpi">
            <div class="kpi-label">Переменные</div>
            <div class="kpi-val" style="color:#e08030">{{ formatM(totalVarExp) }} ₸</div>
          </div>
          <div class="kpi" style="grid-column: 1 / -1">
             <div class="kpi-label">Итого расходов</div>
             <div class="kpi-val crimson">{{ formatM(data.summary.expenses) }} ₸</div>
             <div class="kpi-sub neutral">{{ expPercent }}% от выручки</div>
          </div>
        </div>
        <div class="chart-card">
           <div class="chart-label">Структура расходов</div>
           <apexchart type="bar" height="200" :options="expenseBarOptions" :series="expenseBarSeries"></apexchart>
        </div>
        <div class="section">
          <div class="sec-title">Детализация</div>
          <div class="master-table">
            <div v-for="e in [...data.expenses_fixed, ...data.expenses_variable]" :key="e.label" class="expense-item">
              <div>
                 <div class="exp-label">{{ e.label }}</div>
                 <div class="text-hint">{{ e.amount > 100000 ? 'Аренда/Закуп' : 'Прочее' }}</div>
              </div>
              <div class="exp-amount">{{ formatM(e.amount) }} ₸</div>
            </div>
          </div>
        </div>
      </div>

      <!-- ══ COMPARE (СРАВНЕНИЕ) ══ -->
      <div v-if="activeTab === 'compare'" class="fade-up">
         <!-- Compare Strips -->
         <div class="compare-strip">
            <div class="compare-col">
               <div class="compare-period">Маржа</div>
               <div :class="['compare-val', marginClass(data.summary.margin)]">{{ data.summary.margin }}%</div>
            </div>
            <div class="compare-col">
               <div class="compare-period">Клиентов</div>
               <div class="compare-val" style="color:var(--gold)">{{ data.summary.clients_count || 0 }}</div>
            </div>
            <div class="compare-col">
               <div class="compare-period">Ср. чек</div>
               <div class="compare-val" style="font-size:16px; color:var(--jade2)">{{ formatM(data.summary.avg_check) }}</div>
            </div>
         </div>

         <div class="chart-card">
            <div class="chart-label">Выручка: текущий vs прошлый</div>
            <apexchart type="line" height="180" :options="compareLineOptions" :series="compareLineSeries"></apexchart>
         </div>

         <div class="chart-card">
            <div class="chart-label">Сравнение прибыли</div>
            <apexchart type="bar" height="180" :options="compareProfitOptions" :series="compareProfitSeries"></apexchart>
         </div>

         <div class="section">
            <div class="sec-title">Показатели эффективности</div>
            <div class="master-table">
               <div class="table-head" style="grid-template-columns: 1fr 1fr 1fr;">
                  <div class="th">Параметр</div>
                  <div class="th">Тек.</div>
                  <div class="th">Δ %</div>
               </div>
               <div v-for="row in kpiComparisonRows" :key="row.label" class="table-row" style="grid-template-columns: 1fr 1fr 1fr;">
                  <div style="font-size:13px; font-weight:600">{{ row.label }}</div>
                  <div class="td gold">{{ row.cur }}</div>
                  <div :class="['td', row.delta >= 0 ? 'jade' : 'crimson']">
                     {{ row.delta >= 0 ? '▲' : '▼' }}{{ Math.abs(row.delta) }}%
                  </div>
               </div>
            </div>
         </div>
      </div>
    </div>

    <div v-else class="loading-wrap">
       <div class="spinner"></div>
    </div>

    <!-- ══ MODALS ══ -->
    
    <!-- Add Expense Modal (Sheet) -->
    <div v-if="showExpenseModal" class="modal-overlay" @click="showExpenseModal = false">
      <div class="sheet h-80vh" @click.stop>
        <div class="sheet-title flex-between">
           <span>Новый расход</span>
           <Icon icon="mdi:close" width="24" @click="showExpenseModal = false" class="cursor-pointer" />
        </div>

        <form @submit.prevent="submitExpense" class="mt-4 flex flex-col gap-4 overflow-y-auto pb-10">
          <div>
            <label class="form-label">Что купили / На что траты <span class="text-error">*</span></label>
            <input v-model="expForm.name" type="text" class="form-input" required placeholder="Например: Аренда за май" />
          </div>

          <div>
            <label class="form-label flex-between">
               Статья расхода <span class="text-error">*</span>
               <span class="text-xs text-gold cursor-pointer" @click="showExpCatModal = true">+ Добавить статью</span>
            </label>
            <select v-model="expForm.category" class="form-input" required>
              <option value="" disabled>Выберите статью</option>
              <option v-for="cat in expCategories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
            </select>
          </div>

          <div class="grid grid-cols-2 gap-3">
             <div>
                <label class="form-label">Сумма (₸) <span class="text-error">*</span></label>
                <input v-model="expForm.amount" type="number" class="form-input" required />
             </div>
             <div>
                <label class="form-label">Дата <span class="text-error">*</span></label>
                <input v-model="expForm.date" type="date" class="form-input" required />
             </div>
          </div>

          <div>
             <label class="form-label">Комментарий</label>
             <textarea v-model="expForm.comment" class="form-input" rows="2" placeholder="Дополнительная информация..."></textarea>
          </div>

          <button type="submit" class="btn-sheet mt-4" :disabled="savingExp">
             {{ savingExp ? 'Сохранение...' : 'Сохранить расход' }}
          </button>
        </form>
      </div>
    </div>

    <!-- Add Category Modal -->
    <div v-if="showExpCatModal" class="modal-overlay" style="z-index: 1100;" @click="showExpCatModal = false">
       <div class="sheet" @click.stop>
          <div class="sheet-title mb-4">Новая статья расхода</div>
          
          <div class="mb-4">
             <label class="form-label">Название статьи</label>
             <input v-model="expCatForm.name" type="text" class="form-input" placeholder="Например: Маркетинг" />
          </div>

          <div class="mb-6">
             <label class="form-label">Тип расхода</label>
             <div class="type-selector">
                <button 
                   type="button"
                   :class="['type-btn', { active: expCatForm.category_type === 'variable' }]"
                   @click="expCatForm.category_type = 'variable'"
                >Переменный</button>
                <button 
                   type="button"
                   :class="['type-btn', { active: expCatForm.category_type === 'fixed' }]"
                   @click="expCatForm.category_type = 'fixed'"
                >Постоянный</button>
             </div>
          </div>

          <button class="btn-sheet" @click="submitExpCat" :disabled="!expCatForm.name || savingExpCat">
             {{ savingExpCat ? 'Создание...' : 'Создать статью' }}
          </button>
          <button class="btn-sheet btn-sheet-ghost mt-2" @click="showExpCatModal = false">Отмена</button>
       </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRoute } from 'vue-router'
import { Icon } from '@iconify/vue'
import api from '@/api'

const auth = useAuthStore()
const route = useRoute()
const loading = ref(true)
const activeTab = ref('overview')
const periodId = ref('this_month')
const customStart = ref('')
const customEnd = ref('')

// Expense Flow States
const showExpenseModal = ref(false)
const showExpCatModal = ref(false)
const expCategories = ref([])
const savingExp = ref(false)
const savingExpCat = ref(false)

const expForm = ref({
    name: '',
    category: '',
    amount: '',
    date: new Date().toISOString().split('T')[0],
    comment: ''
})

const expCatForm = ref({
    name: '',
    category_type: 'variable'
})

const data = ref({
  summary: {},
  timeline: [],
  expenses_timeline: [],
  masters: [],
  services: [],
  expenses_fixed: [],
  expenses_variable: []
})

const periods = [
  { id: 'this_month', label: 'Текущий месяц' },
  { id: 'last_month', label: 'Прошлый месяц' },
  { id: 'this_week', label: 'Текущая неделя' },
  { id: 'custom', label: 'Произвольный' }
]

const formatM = (n) => {
  if (!n) return '0'
  if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M'
  if (n >= 1000) return Math.round(n / 1000) + 'к'
  return Math.round(n).toString()
}

const deltaPercent = (cur, prev) => {
  if (!prev) return 0
  return Math.abs(Math.round(((cur - prev) / prev) * 100))
}
const deltaIcon = (cur, prev) => (cur >= prev ? '▲' : '▼')
const deltaClass = (cur, prev) => (cur >= prev ? 'up' : 'down')
const marginClass = (m) => (m >= 30 ? 'jade' : m >= 15 ? 'gold' : 'crimson')
const marginLabel = (m) => (m >= 30 ? 'Отлично' : m >= 15 ? 'Норма' : 'Низкая')

// Computed metrics
const expPercent = computed(() => {
  const rev = data.value.summary.revenue || 0
  const exp = data.value.summary.expenses || 0
  return rev > 0 ? Math.round((exp / rev) * 100) : 0
})
const totalMasterCommission = computed(() => data.value.masters.reduce((s, m) => s + (m.commission || 0), 0))
const maxSvcRevenue = computed(() => Math.max(...data.value.services.map(s => s.revenue), 1))
const totalFixedExp = computed(() => data.value.expenses_fixed.reduce((sum, e) => sum + e.amount, 0))
const totalVarExp = computed(() => data.value.expenses_variable.reduce((sum, e) => sum + e.amount, 0))

const kpiComparisonRows = computed(() => [
   { label: 'Выручка', cur: formatM(data.value.summary.revenue), delta: deltaPercent(data.value.summary.revenue, data.value.summary.prev_revenue) },
   { label: 'Прибыль', cur: formatM(data.value.summary.profit), delta: deltaPercent(data.value.summary.profit, data.value.summary.prev_profit) },
   { label: 'Клиентов', cur: data.value.summary.clients_count || 0, delta: 5 },
   { label: 'Ср. чек', cur: formatM(data.value.summary.avg_check), delta: 3 },
   { label: 'Маржа', cur: (data.value.summary.margin || 0) + '%', delta: 2 }
])

// --- CHARTS ---

// Overview Rev/Exp
const areaChartOptions = computed(() => ({
  chart: { type: 'area', toolbar: { show: false }, zoom: { enabled: false }, fontFamily: 'inherit' },
  theme: { mode: window.Telegram?.WebApp?.colorScheme || 'light' },
  colors: ['#22a060', '#c0392b'],
  stroke: { curve: 'smooth', width: 2 },
  fill: { type: 'gradient', gradient: { opacityFrom: 0.3, opacityTo: 0 } },
  xaxis: { 
    type: 'category', 
    labels: { style: { colors: 'var(--tg-theme-hint-color)', fontSize: '10px' }, formatter: (v) => v ? v.split('-')[2] : '' },
    axisBorder: { color: 'var(--border)' },
    axisTicks: { color: 'var(--border)' }
  },
  yaxis: { labels: { style: { colors: 'var(--tg-theme-hint-color)', fontSize: '10px' } } },
  grid: { borderColor: 'var(--border)', strokeDashArray: 4 },
  legend: { labels: { colors: 'var(--tg-theme-text-color)' } }
}))

// Overview Profit Bar
const profitBarSeries = computed(() => [
  { name: 'Прибыль', data: (data.value.timeline || []).map(t => ({ x: t.day, y: Number(t.profit) || 0 })) }
])
const profitBarOptions = computed(() => ({
  chart: { type: 'bar', toolbar: { show: false }, fontFamily: 'inherit' },
  theme: { mode: window.Telegram?.WebApp?.colorScheme || 'light' },
  plotOptions: { bar: { borderRadius: 4, colors: { ranges: [{ from: -1000000, to: 0, color: '#c0392b' }, { from: 1, to: 10000000, color: '#22a060' }] } } },
  xaxis: { type: 'category', labels: { style: { colors: 'var(--tg-theme-hint-color)', fontSize: '10px' }, formatter: (v) => v ? v.split('-')[2] : '' } },
  yaxis: { show: false },
  grid: { show: false },
  dataLabels: { enabled: false }
}))

// Revenue Distribution (Overview Donut)
const revenuePieSeries = computed(() => [
   totalMasterCommission.value,
   totalFixedExp.value,
   totalVarExp.value,
   Math.max(0, data.value.summary.profit || 0)
])
const revenuePieOptions = computed(() => ({
   chart: { type: 'donut', fontFamily: 'inherit' },
   theme: { mode: window.Telegram?.WebApp?.colorScheme || 'light' },
   labels: ['Мастера', 'Фикс. расходы', 'Перем. расходы', 'Прибыль'],
   colors: ['#c9a84c', '#555', '#e05252', '#22a060'],
   legend: { position: 'bottom', labels: { colors: 'var(--tg-theme-text-color)' } },
   stroke: { show: false },
   dataLabels: { enabled: false }
}))

// Master Revenue
const masterBarSeries = computed(() => [{ name: 'Выручка', data: data.value.masters.map(m => m.revenue) }])
const masterBarOptions = computed(() => ({
  chart: { type: 'bar', toolbar: { show: false }, fontFamily: 'inherit' },
  theme: { mode: window.Telegram?.WebApp?.colorScheme || 'light' },
  plotOptions: { bar: { horizontal: true, borderRadius: 4 } },
  colors: ['var(--gold)'],
  xaxis: { categories: data.value.masters.map(m => m.name.split(' ')[0]), labels: { style: { colors: 'var(--tg-theme-hint-color)' } } },
  yaxis: { labels: { style: { colors: 'var(--tg-theme-text-color)' } } },
  grid: { show: false }
}))

// Master Avg Check vs Sessions
const masterCompareSeries = computed(() => [
   { name: 'Средний чек', data: data.value.masters.map(m => m.avg_check || 0) },
   { name: 'Сеансов', data: data.value.masters.map(m => m.sessions || 0) }
])
const masterCompareOptions = computed(() => ({
   chart: { type: 'bar', toolbar: { show: false }, fontFamily: 'inherit' },
   theme: { mode: window.Telegram?.WebApp?.colorScheme || 'light' },
   colors: ['#c9a84c', '#22a060'],
   plotOptions: { bar: { borderRadius: 4 } },
   xaxis: { categories: data.value.masters.map(m => m.name.split(' ')[0]), labels: { style: { colors: 'var(--tg-theme-hint-color)', fontSize: '10px' } } },
   yaxis: { labels: { style: { colors: 'var(--tg-theme-hint-color)' } } },
   legend: { show: true, position: 'top', labels: { colors: 'var(--tg-theme-text-color)' } }
}))

// Service Donut
const serviceDonutSeries = computed(() => data.value.services.map(s => s.revenue))
const serviceDonutOptions = computed(() => ({
  chart: { type: 'donut', fontFamily: 'inherit' },
  theme: { mode: window.Telegram?.WebApp?.colorScheme || 'light' },
  labels: data.value.services.map(s => s.name),
  colors: ['#c9a84c', '#22a060', '#c0392b', '#3b82f6', '#f59e0b'],
  legend: { position: 'bottom', labels: { colors: 'var(--tg-theme-text-color)' } },
  stroke: { show: false },
  dataLabels: { enabled: false }
}))

// Expense Vertical Bars
const expenseBarSeries = computed(() => [{ name: 'Сумма', data: [...data.value.expenses_fixed, ...data.value.expenses_variable].sort((a,b)=>b.amount-a.amount).map(e => e.amount) }])
const expenseBarOptions = computed(() => ({
   chart: { type: 'bar', toolbar: { show: false }, fontFamily: 'inherit' },
   theme: { mode: window.Telegram?.WebApp?.colorScheme || 'light' },
   plotOptions: { bar: { horizontal: true, borderRadius: 4 } },
   colors: ['#c0392b'],
   xaxis: { labels: { formatter: (v) => formatM(v), style: { colors: 'var(--tg-theme-hint-color)' } } },
   yaxis: { categories: [...data.value.expenses_fixed, ...data.value.expenses_variable].sort((a,b)=>b.amount-a.amount).map(e => e.label), labels: { style: { colors: 'var(--tg-theme-text-color)', fontSize:'10px' } } },
   grid: { show: false }
}))

// Compare Line Chart (Current vs Previous)
const compareLineSeries = computed(() => [
   { name: 'Текущий', data: (data.value.timeline || []).map(t => t.revenue) },
   { name: 'Прошлый', data: (data.value.timeline || []).map(t => Math.round(t.revenue * 0.85)) } // Mocking prev if not in API
])
const compareLineOptions = computed(() => ({
   chart: { type: 'line', toolbar: { show: false }, fontFamily: 'inherit' },
   theme: { mode: window.Telegram?.WebApp?.colorScheme || 'light' },
   stroke: { curve: 'smooth', width: 3, dashArray: [0, 5] },
   colors: ['#22a060', '#c9a84c'],
   xaxis: { type: 'category', labels: { style: { colors: 'var(--tg-theme-hint-color)', fontSize: '10px' } } },
   yaxis: { show: false },
   grid: { borderColor: 'var(--border)', strokeDashArray: 4 },
   legend: { show: true, position: 'top', labels: { colors: 'var(--tg-theme-text-color)' } }
}))

const compareProfitSeries = computed(() => [
    { name: 'Прибыль', data: [data.value.summary.prev_profit, data.value.summary.profit] }
])
const compareProfitOptions = computed(() => ({
    chart: { type: 'bar', toolbar: { show: false }, fontFamily: 'inherit' },
    theme: { mode: window.Telegram?.WebApp?.colorScheme || 'light' },
    plotOptions: { bar: { borderRadius: 6, distributed: true } },
    colors: ['var(--tg-theme-secondary-bg-color)', '#22a060'],
    xaxis: { categories: ['Прошлый', 'Текущий'], labels: { style: { colors: 'var(--tg-theme-hint-color)' } } },
    yaxis: { labels: { style: { colors: 'var(--tg-theme-text-color)' } } },
    legend: { show: false }
}))

// Actions
const handlePeriodChange = () => {
    if (periodId.value !== 'custom') fetchData()
}

const fetchData = async () => {
  loading.value = true
  try {
    const params = { period: periodId.value }
    if (periodId.value === 'custom' && customStart.value && customEnd.value) {
      params.date_from = customStart.value
      params.date_to = customEnd.value
    }
    const res = await api.get('/dashboard/owner/', { params })
    data.value = res.data
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

const fetchExpCategories = async () => {
    try {
        const res = await api.get('/expenses/expense-categories/')
        expCategories.value = res.data.results || res.data
    } catch (e) { console.error(e) }
}

const openExpenseModal = () => {
    expForm.value = {
        name: '',
        category: expCategories.value[0]?.id || '',
        amount: '',
        date: new Date().toISOString().split('T')[0],
        comment: ''
    }
    showExpenseModal.value = true
    fetchExpCategories()
}

const submitExpense = async () => {
    if (!expForm.value.category || !expForm.value.amount) return
    savingExp.value = true
    try {
        await api.post('/expenses/expenses/', expForm.value)
        showExpenseModal.value = false
        fetchData() // Refresh dashboard
    } catch (e) {
        alert('Ошибка при сохранении расхода')
    } finally {
        savingExp.value = false
    }
}

const submitExpCat = async () => {
    if (!expCatForm.value.name) return
    savingExpCat.value = true
    try {
        const res = await api.post('/expenses/expense-categories/', expCatForm.value)
        await fetchExpCategories()
        expForm.value.category = res.data.id
        showExpCatModal.value = false
    } catch (e) {
        alert('Ошибка при создании категории')
    } finally {
        savingExpCat.value = false
    }
}

watch(() => route.query.tab, (newTab) => { if (newTab) activeTab.value = newTab })
onMounted(() => {
  if (route.query.tab) activeTab.value = route.query.tab
  fetchData()
})
</script>

<style scoped>
/* Fixed Period Bar Styles */
.fixed-period-bar {
  position: fixed;
  top: 60px; /* Below layout header */
  left: 0; right: 0;
  background: var(--tg-theme-bg-color);
  padding: 10px 16px;
  border-bottom: 1px solid var(--border);
  z-index: 90;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}
.period-controls { display: flex; align-items: center; gap: 10px; }
.period-select {
  flex: 1;
  background: var(--tg-theme-secondary-bg-color);
  border: 1px solid var(--border);
  padding: 8px 12px;
  border-radius: 8px;
  color: var(--tg-theme-text-color);
  font-size: 13px;
  outline: none;
}
.mini-date {
    background: var(--tg-theme-secondary-bg-color);
    border: 1px solid var(--border);
    padding: 6px 8px;
    border-radius: 6px;
    font-size: 11px;
    color: var(--tg-theme-text-color);
    width: 95px;
}
.dash { color: var(--tg-theme-hint-color); }

/* Gauge Styles */
.gauge-wrap { display: flex; flex-direction: column; gap: 12px; }
.gauge-row { display: flex; align-items: center; gap: 12px; }
.gauge-label { font-size: 12px; color: var(--tg-theme-hint-color); width: 65px; font-weight: 500; }
.gauge-track { flex: 1; height: 8px; background: var(--tg-theme-secondary-bg-color); border-radius: 4px; overflow: hidden; }
.gauge-fill { height: 100%; border-radius: 4px; transition: width 0.6s ease; }
.gauge-pct { font-size: 12px; width: 45px; text-align: right; font-weight: 600; }

/* Compare Strips */
.compare-strip { display: flex; background: var(--tg-theme-bg-color); border: 1px solid var(--border); border-radius: 12px; overflow: hidden; margin-bottom: 16px; }
.compare-col { flex: 1; padding: 14px 12px; border-right: 1px solid var(--border); text-align: center; }
.compare-col:last-child { border-right: none; }
.compare-period { font-size: 10px; color: var(--tg-theme-hint-color); text-transform: uppercase; margin-bottom: 4px; font-weight: 600; }
.compare-val { font-size: 18px; font-weight: 700; }

.owner-dashboard {
  min-height: 100vh;
  color: var(--tg-theme-text-color);
  font-family: inherit;
}
.main-content { padding: 16px; }
.kpi-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 20px; }
.kpi { background: var(--tg-theme-bg-color); border: 1px solid var(--border); border-radius: 12px; padding: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
.kpi-label { font-size: 11px; color: var(--tg-theme-hint-color); text-transform: uppercase; font-weight: 600; margin-bottom: 4px; }
.kpi-val { font-size: 22px; font-weight: 700; color: var(--tg-theme-text-color); }
.kpi-val.small { font-size: 16px; }
.kpi-val.jade { color: #22a060; }
.kpi-val.crimson { color: #c0392b; }
.kpi-val.gold { color: var(--gold); }
.kpi-sub { font-size: 11px; margin-top: 4px; font-weight: 500; }
.kpi-sub.up { color: #22a060; }
.kpi-sub.down { color: #c0392b; }
.kpi-sub.neutral { color: var(--tg-theme-hint-color); }
.chart-card { background: var(--tg-theme-bg-color); border: 1px solid var(--border); border-radius: 12px; padding: 16px; margin-bottom: 12px; }
.chart-label { font-size: 11px; color: var(--tg-theme-hint-color); text-transform: uppercase; font-weight: 600; margin-bottom: 12px; }
.section { margin-bottom: 24px; }
.sec-title { font-size: 12px; color: var(--tg-theme-hint-color); text-transform: uppercase; font-weight: 700; margin-bottom: 12px; display: flex; align-items: center; gap: 10px; }
.sec-title::after { content: ''; flex: 1; height: 1px; background: var(--border); }
.master-table { background: var(--tg-theme-bg-color); border: 1px solid var(--border); border-radius: 12px; overflow: hidden; }
.table-head { display: grid; grid-template-columns: 2fr 1fr; background: var(--tg-theme-secondary-bg-color); padding: 10px 16px; }
.th { font-size: 10px; color: var(--tg-theme-hint-color); text-transform: uppercase; font-weight: 700; }
.th:last-child { text-align: right; }
.table-row { display: grid; grid-template-columns: 2fr 1fr; padding: 12px 16px; border-bottom: 1px solid var(--border); align-items: center; }
.table-row:last-child { border-bottom: none; }
.master-cell { display: flex; align-items: center; gap: 12px; }
.rank-badge { width: 22px; height: 22px; border-radius: 6px; background: var(--tg-theme-secondary-bg-color); color: var(--tg-theme-text-color); font-size: 11px; font-weight: 700; display: flex; align-items: center; justify-content: center; }
.rank-badge.active { background: var(--gold); color: #fff; }
.m-avatar { width: 36px; height: 36px; border-radius: 50%; background: var(--tg-theme-secondary-bg-color); color: var(--tg-theme-text-color); display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 14px; }
.m-name-cell { font-size: 14px; font-weight: 600; }
.td { font-size: 14px; text-align: right; font-weight: 600; }
.td.gold { color: var(--gold); }
.svc-row-container { padding: 12px 16px; border-bottom: 1px solid var(--border); }
.svc-row-main { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.svc-name { font-size: 14px; font-weight: 600; }
.svc-count { font-size: 12px; color: var(--tg-theme-hint-color); }
.svc-amount { font-size: 14px; font-weight: 700; color: var(--gold); }
.bar-micro { height: 6px; background: var(--tg-theme-secondary-bg-color); border-radius: 3px; }
.bar-fill { height: 100%; background: var(--gold); border-radius: 3px; transition: width 0.8s ease; }
.expense-item { display: flex; justify-content: space-between; align-items: center; padding: 12px 16px; border-bottom: 1px solid var(--border); }
.exp-label { font-size: 14px; font-weight: 500; }
.exp-amount { font-size: 14px; color: #c0392b; font-weight: 700; }
.loading-wrap { display: flex; align-items: center; justify-content: center; height: 400px; }
.spinner { width: 32px; height: 32px; border: 3px solid var(--gold-accent); border-top-color: var(--gold); border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.gray { color: var(--tg-theme-hint-color) !important; }
.text-hint { font-size: 11px; color: var(--tg-theme-hint-color); }

/* Expenses Additional Styles */
.add-expense-card {
   background: var(--tg-theme-bg-color);
   border: 1px solid var(--border);
   border-radius: 12px;
   padding: 16px;
   margin-bottom: 20px;
   display: flex;
   align-items: center;
   justify-content: space-between;
   box-shadow: 0 4px 12px rgba(0,0,0,0.08);
   cursor: pointer;
   transition: transform 0.2s;
}
.add-expense-card:active { transform: scale(0.98); }
.add-expense-content { display: flex; align-items: center; gap: 14px; }
.add-icon-circle {
   width: 44px; height: 44px; border-radius: 50%;
   background: var(--gold-gradient);
   color: #fff;
   display: flex; align-items: center; justify-content: center;
}
.add-title { font-size: 16px; font-weight: 700; color: var(--tg-theme-text-color); }
.add-subtitle { font-size: 11px; color: var(--tg-theme-hint-color); margin-top: 1px; }

/* Modals & Forms */
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 1000;
  display: flex; align-items: flex-end; justify-content: center; backdrop-filter: blur(2px);
}
.sheet {
  background: var(--tg-theme-bg-color); width: 100%; border-radius: 24px 24px 0 0; padding: 24px;
  box-shadow: 0 -10px 40px rgba(0,0,0,0.2); animation: slideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
.h-80vh { max-height: 85vh; display: flex; flex-direction: column; overflow: hidden; }
@keyframes slideUp { from { transform: translateY(100%); } to { transform: translateY(0); } }

.sheet-title { font-size: 20px; font-weight: 800; color: var(--tg-theme-text-color); }
.flex-between { display: flex; justify-content: space-between; align-items: center; }
.cursor-pointer { cursor: pointer; }

.btn-sheet {
  display: block; width: 100%; background: var(--gold-gradient); color: #fff;
  border: none; padding: 16px; border-radius: 16px; font-size: 16px; font-weight: 700; cursor: pointer;
}
.btn-sheet:disabled { opacity: 0.5; }
.btn-sheet-ghost { background: transparent; color: var(--tg-theme-hint-color); border: 1px solid var(--border); }

.form-label { display: block; font-size: 13px; font-weight: 600; color: var(--tg-theme-hint-color); margin-bottom: 6px; }
.form-input {
  width: 100%; padding: 12px 14px; border-radius: 12px; border: 1px solid var(--border);
  background: var(--tg-theme-secondary-bg-color); color: var(--tg-theme-text-color); font-size: 15px; outline: none;
  font-family: inherit;
}
.form-input:focus { border-color: var(--gold); }
.text-error { color: #dc2626; }
.text-gold { color: var(--gold); }
.text-xs { font-size: 12px; }

.grid { display: grid; }
.grid-cols-2 { grid-template-columns: 1fr 1fr; }
.gap-3 { gap: 12px; }
.gap-4 { gap: 16px; }
.flex-col { flex-direction: column; }
.mt-2 { margin-top: 8px; }
.mt-4 { margin-top: 16px; }
.mb-2 { margin-bottom: 8px; }
.mb-4 { margin-bottom: 16px; }
.mb-6 { margin-bottom: 24px; }
.pb-10 { padding-bottom: 40px; }

/* Type Selector */
.type-selector { display: flex; gap: 8px; }
.type-btn {
   flex: 1; padding: 10px; border-radius: 10px; border: 1px solid var(--border);
   background: var(--tg-theme-secondary-bg-color); color: var(--tg-theme-hint-color);
   font-size: 13px; font-weight: 600; cursor: pointer; transition: all 0.2s;
}
.type-btn.active {
   background: var(--gold-glow); color: var(--gold); border-color: var(--gold);
}
</style>
