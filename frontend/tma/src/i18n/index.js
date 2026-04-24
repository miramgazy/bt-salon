import { createI18n } from 'vue-i18n'
import ru from '../locales/ru.json'
import kz from '../locales/kz.json'

const LOCALE_KEY = 'tma_locale'

export function getStoredLocale() {
  return localStorage.getItem(LOCALE_KEY) || null
}

export function setStoredLocale(code) {
  localStorage.setItem(LOCALE_KEY, code)
}

const i18n = createI18n({
  legacy: false,
  locale: getStoredLocale() || 'ru',
  fallbackLocale: 'ru',
  messages: {
    ru,
    kz
  }
})

export default i18n
