from django.urls import path
from . import views

urlpatterns = [
    path('servicos/', views.service_list, name='service_list'),
    path('servicos/novo/', views.service_create, name='service_create'),
    path('servicos/<int:pk>/editar/', views.service_edit, name='service_edit'),
    path('servicos/<int:pk>/excluir/', views.service_delete, name='service_delete'),
]