<template>
  <div class="mx-auto max-w-screen-2xl p-4 md:p-6 2xl:p-8">
    <!-- Header Area -->
    <div class="mb-5 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h2 class="text-2xl font-bold text-black dark:text-white">
          Учёт расходов
        </h2>
        <p class="text-xs font-medium text-body">Управление затратами и статьями расходов</p>
      </div>
 
      <div class="flex items-center gap-4">
        <div class="flex flex-col items-end">
          <p class="text-[10px] font-bold text-body uppercase tracking-wider mb-0.5">Итого за период</p>
          <p class="text-2xl font-black text-danger">{{ formatCurrency(totalAmount) }}</p>
        </div>
        <button
          @click="openAddModal"
          class="flex items-center justify-center gap-2 rounded-lg bg-primary py-2 px-5 text-sm font-medium text-white hover:bg-opacity-90 active:scale-95 transition-all shadow-md shadow-primary/20"
        >
          <Icon icon="mdi:plus-circle" width="18" />
          <span>Добавить расход</span>
        </button>
      </div>
    </div>

    <!-- Filters Area -->
    <ExpenseFilters
      :filters="filters"
      :categories="categories"
      @apply="handleApplyFilters"
      @reset="handleResetFilters"
    />

    <!-- Content Table -->
    <ExpenseTable
      :expenses="expenses"
      :loading="loading"
      :sortBy="filters.sort_by"
      :sortOrder="filters.sort_order"
      :currentPage="filters.page"
      :totalPages="totalPages"
      @sort="handleSort"
      @edit="openEditModal"
      @delete="handleDelete"
      @pageChange="handlePageChange"
    />

    <!-- Modals -->
    <ExpenseFormModal
      :show="showFormModal"
      :expense="editingExpense"
      :categories="categories"
      @close="showFormModal = false"
      @success="handleFormSuccess"
      @refreshCategories="fetchCategories"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { Icon } from '@iconify/vue'
import { useExpenses } from '../../composables/useExpenses'
import { useExpenseCategories } from '../../composables/useExpenseCategories'
import { useToast } from '../../composables/useToast'
import expensesApi from '../../api/expenses'
import ExpenseFilters from '../../components/expenses/ExpenseFilters.vue'
import ExpenseTable from '../../components/expenses/ExpenseTable.vue'
import ExpenseFormModal from '../../components/modals/ExpenseFormModal.vue'
import type { Expense, ExpenseFilters as IFilters } from '../../types/expenses'

const { expenses, totalCount, totalAmount, loading, fetchExpenses } = useExpenses()
const { categories, fetchCategories } = useExpenseCategories()
const toast = useToast()

// Filters state
const filters = reactive<IFilters>({
  date_from: new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString().split('T')[0],
  date_to: new Date(new Date().getFullYear(), new Date().getMonth() + 1, 0).toISOString().split('T')[0],
  search: '',
  category_id: '',
  page: 1,
  page_size: 25,
  sort_by: 'date',
  sort_order: 'desc'
})

const totalPages = computed(() => Math.ceil(totalCount.value / (filters.page_size || 25)))

// Modals state
const showFormModal = ref(false)
const editingExpense = ref<Expense | null>(null)

// Handlers
const refreshData = () => fetchExpenses(filters)

const handleApplyFilters = (newFilters: Partial<IFilters>) => {
  Object.assign(filters, newFilters)
  filters.page = 1
  refreshData()
}

const handleResetFilters = () => {
  filters.date_from = new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString().split('T')[0]
  filters.date_to = new Date(new Date().getFullYear(), new Date().getMonth() + 1, 0).toISOString().split('T')[0]
  filters.search = ''
  filters.category_id = ''
  filters.page = 1
  refreshData()
}

const handleSort = (field: any) => {
  if (filters.sort_by === field) {
    filters.sort_order = filters.sort_order === 'asc' ? 'desc' : 'asc'
  } else {
    filters.sort_by = field
    filters.sort_order = 'desc'
  }
  refreshData()
}

const handlePageChange = (page: number) => {
  filters.page = page
  refreshData()
}

const openAddModal = () => {
  editingExpense.value = null
  showFormModal.value = true
}

const openEditModal = (exp: Expense) => {
  editingExpense.value = exp
  showFormModal.value = true
}

const handleFormSuccess = () => {
  showFormModal.value = false
  refreshData()
}

const handleDelete = async (exp: Expense) => {
  if (!confirm(`Удалить расход «${exp.name}» на сумму ${formatCurrency(Number(exp.amount))}?`)) return
  try {
    await expensesApi.deleteExpense(exp.id)
    toast.success('Расход успешно удален')
    refreshData()
  } catch (err) {
    toast.error('Произошла ошибка при удалении')
  }
}

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('ru-RU', { 
    style: 'currency', 
    currency: 'KZT', 
    maximumFractionDigits: 0 
  }).format(amount)
}

onMounted(() => {
  fetchCategories()
  refreshData()
})
</script>
