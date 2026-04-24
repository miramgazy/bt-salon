<template>
  <div class="mx-auto max-w-270">
    <!-- Breadcrumb Start -->
    <div class="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <h2 class="text-title-md2 font-bold text-black dark:text-white">
        Услуги и категории
      </h2>
      <div class="flex items-center gap-3">
        <button 
          @click="openCategoryModal"
          class="inline-flex items-center justify-center gap-2.5 rounded-md border border-stroke py-2 px-6 text-center font-medium text-black hover:bg-opacity-90 dark:border-strokedark dark:text-white dark:hover:bg-meta-4 transition-all"
        >
          <Icon icon="mdi:shape-outline" width="20" />
          Категории
        </button>
        <button 
          @click="openCreateModal"
          class="inline-flex items-center justify-center gap-2.5 rounded-md bg-primary py-2 px-6 text-center font-medium text-white hover:bg-opacity-90 transition-all shadow-md active:scale-95"
        >
          <Icon icon="mdi:plus" width="20" />
          Создать услугу
        </button>
      </div>
    </div>
    <!-- Breadcrumb End -->

    <!-- Table Start -->
    <div class="rounded-sm border border-stroke bg-white px-5 pt-6 pb-2.5 shadow-default dark:border-strokedark dark:bg-bg-dark-2 sm:px-7.5 xl:pb-1">
      <div class="max-w-full overflow-x-auto">
        <div v-if="loading" class="flex h-40 items-center justify-center">
            <div class="h-12 w-12 animate-spin rounded-full border-4 border-solid border-primary border-t-transparent"></div>
        </div>
        
        <table v-else class="w-full table-auto">
          <thead>
            <tr class="bg-gray-2 text-left dark:bg-meta-4">
              <th class="min-w-[220px] py-4 px-4 font-medium text-black dark:text-white xl:pl-11">
                Название
              </th>
              <th class="min-w-[150px] py-4 px-4 font-medium text-black dark:text-white">
                Категория
              </th>
              <th class="min-w-[120px] py-4 px-4 font-medium text-black dark:text-white">
                Длительность
              </th>
              <th class="py-4 px-4 font-medium text-black dark:text-white">
                Цена (Итого)
              </th>
              <th class="py-4 px-4 font-medium text-black dark:text-white text-center">
                Статус
              </th>
              <th class="py-4 px-4 font-medium text-black dark:text-white text-right">
                Действия
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="service in services" :key="service.id" :class="{'opacity-50': !service.is_active}">
              <td class="border-b border-[#eee] py-5 px-4 pl-9 dark:border-strokedark xl:pl-11">
                <h5 class="font-medium text-black dark:text-white">{{ service.name }}</h5>
                <p class="text-xs text-body dark:text-bodydark">{{ service.base_price }} ₸ (база)</p>
              </td>
              <td class="border-b border-[#eee] py-5 px-4 dark:border-strokedark">
                <p class="text-black dark:text-white">{{ getCategoryName(service.category) }}</p>
              </td>
              <td class="border-b border-[#eee] py-5 px-4 dark:border-strokedark">
                <p class="text-black dark:text-white">{{ service.duration_minutes }} мин</p>
              </td>
              <td class="border-b border-[#eee] py-5 px-4 dark:border-strokedark">
                <p class="font-bold text-primary">{{ service.total_price }} ₸</p>
              </td>
              <td class="border-b border-[#eee] py-5 px-4 dark:border-strokedark text-center">
                <span 
                  :class="service.is_active ? 'bg-success/10 text-success' : 'bg-danger/10 text-danger'"
                  class="inline-flex rounded-full py-1 px-3 text-sm font-medium"
                >
                  {{ service.is_active ? 'Активна' : 'Неактивна' }}
                </span>
              </td>
              <td class="border-b border-[#eee] py-5 px-4 dark:border-strokedark text-right">
                <div class="flex items-center justify-end gap-3.5">
                  <button @click="openEditModal(service)" class="hover:text-primary transition-colors" title="Редактировать">
                    <Icon icon="mdi:pencil" width="18" />
                  </button>
                  <button @click="confirmDelete(service)" class="hover:text-danger transition-colors" :title="service.is_active ? 'Деактивировать' : 'Восстановить'">
                    <Icon :icon="service.is_active ? 'mdi:trash-can-outline' : 'mdi:restore'" width="18" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <!-- Table End -->

    <!-- Main Modal Start -->
    <div v-if="showModal" class="fixed inset-0 z-100 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div class="w-full max-w-142.5 rounded-lg bg-white py-8 px-8 dark:bg-bg-dark-2 shadow-2xl relative">
        <button @click="closeModal" class="absolute top-4 right-4 text-body hover:text-primary transition-colors">
            <Icon icon="mdi:close" width="24" />
        </button>
        
        <h3 class="pb-2 text-xl font-bold text-black dark:text-white sm:text-2xl border-b border-stroke dark:border-strokedark mb-6">
          {{ isEditing ? 'Редактировать услугу' : 'Создать новую услугу' }}
        </h3>
        
        <form @submit.prevent="saveService">
          <div class="mb-4.5">
            <label class="mb-2.5 block text-black dark:text-white font-medium">Название</label>
            <input
              v-model="form.name"
              type="text"
              placeholder="Например: Стрижка мужская"
              class="w-full rounded border-[1.5px] border-stroke bg-gray-50 py-3 px-5 font-medium outline-none transition focus:border-primary active:border-primary disabled:cursor-default dark:border-strokedark dark:bg-bg-dark dark:text-white"
              required
            />
          </div>

          <div class="mb-4.5 flex flex-col gap-6 xl:flex-row">
            <div class="w-full xl:w-1/2">
              <label class="mb-2.5 block text-black dark:text-white font-medium">Категория</label>
              <div class="flex gap-2">
                <select
                  v-model="form.category"
                  class="w-full rounded border-[1.5px] border-stroke bg-gray-50 py-3 px-5 font-medium outline-none transition focus:border-primary active:border-primary dark:border-strokedark dark:bg-bg-dark dark:text-white"
                  required
                >
                  <option value="" disabled>Выберите...</option>
                  <option v-for="cat in categories" :key="cat.id" :value="cat.id">
                    {{ cat.name }}
                  </option>
                </select>
                <button type="button" @click="openCategoryModal" class="flex items-center justify-center rounded bg-gray-200 dark:bg-meta-4 px-4 hover:bg-primary hover:text-white transition-all">
                  <Icon icon="mdi:plus" width="20" />
                </button>
              </div>
            </div>

            <div class="w-full xl:w-1/2">
              <label class="mb-2.5 block text-black dark:text-white font-medium">Длительность (мин)</label>
              <input
                v-model.number="form.duration_minutes"
                type="number"
                class="w-full rounded border-[1.5px] border-stroke bg-gray-50 py-3 px-5 font-medium outline-none transition focus:border-primary active:border-primary dark:border-strokedark dark:bg-bg-dark dark:text-white"
                required
              />
            </div>
          </div>

          <div class="mb-4.5 grid grid-cols-3 gap-4">
            <div>
              <label class="mb-2.5 block text-xs font-medium uppercase text-bodydark2">База (₸)</label>
              <input v-model.number="form.base_price" type="number" class="w-full rounded border border-stroke bg-gray-50 py-2 px-3 outline-none dark:border-strokedark dark:bg-bg-dark dark:text-white" />
            </div>
            <div>
                <label class="mb-2.5 block text-xs font-medium uppercase text-bodydark2">Тип наценки</label>
                <select v-model="form.margin_type" class="w-full rounded border border-stroke bg-gray-50 py-2 px-3 outline-none dark:border-strokedark dark:bg-bg-dark dark:text-white">
                    <option value="fixed">Фикс (₸)</option>
                    <option value="percent">Процент (%)</option>
                </select>
            </div>
            <div>
                <label class="mb-2.5 block text-xs font-medium uppercase text-bodydark2">Наценка</label>
                <input v-model.number="form.margin_value" type="number" class="w-full rounded border border-stroke bg-gray-50 py-2 px-3 outline-none dark:border-strokedark dark:bg-bg-dark dark:text-white" />
            </div>
          </div>

          <div class="mb-6 rounded-md bg-primary/5 p-4 flex justify-between items-center border border-primary/20">
            <span class="text-sm font-medium text-body">Итоговая цена для клиента:</span>
            <span class="text-xl font-bold text-primary">{{ calculatedTotalPrice }} ₸</span>
          </div>

          <div class="flex gap-4">
            <button
               type="button"
               @click="closeModal"
               class="flex w-full justify-center rounded border border-stroke py-3 font-medium text-black hover:bg-gray-100 dark:border-strokedark dark:text-white dark:hover:bg-meta-4"
            >
              Отмена
            </button>
            <button
              type="submit"
              class="flex w-full justify-center rounded bg-primary py-3 font-medium text-white hover:bg-opacity-90 transition-all active:scale-95"
              :disabled="saving"
            >
              {{ saving ? 'Сохранение...' : 'Сохранить' }}
            </button>
          </div>
        </form>
      </div>
    </div>
    <!-- Main Modal End -->

    <!-- Category Management Modal Start -->
    <div v-if="showCategoryModal" class="fixed inset-0 z-100 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
        <div class="w-full max-w-125 rounded-lg bg-white py-8 px-8 dark:bg-bg-dark-2 shadow-2xl relative">
            <button @click="closeCategoryModal" class="absolute top-4 right-4 text-body hover:text-primary">
                <Icon icon="mdi:close" width="24" />
            </button>

            <h3 class="mb-6 text-xl font-bold text-black dark:text-white">Управление категориями</h3>

            <div class="mb-5.5 flex gap-2">
                <input
                    v-model="newCategoryName"
                    type="text"
                    placeholder="Новая категория"
                    class="w-full rounded border-[1.5px] border-stroke bg-gray-50 py-2 px-4 text-black outline-none transition focus:border-primary dark:border-strokedark dark:bg-bg-dark dark:text-white"
                    @keyup.enter="saveCategory"
                />
                <button 
                  @click="saveCategory"
                  :disabled="!newCategoryName || saving"
                  class="flex items-center justify-center rounded bg-primary px-4 text-white hover:bg-opacity-90"
                >
                    <Icon icon="mdi:plus" width="20" />
                </button>
            </div>

            <div class="max-h-60 overflow-y-auto space-y-2 mb-6 pr-2 custom-scrollbar">
                <div v-for="cat in categories" :key="cat.id" class="flex items-center justify-between rounded bg-gray-50 p-3 dark:bg-bg-dark border border-stroke dark:border-strokedark">
                    <span class="font-medium text-black dark:text-white">{{ cat.name }}</span>
                    <button @click="deleteCategory(cat.id)" class="text-body hover:text-danger transition-colors">
                        <Icon icon="mdi:close-circle-outline" width="20" />
                    </button>
                </div>
                <div v-if="categories.length === 0" class="text-center py-4 text-bodydark2 italic">Категорий пока нет</div>
            </div>

            <button
                @click="closeCategoryModal"
                class="w-full rounded border border-stroke py-3 font-medium text-black hover:bg-gray-100 dark:border-strokedark dark:text-white dark:hover:bg-meta-4"
            >
                Закрыть
            </button>
        </div>
    </div>
    <!-- Category Management Modal End -->

    <!-- Confirmation Modal -->
    <div v-if="showDeleteConfirm" class="fixed inset-0 z-100 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
        <div class="w-full max-w-100 rounded-lg bg-white p-8 dark:bg-bg-dark-2 shadow-2xl text-center">
            <div class="mx-auto mb-5 flex h-14 w-14 items-center justify-center rounded-full bg-warning/10 text-warning">
                <Icon icon="mdi:alert-outline" width="32" />
            </div>
            <h4 class="mb-2 text-xl font-bold text-black dark:text-white">
                {{ serviceToDelete?.is_active ? 'Деактивировать услугу?' : 'Восстановить услугу?' }}
            </h4>
            <p class="mb-8 text-body text-sm">
                {{ serviceToDelete?.is_active 
                    ? 'Услуга "' + serviceToDelete.name + '" перестанет отображаться в приложении для записи.' 
                    : 'Услуга "' + serviceToDelete.name + '" будет снова доступна для клиентов.' }}
            </p>
            <div class="flex gap-3">
                <button @click="showDeleteConfirm = false" class="w-1/2 rounded border border-stroke py-2 text-black dark:border-strokedark dark:text-white hover:bg-gray-50">Отмена</button>
                <button 
                  @click="toggleServiceStatus" 
                  :class="serviceToDelete?.is_active ? 'bg-danger' : 'bg-success'"
                  class="w-1/2 rounded py-2 text-white hover:opacity-90"
                >
                    {{ serviceToDelete?.is_active ? 'Подтвердить' : 'Восстановить' }}
                </button>
            </div>
        </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../../api'
