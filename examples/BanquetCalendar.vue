<template>
  <div class="calendar-container">
    <ScheduleXCalendar v-if="calendarApp" :calendar-app="calendarApp" />
  </div>
</template>

<script>
import { ScheduleXCalendar } from '@schedule-x/vue'
import { createCalendar, createViewMonthGrid, createViewWeek } from '@schedule-x/calendar'
import '@schedule-x/theme-default/dist/index.css'
import { shallowRef, onMounted, watch } from 'vue'

export default {
  name: 'BanquetCalendar',
  components: {
    ScheduleXCalendar
  },
  props: {
    bookings: {
      type: Array,
      default: () => []
    }
  },
  emits: ['booking-click', 'date-select'],
  setup(props, { emit }) {
    const calendarApp = shallowRef(null)

    const transformBookingsToEvents = (bookings) => {
      return bookings.map(booking => {
        try {
          // Создаем дату начала события
          const [year, month, day] = booking.date.split('-')
          const [hours, minutes] = booking.time.split(':')
          
          // Форматируем даты в формат ISO string (YYYY-MM-DD HH:mm)
          const startStr = `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')} ${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}`
          
          // Создаем дату окончания события
          const startDate = new Date(year, month - 1, day, hours, minutes)
          const endDate = new Date(startDate)
          endDate.setHours(endDate.getHours() + booking.duration_hours)
          
          const endStr = `${endDate.getFullYear()}-${String(endDate.getMonth() + 1).padStart(2, '0')}-${String(endDate.getDate()).padStart(2, '0')} ${String(endDate.getHours()).padStart(2, '0')}:${String(endDate.getMinutes()).padStart(2, '0')}`

          return {
            id: booking.id,
            title: '',
            start: startStr,
            end: endStr,
            color: booking.event_status === 'confirmed' ? '#4CAF50' : '#FFC107',
            booking: booking
          }
        } catch (error) {
          console.error('Error transforming booking:', booking, error)
          return null
        }
      }).filter(Boolean)
    }

    const initializeCalendar = () => {
      calendarApp.value = createCalendar({
        defaultView: 'month',
        timeFormat24: true,
        views: [
          createViewMonthGrid({
            name: 'month',
            label: 'Месяц',
            eventMapping: {
              title: 'title',
              start: 'start',
              end: 'end',
              display: {
                showTime: false
              }
            },
            hideEventTime: true
          }),
          createViewWeek({
            name: 'week',
            label: 'Неделя',
            eventMapping: {
              title: 'title',
              start: 'start',
              end: 'end',
              display: {
                showTime: false
              }
            },
            hideEventTime: true
          })
        ],
        events: transformBookingsToEvents(props.bookings),
        callbacks: {
          onEventClick: (event) => {
            emit('booking-click', event.booking)
          },
          onDateClick: (dateInfo) => {
            emit('date-select', dateInfo.date)
          }
        },
        monthGrid: {
          weekDayStart: 1
        },
        dayBoundaries: {
          start: '08:00',
          end: '23:00'
        },
        i18n: {
          locale: 'ru',
          monthNames: [
            'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
            'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
          ],
          weekDays: ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'],
          today: 'Сегодня',
          allDay: 'Весь день',
          noEvents: 'Нет событий',
          loading: 'Загрузка...',
          moreEvents: '{count} еще...',
          viewNames: {
            month: 'Месяц',
            week: 'Неделя'
          }
        }
      })
    }

    // Инициализируем календарь после монтирования компонента
    onMounted(() => {
      initializeCalendar()
    })

    // Следим за изменениями в props.bookings
    watch(() => props.bookings, () => {
      if (calendarApp.value) {
        calendarApp.value.setEvents(transformBookingsToEvents(props.bookings))
      }
    }, { deep: true })

    return {
      calendarApp
    }
  }
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

.calendar-container {
  width: 100%;
  height: 100%;
  min-height: 800px;
  padding: 1rem;
  font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
}

.calendar-wrapper {
  width: 100%;
  height: 100%;
  min-height: 800px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

:deep(.sx__event-preview) {
  border-radius: 4px;
  padding: 4px;
  min-height: 20px;
  cursor: pointer;
  display: block !important;
}

:deep(.sx__time-grid-event) {
  border-radius: 4px;
  cursor: pointer;
  min-height: 20px;
  display: block !important;
}

:deep(.sx__month-grid-event) {
  min-height: 16px;
  cursor: pointer;
  display: block !important;
}

:deep(.sx__event-time),
:deep(.sx__event-preview-time) {
  display: none !important;
}

:deep(.sx__time-grid-event-content),
:deep(.sx__month-grid-event-content) {
  padding: 2px !important;
}

:deep(.sx__calendar) {
  --sx-font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  --sx-color-primary: #4CAF50;
  --sx-color-primary-hover: #45a049;
}

:deep(.sx__modal) {
  font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
}

:deep(.sx__modal-close-button) {
  font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif !important;
}

:deep(.sx__modal-close-button)::before {
  content: '×' !important;
  font-size: 24px;
  line-height: 1;
}

/* Мобильная оптимизация */
@media (max-width: 768px) {
  .calendar-container {
    padding: 0.5rem;
    min-height: 600px;
  }

  :deep(.sx__calendar) {
    /* Уменьшаем отступы на мобильных устройствах */
    --sx-spacing-1: 0.25rem;
    --sx-spacing-2: 0.5rem;
  }

  :deep(.sx__month-grid) {
    /* Оптимизация сетки месяца для мобильных устройств */
    min-width: 100%;
    overflow-x: hidden;
  }

  :deep(.sx__month-grid-cell) {
    /* Уменьшаем размер ячеек для лучшего отображения на мобильных */
    min-height: 80px;
  }

  :deep(.sx__month-grid-event) {
    /* Уменьшаем размер текста событий */
    font-size: 0.8rem;
    line-height: 1.2;
  }

  :deep(.sx__header) {
    /* Оптимизация заголовка для мобильных */
    flex-wrap: wrap;
    gap: 0.5rem;
  }
}
</style> 