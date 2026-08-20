from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from datetime import timedelta
from business.models import Business
from .models import Appointment
from .forms import AppointmentForm
from .tasks import send_confirmation_notification
from django.urls import reverse
from django.contrib import messages
from .tasks import send_confirmation_notification, send_cancellation_notification

def home(request):
    return render(request, 'scheduling/home.html')


@login_required
def dashboard(request):
    business = get_object_or_404(Business, owner=request.user)
    appointments = Appointment.objects.filter(business=business).order_by('start_time')
    public_url = request.build_absolute_uri(
        reverse('public_booking', kwargs={'slug': business.slug})
    )
    return render(request, 'scheduling/dashboard.html', {
        'business': business,
        'appointments': appointments,
        'public_url': public_url,
    })

from django.contrib import messages


@login_required
def appointment_confirm(request, pk):
    business = get_object_or_404(Business, owner=request.user)
    appointment = get_object_or_404(Appointment, pk=pk, business=business)
    appointment.status = Appointment.Status.CONFIRMED
    appointment.save(update_fields=['status'])
    messages.success(request, f'Agendamento de {appointment.client_name} confirmado.')
    return redirect('dashboard')


@login_required
def appointment_cancel(request, pk):
    business = get_object_or_404(Business, owner=request.user)
    appointment = get_object_or_404(Appointment, pk=pk, business=business)
    appointment.status = Appointment.Status.CANCELLED
    appointment.save(update_fields=['status'])
    send_cancellation_notification.delay(appointment.id)
    messages.success(request, f'Agendamento de {appointment.client_name} cancelado.')
    return redirect('dashboard')


@login_required
def appointment_delete(request, pk):
    business = get_object_or_404(Business, owner=request.user)
    appointment = get_object_or_404(Appointment, pk=pk, business=business)
    if request.method == 'POST':
        appointment.delete()
        messages.success(request, 'Agendamento excluído.')
        return redirect('dashboard')
    return render(request, 'scheduling/appointment_confirm_delete.html', {'appointment': appointment})

@login_required
def appointment_done(request, pk):
    business = get_object_or_404(Business, owner=request.user)
    appointment = get_object_or_404(Appointment, pk=pk, business=business)
    appointment.status = Appointment.Status.DONE
    appointment.save(update_fields=['status'])
    messages.success(request, f'Agendamento de {appointment.client_name} marcado como concluído.')
    return redirect('dashboard')

def public_booking_page(request, slug):
    business = get_object_or_404(Business, slug=slug)
    services = business.services.all()

    if request.method == 'POST':
        form = AppointmentForm(request.POST, business=business)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.business = business
            appointment.start_time = form.get_start_time()
            appointment.end_time = appointment.start_time + timedelta(
                minutes=appointment.service.duration_minutes
            )
            try:
                appointment.full_clean()
                appointment.save()
                send_confirmation_notification.delay(appointment.id)
                return redirect('booking_success', slug=business.slug)
            except ValidationError as e:
                form.add_error(None, e)
    else:
        form = AppointmentForm(business=business)

    return render(request, 'scheduling/booking.html', {
        'business': business,
        'services': services,
        'form': form,
    })


def booking_success(request, slug):
    business = get_object_or_404(Business, slug=slug)
    return render(request, 'scheduling/booking_success.html', {'business': business})