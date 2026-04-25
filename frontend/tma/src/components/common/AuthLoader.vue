<template>
  <div class="auth-loader">
    <div class="loader-content">
      <!-- Kazakh Text Top -->
      <p class="text-kz">Қосымшаға авторизация процесі жүріп жатыр! Күте тұруыңызды сұраймыз.</p>

      <!-- Circular Loader with Countdown -->
      <div class="circle-container">
        <svg class="progress-ring" width="120" height="120">
          <circle
            class="progress-ring__background"
            stroke="rgba(255, 255, 255, 0.1)"
            stroke-width="8"
            fill="transparent"
            r="52"
            cx="60"
            cy="60"
          />
          <circle
            class="progress-ring__circle"
            stroke="var(--gold, #c9a84c)"
            stroke-width="8"
            stroke-linecap="round"
            fill="transparent"
            r="52"
            cx="60"
            cy="60"
            :style="{ strokeDashoffset: strokeDashoffset }"
          />
        </svg>
        <div class="countdown-number">{{ countdown }}</div>
      </div>

      <!-- Russian Text Bottom -->
      <p class="text-ru">Сейчас идет процесс авторизации в приложении! Прошу ожидайте.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'

const countdown = ref(5)
const totalTime = 5
const circumference = 2 * Math.PI * 52

const strokeDashoffset = computed(() => {
  const progress = (totalTime - countdown.value) / totalTime
  return circumference * progress
})

onMounted(() => {
  const timer = setInterval(() => {
    if (countdown.value > 1) {
      countdown.value--
    } else {
      clearInterval(timer)
    }
  }, 1000)
})
</script>

<style scoped>
.auth-loader {
  position: fixed;
  inset: 0;
  z-index: 10000;
  background: radial-gradient(circle at 50% 50%, #1e1e1e 0%, #0a0a0a 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px;
  text-align: center;
}

.loader-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 40px;
  max-width: 340px;
  animation: slideUp 1s cubic-bezier(0.22, 1, 0.36, 1);
}

.text-kz {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
  line-height: 1.4;
  letter-spacing: 0.5px;
  opacity: 0.9;
}

.text-ru {
  font-size: 14px;
  font-weight: 400;
  color: rgba(255, 255, 255, 0.5);
  line-height: 1.6;
  max-width: 260px;
}

.circle-container {
  position: relative;
  width: 140px;
  height: 140px;
  display: flex;
  align-items: center;
  justify-content: center;
  filter: drop-shadow(0 0 15px rgba(201, 168, 76, 0.2));
}

.progress-ring {
  transform: rotate(-90deg);
}

.progress-ring__background {
  stroke: rgba(255, 255, 255, 0.05);
}

.progress-ring__circle {
  transition: stroke-dashoffset 1s linear;
  stroke-dasharray: 326.7;
  filter: drop-shadow(0 0 8px var(--gold, #c9a84c));
}

.countdown-number {
  position: absolute;
  font-size: 48px;
  font-weight: 800;
  color: #fff;
  font-variant-numeric: tabular-nums;
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Fallback for when --gold is not set yet */
:root {
  --gold: #c9a84c;
}
</style>
