from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.text import slugify
from .models import Business, Service


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'duration_minutes', 'price']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


class BusinessSignupForm(UserCreationForm):
    business_name = forms.CharField(
        label='Nome do negócio',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Barbearia do Zé'})
    )
    email = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'seuemail@exemplo.com'})
    )
    whatsapp_number = forms.CharField(
        label='WhatsApp (com DDD)',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '55 32 99999-9999'})
    )
    username = forms.CharField(
        label='Nome de usuário',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Como você vai fazer login'}),
        help_text='Use apenas letras, números e @/./+/-/_'
    )
    password1 = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text='Use pelo menos 8 caracteres, evite senhas muito simples.'
    )
    password2 = forms.CharField(
        label='Confirme a senha',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text='Digite a mesma senha novamente para confirmação.'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_business_name(self):
        name = self.cleaned_data['business_name']
        slug = slugify(name)
        if Business.objects.filter(slug=slug).exists():
            raise forms.ValidationError('Já existe um negócio com um nome muito parecido. Tente outro nome.')
        return name

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.is_staff = False
        user.is_superuser = False
        if commit:
            user.save()
            Business.objects.create(
                owner=user,
                name=self.cleaned_data['business_name'],
                slug=slugify(self.cleaned_data['business_name']),
                whatsapp_number=self.cleaned_data['whatsapp_number'],
                email=self.cleaned_data['email'],
            )
        return user