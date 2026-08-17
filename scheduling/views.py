from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from datetime import timedelta
from business.models import Business
from .models import Appointment
from .forms import AppointmentForm

@login_required
def dashboard(request):
    business = get_object_or_404(Business, owner=request.user)
    appointments = Appointment.objects.filter(business=business).order_by('start_time')
    return render(request, 'scheduling/dashboard.html', {
        'business': business,
        'appointments': appointments,
    })

def public_booking_page(request, slug):
    business = get_object_or_404(Business, slug=slug)
    services = business.services.all()

    if request.method == 'POST':
        form = AppointmentForm(request.POST, business=business)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.business = business
            appointment.end_time = appointment.start_time + timedelta(
                minutes=appointment.service.duration_minutes
            )
            try:
                appointment.full_clean()
                appointment.save()
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