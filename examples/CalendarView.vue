<template>
    <div class="calendar-container">
        <div v-if="loading" class="loading">
            <div class="spinner"></div>
            <p>Загрузка бронирований...</p>
        </div>
        <div v-else-if="error" class="error">{{ error }}</div>

        <div v-else>
            <div class="calendar-header">
                <div class="header-content">
                    <h2 class="calendar-title">Календарь бронирований</h2>
                    <div v-if="isSuperAdmin" class="cafe-selector">
                        <select v-model="selectedCafeId" class="cafe-select" @change="fetchBookings">
                            <option :value="null">Все заведения</option>
                            <option v-for="cafe in cafes" :key="cafe.id" :value="cafe.id">
                                {{ cafe.name }}
                            </option>
                        </select>
                    </div>
                </div>
                <div v-if="isAdmin || isSuperAdmin" class="show-cancelled-wrapper">
                    <label class="show-cancelled-label">
                        <input
                            type="checkbox"
                            v-model="showCancelled"
                            class="show-cancelled-checkbox"
                        />
                        показать отмененные
                    </label>
                </div>
            </div>

            <div class="calendar-grid">
                <div class="calendar-month">
                    <div class="month-navigation">
                        <button class="nav-button" @click="previousMonth">
                            <i class="fas fa-chevron-left"></i>
                        </button>
                        <div class="date-selector">
                            <select v-model="selectedMonth" class="month-select" @change="onDateChange">
                                <option v-for="(month, index) in months" 
                                        :key="index" 
                                        :value="index">
                                    {{ month }}
                                </option>
                            </select>
                            <select v-model="selectedYear" class="year-select" @change="onDateChange">
                                <option v-for="year in yearRange" 
                                        :key="year" 
                                        :value="year">
                                    {{ year }}
                                </option>
                            </select>
                        </div>
                        <button class="nav-button" @click="nextMonth">
                            <i class="fas fa-chevron-right"></i>
                        </button>
                    </div>
                    <div class="calendar-weekdays">
                        <div v-for="day in weekDays" :key="day" class="weekday">{{ day }}</div>
                    </div>
                    <div class="calendar-days">
                        <div
                            v-for="day in calendarDays"
                            :key="day.date"
                            class="calendar-day"
                            :class="{
                                'other-month': day.isOtherMonth,
                                'today': day.isToday,
                                'has-events': day.events.length > 0,
                                'weekend': day.isWeekend
                            }"
                            @click="onDayClick(day)"
                            @dblclick="onDayDoubleClick(day)">
                            <div class="day-content-wrapper">
                                <div class="day-header">
                                    <span class="day-number">{{ day.dayNumber }}</span>
                                    <span v-if="day.events.length > 0" class="event-count">
                                        {{ day.events.length }}
                                    </span>
                                </div>
                                <div class="events-container">
                                    <div
                                        v-for="event in day.events"
                                        :key="event.id"
                                        class="event-dot"
                                        :class="[event.status, { 'mobile-view': isMobileView }]"
                                        @click.stop="showEventDetails(event, day)">
                                        <span class="event-time">{{ formatTime(event.time) }}</span>
                                        <span class="event-title" v-if="!isMobileView">{{ event.title }}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Модальное окно для просмотра событий -->
            <div v-if="showEventsModal" class="modal">
                <div class="modal-content events-modal">
                    <div class="modal-header">
                        <h3>События на {{ formatSelectedDate }}</h3>
                        <button class="close-button" @click="closeModal">&times;</button>
                    </div>
                    <div class="events-list">
                        <div v-if="selectedDayEvents.length === 0" class="no-events">
                            Нет событий на эту дату
                        </div>
                        <div v-else v-for="event in selectedDayEvents" 
                             :key="event.id" 
                             class="event-item"
                             :class="event.event_status">
                            <div class="event-header">
                                <span class="event-time">{{ formatTime(event.time) }} - {{ calculateEndTime(event) }}</span>
                                <span :class="['event-status', event.event_status]">
                                    <i v-if="event.event_status === 'confirmed'" class="fas fa-check-circle"></i>
                                    <i v-else class="fas fa-hourglass-half"></i>
                                </span>
                            </div>
                            <div class="event-details">
                                <p><strong>Мероприятие:</strong> {{ event.event_name || 'Без названия' }}</p>
                                <p><strong>Клиент:</strong> {{ event.client_name }}</p>
                                <p>
                                    <strong>Телефон:</strong>
                                    <PhoneActions 
                                        v-if="event.client_phone" 
                                        :phone-number="event.client_phone"
                                        :active="openedPhoneId === event.id"
                                        @open="handlePhoneOpen(event.id)"
                                        @close="handlePhoneOpen(null)"
                                        @copied="showCopiedMessage"
                                        @error="handleError"
                                    />
                                    <span v-else>Нет данных</span>
                                </p>
                                <p><strong>Количество гостей:</strong> {{ event.number_of_people }} чел.</p>
                                <p><strong>Цена за гостя:</strong> <span style="text-align:right">{{ formatPrice(event.price_per_visitor) }}</span></p>
                                <p><strong>Предоплата:</strong> <span style="text-align:right">{{ formatPrice(event.prepayment) }}</span></p>
                                <p><strong>Сумма без скидки:</strong> <span style="text-align:right">{{ formatPrice(event.total_price) }}</span></p>
                                <p><strong>Тип скидки:</strong> {{ event.discount_type === 'percent' ? 'в %' : 'Фиксированная' }}</p>
                                <p><strong>Скидка:</strong> <span style="text-align:right">{{ formatDiscount(event.discount) }}</span></p>
                                <p><strong>Сумма скидки:</strong> <span style="text-align:right">{{ Number(event.discount) === 0 ? 0 : formatPrice((event.total_price || 0) - (event.final_price || 0)) }}</span></p>
                                <p><strong>Сумма со скидкой:</strong> <span style="text-align:right">{{ formatPrice(event.final_price) }}</span></p>
                                <p><strong>Остаток суммы к оплате:</strong> <span style="text-align:right">{{ formatPrice(event.remaining_payment) }}</span></p>
                                <div v-if="event.client_comment" class="comment-section">
                                    <strong>Комментарий:</strong> 
                                    <div class="event-comment">{{ event.client_comment }}</div>
                                    <div class="comment-meta">
                                        <span class="comment-author">автор: {{ event.assistant_name || 'Не указан' }}</span>
                                        <span class="comment-date">изменено: {{ formatDateTime(event.modified_at) }}</span>
                                    </div>
                                </div>
                            </div>
                            <div class="event-actions" v-if="isAdmin || isAssistant">
                                <button v-if="isAdmin && event.event_status !== 'cancelled'" 
                                        class="btn btn-edit" 
                                        @click="editBooking(event)">
                                    <i class="fas fa-edit"></i> Редактировать
                                </button>
                                <button v-if="event.event_status === 'not_confirmed' && (isAdmin || isAssistant) && event.event_status !== 'cancelled'" 
                                        class="btn btn-confirm" 
                                        @click="showConfirmationForm(event)">
                                    <i class="fas fa-check"></i> Подтвердить
                                </button>
                                <button v-if="isAdmin && event.event_status !== 'cancelled'" 
                                        class="btn btn-cancel" 
                                        @click.stop="showCancelConfirmation(event.id)">
                                    <i class="fas fa-ban"></i> Отменить
                                </button>
                                <button v-if="event.event_status !== 'cancelled'" class="btn btn-prepayment" @click="openPrepaymentModal(event)">
                                    <i class="fas fa-money-bill-wave"></i> Предоплата
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Модальное окно для создания бронирования -->
            <div v-if="showCreateModal" class="modal">
                <div class="modal-content">
                    <div class="modal-header">
                        <h3>Новое бронирование на {{ formatSelectedDate }}</h3>
                        <button class="close-button" @click="closeModal">&times;</button>
                    </div>
                    <BookingForm
                        :initial-date="selectedDate"
                        :selected-time="selectedTime"
                        @submit-success="onBookingCreated"
                        @close="closeModal"
                    />
                </div>
            </div>

            <!-- Модальное окно для редактирования -->
            <div v-if="showEditModal" class="modal">
                <div class="modal-content">
                    <div class="modal-header">
                        <h3>Редактирование бронирования</h3>
                        <button class="close-button" @click="closeModal">&times;</button>
                    </div>
                    <BookingForm
                        :initial-date="selectedDate"
                        :selected-time="selectedTime"
                        :editing-booking="editingBooking"
                        :is-editing="true"
                        @submit-success="onBookingUpdated"
                        @close="closeModal"
                    />
                </div>
            </div>

            <!-- Модальное окно подтверждения отмены -->
            <BookingCancellation
                :show="showCancelConfirmModal"
                :booking-id="bookingToCancel"
                @close="closeCancelConfirmation"
                @booking-cancelled="onBookingCancelled"
                @error="handleError"
            />

            <!-- Добавляем компонент подтверждения -->
            <BookingConfirmation
                :confirmation-booking="confirmationBooking"
                :show-delete-modal="showDeleteModal"
                :booking-to-delete="bookingToDelete"
                :user-role="userRole"
                @close-confirmation="closeConfirmationForm"
                @close-delete="cancelDelete"
                @booking-confirmed="onBookingConfirmed"
                @booking-deleted="onBookingDeleted"
                @booking-updated="fetchBookings"
                @error="handleError"
            />

            <!-- Success message notification -->
            <div v-if="showSuccessMessage" class="success-message">
                {{ successMessage }}
            </div>
        </div>

        <!-- Подтверждение удаления -->
        <div v-if="showDeleteConfirm" class="modal">
            <div class="modal-content delete-confirm">
                <h3>Подтверждение удаления</h3>
                <p>Вы действительно хотите удалить это бронирование?</p>
                <div class="delete-actions">
                    <button class="btn btn-cancel" @click="cancelDelete">Отмена</button>
                    <button class="btn btn-confirm-delete" @click="confirmDelete">Удалить</button>
                </div>
            </div>
        </div>
        <PrepaymentModal
            :show="showPrepaymentModal"
            :booking="prepaymentBooking"
            @close="closePrepaymentModal"
            @success="onPrepaymentSuccess"
        />
    </div>
