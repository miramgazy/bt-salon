<template>
  <div class="mx-auto max-w-270">
    <!-- Breadcrumb Start -->
    <div class="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <h2 class="text-title-md2 font-bold text-black dark:text-white">
        Настройки Организации
      </h2>
      <nav>
        <ol class="flex items-center gap-2">
          <li>
            <router-link class="font-medium" to="/admin/calendar">Dashboard /</router-link>
          </li>
          <li class="font-medium text-primary">Организация</li>
        </ol>
      </nav>
    </div>
    <!-- Breadcrumb End -->

    <div v-if="loading" class="flex h-60 items-center justify-center rounded-sm border border-stroke bg-white shadow-default dark:border-strokedark dark:bg-bg-dark-2">
      <div class="h-16 w-16 animate-spin rounded-full border-4 border-solid border-primary border-t-transparent"></div>
    </div>

    <div v-else class="grid grid-cols-1 gap-8">
      <div class="col-span-5 xl:col-span-3">
        <div class="rounded-sm border border-stroke bg-white shadow-default dark:border-strokedark dark:bg-bg-dark-2">
          <div class="border-b border-stroke py-4 px-7 dark:border-strokedark">
            <h3 class="font-medium text-black dark:text-white text-lg">
              Основная информация
            </h3>
          </div>
          <div class="p-7">
            <form @submit.prevent="saveOrganization">
              <div class="mb-5.5 flex flex-col gap-5.5 sm:flex-row">
                <div class="w-full sm:w-1/2">
                  <label class="mb-3 block text-sm font-medium text-black dark:text-white">
                    Название организации
                  </label>
                  <div class="relative">
                    <input
                      v-model="org.name"
                      class="w-full rounded border border-stroke bg-gray-50 py-3 px-4.5 text-black focus:border-primary focus-visible:outline-none dark:border-strokedark dark:bg-bg-dark dark:text-white dark:focus:border-primary"
                      type="text"
                      placeholder="Например: BT Salon VIP"
                      required
                    />
                  </div>
                </div>

                <div class="w-full sm:w-1/2">
                  <label class="mb-3 block text-sm font-medium text-black dark:text-white">
                    Токен Telegram бота
                  </label>
                  <input
                    v-model="org.bot_token"
                    class="w-full rounded border border-stroke bg-gray-50 py-3 px-4.5 text-black focus:border-primary focus-visible:outline-none dark:border-strokedark dark:bg-bg-dark dark:text-white dark:focus:border-primary"
                    type="text"
                    placeholder="123456:ABC-DEF1234ghIkl"
                    required
                  />
                </div>
              </div>

              <div class="mb-5.5 flex flex-col gap-5.5 sm:flex-row">
                <div class="w-full sm:w-1/2">
                  <label class="mb-3 block text-sm font-medium text-black dark:text-white">
                    Username бота
                  </label>
                  <input
                    v-model="org.bot_username"
                    class="w-full rounded border border-stroke bg-gray-50 py-3 px-4.5 text-black focus:border-primary focus-visible:outline-none dark:border-strokedark dark:bg-bg-dark dark:text-white dark:focus:border-primary"
                    type="text"
                    placeholder="bt_salon_bot (без @)"
                  />
                </div>

                <div class="w-full sm:w-1/2">
                  <label class="mb-3 block text-sm font-medium text-black dark:text-white">
                    Короткое имя Mini App
                  </label>
                  <input
                    v-model="org.tma_name"
                    class="w-full rounded border border-stroke bg-gray-50 py-3 px-4.5 text-black focus:border-primary focus-visible:outline-none dark:border-strokedark dark:bg-bg-dark dark:text-white dark:focus:border-primary"
                    type="text"
                    placeholder="booking"
                  />
                </div>
              </div>

              <div v-if="org.bot_username && org.tma_name" class="mb-5.5 p-4 bg-primary/5 border border-primary/20 rounded-md">
                <label class="mb-2 block text-xs font-bold text-primary uppercase">
                  Ваша ссылка на Mini App
                </label>
                <div class="flex items-center justify-between gap-2 overflow-hidden">
                  <code class="text-sm text-primary font-mono truncate">
                    https://t.me/{{ org.bot_username }}/{{ org.tma_name }}?startapp={{ org.id }}
                  </code>
                  <a :href="`https://t.me/${org.bot_username}/${org.tma_name}?startapp=${org.id}`" target="_blank" class="text-xs text-white bg-primary px-3 py-1 rounded hover:bg-opacity-90">
                    Открыть
                  </a>
                </div>
              </div>

              <div class="mb-5.5">
                <label class="mb-3 block text-sm font-medium text-black dark:text-white">
                  Адрес
                </label>
                <textarea
                  v-model="org.address"
                  class="w-full rounded border border-stroke bg-gray-50 py-3 px-4.5 text-black focus:border-primary focus-visible:outline-none dark:border-strokedark dark:bg-bg-dark dark:text-white dark:focus:border-primary"
                  rows="3"
                  placeholder="Город, Улица, Дом"
                  required
                ></textarea>
              </div>

              <!-- Webhook Section -->
              <div v-if="org.bot_token" class="mb-5 mt-10 rounded-sm border border-stroke bg-gray-50 p-5 dark:border-strokedark dark:bg-bg-dark">
                <div class="flex items-center justify-between mb-4">
                  <h4 class="font-bold text-black dark:text-white flex items-center gap-2">
                    <Icon icon="mdi:webhook" class="text-primary" width="20" />
                    Статус Webhook Telegram
                  </h4>
                  <div class="flex items-center gap-2">
                    <span v-if="webhookLoading" class="animate-spin">
                      <Icon icon="mdi:loading" width="18" />
                    </span>
                    <span 
                      v-else
                      :class="webhookStatus?.url ? 'bg-success/10 text-success' : 'bg-danger/10 text-danger'"
                      class="rounded-full py-1 px-3 text-xs font-medium"
                    >
                      {{ webhookStatus?.url ? 'Подключено' : 'Не настроено' }}
                    </span>
                  </div>
                </div>

                <div v-if="webhookStatus" class="space-y-2 mb-6">
                  <div class="flex justify-between text-xs border-b border-stroke pb-1 dark:border-strokedark">
                    <span class="text-body">URL Webhook:</span>
                    <span class="font-mono text-black dark:text-white">{{ webhookStatus.url || '—' }}</span>
                  </div>
                  <div v-if="webhookStatus.last_error_message" class="flex justify-between text-xs text-danger">
                    <span>Последняя ошибка:</span>
                    <span class="text-right">{{ webhookStatus.last_error_message }}</span>
                  </div>
                  <div v-if="webhookStatus.pending_update_count > 0" class="flex justify-between text-xs text-warning">
                    <span>Очередь обновлений:</span>
                    <span>{{ webhookStatus.pending_update_count }}</span>
                  </div>
                </div>

                <button
                  type="button"
                  @click="setupWebhook"
                  :disabled="webhookSettingUp"
                  class="flex w-full items-center justify-center gap-2 rounded bg-black py-2 px-6 font-medium text-white hover:bg-opacity-90 transition-all dark:bg-primary"
                >
                  <Icon v-if="webhookSettingUp" icon="mdi:loading" class="animate-spin" width="18" />
                  <Icon v-else icon="mdi:sync" width="18" />
                  {{ webhookStatus?.url ? 'Обновить Webhook' : 'Настроить Webhook' }}
                </button>
                <p class="mt-2 text-[10px] text-body italic">
                  * Нажмите, чтобы связать бота с сервером для получения контактов пользователей.
                </p>
              </div>


              <!-- TMA Design Settings -->
              <h3 class="mb-5 mt-10 font-medium text-black dark:text-white border-b border-stroke pb-2 dark:border-strokedark text-lg">
                Оформление Mini App (TMA)
              </h3>
              
              <div class="mb-5.5 flex flex-col gap-5.5 sm:flex-row">
                <div class="w-full sm:w-1/2">
                  <label class="mb-3 block text-sm font-medium text-black dark:text-white">
                    Приветственный текст
                  </label>
                  <input
                    v-model="org.greeting_text"
                    class="w-full rounded border border-stroke bg-gray-50 py-3 px-4.5 text-black focus:border-primary focus-visible:outline-none dark:border-strokedark dark:bg-bg-dark dark:text-white dark:focus:border-primary"
                    type="text"
                    placeholder="Например: Добро пожаловать!"
                  />
                </div>

                <div class="w-full sm:w-1/2 flex items-center gap-4">
                  <div class="flex-1">
                    <label class="mb-3 block text-sm font-medium text-black dark:text-white">
                      Цвет дизайна (HEX)
                    </label>
                    <input
                      v-model="org.design_color"
                      class="w-full rounded border border-stroke bg-gray-50 py-3 px-4.5 text-black focus:border-primary focus-visible:outline-none dark:border-strokedark dark:bg-bg-dark dark:text-white dark:focus:border-primary"
                      type="text"
                      placeholder="#c9a84c"
                    />
                  </div>
                  <input type="color" v-model="org.design_color" class="h-12 w-16 p-1 bg-transparent cursor-pointer mt-7" />
                </div>
              </div>

              <div class="mb-5.5 flex flex-col gap-5.5 sm:flex-row">
                <div class="w-full sm:w-1/2">
                  <label class="mb-3 block text-sm font-medium text-black dark:text-white">
                    Ссылка на Instagram
                  </label>
                  <input
                    v-model="org.instagram_link"
                    class="w-full rounded border border-stroke bg-gray-50 py-3 px-4.5 text-black focus:border-primary focus-visible:outline-none dark:border-strokedark dark:bg-bg-dark dark:text-white dark:focus:border-primary"
                    type="url"
                    placeholder="https://instagram.com/btsalon"
                  />
                </div>

                <div class="w-full sm:w-1/2">
                  <label class="mb-3 block text-sm font-medium text-black dark:text-white">
                    Номер WhatsApp
                  </label>
                  <input
                    v-model="org.whatsapp_number"
                    class="w-full rounded border border-stroke bg-gray-50 py-3 px-4.5 text-black focus:border-primary focus-visible:outline-none dark:border-strokedark dark:bg-bg-dark dark:text-white dark:focus:border-primary"
                    type="text"
                    placeholder="77012345678"
                  />
                </div>
              </div>

              <div class="mb-5.5">
                <label class="mb-3 block text-sm font-medium text-black dark:text-white">
                  Логотип салона (Отображается в Telegram)
                </label>
                <div class="flex items-center gap-4">
                  <img v-if="org.logo_url" :src="org.logo_url" alt="Current Logo" class="h-16 w-16 rounded-full object-cover border border-stroke" />
                  <input
                    type="file"
                    accept="image/*"
                    @change="handleLogoUpload"
                    class="w-full rounded-md border border-stroke p-3 outline-none transition file:mr-4 file:rounded file:border-[0.5px] file:border-stroke file:bg-[#EEEEEE] file:py-1 file:px-2.5 file:text-sm file:font-medium focus:border-primary file:focus:border-primary active:border-primary disabled:cursor-default disabled:bg-whiter dark:border-form-strokedark dark:bg-form-input dark:file:border-strokedark dark:file:bg-white/30 dark:file:text-white"
                  />
                </div>
              </div>

              <!-- Map Coordinates Settings -->
              <h3 class="mb-5 mt-10 font-medium text-black dark:text-white border-b border-stroke pb-2 dark:border-strokedark text-lg">
                Координаты (Карта)
              </h3>
              <div class="mb-5.5 flex flex-col gap-5.5 sm:flex-row">
                <div class="w-full sm:w-1/2">
                  <label class="mb-3 block text-sm font-medium text-black dark:text-white">Широта (Latitude)</label>
                  <input v-model="org.latitude" type="number" step="any" placeholder="Например: 43.238949" class="w-full rounded border border-stroke bg-gray-50 py-2.5 px-4.5 text-black focus:border-primary focus-visible:outline-none dark:border-strokedark dark:bg-bg-dark dark:text-white dark:focus:border-primary" />
                </div>
                <div class="w-full sm:w-1/2">
                  <label class="mb-3 block text-sm font-medium text-black dark:text-white">Долгота (Longitude)</label>
                  <input v-model="org.longitude" type="number" step="any" placeholder="Например: 76.889709" class="w-full rounded border border-stroke bg-gray-50 py-2.5 px-4.5 text-black focus:border-primary focus-visible:outline-none dark:border-strokedark dark:bg-bg-dark dark:text-white dark:focus:border-primary" />
                </div>
              </div>

              <!-- Graphic settings -->
              <h3 class="mb-5 mt-10 font-medium text-black dark:text-white border-b border-stroke pb-2 dark:border-strokedark text-lg">
                График работы
              </h3>
              <div class="mb-5.5">
                <div class="flex flex-col gap-5.5 sm:flex-row">
                  <div class="w-full sm:w-1/2">
                    <label class="mb-3 block text-sm font-medium text-black dark:text-white">Начало дня</label>
                    <input v-model="org.work_start" type="time" class="w-full rounded border border-stroke bg-gray-50 py-2.5 px-4.5 text-black focus:border-primary focus-visible:outline-none dark:border-strokedark dark:bg-bg-dark dark:text-white dark:focus:border-primary" required />
                  </div>
                  <div class="w-full sm:w-1/2">
                    <label class="mb-3 block text-sm font-medium text-black dark:text-white">Конец дня</label>
                    <input v-model="org.work_end" type="time" class="w-full rounded border border-stroke bg-gray-50 py-2.5 px-4.5 text-black focus:border-primary focus-visible:outline-none dark:border-strokedark dark:bg-bg-dark dark:text-white dark:focus:border-primary" required />
                  </div>
                </div>
              </div>

              <div class="mb-5.5">
                <h4 class="mb-4 text-sm font-medium text-black dark:text-white">Обеденный перерыв</h4>
                <div class="flex flex-col gap-5.5 sm:flex-row">
                  <div class="w-full sm:w-1/2">
                    <label class="mb-3 block text-sm font-medium text-black dark:text-white">Начало</label>
                    <input v-model="org.lunch_start" type="time" class="w-full rounded border border-stroke bg-gray-50 py-2.5 px-4.5 text-black focus:border-primary focus-visible:outline-none dark:border-strokedark dark:bg-bg-dark dark:text-white dark:focus:border-primary" required />
                  </div>
                  <div class="w-full sm:w-1/2">
                    <label class="mb-3 block text-sm font-medium text-black dark:text-white">Конец</label>
                    <input v-model="org.lunch_end" type="time" class="w-full rounded border border-stroke bg-gray-50 py-2.5 px-4.5 text-black focus:border-primary focus-visible:outline-none dark:border-strokedark dark:bg-bg-dark dark:text-white dark:focus:border-primary" required />
                  </div>
                </div>
              </div>

              <div class="mb-5.5">
                <h4 class="mb-4 text-sm font-medium text-black dark:text-white">Настройки записи</h4>
                <div class="flex flex-col gap-5.5 sm:flex-row">
                  <div class="w-full sm:w-1/2">
                    <label class="mb-3 block text-sm font-medium text-black dark:text-white">Базовый шаг записи (минут)</label>
                    <input v-model="org.slot_duration" type="number" min="5" step="5" class="w-full rounded border border-stroke bg-gray-50 py-2.5 px-4.5 text-black focus:border-primary focus-visible:outline-none dark:border-strokedark dark:bg-bg-dark dark:text-white dark:focus:border-primary" required />
                    <p class="mt-2 text-xs text-body italic">
                      * Определяет интервал времени между доступными слотами для записи.
                    </p>
                  </div>
                </div>
              </div>

              <!-- Notification Settings -->
              <h3 class="mb-5 mt-10 font-medium text-black dark:text-white border-b border-stroke pb-2 dark:border-strokedark text-lg">
                Уведомления и напоминания (Бот)
              </h3>
              
              <div class="mb-5.5">
                <label class="flex items-center cursor-pointer">
                  <div class="relative">
                    <input type="checkbox" v-model="org.is_reminders_enabled" class="sr-only" />
                    <div :class="org.is_reminders_enabled ? 'bg-primary' : 'bg-gray-400'" class="block h-8 w-14 rounded-full transition"></div>
                    <div :class="org.is_reminders_enabled ? 'translate-x-full' : ''" class="absolute left-1 top-1 h-6 w-6 rounded-full bg-white transition shadow-sm border border-gray-100"></div>
                  </div>
                  <div class="ml-3 font-medium text-black dark:text-white">
                    Включить автоматические напоминания клиентам
                  </div>
                </label>
                <p class="mt-2 text-xs text-body italic">
                  * Если включено, сервер будет отправлять сообщение в Telegram за указанное время до начала записи.
                </p>
              </div>

              <div v-if="org.is_reminders_enabled" class="space-y-5.5 mb-10">
                <div class="w-full sm:w-1/2">
                  <label class="mb-3 block text-sm font-medium text-black dark:text-white">
                    За сколько часов до записи отправлять?
                  </label>
                  <input
                    v-model="org.reminder_hours_before"
                    type="number"
                    min="1"
                    max="48"
                    class="w-full rounded border border-stroke bg-gray-50 py-3 px-4.5 text-black focus:border-primary focus-visible:outline-none dark:border-strokedark dark:bg-bg-dark dark:text-white dark:focus:border-primary"
                  />
                </div>

                <div>
                  <label class="mb-3 block text-sm font-medium text-black dark:text-white">
                    Шаблон напоминания (RU)
                  </label>
                  <textarea
                    v-model="org.reminder_template_ru"
                    rows="4"
                    class="w-full rounded border border-stroke bg-gray-50 py-3 px-4.5 text-black focus:border-primary focus-visible:outline-none dark:border-strokedark dark:bg-bg-dark dark:text-white dark:focus:border-primary text-sm"
                  ></textarea>
                </div>

                <div>
                  <label class="mb-3 block text-sm font-medium text-black dark:text-white">
                    Шаблон напоминания (KZ)
                  </label>
                  <textarea
                    v-model="org.reminder_template_kz"
                    rows="4"
                    class="w-full rounded border border-stroke bg-gray-50 py-3 px-4.5 text-black focus:border-primary focus-visible:outline-none dark:border-strokedark dark:bg-bg-dark dark:text-white dark:focus:border-primary text-sm"
                  ></textarea>
                </div>

                <div class="p-4 bg-gray-100 dark:bg-bg-dark border border-stroke dark:border-strokedark rounded">
                  <h5 class="text-xs font-bold uppercase text-body mb-2">Доступные плейсхолдеры:</h5>
                  <div class="grid grid-cols-2 gap-2 text-[10px] text-body">
                    <div><code>{Organization_name}</code> - Название салона</div>
                    <div><code>{User_name}</code> - Имя клиента</div>
                    <div><code>{Service_name}</code> - Название услуги</div>
                    <div><code>{Master_name}</code> - Имя мастера</div>
                    <div><code>{Start_time}</code> - Время записи (ЧЧ:ММ)</div>
                  </div>
                </div>
              </div>

              <div v-if="successMsg" class="mb-5.5 flex w-full rounded-[10px] border-l-[6px] border-success bg-success/10 py-4 px-7 shadow-md dark:bg-[#1b1b24] md:p-9">
                  <div class="mr-5 flex h-9 w-9 items-center justify-center rounded-lg bg-success text-white">
                      <Icon icon="mdi:check-circle" width="24" />
                  </div>
                  <div class="w-full">
                      <h5 class="mb-2 text-lg font-bold text-success">Успех!</h5>
                      <p class="text-body">{{ successMsg }}</p>
                  </div>
              </div>

              <div v-if="errorMsg" class="mb-5.5 flex w-full rounded-[10px] border-l-[6px] border-danger bg-danger/10 py-4 px-7 shadow-md dark:bg-[#1b1b24] md:p-9">
                  <div class="mr-5 flex h-9 w-9 items-center justify-center rounded-lg bg-danger text-white">
                      <Icon icon="mdi:alert-circle" width="24" />
                  </div>
                  <div class="w-full">
                      <h5 class="mb-2 text-lg font-bold text-danger">Ошибка</h5>
                      <p class="text-body">{{ errorMsg }}</p>
                  </div>
              </div>

              <div class="flex justify-end gap-4.5">
                <button
                  class="flex justify-center rounded bg-primary py-2 px-6 font-medium text-white hover:bg-opacity-90 transition-all hover:scale-105"
                  type="submit"
                  :disabled="saving"
                >
                  <Icon icon="mdi:content-save" width="20" class="mr-2" />
                  {{ saving ? 'Сохранение...' : 'Сохранить изменения' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import api from '../../api'
import { Icon } from '@iconify/vue'

const DEFAULT_TEMPLATE_RU = "Привет, {User_name}! Напоминаем о вашей записи в {Organization_name} в {Start_time}.\n\nУслуга: {Service_name}\nМастер: {Master_name}\n\nВы придете?"
const DEFAULT_TEMPLATE_KZ = "Сәлем, {User_name}! {Organization_name} салонындағы сағат {Start_time}-дегі жазбаңызды еске саламыз.\n\nҚызмет: {Service_name}\nШебер: {Master_name}\n\nКелесіз бе?"

const loading = ref(true)
const saving = ref(false)
const successMsg = ref('')
const errorMsg = ref('')

const org = ref({
  name: '',
  address: '',
  bot_token: '',
  bot_username: '',
  tma_name: '',
  work_start: '09:00',
  work_end: '20:00',
  lunch_start: '13:00',
  lunch_end: '14:00',
  greeting_text: 'Добро пожаловать!',
  instagram_link: '',
  whatsapp_number: '',
  design_color: '#c9a84c',
  latitude: null,
  longitude: null,
  is_reminders_enabled: false,
  reminder_hours_before: 1,
  reminder_template_ru: '',
  reminder_template_kz: '',
  slot_duration: 30
})

watch(() => org.value.is_reminders_enabled, (newVal) => {
  if (newVal) {
    if (!org.value.reminder_template_ru) {
      org.value.reminder_template_ru = DEFAULT_TEMPLATE_RU
    }
    if (!org.value.reminder_template_kz) {
      org.value.reminder_template_kz = DEFAULT_TEMPLATE_KZ
    }
  }
})

const logoFile = ref(null)

const webhookStatus = ref(null)
const webhookLoading = ref(false)
const webhookSettingUp = ref(false)

const fetchWebhookInfo = async () => {
  if (!org.value.bot_token) return
  try {
    webhookLoading.value = true
    const response = await api.get('/api/organization/webhook-info/')
    if (response.data?.ok) {
      webhookStatus.value = response.data.result
    }
  } catch (err) {
    console.error('Failed to fetch webhook info:', err)
  } finally {
    webhookLoading.value = false
  }
}

const setupWebhook = async () => {
  try {
    webhookSettingUp.value = true
    const response = await api.post('/api/organization/set-webhook/')
    if (response.data?.ok) {
      successMsg.value = 'Webhook успешно настроен!'
      await fetchWebhookInfo()
      setTimeout(() => (successMsg.value = ''), 3000)
    } else {
      errorMsg.value = 'Telegram отклонил запрос: ' + (response.data?.description || 'неизвестная ошибка')
    }
  } catch (err) {
    console.error('Failed to set webhook:', err)
    errorMsg.value = 'Ошибка при настройке Webhook. Проверьте токен бота.'
  } finally {
    webhookSettingUp.value = false
  }
}

const handleLogoUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    logoFile.value = file
  }
}

