<template>
  <div class="master-income page-p fade-up">
    <div class="page-header" style="margin-bottom: 24px">
       <button class="back-btn" @click="$router.push('/master')">
          <Icon icon="mdi:arrow-left" width="20" />
       </button>
       <h1 class="page-title header-font">{{ $t('master.income') }}</h1>
    </div>

    <!-- ── PERIOD SELECTOR ── -->
    <div class="period-selector">
      <button 
        v-for="p in periods" 
        :key="p.id"
        :class="['period-btn', { active: activePeriod === p.id }]"
        @click="setPeriod(p.id)"
      >{{ p.label }}</button>
    </div>

    <!-- ── CUSTOM DATE RANGE (shown only if activePeriod === 'custom') ── -->
    <div v-if="activePeriod === 'custom'" class="custom-range fade-in">
       <div class="range-field">
         <label>{{ $t('master.from') }}</label>
         <input type="date" v-model="startDate" @change="fetchStats" class="range-input" />
       </div>
       <div class="range-field">
         <label>{{ $t('master.to') }}</label>
         <input type="date" v-model="endDate" @change="fetchStats" class="range-input" />
       </div>
    </div>

    <!-- ── KPI GRID ── -->
    <div class="kpi-grid">
      <div class="kpi-card glass">
        <div class="kpi-label">{{ $t('master.income') }} ({{ periodLabel }})</div>
        <div class="kpi-value text-gold">{{ Number(stats.total_income || 0).toLocaleString() }} ₸</div>
      </div>
      <div class="kpi-card glass">
        <div class="kpi-label">{{ $t('master.earnings') }}</div>
        <div class="kpi-value text-success">{{ Number(stats.master_earnings || 0).toLocaleString() }} ₸</div>
      </div>
      <div class="kpi-card glass">
        <div class="kpi-label">{{ $t('master.avgCheck') }}</div>
        <div class="kpi-value">{{ Number(stats.avg_check || 0).toLocaleString() }} ₸</div>
      </div>
    </div>

    <!-- ── CHARTS ── -->
    <div class="chart-section card glass">
      <div class="chart-header">
        <div class="chart-title">{{ $t('master.chartTitle') }}</div>
        <div class="chart-period">{{ $t('master.days7') }}</div>
      </div>
      <div class="chart-container">
        <apexchart
          type="area"
          height="220"
          :options="chartOptions"
          :series="chartSeries"
        />
      </div>
    </div>

    <div class="gold-line"></div>
    
    <div v-if="stats.popular_services && stats.popular_services.length > 0" class="services-box">
       <h3 class="box-title">{{ $t('master.popularServices') }}</h3>
       <div v-for="s in stats.popular_services" :key="s.name" class="service-row">
          <div class="s-info">
             <div class="s-name">{{ s.name }}</div>
             <div class="s-count">{{ s.count }} {{ $t('master.records') }}</div>
          </div>
          <div class="s-income">{{ Number(s.income).toLocaleString() }} ₸</div>
       </div>
    </div>

  </div>
</template>

<script setup>
import { reactive, onMounted, computed, ref } from 'vue'
import { Icon } from '@iconify/vue'
import { useAuthStore } from '@/stores/auth'
import { useI18n } from 'vue-i18n'
import api from '@/api'
import apexchart from 'vue3-apexcharts'

const auth = useAuthStore()
const { t } = useI18n()

const activePeriod = ref('month')
const startDate = ref('')
const endDate = ref('')

const periods = computed(() => [
   { id: 'today', label: t('master.today') },
   { id: 'week', label: t('master.incomeWeek') },
   { id: 'month', label: t('master.incomeMonth') },
   { id: 'custom', label: t('master.periodCustom') }
])

const periodLabel = computed(() => {
  const p = periods.value.find(x => x.id === activePeriod.value)
  return p ? p.label : ''
})

const setPeriod = (id) => {
  activePeriod.value = id
  if (id !== 'custom') {
    fetchStats()
  }
}

const stats = reactive({
  total_income: 0,
  master_earnings: 0,
  total_clients: 0,
  avg_check: 0,
  daily: [],
  popular_services: []
})

