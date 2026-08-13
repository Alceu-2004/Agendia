from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from business.models import Business, Service
from scheduling.models import Appointment


class AppointmentConflictTests(TestCase):
    def setUp(self):
        self.business = Business.objects.create(
            name="Barbearia do Zé",
            slug="barbearia-do-ze",
            whatsapp_number="5511999999999",
        )
        self.service = Service.objects.create(
            business=self.business,
            name="Corte de cabelo",
            duration_minutes=30,
            price=40.00,
        )
        self.start = timezone.now() + timedelta(days=1)
        self.end = self.start + timedelta(minutes=30)

        Appointment.objects.create(
            business=self.business,
            service=self.service,
            client_name="Cliente Um",
            client_phone="5511988888888",
            start_time=self.start,
            end_time=self.end,
        )

    def test_conflito_de_horario_e_bloqueado(self):
        agendamento_conflitante = Appointment(
            business=self.business,
            service=self.service,
            client_name="Cliente Dois",
            client_phone="5511977777777",
            start_time=self.start + timedelta(minutes=10),
            end_time=self.end + timedelta(minutes=10),
        )
        with self.assertRaises(ValidationError):
            agendamento_conflitante.full_clean()

    def test_horario_sem_conflito_e_permitido(self):
        agendamento_ok = Appointment(
            business=self.business,
            service=self.service,
            client_name="Cliente Três",
            client_phone="5511966666666",
            start_time=self.end,
            end_time=self.end + timedelta(minutes=30),
        )
        agendamento_ok.full_clean()