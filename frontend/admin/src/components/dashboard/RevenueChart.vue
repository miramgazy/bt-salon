<template>
  <div class="rounded-sm border border-stroke bg-white px-5 pt-7.5 pb-5 shadow-default dark:border-strokedark dark:bg-bg-dark-2 sm:px-7.5">
    <div class="flex flex-wrap items-start justify-between gap-3 sm:flex-nowrap">
      <div class="flex w-full flex-wrap gap-3 sm:gap-5">
        <div class="flex min-w-47.5">
          <span class="mt-1 mr-2 flex h-4 w-full max-w-4 items-center justify-center rounded-full border border-primary">
            <span class="block h-2.5 w-full max-w-2.5 rounded-full bg-primary"></span>
          </span>
          <div class="w-full">
            <p class="font-semibold text-primary">Выручка</p>
            <p class="text-sm font-medium text-body">Всего за период</p>
          </div>
        </div>
        <div class="flex min-w-47.5">
          <span class="mt-1 mr-2 flex h-4 w-full max-w-4 items-center justify-center rounded-full border border-success">
            <span class="block h-2.5 w-full max-w-2.5 rounded-full bg-success"></span>
          </span>
          <div class="w-full">
            <p class="font-semibold text-success">Маржа</p>
            <p class="text-sm font-medium text-body">Чистая прибыль владельца</p>
          </div>
        </div>
      </div>
      
      <div class="flex w-full max-w-45 justify-end">
        <div class="inline-flex items-center rounded-md bg-whiter p-1.5 dark:bg-meta-4">
          <button 
            v-for="mode in ['day', 'week', 'month']" 
            :key="mode"
            @click="$emit('updateGroup', mode)"
            class="rounded py-1 px-3 text-xs font-medium text-black hover:bg-white hover:shadow-card dark:text-white dark:hover:bg-bg-dark"
            :class="{ 'bg-white shadow-card dark:bg-bg-dark': currentGroup === mode }"
          >
            {{ mode === 'day' ? 'День' : mode === 'week' ? 'Неделя' : 'Месяц' }}
          </button>
        </div>
      </div>
    </div>

    <div>
      <div id="chartOne" class="-ml-5 h-[350px]">
        <Line v-if="chartData.labels.length" :data="chartData" :options="chartOptions" />
        <div v-else class="flex h-full items-center justify-center text-body italic">Нет данных для отображения</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import { Line } from 'vue-chartjs'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

const props = defineProps({
  data: Array,
  currentGroup: String
})

defineEmits(['updateGroup'])

const chartData = computed(() => ({
  labels: props.data.map(d => d.date),
  datasets: [
    {
      label: 'Выручка',
      backgroundColor: 'rgba(60, 80, 224, 0.1)',
      borderColor: '#3C50E0',
      data: props.data.map(d => d.revenue),
      fill: true,
      tension: 0.4,
    },
    {
      label: 'Маржа',
      backgroundColor: 'rgba(16, 185, 129, 0.1)',
      borderColor: '#10B981',
      data: props.data.map(d => d.owner_margin),
      fill: true,
      tension: 0.4,
    }
  ]
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      mode: 'index',
      intersect: false,
      backgroundColor: '#1C2434',
      titleColor: '#FFFFFF',
      bodyColor: '#A0AEC0',
      padding: 12,
      cornerRadius: 4,
    }
  },
  scales: {
    y: {
      grid: { color: 'rgba(226, 232, 240, 0.1)', drawBorder: false },
      ticks: { color: '#8A99AF', font: { size: 10 } }
    },
    x: {
      grid: { display: false },
      ticks: { color: '#8A99AF', font: { size: 10 } }
    }
  }
}
</script>
