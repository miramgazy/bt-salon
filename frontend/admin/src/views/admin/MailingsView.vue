<template>
  <div class="mx-auto max-w-270">
    <!-- Breadcrumb Start -->
    <div class="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h2 class="text-title-md2 font-bold text-black dark:text-white">
          Целевые рассылки
        </h2>
        <p class="text-sm text-body dark:text-bodydark mt-1">
          Управление отложенными уведомлениями и акциями в Telegram
        </p>
      </div>
      <div class="flex items-center gap-3">
        <button 
          @click="openCreateModal"
          class="inline-flex items-center justify-center gap-2.5 rounded-lg bg-primary py-2.5 px-6 text-center font-medium text-white hover:bg-opacity-90 transition-all shadow-md active:scale-95"
        >
          <Icon icon="mdi:plus" width="20" />
          Создать рассылку
        </button>
      </div>
    </div>
    <!-- Breadcrumb End -->

    <!-- Table Start -->
    <div class="rounded-xl border border-stroke bg-white px-5 pt-6 pb-2.5 shadow-default dark:border-strokedark dark:bg-bg-dark-2 sm:px-7.5 xl:pb-4">
      <div class="max-w-full overflow-x-auto">
        <div v-if="loading" class="flex h-40 items-center justify-center">
          <div class="h-12 w-12 animate-spin rounded-full border-4 border-solid border-primary border-t-transparent"></div>
        </div>
        
        <table v-else class="w-full table-auto">
          <thead>
            <tr class="bg-gray-2 text-left dark:bg-meta-4 rounded-lg">
              <th class="min-w-[220px] py-4 px-4 font-bold text-black dark:text-white xl:pl-6">
                Название
              </th>
              <th class="min-w-[150px] py-4 px-4 font-bold text-black dark:text-white">
                Сегмент
              </th>
              <th class="min-w-[160px] py-4 px-4 font-bold text-black dark:text-white">
                Запланировано
              </th>
              <th class="min-w-[150px] py-4 px-4 font-bold text-black dark:text-white text-center">
                Статус
              </th>
              <th class="min-w-[200px] py-4 px-4 font-bold text-black dark:text-white text-center">
                Прогресс
              </th>
              <th class="py-4 px-4 font-bold text-black dark:text-white text-right">
                Действия
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in mailings" :key="item.id" class="hover:bg-gray-50 dark:hover:bg-meta-4/50 transition-colors">
              <td class="border-b border-[#eee] py-5 px-4 pl-6 dark:border-strokedark">
                <h5 class="font-bold text-black dark:text-white">{{ item.title }}</h5>
                <p class="text-xs text-body line-clamp-1 mt-0.5" :title="item.message_ru">{{ item.message_ru }}</p>
              </td>
              <td class="border-b border-[#eee] py-5 px-4 dark:border-strokedark">
                <span class="inline-flex rounded-md bg-gray-100 dark:bg-meta-4 py-1 px-2.5 text-xs font-medium text-black dark:text-white">
                  {{ item.audience_display }}
                </span>
              </td>
              <td class="border-b border-[#eee] py-5 px-4 dark:border-strokedark">
                <p class="text-sm text-black dark:text-white font-medium">
                  {{ formatDate(item.scheduled_at) }}
                </p>
              </td>
              <td class="border-b border-[#eee] py-5 px-4 dark:border-strokedark text-center">
                <span 
                  :class="{
                    'bg-warning/10 text-warning': item.status === 'scheduled',
                    'bg-primary/10 text-primary animate-pulse': item.status === 'in_progress',
                    'bg-success/10 text-success': item.status === 'done',
                    'bg-danger/10 text-danger': item.status === 'error',
                    'bg-gray-100 text-body': item.status === 'draft'
                  }"
                  class="inline-flex rounded-full py-1 px-3 text-xs font-bold uppercase tracking-wider"
                >
                  {{ item.status_display }}
                </span>
              </td>
              <td class="border-b border-[#eee] py-5 px-4 dark:border-strokedark">
                <div class="flex flex-col gap-1">
                  <div class="flex justify-between text-[10px] font-bold text-body">
                    <span>Успешно: {{ item.sent_success }}</span>
                    <span v-if="item.total_recipients > 0">{{ Math.round((item.sent_success / item.total_recipients) * 100) }}%</span>
                  </div>
                  <div class="w-full bg-gray-200 dark:bg-meta-4 rounded-full h-2 overflow-hidden">
                    <div 
                      class="bg-primary h-2 rounded-full transition-all duration-500" 
                      :style="{ width: item.total_recipients ? `${(item.sent_success / item.total_recipients) * 100}%` : '0%' }"
                    ></div>
                  </div>
                  <div class="flex justify-between text-[9px] text-danger mt-0.5">
                    <span v-if="item.failed_count">Ошибок: {{ item.failed_count }}</span>
                    <span v-if="item.unsubscribed_count" class="text-warning">Отписок: {{ item.unsubscribed_count }}</span>
                  </div>
                </div>
              </td>
              <td class="border-b border-[#eee] py-5 px-4 dark:border-strokedark text-right">
                <div class="flex items-center justify-end gap-2">
                  <button 
                    @click="openTestModal(item)" 
                    class="p-1.5 hover:bg-primary/10 rounded-lg text-primary transition-colors" 
                    title="Тестовая отправка"
                  >
                    <Icon icon="mdi:send-check-outline" width="18" />
                  </button>
                  <button 
                    v-if="item.status === 'scheduled' || item.status === 'draft'"
                    @click="confirmDelete(item)" 
                    class="p-1.5 hover:bg-danger/10 rounded-lg text-danger transition-colors" 
                    title="Удалить"
                  >
                    <Icon icon="mdi:trash-can-outline" width="18" />
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="mailings.length === 0">
              <td colspan="6" class="text-center py-8 text-body dark:text-bodydark italic">
                Рассылок пока нет. Нажмите "Создать рассылку", чтобы запланировать первую.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <!-- Table End -->

    <!-- Create/Edit Modal Start -->
    <div v-if="showModal" class="fixed inset-0 z-100 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div class="w-full max-w-150 rounded-2xl bg-white dark:bg-bg-dark-2 shadow-2xl relative flex flex-col max-h-[90vh] overflow-hidden border border-stroke dark:border-strokedark">
        <!-- Header -->
        <div class="px-8 pt-8 pb-4 shrink-0 border-b border-stroke dark:border-strokedark flex justify-between items-center">
          <h3 class="text-xl font-bold text-black dark:text-white">
            Создание целевой рассылки
          </h3>
          <button @click="closeModal" class="text-body hover:text-primary transition-colors">
            <Icon icon="mdi:close" width="24" />
          </button>
        </div>
        
        <form @submit.prevent="saveMailing" class="flex flex-col flex-1 overflow-hidden">
          <div class="flex-1 overflow-y-auto px-8 py-6 space-y-5 custom-scrollbar">
            <!-- Title -->
            <div>
              <label class="mb-2 block text-sm font-bold text-black dark:text-white">Название рассылки</label>
              <input
                v-model="form.title"
                type="text"
                placeholder="Например: Акция к 8 марта / Скидка 20%"
                class="w-full rounded-xl border-2 border-stroke bg-transparent py-3 px-4 outline-none focus:border-primary dark:border-strokedark dark:text-white transition-all"
                required
              />
            </div>

            <!-- Segment & Precalculation -->
            <div class="p-4 bg-gray-50 dark:bg-meta-4 rounded-xl border border-stroke dark:border-strokedark space-y-3">
              <div class="flex justify-between items-center">
                <label class="text-sm font-bold text-black dark:text-white">Сегмент получателей</label>
                <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-black bg-primary/10 text-primary">
                  <Icon icon="mdi:account-group" width="14" />
                  Аудитория: {{ calculatedAudienceCount }} чел.
                </span>
              </div>
              <select
                v-model="form.audience_type"
                @change="fetchAudienceCount"
                class="w-full rounded-lg border border-stroke bg-white py-2.5 px-4 text-sm outline-none focus:border-primary dark:border-strokedark dark:bg-bg-dark dark:text-white transition-all"
              >
                <option value="all">Все пользователи (подписанные на бота)</option>
                <option value="active">Активные (имели записи за последние 60 дней)</option>
                <option value="inactive">Неактивные (не посещали более 60 дней)</option>
              </select>
            </div>

            <!-- Scheduled Date -->
            <div>
              <label class="mb-2 block text-sm font-bold text-black dark:text-white">Дата и время отправки</label>
              <input
                v-model="form.scheduled_at"
                type="datetime-local"
                class="w-full rounded-xl border-2 border-stroke bg-transparent py-3 px-4 outline-none focus:border-primary dark:border-strokedark dark:text-white transition-all"
                required
              />
            </div>

            <!-- Messages -->
            <div class="space-y-4">
              <div class="flex justify-between items-center">
                <label class="text-sm font-bold text-black dark:text-white">Тексты сообщений</label>
                <button 
                  type="button"
                  @click="insertPlaceholder" 
                  class="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-primary/10 text-primary hover:bg-primary hover:text-white text-xs font-bold transition-all"
                  title="Вставить имя пользователя в позицию курсора"
                >
                  <Icon icon="mdi:code-tags" width="14" />
                  Вставить {{user_name}}
                </button>
              </div>

              <!-- RU -->
              <div>
                <span class="text-xs font-bold text-body uppercase tracking-wider block mb-1">Русский язык</span>
                <textarea
                  ref="textareaRu"
                  v-model="form.message_ru"
                  rows="3"
                  placeholder="Здравствуйте, {{user_name}}! Приглашаем вас..."
                  class="w-full rounded-xl border-2 border-stroke bg-transparent p-3 text-sm outline-none focus:border-primary dark:border-strokedark dark:text-white transition-all"
                  required
                ></textarea>
              </div>

              <!-- KZ -->
              <div>
                <span class="text-xs font-bold text-body uppercase tracking-wider block mb-1">Қазақ тілі</span>
                <textarea
                  ref="textareaKz"
                  v-model="form.message_kz"
                  rows="3"
                  placeholder="Сәлеметсіз бе, {{user_name}}! Сізді шақырамыз..."
                  class="w-full rounded-xl border-2 border-stroke bg-transparent p-3 text-sm outline-none focus:border-primary dark:border-strokedark dark:text-white transition-all"
                  required
                ></textarea>
              </div>
            </div>
          </div>

          <!-- Footer -->
          <div class="px-8 py-4 shrink-0 border-t border-stroke dark:border-strokedark bg-gray-50 dark:bg-meta-4 flex gap-4">
            <button
              type="button"
              @click="closeModal"
              class="flex-1 py-3 rounded-xl border border-stroke font-bold text-black hover:bg-white dark:border-strokedark dark:text-white dark:hover:bg-bg-dark transition-all"
            >
              Отмена
            </button>
            <button
              type="submit"
              class="flex-1 py-3 rounded-xl bg-primary font-bold text-white hover:opacity-90 active:scale-95 transition-all shadow-lg disabled:opacity-50"
              :disabled="saving"
            >
              {{ saving ? 'Планирование...' : 'Запланировать' }}
            </button>
          </div>
        </form>
      </div>
    </div>
    <!-- Create/Edit Modal End -->

    <!-- Test Send Modal Start -->
    <div v-if="showTestModal" class="fixed inset-0 z-100 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div class="w-full max-w-100 rounded-2xl bg-white p-8 dark:bg-bg-dark-2 shadow-2xl relative border border-stroke dark:border-strokedark">
        <button @click="showTestModal = false" class="absolute top-4 right-4 text-body hover:text-primary">
          <Icon icon="mdi:close" width="20" />
        </button>

        <h4 class="text-lg font-bold text-black dark:text-white mb-2">Тестовая отправка</h4>
        <p class="text-xs text-body mb-5">
          Проверьте, как выглядит сообщение у администратора перед массовой рассылкой.
        </p>

        <div class="space-y-4">
          <div>
            <label class="mb-1.5 block text-xs font-bold text-body uppercase">Ваш Telegram ID</label>
            <input 
              v-model="testTelegramId" 
              type="text" 
              placeholder="Например: 123456789" 
              class="w-full rounded-lg border border-stroke p-2.5 text-sm outline-none focus:border-primary dark:border-strokedark dark:bg-meta-4 dark:text-white"
            />
            <span class="text-[10px] text-body mt-1 block">Узнать свой ID можно в боте через команду /getmyid</span>
          </div>

          <button 
            @click="sendTestMessage" 
            :disabled="testing || !testTelegramId"
            class="w-full py-2.5 rounded-lg bg-primary text-white font-bold text-sm hover:opacity-90 transition-all disabled:opacity-50 flex items-center justify-center gap-2"
          >
            <Icon v-if="testing" icon="mdi:loading" class="animate-spin" width="18" />
            <Icon v-else icon="mdi:send" width="18" />
            {{ testing ? 'Отправка...' : 'Отправить мне' }}
          </button>
        </div>
      </div>
    </div>
    <!-- Test Send Modal End -->
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api'
import { Icon } from '@iconify/vue'

