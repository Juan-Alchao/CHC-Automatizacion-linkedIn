"""
🛡️ SISTEMA DE SEGURIDAD AVANZADO
Versión: 2.0 | Protección: Máxima
Características:
- Detección de patrones de baneo
- Recuperación automática
- Estadísticas predictivas
- Alertas inteligentes
"""

import time
import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

class AdvancedSafetyManager:
    """🛡️ GESTOR DE SEGURIDAD AVANZADO - Sistema anti-baneo profesional"""
    
    def __init__(self):
        self.config = None
        self.session_data = {}
        self.suspicion_level = 0  # 0-100, donde 100 = riesgo máximo
        self.recovery_mode = False
        self.last_action_time = None
        self.action_pattern = []
        
        # Inicializar logging
        self._setup_logging()
        
    def _setup_logging(self):
        """Configura sistema de logs avanzado"""
        log_dir = Path('logs/security')
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / f'security_{datetime.now().strftime("%Y%m%d")}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def load_config(self, config_path: str = 'config.yaml'):
        """Carga configuración y estado previo"""
        import yaml
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            
            # Cargar estado de sesión previa
            self._load_session_state()
            
            self.logger.info("✅ Configuración de seguridad cargada")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error cargando configuración: {e}")
            return False
    
    def _load_session_state(self):
        """Carga el estado de sesiones anteriores"""
        state_file = Path('session/security_state.json')
        
        if state_file.exists():
            try:
                with open(state_file, 'r') as f:
                    self.session_data = json.load(f)
                
                # Calcular nivel de sospecha basado en historial
                self._calculate_suspicion_level()
                
                self.logger.info(f"📊 Estado anterior cargado: {len(self.session_data.get('actions', []))} acciones")
            except:
                self.session_data = {'actions': [], 'errors': [], 'recoveries': []}
        else:
            self.session_data = {'actions': [], 'errors': [], 'recoveries': []}
    
    def can_perform_action(self, action_type: str) -> Dict:
        """
        Verifica si se puede realizar una acción de forma segura
        Retorna: {'allowed': bool, 'reason': str, 'delay': int, 'mode': str}
        """
        if not self.config:
            return {'allowed': False, 'reason': 'Configuración no cargada', 'delay': 0, 'mode': 'blocked'}
        
        # Verificar modo recuperación
        if self.recovery_mode:
            return {'allowed': False, 'reason': 'Modo recuperación activo', 'delay': 300, 'mode': 'recovery'}
        
        # Verificar nivel de sospecha
        if self.suspicion_level > 70:
            return {'allowed': False, 'reason': f'Nivel de sospecha alto ({self.suspicion_level}%)', 'delay': 600, 'mode': 'suspicious'}
        
        # Verificar límites diarios
        daily_check = self._check_daily_limits(action_type)
        if not daily_check['allowed']:
            return daily_check
        
        # Verificar patrones temporales
        pattern_check = self._check_action_patterns()
        if not pattern_check['allowed']:
            return pattern_check
        
        # Verificar horarios seguros
        time_check = self._check_safe_hours()
        if not time_check['allowed']:
            return time_check
        
        # Calcular delay seguro
        safe_delay = self._calculate_safe_delay(action_type)
        
        return {
            'allowed': True,
            'reason': 'Acción permitida',
            'delay': safe_delay,
            'mode': 'normal'
        }
    
    def _check_daily_limits(self, action_type: str) -> Dict:
        """Verifica límites diarios de seguridad"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Contar acciones hoy
        today_actions = [
            a for a in self.session_data.get('actions', [])
            if a.get('date') == today and a.get('type') == action_type
        ]
        
        limits = self.config['limits']
        
        if action_type == 'connection':
            max_allowed = limits['daily_connections']
            current = len(today_actions)
            
            if current >= max_allowed:
                return {
                    'allowed': False,
                    'reason': f'Límite diario alcanzado ({current}/{max_allowed})',
                    'delay': 3600,
                    'mode': 'limit_reached'
                }
        
        elif action_type == 'message':
            max_allowed = limits['messages_per_day']
            current = len([a for a in today_actions if a.get('subtype') == 'message'])
            
            if current >= max_allowed:
                return {
                    'allowed': False,
                    'reason': f'Límite mensajes alcanzado ({current}/{max_allowed})',
                    'delay': 1800,
                    'mode': 'limit_reached'
                }
        
        return {'allowed': True, 'reason': 'OK', 'delay': 0, 'mode': 'normal'}
    
    def _check_action_patterns(self) -> Dict:
        """Analiza patrones para detectar comportamiento robótico"""
        actions = self.session_data.get('actions', [])
        
        if len(actions) < 3:
            return {'allowed': True, 'reason': 'Patrón insuficiente', 'delay': 0, 'mode': 'normal'}
        
        # Verificar repetición exacta de tiempos
        last_actions = actions[-3:]
        times = [datetime.fromisoformat(a['timestamp']) for a in last_actions]
        intervals = [(times[i+1] - times[i]).seconds for i in range(len(times)-1)]
        
        # Si todos los intervalos son idénticos (patrón robótico)
        if len(set(intervals)) == 1 and intervals[0] < 30:
            self.suspicion_level += 20
            self.logger.warning(f"⚠️ Patrón robótico detectado: intervalos idénticos de {intervals[0]}s")
            
            return {
                'allowed': False,
                'reason': 'Patrón temporal detectado (parece robótico)',
                'delay': random.randint(60, 180),
                'mode': 'pattern_detected'
            }
        
        return {'allowed': True, 'reason': 'Patrón normal', 'delay': 0, 'mode': 'normal'}
    
    def _check_safe_hours(self) -> Dict:
        """Verifica si estamos en horarios seguros"""
        if not self.config.get('behavior', {}).get('work_schedule'):
            return {'allowed': True, 'reason': 'Sin horarios configurados', 'delay': 0, 'mode': 'normal'}
        
        now = datetime.now()
        current_day = now.strftime('%A').lower()
        current_time = now.strftime('%H:%M')
        
        schedule = self.config['behavior']['work_schedule'].get(current_day, [])
        
        if not schedule:
            return {'allowed': False, 'reason': 'Día no laboral configurado', 'delay': 3600, 'mode': 'off_hours'}
        
        if current_time < schedule[0] or current_time > schedule[1]:
            return {'allowed': False, 'reason': 'Fuera de horario laboral', 'delay': 3600, 'mode': 'off_hours'}
        
        return {'allowed': True, 'reason': 'Horario laboral', 'delay': 0, 'mode': 'normal'}
    
    def _calculate_safe_delay(self, action_type: str) -> int:
        """Calcula un delay seguro basado en múltiples factores"""
        base_delay = random.randint(
            self.config['limits']['min_action_delay'],
            self.config['limits']['max_action_delay']
        )
        
        # Ajustar por nivel de sospecha
        suspicion_multiplier = 1 + (self.suspicion_level / 100)
        
        # Ajustar por tipo de acción
        if action_type == 'connection':
            action_multiplier = 1.2
        elif action_type == 'message':
            action_multiplier = 1.0
        else:
            action_multiplier = 1.0
        
        # Ajustar por hora del día (más lento en horas pico)
        hour = datetime.now().hour
        if 9 <= hour <= 11 or 14 <= hour <= 16:
            time_multiplier = 1.3  # Horas pico
        else:
            time_multiplier = 1.0
        
        final_delay = int(base_delay * suspicion_multiplier * action_multiplier * time_multiplier)
        
        # Delay mínimo y máximo
        final_delay = max(10, min(final_delay, 120))
        
        return final_delay
    
    def _calculate_suspicion_level(self):
        """Calcula nivel de sospecha basado en historial"""
        actions = self.session_data.get('actions', [])
        errors = self.session_data.get('errors', [])
        
        if not actions:
            self.suspicion_level = 0
            return
        
        # Factor 1: Densidad de acciones
        if len(actions) > 0:
            first_action = datetime.fromisoformat(actions[0]['timestamp'])
            last_action = datetime.fromisoformat(actions[-1]['timestamp'])
            total_hours = (last_action - first_action).total_seconds() / 3600
            
            if total_hours > 0:
                actions_per_hour = len(actions) / total_hours
                if actions_per_hour > 10:  # Más de 10 acciones por hora
                    self.suspicion_level += 30
        
        # Factor 2: Tasa de errores
        if len(actions) > 0:
            error_rate = len(errors) / len(actions) * 100
            if error_rate > 20:  # Más del 20% de errores
                self.suspicion_level += 25
        
        # Factor 3: Recuperaciones recientes
        recoveries = self.session_data.get('recoveries', [])
        recent_recoveries = [r for r in recoveries if 
                           (datetime.now() - datetime.fromisoformat(r['timestamp'])).days < 1]
        
        if len(recent_recoveries) > 2:
            self.suspicion_level += 30
        
        # Limitar a 100%
        self.suspicion_level = min(100, self.suspicion_level)
        
        # Reducir gradualmente con el tiempo
        time_since_last_action = datetime.now() - datetime.fromisoformat(actions[-1]['timestamp'])
        if time_since_last_action.total_seconds() > 3600:  # 1 hora sin acciones
            self.suspicion_level *= 0.8  # Reducir 20%
    
    def record_action(self, action_type: str, success: bool = True, details: Dict = None):
        """Registra una acción para análisis futuro"""
        action_record = {
            'type': action_type,
            'timestamp': datetime.now().isoformat(),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'success': success,
            'suspicion_level': self.suspicion_level,
            'details': details or {}
        }
        
        self.session_data.setdefault('actions', []).append(action_record)
        self.last_action_time = datetime.now()
        self.action_pattern.append(action_type)
        
        # Mantener solo últimas 100 acciones
        if len(self.session_data['actions']) > 100:
            self.session_data['actions'] = self.session_data['actions'][-100:]
        
        # Actualizar nivel de sospecha
        if not success:
            self.session_data.setdefault('errors', []).append(action_record)
            self.suspicion_level += 5
        else:
            self.suspicion_level = max(0, self.suspicion_level - 1)
        
        # Guardar estado
        self._save_session_state()
        
        self.logger.info(f"📝 Acción registrada: {action_type} - {'✅' if success else '❌'}")
    
    def record_error(self, error_type: str, details: str):
        """Registra un error específico"""
        error_record = {
            'type': error_type,
            'timestamp': datetime.now().isoformat(),
            'details': details,
            'suspicion_level': self.suspicion_level
        }
        
        self.session_data.setdefault('errors', []).append(error_record)
        self.suspicion_level += 10
        
        # Si hay muchos errores recientes, activar modo recuperación
        recent_errors = [
            e for e in self.session_data['errors']
            if (datetime.now() - datetime.fromisoformat(e['timestamp'])).total_seconds() < 3600
        ]
        
        if len(recent_errors) > 3:
            self.activate_recovery_mode()
        
        self._save_session_state()
        self.logger.warning(f"⚠️ Error registrado: {error_type} - {details}")
    
    def activate_recovery_mode(self, duration_minutes: int = 60):
        """Activa modo recuperación para enfriar la cuenta"""
        self.recovery_mode = True
        self.suspicion_level = min(100, self.suspicion_level + 30)
        
        recovery_record = {
            'timestamp': datetime.now().isoformat(),
            'duration': duration_minutes,
            'reason': 'Múltiples errores detectados',
            'suspicion_level': self.suspicion_level
        }
        
        self.session_data.setdefault('recoveries', []).append(recovery_record)
        
        # Programar desactivación
        import threading
        threading.Timer(duration_minutes * 60, self.deactivate_recovery_mode).start()
        
        self.logger.warning(f"🛡️ Modo recuperación activado por {duration_minutes} minutos")
    
    def deactivate_recovery_mode(self):
        """Desactiva modo recuperación"""
        self.recovery_mode = False
        self.suspicion_level = max(0, self.suspicion_level - 20)
        self.logger.info("✅ Modo recuperación desactivado")
    
    def get_safety_report(self) -> Dict:
        """Genera reporte de seguridad"""
        return {
            'suspicion_level': self.suspicion_level,
            'recovery_mode': self.recovery_mode,
            'actions_today': len([a for a in self.session_data.get('actions', []) 
                                 if a.get('date') == datetime.now().strftime('%Y-%m-%d')]),
            'errors_today': len([e for e in self.session_data.get('errors', [])
                                if e.get('date') == datetime.now().strftime('%Y-%m-%d')]),
            'suggested_action': self._get_safety_suggestion(),
            'risk_level': self._get_risk_level(),
            'safe_until': self._get_safe_until_time()
        }
    
    def _get_safety_suggestion(self) -> str:
        """Sugiere acción basada en nivel de riesgo"""
        if self.suspicion_level > 80:
            return "🛑 DETENER: Riesgo muy alto de baneo. Espera 24 horas."
        elif self.suspicion_level > 60:
            return "⚠️  REDUCIR: Riesgo alto. Reduce acciones a 10/día."
        elif self.suspicion_level > 40:
            return "🔶 PRECAUCIÓN: Riesgo moderado. Mantén límites actuales."
        elif self.suspicion_level > 20:
            return "🔸 NORMAL: Riesgo bajo. Puedes continuar."
        else:
            return "✅ SEGURO: Riesgo mínimo. Operación normal."
    
    def _get_risk_level(self) -> str:
        """Obtiene nivel de riesgo en texto"""
        if self.suspicion_level > 80:
            return "Muy Alto"
        elif self.suspicion_level > 60:
            return "Alto"
        elif self.suspicion_level > 40:
            return "Moderado"
        elif self.suspicion_level > 20:
            return "Bajo"
        else:
            return "Mínimo"
    
    def _get_safe_until_time(self) -> str:
        """Calcula hasta cuándo es seguro operar"""
        if self.suspicion_level > 60:
            safe_until = datetime.now() + timedelta(hours=2)
        elif self.suspicion_level > 40:
            safe_until = datetime.now() + timedelta(hours=4)
        else:
            safe_until = datetime.now() + timedelta(hours=8)
        
        return safe_until.strftime("%H:%M")
    
    def _save_session_state(self):
        """Guarda el estado de seguridad"""
        state_dir = Path('session')
        state_dir.mkdir(exist_ok=True)
        
        # Agregar estadísticas actuales
        self.session_data['last_updated'] = datetime.now().isoformat()
        self.session_data['suspicion_level'] = self.suspicion_level
        self.session_data['recovery_mode'] = self.recovery_mode
        
        with open(state_dir / 'security_state.json', 'w') as f:
            json.dump(self.session_data, f, indent=2, default=str)
    
    def reset_for_new_day(self):
        """Reinicia contadores para nuevo día"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Reducir nivel de sospecha
        self.suspicion_level = max(0, self.suspicion_level * 0.7)
        
        # Reiniciar modo recuperación si ha pasado mucho tiempo
        if self.recovery_mode:
            last_recovery = self.session_data.get('recoveries', [{}])[-1]
            if last_recovery:
                recovery_time = datetime.fromisoformat(last_recovery.get('timestamp', datetime.now().isoformat()))
                if (datetime.now() - recovery_time).total_seconds() > 7200:  # 2 horas
                    self.recovery_mode = False
        
        self.logger.info("🔄 Contadores reiniciados para nuevo día")
    
    def emergency_stop(self, reason: str):
        """Parada de emergencia - activa todas las protecciones"""
        self.suspicion_level = 100
        self.recovery_mode = True
        self.activate_recovery_mode(240)  # 4 horas
        
        emergency_record = {
            'timestamp': datetime.now().isoformat(),
            'reason': reason,
            'action': 'EMERGENCY_STOP'
        }
        
        self.session_data.setdefault('emergencies', []).append(emergency_record)
        self._save_session_state()
        
        self.logger.critical(f"🚨 PARADA DE EMERGENCIA: {reason}")
        
        return {
            'stopped': True,
            'message': f'Parada de emergencia activada: {reason}',
            'recovery_time': (datetime.now() + timedelta(hours=4)).strftime("%H:%M"),
            'recommendation': 'No uses LinkedIn manualmente por 4 horas'
        }
      
