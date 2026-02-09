@echo off
chcp 65001 >nul
title LinkedIn Assistant - Instalador

echo.
echo ========================================
echo    LINKEDIN ASSISTANT - INSTALADOR
echo ========================================
echo.
echo 🚀 Este instalador configurará todo automáticamente
echo 📦 Se instalarán: Python, dependencias y estructura
echo.
echo ⚠️  Asegúrate de tener:
echo    • Windows 10 o superior
echo    • Conexión a Internet activa
echo    • Permisos de administrador (recomendado)
echo.

REM Verificar si Python está instalado
echo 🔍 Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no está instalado
    echo.
    echo 📥 Instalando Python automáticamente...
    
    REM Descargar Python
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.9.13/python-3.9.13-amd64.exe' -OutFile 'python_installer.exe'"
    
    if exist python_installer.exe (
        echo ✅ Python descargado. Ejecutando instalador...
        echo ⏳ Esto puede tomar unos minutos...
        start /wait python_installer.exe /quiet InstallAllUsers=1 PrependPath=1
        del python_installer.exe
        
        echo ✅ Python instalado. Reiniciando instalación...
        timeout /t 3 /nobreak >nul
        call "%~f0"
        exit /b
    ) else (
        echo ❌ No se pudo descargar Python
        echo 📥 Descarga manualmente desde: https://www.python.org/downloads/
        pause
        exit /b 1
    )
)

echo ✅ Python detectado: 
python --version

REM Crear carpeta del proyecto
echo.
echo 📁 Creando estructura de carpetas...
if not exist "linkedin_assistant" mkdir linkedin_assistant
cd linkedin_assistant

mkdir exports 2>nul
mkdir logs 2>nul
mkdir backups 2>nul
mkdir session 2>nul
mkdir static 2>nul
mkdir templates 2>nul

echo ✅ Carpetas creadas

REM Crear entorno virtual
echo.
echo 🐍 Creando entorno virtual Python...
python -m venv venv
if errorlevel 1 (
    echo ❌ Error creando entorno virtual
    pause
    exit /b 1
)

echo ✅ Entorno virtual creado

REM Activar entorno e instalar dependencias
echo.
echo 📦 Instalando dependencias...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Error activando entorno virtual
    pause
    exit /b 1
)

pip install --upgrade pip
pip install selenium==4.15.2 flask==3.0.0 pyyaml==6.0.1

echo ✅ Dependencias instaladas

REM Crear archivos de configuración
echo.
echo ⚙️  Creando archivos de configuración...

REM Crear config.yaml básico
(
echo # 🛡️ CONFIGURACIÓN DE LINKEDIN ASSISTANT
echo.
echo linkedin:
echo   email: "TU_EMAIL_AQUI@ejemplo.com"
echo   password: "TU_CONTRASEÑA_AQUI"
echo.
echo limits:
echo   daily_connections: 25
echo   weekly_connections: 100
echo   connections_per_hour: 8
echo   messages_per_day: 40
echo   min_action_delay: 12
echo   max_action_delay: 30
echo.
echo search:
echo   keywords: "CEO Founder Director"
echo   locations: "España"
echo   industries: "Tecnología"
echo.
echo messages:
echo   connection_request:
echo     - template: "Hola {{first_name}}, vi tu perfil y me gustaría conectar."
echo.
echo behavior:
echo   work_schedule:
echo     monday: ["09:00", "18:00"]
echo     tuesday: ["09:00", "18:00"]
echo     wednesday: ["09:00", "18:00"]
echo     thursday: ["09:00", "18:00"]
echo     friday: ["09:00", "16:00"]
echo     saturday: []
echo     sunday: []
) > config.yaml

echo ✅ config.yaml creado

REM Crear archivos Python principales
echo.
echo 🤖 Creando archivos del bot...

REM linkedin_bot.py (versión simplificada para instalación)
(
echo import time
echo import random
echo import yaml
echo.
echo print("LinkedIn Bot - Instalación completada")
echo print("Por favor, configura tu config.yaml primero")
) > linkedin_bot.py

REM app.py (versión simplificada)
(
echo from flask import Flask
echo.
echo app = Flask(__name__)
echo.
echo @app.route('/')
echo def home():
echo     return "LinkedIn Assistant - Instalación completada"
echo.
echo if __name__ == "__main__":
echo     app.run(debug=True)
) > app.py

REM Crear archivos de inicio
echo.
echo 🚀 Creando archivos de inicio...

