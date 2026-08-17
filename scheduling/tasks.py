from celery import shared_task

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