import { Icon } from '@iconify/vue'

const services = ref([])
const categories = ref([])
const loading = ref(true)
const saving = ref(false)

const showModal = ref(false)
const showCategoryModal = ref(false)
const isEditing = ref(false)
const showDeleteConfirm = ref(false)
const serviceToDelete = ref(null)
const newCategoryName = ref('')

const openCategoryModal = () => {
  showCategoryModal.value = true
}

const closeCategoryModal = () => {
  showCategoryModal.value = false
  newCategoryName.value = ''
}

const saveCategory = async () => {
  if (!newCategoryName.value) return
  try {
    saving.value = true
    await api.post('/api/categories/', { name: newCategoryName.value })
    newCategoryName.value = ''
    await fetchCategories()
  } catch (error) {
    console.error('Error saving category:', error)
  } finally {
    saving.value = false
  }
}

const deleteCategory = async (catId) => {
  try {
    saving.value = true
    await api.delete(`/api/categories/${catId}/`)
    await fetchCategories()
  } catch (error) {
    console.error('Error deleting category:', error)
    if (error.response?.status === 409 || error.response?.data?.detail?.includes('PROTECT')) {
      alert('Нельзя удалить категорию, в которой есть услуги.')
    } else {
      alert('Ошибка при удалении категории. Возможно, в ней есть услуги.')
    }
  } finally {
    saving.value = false
  }
}

