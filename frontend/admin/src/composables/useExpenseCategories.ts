import { ref } from 'vue'
import expensesApi from '../api/expenses'
import { useToast } from './useToast'
import type { ExpenseCategory } from '../types/expenses'

export function useExpenseCategories() {
  const categories = ref<ExpenseCategory[]>([])
  const loading = ref(false)
  const toast = useToast()

  const fetchCategories = async () => {
    loading.value = true
    try {
      const res = await expensesApi.getCategories()
      // Handle both direct array and paginated response just in case
      categories.value = Array.isArray(res.data) ? res.data : (res.data as any)?.results || []
    } catch (err) {
      toast.error('Ошибка при загрузке статей расходов')
    } finally {
      loading.value = false
    }
  }

  const findCategory = (id: number) => categories.value.find(c => c.id === id)

  return {
    categories,
    loading,
    fetchCategories,
    findCategory
  }
}
