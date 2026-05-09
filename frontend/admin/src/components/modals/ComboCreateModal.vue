<template>
  <div v-if="show" class="fixed inset-0 z-100 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
    <div class="w-full max-w-2xl rounded-lg bg-white dark:bg-bg-dark-2 shadow-2xl relative flex flex-col max-h-[90vh] overflow-hidden">
      <!-- Header (Fixed) -->
      <div class="px-8 pt-8 pb-2 shrink-0">
        <button @click="$emit('close')" class="absolute top-4 right-4 text-body hover:text-primary transition-colors">
            <Icon icon="mdi:close" width="24" />
        </button>
        
        <h3 class="pb-4 text-xl font-bold text-black dark:text-white sm:text-2xl border-b border-stroke dark:border-strokedark mb-2">
          {{ isEditing ? 'Редактировать комбо' : 'Создать комбо-услугу' }}
        </h3>
      </div>
      
      <form @submit.prevent="saveCombo" class="flex flex-col flex-1 overflow-hidden">
        <!-- Body (Scrollable) -->
        <div class="flex-1 overflow-y-auto px-8 py-4 custom-scrollbar">
          <!-- Basic Info -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4.5">
            <div>
              <label class="mb-2.5 block text-black dark:text-white font-medium">Название комбо</label>
              <input
                v-model="form.name"
                type="text"
                placeholder="Например: Отец + Сын"
                class="w-full rounded border-[1.5px] border-stroke bg-gray-50 py-3 px-5 font-medium outline-none transition focus:border-primary dark:border-strokedark dark:bg-bg-dark dark:text-white"
                required
              />
            </div>
            <div>
              <label class="mb-2.5 block text-black dark:text-white font-medium">Категория</label>
              <select
                v-model="form.category"
                class="w-full rounded border-[1.5px] border-stroke bg-gray-50 py-3 px-5 font-medium outline-none transition focus:border-primary dark:border-strokedark dark:bg-bg-dark dark:text-white"
                required
              >
                <option value="" disabled>Выберите...</option>
                <option v-for="cat in categories" :key="cat.id" :value="cat.id">
                  {{ cat.name }}
                </option>
              </select>
            </div>
          </div>

          <!-- Sub-services Selection -->
          <div class="mb-6">
            <div class="flex justify-between items-center mb-3">
              <label class="text-black dark:text-white font-bold uppercase text-xs tracking-wider">Состав комбо</label>
              <button 
                type="button" 
                @click="addSubService"
                class="text-xs font-bold text-primary flex items-center gap-1 hover:underline"
              >
                <Icon icon="mdi:plus-circle" width="16" /> Добавить услугу
              </button>
            </div>
            
            <div class="space-y-3">
              <div v-for="(item, index) in selectedSubServices" :key="index" class="flex gap-2 items-center animate-fade-in">
                <div class="flex-1">
                  <select 
                    v-model="item.id"
                    class="w-full rounded border border-stroke bg-gray-50 py-2.5 px-4 outline-none dark:border-strokedark dark:bg-bg-dark dark:text-white"
                    required
                  >
                    <option value="" disabled>Выберите услугу...</option>
                    <option v-for="s in availableServices" :key="s.id" :value="s.id" :disabled="isAlreadySelected(s.id, index)">
                      {{ s.name }} ({{ s.total_price }} ₸)
                    </option>
                  </select>
                </div>
                <div class="w-16">
                  <input 
                    v-model.number="item.quantity"
                    type="number"
                    min="1"
                    class="w-full rounded border border-stroke bg-gray-50 py-2.5 px-2 text-center outline-none dark:border-strokedark dark:bg-bg-dark dark:text-white"
                    title="Количество"
                  />
                </div>
                <div class="flex items-center">
                  <label class="cursor-pointer p-1 rounded hover:bg-gray-100 dark:hover:bg-meta-4 transition-colors" :title="mainIndex === index ? 'Главная услуга' : 'Сделать главной'">
                    <input type="radio" :value="index" v-model="mainIndex" class="sr-only" />
                    <Icon :icon="mainIndex === index ? 'mdi:star' : 'mdi:star-outline'" 
                          :class="mainIndex === index ? 'text-warning' : 'text-body'" 
                          width="24" />
                  </label>
                </div>
                <button 
                  type="button" 
                  @click="removeSubService(index)"
                  class="text-danger hover:bg-danger/10 p-2 rounded transition-colors"
                  v-if="selectedSubServices.length > 1"
                >
                  <Icon icon="mdi:trash-can-outline" width="20" />
                </button>
              </div>
            </div>
          </div>

          <!-- Financial Summary -->
          <div class="bg-gray-100 dark:bg-meta-4 rounded-xl p-5 mb-6 border border-stroke dark:border-strokedark shadow-sm">
            <div class="grid grid-cols-2 gap-4 mb-4">
              <div>
                <p class="text-xs text-body uppercase font-bold mb-1">Суммарная цена</p>
                <p class="text-lg font-bold text-black dark:text-white">{{ sumPrice }} ₸</p>
              </div>
              <div>
                <p class="text-xs text-body uppercase font-bold mb-1">Суммарная длительность</p>
                <p class="text-lg font-bold text-black dark:text-white">{{ sumDuration }} мин</p>
              </div>
            </div>

            <div class="mb-4 mt-6">
              <div class="mb-4 flex items-center justify-between p-3 bg-white dark:bg-bg-dark rounded-lg border border-stroke dark:border-strokedark shadow-sm">
                <div>
                    <label class="font-medium text-black dark:text-white block">Плавающая цена</label>
                    <span class="text-xs text-body">Итоговая цена будет в диапазоне</span>
                </div>
                <label class="relative inline-flex cursor-pointer items-center">
                    <input type="checkbox" v-model="form.is_floating_price" class="sr-only peer" />
                    <div class="peer h-6 w-11 rounded-full bg-gray-200 after:absolute after:top-[2px] after:left-[2px] after:h-5 after:w-5 after:rounded-full after:border after:border-gray-300 after:bg-white after:transition-all after:content-[''] peer-checked:bg-primary peer-checked:after:translate-x-full peer-checked:after:border-white peer-focus:outline-none dark:border-gray-600 dark:bg-gray-700"></div>
                </label>
              </div>

              <!-- Total Price Input -->
              <div class="mb-6 p-5 bg-primary/5 rounded-2xl border-2 border-primary/20">
                  <label class="mb-3 block text-black dark:text-white font-black text-lg uppercase tracking-tight">Стоимость комбо (для клиента)</label>
                  <div v-if="form.is_floating_price" class="grid grid-cols-2 gap-4 animate-fadeIn">
                      <div>
                          <label class="mb-2 block text-[10px] font-bold uppercase text-primary">Минимум (₸)</label>
                          <input v-model.number="form.price_min" type="number" class="w-full rounded-xl border-2 border-primary/20 bg-white py-3 px-5 text-xl font-black text-primary outline-none transition focus:border-primary dark:bg-bg-dark" required />
                      </div>
                      <div>
                          <label class="mb-2 block text-[10px] font-bold uppercase text-primary">Максимум (₸)</label>
                          <input v-model.number="form.price_max" type="number" class="w-full rounded-xl border-2 border-primary/20 bg-white py-3 px-5 text-xl font-black text-primary outline-none transition focus:border-primary dark:bg-bg-dark" required />
                      </div>
                  </div>
                  <div v-else class="animate-fadeIn">
                      <input v-model.number="form.total_price" type="number" class="w-full rounded-xl border-2 border-primary bg-white py-4 px-6 text-3xl font-black text-primary outline-none transition dark:bg-bg-dark" placeholder="0" required />
                  </div>
              </div>

              <!-- Margin Selection -->
              <div class="mb-4 p-5 bg-gray-50 dark:bg-meta-4 rounded-2xl border border-stroke dark:border-strokedark shadow-sm">
                  <label class="mb-4 block text-xs font-bold uppercase text-bodydark2 tracking-widest">Наценка салона</label>
                  <div class="grid grid-cols-2 gap-4 mb-4">
                      <div>
                          <label class="mb-2 block text-[10px] font-medium uppercase text-body">Тип</label>
                          <select v-model="form.margin_type" class="w-full rounded-lg border border-stroke bg-white py-2.5 px-4 outline-none dark:border-strokedark dark:bg-bg-dark dark:text-white">
                              <option value="fixed">Фиксированная (₸)</option>
                              <option value="percent">Процент от итога (%)</option>
                          </select>
                      </div>
                      <div>
                          <label class="mb-2 block text-[10px] font-medium uppercase text-body">Значение</label>
                          <input v-model.number="form.margin_value" type="number" class="w-full rounded-lg border border-stroke bg-white py-2.5 px-4 outline-none dark:border-strokedark dark:bg-bg-dark dark:text-white" />
                      </div>
                  </div>

                  <!-- Master Share Preview -->
                  <div class="pt-4 border-t border-stroke dark:border-strokedark flex justify-between items-center">
                      <div class="text-xs font-bold text-body uppercase">Доля мастера:</div>
                      <div class="text-right">
                          <div v-if="form.is_floating_price" class="font-bold text-black dark:text-white">
                              {{ masterShareMin }} — {{ masterShareMax }} ₸
                          </div>
                          <div v-else class="font-black text-xl text-black dark:text-white">
                              {{ masterShareTotal }} ₸
                          </div>
                      </div>
                  </div>
              </div>
            </div>

            <!-- Strategy Selection -->
            <div v-if="discount > 0" class="animate-fade-in mb-4">
              <label class="mb-3 block text-xs font-bold uppercase text-body tracking-widest">Кто платит за скидку?</label>
              <div class="grid grid-cols-3 gap-3">
                <label 
                  v-for="strat in strategies" :key="strat.value"
                  class="relative flex cursor-pointer flex-col rounded-lg border border-stroke p-3 hover:bg-gray-50 dark:border-strokedark dark:hover:bg-meta-4 shadow-sm"
                  :class="{'border-primary bg-primary/5': form.discount_strategy === strat.value}"
                >
                  <input type="radio" :value="strat.value" v-model="form.discount_strategy" class="sr-only" />
                  <span class="text-xs font-bold text-black dark:text-white mb-1">{{ strat.label }}</span>
                  <span class="text-[10px] text-body leading-tight">{{ strat.desc }}</span>
                </label>
              </div>
            </div>
          </div>
        </div>

        <!-- Footer (Fixed) -->
        <div class="px-8 pb-8 pt-4 shrink-0">
          <div class="flex gap-4">
            <button
               type="button"
               @click="$emit('close')"
               class="flex-1 justify-center rounded border border-stroke py-3 font-medium text-black hover:bg-gray-100 dark:border-strokedark dark:text-white dark:hover:bg-meta-4 transition-all"
            >
              Отмена
            </button>
            <button
              type="submit"
              class="flex-1 justify-center rounded bg-primary py-3 font-medium text-white hover:bg-opacity-90 transition-all active:scale-95 disabled:opacity-50"
              :disabled="saving || !isValid"
            >
              {{ saving ? 'Сохранение...' : (isEditing ? 'Обновить комбо' : 'Создать комбо') }}
            </button>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Icon } from '@iconify/vue'
