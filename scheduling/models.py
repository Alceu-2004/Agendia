from django.db import models
from business.models import Business, Service
from django.core.exceptions import ValidationError
from django.db.models import Q


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
    client_email = models.EmailField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    reminder_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.client_name} - {self.start_time.strftime('%d/%m %H:%M')}"

    def clean(self):
        if self.start_time and self.end_time:
            if self.start_time >= self.end_time:
                raise ValidationError("O horário de início deve ser anterior ao horário de término.")

            conflitos = Appointment.objects.filter(
                business=self.business,
                status__in=[self.Status.PENDING, self.Status.CONFIRMED],
            ).filter(
                Q(start_time__lt=self.end_time) & Q(end_time__gt=self.start_time)
            ).exclude(pk=self.pk)

            if conflitos.exists():
                raise ValidationError("Já existe um agendamento nesse horário para este negócio.")