const fetchCategories = async () => {
  try {
    const catRes = await api.get('/api/categories/')
    categories.value = catRes.data.results || catRes.data
  } catch (error) {
    console.error('Error fetching categories:', error)
  }
}

const form = ref({
  id: null,
  name: '',
  category: '',
  duration_minutes: 30,
  base_price: 0,
  margin_type: 'fixed',
  margin_value: 0
})

const calculatedTotalPrice = computed(() => {
  const base = parseFloat(form.value.base_price) || 0
  const margin = parseFloat(form.value.margin_value) || 0
  if (form.value.margin_type === 'fixed') {
    return (base + margin).toFixed(2)
  } else {
    return (base * (1 + margin / 100)).toFixed(2)
  }
})

const getCategoryName = (catId) => {
  const cat = categories.value.find(c => c.id === catId)
  return cat ? cat.name : 'Без категории'
}

const fetchData = async () => {
  try {
    loading.value = true
    const [servRes, catRes] = await Promise.all([
      api.get('/api/services/'),
      api.get('/api/categories/')
    ])
    services.value = servRes.data.results || servRes.data
    categories.value = catRes.data.results || catRes.data
  } catch (error) {
    console.error('Error fetching data:', error)
  } finally {
    loading.value = false
  }
}

const openCreateModal = () => {
  isEditing.value = false
  form.value = {
    id: null,
    name: '',
    category: categories.value.length > 0 ? categories.value[0].id : '',
    duration_minutes: 30,
    base_price: 0,
    margin_type: 'fixed',
    margin_value: 0
  }
  showModal.value = true
}

