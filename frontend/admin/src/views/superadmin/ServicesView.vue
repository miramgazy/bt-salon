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
          @click="openComboModal"
          class="inline-flex items-center justify-center gap-2.5 rounded-md bg-warning py-2 px-6 text-center font-medium text-white hover:bg-opacity-90 transition-all shadow-md active:scale-95"
        >
          <Icon icon="mdi:link-variant" width="20" />
          Создать комбо
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

    <!-- Filter Bar Start -->
    <div class="mb-5 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between rounded-sm border border-stroke bg-white py-4 px-4 shadow-default dark:border-strokedark dark:bg-bg-dark-2 sm:px-6 xl:px-7.5">
      <div class="flex flex-1 items-center gap-4">
        <div class="relative flex-1 max-w-sm">
          <span class="absolute top-1/2 left-4 -translate-y-1/2 text-body">
            <Icon icon="mdi:magnify" width="20" />
          </span>
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Поиск по названию..." 
            class="w-full rounded-md border border-stroke bg-gray-50 py-2.5 pl-11 pr-4 outline-none focus:border-primary dark:border-strokedark dark:bg-meta-4 dark:text-white transition-all"
            @input="onFilterChange"
          />
        </div>
        <div class="relative">
          <select 
            v-model="selectedCategoryFilter" 
            class="appearance-none rounded-md border border-stroke bg-gray-50 py-2.5 pl-4 pr-10 outline-none focus:border-primary dark:border-strokedark dark:bg-meta-4 dark:text-white transition-all"
            @change="onFilterChange"
          >
            <option value="">Все категории</option>
            <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
          </select>
          <span class="absolute top-1/2 right-3 -translate-y-1/2 text-body pointer-events-none">
            <Icon icon="mdi:chevron-down" width="18" />
          </span>
        </div>
      </div>
      <div class="flex items-center gap-2 text-sm text-body">
        Всего: <span class="font-bold text-black dark:text-white">{{ totalCount }}</span>
      </div>
    </div>
    <!-- Filter Bar End -->

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
              <td class="border-b border-[#eee] py-5 px-4 pl-9 dark:border-strokedark xl:pl-11" :class="{'bg-warning/5': service.is_combo}">
                <div class="flex items-center gap-2">
                  <h5 class="font-medium text-black dark:text-white">{{ service.name }}</h5>
                  <span v-if="service.is_combo" class="inline-flex items-center gap-1 rounded bg-warning/10 px-2 py-1 text-[10px] font-bold text-warning uppercase">
                    <Icon icon="mdi:link-variant" width="10" /> Комбо
                  </span>
                </div>
                <p v-if="!service.is_combo && !service.is_floating_price" class="text-xs text-body dark:text-bodydark">{{ service.base_price }} ₸ (база)</p>
                <p v-else-if="service.is_floating_price" class="text-xs text-warning font-bold">Плавающая цена</p>
                <p v-else class="text-[10px] text-body dark:text-bodydark">Состоит из {{ service.combo_items?.length || 0 }} услуг</p>
              </td>
              <td class="border-b border-[#eee] py-5 px-4 dark:border-strokedark">
                <p class="text-black dark:text-white">{{ getCategoryName(service.category) }}</p>
              </td>
              <td class="border-b border-[#eee] py-5 px-4 dark:border-strokedark">
                <p class="text-black dark:text-white">{{ service.duration_minutes }} мин</p>
              </td>
              <td class="border-b border-[#eee] py-5 px-4 dark:border-strokedark">
                <p v-if="service.is_floating_price" class="font-bold text-primary">{{ service.price_min }} — {{ service.price_max }} ₸</p>
                <p v-else class="font-bold text-primary">{{ service.total_price }} ₸</p>
              </td>
              <td class="border-b border-[#eee] py-5 px-4 dark:border-strokedark text-center">
                <span 
                  :class="service.is_active ? 'bg-success/10 text-success' : 'bg-danger/10 text-danger'"
                  class="inline-flex rounded-full py-1 px-3 text-sm font-medium"
                >
                  {{ service.is_active ? 'Активна' : 'Неактивна' }}
                </span>
              </td>
              <td class="border-b border-[#eee] py-5 px-4 dark:border-strokedark text-right" :class="{'bg-warning/5': service.is_combo}">
                <div class="flex items-center justify-end gap-3.5">
                  <button @click="copyLink('ser', service.id)" class="hover:text-primary transition-colors" title="Копировать прямую ссылку">
                    <Icon icon="mdi:link" width="18" />
                  </button>
                  <button @click="service.is_combo ? openEditCombo(service) : openEditModal(service)" class="hover:text-primary transition-colors" title="Редактировать">
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

        <!-- Pagination Start -->
        <div class="flex items-center justify-between py-5 px-4 sm:px-6 border-t border-stroke dark:border-strokedark mt-4">
          <div class="flex items-center gap-3">
            <span class="text-sm text-body">Показывать по:</span>
            <select v-model="pageSize" @change="onPageSizeChange" class="rounded border border-stroke bg-transparent py-1 px-2 text-sm outline-none focus:border-primary dark:border-strokedark">
              <option :value="20">20</option>
              <option :value="50">50</option>
              <option :value="100">100</option>
            </select>
          </div>
          
          <div class="flex items-center gap-4">
            <div class="flex items-center gap-2">
              <button 
                @click="prevPage" 
                :disabled="currentPage === 1"
                class="flex h-9 w-9 items-center justify-center rounded border border-stroke hover:bg-gray-50 disabled:opacity-50 dark:border-strokedark dark:hover:bg-meta-4 transition-all"
              >
                <Icon icon="mdi:chevron-left" width="22" />
              </button>
              
              <div class="flex items-center gap-1 px-2">
                <span class="text-sm font-bold text-black dark:text-white">{{ currentPage }}</span>
                <span class="text-sm text-body">из</span>
                <span class="text-sm font-bold text-black dark:text-white">{{ totalPages }}</span>
              </div>

              <button 
                @click="nextPage" 
                :disabled="currentPage >= totalPages"
                class="flex h-9 w-9 items-center justify-center rounded border border-stroke hover:bg-gray-50 disabled:opacity-50 dark:border-strokedark dark:hover:bg-meta-4 transition-all"
              >
                <Icon icon="mdi:chevron-right" width="22" />
              </button>
            </div>
          </div>
        </div>
        <!-- Pagination End -->
      </div>
    </div>
    <!-- Table End -->

    <!-- Main Modal Start -->
    <div v-if="showModal" class="fixed inset-0 z-100 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div class="w-full max-w-142.5 rounded-lg bg-white dark:bg-bg-dark-2 shadow-2xl relative flex flex-col max-h-[90vh] overflow-hidden">
        <!-- Modal Header -->
        <div class="px-8 pt-8 pb-2 shrink-0">
          <button @click="closeModal" class="absolute top-4 right-4 text-body hover:text-primary transition-colors">
              <Icon icon="mdi:close" width="24" />
          </button>
          
          <h3 class="pb-4 text-xl font-bold text-black dark:text-white sm:text-2xl border-b border-stroke dark:border-strokedark mb-2">
            {{ isEditing ? 'Редактировать услугу' : 'Создать новую услугу' }}
          </h3>
        </div>
        
        <form @submit.prevent="saveService" class="flex flex-col flex-1 overflow-hidden">
          <!-- Modal Body (Scrollable) -->
          <div class="flex-1 overflow-y-auto px-8 py-4 custom-scrollbar">
            <!-- Basic Info -->
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

            <div class="mb-4.5 grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="mb-2.5 block text-black dark:text-white font-medium">Категория</label>
                <div class="flex gap-2">
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
                  <button type="button" @click="openCategoryModal" class="flex items-center justify-center rounded bg-gray-200 dark:bg-meta-4 px-4 hover:bg-primary hover:text-white transition-all">
                    <Icon icon="mdi:plus" width="20" />
                  </button>
                </div>
              </div>
              <div>
                <label class="mb-2.5 block text-black dark:text-white font-medium">Длительность (мин)</label>
                <input v-model.number="form.duration_minutes" type="number" class="w-full rounded border-[1.5px] border-stroke bg-gray-50 py-3 px-5 font-medium outline-none transition focus:border-primary dark:border-strokedark dark:bg-bg-dark dark:text-white" required />
              </div>
            </div>
            
            <!-- Floating Price Toggle -->
            <div class="mb-6 flex items-center justify-between p-4 bg-gray-50 dark:bg-meta-4 rounded-xl border border-stroke dark:border-strokedark shadow-sm">
              <div>
                  <label class="font-bold text-black dark:text-white block">Плавающая цена</label>
                  <span class="text-xs text-body">Клиент видит диапазон цен</span>
              </div>
              <label class="relative inline-flex cursor-pointer items-center">
                  <input type="checkbox" v-model="form.is_floating_price" class="sr-only peer" />
                  <div class="peer h-6 w-11 rounded-full bg-gray-200 after:absolute after:top-[2px] after:left-[2px] after:h-5 after:w-5 after:rounded-full after:border after:border-gray-300 after:bg-white after:transition-all after:content-[''] peer-checked:bg-primary peer-checked:after:translate-x-full peer-checked:after:border-white peer-focus:outline-none dark:border-gray-600 dark:bg-gray-700"></div>
              </label>
            </div>

            <!-- New Flow: Total Price First -->
            <div class="mb-6 p-5 bg-primary/5 rounded-2xl border-2 border-primary/20">
              <label class="mb-3 block text-black dark:text-white font-black text-lg uppercase tracking-tight">Стоимость услуги (для клиента)</label>
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

            <!-- Margin Distribution -->
            <div class="mb-4 p-5 bg-gray-50 dark:bg-meta-4 rounded-2xl border border-stroke dark:border-strokedark">
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

            <!-- Prepayment Settings -->
            <div class="mb-6 p-5 bg-warning/5 rounded-2xl border border-warning/30">
              <div class="flex items-center justify-between mb-4">
                <div>
                  <label class="font-black text-black dark:text-white block uppercase tracking-tight">Предоплата</label>
                  <span class="text-[10px] text-body">Обязательна для бронирования</span>
                </div>
                <label class="relative inline-flex cursor-pointer items-center">
                  <input type="checkbox" v-model="form.is_prepayment_required" class="sr-only peer" />
                  <div class="peer h-6 w-11 rounded-full bg-gray-200 after:absolute after:top-[2px] after:left-[2px] after:h-5 after:w-5 after:rounded-full after:border after:border-gray-300 after:bg-white after:transition-all after:content-[''] peer-checked:bg-warning peer-checked:after:translate-x-full peer-checked:after:border-white peer-focus:outline-none dark:border-gray-600 dark:bg-gray-700"></div>
                </label>
              </div>

              <div v-if="form.is_prepayment_required" class="grid grid-cols-2 gap-4 animate-fadeIn">
                <div>
                  <label class="mb-2 block text-[10px] font-bold uppercase text-body">Тип</label>
                  <select v-model="form.prepayment_type" class="w-full rounded-lg border border-stroke bg-white py-2.5 px-4 outline-none dark:border-strokedark dark:bg-bg-dark dark:text-white">
                    <option value="fixed">Фикс (₸)</option>
                    <option value="percent">Процент (%)</option>
                  </select>
                </div>
                <div>
                  <label class="mb-2 block text-[10px] font-bold uppercase text-body">Значение</label>
                  <input v-model.number="form.prepayment_value" type="number" class="w-full rounded-lg border border-stroke bg-white py-2.5 px-4 outline-none dark:border-strokedark dark:bg-bg-dark dark:text-white" />
                </div>
              </div>

              <div v-if="form.is_prepayment_required" class="mt-4 pt-3 border-t border-warning/20 flex justify-between items-center text-sm font-bold text-warning">
                <span>Сумма к оплате:</span>
                <span>{{ calculatedPrepayment }} ₸</span>
              </div>
            </div>
          </div>

          <!-- Modal Footer (Fixed) -->
          <div class="px-8 pb-8 pt-4 shrink-0">
            <div class="flex gap-4">
              <button
                 type="button"
                 @click="closeModal"
                 class="flex-1 justify-center rounded border border-stroke py-3 font-medium text-black hover:bg-gray-100 dark:border-strokedark dark:text-white dark:hover:bg-meta-4 transition-all"
              >
                Отмена
              </button>
              <button
                type="submit"
                class="flex-1 justify-center rounded bg-primary py-3 font-medium text-white hover:bg-opacity-90 transition-all active:scale-95 disabled:opacity-50"
                :disabled="saving"
              >
                {{ saving ? 'Сохранение...' : 'Сохранить' }}
              </button>
            </div>
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
                    <div class="flex items-center gap-2">
                        <button @click="copyLink('cat', cat.id)" class="text-body hover:text-primary transition-colors" title="Копировать прямую ссылку">
                            <Icon icon="mdi:link" width="18" />
                        </button>
                        <button @click="deleteCategory(cat.id)" class="text-body hover:text-danger transition-colors">
                            <Icon icon="mdi:close-circle-outline" width="20" />
                        </button>
                    </div>
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
    <!-- Confirmation Modal -->
    ...
    <!-- Table End -->

    <ComboCreateModal 
      :show="showComboModal"
      :combo="editingCombo"
      :categories="categories"
      :services="allServices"
      @close="closeComboModal"
      @success="fetchData"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../../api'
