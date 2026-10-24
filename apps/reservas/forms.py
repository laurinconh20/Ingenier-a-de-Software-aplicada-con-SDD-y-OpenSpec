from django import forms

from apps.espacios.models import Espacio
from apps.usuarios.models import Usuario

from .models import Reserva
from .services import validar_espacio_y_horario, validar_intervalo_temporal


class SolicitudReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ("espacio", "inicio", "fin")
        widgets = {
            "inicio": forms.DateTimeInput(
                attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
            ),
            "fin": forms.DateTimeInput(
                attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["espacio"].queryset = Espacio.objects.filter(activo=True)
        self.fields["inicio"].input_formats = ["%Y-%m-%dT%H:%M"]
        self.fields["fin"].input_formats = ["%Y-%m-%dT%H:%M"]

    def _get_validation_exclusions(self):
        exclusions = super()._get_validation_exclusions()
        # El estado no se expone en el formulario, pero su valor fijo PENDIENTE
        # participa en las condiciones de las restricciones de exclusión.
        exclusions.discard("estado")
        return exclusions


class ConsultaDisponibilidadForm(forms.Form):
    espacio = forms.ModelChoiceField(queryset=Espacio.objects.all())
    inicio = forms.DateTimeField(
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
    )
    fin = forms.DateTimeField(
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
    )

    def clean(self):
        cleaned = super().clean()
        if all(cleaned.get(campo) is not None for campo in ("espacio", "inicio", "fin")):
            validar_intervalo_temporal(cleaned["inicio"], cleaned["fin"])
            validar_espacio_y_horario(
                cleaned["espacio"], cleaned["inicio"], cleaned["fin"]
            )
        return cleaned


class AprobacionForm(forms.Form):
    observacion = forms.CharField(
        required=False,
        max_length=1000,
        widget=forms.Textarea,
    )


class RechazoForm(forms.Form):
    motivo = forms.CharField(max_length=1000, widget=forms.Textarea)

    def clean_motivo(self):
        motivo = self.cleaned_data["motivo"].strip()
        if not motivo:
            raise forms.ValidationError("El motivo es obligatorio.")
        return motivo


class CancelacionPropiaForm(forms.Form):
    motivo = forms.CharField(required=False, max_length=1000, widget=forms.Textarea)


class CancelacionAdministrativaForm(forms.Form):
    motivo = forms.CharField(max_length=1000, widget=forms.Textarea)

    def clean_motivo(self):
        motivo = self.cleaned_data["motivo"].strip()
        if not motivo:
            raise forms.ValidationError("El motivo es obligatorio.")
        return motivo


class HistorialFiltroForm(forms.Form):
    estado = forms.ChoiceField(
        required=False, choices=(("", "Todos"), *Reserva.Estado.choices)
    )
    espacio = forms.ModelChoiceField(
        required=False, queryset=Espacio.objects.all()
    )
    solicitante = forms.ModelChoiceField(
        required=False, queryset=Usuario.objects.all()
    )
    desde = forms.DateField(
        required=False, widget=forms.DateInput(attrs={"type": "date"})
    )
    hasta = forms.DateField(
        required=False, widget=forms.DateInput(attrs={"type": "date"})
    )
    tamano = forms.IntegerField(required=False, min_value=1)
