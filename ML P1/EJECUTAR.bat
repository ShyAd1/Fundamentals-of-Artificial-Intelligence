@echo off
REM ============================================================
REM Sistema de Carga y Manipulacion de Datos - Arquitectura MVC
REM Ejecutable para Windows
REM ============================================================

echo.
echo ============================================================
echo   Sistema de Carga y Manipulacion de Datos - IA
echo   Arquitectura MVC con Interfaz Grafica
echo ============================================================
echo.

REM Verificar si Python esta instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado en este sistema.
    echo.
    echo Por favor, instale Python desde: https://www.python.org/downloads/
    echo Asegurese de marcar "Add Python to PATH" durante la instalacion.
    echo.
    pause
    exit /b 1
)

echo [OK] Python detectado correctamente
echo.

REM Verificar e instalar numpy si es necesario
echo Verificando dependencias...
python -c "import numpy" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Instalando numpy...
    python -m pip install numpy
    if errorlevel 1 (
        echo [ERROR] No se pudo instalar numpy.
        echo.
        pause
        exit /b 1
    )
    echo [OK] numpy instalado correctamente
) else (
    echo [OK] numpy ya esta instalado
)

echo.
echo Iniciando aplicacion...
echo.

REM Ejecutar la aplicacion GUI
python main_gui.py

REM Si hay error al ejecutar
if errorlevel 1 (
    echo.
    echo [ERROR] Ocurrio un error al ejecutar la aplicacion.
    echo.
    pause
    exit /b 1
)

exit /b 0
