<template>
  <div class="profile-view">
    <div class="page-header">
      <button class="back-btn" @click="$router.push('/owner')">
        <Icon icon="mdi:arrow-left" width="20" />
      </button>
      <div class="page-title header-font">Профиль владельца</div>
    </div>
    
    <div class="card user-info-card">
      <div class="avatar-container">
        <img v-if="auth.user?.photo_url" :src="auth.user.photo_url" class="avatar-img" />
        <div v-else class="avatar-placeholder">👤</div>
      </div>
      <div class="header-name header-font">{{ auth.user?.first_name }} {{ auth.user?.last_name || '' }}</div>
      <div style="color: var(--muted); font-size: 14px">+{{ auth.user?.phone }}</div>
      <div class="role-badge owner-badge">Owner</div>
    </div>

    <!-- Role Switching Actions -->
    <div class="card switch-card">
       <div class="section-title header-font">Управление ролью</div>
       <div class="switch-grid">
          <button class="btn-switch client-mode" @click="switchToClient">
            <Icon icon="mdi:account-convert" width="20" />
            <span>Режим клиента</span>
          </button>
          <button class="btn-switch admin-mode" @click="switchToAdmin">
            <Icon icon="mdi:shield-crown" width="20" />
            <span>Панель админа</span>
          </button>
          <button class="btn-switch master-mode" @click="switchToMaster">
            <Icon icon="mdi:shield-account-variant" width="20" />
            <span>Панель мастера</span>
          </button>
       </div>
    </div>

    <div class="card settings-card">
      <div class="section-title header-font">Настройки</div>
      
      <div class="setting-row">
        <span>{{ $t('profile.phone', 'Номер телефона') }}</span>
        <div class="phone-display">
          <span>+{{ auth.user?.phone }}</span>
        </div>
      </div>

      <div class="setting-row">
        <span>Язык приложения</span>
        <select v-model="selectedLanguage" @change="updateLanguage" class="custom-select">
          <option value="ru">Русский</option>
          <option value="kz">Қазақша</option>
        </select>
      </div>

      <div class="setting-row" style="border-bottom: none">
        <span>Уведомления бота</span>
        <label class="toggle-switch">
          <input type="checkbox" v-model="isBotSubscribed" @change="updateSubscription">
          <span class="slider"></span>
        </label>
      </div>
    </div>

    <!-- Info Card -->
    <div class="card info-card">
       <div class="section-title header-font">Об организации</div>
       <div class="info-row">
          <span>Название:</span>
          <b>{{ auth.organizationName }}</b>
       </div>
       <div class="info-row" v-if="auth.organizationSettings?.instagram_link">
          <span>Instagram:</span>
          <a :href="auth.organizationSettings.instagram_link" target="_blank">Открыть</a>
       </div>
    </div>

    <!-- Auth Actions -->
    <div class="card logout-card" style="margin-top: 16px; border-color: rgba(224, 82, 82, 0.2);">
       <button class="btn-logout" @click="handleLogout">
         <Icon icon="mdi:logout" width="18" />
         <span>Выйти из аккаунта</span>
       </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Icon } from '@iconify/vue'
import { useAuthStore } from '@/stores/auth'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const { locale } = useI18n()
const router = useRouter()

const selectedLanguage = ref('ru')
const isBotSubscribed = ref(true)

onMounted(async () => {
  await auth.fetchCurrentUser()
  selectedLanguage.value = auth.user?.language || 'ru'
  isBotSubscribed.value = auth.user?.is_bot_subscribed ?? true
})

const updateLanguage = async () => {
  locale.value = selectedLanguage.value
  await auth.updateProfile({ language: selectedLanguage.value })
}

const updateSubscription = async () => {
  await auth.updateProfile({ is_bot_subscribed: isBotSubscribed.value })
}

const handleLogout = () => {
  auth.logout()
  router.push('/onboarding/welcome')
}

const switchToAdmin = () => {
  auth.setRoleMode('admin')
  router.push('/admin')
}

const switchToMaster = () => {
  auth.setRoleMode('master')
  router.push('/master')
}

const switchToClient = () => {
  auth.setRoleMode('client')
  router.push('/')
}
</script>

<style scoped>
.profile-view {
  padding: calc(var(--tg-safe-top, 0px) + 20px) 16px 100px;
  transition: padding-top 0.3s ease;
}
.user-info-card {
  text-align: center;
  padding: 30px 16px;
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  display: flex;
  flex-direction: column;
  align-items: center;
}
.avatar-container {
  width: 90px;
  height: 90px;
  border-radius: 50%;
  background: var(--bg-secondary);
  margin-bottom: 16px;
  border: 2px solid var(--gold);
  box-shadow: 0 4px 14px var(--gold-glow);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}
.avatar-img { width: 100%; height: 100%; object-fit: cover; }
.avatar-placeholder { font-size: 40px; }
.header-name { font-size: 22px; font-weight: 700; color: var(--text); }

.role-badge {
  margin-top: 8px;
  font-size: 10px;
  padding: 3px 12px;
  border-radius: 12px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.owner-badge { background: var(--gold); color: #000; }

.switch-card, .settings-card, .info-card {
  margin-top: 16px;
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 20px;
}
.section-title { font-size: 14px; font-weight: 700; margin-bottom: 16px; text-transform: uppercase; color: var(--gold); letter-spacing: 1px; }

.switch-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
}

.btn-switch {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  color: var(--gold);
  padding: 16px;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-switch:active { transform: scale(0.95); }
.btn-switch span { font-size: 12px; font-weight: 700; }
.admin-mode { border-color: #22a060; color: #22a060; }
.master-mode { border-color: var(--gold); color: var(--gold); }
.client-mode { border-color: var(--gold); color: var(--gold); }

.setting-row, .info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 0;
  border-bottom: 1px solid var(--border);
  font-size: 14px;
}
.info-row b { color: var(--gold); }
.info-row a { color: var(--gold); text-decoration: none; font-weight: 600; }

.custom-select {
  background: var(--bg-secondary);
  color: var(--text);
  border: 1px solid var(--border);
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  outline: none;
}

.toggle-switch { position: relative; display: inline-block; width: 44px; height: 24px; }
.toggle-switch input { opacity: 0; width: 0; height: 0; }
.slider {
  position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0;
  background-color: var(--bg-secondary); transition: .3s; border-radius: 24px; border: 1px solid var(--border);
}
.slider:before {
  position: absolute; content: ""; height: 18px; width: 18px; left: 2px; bottom: 2px; background-color: var(--muted); transition: .3s; border-radius: 50%;
}
input:checked + .slider { background-color: var(--gold); border-color: var(--gold); }
input:checked + .slider:before { transform: translateX(20px); background-color: #000; }

.btn-logout {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: transparent;
  border: none;
  color: #e05252;
  font-weight: 700;
  font-size: 14px;
  padding: 12px;
  cursor: pointer;
}
</style>
