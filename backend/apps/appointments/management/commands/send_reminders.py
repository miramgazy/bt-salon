import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.appointments.models import Appointment
from apps.organization.models import Organization
from apps.accounts.utils import send_telegram_message

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Sends reminders to clients based on organization settings'

    def handle(self, *args, **options):
        now = timezone.now()
        
        # 1. Get enabled organizations
        orgs = Organization.objects.filter(is_reminders_enabled=True, bot_token__isnull=False)
        
        total_count = 0
        for org in orgs:
            # 2. Calculate time range for this specific organization
            hours = org.reminder_hours_before
            # We look in a 20-minute window around the target hour to ensure 
            # we don't miss appointments if cron runs every 10 mins
            target_time = now + timedelta(hours=hours)
            start_range = target_time - timedelta(minutes=10)
            end_range = target_time + timedelta(minutes=10)
            
            # 3. Find appointments for this org
            appointments = Appointment.objects.filter(
                organization=org,
                start_time__range=(start_range, end_range),
                status__in=[Appointment.STATUS_PENDING, Appointment.STATUS_CONFIRMED],
                client_confirmation=Appointment.CONFIRMATION_PENDING,
                is_reminder_sent=False,
                client__user__telegram_id__isnull=False
            ).select_related('client__user', 'service', 'master__user')
            
            for appt in appointments:
                user = appt.client.user
                
                # Pick template
                template = org.reminder_template_ru
                if user.language == 'kz':
                    template = org.reminder_template_kz
                    
                # Format placeholders
                start_time_str = timezone.localtime(appt.start_time).strftime('%H:%M')
                
                try:
                    message = template.format(
                        Organization_name=org.name,
                        User_name=user.first_name or "Клиент",
                        Service_name=appt.service.name if appt.service else "Услуга",
                        Master_name=appt.master.user.first_name if appt.master and appt.master.user else "Мастер",
                        Start_time=start_time_str
                    )
                    
                    markup = {
                        "inline_keyboard": [[
                            {"text": "✅ Да, приду", "callback_data": f"appt_confirm_{appt.id}"},
                            {"text": "❌ Нет, не смогу", "callback_data": f"appt_cancel_{appt.id}"}
                        ]]
                    }
                    
                    res = send_telegram_message(org.bot_token, user.telegram_id, message, reply_markup=markup)
                    
                    if res and res.get('ok'):
                        appt.is_reminder_sent = True
                        appt.save(update_fields=['is_reminder_sent'])
                        logger.info(f"Reminder sent to {user.telegram_id} for appt {appt.id} (Org: {org.name})")
                        total_count += 1
                    else:
                        logger.error(f"Failed to send reminder for appt {appt.id}: {res}")
                except Exception as e:
                    logger.error(f"Error formatting/sending reminder for appt {appt.id}: {e}")
                    
        self.stdout.write(self.style.SUCCESS(f'Successfully sent {total_count} reminders across all organizations'))
