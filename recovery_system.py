"""
🔄 SISTEMA DE RECUPERACIÓN AUTOMÁTICA
Versión: 1.0 | Recuperación: Inteligente
Características:
- Detección de CAPTCHA automática
- Recuperación de sesión
- Backup continuo
- Restauración punto por punto
"""

import time
import json
import pickle
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import logging
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class RecoverySystem:
    """🔄 SISTEMA DE RECUPERACIÓN - Recupera automáticamente de errores"""
    
    def __init__(self, driver=None):
        self.driver = driver
        self.backup_dir = Path('backups')
        self.session_dir = Path('session')
        self.recovery_log = []
        self.last_backup = None
        
        # Configurar directorios
        self._setup_directories()
        
        # Configurar logging
        self._setup_logging()
    
    def _setup_directories(self):
        """Crea estructura de directorios para recuperación"""
        directories = [
            self.backup_dir / 'daily',
            self.backup_dir / 'hourly',
            self.session_dir / 'cookies',
            self.session_dir / 'state',
            'logs/recovery'
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def _setup_logging(self):
        """Configura sistema de logs de recuperación"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/recovery/recovery.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def create_backup(self, backup_type: str = 'auto', data: Dict = None):
        """
        Crea un backup del estado actual
        Tipos: 'auto', 'manual', 'pre_action', 'post_action'
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if backup_type == 'hourly':
            backup_path = self.backup_dir / 'hourly' / f'backup_{timestamp}.json'
        elif backup_type == 'daily':
            backup_path = self.backup_dir / 'daily' / f'backup_{timestamp}.json'
        else:
            backup_path = self.backup_dir / f'backup_{timestamp}_{backup_type}.json'
        
        backup_data = {
            'timestamp': timestamp,
            'type': backup_type,
            'data': data or {},
            'created_at': datetime.now().isoformat()
        }
        
        # Incluir cookies si hay driver
        if self.driver:
            try:
                cookies = self.driver.get_cookies()
                backup_data['cookies'] = cookies
                
                # Guardar cookies por separado
                cookies_file = self.session_dir / 'cookies' / f'cookies_{timestamp}.pkl'
                with open(cookies_file, 'wb') as f:
                    pickle.dump(cookies, f)
            except:
                pass
        
        # Guardar backup
        with open(backup_path, 'w') as f:
            json.dump(backup_data, f, indent=2)
        
        self.last_backup = backup_path
        self.logger.info(f"💾 Backup creado: {backup_type} - {backup_path.name}")
        
        # Limpiar backups antiguos
        self._clean_old_backups()
        
        return str(backup_path)
    
    def _clean_old_backups(self):
        """Elimina backups antiguos para ahorrar espacio"""
        # Mantener solo 24 backups por hora
        hourly_dir = self.backup_dir / 'hourly'
        if hourly_dir.exists():
            hourly_files = sorted(hourly_dir.glob('*.json'))
            if len(hourly_files) > 24:
                for old_file in hourly_files[:-24]:
                    old_file.unlink()
        
        # Mantener solo 7 backups diarios
        daily_dir = self.backup_dir / 'daily'
        if daily_dir.exists():
            daily_files = sorted(daily_dir.glob('*.json'))
            if len(daily_files) > 7:
                for old_file in daily_files[:-7]:
                    old_file.unlink()
    
    def detect_captcha(self) -> bool:
        """Detecta si LinkedIn muestra CAPTCHA"""
        if not self.driver:
            return False
        
        captcha_indicators = [
            "captcha", "CAPTCHA", "verification", "robot",
            "not a robot", "security check", "Verify"
        ]
        
        try:
            # Verificar título y body
            page_source = self.driver.page_source.lower()
            
            for indicator in captcha_indicators:
                if indicator.lower() in page_source:
                    self.logger.warning(f"🔍 CAPTCHA detectado: {indicator}")
                    return True
            
            # Verificar elementos específicos de CAPTCHA
            captcha_selectors = [
                "iframe[src*='captcha']",
                "div[class*='captcha']",
                "div[id*='captcha']",
                "img[src*='captcha']"
            ]
            
            for selector in captcha_selectors:
                try:
                    element = self.driver.find_element_by_css_selector(selector)
                    if element:
                        self.logger.warning("🔍 CAPTCHA detectado por selector")
                        return True
                except:
                    continue
            
            # Verificar redirección a página de verificación
            current_url = self.driver.current_url.lower()
            if 'challenge' in current_url or 'verify' in current_url or 'security' in current_url:
                self.logger.warning(f"🔍 Página de verificación detectada: {current_url}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Error detectando CAPTCHA: {e}")
            return False
    
    def handle_captcha(self, action: str = 'wait') -> Dict:
        """
        Maneja CAPTCHA detectado
        Acciones: 'wait', 'notify', 'stop', 'bypass'
        """
        captcha_info = {
            'detected_at': datetime.now().isoformat(),
            'action_taken': action,
            'status': 'pending'
        }
        
        if action == 'wait':
            # Esperar tiempo humano para resolver CAPTCHA manualmente
            wait_time = 300  # 5 minutos
            self.logger.warning(f"⏳ CAPTCHA detectado. Esperando {wait_time//60} minutos para resolución manual...")
            
            captcha_info['wait_time'] = wait_time
            captcha_info['message'] = 'Por favor, resuelve el CAPTCHA manualmente'
            
            time.sleep(wait_time)
            
            # Verificar si CAPTCHA sigue presente
            if self.detect_captcha():
                captcha_info['status'] = 'still_present'
                self.logger.error("❌ CAPTCHA no resuelto después de espera")
            else:
                captcha_info['status'] = 'resolved'
                self.logger.info("✅ CAPTCHA aparentemente resuelto")
        
        elif action == 'notify':
            # Solo notificar y continuar (para pruebas)
            self.logger.critical("🚨 CAPTCHA DETECTADO - Notificación enviada")
            captcha_info['status'] = 'notified'
        
        elif action == 'stop':
            # Detener completamente
            self.logger.critical("🛑 CAPTCHA detectado - Deteniendo ejecución")
            captcha_info['status'] = 'stopped'
            raise Exception("CAPTCHA detectado - Ejecución detenida")
        
        # Guardar registro del CAPTCHA
        self.recovery_log.append(captcha_info)
        self._save_recovery_log()
        
        return captcha_info
    
    def save_session_state(self, state_data: Dict):
        """Guarda el estado actual de la sesión"""
        state_file = self.session_dir / 'state' / 'current_state.json'
        
        full_state = {
            'saved_at': datetime.now().isoformat(),
            'data': state_data,
            'url': self.driver.current_url if self.driver else None,
            'title': self.driver.title if self.driver else None
        }
        
        with open(state_file, 'w') as f:
            json.dump(full_state, f, indent=2)
        
        self.logger.info("💾 Estado de sesión guardado")
        return str(state_file)
    
    def restore_session_state(self) -> Optional[Dict]:
        """Restaura el último estado guardado de la sesión"""
        state_file = self.session_dir / 'state' / 'current_state.json'
        
        if not state_file.exists():
            self.logger.warning("⚠️ No hay estado previo para restaurar")
            return None
        
        try:
            with open(state_file, 'r') as f:
                state_data = json.load(f)
            
            self.logger.info(f"🔄 Restaurando estado de sesión de {state_data['saved_at']}")
            
            # Restaurar cookies si hay driver
            if self.driver and 'cookies' in state_data:
                try:
                    self.driver.delete_all_cookies()
                    for cookie in state_data['cookies']:
                        self.driver.add_cookie(cookie)
                    self.logger.info("🍪 Cookies restauradas")
                except:
                    self.logger.warning("⚠️ No se pudieron restaurar cookies")
            
            return state_data
            
        except Exception as e:
            self.logger.error(f"❌ Error restaurando estado: {e}")
            return None
    
    def recover_from_crash(self, crash_data: Dict = None) -> Dict:
        """Intenta recuperar de un crash inesperado"""
        recovery_attempt = {
            'attempted_at': datetime.now().isoformat(),
            'steps': [],
            'success': False
        }
        
        self.logger.info("🔄 Intentando recuperación de crash...")
        
        # Paso 1: Buscar backup más reciente
        latest_backup = self._find_latest_backup()
        if latest_backup:
            recovery_attempt['steps'].append(f"Backup encontrado: {latest_backup.name}")
            self.logger.info(f"📂 Backup disponible: {latest_backup.name}")
        
        # Paso 2: Restaurar cookies si es posible
        if self.driver:
            try:
                cookies_restored = self._restore_latest_cookies()
                if cookies_restored:
                    recovery_attempt['steps'].append("Cookies restauradas")
                    self.logger.info("🍪 Cookies restauradas")
            except Exception as e:
                recovery_attempt['steps'].append(f"Error restaurando cookies: {e}")
                self.logger.error(f"❌ Error restaurando cookies: {e}")
        
        # Paso 3: Limpiar elementos problemáticos
        try:
            self._clean_problematic_elements()
            recovery_attempt['steps'].append("Elementos problemáticos limpiados")
            self.logger.info("🧹 Elementos problemáticos limpiados")
        except Exception as e:
            recovery_attempt['steps'].append(f"Error limpiando elementos: {e}")
        
        # Paso 4: Verificar si LinkedIn responde
        linkedin_accessible = self._check_linkedin_access()
        recovery_attempt['linkedin_accessible'] = linkedin_accessible
        
        if linkedin_accessible:
            recovery_attempt['success'] = True
            recovery_attempt['steps'].append("Recuperación exitosa")
            self.logger.info("✅ Recuperación exitosa")
        else:
            recovery_attempt['steps'].append("LinkedIn no accesible - requiere intervención manual")
            self.logger.error("❌ LinkedIn no accesible después de recuperación")
        
        # Guardar registro de recuperación
        self.recovery_log.append(recovery_attempt)
        self._save_recovery_log()
        
        return recovery_attempt
    
    def _find_latest_backup(self) -> Optional[Path]:
        """Encuentra el backup más reciente"""
        backup_files = list(self.backup_dir.glob('**/*.json'))
        
        if not backup_files:
            return None
        
        # Ordenar por fecha de modificación
        latest_backup = max(backup_files, key=lambda x: x.stat().st_mtime)
        return latest_backup
    
    def _restore_latest_cookies(self) -> bool:
        """Restaura las cookies más recientes"""
        cookies_dir = self.session_dir / 'cookies'
        cookie_files = list(cookies_dir.glob('*.pkl'))
        
        if not cookie_files:
            return False
        
        # Obtener archivo más reciente
        latest_cookie = max(cookie_files, key=lambda x: x.stat().st_mtime)
        
        try:
            with open(latest_cookie, 'rb') as f:
                cookies = pickle.load(f)
            
            self.driver.delete_all_cookies()
            for cookie in cookies:
                self.driver.add_cookie(cookie)
            
            # Refrescar para aplicar cookies
            self.driver.refresh()
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error restaurando cookies: {e}")
            return False
    
    def _clean_problematic_elements(self):
        """Limpia elementos que pueden causar problemas"""
        if not self.driver:
            return
        
        try:
            # Limpiar almacenamiento local
            self.driver.execute_script("window.localStorage.clear();")
            self.driver.execute_script("window.sessionStorage.clear();")
            
            # Eliminar cookies problemáticas
            self.driver.delete_all_cookies()
            
        except:
            pass
    
    def _check_linkedin_access(self) -> bool:
        """Verifica si LinkedIn es accesible"""
        if not self.driver:
            return False
        
        try:
            # Intentar cargar página principal
            self.driver.get("https://www.linkedin.com/")
            time.sleep(3)
            
            # Verificar que no estamos en página de login forzado
            current_url = self.driver.current_url
            
            if "login" in current_url and "feed" not in current_url:
                return False
            
            # Verificar elementos clave de LinkedIn
            linkedin_indicators = [
                "feed", "voyager", "linkedin", "mynetwork",
                "notifications", "messaging"
            ]
            
            page_source = self.driver.page_source.lower()
            
            for indicator in linkedin_indicators:
                if indicator in page_source:
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Error verificando acceso: {e}")
            return False
    
    def _save_recovery_log(self):
        """Guarda el log de recuperación"""
        log_file = Path('logs/recovery/recovery_history.json')
        
        log_data = {
            'last_updated': datetime.now().isoformat(),
            'entries': self.recovery_log[-100:]  # Mantener solo últimas 100 entradas
        }
        
        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2)
    
    def get_recovery_status(self) -> Dict:
        """Obtiene estado actual del sistema de recuperación"""
        backups_count = len(list(self.backup_dir.glob('**/*.json')))
        cookies_count = len(list((self.session_dir / 'cookies').glob('*.pkl')))
        
        latest_backup = self._find_latest_backup()
        
        return {
            'last_backup': self.last_backup.name if self.last_backup else None,
            'backups_count': backups_count,
            'cookies_count': cookies_count,
            'recovery_log_entries': len(self.recovery_log),
            'system_status': 'healthy' if backups_count > 0 else 'needs_backup',
            'recommendation': self._get_recovery_recommendation(backups_count),
            'latest_backup_age': self._get_file_age(latest_backup) if latest_backup else 'no_backup'
        }
    
    def _get_recovery_recommendation(self, backups_count: int) -> str:
        """Genera recomendación basada en estado de backups"""
        if backups_count == 0:
            return "⚠️  Crear backup inmediatamente"
        elif backups_count < 3:
            return "🔶 Pocos backups - crear más frecuentemente"
        else:
            return "✅ Sistema de recuperación listo"
    
    def _get_file_age(self, file_path: Path) -> str:
        """Calcula edad del archivo en texto legible"""
        if not file_path or not file_path.exists():
            return "N/A"
        
        modified_time = datetime.fromtimestamp(file_path.stat().st_mtime)
        age = datetime.now() - modified_time
        
        if age.days > 0:
            return f"{age.days} días"
        elif age.seconds > 3600:
            return f"{age.seconds // 3600} horas"
        elif age.seconds > 60:
            return f"{age.seconds // 60} minutos"
        else:
            return f"{age.seconds} segundos"
    
    def create_emergency_recovery_kit(self):
        """Crea un kit de recuperación de emergencia (para enviar a soporte)"""
        kit_dir = Path('emergency_kit')
        kit_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        kit_name = f"recovery_kit_{timestamp}"
        kit_path = kit_dir / kit_name
        
        # Crear zip con archivos importantes
        import zipfile
        
        with zipfile.ZipFile(f"{kit_path}.zip", 'w') as zipf:
            # Incluir logs
            for log_file in Path('logs').rglob('*.log'):
                zipf.write(log_file, f"logs/{log_file.name}")
            
            # Incluir configuración
            config_files = ['config.yaml', 'session/security_state.json']
            for config_file in config_files:
                if Path(config_file).exists():
                    zipf.write(config_file, config_file)
            
            # Incluir último backup
            latest_backup = self._find_latest_backup()
            if latest_backup:
                zipf.write(latest_backup, f"backups/{latest_backup.name}")
            
            # Incluir readme con instrucciones
            readme_content = f"""EMERGENCY RECOVERY KIT
Created: {datetime.now().isoformat()}
Contains: Logs, configuration, last backup

Instructions:
1. Send this file to support
2. Do NOT share with unauthorized persons
3. Contains sensitive information

Issues detected in logs: {len(self.recovery_log)}
"""
            
            zipf.writestr("README.txt", readme_content)
        
        self.logger.info(f"📦 Kit de emergencia creado: {kit_path}.zip")
        return f"{kit_path}.zip"
