/**
 * Telegram WebApp service wrapper
 */

export function isInTelegram() {
  return !!(window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.initData)
}

export function getWebApp() {
  return window.Telegram?.WebApp || null
}

export function openTelegramLink(url) {
  const webApp = getWebApp()
  if (webApp && webApp.openTelegramLink) {
    webApp.openTelegramLink(url)
  } else {
    window.open(url, '_blank')
  }
}

export default {
  isInTelegram,
  getWebApp,
  openTelegramLink
}