import api from '../../api'

const props = defineProps({
  show: Boolean,
  combo: Object,
  categories: Array,
  services: Array
})
const emit = defineEmits(['close', 'success'])

const isEditing = computed(() => !!props.combo)
const saving = ref(false)

const form = ref({
  name: '',
  category: '',
  total_price: 0,
  discount_strategy: 'owner_only',
  is_combo: true,
  base_price: 0,
  margin_type: 'fixed',
  margin_value: 0,
  is_floating_price: false,
  price_min: 0,
  price_max: 0
})

const selectedSubServices = ref([{ id: '', quantity: 1 }])
const mainIndex = ref(0) // Index of the main service

const strategies = [
  { value: 'owner_only', label: 'Салон', desc: 'Вся скидка за счет маржи салона' },
  { value: 'master_only', label: 'Мастер', desc: 'Вся скидка за счет работы мастера' },
  { value: 'equal_split', label: '50 / 50', desc: 'Делится поровну между всеми' }
]

const availableServices = computed(() => {
  return props.services.filter(s => !s.is_combo)
})

watch(() => props.show, (val) => {
  if (val) {
    if (props.combo) {
      form.value = { ...props.combo }
      selectedSubServices.value = props.combo.combo_items.map(item => ({
        id: item.sub_service,
        quantity: item.quantity
      }))
      const idx = props.combo.combo_items.findIndex(item => item.is_main)
      mainIndex.value = idx !== -1 ? idx : 0
    } else {
      form.value = {
        name: '',
        category: props.categories[0]?.id || '',
        total_price: 0,
        discount_strategy: 'owner_only',
        is_combo: true,
        base_price: 0,
        margin_type: 'fixed',
        margin_value: 0,
        is_floating_price: false,
        price_min: 0,
        price_max: 0
      }
      selectedSubServices.value = [{ id: '', quantity: 1 }]
      mainIndex.value = 0
    }
  }
})

