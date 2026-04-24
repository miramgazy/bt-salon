<template>
  <div class="rounded-sm border border-stroke bg-white px-5 pt-7.5 pb-5 shadow-default dark:border-strokedark dark:bg-bg-dark-2 sm:px-7.5">
    <div class="mb-4 justify-between gap-4 sm:flex">
      <div>
        <h4 class="text-xl font-bold text-black dark:text-white">Выручка по мастерам</h4>
      </div>
    </div>

    <div>
      <div id="masterChart" class="h-[350px]">
        <Bar v-if="chartData.labels.length" :data="chartData" :options="chartOptions" />
        <div v-else class="flex h-full items-center justify-center text-body italic">Нет данных для отображения</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale
} from 'chart.js'
import { Bar } from 'vue-chartjs'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

const props = defineProps({
  data: Array
})

const chartData = computed(() => {
  // Sort masters by total revenue
  const sorted = [...props.data].sort((a, b) => b.revenue - a.revenue)
  
  return {
    labels: sorted.map(d => d.master_name),
    datasets: [
      {
        label: 'Доля мастера',
        backgroundColor: '#3C50E0',
        data: sorted.map(d => d.master_share),
      },
      {
        label: 'Маржа владельца',
        backgroundColor: '#10B981',
        data: sorted.map(d => d.owner_margin),
      }
    ]
  }
})

const chartOptions = {
  indexAxis: 'y', // Horizontal bars
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom',
      labels: { color: '#8A99AF', boxWidth: 12, padding: 20 }
    },
    tooltip: {
      mode: 'index',
      intersect: false,
      backgroundColor: '#1C2434',
      cornerRadius: 4,
    }
  },
  scales: {
    x: {
      stacked: true,
      grid: { color: 'rgba(226, 232, 240, 0.1)', drawBorder: false },
      ticks: { color: '#8A99AF', font: { size: 10 } }
    },
    y: {
      stacked: true,
      grid: { display: false },
      ticks: { color: '#8A99AF', font: { size: 11 } }
    }
  }
}
</script>