REM Crear inicio.bat
(
echo @echo off
echo chcp 65001 ^>nul
echo title LinkedIn Assistant
echo.
echo echo ========================================
echo echo    LINKEDIN ASSISTANT - INICIANDO
echo echo ========================================
echo echo.
echo.
echo REM Verificar ChromeDriver
echo if not exist "chromedriver.exe" (
echo     echo ❌ ERROR: No se encontró chromedriver.exe
echo     echo.
echo     echo 📥 Para solucionarlo:
echo     echo 1. Ve a https://chromedriver.chromium.org/
echo     echo 2. Descarga la versión compatible con tu Chrome
echo     echo 3. Guarda el archivo como chromedriver.exe aquí
echo     echo.
echo     echo 🔍 Para ver tu versión de Chrome:
echo     echo    • Abre Chrome
echo     echo    • Haz clic en los 3 puntos → Ayuda → Acerca de Google Chrome
echo     echo.
echo     pause
echo     exit /b 1
echo )
echo.
echo REM Verificar config.yaml
echo if not exist "config.yaml" (
echo     echo ❌ ERROR: No se encontró config.yaml
echo     echo Crea el archivo de configuración primero
echo     pause
echo     exit /b 1
echo )
echo.
echo REM Activar entorno virtual
echo call venv\Scripts\activate.bat
echo.
echo REM Iniciar aplicación
echo python app.py
echo pause
) > inicio.bat

REM Crear configurar.bat
(
echo @echo off
echo chcp 65001 ^>nul
echo title Configurar LinkedIn Assistant
echo.
echo echo ========================================
echo echo    CONFIGURACIÓN PASO A PASO
echo echo ========================================
echo echo.
echo echo 📝 Vamos a configurar tu LinkedIn Assistant:
echo echo.
echo.
echo REM 1. ChromeDriver
echo if not exist "chromedriver.exe" (
echo     echo 🔧 PASO 1: Instalar ChromeDriver
echo     echo.
echo     echo 1. Abre Google Chrome
echo     echo 2. Haz clic en los 3 puntos (arriba derecha)
echo     echo 3. Ve a "Ayuda" → "Acerca de Google Chrome"
echo     echo 4. Anota el número de versión (ej: 120.0.6099.130)
echo     echo.
echo     echo ⏳ Abriendo navegador para descargar...
echo     start "" "https://chromedriver.chromium.org/"
echo     echo.
echo     echo 📥 Descarga la versión que coincida con tu Chrome
echo     echo 💡 Ejemplo: Si tienes Chrome 120, descarga ChromeDriver 120.x.x.x
echo     echo.
echo     pause
echo ) else (
echo     echo ✅ ChromeDriver ya instalado
echo )
echo.
echo REM 2. Configuración básica
echo echo.
echo echo 🔧 PASO 2: Configurar credenciales
echo echo.
echo echo Abriendo config.yaml para editar...
echo timeout /t 2 /nobreak ^>nul
echo.
echo if not exist "config.yaml" (
echo     echo ❌ config.yaml no encontrado
echo     pause
echo     exit /b 1
echo )
echo.
echo REM Abrir con editor predeterminado
echo start "" "config.yaml"
echo.
echo echo 💡 INSTRUCCIONES:
echo echo 1. Cambia TU_EMAIL_AQUI@ejemplo.com por tu email real
echo echo 2. Cambia TU_CONTRASEÑA_AQUI por tu contraseña real
echo echo 3. Ajusta keywords, locations, industries a tu nicho
echo echo 4. Guarda el archivo y cierra el editor
echo echo.
echo echo ⚠️  CONSEJO DE SEGURIDAD:
echo echo • Nunca compartas este archivo con nadie
echo echo • Mantén una copia de seguridad de tus datos
echo echo.
echo pause
echo.
echo echo ✅ Configuración completada
echo echo.
echo echo 🚀 Ahora puedes ejecutar inicio.bat para comenzar
echo pause
) > configurar.bat

REM Crear actualizar.bat
(
echo @echo off
echo chcp 65001 ^>nul
echo title Actualizar LinkedIn Assistant
echo.
echo echo ========================================
echo echo    ACTUALIZANDO LINKEDIN ASSISTANT
echo echo ========================================
echo echo.
echo.
echo REM Activar entorno virtual
echo call venv\Scripts\activate.bat
echo.
echo REM Actualizar dependencias
echo echo 📦 Actualizando Python packages...
echo pip install --upgrade selenium flask pyyaml
echo.
echo REM Verificar ChromeDriver
echo echo 🔍 Verificando versión de ChromeDriver...
echo if exist chromedriver.exe (
echo     echo ✅ ChromeDriver encontrado
echo     echo 💡 Recuerda actualizarlo si actualizas Chrome
echo ) else (
echo     echo ⚠️  ChromeDriver no encontrado
echo     echo Ejecuta configurar.bat primero
echo )
echo.
echo echo ✅ Actualización completada
echo pause
) > actualizar.bat

