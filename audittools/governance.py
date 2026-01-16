"""
Модуль управленческого аудита AI-систем
Проверяет соответствие корпоративным политикам, миссии и управленческим стандартам
"""

import json
import os
import sys
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import re

class GovernanceAuditor:
    """Аудитор управленческих аспектов AI-систем"""
    
    def __init__(self, config_path: str = ".auditconfig.yaml"):
        self.config = self._load_config(config_path)
        self.governance_frameworks = [
            "COBIT", "ISO_27001", "ISO_42010", "ITAF", "DORA", "NIST_AI_RMF"
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
    
    def evaluate_governance(self) -> Dict[str, Any]:
        """Оценка управленческого соответствия системы"""
        try:
            # Проверка миссии и стратегии
            mission_audit = self._audit_mission_alignment()
            
            # Проверка политик и процедур
            policies_audit = self._audit_policies()
            
            # Проверка ролей и ответственности
            roles_audit = self._audit_roles_responsibilities()
            
            # Проверка соответствия стандартам
            compliance_audit = self._audit_compliance()
            
            # Проверка непрерывности управления
            continuity_audit = self._audit_continuity()
            
            # Общая оценка
            overall_score = self._calculate_governance_score(
                mission_audit, policies_audit, roles_audit, compliance_audit, continuity_audit
            )
            
            return {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "overall_governance_score": overall_score,
                "mission_audit": mission_audit,
                "policies_audit": policies_audit,
                "roles_audit": roles_audit,
                "compliance_audit": compliance_audit,
                "continuity_audit": continuity_audit,
                "governance_status": self._classify_governance_status(overall_score),
                "recommendations": self._generate_governance_recommendations(
                    mission_audit, policies_audit, roles_audit, compliance_audit, continuity_audit
                )
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": "failed"
            }
    
    def _audit_mission_alignment(self) -> Dict[str, Any]:
        """Аудит соответствия миссии"""
        mission_indicators = {
            "mission_statement": False,
            "strategic_objectives": False,
            "value_proposition": False,
            "stakeholder_identification": False,
            "success_metrics": False
        }
        
        # Проверка README на наличие миссии
        if os.path.exists("README.md"):
            readme_content = self._read_file_safe("README.md")
            if readme_content:
                mission_keywords = ["mission", "purpose", "goal", "objective", "vision"]
                if any(keyword in readme_content.lower() for keyword in mission_keywords):
                    mission_indicators["mission_statement"] = True
        
        # Проверка документации архитектуры
        if os.path.exists("docs/architecture/"):
            mission_indicators["strategic_objectives"] = True
        
        # Проверка метрик успеха
        if self.config.get('cognitive_audit', {}).get('enabled'):
            mission_indicators["success_metrics"] = True
        
        # Проверка идентификации заинтересованных сторон
        if os.path.exists("docs/") or os.path.exists("SECURITY.md"):
            mission_indicators["stakeholder_identification"] = True
        
        return {
            "indicators": mission_indicators,
            "alignment_score": sum(mission_indicators.values()) / len(mission_indicators),
            "mission_clarity": self._assess_mission_clarity()
        }
    
    def _assess_mission_clarity(self) -> Dict[str, Any]:
        """Оценка ясности миссии"""
        clarity_indicators = {
            "clear_objectives": False,
            "measurable_outcomes": False,
            "stakeholder_focus": False,
            "value_articulation": False
        }
        
        # Анализ README
        if os.path.exists("README.md"):
            readme_content = self._read_file_safe("README.md")
            if readme_content:
                # Проверка на измеримые результаты
                if any(word in readme_content.lower() for word in ["metrics", "measure", "kpi", "score"]):
                    clarity_indicators["measurable_outcomes"] = True
                
                # Проверка на фокус на пользователях
                if any(word in readme_content.lower() for word in ["user", "stakeholder", "customer", "audience"]):
                    clarity_indicators["stakeholder_focus"] = True
                
                # Проверка на артикуляцию ценности
                if any(word in readme_content.lower() for word in ["benefit", "value", "advantage", "improve"]):
                    clarity_indicators["value_articulation"] = True
        
        return clarity_indicators
    
    def _audit_policies(self) -> Dict[str, Any]:
        """Аудит политик и процедур"""
        policy_areas = {
            "security_policy": False,
            "data_policy": False,
            "audit_policy": False,
            "change_management": False,
            "incident_response": False,
            "risk_management": False
        }
        
        # Проверка наличия политик
        if os.path.exists("SECURITY.md"):
            policy_areas["security_policy"] = True
        
        if os.path.exists("AUDIT_SPEC.md"):
            policy_areas["audit_policy"] = True
        
        # Проверка конфигурации на политики
        if self.config.get('security_audit', {}).get('enabled'):
            policy_areas["security_policy"] = True
        
        if self.config.get('governance_audit', {}).get('enabled'):
            policy_areas["audit_policy"] = True
        
        # Проверка на управление изменениями
        if os.path.exists("CHANGELOG.md"):
            policy_areas["change_management"] = True
        
        # Проверка на управление рисками
        if self.config.get('thresholds'):
            policy_areas["risk_management"] = True
        
        return {
            "policy_areas": policy_areas,
            "policy_coverage": sum(policy_areas.values()) / len(policy_areas),
            "policy_quality": self._assess_policy_quality()
        }
    
    def _assess_policy_quality(self) -> Dict[str, Any]:
        """Оценка качества политик"""
        quality_indicators = {
            "comprehensive": False,
            "up_to_date": False,
            "actionable": False,
            "enforceable": False
        }
        
        # Проверка актуальности (наличие дат в документах)
        if os.path.exists("CHANGELOG.md"):
            changelog_content = self._read_file_safe("CHANGELOG.md")
            if changelog_content and "2024" in changelog_content or "2025" in changelog_content:
                quality_indicators["up_to_date"] = True
        
        # Проверка комплексности (наличие множества политик)
        policy_count = sum(1 for policy in self.config.get('governance_audit', {}).get('checks', []) if policy)
        if policy_count >= 3:
            quality_indicators["comprehensive"] = True
        
        # Проверка действенности (наличие конкретных действий)
        if self.config.get('governance_audit', {}).get('enabled'):
            quality_indicators["actionable"] = True
        
        return quality_indicators
    
    def _audit_roles_responsibilities(self) -> Dict[str, Any]:
        """Аудит ролей и ответственности"""
        roles_indicators = {
            "clear_ownership": False,
            "defined_roles": False,
            "accountability_mechanisms": False,
            "escalation_procedures": False,
            "decision_making_process": False
        }
        
        # Проверка наличия определённых ролей в коде
        source_dirs = self.config.get('source_dirs', ['src/'])
        for source_dir in source_dirs:
            if os.path.exists(source_dir):
                for root, dirs, files in os.walk(source_dir):
                    for file in files:
                        if file.endswith(('.py', '.ts', '.tsx', '.js', '.jsx')):
                            file_path = os.path.join(root, file)
                            content = self._read_file_safe(file_path)
                            if content:
                                # Поиск упоминаний ролей и ответственности
                                if any(keyword in content.lower() for keyword in ["owner", "responsible", "accountable", "role"]):
                                    roles_indicators["defined_roles"] = True
                                if any(keyword in content.lower() for keyword in ["escalate", "escalation", "escalate"]):
                                    roles_indicators["escalation_procedures"] = True
                                if any(keyword in content.lower() for keyword in ["decision", "decide", "choice"]):
                                    roles_indicators["decision_making_process"] = True
        
        # Проверка механизмов подотчётности
        if self.config.get('governance_audit', {}).get('enabled'):
            roles_indicators["accountability_mechanisms"] = True
        
        return {
            "roles_indicators": roles_indicators,
            "roles_score": sum(roles_indicators.values()) / len(roles_indicators),
            "raci_matrix": self._assess_raci_matrix()
        }
    
    def _assess_raci_matrix(self) -> Dict[str, Any]:
        """Оценка матрицы RACI"""
        raci_indicators = {
            "responsible_defined": False,
            "accountable_defined": False,
            "consulted_defined": False,
            "informed_defined": False
        }
        
        # Поиск упоминаний RACI в документации
        if os.path.exists("README.md"):
            readme_content = self._read_file_safe("README.md")
            if readme_content:
                raci_keywords = ["responsible", "accountable", "consulted", "informed", "raci"]
                if any(keyword in readme_content.lower() for keyword in raci_keywords):
                    raci_indicators["responsible_defined"] = True
                    raci_indicators["accountable_defined"] = True
        
        return raci_indicators
    
    def _audit_compliance(self) -> Dict[str, Any]:
        """Аудит соответствия стандартам"""
        compliance_areas = {
            "iso_27001": False,
            "iso_42010": False,
            "cobit": False,
            "nist_ai_rmf": False,
            "dora": False,
            "owasp_llm": False
        }
        
        # Проверка соответствия ISO 27001 (безопасность)
        if self.config.get('security_audit', {}).get('enabled'):
            compliance_areas["iso_27001"] = True
        
        # Проверка соответствия ISO 42010 (архитектура)
        if os.path.exists("docs/architecture/"):
            compliance_areas["iso_42010"] = True
        
        # Проверка соответствия COBIT (управление IT)
        if self.config.get('governance_audit', {}).get('enabled'):
            compliance_areas["cobit"] = True
        
        # Проверка соответствия NIST AI RMF
        if self.config.get('cognitive_audit', {}).get('enabled'):
            compliance_areas["nist_ai_rmf"] = True
        
        # Проверка соответствия DORA (DevOps)
        if os.path.exists(".github/workflows/") or os.path.exists("docker-compose.yml"):
            compliance_areas["dora"] = True
        
        # Проверка соответствия OWASP LLM
        if self.config.get('security_audit', {}).get('checks'):
            owasp_checks = self.config['security_audit']['checks']
            if any(check in owasp_checks for check in ["prompt_injection", "data_leakage", "model_poisoning"]):
                compliance_areas["owasp_llm"] = True
        
        return {
            "compliance_areas": compliance_areas,
            "compliance_score": sum(compliance_areas.values()) / len(compliance_areas),
            "certification_readiness": self._assess_certification_readiness(compliance_areas)
        }
    
    def _assess_certification_readiness(self, compliance_areas: Dict[str, bool]) -> Dict[str, Any]:
        """Оценка готовности к сертификации"""
        readiness_indicators = {
            "documentation_complete": False,
            "processes_defined": False,
            "metrics_established": False,
            "audit_trail": False,
            "continuous_improvement": False
        }
        
        # Проверка полноты документации
        if os.path.exists("docs/") and os.path.exists("README.md") and os.path.exists("SECURITY.md"):
            readiness_indicators["documentation_complete"] = True
        
        # Проверка определённости процессов
        if self.config.get('governance_audit', {}).get('enabled'):
            readiness_indicators["processes_defined"] = True
        
        # Проверка установленных метрик
        if self.config.get('cognitive_audit', {}).get('metrics'):
            readiness_indicators["metrics_established"] = True
        
        # Проверка аудиторского следа
        if os.path.exists("audit_reports/"):
            readiness_indicators["audit_trail"] = True
        
        # Проверка непрерывного улучшения
        if os.path.exists("CHANGELOG.md"):
            readiness_indicators["continuous_improvement"] = True
        
        return readiness_indicators
    
    def _audit_continuity(self) -> Dict[str, Any]:
        """Аудит непрерывности управления"""
        continuity_indicators = {
            "succession_planning": False,
            "knowledge_management": False,
            "change_control": False,
            "stakeholder_engagement": False,
            "performance_monitoring": False
        }
        
        # Проверка планирования преемственности
        if os.path.exists("docs/") and os.path.exists("README.md"):
            continuity_indicators["succession_planning"] = True
        
        # Проверка управления знаниями
        if os.path.exists("docs/architecture/") or os.path.exists("docs/tasks/"):
            continuity_indicators["knowledge_management"] = True
        
        # Проверка контроля изменений
        if os.path.exists("CHANGELOG.md"):
            continuity_indicators["change_control"] = True
        
        # Проверка вовлечения заинтересованных сторон
        if os.path.exists("SECURITY.md") or os.path.exists("AUDIT_SPEC.md"):
            continuity_indicators["stakeholder_engagement"] = True
        
        # Проверка мониторинга производительности
        if self.config.get('cognitive_audit', {}).get('enabled'):
            continuity_indicators["performance_monitoring"] = True
        
        return {
            "continuity_indicators": continuity_indicators,
            "continuity_score": sum(continuity_indicators.values()) / len(continuity_indicators),
            "resilience_assessment": self._assess_resilience()
        }
    
    def _assess_resilience(self) -> Dict[str, Any]:
        """Оценка устойчивости системы"""
        resilience_indicators = {
            "backup_strategy": False,
            "disaster_recovery": False,
            "business_continuity": False,
            "risk_mitigation": False,
            "monitoring_alerting": False
        }
        
        # Проверка стратегии резервного копирования
        if os.path.exists("data/journal/"):
            resilience_indicators["backup_strategy"] = True
        
        # Проверка восстановления после сбоев
        if self.config.get('performance_audit', {}).get('enabled'):
            resilience_indicators["disaster_recovery"] = True
        
        # Проверка непрерывности бизнеса
        if self.config.get('governance_audit', {}).get('enabled'):
            resilience_indicators["business_continuity"] = True
        
        # Проверка снижения рисков
        if self.config.get('thresholds'):
            resilience_indicators["risk_mitigation"] = True
        
        # Проверка мониторинга и оповещений
        if self.config.get('cognitive_audit', {}).get('enabled'):
            resilience_indicators["monitoring_alerting"] = True
        
        return resilience_indicators
    
    def _calculate_governance_score(self, mission_audit: Dict, policies_audit: Dict,
                                  roles_audit: Dict, compliance_audit: Dict, 
                                  continuity_audit: Dict) -> float:
        """Расчёт общей оценки управления"""
        # Веса компонентов
        weights = {
            'mission': 0.25,
            'policies': 0.2,
            'roles': 0.2,
            'compliance': 0.2,
            'continuity': 0.15
        }
        
        # Оценки компонентов
        mission_score = mission_audit.get('alignment_score', 0.0)
        policies_score = policies_audit.get('policy_coverage', 0.0)
        roles_score = roles_audit.get('roles_score', 0.0)
        compliance_score = compliance_audit.get('compliance_score', 0.0)
        continuity_score = continuity_audit.get('continuity_score', 0.0)
        
        # Взвешенная сумма
        overall_score = (
            mission_score * weights['mission'] +
            policies_score * weights['policies'] +
            roles_score * weights['roles'] +
            compliance_score * weights['compliance'] +
            continuity_score * weights['continuity']
        )
        
        return min(overall_score, 1.0)
    
    def _classify_governance_status(self, score: float) -> str:
        """Классификация статуса управления"""
        if score >= 0.8:
            return "excellent"
        elif score >= 0.6:
            return "good"
        elif score >= 0.4:
            return "fair"
        else:
            return "poor"
    
    def _generate_governance_recommendations(self, mission_audit: Dict, policies_audit: Dict,
                                           roles_audit: Dict, compliance_audit: Dict,
                                           continuity_audit: Dict) -> List[str]:
        """Генерация управленческих рекомендаций"""
        recommendations = []
        
        # Рекомендации по миссии
        if mission_audit.get('alignment_score', 0) < 0.6:
            recommendations.append("🎯 Улучшите выравнивание миссии: чётко определите цели и ценности проекта")
        
        # Рекомендации по политикам
        if policies_audit.get('policy_coverage', 0) < 0.5:
            recommendations.append("📋 Расширьте политики: добавьте недостающие политики безопасности и данных")
        
        # Рекомендации по ролям
        if roles_audit.get('roles_score', 0) < 0.5:
            recommendations.append("👥 Определите роли и ответственность: создайте матрицу RACI")
        
        # Рекомендации по соответствию
        if compliance_audit.get('compliance_score', 0) < 0.5:
            recommendations.append("📜 Улучшите соответствие стандартам: внедрите недостающие элементы соответствия")
        
        # Рекомендации по непрерывности
        if continuity_audit.get('continuity_score', 0) < 0.5:
            recommendations.append("🔄 Улучшите непрерывность управления: добавьте планы преемственности и восстановления")
        
        if not recommendations:
            recommendations.append("✅ Управленческое соответствие на хорошем уровне, продолжайте улучшения")
        
        return recommendations
    
    def _read_file_safe(self, file_path: str) -> Optional[str]:
        """Безопасное чтение файла"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return None

def main():
    """Основная функция для запуска управленческого аудита"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Управленческий аудит TERAG AI-REPS')
    parser.add_argument('--output', '-o', help='Путь для сохранения отчёта')
    parser.add_argument('--config', '-c', default='.auditconfig.yaml', help='Путь к конфигурации')
    
    args = parser.parse_args()
    
    auditor = GovernanceAuditor(args.config)
    result = auditor.evaluate_governance()
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()



































