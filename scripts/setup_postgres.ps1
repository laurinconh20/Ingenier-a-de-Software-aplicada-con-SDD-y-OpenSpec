[CmdletBinding()]
param(
    [string]$AdminUser = "postgres",
    [string]$HostName = "localhost",
    [int]$Port = 5432
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$envPath = Join-Path $projectRoot ".env"
$psqlPath = "C:\Program Files\PostgreSQL\17\bin\psql.exe"
$databaseName = "reservas_academicas"
$applicationUser = "reservas_app"

if (-not (Test-Path -LiteralPath $psqlPath -PathType Leaf)) {
    throw "No se encontró psql de PostgreSQL 17 en $psqlPath"
}

if (-not (Test-Path -LiteralPath $envPath -PathType Leaf)) {
    Copy-Item -LiteralPath (Join-Path $projectRoot ".env.example") -Destination $envPath
}

$currentEnv = Get-Content -LiteralPath $envPath -Raw
if ($currentEnv -notmatch "POSTGRES_PASSWORD=replace-with-a-local-password") {
    throw "El archivo .env ya contiene una contraseña no provisional. No se sobrescribió."
}

function New-RandomSecret([int]$ByteCount) {
    $bytes = New-Object byte[] $ByteCount
    $generator = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    try {
        $generator.GetBytes($bytes)
    }
    finally {
        $generator.Dispose()
    }
    return [Convert]::ToBase64String($bytes).TrimEnd("=").Replace("+", "-").Replace("/", "_")
}

$adminSecurePassword = Read-Host "Contraseña local del superusuario PostgreSQL '$AdminUser'" -AsSecureString
$adminPasswordPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($adminSecurePassword)
$adminPassword = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($adminPasswordPointer)
$applicationPassword = New-RandomSecret 32
$djangoSecret = New-RandomSecret 48
$sqlPath = Join-Path ([System.IO.Path]::GetTempPath()) ("reservas-setup-{0}.sql" -f [Guid]::NewGuid())

try {
    $env:PGPASSWORD = $adminPassword

    @'
SELECT format('CREATE ROLE reservas_app LOGIN PASSWORD %L', :'app_password')
WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'reservas_app')
\gexec
ALTER ROLE reservas_app WITH LOGIN PASSWORD :'app_password';
SELECT 'CREATE DATABASE reservas_academicas OWNER reservas_app'
WHERE NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'reservas_academicas')
\gexec
ALTER DATABASE reservas_academicas OWNER TO reservas_app;
'@ | Set-Content -LiteralPath $sqlPath -Encoding UTF8

    & $psqlPath -v ON_ERROR_STOP=1 -h $HostName -p $Port -U $AdminUser -d postgres --set "app_password=$applicationPassword" --file $sqlPath
    if ($LASTEXITCODE -ne 0) {
        throw "PostgreSQL rechazó la operación administrativa."
    }

    $updatedEnv = $currentEnv
    $updatedEnv = $updatedEnv -replace "DJANGO_SECRET_KEY=replace-with-a-local-secret", "DJANGO_SECRET_KEY=$djangoSecret"
    $updatedEnv = $updatedEnv -replace "POSTGRES_DB=.*", "POSTGRES_DB=$databaseName"
    $updatedEnv = $updatedEnv -replace "POSTGRES_USER=.*", "POSTGRES_USER=$applicationUser"
    $updatedEnv = $updatedEnv -replace "POSTGRES_PASSWORD=replace-with-a-local-password", "POSTGRES_PASSWORD=$applicationPassword"
    $updatedEnv = $updatedEnv -replace "POSTGRES_HOST=.*", "POSTGRES_HOST=$HostName"
    $updatedEnv = $updatedEnv -replace "POSTGRES_PORT=.*", "POSTGRES_PORT=$Port"
    Set-Content -LiteralPath $envPath -Value $updatedEnv -Encoding UTF8

    $env:PGPASSWORD = $applicationPassword
    & $psqlPath -w -h $HostName -p $Port -U $applicationUser -d $databaseName -c "SELECT current_database(), current_user;"
    if ($LASTEXITCODE -ne 0) {
        throw "El rol se creó, pero falló la verificación de conexión."
    }

    Write-Host "Base y credenciales de aplicación creadas correctamente." -ForegroundColor Green
    Write-Host "Las credenciales quedaron únicamente en .env y no se mostraron en pantalla."
}
finally {
    Remove-Item Env:PGPASSWORD -ErrorAction SilentlyContinue
    if ($adminPasswordPointer -ne [IntPtr]::Zero) {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($adminPasswordPointer)
    }
    $adminPassword = $null
    $applicationPassword = $null
    if (Test-Path -LiteralPath $sqlPath) {
        Remove-Item -LiteralPath $sqlPath -Force
    }
}
