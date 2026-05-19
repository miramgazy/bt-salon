from django.db import models

class UsedReceipt(models.Model):
    organization = models.ForeignKey('organization.Organization', on_delete=models.CASCADE, related_name='used_receipts')
    receipt_number = models.CharField(max_length=100)
    appointment = models.ForeignKey('appointments.Appointment', on_delete=models.CASCADE, related_name='used_receipts')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('organization', 'receipt_number')

    def __str__(self):
        return f"{self.organization.name} - {self.receipt_number}"
