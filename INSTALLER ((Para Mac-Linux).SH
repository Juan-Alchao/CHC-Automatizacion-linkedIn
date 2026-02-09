#!/bin/bash

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir con colores
print_message() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

clear
echo "========================================"
echo "   LINKEDIN ASSISTANT - INSTALADOR"
echo "========================================"
echo ""
echo "🚀 Este instalador configurará todo automáticamente"
echo "📦 Se instalarán: Python, dependencias y estructura"
echo ""
echo "⚠️  Asegúrate de tener:"
echo "   • MacOS 10.15+ o Linux Ubuntu/Debian"
echo "   • Conexión a Internet activa"
echo "   • Permisos de administrador (sudo)"
echo ""

# Verificar si es Mac o Linux
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="MAC"
    print_message "Sistema detectado: macOS"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="LINUX"
    print_message "Sistema detectado: Linux"
else
    print_error "Sistema operativo no compatible"
    exit 1
fi

# Verificar Python
print_message "Verificando Python..."
if ! command -v python3 &> /dev/null; then
    print_warning "Python3 no está instalado"
    
    if [ "$OS" = "MAC" ]; then
        print_message "Instalando Python con Homebrew..."
        if ! command -v brew &> /dev/null; then
            print_message "Instalando Homebrew primero..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        fi
        brew install python@3.9
    elif [ "$OS" = "LINUX" ]; then
        print_message "Instalando Python con apt..."
        sudo apt update
        sudo apt install -y python3 python3-venv python3-pip
    fi
    
    if ! command -v python3 &> /dev/null; then
        print_error "No se pudo instalar Python"
        print_message "Por favor, instala Python manualmente:"
        print_message "https://www.python.org/downloads/"
        exit 1
    fi
fi

PYTHON_VERSION=$(python3 --version)
print_success "Python detectado: $PYTHON_VERSION"

# Crear carpeta del proyecto
print_message "Creando estructura de carpetas..."
mkdir -p linkedin_assistant
cd linkedin_assistant || exit 1

mkdir -p exports logs backups session static templates

print_success "Carpetas creadas"

# Crear entorno virtual
print_message "Creando entorno virtual Python..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    print_error "Error creando entorno virtual"
    exit 1
fi

print_success "Entorno virtual creado"

# Activar entorno e instalar dependencias
print_message "Instalando dependencias..."
source venv/bin/activate

pip install --upgrade pip
pip install selenium==4.15.2 flask==3.0.0 pyyaml==6.0.1

print_success "Dependencias instaladas"

# Crear archivos de configuración
print_message "Creando archivos de configuración..."

# Crear config.yaml básico
cat > config.yaml << 'EOF'
# 🛡️ CONFIGURACIÓN DE LINKEDIN ASSISTANT

linkedin:
  email: "TU_EMAIL_AQUI@ejemplo.com"
  password: "TU_CONTRASEÑA_AQUI"

limits:
  daily_connections: 25
  weekly_connections: 100
  connections_per_hour: 8
  messages_per_day: 40
  min_action_delay: 12
  max_action_delay: 30

search:
  keywords: "CEO Founder Director"
  locations: "España"
  industries: "Tecnología"

messages:
  connection_request:
    - template: "Hola {{first_name}}, vi tu perfil y me gustaría conectar."

behavior:
  work_schedule:
    monday: ["09:00", "18:00"]
    tuesday: ["09:00", "18:00"]
    wednesday: ["09:00", "18:00"]
    thursday: ["09:00", "18:00"]
    friday: ["09:00", "16:00"]
    saturday: []
    sunday: []
EOF

print_success "config.yaml creado"

# Crear archivos Python principales (simplificados)
cat > linkedin_bot.py << 'EOF'
import time
import random
import yaml

print("LinkedIn Bot - Instalación completada")
print("Por favor, configura tu config.yaml primero")
EOF

cat > app.py << 'EOF'
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "LinkedIn Assistant - Instalación completada"

if __name__ == "__main__":
    app.run(debug=True)
EOF

# Crear scripts de inicio
print_message "Creando scripts de inicio..."

# Crear inicio.sh
cat > inicio.sh << 'EOF'
#!/bin/bash

clear
echo "========================================"
echo "   LINKEDIN ASSISTANT - INICIANDO"
echo "========================================"
echo ""

# Verificar ChromeDriver
if [ ! -f "chromedriver" ] && [ ! -f "chromedriver.exe" ]; then
    echo "❌ ERROR: No se encontró chromedriver"
    echo ""
    echo "📥 Para solucionarlo:"
    echo "1. Ve a https://chromedriver.chromium.org/"
    echo "2. Descarga la versión compatible con tu Chrome"
    echo "3. Guarda el archivo como 'chromedriver' aquí"
    echo ""
    echo "🔍 Para ver tu versión de Chrome:"
    echo "   • Abre Chrome"
    echo "   • Haz clic en los 3 puntos → Ayuda → Acerca de Google Chrome"
    echo ""
    exit 1
fi

# Verificar config.yaml
if [ ! -f "config.yaml" ]; then
    echo "❌ ERROR: No se encontró config.yaml"
    echo "Crea el archivo de configuración primero"
    exit 1
fi

# Dar permisos de ejecución a chromedriver
if [ -f "chromedriver" ]; then
    chmod +x chromedriver
fi

# Activar entorno virtual
source venv/bin/activate

# Iniciar aplicación
python3 app.py
EOF

chmod +x inicio.sh

# Crear configurar.sh
cat > configurar.sh << 'EOF'
#!/bin/bash

clear
echo "========================================"
echo "    CONFIGURACIÓN PASO A PASO"
echo "========================================"
echo ""
echo "📝 Vamos a configurar tu LinkedIn Assistant:"
echo ""

# 1. ChromeDriver
if [ ! -f "chromedriver" ] && [ ! -f "chromedriver.exe" ]; then
    echo "🔧 PASO 1: Instalar ChromeDriver"
    echo ""
    echo "1. Abre Google Chrome"
    echo "2. Haz clic en los 3 puntos (arriba derecha)"
    echo "3. Ve a 'Ayuda' → 'Acerca de Google Chrome'"
    echo "4. Anota el número de versión (ej: 120.0.6099.130)"
    echo ""
    echo "⏳ Abriendo navegador para descargar..."
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        open "https://chromedriver.chromium.org/"
    else
        xdg-open "https://chromedriver.chromium.org/"
    fi
    
    echo ""
    echo "📥 Descarga la versión que coincida con tu Chrome"
    echo "💡 Ejemplo: Si tienes Chrome 120, descarga ChromeDriver 120.x.x.x"
    echo ""
    read -p "Presiona Enter cuando hayas descargado ChromeDriver..."
else
    echo "✅ ChromeDriver ya instalado"
fi

# 2. Configuración básica
echo ""
echo "🔧 PASO 2: Configurar credenciales"
echo ""
echo "Abriendo config.yaml para editar..."

sleep 2

if [ ! -f "config.yaml" ]; then
    echo "❌ config.yaml no encontrado"
    exit 1
fi

# Abrir con editor
if command -v nano &> /dev/null; then
    nano config.yaml
elif command -v vim &> /dev/null; then
    vim config.yaml
else
    echo "💡 INSTRUCCIONES:"
    echo "1. Abre config.yaml con tu editor de texto favorito"
    echo "2. Cambia TU_EMAIL_AQUI@ejemplo.com por tu email real"
    echo "3. Cambia TU_CONTRASEÑA_AQUI por tu contraseña real"
    echo "4. Ajusta keywords, locations, industries a tu nicho"
    echo "5. Guarda el archivo"
    echo ""
    read -p "Presiona Enter cuando hayas editado el archivo..."
fi

echo ""
echo "✅ Configuración completada"
echo ""
echo "🚀 Ahora puedes ejecutar ./inicio.sh para comenzar"
EOF

chmod +x configurar.sh

# Crear actualizar.sh
cat > actualizar.sh << 'EOF'
#!/bin/bash

clear
echo "========================================"
echo "   ACTUALIZANDO LINKEDIN ASSISTANT"
echo "========================================"
echo ""

# Activar entorno virtual
source venv/bin/activate

# Actualizar dependencias
echo "📦 Actualizando Python packages..."
pip install --upgrade selenium flask pyyaml

# Verificar ChromeDriver
echo "🔍 Verificando versión de ChromeDriver..."
if [ -f "chromedriver" ] || [ -f "chromedriver.exe" ]; then
    echo "✅ ChromeDriver encontrado"
    echo "💡 Recuerda actualizarlo si actualizas Chrome"
else
    echo "⚠️  ChromeDriver no encontrado"
    echo "Ejecuta ./configurar.sh primero"
fi

echo ""
echo "✅ Actualización completada"
EOF

chmod +x actualizar.sh

# Crear README
cat > README.txt << 'EOF'
========================================
     LINKEDIN ASSISTANT - GUÍA RÁPIDA
========================================

🎯 OBJETIVO: Conectar con 25-30 personas/día
            de forma segura y automática

📁 ARCHIVOS IMPORTANTES:
• config.yaml - Tu configuración (EDITAR ESTE)
• inicio.sh - Para iniciar el programa
• configurar.sh - Para configurar paso a paso
• actualizar.sh - Para actualizar dependencias

🚀 CÓMO COMENZAR (3 PASOS):

1. EJECUTA ./configurar.sh
   Te guiará para instalar ChromeDriver
   y configurar tus credenciales

2. EDITA config.yaml
   • Cambia email y contraseña
   • Ajusta keywords a tu nicho
   • Configura límites seguros

3. EJECUTA ./inicio.sh
   Se abrirá una ventana web en tu navegador
   Usa los botones para controlar el bot

⚠️  CONSEJOS DE SEGURIDAD:
• Nunca superes 25 conexiones/día
• Usa horarios laborales reales
• Personaliza los mensajes
• Haz backup regular de exports/

❓ PROBLEMAS COMUNES:

1. "chromedriver: command not found"
   Solución: Ejecuta ./configurar.sh

2. "Error de login"
   Solución: Verifica email/contraseña en config.yaml

3. "LinkedIn pide verificación"
   Solución: Espera 24 horas, reduce límites

📞 SOPORTE:
Guarda los archivos de logs/ si necesitas ayuda

========================================
        ¡ÉXITO CON TU PROSPECCIÓN!
========================================
EOF

# Intentar detectar y descargar ChromeDriver automáticamente
print_message "Intentando detectar Chrome..."
if [ "$OS" = "MAC" ]; then
    CHROME_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    if [ -f "$CHROME_PATH" ]; then
        CHROME_VERSION=$("$CHROME_PATH" --version | awk '{print $3}')
    fi
elif [ "$OS" = "LINUX" ]; then
    if command -v google-chrome &> /dev/null; then
        CHROME_VERSION=$(google-chrome --version | awk '{print $3}')
    elif command -v chromium-browser &> /dev/null; then
        CHROME_VERSION=$(chromium-browser --version | awk '{print $2}')
    fi
fi

if [ ! -z "$CHROME_VERSION" ]; then
    MAJOR_VERSION=$(echo $CHROME_VERSION | cut -d. -f1)
    print_success "Chrome detectado: Versión $CHROME_VERSION"
    
    print_message "Intentando descargar ChromeDriver automáticamente..."
    
    # Descargar ChromeDriver
    if [ "$OS" = "MAC" ]; then
        ARCH="mac64"
    elif [ "$OS" = "LINUX" ]; then
        ARCH="linux64"
    fi
    
    VERSION_URL="https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$MAJOR_VERSION"
    LATEST_VERSION=$(curl -s $VERSION_URL)
    
    if [ ! -z "$LATEST_VERSION" ]; then
        DOWNLOAD_URL="https://chromedriver.storage.googleapis.com/$LATEST_VERSION/chromedriver_$ARCH.zip"
        
        curl -L -o chromedriver.zip $DOWNLOAD_URL
        if [ $? -eq 0 ]; then
            unzip -o chromedriver.zip
            rm chromedriver.zip
            chmod +x chromedriver
            print_success "ChromeDriver descargado automáticamente"
        else
            print_warning "No se pudo descargar automáticamente"
            print_message "Descarga manual desde: https://chromedriver.chromium.org/"
        fi
    else
        print_warning "No se pudo obtener versión de ChromeDriver"
        print_message "Descarga manual desde: https://chromedriver.chromium.org/"
    fi
else
    print_warning "Chrome no detectado o no está instalado"
    print_message "Descarga manual desde: https://chromedriver.chromium.org/"
fi

print_success "Instalación completada"
echo ""
echo "========================================"
echo "        🎉 INSTALACIÓN COMPLETADA"
echo "========================================"
echo ""
echo "✅ TODO LISTO"
echo ""
echo "📝 AHORA NECESITAS:"
echo "1. Ejecutar ./configurar.sh (para configuración guiada)"
echo "   O"
echo "2. Editar manualmente config.yaml con tus datos"
echo ""
echo "🚀 LUEGO EJECUTA:"
echo "./inicio.sh - Para iniciar el programa"
echo ""
echo "📁 EN ESTA CARPETA ENCONTRARÁS:"
echo "• config.yaml - Configuración (¡EDITA ESTE!)"
echo "• inicio.sh - Para iniciar"
echo "• configurar.sh - Configuración guiada"
echo "• actualizar.sh - Para actualizar"
echo "• README.txt - Esta guía"
echo ""
echo "💡 CONSEJO: Mantén esta carpeta en un lugar seguro"
echo ""
echo "========================================"
EOF

print_success "Instalador creado exitosamente"

# Dar permisos de ejecución
chmod +x installer.sh

echo ""
print_message "Para instalar, ejecuta:"
echo "1. ./installer.sh  (en Mac/Linux)"
echo "2. Doble clic en installer.bat  (en Windows)"
echo ""
print_message "¡Listo para comenzar! 🚀"