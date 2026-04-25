<template>
  <div class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3 2xl:grid-cols-6 md:gap-5">
    <KpiCard 
      label="Общая выручка" 
      :value="formatCurrency(data?.revenue || 0)" 
      :delta="calculateDelta(data?.revenue, data?.prev_period?.revenue)"
    >
      <template #icon><Icon icon="mdi:cash-multiple" width="18" class="text-primary" /></template>
    </KpiCard>

     <KpiCard 
       label="Маржа владельца" 
       :value="formatCurrency(data?.owner_margin || 0)" 
       :delta="calculateDelta(data?.owner_margin, data?.prev_period?.owner_margin)"
     >
        <template #icon><Icon icon="mdi:finance" width="18" class="text-success" /></template>
     </KpiCard>
 
    <KpiCard 
      label="Расходы" 
      :value="formatCurrency(data?.total_expenses || 0)" 
      :delta="calculateDelta(data?.total_expenses, data?.prev_period?.total_expenses)"
      color="danger"
    >
       <template #icon><Icon icon="mdi:cash-remove" width="18" class="text-danger" /></template>
       <template #footer>
          <div class="flex flex-col gap-1.5">
             <div class="flex justify-between items-center text-[10px]">
                <span class="text-body font-medium">Постоянные:</span>
                <span class="text-danger font-bold">{{ formatCurrency(data?.fixed_expenses || 0) }}</span>
             </div>
             <div class="flex justify-between items-center text-[10px]">
                <span class="text-body font-medium">Переменные:</span>
                <span class="text-warning font-bold">{{ formatCurrency(data?.variable_expenses || 0) }}</span>
             </div>
          </div>
       </template>
    </KpiCard>

    <KpiCard 
      label="Чистая прибыль" 
      :value="formatCurrency(data?.net_profit || 0)" 
      :delta="calculateDelta(data?.net_profit, data?.prev_period?.net_profit)"
      color="success"
    >
       <template #icon><Icon icon="mdi:bank-outline" width="18" class="text-success" /></template>
    </KpiCard>

    <KpiCard 
      label="Кол-во записей" 
      :value="data?.appointments_count || 0" 
      :delta="calculateDelta(data?.appointments_count, data?.prev_period?.appointments_count)"
    >
       <template #icon><Icon icon="mdi:calendar-check" width="18" class="text-warning" /></template>
    </KpiCard>

    <KpiCard 
      label="Уник. клиенты" 
      :value="data?.unique_clients_count || 0" 
      :delta="calculateDelta(data?.unique_clients_count, data?.prev_period?.unique_clients_count)"
    >
       <template #icon><Icon icon="mdi:account-group" width="18" class="text-info" /></template>
    </KpiCard>
  </div>
</template>

<script setup>
import { Icon } from '@iconify/vue'
import KpiCard from './KpiCard.vue'

const props = defineProps({
  data: Object
})

const formatCurrency = (val) => {
  return new Intl.NumberFormat('ru-KZ', { style: 'currency', currency: 'KZT', maximumFractionDigits: 0 }).format(val).replace('KZT', '₸')
}

const calculateDelta = (current, prev) => {
  if (!prev || prev === 0) return undefined
  const delta = ((current - prev) / prev) * 100
  return Math.round(delta * 10) / 10
}
</script>
