from django.urls import path

from .views import (
    CerrarSesionView,
    IniciarSesionView,
    PerfilUpdateView,
    UsuarioCreateView,
    UsuarioListView,
    UsuarioUpdateView,
)

app_name = "usuarios"
urlpatterns = [
    path("iniciar-sesion/", IniciarSesionView.as_view(), name="login"),
    path("cerrar-sesion/", CerrarSesionView.as_view(), name="logout"),
    path("perfil/", PerfilUpdateView.as_view(), name="profile"),
    path("administrar/", UsuarioListView.as_view(), name="list"),
    path("administrar/nuevo/", UsuarioCreateView.as_view(), name="create"),
    path("administrar/<int:pk>/", UsuarioUpdateView.as_view(), name="update"),
]

