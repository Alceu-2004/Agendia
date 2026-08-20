from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('agendar/<slug:slug>/', views.public_booking_page, name='public_booking'),
    path('agendar/<slug:slug>/sucesso/', views.booking_success, name='booking_success'),
    path('painel/', views.dashboard, name='dashboard'),
    path('agendamentos/<int:pk>/confirmar/', views.appointment_confirm, name='appointment_confirm'),
    path('agendamentos/<int:pk>/cancelar/', views.appointment_cancel, name='appointment_cancel'),
    path('agendamentos/<int:pk>/excluir/', views.appointment_delete, name='appointment_delete'),
    path('agendamentos/<int:pk>/concluir/', views.appointment_done, name='appointment_done'),
]