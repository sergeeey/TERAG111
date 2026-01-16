#!/usr/bin/env python3
"""
Nightly Environment Audit Script
Автоматический ночной прогон environment-аудита с уведомлениями
"""

import os
import sys
import json
import datetime
import smtplib
import logging
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional

# Добавляем путь к audittools
sys.path.append(str(Path(__file__).parent.parent))

from audittools.cursor_env import CursorEnvironmentAuditor
from audittools.aggregate import AuditAggregator

class NightlyAuditRunner:
    """Класс для запуска ночного аудита с уведомлениями"""
    
    def __init__(self, config_path: str = ".auditconfig.yaml"):
        self.config_path = config_path
        self.reports_dir = Path("audit_reports/nightly")
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Настройка логирования
        self.setup_logging()
        
        # Загрузка конфигурации
        self.config = self.load_config()
        
        # Пороги для уведомлений
        self.thresholds = {
            'environment_score_critical': 0.5,
            'environment_score_warning': 0.7,
            'overall_score_critical': 0.4,
            'overall_score_warning': 0.6
        }
    
    def setup_logging(self):
        """Настройка логирования"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"nightly_audit_{datetime.date.today()}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        # Настраиваем кодировку для stdout
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
        
        self.logger = logging.getLogger(__name__)
    
    def load_config(self) -> Dict[str, Any]:
        """Загрузка конфигурации"""
        try:
            import yaml
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.warning(f"Не удалось загрузить конфигурацию: {e}")
            return {}
    
    def run_environment_audit(self) -> Dict[str, Any]:
        """Запуск environment-аудита"""
        try:
            self.logger.info("🔍 Запуск environment-аудита...")
            
            auditor = CursorEnvironmentAuditor()
            result = auditor.audit_environment()
            
            # Сохранение отчёта
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = self.reports_dir / f"environment_audit_{timestamp}.json"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"✅ Environment-аудит завершён. Отчёт: {report_file}")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка environment-аудита: {e}")
            return {"error": str(e), "timestamp": datetime.datetime.now().isoformat()}
    
    def run_full_audit(self) -> Dict[str, Any]:
        """Запуск полного аудита"""
        try:
            self.logger.info("🔍 Запуск полного аудита...")
            
            # Создаём временную директорию для отчётов
            temp_reports_dir = self.reports_dir / f"full_audit_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
            temp_reports_dir.mkdir(parents=True, exist_ok=True)
            
            # Запускаем environment-аудит
            env_result = self.run_environment_audit()
            env_report_file = temp_reports_dir / "cursor_env.json"
            with open(env_report_file, 'w', encoding='utf-8') as f:
                json.dump(env_result, f, indent=2, ensure_ascii=False)
            
            # Запускаем другие аудиты (если доступны)
            try:
                from audittools.cognitive import CognitiveAuditor
                cognitive_auditor = CognitiveAuditor()
                cognitive_result = cognitive_auditor.analyze_cognitive_metrics()
                cognitive_report_file = temp_reports_dir / "cognitive_metrics.json"
                with open(cognitive_report_file, 'w', encoding='utf-8') as f:
                    json.dump(cognitive_result, f, indent=2, ensure_ascii=False)
            except Exception as e:
                self.logger.warning(f"Когнитивный аудит недоступен: {e}")
            
            # Агрегируем результаты
            aggregator = AuditAggregator(str(temp_reports_dir))
            aggregated_result = aggregator.aggregate_all_results()
            
            # Сохраняем сводный отчёт
            summary_file = temp_reports_dir / "nightly_audit_summary.json"
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(aggregated_result, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"✅ Полный аудит завершён. Отчёт: {summary_file}")
            return aggregated_result
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка полного аудита: {e}")
            return {"error": str(e), "timestamp": datetime.datetime.now().isoformat()}
    
    def check_thresholds(self, audit_result: Dict[str, Any]) -> Dict[str, Any]:
        """Проверка пороговых значений"""
        alerts = []
        
        # Проверка environment_score
        if 'environment_audit' in audit_result:
            env_score = audit_result['environment_audit'].get('environment_score', 0)
            
            if env_score < self.thresholds['environment_score_critical']:
                alerts.append({
                    'type': 'critical',
                    'component': 'environment',
                    'score': env_score,
                    'threshold': self.thresholds['environment_score_critical'],
                    'message': f'Критический уровень environment-аудита: {env_score:.3f} < {self.thresholds["environment_score_critical"]}'
                })
            elif env_score < self.thresholds['environment_score_warning']:
                alerts.append({
                    'type': 'warning',
                    'component': 'environment',
                    'score': env_score,
                    'threshold': self.thresholds['environment_score_warning'],
                    'message': f'Предупреждение environment-аудита: {env_score:.3f} < {self.thresholds["environment_score_warning"]}'
                })
        
        # Проверка общей оценки
        if 'overall_assessment' in audit_result:
            overall_score = audit_result['overall_assessment'].get('overall_score', 0)
            
            if overall_score < self.thresholds['overall_score_critical']:
                alerts.append({
                    'type': 'critical',
                    'component': 'overall',
                    'score': overall_score,
                    'threshold': self.thresholds['overall_score_critical'],
                    'message': f'Критический уровень общей оценки: {overall_score:.3f} < {self.thresholds["overall_score_critical"]}'
                })
            elif overall_score < self.thresholds['overall_score_warning']:
                alerts.append({
                    'type': 'warning',
                    'component': 'overall',
                    'score': overall_score,
                    'threshold': self.thresholds['overall_score_warning'],
                    'message': f'Предупреждение общей оценки: {overall_score:.3f} < {self.thresholds["overall_score_warning"]}'
                })
        
        return {
            'alerts': alerts,
            'critical_count': len([a for a in alerts if a['type'] == 'critical']),
            'warning_count': len([a for a in alerts if a['type'] == 'warning'])
        }
    
    def send_notification(self, alerts: Dict[str, Any], audit_result: Dict[str, Any]) -> bool:
        """Отправка уведомлений"""
        if not alerts['alerts']:
            self.logger.info("✅ Нет критических проблем - уведомления не требуются")
            return True
        
        try:
            # Проверяем настройки уведомлений
            notification_config = self.config.get('notifications', {})
            
            if not notification_config.get('enabled', False):
                self.logger.info("Уведомления отключены в конфигурации")
                return True
            
            # Подготавливаем сообщение
            message = self.prepare_notification_message(alerts, audit_result)
            
            # Отправляем уведомления
            success = True
            
            # Email уведомления
            if notification_config.get('email', {}).get('enabled', False):
                success &= self.send_email_notification(message, notification_config['email'])
            
            # Slack уведомления
            if notification_config.get('slack', {}).get('enabled', False):
                success &= self.send_slack_notification(message, notification_config['slack'])
            
            # Webhook уведомления
            if notification_config.get('webhook', {}).get('enabled', False):
                success &= self.send_webhook_notification(message, notification_config['webhook'])
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка отправки уведомлений: {e}")
            return False
    
    def prepare_notification_message(self, alerts: Dict[str, Any], audit_result: Dict[str, Any]) -> str:
        """Подготовка сообщения уведомления"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        message = f"""🚨 **TERAG AI-REPS Nightly Audit Alert** - {timestamp}

