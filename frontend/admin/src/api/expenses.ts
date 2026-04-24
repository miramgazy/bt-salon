import api from './index'
import type { 
  Expense, 
  ExpenseCategory, 
  ExpenseFilters, 
  ExpenseListResponse 
} from '../types/expenses'

export default {
  // Categories
  getCategories() {
    return api.get<ExpenseCategory[]>('/api/expenses/expense-categories/')
  },
  createCategory(data: Partial<ExpenseCategory>) {
    return api.post<ExpenseCategory>('/api/expenses/expense-categories/', data)
  },
  updateCategory(id: number, data: Partial<ExpenseCategory>) {
    return api.patch<ExpenseCategory>(`/api/expenses/expense-categories/${id}/`, data)
  },
  deleteCategory(id: number) {
    return api.delete(`/api/expenses/expense-categories/${id}/`)
  },

  // Expenses
  getExpenses(params: Partial<ExpenseFilters>) {
    return api.get<ExpenseListResponse>('/api/expenses/expenses/', { params })
  },
  createExpense(data: Partial<Expense>) {
    return api.post<Expense>('/api/expenses/expenses/', data)
  },
  updateExpense(id: number, data: Partial<Expense>) {
    return api.patch<Expense>(`/api/expenses/expenses/${id}/`, data)
  },
  deleteExpense(id: number) {
    return api.delete(`/api/expenses/expenses/${id}/`)
  }
}
