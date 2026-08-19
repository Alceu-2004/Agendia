from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('agendar/<slug:slug>/', views.public_booking_page, name='public_booking'),
    path('agendar/<slug:slug>/sucesso/', views.booking_success, name='booking_success'),
    path('painel/', views.dashboard, name='dashboard'),
]