</template>

<script>
import BookingForm from '../components/BookingForm.vue'
import axios from '../plugins/axios'
import { format, parseISO, addMonths, subMonths, startOfMonth, endOfMonth, eachDayOfInterval, isToday, isSameMonth, getDay } from 'date-fns'
import { ru } from 'date-fns/locale'
import { addDays, subDays } from 'date-fns'
import BookingConfirmation from '../components/BookingConfirmation.vue'
import BookingCancellation from '../components/BookingCancellation.vue'
import PhoneActions from '../components/PhoneActions.vue'
import PrepaymentModal from '../components/PrepaymentModal.vue'

export default {
    name: 'CalendarView',
    components: {
        BookingForm,
        BookingConfirmation,
        BookingCancellation,
        PhoneActions,
        PrepaymentModal
    },
    data() {
        const currentYear = new Date().getFullYear();
        return {
            bookings: [],
            loading: true,
            error: null,
            showModal: false,
            selectedEvent: null,
            selectedDate: new Date(),
            currentDate: new Date(),
            selectedTime: null,
            cafes: [],
            selectedCafeId: null,
            isAdmin: false,
            isAssistant: false,
            isSuperAdmin: false,
            showDeleteConfirm: false,
            bookingToDelete: null,
            weekDays: ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'],
            isMobileView: false,
            mobileBreakpoint: 768,
            selectedMonth: new Date().getMonth(),
            selectedYear: currentYear,
            showCancelled: false,
            months: [
                'Январь', 'Февраль', 'Март', 'Апрель', 
                'Май', 'Июнь', 'Июль', 'Август',
                'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
            ],
            yearRange: Array.from(
                { length: 3 }, 
                (_, i) => currentYear + i
            ),
            showEventsModal: false,
            showCreateModal: false,
            selectedDayEvents: [],
            clickTimeout: null,
            showEditModal: false,
            editingBooking: null,
            showCancelConfirmModal: false,
            bookingToCancel: null,
            confirmationBooking: null,
            showDeleteModal: false,
            userRole: null,
            cancelComment: '',
            showCommentError: false,
            successMessage: '',
            showSuccessMessage: false,
            showPrepaymentModal: false,
            prepaymentBooking: null,
            openedPhoneId: null,
        }
    },
    computed: {
        currentMonthName() {
            return format(this.currentDate, 'LLLL yyyy', { locale: ru })
        },
        currentCafeName() {
            if (!this.selectedCafeId) return 'Все заведения';
            const selectedCafe = this.cafes.find(cafe => cafe.id === this.selectedCafeId);
            return selectedCafe ? selectedCafe.name : '';
        },
        calendarDays() {
            const start = startOfMonth(this.currentDate)
            const end = endOfMonth(this.currentDate)
            
            // Получаем первый день месяца
            let firstDayOfMonth = startOfMonth(this.currentDate)
            
            // Корректируем начальную дату, чтобы неделя начиналась с понедельника
            let startDate = firstDayOfMonth
            const dayOfWeek = getDay(firstDayOfMonth)
            if (dayOfWeek !== 1) { // Если не понедельник
                startDate = subDays(firstDayOfMonth, dayOfWeek === 0 ? 6 : dayOfWeek - 1)
            }
            
            // Корректируем конечную дату
            let endDate = end
            const lastDayOfWeek = getDay(end)
            if (lastDayOfWeek !== 0) {
                endDate = addDays(end, 7 - lastDayOfWeek)
            }

            const days = eachDayOfInterval({ start: startDate, end: endDate })

            return days.map(date => {
                const dayEvents = this.bookings.filter(booking => {
                    if (!this.showCancelled && booking.event_status === 'cancelled') {
                        return false;
                    }
                    const bookingDate = parseISO(`${booking.date}T${booking.time}`)
                    return format(bookingDate, 'yyyy-MM-dd') === format(date, 'yyyy-MM-dd')
                })

                const dayOfWeek = getDay(date);
                const isWeekend = dayOfWeek === 0 || dayOfWeek === 6; // 0 - воскресенье, 6 - суббота

                return {
                    date: date,
                    dayNumber: date.getDate(),
                    isToday: isToday(date),
                    isOtherMonth: !isSameMonth(date, this.currentDate),
                    isWeekend: isWeekend,
                    events: dayEvents.map(booking => ({
                        id: booking.id,
                        title: booking.event_name || 'Без названия',
                        time: booking.time,
                        status: booking.event_status,
                        ...booking
                    }))
                }
            })
        },
        modalTitle() {
            return this.selectedEvent 
                ? `Бронирование: ${this.selectedEvent.event_name || 'Без названия'}` 
                : `Новое бронирование на ${format(this.selectedDate, 'd MMMM yyyy', { locale: ru })}`
        },
        formatSelectedDate() {
            return format(this.selectedDate, 'd MMMM yyyy', { locale: ru })
        }
    },
    methods: {
        async fetchUserRole() {
            try {
                const token = localStorage.getItem('access')
                const response = await axios.get('/api/user/', {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                })
                this.isAdmin = response.data.role === 'admin'
                this.isAssistant = response.data.role === 'assistant'
                this.isSuperAdmin = response.data.is_superuser

                if (this.isSuperAdmin) {
                    await this.fetchCafes()
                }
            } catch (error) {
                console.error('Error fetching user role:', error)
                this.error = 'Ошибка при получении роли пользователя'
            }
        },
        async fetchCafes() {
            try {
                const response = await axios.get('/api/cafes/')
                this.cafes = response.data
            } catch (error) {
                console.error('Error fetching cafes:', error)
            }
        },
        async fetchBookings() {
            try {
                this.loading = true
                this.error = null
                let url = '/api/bookings/'
                if (this.selectedCafeId) {
                    url += `?cafe=${this.selectedCafeId}`
                }
                const response = await axios.get(url)
                this.bookings = response.data
            } catch (error) {
                if (error.response?.status === 404) {
                    this.error = 'Сервис бронирований недоступен'
                } else if (error.response?.status === 401) {
                    this.error = 'Требуется авторизация'
                } else {
                    this.error = 'Ошибка при загрузке бронирований'
                }
                console.error('Error fetching bookings:', error)
            } finally {
                this.loading = false
            }
        },
        formatTime(time) {
            if (!time) return ''
            return time.slice(0, 5)
        },
        calculateEndTime(booking) {
            if (!booking.time || !booking.duration_hours) return ''
            const [hours, minutes] = booking.time.split(':').map(Number)
            const date = new Date(2000, 0, 1, hours, minutes)
            date.setHours(date.getHours() + booking.duration_hours)
            return `${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
        },
        formatPrice(val) {
          return `${Math.round(Number(val)).toLocaleString('ru-RU', { maximumFractionDigits: 0 })} ₸`;
        },
        formatDiscount(val) {
            return `${Math.round(Number(val)).toLocaleString('ru-RU', { maximumFractionDigits: 0 })}`;
        },
        onDayClick(day) {
            // Отменяем предыдущий таймаут, если он есть
            if (this.clickTimeout) {
                clearTimeout(this.clickTimeout)
                this.clickTimeout = null
                return
            }

            // Устанавливаем таймаут для различения одиночного и двойного клика
            this.clickTimeout = setTimeout(() => {
                this.clickTimeout = null
                this.showDayEvents(day)
            }, 300)
        },
        showEventDetails(event, day) {
            // Отменяем всплытие события, чтобы не сработал onDayClick
            if (this.clickTimeout) {
                clearTimeout(this.clickTimeout)
                this.clickTimeout = null
            }
            
            this.selectedDate = day.date
            this.selectedDayEvents = [event] // Показываем только выбранное событие
            this.showEventsModal = true
            this.showCreateModal = false
        },
        showDayEvents(day) {
            this.selectedDate = day.date
            this.selectedDayEvents = day.events
            this.showEventsModal = true
            this.showCreateModal = false
        },
        onDayDoubleClick(day) {
            // Отменяем таймаут одиночного клика
            if (this.clickTimeout) {
                clearTimeout(this.clickTimeout)
                this.clickTimeout = null
            }

            if (!this.isAdmin && !this.isAssistant) return

            // Устанавливаем выбранную дату в формате, который ожидает форма
            this.selectedDate = day.date
            this.selectedTime = '10:00' // Значение по умолчанию
            this.showCreateModal = true
            this.showEventsModal = false
        },
        onEventClick(event) {
            this.selectedEvent = event
            this.selectedDate = parseISO(`${event.date}T${event.time}`)
            this.showModal = true
        },
        previousMonth() {
            if (this.selectedMonth === 0) {
                this.selectedYear--;
                this.selectedMonth = 11;
            } else {
                this.selectedMonth--;
            }
            this.onDateChange();
        },
        nextMonth() {
            if (this.selectedMonth === 11) {
                this.selectedYear++;
                this.selectedMonth = 0;
            } else {
                this.selectedMonth++;
            }
            this.onDateChange();
        },
        closeModal() {
            this.showModal = false
            this.selectedEvent = null
            this.showEventsModal = false
            this.showCreateModal = false
            this.showEditModal = false
            this.editingBooking = null
            this.selectedDayEvents = []
        },
        editBooking(event) {
            this.editingBooking = event;
            this.selectedDate = new Date(event.date);
            this.selectedTime = event.time;
            this.showEditModal = true;
            this.showEventsModal = false;
        },
        showConfirmationForm(booking) {
            if (!this.isAdmin && !this.isAssistant) {
                this.error = "Только администратор или ассистент могут подтверждать заявки";
                return;
            }
            if (booking.event_status === 'confirmed') {
                this.error = "Заявка уже подтверждена";
                return;
            }
            this.error = null;
            this.confirmationBooking = booking;
        },
        closeConfirmationForm() {
            this.confirmationBooking = null;
        },
        onBookingConfirmed(bookingId) {
            const booking = this.bookings.find(b => b.id === bookingId);
            if (booking) {
                booking.event_status = 'confirmed';
            }
            this.closeConfirmationForm();
            this.closeModal();
            this.fetchBookings();
        },
        deleteBooking(event) {
            this.bookingToDelete = event
            this.showDeleteModal = true
        },
        cancelDelete() {
            this.showDeleteModal = false
            this.bookingToDelete = null
        },
        async confirmDelete() {
            if (!this.bookingToDelete) return;

            try {
                // Вместо удаления отправляем запрос на изменение статуса
                await axios.patch(`/api/bookings/${this.bookingToDelete.id}/`, {
                    event_status: 'cancelled'
                });
                
                // Обновляем статус в локальном состоянии
                const booking = this.bookings.find(b => b.id === this.bookingToDelete.id);
                if (booking) {
                    booking.event_status = 'cancelled';
                }
                
                this.showDeleteModal = false;
                this.bookingToDelete = null;
                this.closeModal();
            } catch (error) {
                console.error('Error cancelling booking:', error);
                this.error = 'Ошибка при отмене бронирования';
            }
        },
        async onBookingCreated(booking) {
            await this.fetchBookings()
            this.closeModal()
        },
        checkMobileView() {
            this.isMobileView = window.innerWidth <= this.mobileBreakpoint
        },
        onDateChange() {
            this.currentDate = new Date(this.selectedYear, this.selectedMonth, 1);
            this.fetchBookings();
        },
        showCancelConfirmation(bookingId) {
            this.bookingToCancel = bookingId;
            this.showCancelConfirmModal = true;
        },
        closeCancelConfirmation() {
            this.showCancelConfirmModal = false;
            this.bookingToCancel = null;
        },
        onBookingCancelled(data) {
            const booking = this.bookings.find(b => b.id === data.id);
            if (booking) {
                booking.event_status = 'cancelled';
                booking.client_comment = data.client_comment;
                booking.modified_at = data.modified_at;
            }
            this.closeModal();
            this.fetchBookings();
        },
        async onBookingUpdated(updatedBooking) {
            await this.fetchBookings();
            this.closeModal();
        },
        onBookingDeleted(bookingId) {
            this.fetchBookings();
        },
        handleError(errorMessage) {
            this.error = errorMessage;
        },
        showCopiedMessage() {
            this.successMessage = 'Номер телефона скопирован'
            this.showSuccessMessage = true
            setTimeout(() => {
                this.showSuccessMessage = false
                this.successMessage = ''
            }, 3000)
        },
        formatDateTime(datetime) {
            if (!datetime) return 'Нет данных';
            const date = new Date(datetime);
            const day = String(date.getDate()).padStart(2, '0');
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const year = date.getFullYear();
            const hours = String(date.getHours()).padStart(2, '0');
            const minutes = String(date.getMinutes()).padStart(2, '0');
            return `${day}-${month}-${year} ${hours}:${minutes}`;
        },
        // Добавлено: расчет суммы скидки с учетом требования
        getDiscountAmount(event) {
            const discount = Number(event.discount) || 0;
            if (discount === 0) return 0;
            const total = Number(event.total_price) || 0;
            const withDiscount = Number(event.total_price_with_discount) || 0;
            return total - withDiscount;
        },
        openPrepaymentModal(booking) {
            this.prepaymentBooking = booking;
            this.showPrepaymentModal = true;
        },
        closePrepaymentModal() {
            this.showPrepaymentModal = false;
            this.prepaymentBooking = null;
        },
        async onPrepaymentSuccess() {
            this.showPrepaymentModal = false;
            this.prepaymentBooking = null;
            await this.fetchBookings();
        },
        handlePhoneOpen(id) {
            this.openedPhoneId = id;
        },
    },
    async created() {
        await this.fetchUserRole()
        await this.fetchBookings()
        this.checkMobileView()
        window.addEventListener('resize', this.checkMobileView)
    },
    beforeUnmount() {
        window.removeEventListener('resize', this.checkMobileView)
    },
    watch: {
        currentDate: {
            handler(newDate) {
                this.selectedMonth = newDate.getMonth();
                this.selectedYear = newDate.getFullYear();
            },
            immediate: true
        }
    }
}
</script>

<style>
.calendar-container {
    padding: 16px;
    max-width: 1400px;
    margin: 0 auto;
    background: #fff;
}

.calendar-header {
    margin-bottom: 16px;
    background: white;
    border-radius: 8px;
    padding: 12px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.header-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
}

.calendar-title {
    font-size: 1.5rem;
    margin: 0;
    color: #2c3e50;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.cafe-selector {
    min-width: 200px;
    flex-shrink: 0;
}

.cafe-select {
    width: 100%;
    padding: 8px 12px;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    font-size: 0.9rem;
    color: #2c3e50;
    background-color: white;
    cursor: pointer;
}

.calendar-grid {
    display: grid;
    gap: 20px;
    grid-template-columns: 1fr;
    max-width: 900px;
    margin: 0 auto;
}

.calendar-month {
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.month-navigation {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding: 0 8px;
}

.month-title {
    font-size: 1.2rem;
    font-weight: 600;
    margin: 0;
    color: #2c3e50;
    text-transform: capitalize;
}

.nav-button {
    background: none;
    border: none;
    padding: 8px;
    cursor: pointer;
    color: #2c3e50;
    border-radius: 50%;
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background-color 0.2s;
}

.nav-button:hover {
    background-color: #f5f5f5;
}

.calendar-weekdays {
    display: grid;
    grid-template-columns: repeat(7, minmax(0, 1fr));
    gap: 6px;
    padding: 0;
}

.weekday {
    text-align: center;
    font-weight: 600;
    color: #64748b;
    font-size: 0.9rem;
    padding: 4px 0;
}

.calendar-days {
    display: grid;
    grid-template-columns: repeat(7, minmax(0, 1fr));
    gap: 6px;
    padding: 0;
}

.calendar-day {
    aspect-ratio: 1;
    padding: 4px;
    border: 1px solid #e2e8f0;
    cursor: pointer;
    border-radius: 8px;
    transition: all 0.2s;
    display: flex;
    flex-direction: column;
    width: 100%;
    max-width: 100%;
    margin: 0;
    background: white;
    position: relative;
}

.day-content-wrapper {
    position: absolute;
    top: 4px;
    left: 4px;
    right: 4px;
    bottom: 4px;
    display: flex;
    flex-direction: column;
}

.day-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.day-number {
    font-size: 0.9rem;
    font-weight: 500;
    color: #2c3e50;
}

.event-count {
    font-size: 0.7rem;
    padding: 1px 4px;
    background: #e2e8f0;
    border-radius: 10px;
    color: #64748b;
}

.calendar-day:hover {
    background: #f8fafc;
    border-color: #cbd5e1;
}

.calendar-day.other-month {
    opacity: 0.5;
}

.calendar-day.today {
    background: #e3f2fd;
    border-color: #90caf9;
}

.calendar-day.has-events {
    background: #f8f9fa;
}

.events-container {
    display: flex;
    flex-direction: column;
    gap: 2px;
    overflow-y: auto;
    flex: 1;
    margin-top: 4px;
}

.event-dot {
    padding: 2px 4px;
    border-radius: 4px;
    font-size: 0.75rem;
    cursor: pointer;
    transition: transform 0.2s, background-color 0.2s;
    background-color: #FFC107;
    color: #000;
    display: flex;
    flex-direction: column;
    z-index: 2;
}

.event-dot:hover {
    transform: scale(1.02);
    background-color: #FFB300;
}

.event-dot.confirmed {
  background-color: #C8F7C5;
  border: 1px solid #388E3C;
  color: #237A2C;
}

.event-dot.confirmed:hover {
    background-color: #43A047;
}

.event-time {
    font-weight: 600;
    margin-bottom: 2px;
}

.event-title {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.date-selector {
    display: flex;
    gap: 8px;
    align-items: center;
}

.month-select,
.year-select {
    padding: 6px 12px;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    font-size: 0.9rem;
    color: #2c3e50;
    background-color: white;
    cursor: pointer;
    transition: all 0.2s;
}

.month-select {
    min-width: 120px;
}

.year-select {
    min-width: 80px;
}

.month-select:hover,
.year-select:hover {
    border-color: #94a3b8;
}

/* Медиа-запросы для мобильных устройств */
@media (max-width: 768px) {
    .calendar-header {
        padding: 8px;
        margin-bottom: 8px;
    }

    .header-content {
        flex-direction: row;
        gap: 8px;
    }

    .calendar-title {
        font-size: 1.1rem;
    }

    .cafe-selector {
        min-width: 120px;
    }

    .cafe-select {
        padding: 6px 8px;
        font-size: 0.8rem;
    }

    .calendar-container {
        padding: 4px;
    }

    .calendar-month {
        padding: 8px;
        gap: 8px;
    }

    .calendar-weekdays,
    .calendar-days {
        gap: 4px;
    }

    .weekday {
        font-size: 0.8rem;
        padding: 2px 0;
    }

    .calendar-day {
        padding: 2px;
    }

    .day-content-wrapper {
        top: 2px;
        left: 2px;
        right: 2px;
        bottom: 2px;
    }

    .day-header {
        margin-bottom: 2px;
    }

    .day-number {
        font-size: 0.7rem;
    }

    .event-count {
        font-size: 0.6rem;
        padding: 1px 4px;
    }

    .events-container {
        gap: 1px;
        max-height: 50px;
    }

    .event-dot {
        padding: 1px 2px;
        font-size: 0.65rem;
        flex-direction: row;
        align-items: center;
        justify-content: center;
        min-height: 16px;
    }

    .event-dot.mobile-view {
        justify-content: center;
    }

    .event-dot.mobile-view .event-time {
        margin: 0;
        font-size: 0.65rem;
    }

    .event-dot.mobile-view .event-title {
        display: none;
    }

    .event-time {
        font-size: 0.65rem;
        margin: 0;
    }

    .calendar-grid {
        max-width: 100%;
    }

    .calendar-day {
        max-width: calc(100% * 0.85);
    }

    .date-selector {
        gap: 4px;
    }

    .month-select,
    .year-select {
        padding: 4px 8px;
        font-size: 0.8rem;
    }

    .month-select {
        min-width: 100px;
    }

    .year-select {
        min-width: 70px;
    }
}

/* Стили для очень маленьких экранов */
@media (max-width: 360px) {
    .header-content {
        flex-direction: row;
        gap: 4px;
    }

    .calendar-title {
        font-size: 1rem;
    }

    .cafe-selector {
        min-width: 100px;
    }

    .calendar-container {
        padding: 2px;
    }

    .calendar-weekdays,
    .calendar-days {
        gap: 2px;
        padding: 1px;
    }

    .calendar-day {
        max-width: calc(100% * 0.9);
        padding: 1px;
    }

    .day-number {
        font-size: 0.65rem;
    }

    .event-dot {
        padding: 1px;
        min-height: 14px;
    }

    .event-dot.mobile-view .event-time {
        font-size: 0.6rem;
    }

    .events-container {
        max-height: 45px;
    }

    .calendar-day {
        max-width: calc(100% * 0.9);
    }

    .month-select {
        min-width: 90px;
    }

    .year-select {
        min-width: 60px;
    }
}

/* Стили для средних экранов */
@media (min-width: 769px) and (max-width: 1024px) {
    .calendar-grid {
        max-width: 800px;
    }
}

/* Стили для больших экранов */
@media (min-width: 1025px) {
    .calendar-grid {
        max-width: 900px;
    }
}

/* Улучшенный скроллбар для мобильных устройств */
@media (max-width: 768px) {
    .events-container::-webkit-scrollbar {
        width: 2px;
    }

    .events-container::-webkit-scrollbar-track {
        background: transparent;
    }

    .events-container::-webkit-scrollbar-thumb {
        background: #cbd5e1;
        border-radius: 2px;
    }
}

/* Анимации */
@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(-10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.calendar-month {
    animation: fadeIn 0.3s ease-out;
}

/* Стили модального окна */
.modal {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
}

.modal-content {
    background: white;
    padding: 24px;
    border-radius: 12px;
    max-width: 500px;
    width: 90%;
    max-height: 90vh;
    overflow-y: auto;
    position: relative;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    animation: modalFadeIn 0.3s ease-out;
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 12px;
    border-bottom: 1px solid #e2e8f0;
}

.modal-header h3 {
    margin: 0;
    font-size: 1.25rem;
    color: #2c3e50;
    font-weight: 600;
}

.close-button {
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
    color: #64748b;
    padding: 4px;
    border-radius: 4px;
    transition: all 0.2s;
    line-height: 1;
}

.close-button:hover {
    background-color: #f1f5f9;
    color: #2c3e50;
}

.booking-details {
    padding: 16px;
    background: #f8fafc;
    border-radius: 8px;
}

.booking-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
}

.booking-time {
    font-size: 1.2em;
    font-weight: bold;
    color: #2c3e50;
}

.booking-status {
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 14px;
    display: flex;
    align-items: center;
    gap: 6px;
}

.booking-status.confirmed i {
    color: #4CAF50;
}

.booking-status.not_confirmed i {
    color: #FFC107;
}

.booking-info {
    margin-bottom: 20px;
}

.booking-info p {
    margin: 8px 0;
    color: #475569;
    display: flex;
    gap: 8px;
}

.booking-info p strong {
    color: #2c3e50;
    min-width: 140px;
}

.booking-actions {
    display: flex;
    gap: 10px;
    margin-top: 20px;
}

.btn {
    padding: 8px 16px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
    transition: all 0.2s;
    font-weight: 500;
}

.btn i {
    font-size: 16px;
}

.btn-edit {
    background-color: #2196F3;
    color: white;
    border: 1px solid #1976D2;
}

.btn-edit:hover {
    background-color: #1976D2;
    transform: translateY(-1px);
}

.btn-confirm {
    background-color: #4CAF50;
    color: white;
    border: 1px solid #388E3C;
}

.btn-confirm:hover {
    background-color: #388E3C;
    transform: translateY(-1px);
}

.btn-delete {
    background-color: #f44336;
    color: white;
}

.btn-delete:hover {
    background-color: #D32F2F;
    transform: translateY(-1px);
}

.delete-confirm {
    max-width: 400px;
    text-align: center;
    padding: 24px;
}

.delete-confirm h3 {
    color: #ef4444;
    margin-bottom: 16px;
}

.delete-confirm p {
    color: #475569;
    margin-bottom: 24px;
}

.delete-actions {
    display: flex;
    justify-content: center;
    gap: 16px;
}

.btn-cancel {
    background-color: #dc3545;
    color: white;
    border: 1px solid #a82d2d;
}

.btn-cancel:hover {
    background-color: #c82333;
    transform: translateY(-1px);
}

.btn-confirm-delete {
    background-color: #ef4444;
    color: white;
}

.btn-confirm-delete:hover {
    background-color: #dc2626;
}

@keyframes modalFadeIn {
    from {
        opacity: 0;
        transform: translateY(-20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Медиа-запросы для модального окна на мобильных устройствах */
@media (max-width: 768px) {
    .modal-content {
        width: 95%;
        margin: 10px;
    }

    .modal-header h3 {
        font-size: 1.1rem;
    }

    .booking-details {
        padding: 12px;
    }

    .booking-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 8px;
    }

    .booking-time {
        font-size: 1.1rem;
    }

    .booking-info p {
        flex-direction: column;
        gap: 4px;
    }

    .booking-info p strong {
        min-width: auto;
    }

    .booking-actions {
        flex-direction: column;
        gap: 8px;
    }

    .btn {
        width: 100%;
        justify-content: center;
        padding: 12px;
    }

    .delete-actions {
        flex-direction: column;
        gap: 8px;
    }

    .delete-confirm {
        padding: 16px;
    }
}

/* Добавляем стили для состояния загрузки */
.loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
}

.spinner {
    border: 4px solid #f3f3f3;
    border-top: 4px solid #3498db;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.error {
    color: #f44336;
    text-align: center;
    padding: 20px;
    background-color: #ffebee;
    border-radius: 4px;
    margin: 20px 0;
}

.events-modal {
    max-width: 600px;
    display: flex;
    flex-direction: column;
    max-height: 90vh;
    padding: 0;
}

.modal-header {
    position: sticky;
    top: 0;
    background: white;
    z-index: 10;
    padding: 16px 20px;
    border-bottom: 1px solid #e2e8f0;
    margin: 0;
    border-radius: 8px 8px 0 0;
}

.events-list {
    padding: 16px;
    overflow-y: auto;
    flex: 1;
}

/* Добавляем эффект тени при скролле */
.modal-header::after {
    content: '';
    position: absolute;
    bottom: -10px;
    left: 0;
    right: 0;
    height: 10px;
    background: linear-gradient(to bottom, rgba(0,0,0,0.1), transparent);
    opacity: 0;
    transition: opacity 0.2s;
    pointer-events: none;
}

.events-list:not(:first-child) + .modal-header::after {
    opacity: 1;
}

/* Обновляем стили для мобильных устройств */
@media (max-width: 768px) {
    .modal-content.events-modal {
        width: 95%;
        margin: 10px;
        max-height: 85vh;
    }

    .modal-header {
        padding: 12px 16px;
    }

    .events-list {
        padding: 12px;
    }
}

.no-events {
    text-align: center;
    color: #64748b;
    padding: 20px;
}

.event-item {
    background: #f8fafc;
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 12px;
    border: 1px solid #e2e8f0;
}

.event-item:last-child {
    margin-bottom: 0;
}

.event-item.confirmed {
    border-left: 4px solid #4CAF50;
}

.event-item.not_confirmed {
    border-left: 4px solid #FFC107;
}

.event-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid #e2e8f0;
}

.event-time {
    font-weight: 600;
    color: #2c3e50;
    font-size: 1.1rem;
}

.event-details {
    padding: 15px;
    background-color: #f8f9fa;
    border-radius: 8px;
    margin: 10px 0;
}

.event-details p {
    margin: 8px 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 4px 0;
    border-bottom: 1px solid #e9ecef;
}

.event-details p:last-child {
    border-bottom: none;
    color: #2196F3;
    font-weight: 600;
}

.event-details strong {
    color: #495057;
    font-weight: 500;
}

.comment-section {
    margin: 12px 0;
    padding: 12px;
    background-color: #f8f9fa;
    border-radius: 8px;
    border: 1px solid #e9ecef;
}

.comment-section strong {
    display: block;
    margin-bottom: 8px;
    color: #495057;
    font-weight: 600;
}

.event-comment {
    color: #6c757d;
    font-style: italic;
    padding: 8px 12px;
    border-radius: 6px;
    border-left: 3px solid #007bff;
    background-color: white;
    word-wrap: break-word;
    white-space: pre-wrap;
    line-height: 1.5;
}

.comment-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 8px;
    padding-top: 8px;
    border-top: 1px solid #e9ecef;
    font-size: 0.75rem;
    color: #6c757d;
}

.comment-author,
.comment-date {
    font-size: 0.7rem;
    color: #868e96;
    font-style: normal;
}

.comment-author {
    font-weight: 500;
}

.comment-date {
    font-style: italic;
}

.event-actions {
    display: flex;
    gap: 8px;
    margin-top: 16px;
    flex-wrap: wrap;
}

.event-actions .btn {
    flex: 1;
    min-width: 120px;
    justify-content: center;
}

@media (max-width: 768px) {
    .event-actions {
        flex-direction: column;
    }
    
    .event-actions .btn {
        width: 100%;
    }

    .comment-meta {
        flex-direction: column;
        align-items: flex-start;
        gap: 4px;
    }

    .comment-author,
    .comment-date {
        font-size: 0.65rem;
    }
}

.show-cancelled-wrapper {
    display: flex;
    align-items: center;
    padding: 4px 12px;
    margin-top: 8px;
}

.show-cancelled-label {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    user-select: none;
    color: #64748b;
    font-size: 0.875rem;
}

.show-cancelled-checkbox {
    width: 14px;
    height: 14px;
    cursor: pointer;
    accent-color: #4CAF50;
}

.event-dot.cancelled {
    background-color: #dc3545;
    opacity: 0.7;
}

.event-item.cancelled {
    background-color: #ffebee;
    border-left: 4px solid #dc3545;
}

.event-status.cancelled i {
    color: #dc3545;
}

.calendar-day.weekend {
    background-color: #f8f9fa;
}

.calendar-day.weekend .day-number {
    color: #dc3545;
    font-weight: 600;
}

.calendar-day.weekend:hover {
    background-color: #e9ecef;
}

.calendar-day.weekend.today {
    background-color: #e3f2fd;
}

.calendar-day.weekend.other-month .day-number {
    color: #ff8a8a;
    opacity: 0.5;
}

.calendar-weekdays div:nth-child(6),
.calendar-weekdays div:nth-child(7) {
    color: #dc3545;
    font-weight: 600;
}

.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
}

.modal-content {
    background: white;
    border-radius: 8px;
    width: 90%;
    max-width: 400px;
    position: relative;
    padding: 0;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.modal-header {
    padding: 16px 20px;
    border-bottom: 1px solid #eee;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.modal-header h3 {
    margin: 0;
    font-size: 1.25rem;
    color: #2c3e50;
}

.close-button {
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
    color: #666;
    padding: 0;
    line-height: 1;
}

.close-button:hover {
    color: #333;
}

.confirmation-content {
    padding: 20px;
}

.confirmation-content p {
    margin: 0 0 20px;
    text-align: center;
    color: #2c3e50;
    font-size: 1rem;
}

.warning-text {
    color: #dc3545;
    font-size: 0.9rem;
    text-align: center;
    margin-bottom: 20px;
}

.confirmation-actions {
    display: flex;
    justify-content: center;
    gap: 12px;
    margin-top: 20px;
}

.modal-button {
    padding: 8px 20px;
    border: none;
    border-radius: 4px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: background-color 0.2s;
}

.modal-button i {
    margin-right: 8px;
}

.modal-button.confirm {
    background-color: #dc3545;
    color: white;
}

.modal-button.confirm:hover {
    background-color: #c82333;
}

.modal-button.cancel {
    background-color: #6c757d;
    color: white;
}

.modal-button.cancel:hover {
    background-color: #5a6268;
}

@media (max-width: 768px) {
    .modal-content {
        width: 95%;
        margin: 10px;
    }

    .confirmation-actions {
        flex-direction: column;
    }

    .modal-button {
        width: 100%;
        margin: 5px 0;
    }
}

.comment-section {
    margin: 20px 0;
}

.comment-label {
    display: block;
    margin-bottom: 8px;
    color: #2c3e50;
    font-weight: 500;
}

.cancel-comment-input {
    width: 100%;
    padding: 8px 12px;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    font-size: 14px;
    resize: vertical;
    min-height: 80px;
}

.cancel-comment-input:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

.comment-error {
    display: block;
    color: #dc3545;
    font-size: 0.875rem;
    margin-top: 4px;
}

.modal-button:disabled {
    background-color: #9ca3af;
    cursor: not-allowed;
}

.modal-button:disabled:hover {
    background-color: #9ca3af;
    transform: none;
}

.success-message {
    position: fixed;
    top: 20px;
    right: 20px;
    background-color: #4CAF50;
    color: white;
    padding: 15px 25px;
    border-radius: 4px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    z-index: 1000;
    animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

.event-actions .btn-edit {
    background-color: #E1ECF4;
    color: #2D70B7;
}
.event-actions .btn-edit:hover {
    background-color: #c9e2f6;
    color: #205a8c;
}
.event-actions .btn-confirm {
    background-color: #D7F4DD !important;
    color: #2C8559 !important;
    border: 1px solid #237A2C !important;
    box-shadow: none !important;
}
.event-actions .btn-confirm:hover {
    background-color: #b6eac3 !important;
    color: #206c45 !important;
}
.event-actions .btn-cancel {
    background-color: #FCE2E2;
    color: #C64545;
}
.event-actions .btn-cancel:hover {
    background-color: #f8bcbc;
    color: #a82d2d;
}
.event-actions .btn-prepayment {
    background-color: #FFF6D9;
    color: #D18B00;
    border: 1px solid #D18B00;
}
.event-actions .btn-prepayment:hover {
    background-color: #ffeab0;
    color: #a86c00;
}
.event-dot.not_confirmed {
  background-color: #FFE9B3;
  border: 1px solid #FFA000;
  color: #D18B00;
}
</style> 