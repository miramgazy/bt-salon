<template>
  <div class="mx-auto max-w-screen-2xl">
    <!-- Search and Action Bar -->
    <div class="mb-6 rounded-sm border border-stroke bg-white p-4 shadow-default dark:border-strokedark dark:bg-bg-dark-2 md:p-6 flex flex-wrap items-center justify-between gap-4">
      <div class="relative w-full md:w-96">
        <span class="absolute left-4 top-1/2 -translate-y-1/2 text-body">
          <Icon icon="mdi:magnify" width="20" />
        </span>
        <input
          type="text"
          v-model="searchQuery"
          @input="handleSearch"
          placeholder="Поиск по имени или телефону..."
          class="w-full rounded-lg border border-stroke bg-transparent py-2 pl-11 pr-4 outline-none focus:border-primary dark:border-strokedark dark:bg-meta-4 text-black dark:text-white"
        />
      </div>

      <!-- Tabs -->
      <div class="flex items-center gap-2 overflow-x-auto">
        <button 
          @click="changeTab('all')"
          :class="['px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap', 
                   activeTab === 'all' ? 'bg-primary text-white' : 'bg-gray-100 text-body hover:bg-gray-200 dark:bg-meta-4 dark:text-white']"
        >
          Все клиенты
        </button>
        <button 
          @click="changeTab('offline')"
          :class="['px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap', 
                   activeTab === 'offline' ? 'bg-primary text-white' : 'bg-gray-100 text-body hover:bg-gray-200 dark:bg-meta-4 dark:text-white']"
        >
          Офлайн
        </button>
        <button 
          @click="changeTab('tma')"
          :class="['px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap', 
                   activeTab === 'tma' ? 'bg-primary text-white' : 'bg-gray-100 text-body hover:bg-gray-200 dark:bg-meta-4 dark:text-white']"
        >
          TMA клиенты
        </button>
      </div>
      
      <div class="flex items-center gap-4 ml-auto">
        <h4 class="text-xl font-bold text-black dark:text-white mr-4">Клиенты ({{ totalCount }})</h4>
        <div class="flex items-center gap-2">
            <span class="text-sm text-body">Строк:</span>
            <select 
              v-model="pageSize" 
              @change="handlePageSizeChange"
              class="rounded border border-stroke bg-transparent py-1 px-2 outline-none focus:border-primary dark:border-strokedark dark:bg-meta-4 text-sm"
            >
              <option :value="20">20</option>
              <option :value="50">50</option>
              <option :value="100">100</option>
            </select>
        </div>
      </div>
    </div>

    <!-- Table Card -->
    <div class="rounded-sm border border-stroke bg-white px-5 pt-6 pb-2.5 shadow-default dark:border-strokedark dark:bg-bg-dark-2 sm:px-7.5 xl:pb-1">
      <div class="max-w-full overflow-x-auto">
        <table class="w-full table-auto">
          <thead>
            <tr class="bg-gray-2 text-left dark:bg-meta-4">
              <th class="min-w-[220px] py-4 px-4 font-medium text-black dark:text-white xl:pl-11">Имя</th>
              <th class="min-w-[150px] py-4 px-4 font-medium text-black dark:text-white">Номер телефона</th>
              <th class="min-w-[150px] py-4 px-4 font-medium text-black dark:text-white">Телеграм ID</th>
              <th class="py-4 px-4 font-medium text-black dark:text-white">Действие</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="client in clients" :key="client.id" class="border-b border-[#eee] dark:border-strokedark hover:bg-gray-50 dark:hover:bg-meta-4/20 transition-colors">
              <td class="py-5 px-4 pl-9 xl:pl-11">
                <h5 class="font-medium text-black dark:text-white">{{ client.full_name || '---' }}</h5>
              </td>
              <td class="py-5 px-4 text-black dark:text-white">
                {{ client.phone }}
              </td>
              <td class="py-5 px-4 text-black dark:text-white">
                <span v-if="client.telegram_id" class="inline-flex items-center gap-1 rounded bg-info/10 py-1 px-2 text-xs font-medium text-info">
                  <Icon icon="mdi:telegram" /> {{ client.telegram_id }}
                </span>
                <span v-else class="text-body text-xs italic">не привязан</span>
              </td>
              <td class="py-5 px-4">
                <div class="flex items-center space-x-3.5">
                  <button @click="openEdit(client)" class="hover:text-primary transition-colors text-body" title="Редактировать">
                    <Icon icon="mdi:pencil-outline" width="20" />
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="clients.length === 0 && !loading">
                <td colspan="4" class="py-10 text-center text-body italic">Клиентов не найдено</td>
            </tr>
            <tr v-if="loading">
                <td colspan="4" class="py-10 text-center">
                    <Icon icon="mdi:loading" class="animate-spin text-primary mx-auto" width="40" />
                </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="flex items-center justify-center gap-2 py-6">
        <div class="flex items-center gap-1">
          <button 
            v-for="page in visiblePages" 
            :key="page"
            @click="changePage(page)"
            class="flex h-9 w-9 items-center justify-center rounded border border-stroke font-medium transition-all hover:bg-primary hover:text-white dark:border-strokedark"
            :class="currentPage === page ? 'bg-primary text-white border-primary' : 'text-body dark:text-white'"
          >
            {{ page }}
          </button>
          
          <button 
            v-if="hasMorePages"
            @click="changePage(visiblePages[visiblePages.length - 1] + 1)"
            class="flex h-9 w-9 items-center justify-center rounded border border-stroke text-body transition-all hover:bg-primary hover:text-white dark:border-strokedark dark:text-white"
            title="Следующие страницы"
          >
            >>
          </button>
        </div>
      </div>
    </div>

    <!-- Edit Modal -->
    <ClientEditModal
      :show="showEditModal"
      :client="selectedClient"
      @close="showEditModal = false"
      @success="fetchClients"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { Icon } from '@iconify/vue'
