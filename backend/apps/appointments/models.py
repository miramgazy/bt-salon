from django.db import models
from datetime import timedelta

class Appointment(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_DONE = 'done'
    STATUSES = [
        (STATUS_PENDING, 'Ожидает'),
        (STATUS_CONFIRMED, 'Подтверждена'),
        (STATUS_CANCELLED, 'Отменена'),
        (STATUS_DONE, 'Завершена'),
    ]

    organization = models.ForeignKey('organization.Organization', on_delete=models.CASCADE, related_name='appointments', null=True, blank=True)
    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE)
    master = models.ForeignKey('masters.Master', on_delete=models.CASCADE)
    service = models.ForeignKey('services.Service', on_delete=models.CASCADE)
    shift = models.ForeignKey('masters.MasterShift', on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUSES, default=STATUS_PENDING)
    
    CONFIRMATION_PENDING = 'pending'
    CONFIRMATION_YES = 'yes'
    CONFIRMATION_NO = 'no'
    CONFIRMATION_CHOICES = [
        (CONFIRMATION_PENDING, 'Ожидает ответа'),
        (CONFIRMATION_YES, 'Да, приду'),
        (CONFIRMATION_NO, 'Нет, не приду'),
    ]
    client_confirmation = models.CharField(
        max_length=10, 
        choices=CONFIRMATION_CHOICES, 
        default=CONFIRMATION_PENDING
    )

    created_by_admin = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    cancellation_reason = models.TextField(blank=True, null=True, help_text='Причина отмены, если статус cancelled')
    created_at = models.DateTimeField(auto_now_add=True)

    # Combo fields
    TYPE_SINGLE = 'single'
    TYPE_COMBO_MASTER = 'combo_master'
    TYPE_COMBO_SUB = 'combo_sub'
    APPOINTMENT_TYPES = [
        (TYPE_SINGLE, 'Обычная'),
        (TYPE_COMBO_MASTER, 'Комбо (Основная)'),
        (TYPE_COMBO_SUB, 'Комбо (Дочерняя)'),
    ]
    appointment_type = models.CharField(max_length=20, choices=APPOINTMENT_TYPES, default=TYPE_SINGLE)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    # Financial snapshots
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_strategy = models.CharField(max_length=20, default='owner_only')
    master_net_income = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salon_net_income = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_overflow = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.start_time} - {self.client.full_name} - {self.service.name}"

    def calculate_financials(self):
        """
        Calculates how the total price (after discount) is split between master and salon.
        """
        from decimal import Decimal
        from apps.services.models import Service

        # 0. Base calculation components
        # If this is a combo sub-part or a distributed parent, use self.total_price if > 0
        # Otherwise fallback to service default
        current_total = Decimal(str(self.total_price)) if self.total_price > 0 else Decimal(str(self.service.total_price))
        
        # 1. Determine Gross base_price and margin for this specific record
        if self.appointment_type == self.TYPE_COMBO_MASTER:
            # For the master record in a combo, we use the "Main" sub-service's settings
            main_item = self.service.combo_items.filter(is_main=True).first()
            if main_item:
                sub = main_item.sub_service
                gross_base = sub.base_price
                gross_margin = sub.margin_value
                if sub.margin_type == Service.MARGIN_PERCENT:
                    gross_margin = sub.base_price * (sub.margin_value / 100)
                target_service_total = sub.total_price
            else:
                gross_base = Decimal('0')
                gross_margin = Decimal('0')
                target_service_total = Decimal('0')
        else:
            # Single service or combo sub-record
            gross_base = self.service.base_price
            gross_margin = self.service.margin_value
            if self.service.margin_type == Service.MARGIN_PERCENT:
                gross_margin = self.service.base_price * (self.service.margin_value / 100)
            target_service_total = self.service.total_price
        
        # Discount for this specific record is the difference between its target and actual distributed price
        current_discount = max(Decimal('0'), target_service_total - current_total)

        # 2. Distribute discount according to strategy
        master_share = Decimal('0')
        salon_share = Decimal('0')
        overflow = False

        if self.discount_strategy == 'equal_split':
            half = current_discount / 2
            master_share = half
            salon_share = half
        elif self.discount_strategy == 'master_only':
            master_share = current_discount
        else: # owner_only
            salon_share = current_discount

        # 3. Apply Cap at 0 and Overflow
        final_salon = gross_margin - salon_share
        if final_salon < 0:
            overflow = True
            master_share += abs(final_salon)
            final_salon = Decimal('0')
        
        final_master = gross_base - master_share
        if final_master < 0:
            final_master = Decimal('0')
            
        self.master_net_income = final_master
        self.salon_net_income = final_salon
        self.is_overflow = overflow
        self.discount_amount = current_discount # Sync snapshot

    def save(self, *args, **kwargs):
        from django.db import transaction
        from apps.masters.models import Master, MasterShift
        from datetime import timedelta
        from decimal import Decimal
        
        is_new = self.pk is None
        old_status = None
        old_start = None
        old_reason = None
        
        if not is_new:
            try:
                old_instance = Appointment.objects.get(pk=self.pk)
                old_status = old_instance.status
                old_start = old_instance.start_time
                old_reason = old_instance.cancellation_reason
            except Appointment.DoesNotExist:
                pass

        # 1. Automatic type detection and total_price setup
        if is_new and self.service.is_combo:
            self.appointment_type = self.TYPE_COMBO_MASTER
        
        if not self.total_price and self.service and self.appointment_type != self.TYPE_COMBO_SUB:
            self.total_price = self.service.total_price

        # 2. Financial calculation
        self.calculate_financials()

        # 3. Save the instance itself
        super().save(*args, **kwargs)

        # 4. Handle Combo Logic
        if self.appointment_type == self.TYPE_COMBO_MASTER:
            with transaction.atomic():
                if is_new:
                    # CREATE CHILDREN
                    virtual_master = Master.objects.filter(organization=self.organization, is_virtual=True).first()
                    if not virtual_master:
                        from apps.accounts.models import User as AppUser
                        import random, string
                        username = f"v_{self.organization.id}_{''.join(random.choices(string.ascii_lowercase, k=4))}"
                        v_user = AppUser.objects.create(
                            username=username, 
                            first_name="Виртуальный", 
                            last_name="Мастер", 
                            organization=self.organization, 
                            role=AppUser.ROLE_MASTER
                        )
                        virtual_master = Master.objects.create(
                            organization=self.organization, 
                            user=v_user, 
                            is_virtual=True, 
                            color="#FF9C00"
                        )
                    
                    v_shift, _ = MasterShift.objects.get_or_create(
                        organization=self.organization,
                        master=virtual_master,
                        date=self.start_time.date(),
                        defaults={
                            'is_open': True, 
                            'work_start': self.organization.work_start or '00:00', 
                            'work_end': self.organization.work_end or '23:59'
                        }
                    )
                    if not v_shift.is_open:
                        v_shift.is_open = True
                        v_shift.save(update_fields=['is_open'])
                        
                    children_list = []
                    for item in self.service.combo_items.all():
                        # If main item has quantity > 1, the first one is this appointment,
                        # the rest should be created as children.
                        start_from = 1 if item.is_main else 0
                        for _ in range(start_from, item.quantity):
                            child = Appointment.objects.create(
                                organization=self.organization,
                                client=self.client,
                                master=virtual_master,
                                service=item.sub_service,
                                shift=v_shift,
                                start_time=self.start_time,
                                end_time=self.start_time + timedelta(minutes=item.sub_service.duration_minutes),
                                status=self.status,
                                parent=self,
                                appointment_type=self.TYPE_COMBO_SUB,
                                discount_strategy=self.discount_strategy,
                                created_by_admin=self.created_by_admin
                            )
                            children_list.append(child)
                    
                    # PRICE DISTRIBUTION
                    combo_price = Decimal(str(self.service.total_price))
                    main_item = self.service.combo_items.filter(is_main=True).first()
                    total_parts_price = sum(Decimal(str(it.sub_service.total_price)) * it.quantity for it in self.service.combo_items.all())
                    total_discount = max(Decimal('0'), total_parts_price - combo_price)
                    
                    all_records = [self] + children_list
                    num_records = len(all_records)
                    discount_per_record = total_discount / num_records if num_records > 0 else Decimal('0')
                    
                    for appt in all_records:
                        if appt == self:
                            sub_price = Decimal(str(main_item.sub_service.total_price)) if main_item else Decimal('0')
                        else:
                            sub_price = Decimal(str(appt.service.total_price))
                        
                        appt.total_price = sub_price - discount_per_record
                        appt.calculate_financials()
                        Appointment.objects.filter(pk=appt.pk).update(
                            total_price=appt.total_price,
                            discount_amount=appt.discount_amount,
                            master_net_income=appt.master_net_income,
                            salon_net_income=appt.salon_net_income,
                            is_overflow=appt.is_overflow
                        )

                else:
                    # SYNC UPDATES TO CHILDREN
                    if old_status != self.status or old_start != self.start_time or old_reason != self.cancellation_reason:
                        for child in self.children.all():
                            child.status = self.status
                            child.start_time = self.start_time
                            child.end_time = self.start_time + timedelta(minutes=child.service.duration_minutes)
                            child.cancellation_reason = self.cancellation_reason
                            child.save()
                        
                        self.calculate_financials()
                        super().save(update_fields=['master_net_income', 'salon_net_income', 'is_overflow'])
