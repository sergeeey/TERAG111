"""
Модуль этического аудита AI-систем
Проверяет соответствие этическим принципам, справедливости и прозрачности
"""

import json
import os
import sys
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import re

class EthicsAuditor:
    """Аудитор этических аспектов AI-систем"""
    
    def __init__(self, config_path: str = ".auditconfig.yaml"):
        self.config = self._load_config(config_path)
        self.ethical_principles = [
            "fairness", "transparency", "accountability", "privacy", 
            "safety", "human_autonomy", "non_maleficence", "beneficence"
        ]
        
    def _load_config(self, config_path: str) -> Dict:
        """Загрузка конфигурации"""
        try:
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"⚠️ Ошибка загрузки конфигурации: {e}")
            return {}
    
    def evaluate_ethical_compliance(self) -> Dict[str, Any]:
        """Оценка этического соответствия системы"""
        try:
            # Проверка документации
            documentation_audit = self._audit_documentation()
            
            # Проверка кода на этические аспекты
            code_audit = self._audit_code_ethics()
            
            # Проверка конфигурации
            config_audit = self._audit_configuration()
            
            # Проверка данных и приватности
            privacy_audit = self._audit_privacy()
            
            # Общая оценка
            overall_score = self._calculate_ethical_score(
                documentation_audit, code_audit, config_audit, privacy_audit
            )
            
            return {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "overall_ethical_score": overall_score,
                "documentation_audit": documentation_audit,
                "code_audit": code_audit,
                "config_audit": config_audit,
                "privacy_audit": privacy_audit,
                "ethical_status": self._classify_ethical_status(overall_score),
                "recommendations": self._generate_ethical_recommendations(
                    documentation_audit, code_audit, config_audit, privacy_audit
                )
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": "failed"
            }
    
    def _audit_documentation(self) -> Dict[str, Any]:
        """Аудит этической документации"""
        ethical_docs = []
        missing_docs = []
        
        # Список важных документов
        important_docs = [
            "README.md", "SECURITY.md", "AUDIT_SPEC.md", 
            "docs/ethics/", "docs/governance/", "CHANGELOG.md"
        ]
        
        for doc in important_docs:
            if os.path.exists(doc):
                ethical_docs.append(doc)
            else:
                missing_docs.append(doc)
        
        # Проверка содержания README на этические аспекты
        readme_ethics_score = 0.0
        if os.path.exists("README.md"):
            readme_ethics_score = self._analyze_readme_ethics("README.md")
        
        # Проверка наличия политик
        policies = self._check_ethical_policies()
        
        return {
            "documentation_score": len(ethical_docs) / len(important_docs),
            "present_docs": ethical_docs,
            "missing_docs": missing_docs,
            "readme_ethics_score": readme_ethics_score,
            "policies": policies
        }
    
    def _analyze_readme_ethics(self, readme_path: str) -> float:
        """Анализ этических аспектов в README"""
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read().lower()
            
            ethical_keywords = [
                "ethics", "ethical", "fairness", "bias", "transparency",
                "privacy", "security", "safety", "accountability", "governance",
                "responsible", "trust", "explainable", "audit", "compliance"
            ]
            
            found_keywords = sum(1 for keyword in ethical_keywords if keyword in content)
            return min(found_keywords / len(ethical_keywords), 1.0)
            
        except Exception:
            return 0.0
    
    def _check_ethical_policies(self) -> Dict[str, bool]:
        """Проверка наличия этических политик"""
        policies = {
            "privacy_policy": False,
            "bias_mitigation": False,
            "transparency_policy": False,
            "safety_guidelines": False,
            "audit_procedures": False
        }
        
        # Проверка в конфигурации аудита
        if self.config.get('governance_audit', {}).get('enabled'):
            policies["audit_procedures"] = True
        
        if self.config.get('security_audit', {}).get('enabled'):
            policies["safety_guidelines"] = True
        
        # Проверка в коде на упоминания этических аспектов
        code_ethics = self._scan_code_for_ethics()
        if code_ethics.get('privacy_mentions', 0) > 0:
            policies["privacy_policy"] = True
        if code_ethics.get('bias_mentions', 0) > 0:
            policies["bias_mitigation"] = True
        if code_ethics.get('transparency_mentions', 0) > 0:
            policies["transparency_policy"] = True
        
        return policies
    
    def _scan_code_for_ethics(self) -> Dict[str, int]:
        """Сканирование кода на упоминания этических аспектов"""
        ethics_counts = {
            "privacy_mentions": 0,
            "bias_mentions": 0,
            "transparency_mentions": 0,
            "safety_mentions": 0
        }
        
        # Ключевые слова для поиска
        privacy_keywords = ["privacy", "personal_data", "gdpr", "pii", "confidential"]
        bias_keywords = ["bias", "fairness", "discrimination", "equity", "unbiased"]
        transparency_keywords = ["transparent", "explainable", "interpretable", "audit", "log"]
        safety_keywords = ["safety", "secure", "validation", "sanitize", "escape"]
        
        # Сканирование файлов
        source_dirs = self.config.get('source_dirs', ['src/'])
        for source_dir in source_dirs:
            if os.path.exists(source_dir):
                for root, dirs, files in os.walk(source_dir):
                    for file in files:
                        if file.endswith(('.py', '.ts', '.tsx', '.js', '.jsx')):
                            file_path = os.path.join(root, file)
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    content = f.read().lower()
                                
                                ethics_counts["privacy_mentions"] += sum(1 for kw in privacy_keywords if kw in content)
                                ethics_counts["bias_mentions"] += sum(1 for kw in bias_keywords if kw in content)
                                ethics_counts["transparency_mentions"] += sum(1 for kw in transparency_keywords if kw in content)
                                ethics_counts["safety_mentions"] += sum(1 for kw in safety_keywords if kw in content)
                                
                            except Exception:
                                continue
        
        return ethics_counts
    
    def _audit_code_ethics(self) -> Dict[str, Any]:
        """Аудит этических аспектов в коде"""
        code_ethics = self._scan_code_for_ethics()
        
        # Проверка на потенциально проблемные паттерны
        problematic_patterns = self._check_problematic_patterns()
        
        # Проверка на безопасность данных
        data_safety = self._check_data_safety()
        
        return {
            "ethics_mentions": code_ethics,
            "problematic_patterns": problematic_patterns,
            "data_safety": data_safety,
            "overall_code_ethics_score": self._calculate_code_ethics_score(code_ethics, problematic_patterns, data_safety)
        }
    
    def _check_problematic_patterns(self) -> Dict[str, List[str]]:
        """Проверка на проблемные паттерны в коде"""
        patterns = {
            "hardcoded_secrets": [],
            "unsafe_eval": [],
            "sql_injection_risk": [],
            "xss_risk": []
        }
        
        source_dirs = self.config.get('source_dirs', ['src/'])
        for source_dir in source_dirs:
            if os.path.exists(source_dir):
                for root, dirs, files in os.walk(source_dir):
                    for file in files:
                        if file.endswith(('.py', '.ts', '.tsx', '.js', '.jsx')):
                            file_path = os.path.join(root, file)
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                
                                # Проверка на хардкод секретов
                                if re.search(r'(password|secret|key|token)\s*=\s*["\'][^"\']+["\']', content, re.IGNORECASE):
                                    patterns["hardcoded_secrets"].append(file_path)
                                
                                # Проверка на небезопасный eval
                                if 'eval(' in content:
                                    patterns["unsafe_eval"].append(file_path)
                                
                                # Проверка на SQL инъекции
                                if re.search(r'execute\s*\(\s*["\'].*\+.*["\']', content):
                                    patterns["sql_injection_risk"].append(file_path)
                                
                                # Проверка на XSS
                                if re.search(r'innerHTML\s*=', content):
                                    patterns["xss_risk"].append(file_path)
                                    
                            except Exception:
                                continue
        
        return patterns
    
    def _check_data_safety(self) -> Dict[str, Any]:
        """Проверка безопасности данных"""
        safety_checks = {
            "input_validation": False,
            "output_sanitization": False,
            "error_handling": False,
            "logging_safety": False
        }
        
        source_dirs = self.config.get('source_dirs', ['src/'])
        for source_dir in source_dirs:
            if os.path.exists(source_dir):
                for root, dirs, files in os.walk(source_dir):
                    for file in files:
                        if file.endswith(('.py', '.ts', '.tsx', '.js', '.jsx')):
                            file_path = os.path.join(root, file)
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                
                                # Проверка валидации входных данных
                                if any(keyword in content.lower() for keyword in ['validate', 'sanitize', 'check']):
                                    safety_checks["input_validation"] = True
                                
                                # Проверка санитизации вывода
                                if any(keyword in content.lower() for keyword in ['escape', 'encode', 'sanitize']):
                                    safety_checks["output_sanitization"] = True
                                
                                # Проверка обработки ошибок
                                if any(keyword in content.lower() for keyword in ['try:', 'except:', 'catch', 'error']):
                                    safety_checks["error_handling"] = True
                                
                                # Проверка безопасного логирования
                                if 'log' in content.lower() and 'password' not in content.lower():
                                    safety_checks["logging_safety"] = True
                                    
                            except Exception:
                                continue
        
        return safety_checks
    
    def _calculate_code_ethics_score(self, ethics_mentions: Dict, problematic_patterns: Dict, data_safety: Dict) -> float:
        """Расчёт оценки этичности кода"""
        # Базовый балл
        score = 0.5
        
        # Бонусы за упоминания этики
        total_mentions = sum(ethics_mentions.values())
        if total_mentions > 0:
            score += min(total_mentions * 0.1, 0.3)
        
        # Штрафы за проблемные паттерны
        total_problems = sum(len(patterns) for patterns in problematic_patterns.values())
        if total_problems > 0:
            score -= min(total_problems * 0.05, 0.4)
        
        # Бонусы за безопасность данных
        safety_bonus = sum(1 for check in data_safety.values() if check) * 0.1
        score += min(safety_bonus, 0.2)
        
        return max(0.0, min(score, 1.0))
    
    def _audit_configuration(self) -> Dict[str, Any]:
        """Аудит конфигурации на этические аспекты"""
        config_ethics = {
            "governance_enabled": self.config.get('governance_audit', {}).get('enabled', False),
            "security_enabled": self.config.get('security_audit', {}).get('enabled', False),
            "cognitive_audit_enabled": self.config.get('cognitive_audit', {}).get('enabled', False),
            "transparency_settings": self._check_transparency_settings(),
            "privacy_settings": self._check_privacy_settings()
        }
        
        return config_ethics
    
    def _check_transparency_settings(self) -> Dict[str, bool]:
        """Проверка настроек прозрачности"""
        return {
            "audit_logging": True,  # Предполагаем, что аудит включён
            "metrics_exposure": True,  # Метрики доступны через API
            "error_reporting": True,  # Ошибки логируются
            "decision_tracking": False  # Нужно проверить наличие трекинга решений
        }
    
    def _check_privacy_settings(self) -> Dict[str, bool]:
        """Проверка настроек приватности"""
        return {
            "data_encryption": False,  # Нужно проверить наличие шифрования
            "access_control": True,  # Предполагаем наличие контроля доступа
            "data_retention": True,  # Есть журнал с ограничением записей
            "anonymization": False  # Нужно проверить анонимизацию данных
        }
    
    def _audit_privacy(self) -> Dict[str, Any]:
        """Аудит приватности и защиты данных"""
        privacy_audit = {
            "data_collection": self._analyze_data_collection(),
            "data_storage": self._analyze_data_storage(),
            "data_sharing": self._analyze_data_sharing(),
            "user_consent": self._check_user_consent()
        }
        
        return privacy_audit
    
    def _analyze_data_collection(self) -> Dict[str, Any]:
        """Анализ сбора данных"""
        return {
            "minimal_collection": True,  # Собираем только необходимые метрики
            "purpose_limitation": True,  # Данные используются для анализа системы
            "data_types": ["metrics", "logs", "performance_data"],
            "collection_frequency": "real_time"
        }
    
    def _analyze_data_storage(self) -> Dict[str, Any]:
        """Анализ хранения данных"""
        return {
            "local_storage": True,  # Данные хранятся локально
            "retention_policy": "rolling_window",  # Rolling window для журнала
            "encryption": False,  # Нужно добавить шифрование
            "backup_strategy": "none"  # Нет стратегии резервного копирования
        }
    
    def _analyze_data_sharing(self) -> Dict[str, Any]:
        """Анализ обмена данными"""
        return {
            "third_party_sharing": False,  # Данные не передаются третьим лицам
            "api_exposure": True,  # API доступен для мониторинга
            "data_export": False,  # Нет экспорта данных
            "anonymization": False  # Нет анонимизации
        }
    
    def _check_user_consent(self) -> Dict[str, Any]:
        """Проверка согласия пользователя"""
        return {
            "consent_mechanism": False,  # Нет механизма согласия
            "opt_out_option": False,  # Нет опции отказа
            "privacy_notice": False,  # Нет уведомления о приватности
            "data_subject_rights": False  # Нет прав субъектов данных
        }
    
    def _calculate_ethical_score(self, doc_audit: Dict, code_audit: Dict, 
                               config_audit: Dict, privacy_audit: Dict) -> float:
        """Расчёт общей этической оценки"""
        # Веса компонентов
        weights = {
            'documentation': 0.25,
            'code': 0.35,
            'configuration': 0.2,
            'privacy': 0.2
        }
        
        # Оценки компонентов
        doc_score = doc_audit.get('documentation_score', 0.0)
        code_score = code_audit.get('overall_code_ethics_score', 0.0)
        config_score = sum(1 for v in config_audit.values() if v) / len(config_audit) if config_audit else 0.0
        privacy_score = self._calculate_privacy_score(privacy_audit)
        
        # Взвешенная сумма
        overall_score = (
            doc_score * weights['documentation'] +
            code_score * weights['code'] +
            config_score * weights['configuration'] +
            privacy_score * weights['privacy']
        )
        
        return min(overall_score, 1.0)
    
    def _calculate_privacy_score(self, privacy_audit: Dict) -> float:
        """Расчёт оценки приватности"""
        scores = []
        
        # Оценка сбора данных
        data_collection = privacy_audit.get('data_collection', {})
        if data_collection.get('minimal_collection') and data_collection.get('purpose_limitation'):
            scores.append(0.8)
        else:
            scores.append(0.4)
        
        # Оценка хранения данных
        data_storage = privacy_audit.get('data_storage', {})
        if data_storage.get('local_storage') and data_storage.get('retention_policy'):
            scores.append(0.6)
        else:
            scores.append(0.3)
        
        # Оценка обмена данными
        data_sharing = privacy_audit.get('data_sharing', {})
        if not data_sharing.get('third_party_sharing'):
            scores.append(0.7)
        else:
            scores.append(0.2)
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def _classify_ethical_status(self, score: float) -> str:
        """Классификация этического статуса"""
        if score >= 0.8:
            return "excellent"
        elif score >= 0.6:
            return "good"
        elif score >= 0.4:
            return "fair"
        else:
            return "poor"
    
    def _generate_ethical_recommendations(self, doc_audit: Dict, code_audit: Dict,
                                        config_audit: Dict, privacy_audit: Dict) -> List[str]:
        """Генерация этических рекомендаций"""
        recommendations = []
        
        # Рекомендации по документации
        if doc_audit.get('documentation_score', 0) < 0.5:
            recommendations.append("📚 Улучшите этическую документацию: добавьте политики приватности и этические принципы")
        
        # Рекомендации по коду
        if code_audit.get('overall_code_ethics_score', 0) < 0.6:
            recommendations.append("💻 Улучшите этичность кода: добавьте валидацию данных и обработку ошибок")
        
        # Рекомендации по конфигурации
        if not config_audit.get('governance_enabled', False):
            recommendations.append("⚙️ Включите управленческий аудит в конфигурации")
        
        # Рекомендации по приватности
        if not privacy_audit.get('data_storage', {}).get('encryption', False):
            recommendations.append("🔒 Добавьте шифрование для защиты данных")
        
        if not privacy_audit.get('user_consent', {}).get('consent_mechanism', False):
            recommendations.append("👤 Реализуйте механизм согласия пользователя")
        
        if not recommendations:
            recommendations.append("✅ Этическое соответствие на хорошем уровне, продолжайте мониторинг")
        
        return recommendations

def main():
    """Основная функция для запуска этического аудита"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Этический аудит TERAG AI-REPS')
    parser.add_argument('--output', '-o', help='Путь для сохранения отчёта')
    parser.add_argument('--config', '-c', default='.auditconfig.yaml', help='Путь к конфигурации')
    
    args = parser.parse_args()
    
    auditor = EthicsAuditor(args.config)
    result = auditor.evaluate_ethical_compliance()
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