import api from '../../api'
import ClientEditModal from '../../components/modals/ClientEditModal.vue'

const clients = ref([])
const loading = ref(false)
const searchQuery = ref('')
const activeTab = ref('all') // 'all', 'offline', 'tma'

// Pagination State
const currentPage = ref(1)
const pageSize = ref(20)
const totalCount = ref(0)
const totalPages = computed(() => Math.ceil(totalCount.value / pageSize.value))

const visiblePages = computed(() => {
    const pages = []
    const start = Math.floor((currentPage.value - 1) / 12) * 12 + 1
    const end = Math.min(start + 11, totalPages.value)
    for (let i = start; i <= end; i++) {
        pages.push(i)
    }
    return pages
})

const hasMorePages = computed(() => {
    if (visiblePages.value.length === 0) return false
    return visiblePages.value[visiblePages.value.length - 1] < totalPages.value
})

const showEditModal = ref(false)
const selectedClient = ref(null)

const fetchClients = async () => {
    try {
        loading.value = true
        const params = {
            search: searchQuery.value || undefined,
            page: currentPage.value,
            page_size: pageSize.value
        }
        if (activeTab.value === 'offline') params.is_tma = 'false'
        if (activeTab.value === 'tma') params.is_tma = 'true'
        
        const response = await api.get('/api/clients/', { params })
        if (response.data.results) {
            clients.value = response.data.results
            totalCount.value = response.data.count
        } else {
            clients.value = response.data
            totalCount.value = response.data.length
        }
    } catch (err) {
        console.error('Failed to fetch clients:', err)
    } finally {
        loading.value = false
    }
}

// Search with simple debounce/logic
let searchTimeout
const handleSearch = () => {
    clearTimeout(searchTimeout)
    searchTimeout = setTimeout(() => {
        currentPage.value = 1
        fetchClients()
    }, 400)
}

const changeTab = (tab) => {
    activeTab.value = tab
    currentPage.value = 1
    fetchClients()
}

const handlePageSizeChange = () => {
    currentPage.value = 1
    fetchClients()
}

const changePage = (page) => {
    currentPage.value = page
    fetchClients()
}

const openEdit = (client) => {
    selectedClient.value = client
    showEditModal.value = true
}

onMounted(() => {
    fetchClients()
})
</script>
