<#
.SYNOPSIS
Script para iniciar el contenedor de NVIDIA NeMo.
Asegúrate de que Docker Desktop esté corriendo.
#>

$ImageName = "reto-voz-env"

Write-Host "Iniciando el contenedor de NVIDIA NeMo..."
Write-Host "Imagen: $ImageName"
Write-Host "Montando el directorio actual en /workspace..."

# El flag --gpus all requiere que el NVIDIA Container Toolkit esté configurado en WSL2 (por defecto en Docker Desktop)
docker run --gpus all -it --rm `
    --env NVIDIA_DISABLE_REQUIRE=1 `
    --shm-size=8g `
    -p 8080:8000 `
    -v "${PWD}:/workspace" `
    -w /workspace `
    $ImageName bash
