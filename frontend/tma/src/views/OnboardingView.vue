<template>
  <div class="page-p">
    <div style="text-align: center; margin-top: 60px">
      <div style="font-size: 48px; margin-bottom: 24px">👋</div>
      <h2>Welcome to the Salon!</h2>
      <p style="color: var(--hint-color); margin-bottom: 32px">
        To streamline your booking experience, we securely use your phone number.
      </p>
      
      <button class="btn-primary" @click="requestContact">
        Share Contact
      </button>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const requestContact = () => {
  if (window.Telegram && window.Telegram.WebApp) {
    const webApp = window.Telegram.WebApp;
    // Mock the SDK requestContact behavior which may not trigger safely on web manually
    webApp.requestContact((shared) => {
      if (shared) {
        // Send request to API to sync phone and continue
        router.push('/services')
      }
    })
    
    // Fallback progression for dev simulation without real Client
    setTimeout(() => {
      router.push('/services')
    }, 1000)
  }
}
</script>
