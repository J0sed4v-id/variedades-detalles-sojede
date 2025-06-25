# usuarios/forms.py
from django import forms
from .models import Habitacion
from .models import Reserva
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date

class CustomUserCreationForm(forms.ModelForm):
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput)
    
    class Meta:
        model = User
        fields = ["username", "email"]
    
    def clean_password(self):
        password = self.cleaned_data.get("password")
        if not password or len(password) < 8:
            raise ValidationError("La contraseña debe tener al menos 8 caracteres.")
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class BuscarHabitacionForm(forms.Form):
    check_in = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'min': timezone.now().date().isoformat()}),
        label="Fecha de entrada"
    )
    check_out = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Fecha de salida"
    )

    def clean_check_in(self):
        check_in = self.cleaned_data.get('check_in')
        if check_in < timezone.now().date():
            raise forms.ValidationError("La fecha de entrada no puede ser en el pasado.")
        return check_in

    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get("check_in")
        check_out = cleaned_data.get("check_out")
        
        if check_in and check_out and check_out <= check_in:
            raise forms.ValidationError("La fecha de salida debe ser posterior a la fecha de entrada.")


class HabitacionForm(forms.ModelForm):
    class Meta:
        model = Habitacion
        fields = ['numero', 'tipo', 'capacidad', 'precio_por_noche', 'disponible']


class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['fecha_inicio', 'fecha_fin', 'habitacion']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get("fecha_inicio")
        fecha_fin = cleaned_data.get("fecha_fin")

        # Validación: que las fechas no estén vacías
        if not fecha_inicio or not fecha_fin:
            raise forms.ValidationError("Debes seleccionar ambas fechas.")

        # Validación: que la fecha de inicio no sea en el pasado
        if fecha_inicio < date.today():
            self.add_error('fecha_inicio', "La fecha de check-in no puede ser anterior a hoy.")

        # Validación: que la fecha de fin sea posterior a la de inicio
        if fecha_fin <= fecha_inicio:
            self.add_error('fecha_fin', "La fecha de check-out debe ser posterior a la de check-in.")

