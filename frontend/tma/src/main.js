import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import i18n from './i18n/index'
import VueApexCharts from "vue3-apexcharts"
import './styles/index.css'

if (window.Telegram && window.Telegram.WebApp) {
  window.Telegram.WebApp.ready()
  window.Telegram.WebApp.expand()
}

const app = createApp(App)

// Diagnostic error handling to catch and display any runtime crash on screen
app.config.errorHandler = (err, instance, info) => {
  console.error('Global Vue Error:', err)
  alert(`Vue Render Error: ${err.message}\nInfo: ${info}\nStack: ${err.stack || ''}`)
}

window.addEventListener('error', (event) => {
  alert(`Window Error: ${event.message}\nSource: ${event.filename}:${event.lineno}`);
})

window.addEventListener('unhandledrejection', (event) => {
  alert(`Unhandled Promise Rejection: ${event.reason}`);
})

app.use(createPinia())
app.use(router)
app.use(i18n)
app.use(VueApexCharts)

app.mount('#app')
