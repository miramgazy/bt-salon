export interface ExpenseCategory {
  id: number
  name: string
  expenses_count: number
}

export interface Expense {
  id: number
  date: string
  name: string
  category: number
  category_name: string
  amount: string | number
  comment: string
  created_at: string
  updated_at: string
}

export interface ExpenseFilters {
  date_from: string
  date_to: string
  search: string
  category_id?: number | string
  page: number
  page_size: number
  sort_by: 'date' | 'name' | 'amount' | 'category'
  sort_order: 'asc' | 'desc'
}

export interface ExpenseListResponse {
  count: number
  total_amount: number
  results: Expense[]
  next?: string
  previous?: string
}
