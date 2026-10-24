from django.contrib import admin

from .models import Espacio, HorarioEspacio


class HorarioInline(admin.TabularInline):
    model = HorarioEspacio
    extra = 1


@admin.register(Espacio)
class EspacioAdmin(admin.ModelAdmin):
    list_display = ("nombre", "tipo", "ubicacion", "capacidad", "activo")
    list_filter = ("tipo", "activo")
    search_fields = ("nombre", "ubicacion")
    inlines = (HorarioInline,)

