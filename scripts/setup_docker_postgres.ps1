[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$envPath = Join-Path $projectRoot ".env"
$examplePath = Join-Path $projectRoot ".env.example"

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

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "Docker CLI no está instalado."
}

docker info *> $null
if ($LASTEXITCODE -ne 0) {
    throw "Docker Desktop no está iniciado. Ábrelo y espera hasta que el motor esté listo."
}

if (-not (Test-Path -LiteralPath $envPath -PathType Leaf)) {
    Copy-Item -LiteralPath $examplePath -Destination $envPath
}

$currentEnv = Get-Content -LiteralPath $envPath -Raw
if ($currentEnv -match "POSTGRES_PASSWORD=replace-with-a-local-password") {
    $databasePassword = New-RandomSecret 32
    $djangoSecret = New-RandomSecret 48
    $currentEnv = $currentEnv -replace "DJANGO_SECRET_KEY=replace-with-a-local-secret", "DJANGO_SECRET_KEY=$djangoSecret"
    $currentEnv = $currentEnv -replace "POSTGRES_DB=.*", "POSTGRES_DB=reservas_academicas"
    $currentEnv = $currentEnv -replace "POSTGRES_USER=.*", "POSTGRES_USER=reservas_app"
    $currentEnv = $currentEnv -replace "POSTGRES_PASSWORD=replace-with-a-local-password", "POSTGRES_PASSWORD=$databasePassword"
    $currentEnv = $currentEnv -replace "POSTGRES_HOST=.*", "POSTGRES_HOST=localhost"
    $currentEnv = $currentEnv -replace "POSTGRES_PORT=.*", "POSTGRES_PORT=5433"
    Set-Content -LiteralPath $envPath -Value $currentEnv -Encoding UTF8
}

Push-Location $projectRoot
try {
    docker compose up -d postgres
    if ($LASTEXITCODE -ne 0) {
        throw "No fue posible iniciar PostgreSQL 17 en Docker."
    }

    $healthy = $false
    for ($attempt = 1; $attempt -le 24; $attempt++) {
        $status = docker inspect --format "{{.State.Health.Status}}" reservas-academicas-db 2>$null
        if ($status -eq "healthy") {
            $healthy = $true
            break
        }
        Start-Sleep -Seconds 2
    }
    if (-not $healthy) {
        throw "PostgreSQL no alcanzó el estado saludable dentro del tiempo esperado."
    }

    docker compose exec -T postgres psql -U reservas_app -d reservas_academicas -c "SELECT current_database(), current_user;"
    if ($LASTEXITCODE -ne 0) {
        throw "El contenedor inició, pero falló la verificación de conexión."
    }

    Write-Host "PostgreSQL 17 en Docker quedó listo y .env fue configurado sin mostrar credenciales." -ForegroundColor Green
}
finally {
    Pop-Location
}

