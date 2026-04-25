<template>
  <div class="admin-report">
    <div class="page-header mb-4">
      <h1 class="page-title">{{ $t('admin.reports.title') }}</h1>
    </div>
    
    <div class="date-selector">
      <button 
        :class="['date-pill', { active: activeTab === 'today' }]" 
        @click="setDate('today')"
      >{{ $t('common.today') }}</button>
      <button 
        :class="['date-pill', { active: activeTab === 'week' }]" 
        @click="setDate('week')"
      >{{ $t('common.week') }}</button>
      <button 
        :class="['date-pill', { active: activeTab === 'month' }]" 
        @click="setDate('month')"
      >{{ $t('common.month') }}</button>
    </div>

    <div v-if="loading" class="loading-state">
       <div class="spinner"></div>
    </div>

    <div v-else>
      <div class="kpi-grid">
         <div class="kpi-card highlight">
            <div class="kpi-icon">💰</div>
            <div class="kpi-label">{{ $t('admin.reports.revenue') }}</div>
            <div class="kpi-value text-gold">{{ Number(summary.total_revenue || 0).toLocaleString() }} ₸</div>
         </div>
         <div class="kpi-card">
            <div class="kpi-icon">✅</div>
            <div class="kpi-label">{{ $t('admin.reports.completed') }}</div>
            <div class="kpi-value">{{ summary.completed_appointments || 0 }}</div>
         </div>
         <div class="kpi-card">
            <div class="kpi-icon">⏳</div>
            <div class="kpi-label">{{ $t('admin.reports.pending') }}</div>
            <div class="kpi-value">{{ summary.pending_appointments || 0 }}</div>
         </div>
         <div class="kpi-card text-error">
            <div class="kpi-icon">❌</div>
            <div class="kpi-label">{{ $t('admin.reports.cancelled') }}</div>
            <div class="kpi-value">{{ summary.cancelled_appointments || 0 }}</div>
         </div>
      </div>
      
      <div class="mt-6 mb-4">
         <h2 class="section-subtitle">{{ $t('admin.reports.conversion') }}</h2>
         <div class="conversion-card">
            <div class="conv-row">
               <span>{{ $t('admin.reports.totalRecords') }}</span>
               <span class="font-bold">{{ summary.total_appointments || 0 }}</span>
            </div>
            <div class="conv-bar-wrap">
               <div class="conv-bar" :style="{ width: conversionRate + '%' }"></div>
            </div>
            <div class="conv-row text-xs mt-1">
               <span class="text-muted">{{ $t('admin.reports.completionRate') }}</span>
               <span class="text-success font-bold">{{ conversionRate.toFixed(1) }}%</span>
            </div>
         </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import api from '@/api'

const activeTab = ref('today')
const dateFrom = ref('')
const dateTo = ref('')

const summary = ref({})
const loading = ref(false)

const conversionRate = computed(() => {
    const total = summary.value.total_appointments || 0
    const completed = summary.value.completed_appointments || 0
    if (total === 0) return 0
    return (completed / total) * 100
})

const setDate = (type) => {
    activeTab.value = type
    const tzOffset = (new Date()).getTimezoneOffset() * 60000 
    const today = new Date(Date.now() - tzOffset)
    
    if (type === 'today') {
        dateFrom.value = today.toISOString().split('T')[0]
        dateTo.value = today.toISOString().split('T')[0]
    } else if (type === 'week') {
        const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000)
        dateFrom.value = weekAgo.toISOString().split('T')[0]
        dateTo.value = today.toISOString().split('T')[0]
    } else if (type === 'month') {
        const monthAgo = new Date(today.getFullYear(), today.getMonth() - 1, today.getDate())
        dateFrom.value = monthAgo.toISOString().split('T')[0]
        dateTo.value = today.toISOString().split('T')[0]
    }
}

const fetchReport = async () => {
    loading.value = true
    try {
        const res = await api.get('/dashboard/summary/', {
            params: {
                date_from: dateFrom.value,
                date_to: dateTo.value
            }
        })
        summary.value = res.data
    } catch (e) {
        console.error(e)
    } finally {
        loading.value = false
    }
}

watch(activeTab, () => {
  fetchReport()
})

onMounted(() => {
    setDate('today')
    fetchReport()
})
</script>

<style scoped>
.admin-report {
  padding: 20px 16px 100px;
}
.page-header { display: flex; justify-content: space-between; align-items: center; }
.page-title { font-size: 24px; font-weight: 800; color: var(--text); }
.section-subtitle { font-size: 18px; font-weight: 700; margin-bottom: 12px; color: var(--text); }

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
  flex: 1;
}
.date-pill.active {
  background: var(--gold-gradient);
  color: #000;
  border-color: var(--gold);
  box-shadow: 0 4px 10px var(--gold-glow);
}

.kpi-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
}

.kpi-card {
    background: var(--bg-secondary);
    border-radius: 16px;
    padding: 16px;
    border: 1px solid var(--border);
}
.kpi-card.highlight {
    grid-column: 1 / -1;
    background: var(--gold-glow);
    border-color: var(--gold);
}

.kpi-icon { font-size: 24px; margin-bottom: 8px; }
.kpi-label { font-size: 12px; font-weight: 600; color: var(--muted); margin-bottom: 4px; }
.kpi-value { font-size: 20px; font-weight: 800; color: var(--text); }

.text-gold { color: var(--gold); }
.text-error { color: #dc2626; }
.text-error .kpi-value { color: #dc2626; }
.text-success { color: #16a34a; }
.text-muted { color: var(--muted); }
.font-bold { font-weight: 700; }

.conversion-card {
    background: var(--bg-secondary);
    border-radius: 16px;
    padding: 16px;
    border: 1px solid var(--border);
}
.conv-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.conv-bar-wrap {
    height: 8px;
    background: var(--bg);
    border-radius: 4px;
    overflow: hidden;
    margin: 12px 0;
}
.conv-bar {
    height: 100%;
    background: #16a34a;
    border-radius: 4px;
    transition: width 0.3s;
}

.spinner {
  width: 32px; height: 32px;
  border: 3px solid var(--border);
  border-top-color: var(--gold);
  border-radius: 50%;
  animation: spin 1s infinite linear;
  margin: 40px auto;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
