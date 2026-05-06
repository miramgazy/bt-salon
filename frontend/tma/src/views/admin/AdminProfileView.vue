<template>
  <div class="profile-view">
    <div class="page-header">
      <button class="back-btn" @click="$router.push('/admin')">
        <Icon icon="mdi:arrow-left" width="20" />
      </button>
      <div class="page-title header-font">{{ $t('admin.nav.profile') }}</div>
    </div>
    
    <div class="card user-info-card">
      <div class="avatar-container">
        <img v-if="auth.user?.photo_url" :src="auth.user.photo_url" class="avatar-img" />
        <div v-else class="avatar-placeholder">👤</div>
      </div>
      <div class="header-name header-font">{{ auth.user?.first_name }} {{ auth.user?.last_name || '' }}</div>
      <div class="clickable-phone" @click="openPhoneActions(auth.user?.phone)">
        {{ formatPhone(auth.user?.phone) }}
      </div>
      <div class="role-badge admin-badge">{{ $t('admin.adminRole') }}</div>
    </div>

    <!-- Role Switching Actions -->
    <div class="card switch-card">
       <div class="section-title header-font">{{ $t('admin.roleManagement') }}</div>
       <div class="switch-grid">
          <button v-if="auth.isMaster" class="btn-switch master-mode" @click="switchToMaster">
            <Icon icon="mdi:shield-account-variant" width="20" />
            <span>{{ $t('master.title') }}</span>
          </button>
          <button class="btn-switch client-mode" @click="switchToClient">
            <Icon icon="mdi:account-convert" width="20" />
            <span>{{ $t('admin.clientMode') }}</span>
          </button>
          <!-- For Admin who is also Owner -->
          <button v-if="auth.isOwner" class="btn-switch owner-mode" @click="switchToOwner">
            <Icon icon="mdi:shield-account" width="20" />
            <span>{{ $t('owner.dashboard_eyebrow') }}</span>
          </button>
       </div>
    </div>

    <div class="card settings-card">
      <div class="section-title header-font">{{ $t('master.schedule') }}</div>
      
      <div class="setting-row">
        <span>{{ $t('language.selectLanguage') }}</span>
        <select v-model="selectedLanguage" @change="updateLanguage" class="custom-select">
          <option value="ru">Русский</option>
          <option value="kz">Қазақша</option>
        </select>
      </div>
    </div>

    <!-- Auth Actions -->
    <div class="card logout-card" style="margin-top: 16px; border-color: rgba(224, 82, 82, 0.2);">
       <button class="btn-logout" @click="handleLogout">
         <Icon icon="mdi:logout" width="18" />
         <span>{{ $t('master.exit') }}</span>
       </button>
    </div>

    <!-- Phone Actions Sheet -->
    <Transition name="fade">
      <div v-if="showPhoneActions" class="phone-modal-overlay" @click="showPhoneActions = false">
        <div class="actions-sheet" @click.stop>
          <div class="sheet-header">
            <div class="sheet-title">{{ formatPhone(selectedPhone) }}</div>
          </div>
          <div class="actions-list">
            <button class="action-item" @click="copyPhone">
              <Icon icon="mdi:content-copy" width="24" />
              <span>{{ $t('profile.copyPhone') }}</span>
            </button>
            <button class="action-item whatsapp" @click="openWhatsApp">
              <Icon icon="mdi:whatsapp" width="24" />
              <span>{{ $t('profile.whatsapp') }}</span>
            </button>
          </div>
          <button class="btn-cancel-sheet" @click="showPhoneActions = false">{{ $t('common.cancel') }}</button>
        </div>
      </div>
    </Transition>

    <!-- Toast -->
    <Transition name="toast">
      <div v-if="toast.show" class="toast-message">
        {{ toast.message }}
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Icon } from '@iconify/vue'
import { useAuthStore } from '@/stores/auth'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const { locale } = useI18n()
const router = useRouter()

const selectedLanguage = ref('ru')
const isBotSubscribed = ref(true)

// Phone actions
const showPhoneActions = ref(false)
const selectedPhone = ref('')
const toast = reactive({ show: false, message: '' })

