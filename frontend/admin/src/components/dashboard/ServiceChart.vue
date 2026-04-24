<template>
  <div class="rounded-sm border border-stroke bg-white px-5 pt-6 pb-5 shadow-default dark:border-strokedark dark:bg-bg-dark-2 sm:px-7.5">
    <div class="mb-5">
      <h4 class="text-xl font-bold text-black dark:text-white mb-2">Популярные услуги</h4>
      <div class="flex items-center">
        <select 
          v-model="mode"
          class="text-xs font-bold uppercase tracking-wider bg-gray-100 dark:bg-meta-4 py-1.5 px-3 rounded-md outline-none cursor-pointer text-body hover:text-primary transition-colors"
        >
          <option value="revenue">По выручке</option>
          <option value="count">По количеству</option>
        </select>
      </div>
    </div>
 
    <div class="h-[320px]">
      <Doughnut v-if="chartData.labels.length" :data="chartData" :options="chartOptions" />
      <div v-else class="flex h-full items-center justify-center text-body italic">Нет данных</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'
import { Doughnut } from 'vue-chartjs'

ChartJS.register(ArcElement, Tooltip, Legend)

const props = defineProps({
  data: Array
})

const mode = ref('revenue')

const colors = ['#3C50E0', '#10B981', '#FFB703', '#FB8500', '#023047', '#219EBC']

const chartData = computed(() => {
  const sorted = [...props.data].sort((a, b) => b[mode.value === 'revenue' ? 'revenue' : 'appointments_count'] - a[mode.value === 'revenue' ? 'revenue' : 'appointments_count'])
  const top = sorted.slice(0, 6)
  
  return {
    labels: top.map(d => d.service_name),
    datasets: [
      {
        backgroundColor: colors,
        hoverOffset: 4,
        data: top.map(d => mode.value === 'revenue' ? d.revenue : d.appointments_count)
      }
    ]
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
       backgroundColor: '#1C2434',
       padding: 12,
       cornerRadius: 4,
    }
  },
  cutout: '70%'
}
</script>
