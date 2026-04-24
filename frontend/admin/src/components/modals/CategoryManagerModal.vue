<template>
  <div v-if="show" class="fixed inset-0 z-[10000] flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm">
    <div class="w-full max-w-md rounded-lg bg-white p-6 shadow-2xl dark:bg-bg-dark-2">
      <div class="flex items-center justify-between mb-6">
        <h3 class="text-xl font-bold text-black dark:text-white">Статьи расходов</h3>
        <button @click="$emit('close')" class="hover:text-danger p-1">
          <Icon icon="mdi:close" width="24" />
        </button>
      </div>

      <!-- Add New Category -->
      <div class="mb-6 flex gap-2">
        <input
          v-model="newName"
          type="text"
          placeholder="Новая статья..."
          class="flex-1 rounded border border-stroke bg-gray-50 py-2 px-3 text-sm outline-none focus:border-primary dark:border-strokedark dark:bg-meta-4 dark:text-white"
          @keyup.enter="handleCreate"
        />
        <button
          @click="handleCreate"
          :disabled="creating || !newName.trim()"
          class="rounded bg-primary px-4 py-2 text-sm font-medium text-white hover:bg-opacity-90 disabled:opacity-50 transition-all"
        >
          <Icon v-if="creating" icon="mdi:loading" class="animate-spin" />
          <span v-else>Добавить</span>
        </button>
      </div>

      <div class="max-h-[300px] overflow-y-auto space-y-2 pr-2">
        <template v-for="cat in categories" :key="cat?.id">
          <div 
            v-if="cat"
            class="flex items-center justify-between rounded-md border border-stroke p-3 dark:border-strokedark group"
          >
            <div v-if="editingId === cat.id" class="flex-1 flex gap-2 mr-2">
              <input
                v-model="editingName"
                type="text"
                class="w-full rounded border border-stroke bg-white py-1 px-2 text-sm outline-none focus:border-primary dark:border-strokedark dark:bg-bg-dark-2 dark:text-white"
                @keyup.enter="handleUpdate(cat.id)"
              />
              <button @click="handleUpdate(cat.id)" class="text-success hover:scale-110"><Icon icon="mdi:check" /></button>
              <button @click="editingId = null" class="text-danger hover:scale-110"><Icon icon="mdi:close" /></button>
            </div>
            <template v-else>
              <span class="text-sm font-medium">{{ cat.name }}</span>
              <div class="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                <button @click="startEdit(cat)" class="hover:text-primary"><Icon icon="mdi:pencil-outline" /></button>
                <button @click="handleDelete(cat)" class="hover:text-danger"><Icon icon="mdi:trash-can-outline" /></button>
              </div>
            </template>
          </div>
        </template>
      </div>

      <div class="mt-8">
        <button
          @click="$emit('close')"
          class="w-full rounded border border-stroke py-2 text-center text-sm font-medium hover:bg-gray-50 dark:border-strokedark dark:hover:bg-meta-4"
        >
          Закрыть
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Icon } from '@iconify/vue'
import expensesApi from '../../api/expenses'
import { useToast } from '../../composables/useToast'
import type { ExpenseCategory } from '../../types/expenses'

const props = defineProps({
  show: Boolean,
  categories: {
    type: Array as () => ExpenseCategory[],
    required: true
  }
})

const emit = defineEmits(['close', 'refresh'])
const toast = useToast()

const newName = ref('')
const creating = ref(false)
const editingId = ref<number | null>(null)
const editingName = ref('')

const handleCreate = async () => {
  if (!newName.value.trim()) return
  creating.value = true
  try {
    await expensesApi.createCategory({ name: newName.value })
    newName.value = ''
    toast.success('Статья добавлена')
    emit('refresh')
  } catch (err: any) {
    const errorData = err.response?.data
    let message = 'Ошибка при добавлении статьи'
    
    if (errorData) {
      if (typeof errorData === 'string') message = errorData
      else if (errorData.non_field_errors) message = errorData.non_field_errors[0]
      else if (errorData.name) message = `Название: ${errorData.name[0]}`
      else if (errorData.detail) message = errorData.detail
    }
    
    toast.error(message)
  } finally {
    creating.value = false
  }
}

const startEdit = (cat: ExpenseCategory) => {
  editingId.value = cat.id
  editingName.value = cat.name
}

const handleUpdate = async (id: number) => {
  if (!editingName.value.trim()) return
  try {
    await expensesApi.updateCategory(id, { name: editingName.value })
    editingId.value = null
    toast.success('Название обновлено')
    emit('refresh')
  } catch (err: any) {
    const errorData = err.response?.data
    let message = 'Ошибка при обновлении'
    
    if (errorData) {
      if (errorData.non_field_errors) message = errorData.non_field_errors[0]
      else if (errorData.name) message = `Название: ${errorData.name[0]}`
      else if (errorData.detail) message = errorData.detail
    }
    
    toast.error(message)
  }
}

const handleDelete = async (cat: ExpenseCategory) => {
  if (cat.expenses_count > 0) {
    toast.warning(`Нельзя удалить: к статье привязано ${cat.expenses_count} расходов`)
    return
  }
  
  if (!confirm(`Удалить статью «${cat.name}»?`)) return

  try {
    await expensesApi.deleteCategory(cat.id)
    toast.success('Статья удалена')
    emit('refresh')
  } catch (err) {
    const detail = (err as any).response?.data?.detail || 'Ошибка при удалении'
    toast.error(detail)
  }
}
</script>
