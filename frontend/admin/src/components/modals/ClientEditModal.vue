<template>
  <div v-if="show" class="fixed inset-0 z-[99999] flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm" @click.self="$emit('close')">
    <div class="w-full max-w-md rounded-xl bg-white dark:bg-bg-dark-2 shadow-2xl overflow-hidden flex flex-col">
       <!-- Header -->
       <div class="px-6 py-4 border-b border-stroke dark:border-strokedark flex justify-between items-center bg-gray-50 dark:bg-meta-4">
         <h3 class="font-bold text-black dark:text-white">Редактирование клиента</h3>
         <button @click="$emit('close')" class="text-body hover:text-danger"><Icon icon="mdi:close" width="24" /></button>
       </div>
       
       <!-- Body -->
       <div class="p-6 space-y-4">
         <div>
            <label class="mb-2.5 block text-sm font-medium text-black dark:text-white">Имя клиента</label>
            <input 
              type="text" 
              v-model="form.full_name"
              placeholder="Введите имя"
              class="w-full rounded border border-stroke bg-white py-3 px-5 text-black outline-none focus:border-primary dark:border-strokedark dark:bg-bg-dark-2 dark:text-white"
            />
         </div>

         <div>
            <label class="mb-2.5 block text-sm font-medium text-black dark:text-white">Номер телефона</label>
            <input 
              type="text" 
              v-model="form.phone"
              placeholder="+7 (___) ___-__-__"
              class="w-full rounded border border-stroke bg-white py-3 px-5 text-black outline-none focus:border-primary dark:border-strokedark dark:bg-bg-dark-2 dark:text-white"
            />
         </div>

         <div>
            <label class="mb-2.5 block text-sm font-medium text-black dark:text-white">Telegram ID</label>
            <input 
              type="number" 
              v-model="form.telegram_id"
              placeholder="ID пользователя"
              class="w-full rounded border border-stroke bg-white py-3 px-5 text-black outline-none focus:border-primary dark:border-strokedark dark:bg-bg-dark-2 dark:text-white"
            />
         </div>
       </div>

       <!-- Footer -->
       <div class="px-6 py-4 border-t border-stroke dark:border-strokedark flex gap-3">
         <button @click="$emit('close')" class="flex-1 rounded border border-stroke py-2 text-center font-medium hover:bg-gray-100 transition-colors dark:border-strokedark dark:hover:bg-meta-4 text-black dark:text-white">Отмена</button>
         <button @click="save" :disabled="loading" class="flex-1 rounded bg-primary py-2 text-center font-medium text-white hover:bg-opacity-90 transition-colors disabled:opacity-50">
           <Icon v-if="loading" icon="mdi:loading" class="animate-spin inline mr-1" />
           Сохранить
         </button>
       </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { Icon } from '@iconify/vue'
import api from '../../api'

const props = defineProps({
  show: Boolean,
  client: Object
})
const emit = defineEmits(['close', 'success'])

const loading = ref(false)
const form = reactive({
  full_name: '',
  phone: '',
  telegram_id: ''
})

watch(() => props.show, (val) => {
  if (val && props.client) {
    form.full_name = props.client.full_name || ''
    form.phone = props.client.phone || ''
    form.telegram_id = props.client.telegram_id || ''
  }
})

const save = async () => {
  if (!form.phone) {
    alert('Номер телефона обязателен')
    return
  }
  
  try {
    loading.value = true
    await api.patch(`/api/clients/${props.client.id}/`, {
      full_name: form.full_name,
      phone: form.phone,
      telegram_id: form.telegram_id || null
    })
    
    emit('success')
    emit('close')
  } catch (err) {
    console.error('Failed to update client:', err)
    alert(err.response?.data?.detail || 'Ошибка при обновлении данных клиента.')
  } finally {
    loading.value = false
  }
}
</script>