const mailings = ref([])
const loading = ref(true)
const saving = ref(false)
const showModal = ref(false)

const form = ref({
  title: '',
  message_ru: '',
  message_kz: '',
  scheduled_at: '',
  audience_type: 'all'
})

const textareaRu = ref(null)
const textareaKz = ref(null)
const lastFocusedTextarea = ref('ru')

const calculatedAudienceCount = ref(0)

// Test Modal State
const showTestModal = ref(false)
const selectedMailingForTest = ref(null)
const testTelegramId = ref('')
const testing = ref(false)

const fetchMailings = async () => {
  try {
    loading.value = true
    const res = await api.get('/api/mailings/')
    mailings.value = res.data.results || res.data || []
  } catch (error) {
    console.error('Error fetching mailings:', error)
  } finally {
    loading.value = false
  }
}

const fetchAudienceCount = async () => {
  try {
    const res = await api.get('/api/mailings/count_recipients/', {
      params: { audience_type: form.value.audience_type }
    })
    calculatedAudienceCount.value = res.data.count || 0
  } catch (error) {
    console.error('Error counting audience:', error)
    calculatedAudienceCount.value = 0
  }
}

const openCreateModal = () => {
  const now = new Date()
  now.setMinutes(now.getMinutes() + 10) // default 10 mins in future
  const tzOffset = now.getTimezoneOffset() * 60000
  const localIso = new Date(now.getTime() - tzOffset).toISOString().slice(0, 16)

  form.value = {
    title: '',
    message_ru: '',
    message_kz: '',
    scheduled_at: localIso,
    audience_type: 'all'
  }
  showModal.value = true
  fetchAudienceCount()
}

