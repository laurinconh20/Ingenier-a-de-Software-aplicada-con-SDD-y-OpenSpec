from django.urls import path

from .views import (
    DisponibilidadView,
    AprobarView,
    CancelarPropiaView,
    CancelarAdministrativaView,
    DecisionDetailView,
    HistorialGlobalView,
    RechazarView,
    SolicitudCreateView,
    SolicitudDetailView,
    SolicitudListView,
)

app_name = "reservas"
urlpatterns = [
    path("", SolicitudListView.as_view(), name="list"),
    path("disponibilidad/", DisponibilidadView.as_view(), name="availability"),
    path("historial/", HistorialGlobalView.as_view(), name="global-history"),
    path("nueva/", SolicitudCreateView.as_view(), name="create"),
    path("<int:pk>/decision/", DecisionDetailView.as_view(), name="decision"),
    path("<int:pk>/aprobar/", AprobarView.as_view(), name="approve"),
    path("<int:pk>/rechazar/", RechazarView.as_view(), name="reject"),
    path("<int:pk>/cancelar/", CancelarPropiaView.as_view(), name="cancel-own"),
    path(
        "<int:pk>/cancelar-administrativamente/",
        CancelarAdministrativaView.as_view(),
        name="cancel-admin",
    ),
    path("<int:pk>/", SolicitudDetailView.as_view(), name="detail"),
]

