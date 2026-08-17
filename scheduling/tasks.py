from celery import shared_task
from django.utils import timezone
from datetime import timedelta

@shared_task
def send_confirmation_notification(appointment_id):
    from .models import Appointment
    try:
        appointment = Appointment.objects.get(id=appointment_id)
    except Appointment.DoesNotExist:
        return f"Appointment {appointment_id} não encontrado."

    print(f"[SIMULAÇÃO] Enviando confirmação para {appointment.client_name} "
          f"sobre agendamento em {appointment.start_time}")

    return f"Notificação simulada enviada para {appointment.client_name}"

@shared_task
def send_pending_reminders():
    from .models import Appointment

    now = timezone.now()
    window_start = now
    window_end = now + timedelta(hours=24)

    appointments = Appointment.objects.filter(
        start_time__gte=window_start,
        start_time__lte=window_end,
        reminder_sent=False,
        status__in=[Appointment.Status.PENDING, Appointment.Status.CONFIRMED],
    )

    count = 0
    for appointment in appointments:
        print(f"[SIMULAÇÃO] Lembrete para {appointment.client_name}: "
              f"seu horário é em {appointment.start_time}")
        appointment.reminder_sent = True
        appointment.save(update_fields=['reminder_sent'])
        count += 1

    return f"{count} lembrete(s) processado(s)."