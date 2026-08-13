from django.db import models
from business.models import Business, Service

class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pendente'
        CONFIRMED = 'confirmed', 'Confirmado'
        CANCELLED = 'cancelled', 'Cancelado'
        DONE = 'done', 'Concluído'

    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    client_name = models.CharField(max_length=100)
    client_phone = models.CharField(max_length=20)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    reminder_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.client_name} - {self.start_time.strftime('%d/%m %H:%M')}"