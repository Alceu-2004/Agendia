from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Business, Service
from .forms import ServiceForm


@login_required
def service_list(request):
    business = get_object_or_404(Business, owner=request.user)
    services = business.services.all()
    return render(request, 'business/service_list.html', {
        'business': business,
        'services': services,
    })


@login_required
def service_create(request):
    business = get_object_or_404(Business, owner=request.user)
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.business = business
            service.save()
            return redirect('service_list')
    else:
        form = ServiceForm()
    return render(request, 'business/service_form.html', {'form': form, 'action': 'Criar'})


@login_required
def service_edit(request, pk):
    business = get_object_or_404(Business, owner=request.user)
    service = get_object_or_404(Service, pk=pk, business=business)
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            return redirect('service_list')
    else:
        form = ServiceForm(instance=service)
    return render(request, 'business/service_form.html', {'form': form, 'action': 'Editar'})


@login_required
def service_delete(request, pk):
    business = get_object_or_404(Business, owner=request.user)
    service = get_object_or_404(Service, pk=pk, business=business)
    if request.method == 'POST':
        service.delete()
        return redirect('service_list')
    return render(request, 'business/service_confirm_delete.html', {'service': service})