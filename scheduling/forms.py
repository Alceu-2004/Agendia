from django import forms
from django.utils import timezone
from datetime import datetime
from .models import Appointment


class AppointmentForm(forms.ModelForm):
    date = forms.DateField(
        label='Data',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    time = forms.TimeField(
        label='Horário',
        widget=forms.TimeInput(attrs={'type': 'time', 'step': 1800, 'class': 'form-control'})
    )

    class Meta:
        model = Appointment
        fields = ['service', 'client_name', 'client_phone', 'client_email']

    def __init__(self, *args, business=None, **kwargs):
        super().__init__(*args, **kwargs)
        if business:
            self.fields['service'].queryset = business.services.all()
        for field_name, field in self.fields.items():
            if field_name not in ('date', 'time'):
                field.widget.attrs['class'] = 'form-control'

    def clean_time(self):
        time = self.cleaned_data['time']
        if time.minute not in (0, 30):
            raise forms.ValidationError('O horário deve ser em intervalos de 30 minutos (ex: 09:00, 09:30).')
        return time

    def get_start_time(self):
        """Combina data + hora validadas num único datetime."""
        date = self.cleaned_data['date']
        time = self.cleaned_data['time']
        naive_datetime = datetime.combine(date, time)
        return timezone.make_aware(naive_datetime)