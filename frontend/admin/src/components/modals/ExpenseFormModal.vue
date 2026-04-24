<template>
  <div v-if="show" class="fixed inset-0 z-[9999] flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm">
    <div class="w-full max-w-lg rounded-lg bg-white p-8 shadow-2xl dark:bg-bg-dark-2 overflow-y-auto max-h-[95vh]">
      <div class="flex items-center justify-between mb-6">
        <h3 class="text-2xl font-bold text-black dark:text-white">
          {{ isEdit ? 'Редактировать расход' : 'Добавить расход' }}
        </h3>
        <button @click="$emit('close')" class="hover:text-danger p-1">
          <Icon icon="mdi:close" width="24" />
        </button>
      </div>

      <form @submit.prevent="handleSubmit" class="space-y-5">
        <!-- Date -->
        <div>
          <label class="mb-2 block text-sm font-medium text-black dark:text-white uppercase tracking-wider">Дата <span class="text-danger">*</span></label>
          <input
            v-model="form.date"
            type="date"
            required
            class="w-full rounded border border-stroke bg-gray-50 py-3 px-5 outline-none focus:border-primary dark:border-strokedark dark:bg-meta-4 dark:text-white transition-all"
          />
        </div>

        <!-- Name -->
        <div>
          <label class="mb-2 block text-sm font-medium text-black dark:text-white uppercase tracking-wider">Название <span class="text-danger">*</span></label>
          <input
            v-model="form.name"
            type="text"
            required
            placeholder="Напр. Аренда офиса"
            class="w-full rounded border border-stroke bg-gray-50 py-3 px-5 outline-none focus:border-primary dark:border-strokedark dark:bg-meta-4 dark:text-white transition-all"
          />
        </div>

        <!-- Category -->
        <div>
          <label class="mb-2 block text-sm font-medium text-black dark:text-white uppercase tracking-wider">Статья расхода <span class="text-danger">*</span></label>
          <div class="flex gap-2">
            <select
              v-model="form.category"
              required
              class="flex-1 rounded border border-stroke bg-gray-50 py-3 px-5 outline-none focus:border-primary dark:border-strokedark dark:bg-meta-4 dark:text-white transition-all"
            >
              <option value="">Выберите статью</option>
              <option v-for="c in categories" :key="c?.id" :value="c?.id">
                {{ c?.name }}
              </option>
            </select>
            <button
              type="button"
              @click="showManager = true"
              class="flex h-[50px] w-[50px] shrink-0 items-center justify-center rounded border border-stroke bg-white hover:bg-gray-50 dark:border-strokedark dark:bg-meta-4 text-body hover:text-primary transition-all shadow-sm"
              title="Управление статьями"
            >
              <Icon icon="mdi:cog" width="20" />
            </button>
          </div>
        </div>

        <!-- Amount -->
        <div>
          <label class="mb-2 block text-sm font-medium text-black dark:text-white uppercase tracking-wider">Сумма (₸) <span class="text-danger">*</span></label>
          <input
            v-model.number="form.amount"
            type="number"
            step="0.01"
            required
            min="0.01"
            class="w-full rounded border border-stroke bg-gray-50 py-3 px-5 outline-none focus:border-primary dark:border-strokedark dark:bg-meta-4 dark:text-white transition-all"
          />
        </div>

        <!-- Comment -->
        <div>
          <label class="mb-2 block text-sm font-medium text-black dark:text-white uppercase tracking-wider">Комментарий</label>
          <textarea
            v-model="form.comment"
            rows="3"
            placeholder="Дополнительная информация..."
            class="w-full rounded border border-stroke bg-gray-50 py-3 px-5 outline-none focus:border-primary dark:border-strokedark dark:bg-meta-4 dark:text-white transition-all"
          ></textarea>
        </div>

        <!-- Warning for future date -->
        <div v-if="isFutureDate" class="flex items-center gap-2 rounded-lg bg-warning/10 p-4 text-sm text-warning animate-fadeIn">
          <Icon icon="mdi:alert-circle-outline" width="18" />
          <span>Внимание: Дата указана в будущем</span>
        </div>

        <!-- Footer -->
        <div class="flex gap-4 pt-4">
          <button
            type="button"
            @click="$emit('close')"
            class="flex-1 rounded border border-stroke py-3 px-6 text-center font-medium text-black transition hover:bg-gray-50 dark:border-strokedark dark:text-white dark:hover:bg-meta-4 active:scale-95"
          >
            Отмена
          </button>
          <button
            type="submit"
            :disabled="saving || !isValid"
            class="flex-1 rounded bg-primary py-3 px-6 text-center font-medium text-white transition hover:bg-opacity-90 disabled:opacity-50 active:scale-95 flex items-center justify-center gap-2"
          >
            <Icon v-if="saving" icon="mdi:loading" class="animate-spin" />
            {{ isEdit ? 'Сохранить' : 'Добавить' }}
          </button>
        </div>
      </form>
    </div>

    <!-- Category Manager (Higher Z-index) -->
    <CategoryManagerModal
      :show="showManager"
      :categories="categories"
      @close="showManager = false"
      @refresh="$emit('refreshCategories')"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import { Icon } from '@iconify/vue'