import { Icon } from '@iconify/vue'
import ComboCreateModal from '../../components/modals/ComboCreateModal.vue'
import { useToast } from '../../composables/useToast'

const toast = useToast()
const org = ref(null)
const services = ref([])
const allServices = ref([])
const categories = ref([])
const loading = ref(true)
const saving = ref(false)

const showModal = ref(false)
const showCategoryModal = ref(false)
const isEditing = ref(false)
const showDeleteConfirm = ref(false)
const serviceToDelete = ref(null)
const newCategoryName = ref('')

const showComboModal = ref(false)
const editingCombo = ref(null)

// Filtering & Pagination State
const searchQuery = ref('')
const selectedCategoryFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const totalCount = ref(0)
const totalPages = computed(() => Math.ceil(totalCount.value / pageSize.value) || 1)

let debounceTimer = null
const onFilterChange = () => {
    if (debounceTimer) clearTimeout(debounceTimer)
    debounceTimer = setTimeout(() => {
        currentPage.value = 1
        fetchData()
    }, 400)
}

const onPageSizeChange = () => {
    currentPage.value = 1
    fetchData()
}

const nextPage = () => {
    if (currentPage.value < totalPages.value) {
        currentPage.value++
        fetchData()
    }
}

const prevPage = () => {
    if (currentPage.value > 1) {
        currentPage.value--
        fetchData()
    }
}