const addSubService = () => {
  selectedSubServices.value.push({ id: '', quantity: 1 })
}

const removeSubService = (index) => {
  selectedSubServices.value.splice(index, 1)
  if (mainIndex.value >= selectedSubServices.value.length) {
    mainIndex.value = 0
  }
}

const isAlreadySelected = (id, currentIndex) => {
  return selectedSubServices.value.some((item, idx) => item.id === id && idx !== currentIndex)
}

const sumPrice = computed(() => {
  return selectedSubServices.value.reduce((acc, item) => {
    const s = availableServices.value.find(svc => svc.id === item.id)
    return acc + (s ? parseFloat(s.total_price) * item.quantity : 0)
  }, 0)
})

const sumDuration = computed(() => {
  if (mainIndex.value === null || mainIndex.value === undefined) return 0
  const mainItem = selectedSubServices.value[mainIndex.value]
  if (mainItem && mainItem.id) {
    const s = availableServices.value.find(svc => svc.id === mainItem.id)
    return s ? s.duration_minutes : 0
  }
  return 0
})

const masterShareTotal = computed(() => {
  const total = parseFloat(form.value.total_price) || 0
  const margin = parseFloat(form.value.margin_value) || 0
  if (form.value.margin_type === 'fixed') {
    return Math.max(0, total - margin).toFixed(0)
  } else {
    return Math.max(0, total * (1 - margin / 100)).toFixed(0)
  }
})