const formatPhone = (phone) => {
  if (!phone) return ''
  const clean = phone.toString().replace(/\+/g, '')
  return `+${clean}`
}

const openPhoneActions = (phone) => {
  if (!phone) return
  selectedPhone.value = phone
  showPhoneActions.value = true
}

const showToastMessage = (msg) => {
  toast.message = msg
  toast.show = true
  setTimeout(() => { toast.show = false }, 2000)
}

const copyPhone = () => {
  const phone = formatPhone(selectedPhone.value)
  navigator.clipboard.writeText(phone).then(() => {
    showToastMessage(t('common.copied'))
    showPhoneActions.value = false
  })
}

const openWhatsApp = () => {
  const clean = selectedPhone.value.toString().replace(/\D/g, '')
  window.open(`https://wa.me/${clean}`, '_blank')
  showPhoneActions.value = false
}

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

const switchToMaster = () => {
  auth.setRoleMode('master')
  router.push('/master')
}

const switchToClient = () => {
  auth.setRoleMode('client')
  router.push('/')
}

const switchToOwner = () => {
  auth.setRoleMode('owner')
  router.push('/owner')
}
</script>

<style scoped>
.profile-view {
  padding: 20px 16px 100px;
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
  border: 2px solid #22a060;
  box-shadow: 0 4px 14px rgba(34, 160, 96, 0.2);
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
.admin-badge { background: #E6F3EE; color: #22a060; border: 1px solid #22a060; }

.switch-card, .settings-card {
  margin-top: 16px;
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 20px;
}
.section-title { font-size: 14px; font-weight: 700; margin-bottom: 16px; text-transform: uppercase; color: #22a060; letter-spacing: 1px; }

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
  color: var(--text);
  padding: 16px;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-switch:active { transform: scale(0.95); }
.btn-switch span { font-size: 12px; font-weight: 700; }
.master-mode { border-color: var(--gold); color: var(--gold); }
.client-mode { border-color: var(--gold); color: var(--gold); }
.owner-mode { border-color: var(--gold); color: var(--gold); }

.setting-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 0;
  border-bottom: 1px solid var(--border);
  font-size: 14px;
}

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
input:checked + .slider { background-color: #22a060; border-color: #22a060; }
input:checked + .slider:before { transform: translateX(20px); background-color: #fff; }

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

/* Phone Actions Sheet */
.clickable-phone {
  color: var(--gold);
  font-size: 15px;
  font-weight: 600;
  margin-top: 4px;
  cursor: pointer;
  text-decoration: underline;
  text-underline-offset: 4px;
  text-decoration-color: rgba(212, 175, 55, 0.3);
}
.clickable-phone-text {
  cursor: pointer;
  color: var(--gold);
}

.phone-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.6);
  backdrop-filter: blur(4px);
  z-index: 1000;
  display: flex;
  align-items: flex-end;
  justify-content: center;
}

.actions-sheet {
  width: 100%;
  max-width: 500px;
  background: var(--bg);
  border-radius: 24px 24px 0 0;
  padding: 24px 16px 40px;
  animation: slide-up 0.3s ease-out;
}

@keyframes slide-up {
  from { transform: translateY(100%); }
  to { transform: translateY(0); }
}

.sheet-header {
  text-align: center;
  margin-bottom: 20px;
}
.sheet-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--text);
}

.actions-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
}

.action-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 16px;
  color: var(--text);
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  width: 100%;
}
.action-item:active {
  transform: scale(0.98);
  background: var(--border);
}
.action-item.whatsapp {
  color: #25D366;
  border-color: rgba(37, 211, 102, 0.3);
}

.btn-cancel-sheet {
  width: 100%;
  padding: 16px;
  background: transparent;
  border: 1px solid var(--border);
  border-radius: 16px;
  font-size: 16px;
  font-weight: 700;
  color: var(--muted);
  cursor: pointer;
}

/* Toast */
.toast-message {
  position: fixed;
  bottom: 100px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0,0,0,0.8);
  color: #fff;
  padding: 12px 24px;
  border-radius: 50px;
  font-size: 14px;
  font-weight: 600;
  z-index: 2000;
  box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}

.toast-enter-active, .toast-leave-active { transition: all 0.3s ease; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translate(-50%, 20px); }

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
