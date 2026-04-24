<template>
  <div class="flex flex-wrap h-screen items-center justify-center bg-gray-50 dark:bg-bg-dark">
    <div class="w-full max-w-125 rounded-sm border border-stroke bg-white shadow-default dark:border-strokedark dark:bg-bg-dark-2">
      <div class="flex flex-wrap items-center">
        <div class="w-full border-stroke dark:border-strokedark xl:w-full xl:border-l-2">
          <div class="w-full p-8 sm:p-12.5 xl:p-17.5">
            <span class="mb-1.5 block font-medium text-black dark:text-white uppercase tracking-widest text-xs">
              Salon Management System
            </span>
            <h2 class="mb-9 text-2xl font-bold text-black dark:text-white sm:text-title-xl2">
              BT Salon Admin
            </h2>

            <form @submit.prevent="handleLogin">
              <div v-if="errorMsg" class="mb-4 rounded bg-danger/10 p-3 text-sm text-danger text-center">
                {{ errorMsg }}
              </div>

              <div class="mb-4">
                <label class="mb-2.5 block font-medium text-black dark:text-white">Пользователь</label>
                <div class="relative">
                  <input
                    v-model="username"
                    type="text"
                    placeholder="Введите имя пользователя"
                    class="w-full rounded-lg border border-stroke bg-transparent py-4 pl-6 pr-10 outline-none focus:border-primary focus-visible:shadow-none dark:border-form-strokedark dark:bg-form-input dark:focus:border-primary"
                    required
                  />
                  <span class="absolute right-4 top-4 text-bodydark2">
                    <Icon icon="mdi:account-outline" width="22" />
                  </span>
                </div>
              </div>

              <div class="mb-6">
                <label class="mb-2.5 block font-medium text-black dark:text-white">Пароль</label>
                <div class="relative">
                  <input
                    v-model="password"
                    type="password"
                    placeholder="••••••••"
                    class="w-full rounded-lg border border-stroke bg-transparent py-4 pl-6 pr-10 outline-none focus:border-primary focus-visible:shadow-none dark:border-form-strokedark dark:bg-form-input dark:focus:border-primary"
                    required
                  />
                  <span class="absolute right-4 top-4 text-bodydark2">
                    <Icon icon="mdi:lock-outline" width="22" />
                  </span>
                </div>
              </div>

              <div class="mb-5">
                <button
                  type="submit"
                  class="w-full cursor-pointer rounded-lg border border-primary bg-primary p-4 text-white transition hover:bg-opacity-90 active:scale-95"
                >
                  Войти в систему
                </button>
              </div>

              <div class="mt-6 text-center">
                <p class="text-bodydark2">
                  Забыли пароль? 
                  <a href="#" class="text-primary hover:underline">Сбросить</a>
                </p>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { Icon } from '@iconify/vue'

const username = ref('')
const password = ref('')
const errorMsg = ref('')
const router = useRouter()

const handleLogin = async () => {
    try {
        errorMsg.value = ''
        const response = await axios.post('/api/accounts/token/', {
            username: username.value,
            password: password.value
        })
        
        if (response.data.access) {
            localStorage.setItem('access_token', response.data.access)
        }
        if (response.data.refresh) {
            localStorage.setItem('refresh_token', response.data.refresh)
        }
        
        router.push('/admin/calendar')
    } catch (error) {
        console.error('Login failed:', error)
        errorMsg.value = 'Неверное имя пользователя или пароль'
    }
}
</script>

<style scoped>
.sm\:text-title-xl2 {
  font-size: 2.125rem;
  line-height: 2.625rem;
}
.max-w-125 {
  max-width: 31.25rem;
}
</style>
