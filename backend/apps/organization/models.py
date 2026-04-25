from django.db import models

class Organization(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    work_start = models.TimeField(default='09:00')
    work_end = models.TimeField(default='20:00')
    lunch_start = models.TimeField(default='13:00')
    lunch_end = models.TimeField(default='14:00')
    bot_token = models.CharField(max_length=255)
    bot_username = models.CharField(max_length=100, blank=True, null=True, help_text="Username of the bot (without @)")
    tma_name = models.CharField(max_length=100, blank=True, null=True, help_text="Short name of the Mini App in BotFather")
    
    # TMA Customization fields
    instagram_link = models.URLField(blank=True, null=True, help_text="Link to Instagram profile")
    whatsapp_number = models.CharField(max_length=20, blank=True, null=True, help_text="WhatsApp contact number")
    greeting_text = models.CharField(max_length=255, default="Добро пожаловать!", help_text="Greeting text in the TMA header")
    design_color = models.CharField(max_length=7, default="#c9a84c", help_text="Hex color code for the TMA theme")
    logo = models.ImageField(upload_to='organizations/logos/', null=True, blank=True, help_text="Organization logo for TMA header")
    latitude = models.FloatField(null=True, blank=True, help_text="Latitude for maps geocoding")
    longitude = models.FloatField(null=True, blank=True, help_text="Longitude for maps geocoding")
    
    # Notification Settings
    is_reminders_enabled = models.BooleanField(
        default=False, 
        help_text="Включить автоматическую рассылку напоминаний"
    )
    reminder_hours_before = models.PositiveIntegerField(
        default=1, 
        help_text="За сколько часов до записи отправлять напоминание"
    )

    # Notification Templates
    reminder_template_ru = models.TextField(
        default="Привет, {User_name}! Напоминаем о вашей записи в {Organization_name} в {Start_time}.\n\nУслуга: {Service_name}\nМастер: {Master_name}\n\nВы придете?",
        help_text="Шаблон на русском. Плейсхолдеры: {Organization_name}, {User_name}, {Service_name}, {Master_name}, {Start_time}"
    )
    reminder_template_kz = models.TextField(
        default="Сәлем, {User_name}! {Organization_name} салонындағы сағат {Start_time}-дегі жазбаңызды еске саламыз.\n\nҚызмет: {Service_name}\nШебер: {Master_name}\n\nКелесіз бе?",
        help_text="Шаблон на казахском. Плейсхолдеры: {Organization_name}, {User_name}, {Service_name}, {Master_name}, {Start_time}"
    )

    # Scheduling Settings
    slot_duration = models.PositiveIntegerField(
        default=30,
        help_text="Базовая длительность слота в минутах (шаг записи)"
    )

    created_at = models.DateTimeField(auto_now_add=True)