import expensesApi from '../../api/expenses'
import { useToast } from '../../composables/useToast'
import CategoryManagerModal from './CategoryManagerModal.vue'
import type { Expense, ExpenseCategory } from '../../types/expenses'

const props = defineProps({
  show: Boolean,
  expense: {
    type: Object as () => Expense | null,
    default: null
  },
  categories: {
    type: Array as () => ExpenseCategory[],
    default: () => []
  }
})

const emit = defineEmits(['close', 'success', 'refreshCategories'])
const toast = useToast()

const isEdit = computed(() => !!props.expense)
const saving = ref(false)
const showManager = ref(false)

const form = reactive({
  date: new Date().toISOString().split('T')[0],
  name: '',
  category: '' as string | number,
  amount: '' as string | number,
  comment: ''
})

watch(() => props.show, (newVal) => {
  if (newVal) {
    if (props.expense) {
      form.date = props.expense.date
      form.name = props.expense.name
      form.category = props.expense.category
      form.amount = props.expense.amount
      form.comment = props.expense.comment
    } else {
      form.date = new Date().toISOString().split('T')[0]
      form.name = ''
      form.category = ''
      form.amount = ''
      form.comment = ''
    }
  }
})

const isFutureDate = computed(() => {
  if (!form.date) return false
  return new Date(form.date) > new Date()
})

const isValid = computed(() => {
  return form.date && form.name && form.category && Number(form.amount) > 0
})

const handleSubmit = async () => {
  if (!form.category) {
    toast.warning('Выберите статью расхода');
    return;
  }
  saving.value = true
  try {
    const payload = { 
      ...form, 
      category: Number(form.category),
      amount: Number(form.amount) 
    }
    if (isEdit.value && props.expense) {
      await expensesApi.updateExpense(props.expense.id, payload)
      toast.success('Запись расхода обновлена')
    } else {
      await expensesApi.createExpense(payload)
      toast.success('Расход успешно добавлен')
    }
    emit('success')
  } catch (err: any) {
    const errorData = err.response?.data
    let message = 'Произошла ошибка при сохранении'
    
    if (errorData) {
      if (typeof errorData === 'string') message = errorData
      else if (errorData.non_field_errors) message = errorData.non_field_errors[0]
      else if (errorData.detail) message = errorData.detail
      else {
        // Handle field-specific errors
        const fields = Object.keys(errorData)
        if (fields.length > 0) {
          message = `${fields[0]}: ${errorData[fields[0]][0]}`
        }
      }
    }
    
    toast.error(message)
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.animate-fadeIn {
  animation: fadeIn 0.3s ease-out;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-5px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
