# Sistema de reservas de espacios académicos

Aplicación web monolítica modular construida con Python 3.13, Django 5.2 LTS y
PostgreSQL 17. Gestiona espacios, horarios, solicitudes, decisiones, cancelaciones
y trazabilidad. La zona horaria institucional es `America/Bogota`.

## Requisitos locales

- Python 3.13.
- Docker Desktop con Docker Compose.
- PowerShell en Windows.

No se necesita conocer ni modificar la contraseña de un PostgreSQL instalado en el
equipo: el proyecto usa un contenedor aislado publicado en `localhost:5433`.

## Instalación en Windows

Desde la raíz del proyecto:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\scripts\setup_docker_postgres.ps1
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py sync_roles
.\.venv\Scripts\python.exe scripts\check_database.py
```

También se puede hacer doble clic en `Configurar PostgreSQL.cmd`; crea `.env` con
secretos aleatorios, inicia PostgreSQL 17 y comprueba la conexión sin mostrar las
credenciales. El script conserva un `.env` existente y solo sustituye los valores de
ejemplo. `.env` está excluido del control de versiones.

Para crear la primera cuenta administrativa:

```powershell
.\.venv\Scripts\python.exe manage.py createsuperuser
```

Luego inicia la aplicación:

```powershell
.\.venv\Scripts\python.exe manage.py runserver
```

Abre `http://127.0.0.1:8000/`. La administración funcional de usuarios está en
`/usuarios/administrar/`, los espacios en `/espacios/`, las solicitudes en
`/reservas/` y el historial global autorizado en `/reservas/historial/`.

## Variables de entorno

Copia `.env.example` a `.env` solo si no usas el script automático. Debes reemplazar
los dos valores `replace-with-...` y nunca publicar el archivo resultante.

| Variable | Uso |
|---|---|
| `DJANGO_SETTINGS_MODULE` | Configuración; localmente `config.settings.development` |
| `DJANGO_SECRET_KEY` | Secreto propio de la instalación |
| `DJANGO_DEBUG` | `true` solo en desarrollo |
| `DJANGO_ALLOWED_HOSTS` | Hosts aceptados separados por coma |
| `POSTGRES_DB` | Base de datos, por defecto `reservas_academicas` |
| `POSTGRES_USER` | Usuario de aplicación, por defecto `reservas_app` |
| `POSTGRES_PASSWORD` | Contraseña local generada o definida por el operador |
| `POSTGRES_HOST` | `localhost` al ejecutar Django fuera de Docker |
| `POSTGRES_PORT` | `5433` para no interferir con PostgreSQL local |

## Roles

`migrate` crea las tablas y la señal posterior sincroniza los grupos. El comando
idempotente `manage.py sync_roles` permite repetirlo explícitamente:

- `Solicitante`: crea, consulta y cancela sus propias solicitudes.
- `Gestor de espacios`: decide/cancela solicitudes y consulta el historial global.
- `Administrador`: suma gestión de usuarios, espacios y horarios.

Un superusuario puede asignar estos grupos desde `/admin/`, o un Administrador desde
la pantalla funcional de usuarios.

## Pruebas y cobertura

La suite usa una base de prueba PostgreSQL y contiene pruebas unitarias, de
integración, funcionales, seguridad y concurrencia real:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pytest --cov=apps --cov-report=term-missing -q
```

Resultado de referencia de esta entrega: 218 pruebas aprobadas y 96,79 % de cobertura
global. La prueba concurrente abre conexiones independientes y comprueba que una
carrera nunca deja dos reservas aprobadas incompatibles.

## Operación de PostgreSQL

```powershell
docker compose up -d postgres
docker compose ps
docker compose logs postgres
docker compose stop postgres
```

`docker compose down` elimina el contenedor y la red, pero conserva el volumen de
datos mientras no se use la opción `--volumes`.

Si el puerto 5433 ya está ocupado, elige otro en `.env`, reinicia el contenedor y usa
el mismo valor para Django. Si cambia la contraseña después de que el volumen fue
creado, PostgreSQL conservará la credencial original; en ese caso restaura el valor
anterior o crea deliberadamente una instalación nueva respaldando antes los datos.
