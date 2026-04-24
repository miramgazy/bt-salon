<template>
  <div class="master-page">
    <!-- Header -->
    <div class="master-header">
      <div class="master-avatar">
        <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M5.121 17.804A13.937 13.937 0 0112 16c2.5 0 4.847.655 6.879 1.804M15 10a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
      </div>
      <h1 class="master-greeting">{{ t('master.welcome') }}</h1>
      <p class="master-name">{{ auth.user?.first_name || '' }} {{ auth.user?.last_name || '' }}</p>
      <span class="master-badge">{{ t('master.title') }}</span>
    </div>

    <!-- Quick actions -->
    <div class="master-cards">
      <div class="action-card">
        <div class="action-icon action-icon--blue">
          <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
          </svg>
        </div>
        <div>
          <p class="action-title">{{ t('master.myAppointments') }}</p>
          <p class="action-hint">{{ t('appointments.title') }}</p>
        </div>
      </div>

      <div class="action-card">
        <div class="action-icon action-icon--purple">
          <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
        </div>
        <div>
          <p class="action-title">{{ t('master.schedule') }}</p>
          <p class="action-hint">{{ auth.organizationName }}</p>
        </div>
      </div>
    </div>

    <p class="master-desc">{{ t('master.description') }}</p>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'

const { t } = useI18n()
const auth = useAuthStore()
</script>

<style scoped>
.master-page {
  min-height: 100vh;
  background: linear-gradient(160deg, #1e1b4b 0%, #3730a3 50%, #667eea 100%);
  padding: 32px 16px 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.master-header {
  text-align: center;
  margin-bottom: 32px;
}
.master-avatar {
  width: 88px;
  height: 88px;
  background: rgba(255,255,255,0.15);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
  border: 3px solid rgba(255,255,255,0.3);
}
.master-avatar svg { width: 44px; height: 44px; color: #fff; }
.master-greeting {
  font-size: 26px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 4px;
}
.master-name {
  font-size: 15px;
  color: rgba(255,255,255,0.75);
  margin-bottom: 12px;
}
.master-badge {
  display: inline-block;
  background: rgba(255,255,255,0.2);
  color: #fff;
  border: 1px solid rgba(255,255,255,0.3);
  border-radius: 20px;
  padding: 4px 14px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.5px;
}
.master-cards {
  width: 100%;
  max-width: 420px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 24px;
}
.action-card {
  background: rgba(255,255,255,0.95);
  border-radius: 16px;
  padding: 16px 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
  cursor: pointer;
  transition: transform 0.2s;
}
.action-card:active { transform: scale(0.97); }
.action-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.action-icon--blue { background: #dbeafe; }
.action-icon--blue svg { color: #3b82f6; }
.action-icon--purple { background: #ede9fe; }
.action-icon--purple svg { color: #7c3aed; }
.action-icon svg { width: 24px; height: 24px; }
.action-title { font-size: 15px; font-weight: 600; color: #111827; margin-bottom: 2px; }
.action-hint  { font-size: 12px; color: #6b7280; }
.master-desc {
  max-width: 320px;
  text-align: center;
  font-size: 13px;
  color: rgba(255,255,255,0.6);
  line-height: 1.5;
}
</style>
