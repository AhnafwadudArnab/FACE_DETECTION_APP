@echo off
REM Object Detection System - Easy Run Script
REM This script ensures the correct Python environment is used

echo Object Detection System - Easy Runner
echo ========================================

set PYTHON_PATH="C:/flutter/projects/Ai models/.venv/Scripts/python.exe"
set SCRIPT_DIR="C:\flutter\projects\Ai models\Models\Objects"

cd /d %SCRIPT_DIR%

if "%1"=="test" (
    echo Running test suite...
    %PYTHON_PATH% test_object_detection.py
) else if "%1"=="demo" (
    echo Starting real-time detection demo...
    %PYTHON_PATH% object_detection_demo.py
) else if "%1"=="camera-test" (
    echo Testing camera access...
    %PYTHON_PATH% object_detection_demo.py --mode test
) else if "%1"=="image" (
    if "%2"=="" (
        echo Error: Please provide image path
        echo Usage: run.bat image "path/to/image.jpg"
    ) else (
        echo Processing image: %2
        %PYTHON_PATH% object_detection_demo.py --mode image --image %2
    )
) else if "%1"=="batch" (
    if "%2"=="" (
        echo Processing sample images from dataset...
        %PYTHON_PATH% object_detection_demo.py --mode batch --folder "../../DataSets/object dataset/Images"
    ) else (
        echo Processing images from folder: %2
        %PYTHON_PATH% object_detection_demo.py --mode batch --folder %2
    )
) else (
    echo Usage: run.bat [command] [options]
    echo.
    echo Commands:
    echo   test         - Run unit tests
    echo   demo         - Start real-time detection
    echo   camera-test  - Test camera access
    echo   image "path" - Process single image
    echo   batch [dir]  - Process multiple images
    echo.
    echo Examples:
    echo   run.bat test
    echo   run.bat demo
    echo   run.bat camera-test
    echo   run.bat image "sample.jpg"
    echo   run.bat batch
    echo   run.bat batch "C:\path\to\images"
)

pause