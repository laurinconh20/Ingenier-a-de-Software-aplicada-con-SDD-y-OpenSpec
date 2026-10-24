from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Usuario


class CorreoAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label="Correo institucional",
        widget=forms.EmailInput(attrs={"autocomplete": "email", "autofocus": True}),
    )
    error_messages = {
        "invalid_login": "Las credenciales proporcionadas no son válidas.",
        "inactive": "Las credenciales proporcionadas no son válidas.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {"placeholder": "nombre@universidad.edu.co"}
        )
        self.fields["password"].widget.attrs.update(
            {"placeholder": "Tu contraseña", "autocomplete": "current-password"}
        )


class UsuarioCreateForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ("email", "nombre", "is_active")


class PerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ("nombre",)


class UsuarioAdminUpdateForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ("nombre", "email", "is_active", "groups")