const formatTime = (timeStr) => {
  if (!timeStr) return ''
  return timeStr.slice(0, 5)
}

const fetchOrganization = async () => {
  try {
    loading.value = true
    const response = await api.get('/api/organization/')
    
    if (response.data) {
      org.value = {
        ...response.data,
        work_start: formatTime(response.data.work_start),
        work_end: formatTime(response.data.work_end),
        lunch_start: formatTime(response.data.lunch_start),
        lunch_end: formatTime(response.data.lunch_end)
      }
      // If logo exists from backend, we might want to display it
      if (response.data.logo) {
         org.value.logo_url = response.data.logo
      }
    }
  } catch (err) {
    if (err.response?.status === 404) {
      errorMsg.value = 'Данные организации не найдены в базе. Будет создана новая запись при сохранении.'
    } else {
      console.error('Ошибка загрузки:', err)
      errorMsg.value = 'Ошибка при загрузке данных организации'
    }
  } finally {
    loading.value = false
    if (org.value.bot_token) {
      fetchWebhookInfo()
    }
  }
}

const saveOrganization = async () => {
  try {
    saving.value = true
    successMsg.value = ''
    errorMsg.value = ''
    
    const formData = new FormData()
    
    // Append all text fields
    for (const key in org.value) {
      if (key === 'logo_url' || key === 'logo') continue // Skip raw logo URL/object, we handle file separately
      if (org.value[key] !== null && org.value[key] !== undefined) {
          formData.append(key, org.value[key])
      }
    }
    
    // Append logo file if selected
    if (logoFile.value) {
      formData.append('logo', logoFile.value)
    }
    
    await api.put('/api/organization/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    successMsg.value = 'Информация об организации успешно обновлена!'
    // Re-fetch to get updated logo URL
    await fetchOrganization()
    
    setTimeout(() => {
      successMsg.value = ''
    }, 3000)
    
  } catch (err) {
    console.error('Ошибка сохранения:', err)
    errorMsg.value = 'Не удалось сохранить настройки. Проверьте данные и попробуйте снова.'
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  fetchOrganization()
})
</script>

<style scoped>
.max-w-270 {
  max-width: 67.5rem;
}
.text-title-md2 {
  font-size: 1.625rem;
  line-height: 2.125rem;
}
.mb-5.5 {
  margin-bottom: 1.375rem;
}
.gap-5.5 {
  gap: 1.375rem;
}
</style>
