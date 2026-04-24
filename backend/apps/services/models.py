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
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.margin_type == self.MARGIN_FIXED:
            self.total_price = self.base_price + self.margin_value
        else:
            self.total_price = self.base_price * (1 + self.margin_value / 100)
        super().save(*args, **kwargs)