const openEditModal = (service) => {
  isEditing.value = true
  form.value = { ...service }
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
}

const saveService = async () => {
  try {
    saving.value = true
    if (isEditing.value) {
      await api.put(`/api/services/${form.value.id}/`, form.value)
    } else {
      await api.post('/api/services/', form.value)
    }
    await fetchData()
    closeModal()
  } catch (error) {
    console.error('Error saving service:', error)
    alert('Ошибка при сохранении')
  } finally {
    saving.value = false
  }
}

const confirmDelete = (service) => {
  serviceToDelete.value = service
  showDeleteConfirm.value = true
}

const toggleServiceStatus = async () => {
  try {
    saving.value = true
    await api.patch(`/api/services/${serviceToDelete.value.id}/`, {
      is_active: !serviceToDelete.value.is_active
    })
    await fetchData()
    showDeleteConfirm.value = false
  } catch (error) {
    console.error('Error toggling service status:', error)
  } finally {
    saving.value = false
  }
}

onMounted(fetchData)
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 5px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 10px;
}
.dark .custom-scrollbar::-webkit-scrollbar-thumb {
  background: #475569;
}
.text-title-md2 {
  font-size: 1.625rem;
  line-height: 2.125rem;
}
.z-100 {
  z-index: 100;
}
</style>
