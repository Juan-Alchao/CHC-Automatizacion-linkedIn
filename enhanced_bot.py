"""
🤖 LINKEDIN BOT MEJORADO - Con seguridad y recuperación
Versión: 2.0 | Seguridad: Máxima
Características:
- Sistema anti-baneo avanzado
- Recuperación automática
- Backup continuo
- Monitoreo en tiempo real
"""

from safety_manager import AdvancedSafetyManager
from recovery_system import RecoverySystem
import time
from datetime import datetime

class EnhancedLinkedInBot:
    """🤖 BOT MEJORADO CON SEGURIDAD Y RECUPERACIÓN"""
    
    def __init__(self):
        self.safety = AdvancedSafetyManager()
        self.recovery = RecoverySystem()
        self.driver = None
        self.is_running = False
        
    def safe_operation(self, operation_name: str, operation_func, *args, **kwargs):
        """
        Ejecuta una operación con seguridad y recuperación
        Retorna: (success, result, error_message)
        """
        # Verificar seguridad primero
        safety_check = self.safety.can_perform_action(operation_name)
        
        if not safety_check['allowed']:
            self.safety.record_action(operation_name, False, {
                'reason': safety_check['reason'],
                'mode': safety_check['mode']
            })
            
            # Esperar delay sugerido
            if safety_check['delay'] > 0:
                print(f"⏳ Esperando {safety_check['delay']}s por seguridad...")
                time.sleep(safety_check['delay'])
            
            return False, None, safety_check['reason']
        
        # Crear backup pre-operación
        self.recovery.create_backup('pre_action', {
            'operation': operation_name,
            'timestamp': datetime.now().isoformat()
        })
        
        try:
            # Aplicar delay seguro
            time.sleep(safety_check['delay'])
            
            # Ejecutar operación
            print(f"🔄 Ejecutando: {operation_name}")
            result = operation_func(*args, **kwargs)
            
            # Registrar éxito
            self.safety.record_action(operation_name, True, {
                'delay_used': safety_check['delay'],
                'mode': safety_check['mode']
            })
            
            # Crear backup post-operación
            self.recovery.create_backup('post_action', {
                'operation': operation_name,
                'success': True,
                'result': str(result)[:100]  # Limitar tamaño
            })
            
            return True, result, "Operación exitosa"
            
        except Exception as e:
            error_msg = str(e)
            
            # Registrar error
            self.safety.record_error('operation_failed', error_msg)
            self.safety.record_action(operation_name, False, {
                'error': error_msg,
                'delay_used': safety_check['delay']
            })
            
            # Intentar recuperación automática
            print(f"⚠️  Error en {operation_name}: {error_msg}")
            print("🔄 Intentando recuperación automática...")
            
            recovery_result = self.recovery.recover_from_crash({
                'operation': operation_name,
                'error': error_msg
            })
            
            if not recovery_result['success']:
                # Si la recuperación falla, activar parada de emergencia
                emergency = self.safety.emergency_stop(
                    f"Fallo en {operation_name}: {error_msg}"
                )
                print(f"🚨 {emergency['message']}")
            
            return False, None, f"{error_msg} | Recuperación: {recovery_result.get('status', 'unknown')}"
    
    def get_system_status(self):
        """Obtiene estado completo del sistema"""
        safety_status = self.safety.get_safety_report()
        recovery_status = self.recovery.get_recovery_status()
        
        return {
            'safety': safety_status,
            'recovery': recovery_status,
            'overall_health': self._calculate_overall_health(safety_status, recovery_status),
            'recommendations': self._generate_recommendations(safety_status, recovery_status),
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_overall_health(self, safety_status, recovery_status):
        """Calcula salud general del sistema"""
        safety_score = 100 - safety_status['suspicion_level']
        recovery_score = 100 if recovery_status['system_status'] == 'healthy' else 50
        
        overall = (safety_score + recovery_score) / 2
        
        if overall >= 80:
            return "✅ Excelente"
        elif overall >= 60:
            return "🔶 Buena"
        elif overall >= 40:
            return "⚠️  Regular"
        else:
            return "🛑 Crítica"
    
    def _generate_recommendations(self, safety_status, recovery_status):
        """Genera recomendaciones basadas en estado"""
        recommendations = []
        
        # Recomendaciones de seguridad
        if safety_status['suspicion_level'] > 60:
            recommendations.append(f"🚨 Reducir actividad: {safety_status['suggested_action']}")
        
        if safety_status['recovery_mode']:
            recommendations.append("🛡️ Sistema en modo recuperación - esperar")
        
        # Recomendaciones de recuperación
        if recovery_status['system_status'] != 'healthy':
            recommendations.append(f"💾 {recovery_status['recommendation']}")
        
        if not recommendations:
            recommendations.append("✅ Todo en orden - continuar normalmente")
        
        return recommendations
      