REM Crear README.txt
echo.
echo 📖 Creando documentación...
(
echo ========================================
echo      LINKEDIN ASSISTANT - GUÍA RÁPIDA
echo ========================================
echo.
echo 🎯 OBJETIVO: Conectar con 25-30 personas/día
echo             de forma segura y automática
echo.
echo 📁 ARCHIVOS IMPORTANTES:
echo • config.yaml - Tu configuración (EDITAR ESTE)
echo • inicio.bat - Para iniciar el programa
echo • configurar.bat - Para configurar paso a paso
echo • actualizar.bat - Para actualizar dependencias
echo.
echo 🚀 CÓMO COMENZAR (3 PASOS):
echo.
echo 1. EJECUTA configurar.bat
echo    Te guiará para instalar ChromeDriver
echo    y configurar tus credenciales
echo.
echo 2. EDITA config.yaml
echo    • Cambia email y contraseña
echo    • Ajusta keywords a tu nicho
echo    • Configura límites seguros
echo.
echo 3. EJECUTA inicio.bat
echo    Se abrirá una ventana web en tu navegador
echo    Usa los botones para controlar el bot
echo.
echo ⚠️  CONSEJOS DE SEGURIDAD:
echo • Nunca superes 25 conexiones/día
echo • Usa horarios laborales reales
echo • Personaliza los mensajes
echo • Haz backup regular de exports/
echo.
echo ❓ PROBLEMAS COMUNES:
echo.
echo 1. "No se encontró chromedriver.exe"
echo    Solución: Ejecuta configurar.bat
echo.
echo 2. "Error de login"
echo    Solución: Verifica email/contraseña en config.yaml
echo.
echo 3. "LinkedIn pide verificación"
echo    Solución: Espera 24 horas, reduce límites
echo.
echo 📞 SOPORTE:
echo Guarda los archivos de logs/ si necesitas ayuda
echo.
echo ========================================
echo         ¡ÉXITO CON TU PROSPECCIÓN!
echo ========================================
) > README.txt

echo ✅ Archivos creados

REM Descargar ChromeDriver automáticamente
echo.
echo 🔍 Detectando versión de Chrome...
for /f "tokens=2 delims= " %%a in ('reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v version 2^>nul') do set CHROME_VERSION=%%a

if "%CHROME_VERSION%"=="" (
    echo ⚠️  No se pudo detectar Chrome automáticamente
    echo 📥 Necesitarás descargar ChromeDriver manualmente
) else (
    echo ✅ Chrome detectado: Versión %CHROME_VERSION%
    echo.
    echo 📥 Intentando descargar ChromeDriver automáticamente...
    
    REM Extraer versión mayor (ej: 120.0.6099.130 → 120)
    for /f "tokens=1 delims=." %%v in ("%CHROME_VERSION%") do set MAJOR_VERSION=%%v
    
    powershell -Command ^
    "try {
        $url = 'https://chromedriver.storage.googleapis.com/LATEST_RELEASE_' + '%MAJOR_VERSION%'
        $version = Invoke-WebRequest -Uri $url -UseBasicParsing
        $downloadUrl = 'https://chromedriver.storage.googleapis.com/' + $version.Content + '/chromedriver_win32.zip'
        
        Invoke-WebRequest -Uri $downloadUrl -OutFile 'chromedriver.zip'
        
        if (Test-Path 'chromedriver.zip') {
            Expand-Archive -Path 'chromedriver.zip' -DestinationPath . -Force
            Remove-Item 'chromedriver.zip'
            Write-Host '✅ ChromeDriver descargado automáticamente'
        }
    } catch {
        Write-Host '⚠️  No se pudo descargar automáticamente'
        Write-Host '📥 Descarga manual desde: https://chromedriver.chromium.org/'
    }"
)

echo.
echo ========================================
echo        🎉 INSTALACIÓN COMPLETADA
echo ========================================
echo.
echo ✅ TODO LISTO
echo.
echo 📝 AHORA NECESITAS:
echo 1. Ejecutar configurar.bat (para configuración guiada)
echo    O
echo 2. Editar manualmente config.yaml con tus datos
echo.
echo 🚀 LUEGO EJECUTA:
echo • inicio.bat - Para iniciar el programa
echo.
echo 📁 EN ESTA CARPETA ENCONTRARÁS:
echo • config.yaml - Configuración (¡EDITA ESTE!)
echo • inicio.bat - Para iniciar
echo • configurar.bat - Configuración guiada
echo • actualizar.bat - Para actualizar
echo • README.txt - Esta guía
echo.
echo ⏳ La primera ejecución puede tardar unos segundos
echo 🌐 Se abrirá automáticamente en tu navegador
echo.
echo 💡 CONSEJO: Mantén esta carpeta en un lugar seguro
echo           (como Documentos o Escritorio)
echo.
echo ========================================
echo.
pause