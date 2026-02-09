#!/usr/bin/env python3
"""
🛡️ LINKEDIN SAFE AUTOMATION BOT
Versión: 1.0 | Modo: Seguro
Características:
- Conexiones seguras (15-25/día)
- Anti-baneo integrado
- Logs en lenguaje humano
- Recuperación automática
"""

import time
import random
import yaml
import csv
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, 
    ElementClickInterceptedException, WebDriverException
)

class SafetyManager:
    """🛡️ GESTOR DE SEGURIDAD - Evita que te baneen"""
    
    def __init__(self):
        self.stats = {
            'connections_today': 0,
            'messages_today': 0,
            'profiles_viewed_today': 0,
            'errors_today': 0,
            'last_connection_time': None,
            'daily_start_time': datetime.now()
        }
        self.config = None
        
    def load_config(self, config_path: str = 'config.yaml'):
        """Carga la configuración desde YAML"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            print("✅ Configuración cargada correctamente")
            return True
        except Exception as e:
            print(f"❌ Error cargando configuración: {e}")
            return False
    
    def can_make_connection(self) -> Tuple[bool, str]:
        """Verifica si es seguro hacer una conexión"""
        if not self.config:
            return False, "Configuración no cargada"
        
        limits = self.config['limits']
        
        # Límite diario
        if self.stats['connections_today'] >= limits['daily_connections']:
            return False, f"Límite diario alcanzado ({limits['daily_connections']})"
        
        # Límite por hora
        if self.stats['last_connection_time']:
            time_since_last = datetime.now() - self.stats['last_connection_time']
            if (time_since_last.seconds < 3600 and 
                self.stats['connections_today'] >= limits['connections_per_hour']):
                return False, "Demasiadas conexiones en la última hora"
        
        # Verificar horario laboral
        if not self._is_within_work_hours():
            return False, "Fuera del horario laboral configurado"
        
        return True, "OK"
    
    def _is_within_work_hours(self) -> bool:
        """Verifica si estamos en horario laboral permitido"""
        if not self.config['behavior']['work_schedule']:
            return True
        
        today = datetime.now().strftime('%A').lower()
        schedule = self.config['behavior']['work_schedule'].get(today, [])
        
        if not schedule:
            return False
        
        current_time = datetime.now().strftime('%H:%M')
        return schedule[0] <= current_time <= schedule[1]
    
    def record_connection(self):
        """Registra una conexión exitosa"""
        self.stats['connections_today'] += 1
        self.stats['last_connection_time'] = datetime.now()
        self._save_stats()
    
    def get_human_delay(self) -> float:
        """Retorna un delay aleatorio entre acciones"""
        limits = self.config['limits']
        return random.uniform(limits['min_action_delay'], limits['max_action_delay'])
    
    def _save_stats(self):
        """Guarda estadísticas para recuperación"""
        stats_file = Path('logs/session_stats.json')
        stats_file.parent.mkdir(exist_ok=True)
        
        with open(stats_file, 'w') as f:
            json.dump({
                'last_update': datetime.now().isoformat(),
                'stats': self.stats
            }, f, indent=2)

class LinkedInBot:
    """🤖 BOT PRINCIPAL DE LINKEDIN - Seguro y confiable"""
    
    def __init__(self):
        self.driver = None
        self.safety = SafetyManager()
        self.wait = None
        self.session_active = False
        
    def initialize(self):
        """Inicializa el bot de forma segura"""
        print("=" * 50)
        print("🔄 INICIANDO LINKEDIN BOT (MODO SEGURO)")
        print("=" * 50)
        
        # 1. Cargar configuración
        if not self.safety.load_config():
            return False
        
        # 2. Configurar Chrome con opciones de seguridad
        options = self._get_browser_options()
        
        try:
            self.driver = webdriver.Chrome(options=options)
            self.wait = WebDriverWait(self.driver, self.safety.config['limits']['page_load_timeout'])
            print("✅ Navegador inicializado correctamente")
            return True
        except Exception as e:
            print(f"❌ Error iniciando navegador: {e}")
            return False
    
    def _get_browser_options(self):
        """Configura Chrome para parecer humano"""
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        
        # Configuraciones para evitar detección
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-infobars")
        options.add_argument("--start-maximized")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # User-Agent real
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        return options
    
    def login(self):
        """Inicia sesión en LinkedIn de forma segura"""
        print("\n🔐 INICIANDO SESIÓN EN LINKEDIN...")
        
        try:
            # Ir a LinkedIn
            self.driver.get("https://www.linkedin.com/login")
            time.sleep(3)
            
            # Verificar si ya estamos logueados
            if "feed" in self.driver.current_url:
                print("✅ Ya estabas logueado en LinkedIn")
                return True
            
            # Rellenar credenciales
            email_input = self.wait.until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            email_input.send_keys(self.safety.config['linkedin']['email'])
            
            password_input = self.driver.find_element(By.ID, "password")
            password_input.send_keys(self.safety.config['linkedin']['password'])
            
            # Click en login
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            
            # Esperar login exitoso
            time.sleep(5)
            
            # Verificar login
            if "feed" in self.driver.current_url or "voyager" in self.driver.current_url:
                print("✅ Login exitoso")
                self.session_active = True
                return True
            else:
                print("⚠️ Posible problema con el login")
                return False
                
        except Exception as e:
            print(f"❌ Error en login: {e}")
            return False
    
    def search_profiles(self):
        """Busca perfiles según configuración"""
        print("\n🔍 BUSCANDO PERFILES...")
        
        try:
            # Ir a búsqueda
            self.driver.get("https://www.linkedin.com/search/results/people/")
            time.sleep(3)
            
            # Aplicar filtros
            self._apply_search_filters()
            
            # Scroll para cargar más resultados
            self._human_scroll(max_scrolls=3)
            
            # Extraer perfiles
            profiles = self._extract_profiles_from_page()
            
            print(f"✅ Encontrados {len(profiles)} perfiles")
            return profiles
            
        except Exception as e:
            print(f"❌ Error buscando perfiles: {e}")
            return []
    
    def _apply_search_filters(self):
        """Aplica filtros de búsqueda"""
        try:
            # Esperar que cargue la página de búsqueda
            time.sleep(3)
            
            # Aquí iría la lógica para aplicar filtros
            # Por simplicidad, en esta versión usamos búsqueda directa por URL
            search_params = []
            config = self.safety.config['search']
            
            if config['keywords']:
                search_params.append(f"keywords={config['keywords'].replace(' ', '%20')}")
            if config['locations']:
                search_params.append(f"location={config['locations'].split()[0].replace(' ', '%20')}")
            
            if search_params:
                search_url = f"https://www.linkedin.com/search/results/people/?{'&'.join(search_params)}"
                self.driver.get(search_url)
                time.sleep(3)
                
        except Exception as e:
            print(f"⚠️ No se pudieron aplicar filtros: {e}")
    
    def _extract_profiles_from_page(self) -> List[Dict]:
        """Extrae perfiles de la página actual"""
        profiles = []
        
        try:
            # Encontrar elementos de perfil
            profile_elements = self.driver.find_elements(
                By.XPATH, "//div[contains(@class, 'entity-result__item')]"
            )
            
            for element in profile_elements[:15]:  # Limitar a 15 por página
                try:
                    profile_data = self._extract_profile_data(element)
                    if profile_data:
                        profiles.append(profile_data)
                except:
                    continue
                    
        except Exception as e:
            print(f"⚠️ Error extrayendo perfiles: {e}")
        
        return profiles
    
    def _extract_profile_data(self, element) -> Optional[Dict]:
        """Extrae datos individuales de un perfil"""
        try:
            # Nombre
            name_element = element.find_element(By.XPATH, ".//span[contains(@class, 'entity-result__title-text')]//a")
            full_name = name_element.text.strip()
            name_parts = full_name.split()
            first_name = name_parts[0] if name_parts else ""
            
            # Puesto
            position = element.find_element(
                By.XPATH, ".//div[contains(@class, 'entity-result__primary-subtitle')]"
            ).text.strip()
            
            # Empresa
            company = element.find_element(
                By.XPATH, ".//div[contains(@class, 'entity-result__secondary-subtitle')]"
            ).text.strip()
            
            # URL del perfil
            profile_url = name_element.get_attribute("href").split('?')[0]
            
            return {
                'full_name': full_name,
                'first_name': first_name,
                'position': position,
                'company': company,
                'profile_url': profile_url,
                'found_date': datetime.now().isoformat()
            }
            
        except:
            return None
    
    def send_connection_request(self, profile: Dict) -> bool:
        """Envía solicitud de conexión de forma segura"""
        print(f"\n🤝 INTENTANDO CONECTAR CON: {profile['full_name']}")
        
        # Verificar seguridad primero
        can_connect, reason = self.safety.can_make_connection()
        if not can_connect:
            print(f"⏸️  No se puede conectar: {reason}")
            return False
        
        try:
            # 1. Ir al perfil
            self.driver.get(profile['profile_url'])
            time.sleep(self.safety.get_human_delay())
            
            # 2. Verificar que no estamos ya conectados
            if self._is_already_connected():
                print(f"✅ Ya estás conectado con {profile['full_name']}")
                return False
            
            # 3. Encontrar botón de conectar
            connect_button = self._find_connect_button()
            if not connect_button:
                print(f"⚠️  No se encontró botón de conectar para {profile['full_name']}")
                return False
            
            # 4. Click en conectar
            connect_button.click()
            time.sleep(2)
            
            # 5. Enviar mensaje personalizado si está disponible
            if self._can_send_message():
                self._send_personalized_message(profile)
            
            # 6. Registrar éxito
            self.safety.record_connection()
            profile['connected'] = True
            profile['connection_date'] = datetime.now().isoformat()
            
            print(f"✅ Conexión enviada a {profile['full_name']}")
            
            # 7. Delay humano antes de la siguiente acción
            time.sleep(self.safety.get_human_delay())
            
            return True
            
        except Exception as e:
            print(f"❌ Error conectando con {profile['full_name']}: {e}")
            self.safety.stats['errors_today'] += 1
            return False
    
    def _find_connect_button(self):
        """Busca el botón de conectar en diferentes ubicaciones"""
        button_selectors = [
            "//button[contains(@class, 'connect') and span[text()='Conectar']]",
            "//button[contains(@class, 'connect')]",
            "//button[span[text()='Connect']]",
            "//button[.//span[contains(text(), 'Conectar')]]"
        ]
        
        for selector in button_selectors:
            try:
                return self.driver.find_element(By.XPATH, selector)
            except:
                continue
        return None
    
    def _can_send_message(self) -> bool:
        """Verifica si podemos enviar mensaje con la conexión"""
        try:
            # Buscar textarea para mensaje
            self.driver.find_element(By.ID, "custom-message")
            return True
        except:
            return False
    
    def _send_personalized_message(self, profile: Dict):
        """Envía un mensaje personalizado"""
        try:
            # Seleccionar plantilla aleatoria
            templates = self.safety.config['messages']['connection_request']
            template = random.choice(templates)['template']
            
            # Reemplazar variables
            message = template.replace("{{first_name}}", profile.get('first_name', ''))
            message = message.replace("{{company}}", profile.get('company', 'tu empresa'))
            message = message.replace("{{position}}", profile.get('position', 'tu puesto'))
            
            # Encontrar textarea y escribir
            textarea = self.driver.find_element(By.ID, "custom-message")
            textarea.clear()
            
            # Escribir como humano (carácter por carácter)
            for char in message:
                textarea.send_keys(char)
                time.sleep(random.uniform(0.05, 0.1))
            
            # Enviar
            send_button = self.driver.find_element(
                By.XPATH, "//button[contains(@class, 'send-invite')]"
            )
            send_button.click()
            
            print(f"💬 Mensaje enviado: {message[:50]}...")
            
        except Exception as e:
            print(f"⚠️  No se pudo enviar mensaje: {e}")
    
    def _is_already_connected(self) -> bool:
        """Verifica si ya está conectado con este perfil"""
        try:
            # Buscar indicador de ya conectado
            self.driver.find_element(
                By.XPATH, "//span[contains(text(), 'Conectado') or contains(text(), 'Connected')]"
            )
            return True
        except:
            return False
    
    def _human_scroll(self, max_scrolls: int = 5):
        """Hace scroll como humano"""
        for i in range(max_scrolls):
            scroll_height = random.randint(300, 800)
            self.driver.execute_script(f"window.scrollBy(0, {scroll_height});")
            time.sleep(random.uniform(1, 3))
    
    def export_profiles(self, profiles: List[Dict], filename: str = None):
        """Exporta perfiles a CSV"""
        if not filename:
            date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"linkedin_profiles_{date_str}.csv"
        
        export_path = Path("exports") / filename
        export_path.parent.mkdir(exist_ok=True)
        
        try:
            with open(export_path, 'w', newline='', encoding='utf-8') as f:
                if profiles:
                    writer = csv.DictWriter(f, fieldnames=profiles[0].keys())
                    writer.writeheader()
                    writer.writerows(profiles)
            
            print(f"💾 Exportados {len(profiles)} perfiles a: {export_path}")
            return str(export_path)
            
        except Exception as e:
            print(f"❌ Error exportando: {e}")
            return None
    
    def show_stats(self):
        """Muestra estadísticas en lenguaje humano"""
        stats = self.safety.stats
        config = self.safety.config
        
        print("\n" + "=" * 50)
        print("📊 ESTADÍSTICAS DE HOY")
        print("=" * 50)
        
        connections_left = config['limits']['daily_connections'] - stats['connections_today']
        
        print(f"🤝 Conexiones hoy: {stats['connections_today']}/{config['limits']['daily_connections']}")
        print(f"📤 Restantes hoy: {connections_left}")
        print(f"💬 Mensajes enviados: {stats['messages_today']}")
        print(f"👀 Perfiles vistos: {stats['profiles_viewed_today']}")
        print(f"⚠️  Errores: {stats['errors_today']}")
        
        if stats['last_connection_time']:
            last = stats['last_connection_time'].strftime("%H:%M:%S")
            print(f"⏰ Última conexión: {last}")
        
        # Tiempo estimado para completar
        if connections_left > 0:
            avg_time = (config['limits']['min_action_delay'] + config['limits']['max_action_delay']) / 2
            est_minutes = (connections_left * avg_time) / 60
            print(f"⏱️  Tiempo estimado restante: {est_minutes:.1f} minutos")
    
    def safe_shutdown(self):
        """Cierra el bot de forma segura"""
        print("\n" + "=" * 50)
        print("🛑 APAGANDO BOT DE FORMA SEGURA...")
        print("=" * 50)
        
        try:
            if self.driver:
                # Guardar cookies para próxima sesión
                self._save_session_cookies()
                
                # Cerrar navegador
                self.driver.quit()
                print("✅ Navegador cerrado correctamente")
            
            # Mostrar resumen final
            self.show_stats()
            
            # Exportar estadísticas
            self.safety._save_stats()
            
        except Exception as e:
            print(f"⚠️  Error en apagado: {e}")
        
        print("\n✨ Sesión finalizada. ¡Hasta la próxima!")
    
    def _save_session_cookies(self):
        """Guarda cookies para no tener que reloguear"""
        try:
            cookies = self.driver.get_cookies()
            cookies_file = Path('session/cookies.json')
            cookies_file.parent.mkdir(exist_ok=True)
            
            with open(cookies_file, 'w') as f:
                json.dump(cookies, f)
            
            print("🍪 Cookies guardadas para próxima sesión")
        except:
            pass

# =============== FUNCIÓN PRINCIPAL ===============
def main():
    """Función principal - Punto de entrada del programa"""
    
    bot = LinkedInBot()
    
    try:
        # 1. Inicializar
        if not bot.initialize():
            print("❌ No se pudo inicializar el bot")
            return
        
        # 2. Login
        if not bot.login():
            print("❌ No se pudo hacer login")
            return
        
        # 3. Buscar perfiles
        profiles = bot.search_profiles()
        
        if not profiles:
            print("⚠️  No se encontraron perfiles")
            bot.safe_shutdown()
            return
        
        # 4. Conectar con perfiles (con límites seguros)
        connected_profiles = []
        
        for profile in profiles:
            if bot.safety.stats['connections_today'] >= bot.safety.config['limits']['daily_connections']:
                print("🛑 Límite diario alcanzado. Deteniendo...")
                break
            
            success = bot.send_connection_request(profile)
            if success:
                connected_profiles.append(profile)
            
            # Pausa ocasional más larga (como humano)
            if random.random() < 0.3:  # 30% de probabilidad
                time.sleep(random.uniform(10, 20))
        
        # 5. Exportar resultados
        if connected_profiles:
            bot.export_profiles(connected_profiles)
        
        # 6. Mostrar estadísticas
        bot.show_stats()
        
    except KeyboardInterrupt:
        print("\n⚠️  Interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error crítico: {e}")
    finally:
        # 7. Apagar de forma segura
        bot.safe_shutdown()

if __name__ == "__main__":
    main()
