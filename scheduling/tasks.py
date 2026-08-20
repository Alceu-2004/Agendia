import os
import requests
from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta


def send_whatsapp_message(to_number, message_body):
    token = os.environ.get('WHATSAPP_TOKEN')
    phone_number_id = os.environ.get('WHATSAPP_PHONE_NUMBER_ID')

    if not token or not phone_number_id:
        print(f"[WHATSAPP SIMULADO] Para {to_number}: {message_body}")
        return None

    url = f"https://graph.facebook.com/v21.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": message_body},
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        print(f"[ERRO AO ENVIAR WHATSAPP] {e}")
        return None


def send_email_via_api(to_email, subject, message_body):
    api_key = os.environ.get('BREVO_API_KEY')
    sender_email = os.environ.get('EMAIL_HOST_USER')

    if not api_key:
        try:
            send_mail(subject=subject, message=message_body, from_email=None, recipient_list=[to_email])
        except Exception as e:
            print(f"[ERRO AO ENVIAR EMAIL - SMTP LOCAL] {e}")
        return

    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": api_key,
        "content-type": "application/json",
    }
    payload = {
        "sender": {"name": "Agendia", "email": sender_email},
        "to": [{"email": to_email}],
        "subject": subject,
        "textContent": message_body,
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code >= 400:
            print(f"[ERRO AO ENVIAR EMAIL - API] {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[ERRO AO ENVIAR EMAIL - API] {e}")


@shared_task
def send_confirmation_notification(appointment_id):
    from .models import Appointment
    try:
        appointment = Appointment.objects.get(id=appointment_id)
    except Appointment.DoesNotExist:
        return f"Appointment {appointment_id} não encontrado."

    local_start = timezone.localtime(appointment.start_time)

    message = (
        f"Olá {appointment.client_name}! Seu agendamento em "
        f"{appointment.business.name} foi confirmado para "
        f"{local_start.strftime('%d/%m/%Y às %H:%M')}."
    )

    send_whatsapp_message(appointment.client_phone, message)

    if appointment.client_email:
        send_email_via_api(
            appointment.client_email,
            f'Agendamento confirmado - {appointment.business.name}',
            message,
        )

    return f"Notificação enviada para {appointment.client_name}"


@shared_task
def send_pending_reminders():
    from .models import Appointment

    now = timezone.now()
    window_end = now + timedelta(hours=24)

    appointments = Appointment.objects.filter(
        start_time__gte=now,
        start_time__lte=window_end,
        reminder_sent=False,
        status__in=[Appointment.Status.PENDING, Appointment.Status.CONFIRMED],
    )

    count = 0
    for appointment in appointments:
        local_start = timezone.localtime(appointment.start_time)
        quando = "hoje" if local_start.date() == timezone.localtime(now).date() else "amanhã"

        message = (
            f"Olá {appointment.client_name}! Lembrete: você tem um agendamento em "
            f"{appointment.business.name} {quando}, dia {local_start.strftime('%d/%m às %H:%M')}."
        )

        send_whatsapp_message(appointment.client_phone, message)

        if appointment.client_email:
            send_email_via_api(
                appointment.client_email,
                f'Lembrete de agendamento - {appointment.business.name}',
                message,
            )

        appointment.reminder_sent = True
        appointment.save(update_fields=['reminder_sent'])
        count += 1

    return f"{count} lembrete(s) processado(s)."


@shared_task
def send_cancellation_notification(appointment_id):
    from .models import Appointment
    try:
        appointment = Appointment.objects.get(id=appointment_id)
    except Appointment.DoesNotExist:
        return f"Appointment {appointment_id} não encontrado."

    local_start = timezone.localtime(appointment.start_time)

    message = (
        f"Olá {appointment.client_name}, informamos que seu agendamento em "
        f"{appointment.business.name} para {local_start.strftime('%d/%m/%Y às %H:%M')} "
        f"foi cancelado. Qualquer dúvida, entre em contato com o estabelecimento."
    )

    send_whatsapp_message(appointment.client_phone, message)

    if appointment.client_email:
        send_email_via_api(
            appointment.client_email,
            f'Agendamento cancelado - {appointment.business.name}',
            message,
        )

    return f"Notificação de cancelamento enviada para {appointment.client_name}"