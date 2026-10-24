from django import forms
from django.utils import timezone

from .models import Espacio, HorarioEspacio
from .services import validar_cambio_horario


class EspacioForm(forms.ModelForm):
    class Meta:
        model = Espacio
        fields = (
            "nombre",
            "tipo",
            "ubicacion",
            "capacidad",
            "caracteristicas",
            "activo",
        )

    def clean_capacidad(self):
        capacidad = self.cleaned_data["capacidad"]
        if capacidad <= 0:
            raise forms.ValidationError("La capacidad debe ser mayor que cero.")
        return capacidad

    def clean(self):
        cleaned = super().clean()
        if (
            self.instance.pk
            and self.instance.activo
            and cleaned.get("activo") is False
            and self.instance.reservas.filter(
                estado="APROBADA", inicio__gt=timezone.now()
            ).exists()
        ):
            raise forms.ValidationError(
                "El espacio tiene reservas futuras aprobadas; deben cancelarse antes de desactivarlo."
            )
        return cleaned


class HorarioEspacioForm(forms.ModelForm):
    class Meta:
        model = HorarioEspacio
        fields = ("dia_semana", "hora_inicio", "hora_fin")
        widgets = {
            "hora_inicio": forms.TimeInput(attrs={"type": "time"}),
            "hora_fin": forms.TimeInput(attrs={"type": "time"}),
        }

    def __init__(self, *args, espacio=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.espacio = espacio or (self.instance.espacio if self.instance.pk else None)
        if self.espacio is not None:
            self.instance.espacio = self.espacio

    def clean(self):
        cleaned = super().clean()
        if self.espacio and all(
            cleaned.get(field) is not None
            for field in ("dia_semana", "hora_inicio", "hora_fin")
        ):
            validar_cambio_horario(
                self.espacio,
                horario_propuesto={
                    "dia_semana": cleaned["dia_semana"],
                    "hora_inicio": cleaned["hora_inicio"],
                    "hora_fin": cleaned["hora_fin"],
                },
                horario_excluido_id=self.instance.pk,
            )
        return cleaned


