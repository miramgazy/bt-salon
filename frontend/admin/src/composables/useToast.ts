import { ref, reactive } from 'vue'

export interface Toast {
  id: number
  message: string
  type: 'success' | 'error' | 'warning' | 'info'
  duration?: number
}

const toasts = ref<Toast[]>([])
let counter = 0

export function useToast() {
  const add = (message: string, type: Toast['type'] = 'info', duration = 3000) => {
    const id = ++counter
    const toast: Toast = { id, message, type, duration }
    toasts.value.push(toast)

    if (duration > 0) {
      setTimeout(() => {
        remove(id)
      }, duration)
    }
  }

  const remove = (id: number) => {
    const index = toasts.value.findIndex(t => t.id === id)
    if (index > -1) {
      toasts.value.splice(index, 1)
    }
  }

  const success = (msg: string) => add(msg, 'success')
  const error = (msg: string) => add(msg, 'error')
  const warning = (msg: string) => add(msg, 'warning')
  const info = (msg: string) => add(msg, 'info')

  return {
    toasts,
    add,
    remove,
    success,
    error,
    warning,
    info
  }
}