**Статус:** {'🔴 КРИТИЧЕСКИЙ' if alerts['critical_count'] > 0 else '🟡 ПРЕДУПРЕЖДЕНИЕ'}

**Проблемы:**
"""
        
        for alert in alerts['alerts']:
            icon = "🔴" if alert['type'] == 'critical' else "🟡"
            message += f"{icon} {alert['message']}\n"
        
        # Добавляем детали аудита
        if 'environment_audit' in audit_result:
            env_score = audit_result['environment_audit'].get('environment_score', 0)
            message += f"\n**Environment Score:** {env_score:.3f}\n"
        
        if 'overall_assessment' in audit_result:
            overall_score = audit_result['overall_assessment'].get('overall_score', 0)
            message += f"**Overall Score:** {overall_score:.3f}\n"
        
        message += f"\n**Отчёты:** `audit_reports/nightly/`\n"
        message += f"**Время:** {timestamp}\n"
        
        return message
    
    def send_email_notification(self, message: str, email_config: Dict[str, Any]) -> bool:
        """Отправка email уведомления"""
        try:
            # Простая реализация email уведомлений
            self.logger.info("📧 Email уведомления не реализованы (требует SMTP настройки)")
            return True
        except Exception as e:
            self.logger.error(f"❌ Ошибка email уведомления: {e}")
            return False
    
    def send_slack_notification(self, message: str, slack_config: Dict[str, Any]) -> bool:
        """Отправка Slack уведомления"""
        try:
            # Простая реализация Slack уведомлений
            self.logger.info("💬 Slack уведомления не реализованы (требует webhook настройки)")
            return True
        except Exception as e:
            self.logger.error(f"❌ Ошибка Slack уведомления: {e}")
            return False
    
    def send_webhook_notification(self, message: str, webhook_config: Dict[str, Any]) -> bool:
        """Отправка webhook уведомления"""
        try:
            import requests
            
            webhook_url = webhook_config.get('url')
            if not webhook_url:
                self.logger.warning("Webhook URL не настроен")
                return False
            
            payload = {
                "text": message,
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            
            self.logger.info("✅ Webhook уведомление отправлено")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка webhook уведомления: {e}")
            return False
    
    def cleanup_old_reports(self, days_to_keep: int = 30):
        """Очистка старых отчётов"""
        try:
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days_to_keep)
            
            for report_file in self.reports_dir.glob("*.json"):
                if report_file.stat().st_mtime < cutoff_date.timestamp():
                    report_file.unlink()
                    self.logger.info(f"🗑️ Удалён старый отчёт: {report_file}")
            
            self.logger.info(f"✅ Очистка отчётов старше {days_to_keep} дней завершена")
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка очистки отчётов: {e}")
    
    def run_nightly_audit(self):
        """Основная функция ночного аудита"""
        self.logger.info("🌙 Запуск ночного аудита TERAG AI-REPS")
        
        try:
            # Запуск полного аудита
            audit_result = self.run_full_audit()
            
            # Проверка пороговых значений
            alerts = self.check_thresholds(audit_result)
            
            # Отправка уведомлений при необходимости
            self.send_notification(alerts, audit_result)
            
            # Очистка старых отчётов
            self.cleanup_old_reports()
            
            # Сводка
            self.logger.info("🎉 Ночной аудит завершён успешно")
            self.logger.info(f"📊 Критических проблем: {alerts['critical_count']}")
            self.logger.info(f"⚠️ Предупреждений: {alerts['warning_count']}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Критическая ошибка ночного аудита: {e}")
            return False

def main():
    """Основная функция"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Nightly Environment Audit for TERAG AI-REPS')
    parser.add_argument('--config', '-c', default='.auditconfig.yaml', help='Путь к конфигурации')
    parser.add_argument('--environment-only', action='store_true', help='Только environment-аудит')
    parser.add_argument('--cleanup-days', type=int, default=30, help='Дни для очистки старых отчётов')
    
    args = parser.parse_args()
    
    runner = NightlyAuditRunner(args.config)
    
    if args.environment_only:
        result = runner.run_environment_audit()
        alerts = runner.check_thresholds({'environment_audit': result})
        runner.send_notification(alerts, {'environment_audit': result})
    else:
        runner.run_nightly_audit()
    
    runner.cleanup_old_reports(args.cleanup_days)

if __name__ == "__main__":
    main()
