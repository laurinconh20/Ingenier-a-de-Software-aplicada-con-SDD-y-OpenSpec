from django.contrib import admin
from django.urls import include, path

from .views import DashboardView

urlpatterns = [
    path("", DashboardView.as_view(), name="home"),
    path("admin/", admin.site.urls),
    path("usuarios/", include("apps.usuarios.urls")),
    path("espacios/", include("apps.espacios.urls")),
    path("reservas/", include("apps.reservas.urls")),
    path("auditoria/", include("apps.auditoria.urls")),
]

