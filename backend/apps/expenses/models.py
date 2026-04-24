from django.db import models

class ExpenseCategory(models.Model):
    """Статья расхода"""
    TYPE_FIXED = 'fixed'
    TYPE_VARIABLE = 'variable'
    TYPE_CHOICES = [
        (TYPE_FIXED, 'Постоянный'),
        (TYPE_VARIABLE, 'Переменный'),
    ]

    organization = models.ForeignKey('organization.Organization', on_delete=models.CASCADE, related_name='expense_categories', null=True, blank=True)
    name = models.CharField(max_length=255, verbose_name="Название")
    category_type = models.CharField(
        max_length=10, 
        choices=TYPE_CHOICES, 
        default=TYPE_VARIABLE, 
        verbose_name="Тип расхода"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Статья расхода"
        verbose_name_plural = "Статьи расходов"
        unique_together = ('organization', 'name')
        ordering = ["name"]

    def __str__(self):
        return self.name


class Expense(models.Model):
    """Расход"""
    organization = models.ForeignKey('organization.Organization', on_delete=models.CASCADE, related_name='expenses', null=True, blank=True)
    date = models.DateField(verbose_name="Дата")
    name = models.CharField(max_length=255, verbose_name="Название расхода")
    category = models.ForeignKey(
        ExpenseCategory,
        on_delete=models.PROTECT,
        related_name="expenses",
        verbose_name="Статья расхода"
    )
    amount = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name="Сумма"
    )
    comment = models.TextField(blank=True, default="", verbose_name="Комментарий")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Расход"
        verbose_name_plural = "Расходы"
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.date} | {self.name} | {self.amount}"
