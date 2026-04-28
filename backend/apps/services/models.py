from django.db import models

class Category(models.Model):
    organization = models.ForeignKey('organization.Organization', on_delete=models.CASCADE, related_name='categories', null=True, blank=True)
    name = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)

class Service(models.Model):
    MARGIN_FIXED = 'fixed'
    MARGIN_PERCENT = 'percent'
    MARGIN_TYPES = [(MARGIN_FIXED, 'Фикс'), (MARGIN_PERCENT, 'Процент')]

    organization = models.ForeignKey('organization.Organization', on_delete=models.CASCADE, related_name='services', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    name = models.CharField(max_length=255)
    duration_minutes = models.PositiveIntegerField()
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    margin_type = models.CharField(max_length=10, choices=MARGIN_TYPES)
    margin_value = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    STRATEGY_EQUAL = 'equal_split'
    STRATEGY_MASTER = 'master_only'
    STRATEGY_OWNER = 'owner_only'
    DISCOUNT_STRATEGIES = [
        (STRATEGY_EQUAL, '50/50 (Мастер и Салон)'),
        (STRATEGY_MASTER, 'Только Мастер'),
        (STRATEGY_OWNER, 'Только Салон'),
    ]

    is_active = models.BooleanField(default=True)
    is_combo = models.BooleanField(default=False)
    discount_strategy = models.CharField(max_length=20, choices=DISCOUNT_STRATEGIES, default=STRATEGY_OWNER)

    def save(self, *args, **kwargs):
        if not self.is_combo:
            if self.margin_type == self.MARGIN_FIXED:
                self.total_price = self.base_price + self.margin_value
            else:
                self.total_price = self.base_price * (1 + self.margin_value / 100)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class ComboItem(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='combo_items')
    sub_service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='included_in_combos')
    quantity = models.PositiveIntegerField(default=1)
    is_main = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.service.name} -> {self.sub_service.name} (x{self.quantity})"