const openComboModal = () => {
  editingCombo.value = null
  showComboModal.value = true
}

const openEditCombo = (service) => {
  editingCombo.value = service
  showComboModal.value = true
}

const closeComboModal = () => {
  showComboModal.value = false
  editingCombo.value = null
}

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
  total_price: 1000,
  base_price: 0,
  margin_type: 'fixed',
  margin_value: 0,
  is_floating_price: false,
  price_min: 0,
  price_max: 0,
  is_prepayment_required: false,
  prepayment_type: 'fixed',
  prepayment_value: 0
})

const calculatedPrepayment = computed(() => {
  if (!form.value.is_prepayment_required) return 0
  const total = form.value.is_floating_price ? form.value.price_min : form.value.total_price
  const val = parseFloat(form.value.prepayment_value) || 0
  if (form.value.prepayment_type === 'fixed') {
    return val.toFixed(0)
  } else {
    return (total * (val / 100)).toFixed(0)
  }
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

const getCategoryName = (catId) => {
  const cat = categories.value.find(c => c.id === catId)
  return cat ? cat.name : 'Без категории'
}

const fetchData = async () => {
  try {
    loading.value = true
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      search: searchQuery.value,
      category: selectedCategoryFilter.value
    }
    const [servRes, catRes, allServRes, orgRes] = await Promise.all([
      api.get('/api/services/', { params }),
      api.get('/api/categories/'),
      api.get('/api/services/', { params: { all: 'true' } }),
      api.get('/api/organization/').catch(err => {
        console.error('Failed to load org settings for deep linking', err)
        return { data: null }
      })
    ])
    
    if (servRes.data.results) {
        services.value = servRes.data.results
        totalCount.value = servRes.data.count
    } else {
        services.value = servRes.data
        totalCount.value = Array.isArray(servRes.data) ? servRes.data.length : 0
    }
    
    allServices.value = allServRes.data.results || allServRes.data || []
    categories.value = catRes.data.results || catRes.data
    if (orgRes && orgRes.data) {
      org.value = orgRes.data
    }
  } catch (error) {
    console.error('Error fetching data:', error)
  } finally {
    loading.value = false
  }
}

const copyLink = async (type, id) => {
  if (!org.value) {
    try {
      const orgRes = await api.get('/api/organization/')
      org.value = orgRes.data
    } catch (err) {
      console.error('Error fetching organization info:', err)
      toast.error('Не удалось загрузить настройки организации для генерации ссылки')
      return
    }
  }
  const baseLink = org.value.tma_link || (org.value.bot_username && org.value.tma_name ? `https://t.me/${org.value.bot_username}/${org.value.tma_name}` : '')
  if (!baseLink) {
    toast.error('Базовая ссылка на Mini App не настроена в профиле организации!')
    return
  }
  const separator = baseLink.includes('?') ? '&' : '?'
  const link = `${baseLink}${separator}startapp=${type}_${id}`
  
  try {
    await navigator.clipboard.writeText(link)
    toast.success('Ссылка скопирована! Теперь вы можете использовать её в Instagram')
  } catch (err) {
    console.error('Failed to copy', err)
    toast.error('Не удалось скопировать ссылку в буфер обмена')
  }
}

const openCreateModal = () => {
  isEditing.value = false
  form.value = {
    id: null,
    name: '',
    category: categories.value.length > 0 ? categories.value[0].id : '',
    duration_minutes: 30,
    total_price: 1000,
    base_price: 0,
    margin_type: 'fixed',
    margin_value: 0,
    is_floating_price: false,
    price_min: 0,
    price_max: 0,
    is_prepayment_required: false,
    prepayment_type: 'fixed',
    prepayment_value: 0
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
  if (form.value.is_floating_price && form.value.price_min > form.value.price_max) {
    alert('Минимальная цена не может быть больше максимальной')
    return
  }
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