const closeModal = () => {
  showModal.value = false
}

const insertPlaceholder = () => {
  const tag = '{{user_name}}'
  const activeRef = lastFocusedTextarea.value === 'kz' ? textareaKz.value : textareaRu.value
  const fieldKey = lastFocusedTextarea.value === 'kz' ? 'message_kz' : 'message_ru'

  if (activeRef) {
    const start = activeRef.selectionStart
    const end = activeRef.selectionEnd
    const text = form.value[fieldKey]
    form.value[fieldKey] = text.slice(0, start) + tag + text.slice(end)
    
    // Focus back and move cursor
    setTimeout(() => {
      activeRef.focus()
      activeRef.setSelectionRange(start + tag.length, start + tag.length)
    }, 50)
  } else {
    form.value.message_ru += tag
  }
}

const saveMailing = async () => {
  try {
    saving.value = true
    await api.post('/api/mailings/', form.value)
    closeModal()
    await fetchMailings()
  } catch (error) {
    console.error('Error saving mailing:', error)
    alert('Ошибка при планировании рассылки. Проверьте правильность заполнения полей.')
  } finally {
    saving.value = false
  }
}

const confirmDelete = async (item) => {
  if (confirm(`Вы уверены, что хотите удалить рассылку "${item.title}"?`)) {
    try {
      await api.delete(`/api/mailings/${item.id}/`)
      await fetchMailings()
    } catch (error) {
      console.error('Error deleting mailing:', error)
    }
  }
}

const openTestModal = async (item) => {
  selectedMailingForTest.value = item
  showTestModal.value = true
  // Try to prefill admin's telegram_id if known from profile
  try {
    const meRes = await api.get('/api/accounts/me/')
    if (meRes.data?.telegram_id) {
      testTelegramId.value = String(meRes.data.telegram_id)
    }
  } catch (e) {
    // ignore
  }
}

const sendTestMessage = async () => {
  if (!testTelegramId.value) return
  try {
    testing.value = true
    await api.post(`/api/mailings/${selectedMailingForTest.value.id}/send_test/`, {
      telegram_id: testTelegramId.value
    })
    alert('Тестовое сообщение успешно отправлено в ваш Telegram!')
    showTestModal.value = false
  } catch (error) {
    console.error('Test send error:', error)
    alert(error.response?.data?.error || 'Ошибка при отправке тестового сообщения.')
  } finally {
    testing.value = false
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  fetchMailings()
  // Track focus to know where to insert placeholder
  window.addEventListener('focusin', (e) => {
    if (e.target === textareaRu.value) lastFocusedTextarea.value = 'ru'
    if (e.target === textareaKz.value) lastFocusedTextarea.value = 'kz'
  })
})
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
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
.z-100 {
  z-index: 100;
}
</style>