const fetchStats = async () => {
  try {
    const params = { period: activePeriod.value }
    if (activePeriod.value === 'custom') {
      params.start_date = startDate.value
      params.end_date = endDate.value
    }
    const res = await api.get('/appointments/master-stats/', { params })
    Object.assign(stats, res.data)
  } catch (e) {
    console.error('Fetch stats error', e)
  }
}

onMounted(() => {
  fetchStats()
})

const chartSeries = computed(() => [{
  name: t('master.income'),
  data: stats.daily.map(d => d.income)
}])

const chartOptions = computed(() => {
  const isDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
  return {
    chart: {
      type: 'area',
      toolbar: { show: false },
      sparkline: { enabled: false },
      background: 'transparent',
      fontFamily: 'Inter, sans-serif'
    },
    theme: { mode: isDark ? 'dark' : 'light' },
    dataLabels: { enabled: false },
    stroke: { curve: 'smooth', width: 3, colors: ['#c9a84c'] },
    colors: ['#c9a84c'],
    fill: {
      type: 'gradient',
      gradient: {
        shadeIntensity: 1,
        opacityFrom: 0.45,
        opacityTo: 0.05,
        stops: [20, 100]
      }
    },
    xaxis: {
      categories: stats.daily.map(d => {
        const date = new Date(d.date)
        return date.toLocaleDateString([], { weekday: 'short' })
      }),
      labels: { style: { colors: 'var(--muted)', fontSize: '11px', fontWeight: 600 } },
      axisBorder: { show: false },
      axisTicks: { show: false }
    },
    yaxis: { show: false },
    grid: {
      show: true,
      borderColor: 'var(--border)',
      strokeDashArray: 4,
      padding: { left: 5, right: 5 }
    },
    tooltip: {
      theme: isDark ? 'dark' : 'light',
      x: { show: true },
      y: { formatter: (val) => `${val.toLocaleString()} ₸` }
    }
  }
})
</script>

<style scoped>
.master-income {
  padding: 20px 16px 100px;
}

.period-selector {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  overflow-x: auto;
  scrollbar-width: none;
  padding: 4px 0;
}
.period-selector::-webkit-scrollbar { display: none; }

.period-btn {
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
.period-btn.active {
  background: var(--gold-gradient);
  color: #000;
  border-color: var(--gold);
  box-shadow: 0 4px 10px var(--gold-glow);
}

.custom-range {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}
.range-field {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.range-field label {
  font-size: 10px;
  color: var(--muted);
  text-transform: uppercase;
  font-weight: 800;
  margin-left: 4px;
}
.range-input {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  color: var(--text);
  padding: 10px;
  border-radius: var(--radius-sm);
  font-size: 14px;
  outline: none;
}
.range-input:focus {
  border-color: var(--gold);
}

.kpi-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 24px; }
.kpi-card {
  background: var(--card-bg); border: 1px solid var(--border); border-radius: var(--radius-sm); padding: 18px 8px;
  text-align: center;
}
.kpi-label { font-size: 10px; color: var(--muted); text-transform: uppercase; margin-bottom: 6px; font-weight: 800; letter-spacing: 0.5px; }
.kpi-value { font-family: var(--font-header); font-size: 17px; font-weight: 700; }

.chart-section {
  padding: 24px 16px; margin-bottom: 24px;
}
.chart-header { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 20px; }
.chart-title { font-size: 15px; font-weight: 700; color: var(--text); }
.chart-period { font-size: 11px; color: var(--muted); font-weight: 600; text-transform: uppercase; border: 1px solid var(--border); padding: 2px 8px; border-radius: 12px; }
.chart-container { margin: 0 -10px; }

.box-title { font-size: 11px; font-weight: 800; color: var(--muted); margin-bottom: 20px; text-transform: uppercase; letter-spacing: 1.5px; }
.service-row { 
  display: flex; justify-content: space-between; align-items: center; padding: 16px 0;
  border-bottom: 1px solid var(--border);
}
.service-row:last-child { border-bottom: none; }
.s-name { font-size: 15px; font-weight: 600; color: var(--text); }
.s-count { font-size: 12px; color: var(--muted); margin-top: 2px; font-weight: 500; }
.s-income { font-family: var(--font-header); font-size: 17px; font-weight: 700; color: var(--gold); }
</style>
