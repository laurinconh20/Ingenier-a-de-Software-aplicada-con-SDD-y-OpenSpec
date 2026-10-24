from django.urls import path

from .views import (
    EspacioCreateView,
    EspacioDetailView,
    EspacioListView,
    EspacioUpdateView,
    HorarioCreateView,
    HorarioDeleteView,
    HorarioUpdateView,
)

app_name = "espacios"
urlpatterns = [
    path("", EspacioListView.as_view(), name="list"),
    path("nuevo/", EspacioCreateView.as_view(), name="create"),
    path("<int:pk>/", EspacioDetailView.as_view(), name="detail"),
    path("<int:pk>/editar/", EspacioUpdateView.as_view(), name="update"),
    path("<int:espacio_pk>/horarios/nuevo/", HorarioCreateView.as_view(), name="schedule-create"),
    path("horarios/<int:pk>/editar/", HorarioUpdateView.as_view(), name="schedule-update"),
    path("horarios/<int:pk>/eliminar/", HorarioDeleteView.as_view(), name="schedule-delete"),
]

