"""
Alert Manager Module
Enhanced alert system with persistence and real-time monitoring
"""

from datetime import datetime
from helpers import setup_logger
from alerts_service import generate_alerts

logger = setup_logger(__name__)


class AlertManager:
    """
    Manages weather alerts with history tracking
    """
    
    def __init__(self, max_history=1000):
        self.active_alerts = {}  # city -> list of active alerts
        self.alert_history = deque(maxlen=max_history)
        self.lock = Lock()
        logger.info(f"AlertManager initialized with history size: {max_history}")
    
    def process_weather(self, city, weather_data):
        """Process weather data and generate/update alerts"""
        with self.lock:
            # Generate alerts from weather data
            alerts_result = generate_alerts(weather_data)
            
            # Update active alerts
            if alerts_result['alerts_active']:
                self.active_alerts[city] = {
                    'timestamp': datetime.now().isoformat(),
                    'alerts': alerts_result['alerts'],
                    'weather': {
                        'temperature': weather_data.get('temperature'),
                        'condition': weather_data.get('condition'),
                        'humidity': weather_data.get('humidity')
                    }
                }
                logger.warning(f"Active alerts for {city}: {len(alerts_result['alerts'])} alert(s)")
            else:
                if city in self.active_alerts:
                    del self.active_alerts[city]
                    logger.info(f"Alerts cleared for {city}")
            
            # Record in history
            self.alert_history.append({
                'city': city,
                'timestamp': datetime.now().isoformat(),
                'alerts_active': alerts_result['alerts_active'],
                'alert_count': len(alerts_result['alerts']) if alerts_result['alerts_active'] else 0
            })
            
            return alerts_result
    
    def get_active_alerts(self, city=None):
        """Get active alerts for city or all cities"""
        with self.lock:
            if city:
                return self.active_alerts.get(city, {})
            return self.active_alerts.copy()
    
    def get_alert_summary(self):
        """Get summary of all active alerts"""
        with self.lock:
            total_alerts = sum(len(v['alerts']) for v in self.active_alerts.values())
            return {
                'total_cities_with_alerts': len(self.active_alerts),
                'total_active_alerts': total_alerts,
                'alerts_by_severity': self._group_by_severity(),
                'cities_affected': list(self.active_alerts.keys())
            }
    
    def _group_by_severity(self):
        """Group alerts by severity level"""
        severity_count = {'critical': 0, 'warning': 0, 'info': 0}
        
        for city_alerts in self.active_alerts.values():
            for alert in city_alerts.get('alerts', []):
                severity = alert.get('severity', 'info')
                if severity in severity_count:
                    severity_count[severity] += 1
        
        return severity_count
    
    def get_history(self, limit=100):
        """Get recent alert history"""
        with self.lock:
            return list(self.alert_history)[-limit:]


from threading import Lock
from collections import deque

# Global alert manager instance
alert_manager = AlertManager()
