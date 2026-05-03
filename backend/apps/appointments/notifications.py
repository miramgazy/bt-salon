import logging
from django.utils import timezone
from apps.accounts.utils import send_telegram_message

logger = logging.getLogger(__name__)

def notify_master_new_appointment(appointment):
    """
    Sends a bilingual notification to the master about a new appointment.
    """
    master = appointment.master
    if not master or not master.user or not master.user.telegram_id:
        return
        
    org = appointment.organization
    if not org or not org.bot_token:
        return
        
    user = master.user
    lang = user.language or 'ru'
    
    # Format date and time
    local_time = timezone.localtime(appointment.start_time)
    date_str = local_time.strftime('%d.%m.%Y')
    time_str = local_time.strftime('%H:%M')
    
    client_name = appointment.client.full_name if appointment.client else "Клиент"
    service_name = appointment.service.name if appointment.service else "Услуга"
    
    if lang == 'kz':
        text = (
            f"<b>{user.first_name}, сіздің атыңызға жаңа жазба бар:</b>\n\n"
            f"💇‍♂️ Қызмет: {service_name}\n"
            f"📅 Күні: {date_str}\n"
            f"⏰ Уақыты: {time_str}\n"
            f"👤 Клиент: {client_name}\n\n"
            f"<i>Қызмет көрсетілгеннен кейін төмендегі батырманы басыңыз.</i>"
        )
        btn_done = "✅ Орындалды"
        btn_cancel = "❌ Бас тарту"
    else:
        text = (
            f"<b>{user.first_name}, на ваше имя есть новая запись:</b>\n\n"
            f"💇‍♂️ Услуга: {service_name}\n"
            f"📅 Дата: {date_str}\n"
            f"⏰ Время: {time_str}\n"
            f"👤 Имя клиента: {client_name}\n\n"
            f"<i>После оказания услуг нажмите кнопку ниже.</i>"
        )
        btn_done = "✅ Выполнено"
        btn_cancel = "❌ Отменено"
        
    markup = {
        "inline_keyboard": [[
            {"text": btn_done, "callback_data": f"master_done_{appointment.id}"},
            {"text": btn_cancel, "callback_data": f"master_cancel_{appointment.id}"}
        ]]
    }
    
    res = send_telegram_message(org.bot_token, user.telegram_id, text, reply_markup=markup)
    if res and res.get('ok'):
        logger.info(f"Master notification sent to {user.telegram_id} for appt {appointment.id}")
    else:
        logger.error(f"Failed to send master notification for appt {appointment.id}: {res}")

def notify_master_appointment_updated(appointment, old_data=None):
    """
    Notifies the master that an existing appointment has been updated (time/service).
    """
    master = appointment.master
    if not master or not master.user or not master.user.telegram_id:
        return
        
    org = appointment.organization
    if not org or not org.bot_token:
        return
        
    user = master.user
    lang = user.language or 'ru'
    
    local_time = timezone.localtime(appointment.start_time)
    date_str = local_time.strftime('%d.%m.%Y')
    time_str = local_time.strftime('%H:%M')
    service_name = appointment.service.name if appointment.service else "Услуга"
    
    if lang == 'kz':
        text = (
            f"<b>🔄 Жазба өзгертілді:</b>\n\n"
            f"💇‍♂️ Қызмет: {service_name}\n"
            f"📅 Жаңа күні: {date_str}\n"
            f"⏰ Жаңа уақыты: {time_str}\n"
        )
    else:
        text = (
            f"<b>🔄 Запись изменена:</b>\n\n"
            f"💇‍♂️ Услуга: {service_name}\n"
            f"📅 Новая дата: {date_str}\n"
            f"⏰ Новое время: {time_str}\n"
        )
        
    send_telegram_message(org.bot_token, user.telegram_id, text)

def notify_master_appointment_cancelled(appointment, master=None):
    """
    Notifies the master that an appointment has been cancelled.
    If 'master' is provided, notify that specific master (used when master is changed).
    """
    target_master = master or appointment.master
    if not target_master or not target_master.user or not target_master.user.telegram_id:
        return
        
    org = appointment.organization
    if not org or not org.bot_token:
        return
        
    user = target_master.user
    lang = user.language or 'ru'
    
    local_time = timezone.localtime(appointment.start_time)
    date_str = local_time.strftime('%d.%m.%Y')
    time_str = local_time.strftime('%H:%M')
    
    if lang == 'kz':
        text = (
            f"<b>❌ Жазба тоқтатылды:</b>\n\n"
            f"📅 Күні: {date_str}\n"
            f"⏰ Уақыты: {time_str}\n"
            f"Клиент жазбасы жойылды немесе басқа шеберге ауыстырылды."
        )
    else:
        text = (
            f"<b>❌ Запись отменена:</b>\n\n"
            f"📅 Дата: {date_str}\n"
            f"⏰ Время: {time_str}\n"
            f"Запись клиента была отменена или передана другому мастеру."
        )
        
    send_telegram_message(org.bot_token, user.telegram_id, text)
