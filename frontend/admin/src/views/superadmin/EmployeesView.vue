<template>
  <div class="mx-auto max-w-7xl">
    <!-- Breadcrumb Start -->
    <div class="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <h2 class="text-title-md2 font-bold text-black dark:text-white">
        Сотрудники
      </h2>
      <nav>
        <ol class="flex items-center gap-2">
          <li>
            <router-link class="font-medium" to="/admin/calendar">Dashboard /</router-link>
          </li>
          <li class="font-medium text-primary">Сотрудники</li>
        </ol>
      </nav>
    </div>
    <!-- Breadcrumb End -->

    <div class="rounded-sm border border-stroke bg-white shadow-default dark:border-strokedark dark:bg-bg-dark-2">
      <div class="flex flex-wrap items-center justify-between border-b border-stroke py-4 px-4 dark:border-strokedark sm:px-6 xl:px-7.5">
        <h3 class="font-medium text-black dark:text-white">Список сотрудников</h3>
        <button 
          @click="openAddModal"
          class="inline-flex items-center justify-center rounded-md bg-primary py-2 px-6 text-center font-medium text-white hover:bg-opacity-90 transition-all active:scale-95"
        >
          Добавить сотрудника
        </button>
      </div>

      <div class="p-4 sm:p-6 xl:p-7.5">
        <div v-if="loading" class="flex h-40 items-center justify-center">
            <div class="h-10 w-10 animate-spin rounded-full border-4 border-solid border-primary border-t-transparent"></div>
        </div>
        
        <div v-else-if="masters.length === 0" class="flex flex-col items-center justify-center py-20 text-center">
            <div class="mb-4 flex h-20 w-20 items-center justify-center rounded-full bg-primary/10 text-primary">
                <Icon icon="mdi:account-group-outline" width="40" />
            </div>
            <h4 class="mb-2 text-xl font-bold text-black dark:text-white">Сотрудники не найдены</h4>
            <p class="text-body">Добавьте первого сотрудника в вашу организацию.</p>
        </div>

        <div v-else class="max-w-full overflow-x-auto">
          <table class="w-full table-auto">
            <thead>
              <tr class="bg-gray-2 text-left dark:bg-meta-4">
                <th class="py-4 px-4 font-medium text-black dark:text-white xl:pl-11">Сотрудник</th>
                <th class="py-4 px-4 font-medium text-black dark:text-white">Роль</th>
                <th class="py-4 px-4 font-medium text-black dark:text-white">Контакты</th>
                <th class="py-4 px-4 font-medium text-black dark:text-white">Цвет</th>
                <th class="py-4 px-4 font-medium text-black dark:text-white">Статус</th>
                <th class="py-4 px-4 font-medium text-black dark:text-white text-right">Действия</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="master in masters" :key="master.id" class="border-b border-stroke dark:border-strokedark">
                <td class="py-5 px-4 pl-9 xl:pl-11">
                  <div class="flex items-center gap-3">
                    <div class="h-12 w-12 shrink-0 rounded-full overflow-hidden bg-gray-100 flex items-center justify-center border border-stroke dark:border-strokedark">
                      <img v-if="master.photo_url" :src="master.photo_url" alt="Photo" class="h-full w-full object-cover" />
                      <Icon v-else icon="mdi:account" width="24" class="text-bodydark" />
                    </div>
                    <div>
                        <h5 class="font-medium text-black dark:text-white">{{ master.first_name }} {{ master.last_name }}</h5>
                        <p v-if="master.role === 'master'" class="text-xs text-body">{{ master.services_detail?.length || 0 }} услуг</p>
                    </div>
                  </div>
                </td>
                <td class="py-5 px-4">
                  <span class="inline-flex rounded-full py-1 px-3 text-sm font-medium bg-gray opacity-80 text-black dark:bg-meta-4 dark:text-white">
                    {{ master.role === 'admin' ? 'Администратор' : 'Мастер' }}
                  </span>
                </td>
                <td class="py-5 px-4">
                  <p class="text-black dark:text-white">{{ master.phone || '—' }}</p>
                </td>
                <td class="py-5 px-4">
                  <div class="flex items-center gap-2">
                      <span class="h-5 w-5 rounded-full border border-stroke dark:border-strokedark" :style="{ backgroundColor: master.color }"></span>
                      <span class="text-xs font-mono text-body">{{ master.color }}</span>
                  </div>
                </td>
                <td class="py-5 px-4">
                  <span 
                    class="inline-flex rounded-full py-1 px-3 text-sm font-medium"
                    :class="master.is_active ? 'bg-success/10 text-success' : 'bg-danger/10 text-danger'"
                  >
                    {{ master.is_active ? 'Активен' : 'Неактивен' }}
                  </span>
                </td>
                <td class="py-5 px-4">
                  <div class="flex items-center justify-end space-x-3.5">
                    <button @click="editMaster(master)" class="hover:text-primary transition-colors" title="Редактировать">
                      <Icon icon="mdi:pencil-outline" width="18" />
                    </button>
                    <button 
                        @click="toggleActive(master)" 
                        class="transition-colors"
                        :class="master.is_active ? 'hover:text-danger' : 'hover:text-success'"
                        :title="master.is_active ? 'Деактивировать' : 'Активировать'"
                    >
                      <Icon :icon="master.is_active ? 'mdi:eye-off-outline' : 'mdi:eye-outline'" width="18" />
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Master Modal -->
    <div v-if="showModal" class="fixed inset-0 z-9999 flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm">
      <div class="w-full max-w-180 rounded-lg bg-white py-8 px-8 dark:bg-bg-dark-2 sm:px-12.5 overflow-y-auto max-h-[95vh]">
        <div class="flex justify-between items-center mb-6">
            <h3 class="text-2xl font-bold text-black dark:text-white">
              {{ isEditing ? 'Редактировать сотрудника' : 'Добавить сотрудника' }}
            </h3>
            <button @click="showModal = false" class="text-body hover:text-danger">
              <Icon icon="mdi:close" width="24" />
            </button>
        </div>

        <form @submit.prevent="saveMaster">
          <!-- Photo Upload -->
          <div class="mb-6 flex flex-col items-center">
            <div 
              class="relative h-28 w-28 cursor-pointer overflow-hidden rounded-full border-4 border-stroke dark:border-strokedark group"
              @click="triggerFileInput"
            >
              <img v-if="photoPreview || form.existing_photo_url" :src="photoPreview || form.existing_photo_url" alt="Photo" class="h-full w-full object-cover" />
              <div v-else class="flex h-full w-full items-center justify-center bg-gray-100 dark:bg-meta-4 text-bodydark">
                <Icon icon="mdi:account" width="40" />
              </div>
              <div class="absolute inset-0 flex items-center justify-center bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity rounded-full">
                <Icon icon="mdi:camera" width="28" class="text-white" />
              </div>
            </div>
            <input ref="fileInputRef" type="file" accept="image/*" class="hidden" @change="onPhotoSelected" />
            <p class="mt-2 text-xs text-body">Нажмите на аватар чтобы загрузить фото</p>
          </div>

          <div class="mb-5 grid grid-cols-2 gap-4">
              <div>
                <label class="mb-2.5 block font-medium text-black dark:text-white">Имя <span class="text-danger">*</span></label>
                <input v-model="form.first_name" type="text" placeholder="Иван"
                  class="w-full rounded border border-stroke bg-transparent py-3 px-5 outline-none transition focus:border-primary dark:border-form-strokedark dark:bg-form-input dark:text-white"
                  required />
              </div>
              <div>
                <label class="mb-2.5 block font-medium text-black dark:text-white">Фамилия</label>
                <input v-model="form.last_name" type="text" placeholder="Иванов"
                  class="w-full rounded border border-stroke bg-transparent py-3 px-5 outline-none transition focus:border-primary dark:border-form-strokedark dark:bg-form-input dark:text-white" />
              </div>
          </div>

          <div class="mb-5 grid grid-cols-3 gap-4">
            <div>
              <label class="mb-2.5 block font-medium text-black dark:text-white">Номер телефона</label>
              <input v-model="form.phone" type="text" placeholder="+7 (___) ___-__-__"
                class="w-full rounded border border-stroke bg-transparent py-3 px-5 outline-none transition focus:border-primary dark:border-form-strokedark dark:bg-form-input dark:text-white" />
            </div>
            <div>
              <label class="mb-2.5 block font-medium text-black dark:text-white">Телеграм ID</label>
              <input v-model="form.telegram_id" type="number" placeholder="ID"
                class="w-full rounded border border-stroke bg-transparent py-3 px-5 outline-none transition focus:border-primary dark:border-form-strokedark dark:bg-form-input dark:text-white" />
            </div>
            <div>
              <label class="mb-2.5 block font-medium text-black dark:text-white">Роль</label>
              <div class="relative z-20 bg-transparent dark:bg-form-input">
                <select v-model="form.role" :disabled="isEditing" class="relative z-20 w-full appearance-none rounded border border-stroke bg-transparent py-3 px-5 outline-none transition focus:border-primary active:border-primary dark:border-form-strokedark dark:bg-form-input dark:text-white disabled:opacity-50 disabled:cursor-not-allowed">
                  <option value="master">Мастер</option>
                  <option value="admin">Администратор</option>
                </select>
                <span class="absolute top-1/2 right-4 z-30 -translate-y-1/2">
                  <Icon icon="mdi:chevron-down" width="20" />
                </span>
              </div>
            </div>
          </div>

          <template v-if="form.role === 'master'">
          <!-- Bio / Markdown Editor -->
          <div class="mb-5">
            <label class="mb-2.5 block font-medium text-black dark:text-white">О мастере (Bio)</label>
            <div class="rounded border border-stroke dark:border-form-strokedark overflow-hidden">
              <!-- Toolbar -->
              <div class="flex flex-wrap items-center gap-1 border-b border-stroke bg-gray-50 px-2 py-1.5 dark:border-strokedark dark:bg-meta-4">
                <button type="button" @click="insertMd('**', '**')" class="md-btn" title="Жирный"><Icon icon="mdi:format-bold" width="16" /></button>
                <button type="button" @click="insertMd('*', '*')" class="md-btn" title="Курсив"><Icon icon="mdi:format-italic" width="16" /></button>
                <button type="button" @click="insertMd('# ', '')" class="md-btn" title="Заголовок"><Icon icon="mdi:format-header-1" width="16" /></button>
                <button type="button" @click="insertMd('## ', '')" class="md-btn" title="Подзаголовок"><Icon icon="mdi:format-header-2" width="16" /></button>
                <span class="mx-1 h-5 w-px bg-stroke dark:bg-strokedark"></span>
                <button type="button" @click="insertMd('- ', '')" class="md-btn" title="Список"><Icon icon="mdi:format-list-bulleted" width="16" /></button>
                <button type="button" @click="insertMd('1. ', '')" class="md-btn" title="Нумерованный список"><Icon icon="mdi:format-list-numbered" width="16" /></button>
                <span class="mx-1 h-5 w-px bg-stroke dark:bg-strokedark"></span>
                <button type="button" @click="insertMd('`', '`')" class="md-btn" title="Код"><Icon icon="mdi:code-tags" width="16" /></button>
                <button type="button" @click="insertMd('> ', '')" class="md-btn" title="Цитата"><Icon icon="mdi:format-quote-close" width="16" /></button>
                <div class="ml-auto flex rounded overflow-hidden border border-stroke dark:border-strokedark text-xs">
                  <button type="button" @click="bioTab = 'write'" class="px-2 py-0.5 transition" :class="bioTab === 'write' ? 'bg-primary text-white' : 'text-body hover:bg-gray-100 dark:hover:bg-meta-4'">Редактор</button>
                  <button type="button" @click="bioTab = 'preview'" class="px-2 py-0.5 transition" :class="bioTab === 'preview' ? 'bg-primary text-white' : 'text-body hover:bg-gray-100 dark:hover:bg-meta-4'">Предпросмотр</button>
                </div>
              </div>
              <!-- Editor area -->
              <textarea
                v-if="bioTab === 'write'"
                ref="bioTextareaRef"
                v-model="form.bio"
                rows="6"
                placeholder="Краткое описание квалификации мастера... Поддерживается **Markdown**."
                class="w-full bg-transparent px-4 py-3 text-sm text-black outline-none dark:text-white resize-none"
              ></textarea>
              <!-- Preview area -->
              <div
                v-else
                class="prose prose-sm max-w-none min-h-[9rem] px-4 py-3 dark:prose-invert text-black dark:text-white"
                v-html="renderedBio"
              ></div>
            </div>
            <p class="mt-1 text-xs text-body">Используйте Markdown для форматирования текста</p>
          </div>

          <div class="mb-5">
              <label class="mb-2.5 block font-medium text-black dark:text-white">Цвет в календаре</label>
              <div class="flex items-center gap-3">
                  <input v-model="form.color" type="color"
                    class="h-10 w-10 cursor-pointer rounded border-none bg-transparent" />
                  <input v-model="form.color" type="text"
                    class="max-w-xs rounded border border-stroke bg-transparent py-2.5 px-4 font-mono text-sm uppercase outline-none focus:border-primary dark:border-form-strokedark dark:bg-form-input dark:text-white" />
              </div>
          </div>

          <div class="mb-8">
            <label class="mb-2.5 block font-medium text-black dark:text-white">Услуги мастера</label>
            <div class="grid grid-cols-2 gap-2 max-h-40 overflow-y-auto rounded border border-stroke p-3 dark:border-form-strokedark">
                <div v-for="service in services" :key="service.id" class="flex items-center">
                    <label class="flex cursor-pointer items-center text-sm text-black dark:text-white">
                        <input type="checkbox" v-model="form.services" :value="service.id"
                            class="mr-2 h-4 w-4 rounded border-stroke text-primary focus:ring-primary dark:border-strokedark" />
                        {{ service.name }}
                    </label>
                </div>
            </div>
            <p v-if="services.length === 0" class="text-xs text-warning mt-1">Сначала добавьте услуги в разделе «Услуги»</p>
          </div>
          </template>

          <div class="flex gap-4">
            <button type="button" @click="showModal = false"
              class="flex-1 rounded border border-stroke py-3 px-6 text-center font-medium text-black transition hover:border-danger hover:bg-danger hover:text-white dark:border-strokedark dark:text-white">
              Отмена
            </button>
            <button type="submit" :disabled="saving"
              class="flex-1 rounded bg-primary py-3 px-6 text-center font-medium text-white transition hover:bg-opacity-90 active:scale-95 disabled:opacity-50">
              <Icon v-if="saving" icon="mdi:loading" class="animate-spin inline mr-2" />
              {{ isEditing ? 'Обновить' : 'Добавить' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, computed } from 'vue'
import { Icon } from '@iconify/vue'
import api from '../../api'

const masters = ref([])
const services = ref([])
const loading = ref(true)
const saving = ref(false)
const showModal = ref(false)
const isEditing = ref(false)
const currentMasterId = ref(null)
const bioTab = ref('write')
const fileInputRef = ref(null)
const bioTextareaRef = ref(null)
const photoPreview = ref(null)
const selectedPhotoFile = ref(null)

const form = reactive({
    first_name: '',
    last_name: '',
    phone: '',
    role: 'master',
    color: '#3C50E0',
    telegram_id: '',
    bio: '',
    services: [],
    existing_photo_url: null
})

// Simple markdown renderer (no external deps)
const renderedBio = computed(() => {
  if (!form.bio) return '<p class="text-body italic">Предпросмотр пуст...</p>'
  let html = form.bio
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/^### (.+)$/gm, '<h3 class="text-base font-bold mt-3 mb-1">$1</h3>')
    .replace(/^## (.+)$/gm, '<h2 class="text-lg font-bold mt-4 mb-1">$1</h2>')
    .replace(/^# (.+)$/gm, '<h1 class="text-xl font-bold mt-4 mb-2">$1</h1>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/`(.+?)`/g, '<code class="bg-gray-100 dark:bg-meta-4 px-1 rounded text-sm font-mono">$1</code>')
    .replace(/^> (.+)$/gm, '<blockquote class="border-l-2 border-primary pl-3 italic text-body">$1</blockquote>')
    .replace(/^- (.+)$/gm, '<li class="ml-4 list-disc">$1</li>')
    .replace(/^(\d+)\. (.+)$/gm, '<li class="ml-4 list-decimal">$2</li>')
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br/>')
  return `<p>${html}</p>`
})

const fetchMasters = async () => {
    try {
        loading.value = true
        const response = await api.get('/api/organization/employees/')
        masters.value = response.data.results || response.data || []
    } catch (err) {
        console.error('Error fetching masters:', err)
    } finally {
        loading.value = false
    }
}

const fetchServices = async () => {
    try {
        const response = await api.get('/api/services/')
        services.value = response.data.results || response.data || []
    } catch (err) {
        console.error('Error fetching services:', err)
    }
}

const openAddModal = () => {
    isEditing.value = false
    currentMasterId.value = null
    bioTab.value = 'write'
    Object.assign(form, {
        first_name: '', last_name: '', phone: '', role: 'master',
        color: '#3C50E0', telegram_id: '', bio: '',
        services: [], existing_photo_url: null
    })
    photoPreview.value = null
    selectedPhotoFile.value = null
    showModal.value = true
}

const editMaster = (master) => {
    isEditing.value = true
    currentMasterId.value = master.id
    bioTab.value = 'write'
    Object.assign(form, {
        first_name: master.first_name,
        last_name: master.last_name,
        phone: master.phone || '',
        role: master.role || 'master',
        color: master.color || '#3C50E0',
        telegram_id: master.telegram_id || '',
        bio: master.bio || '',
        services: master.services || [],
        existing_photo_url: master.photo_url || null
    })
    photoPreview.value = null
    selectedPhotoFile.value = null
    showModal.value = true
}

const triggerFileInput = () => fileInputRef.value?.click()

const onPhotoSelected = (e) => {
    const file = e.target.files[0]
    if (!file) return
    selectedPhotoFile.value = file
    const reader = new FileReader()
    reader.onload = (ev) => { photoPreview.value = ev.target.result }
    reader.readAsDataURL(file)
}

const saveMaster = async () => {
    try {
        saving.value = true
        const payload = {
            first_name: form.first_name,
            last_name: form.last_name,
            phone: form.phone,
            role: form.role,
            color: form.color,
            telegram_id: form.telegram_id || null,
            bio: form.bio,
            services: form.services
        }

        let savedMaster
        if (isEditing.value) {
            const resp = await api.patch(`/api/organization/employees/${currentMasterId.value}/`, payload)
            savedMaster = resp.data
        } else {
            const resp = await api.post('/api/organization/employees/', payload)
            savedMaster = resp.data
        }

        // Upload photo separately if a file was chosen
        if (selectedPhotoFile.value && savedMaster?.id) {
            const formData = new FormData()
            formData.append('photo', selectedPhotoFile.value)
            await api.post(`/api/organization/employees/${savedMaster.id}/upload-photo/`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            })
        }

        showModal.value = false
        fetchMasters()
    } catch (err) {
        console.error('Error saving master:', err)
        alert('Ошибка при сохранении данных мастера')
    } finally {
        saving.value = false
    }
}

const toggleActive = async (master) => {
    try {
        await api.patch(`/api/organization/employees/${master.id}/`, { is_active: !master.is_active })
        fetchMasters()
    } catch (err) {
        console.error('Error toggling status:', err)
    }
}

// Markdown toolbar helpers
const insertMd = (prefix, suffix) => {
    const el = bioTextareaRef.value
    if (!el) return
    const start = el.selectionStart
    const end = el.selectionEnd
    const selected = form.bio.substring(start, end)
    const replacement = prefix + (selected || 'текст') + suffix
    form.bio = form.bio.substring(0, start) + replacement + form.bio.substring(end)
    // restore cursor
    setTimeout(() => {
        el.focus()
        el.setSelectionRange(start + prefix.length, start + prefix.length + (selected || 'текст').length)
    }, 0)
}

onMounted(() => {
    fetchMasters()
    fetchServices()
})
</script>

<style scoped>
.text-title-md2 {
  font-size: 1.625rem;
  line-height: 2.125rem;
}
.max-w-180 {
  max-width: 45rem;
}
.md-btn {
  display: flex;
  height: 1.75rem;
  width: 1.75rem;
  align-items: center;
  justify-content: center;
  border-radius: 0.25rem;
  color: #64748b;
  transition: background-color 0.15s, color 0.15s;
}
.md-btn:hover {
  background-color: #f3f4f6;
  color: #1a222c;
}
.dark .md-btn:hover {
  background-color: #313d4a;
  color: white;
}
</style>
