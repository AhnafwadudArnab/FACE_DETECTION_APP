# Object Detection System - PowerShell Runner
# This script ensures the correct Python environment is used

param(
    [Parameter(Position=0)]
    [string]$Command,
    
    [Parameter(Position=1)]
    [string]$Path
)

$PythonExe = "C:/flutter/projects/Ai models/.venv/Scripts/python.exe"
$ScriptDir = "C:\flutter\projects\Ai models\Models\Objects"

Write-Host "Object Detection System - PowerShell Runner" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

# Change to script directory
Set-Location $ScriptDir

switch ($Command) {
    "test" {
        Write-Host "Running test suite..." -ForegroundColor Yellow
        & $PythonExe test_object_detection.py
    }
    "demo" {
        Write-Host "Starting real-time detection demo..." -ForegroundColor Yellow
        & $PythonExe object_detection_demo.py
    }
    "camera-test" {
        Write-Host "Testing camera access..." -ForegroundColor Yellow
        & $PythonExe object_detection_demo.py --mode test
    }
    "image" {
        if (-not $Path) {
            Write-Host "Error: Please provide image path" -ForegroundColor Red
            Write-Host "Usage: .\run.ps1 image 'path/to/image.jpg'" -ForegroundColor Yellow
        } else {
            Write-Host "Processing image: $Path" -ForegroundColor Yellow
            & $PythonExe object_detection_demo.py --mode image --image $Path
        }
    }
    "batch" {
        if (-not $Path) {
            Write-Host "Processing sample images from dataset..." -ForegroundColor Yellow
            & $PythonExe object_detection_demo.py --mode batch --folder "../../DataSets/object dataset/Images"
        } else {
            Write-Host "Processing images from folder: $Path" -ForegroundColor Yellow
            & $PythonExe object_detection_demo.py --mode batch --folder $Path
        }
    }
    default {
        Write-Host "Usage: .\run.ps1 [command] [options]" -ForegroundColor White
        Write-Host ""
        Write-Host "Commands:" -ForegroundColor Green
        Write-Host "  test         - Run unit tests" -ForegroundColor White
        Write-Host "  demo         - Start real-time detection" -ForegroundColor White
        Write-Host "  camera-test  - Test camera access" -ForegroundColor White
        Write-Host "  image 'path' - Process single image" -ForegroundColor White
        Write-Host "  batch [dir]  - Process multiple images" -ForegroundColor White
        Write-Host ""
        Write-Host "Examples:" -ForegroundColor Green
        Write-Host "  .\run.ps1 test" -ForegroundColor Gray
        Write-Host "  .\run.ps1 demo" -ForegroundColor Gray
        Write-Host "  .\run.ps1 camera-test" -ForegroundColor Gray
        Write-Host "  .\run.ps1 image 'sample.jpg'" -ForegroundColor Gray
        Write-Host "  .\run.ps1 batch" -ForegroundColor Gray
        Write-Host "  .\run.ps1 batch 'C:\path\to\images'" -ForegroundColor Gray
    }
}