const masterShareMin = computed(() => {
  const total = parseFloat(form.value.price_min) || 0
  const margin = parseFloat(form.value.margin_value) || 0
  if (form.value.margin_type === 'fixed') {
    return Math.max(0, total - margin).toFixed(0)
  } else {
    return Math.max(0, total * (1 - margin / 100)).toFixed(0)
  }
})

const masterShareMax = computed(() => {
  const total = parseFloat(form.value.price_max) || 0
  const margin = parseFloat(form.value.margin_value) || 0
  if (form.value.margin_type === 'fixed') {
    return Math.max(0, total - margin).toFixed(0)
  } else {
    return Math.max(0, total * (1 - margin / 100)).toFixed(0)
  }
})

// Auto-update total_price when sumPrice changes
watch(sumPrice, (newVal) => {
  if (!isEditing.value && form.value.total_price === 0) {
    form.value.total_price = newVal
  }
})

const isValid = computed(() => {
  if (form.value.is_floating_price) {
    return form.value.name && form.value.category && selectedSubServices.value.every(item => item.id) && form.value.price_max >= form.value.price_min && form.value.price_min > 0
  }
  return form.value.name && 
         form.value.category && 
         selectedSubServices.value.every(item => item.id) &&
         form.value.total_price > 0 &&
         mainIndex.value !== null
})

const saveCombo = async () => {
  if (form.value.is_floating_price && form.value.price_min > form.value.price_max) {
    alert('Минимальная цена не может быть больше максимальной')
    return
  }
  try {
    saving.value = true
    
    // For combos, base_price is the master share
    const totalBase = parseFloat(masterShareTotal.value)
    
    const payload = {
      ...form.value,
      duration_minutes: sumDuration.value,
      base_price: totalBase,
      sub_services: selectedSubServices.value.map((s, idx) => ({
        sub_service: s.id,
        quantity: s.quantity,
        is_main: mainIndex.value === idx
      }))
    }

    if (isEditing.value) {
      await api.put(`/api/services/${form.value.id}/`, payload)
    } else {
      await api.post('/api/services/', payload)
    }
    
    emit('success')
    emit('close')
  } catch (error) {
    console.error('Error saving combo:', error)
    alert(error.response?.data?.non_field_errors?.[0] || 'Ошибка при сохранении комбо')
  } finally {
    saving.value = false
  }
}
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
.animate-fade-in {
  animation: fadeIn 0.3s ease-out;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(5px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
