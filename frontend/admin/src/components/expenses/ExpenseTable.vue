<template>
  <div class="rounded-sm border border-stroke bg-white shadow-default dark:border-strokedark dark:bg-bg-dark-2">
    <div class="max-w-full overflow-x-auto">
      <table class="w-full table-auto">
        <thead>
          <tr class="bg-gray-2 text-left dark:bg-meta-4">
            <th class="py-3 px-4 text-xs font-bold text-black dark:text-white uppercase tracking-wider cursor-pointer hover:text-primary transition-colors" @click="handleSort('date')">
              Дата <Icon v-if="sortBy === 'date'" :icon="sortOrder === 'asc' ? 'mdi:chevron-up' : 'mdi:chevron-down'" class="inline" />
            </th>
            <th class="py-3 px-4 text-xs font-bold text-black dark:text-white uppercase tracking-wider cursor-pointer hover:text-primary transition-colors" @click="handleSort('name')">
              Название <Icon v-if="sortBy === 'name'" :icon="sortOrder === 'asc' ? 'mdi:chevron-up' : 'mdi:chevron-down'" class="inline" />
            </th>
            <th class="py-3 px-4 text-xs font-bold text-black dark:text-white uppercase tracking-wider cursor-pointer hover:text-primary transition-colors" @click="handleSort('category')">
              Статья <Icon v-if="sortBy === 'category'" :icon="sortOrder === 'asc' ? 'mdi:chevron-up' : 'mdi:chevron-down'" class="inline" />
            </th>
            <th class="py-3 px-4 text-xs font-bold text-black dark:text-white uppercase tracking-wider text-right cursor-pointer hover:text-primary transition-colors" @click="handleSort('amount')">
              Сумма <Icon v-if="sortBy === 'amount'" :icon="sortOrder === 'asc' ? 'mdi:chevron-up' : 'mdi:chevron-down'" class="inline" />
            </th>
            <th class="py-3 px-4 text-xs font-bold text-black dark:text-white uppercase tracking-wider text-center">Действия</th>
          </tr>
        </thead>
        <tbody>
          <template v-if="loading">
             <tr v-for="i in 5" :key="i">
                <td v-for="j in 5" :key="j" class="border-b border-[#eee] py-3 px-4 dark:border-strokedark">
                   <div class="h-4 w-full animate-pulse rounded bg-gray-100 dark:bg-meta-4"></div>
                </td>
             </tr>
          </template>
          <template v-else-if="expenses && expenses.length">
            <template v-for="exp in expenses" :key="exp?.id">
              <tr v-if="exp" class="hover:bg-gray-50 dark:hover:bg-meta-4/30 transition-colors">
                <td class="border-b border-[#eee] py-2.5 px-4 dark:border-strokedark">
                  <p class="text-sm text-black dark:text-white">{{ formatDate(exp.date) }}</p>
                </td>
                <td class="border-b border-[#eee] py-2.5 px-4 dark:border-strokedark">
                  <p class="text-sm text-black dark:text-white font-medium">{{ exp.name }}</p>
                  <p v-if="exp.comment" class="text-[10px] text-body line-clamp-1 mt-0.5">{{ exp.comment }}</p>
                </td>
                <td class="border-b border-[#eee] py-2.5 px-4 dark:border-strokedark">
                  <span class="inline-flex rounded-full bg-primary/10 py-0.5 px-2.5 text-[11px] font-bold text-primary">
                    {{ exp.category_name }}
                  </span>
                </td>
                <td class="border-b border-[#eee] py-2.5 px-4 dark:border-strokedark text-right">
                  <p class="text-sm text-black dark:text-white font-bold">{{ formatCurrency(exp.amount) }}</p>
                </td>
                <td class="border-b border-[#eee] py-2.5 px-4 dark:border-strokedark">
                  <div class="flex items-center justify-center space-x-3">
                    <button @click="$emit('edit', exp)" class="hover:text-primary transition-colors" title="Редактировать">
                      <Icon icon="mdi:pencil-outline" width="16" />
                    </button>
                    <button @click="$emit('delete', exp)" class="hover:text-danger transition-colors" title="Удалить">
                      <Icon icon="mdi:trash-can-outline" width="16" />
                    </button>
                  </div>
                </td>
              </tr>
            </template>
          </template>
          <tr v-else>
            <td colspan="5" class="py-20 text-center">
              <div class="flex flex-col items-center justify-center text-body opacity-50">
                <Icon icon="mdi:cash-remove" width="48" class="mb-2" />
                <p>Расходов не найдено</p>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <!-- Pagination -->
    <div v-if="totalPages > 1" class="flex items-center justify-between p-4 border-t border-stroke dark:border-strokedark">
       <span class="text-sm text-body">Страница {{ currentPage }} из {{ totalPages }}</span>
       <div class="flex gap-2">
          <button 
            @click="$emit('pageChange', currentPage - 1)" 
            :disabled="currentPage === 1"
            class="flex items-center justify-center rounded border border-stroke p-2 hover:bg-gray-50 disabled:opacity-30 dark:border-strokedark dark:hover:bg-meta-4 transition-all"
          >
            <Icon icon="mdi:chevron-left" width="20" />
          </button>
          <button 
            @click="$emit('pageChange', currentPage + 1)" 
            :disabled="currentPage === totalPages"
            class="flex items-center justify-center rounded border border-stroke p-2 hover:bg-gray-50 disabled:opacity-30 dark:border-strokedark dark:hover:bg-meta-4 transition-all"
          >
            <Icon icon="mdi:chevron-right" width="20" />
          </button>
       </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Icon } from '@iconify/vue'

interface Expense {
  id: number
  date: string
  name: string
  category_name: string
  amount: number | string
  comment?: string
}

defineProps<{
  expenses: Expense[]
  loading: boolean
  sortBy: string
  sortOrder: 'asc' | 'desc'
  currentPage: number
  totalPages: number
}>()

const emit = defineEmits(['edit', 'delete', 'sort', 'pageChange'])

const handleSort = (field: string) => emit('sort', field)

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString('ru-RU')
}

const formatCurrency = (amount: any) => {
  return new Intl.NumberFormat('ru-RU', { 
    style: 'currency', 
    currency: 'KZT', 
    maximumFractionDigits: 0 
  }).format(amount)
}
</script>
