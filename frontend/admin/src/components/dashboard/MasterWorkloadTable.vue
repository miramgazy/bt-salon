<template>
  <div class="rounded-sm border border-stroke bg-white shadow-default dark:border-strokedark dark:bg-bg-dark-2">
    <div class="py-6 px-4 md:px-6 xl:px-7.5">
      <h4 class="text-xl font-bold text-black dark:text-white">Эффективность мастеров</h4>
    </div>

    <div class="max-w-full overflow-x-auto">
      <table class="w-full table-auto">
        <thead>
          <tr class="bg-gray-2 text-left dark:bg-meta-4">
            <th class="min-w-[150px] py-4 px-4 font-medium text-black dark:text-white xl:pl-11">Мастер</th>
            <th class="min-w-[100px] py-4 px-4 font-medium text-black dark:text-white">Записей</th>
            <th class="min-w-[120px] py-4 px-4 font-medium text-black dark:text-white">Выручка</th>
            <th class="min-w-[120px] py-4 px-4 font-medium text-black dark:text-white">Зарплата</th>
            <th class="min-w-[120px] py-4 px-4 font-medium text-black dark:text-white">Маржа</th>
            <th class="min-w-[150px] py-4 px-4 font-medium text-black dark:text-white">Загруженность</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="master in data" :key="master.master_id" class="border-b border-stroke dark:border-strokedark">
            <td class="py-5 px-4 pl-9 xl:pl-11">
              <h5 class="font-medium text-black dark:text-white">{{ master.master_name }}</h5>
            </td>
            <td class="py-5 px-4 text-black dark:text-white">
              {{ master.appointments_count }}
            </td>
            <td class="py-5 px-4 text-black dark:text-white">
              {{ formatCurrency(master.revenue) }}
            </td>
            <td class="py-5 px-4 text-black dark:text-white">
              {{ formatCurrency(master.master_share) }}
            </td>
             <td class="py-5 px-4 text-black dark:text-white">
              {{ formatCurrency(master.owner_margin) }}
            </td>
            <td class="py-5 px-4">
              <div class="flex items-center gap-3">
                <div class="relative h-2.5 w-full rounded-full bg-stroke dark:bg-meta-4">
                  <div 
                    class="absolute left-0 h-full rounded-full bg-primary transition-all duration-500" 
                    :style="{ width: master.utilization_percent + '%' }"
                  ></div>
                </div>
                <span class="text-xs font-medium text-primary">{{ master.utilization_percent }}%</span>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
defineProps({
  data: Array
})

const formatCurrency = (val) => {
  return new Intl.NumberFormat('ru-KZ', { maximumFractionDigits: 0 }).format(val) + ' ₸'
}
</script>
