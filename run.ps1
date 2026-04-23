Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path

$apiEnv = Join-Path $root "apps\api\.env"
$apiEnvExample = Join-Path $root "apps\api\.env.example"
$frontendEnv = Join-Path $root "apps\frontend\.env.local"
$frontendEnvExample = Join-Path $root "apps\frontend\.env.local.example"

if (-not (Test-Path $apiEnv) -and (Test-Path $apiEnvExample)) {
    Copy-Item $apiEnvExample $apiEnv
}

if (-not (Test-Path $frontendEnv) -and (Test-Path $frontendEnvExample)) {
    Copy-Item $frontendEnvExample $frontendEnv
}

Push-Location $root
try {
    docker compose up --build
}
finally {
    Pop-Location
}
