import { ref } from 'vue'
import expensesApi from '../api/expenses'
import { useToast } from './useToast'
import type { Expense, ExpenseFilters } from '../types/expenses'

export function useExpenses() {
  const expenses = ref<Expense[]>([])
  const totalCount = ref(0)
  const totalAmount = ref(0)
  const loading = ref(false)
  const toast = useToast()

  const fetchExpenses = async (filters: Partial<ExpenseFilters>) => {
    loading.value = true
    try {
      const res = await expensesApi.getExpenses(filters)
      expenses.value = res.data?.results || []
      totalCount.value = res.data?.count || 0
      totalAmount.value = res.data?.total_amount || 0
    } catch (err) {
      toast.error('Ошибка при загрузке расходов')
    } finally {
      loading.value = false
    }
  }

  return {
    expenses,
    totalCount,
    totalAmount,
    loading,
    fetchExpenses
  }
}
