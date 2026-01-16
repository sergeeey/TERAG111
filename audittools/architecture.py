#!/usr/bin/env python3
"""
Architecture Audit Blueprint for TERAG AI-REPS
Проверяет, совпадает ли реальная структура reasoning-пайплайна
с эталонным описанием в AUDIT_ARCHITECTURE.md
"""

import re
import os
import json
import pathlib
import datetime
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass


@dataclass
class ArchitectureSection:
    """Представление секции архитектурного документа"""
    title: str
    content: str
    subsections: List[str]
    keywords: List[str]
    expected_components: List[str]


@dataclass
class CodeModule:
    """Представление модуля кода"""
    path: str
    name: str
    functions: List[str]
    classes: List[str]
    imports: List[str]
    size: int


class ArchitectureAuditor:
    """Аудитор архитектурного соответствия"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = pathlib.Path(project_root)
        self.src_dir = self.project_root / "src"
        self.docs_dir = self.project_root / "docs"
        
        # Ожидаемые архитектурные компоненты
        self.expected_components = {
            "context_analysis": ["context", "analysis", "parsing", "validation"],
            "reasoning_chain": ["reasoning", "planning", "decomposition", "execution"],
            "tool_selection": ["tool", "selection", "algorithm", "criteria"],
            "error_handling": ["error", "recovery", "uncertainty", "fallback"],
            "resource_management": ["resource", "limit", "constraint", "timeout"],
            "user_interaction": ["user", "interaction", "memory", "conversation"],
            "self_monitoring": ["monitoring", "reflection", "meta", "self"],
            "project_adaptation": ["project", "adaptation", "specific", "integration"]
        }
        
        # Ключевые слова для каждой секции
        self.section_keywords = {
            "1": ["архитектура", "обработка", "запрос", "инициализация", "контекст"],
            "2": ["когнитивная", "reasoning", "chain", "meta", "cognitive"],
            "3": ["инструмент", "tool", "selection", "algorithm", "criteria"],
            "4": ["неопределенность", "ошибка", "uncertainty", "error", "recovery"],
            "5": ["ограничение", "критерий", "limit", "constraint", "completion"],
            "6": ["пользователь", "user", "interaction", "memory", "conversation"],
            "7": ["самопроверка", "monitoring", "reflection", "meta", "self"],
            "8": ["специализированный", "project", "adaptation", "specific", "integration"]
        }
    
    def parse_blueprint(self, md_path: str) -> Dict[str, ArchitectureSection]:
        """Парсинг архитектурного документа"""
        try:
            with open(md_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            return {}
        
        # Извлекаем основные секции
        section_pattern = r'##\s+(\d+\.\s[^\n]+)\n([\s\S]*?)(?=\n##|\Z)'
        sections = re.findall(section_pattern, content)
        
        parsed_sections = {}
        
        for title, content in sections:
            section_num = title.split('.')[0].strip()
            
            # Извлекаем подсекции
            subsection_pattern = r'###\s+([^\n]+)'
            subsections = re.findall(subsection_pattern, content)
            
            # Извлекаем ключевые слова
            keywords = self.section_keywords.get(section_num, [])
            
            # Определяем ожидаемые компоненты
            expected_components = []
            for component, keywords_list in self.expected_components.items():
                if any(keyword in content.lower() for keyword in keywords_list):
                    expected_components.append(component)
            
            parsed_sections[section_num] = ArchitectureSection(
                title=title.strip(),
                content=content.strip(),
                subsections=subsections,
                keywords=keywords,
                expected_components=expected_components
            )
        
        return parsed_sections
    
    def analyze_codebase(self) -> List[CodeModule]:
        """Анализ кодовой базы проекта"""
        modules = []
        
        if not self.src_dir.exists():
            return modules
        
        for py_file in self.src_dir.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Извлекаем функции
                function_pattern = r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
                functions = re.findall(function_pattern, content)
                
                # Извлекаем классы
                class_pattern = r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[\(:]'
                classes = re.findall(class_pattern, content)
                
                # Извлекаем импорты
                import_pattern = r'(?:from\s+(\S+)\s+)?import\s+([^\n]+)'
                imports = re.findall(import_pattern, content)
                import_list = [f"{imp[0]}.{imp[1]}" if imp[0] else imp[1] for imp in imports]
                
                # Размер файла
                size = len(content.split('\n'))
                
                # Относительный путь
                rel_path = py_file.relative_to(self.project_root)
                
                modules.append(CodeModule(
                    path=str(rel_path),
                    name=py_file.stem,
                    functions=functions,
                    classes=classes,
                    imports=import_list,
                    size=size
                ))
                
            except Exception as e:
                print(f"Ошибка анализа файла {py_file}: {e}")
                continue
        
        return modules
    
    def check_architecture_compliance(self, blueprint: Dict[str, ArchitectureSection], 
                                    modules: List[CodeModule]) -> Dict[str, Any]:
        """Проверка соответствия архитектуре"""
        issues = []
        matches = 0
        total_sections = len(blueprint)
        
        # Проверяем наличие всех ожидаемых секций
        expected_sections = ["1", "2", "3", "4", "5", "6", "7", "8"]
        for section_num in expected_sections:
            if section_num not in blueprint:
                issues.append(f"Отсутствует секция {section_num} в архитектурном документе")
            else:
                matches += 1
        
        # Анализируем соответствие кода архитектурным принципам
        code_analysis = self._analyze_code_architecture(modules, blueprint)
        
        # Проверяем наличие ключевых компонентов в коде
        component_coverage = self._check_component_coverage(modules, blueprint)
        
        # Оценка архитектурного соответствия
        architecture_score = self._calculate_architecture_score(
            matches, total_sections, code_analysis, component_coverage
        )
        
        return {
            "architecture_score": architecture_score,
            "sections_found": matches,
            "sections_expected": len(expected_sections),
            "total_modules": len(modules),
            "code_analysis": code_analysis,
            "component_coverage": component_coverage,
            "issues": issues,
            "recommendations": self._generate_recommendations(issues, code_analysis, component_coverage)
        }
    
    def _analyze_code_architecture(self, modules: List[CodeModule], 
                                 blueprint: Dict[str, ArchitectureSection]) -> Dict[str, Any]:
        """Анализ архитектурных паттернов в коде"""
        analysis = {
            "reasoning_patterns": 0,
            "error_handling": 0,
            "tool_integration": 0,
            "context_management": 0,
            "self_monitoring": 0,
            "total_functions": sum(len(m.functions) for m in modules),
            "total_classes": sum(len(m.classes) for m in modules)
        }
        
        # Анализируем паттерны в коде
        for module in modules:
            module_content = " ".join(module.functions + module.classes)
            module_content_lower = module_content.lower()
            
            # Проверяем reasoning patterns
            if any(keyword in module_content_lower for keyword in 
                   ["reasoning", "planning", "decomposition", "execution"]):
                analysis["reasoning_patterns"] += 1
            
            # Проверяем error handling
            if any(keyword in module_content_lower for keyword in 
                   ["error", "exception", "try", "catch", "recovery"]):
                analysis["error_handling"] += 1
            
            # Проверяем tool integration
            if any(keyword in module_content_lower for keyword in 
                   ["tool", "api", "call", "execute", "run"]):
                analysis["tool_integration"] += 1
            
            # Проверяем context management
            if any(keyword in module_content_lower for keyword in 
                   ["context", "memory", "state", "cache"]):
                analysis["context_management"] += 1
            
            # Проверяем self monitoring
            if any(keyword in module_content_lower for keyword in 
                   ["monitor", "log", "audit", "check", "validate"]):
                analysis["self_monitoring"] += 1
        
        return analysis
    
    def _check_component_coverage(self, modules: List[CodeModule], 
                                blueprint: Dict[str, ArchitectureSection]) -> Dict[str, Any]:
        """Проверка покрытия архитектурных компонентов"""
        coverage = {}
        
        for component, keywords in self.expected_components.items():
            found_in_code = False
            found_in_docs = False
            
            # Проверяем наличие в коде
            for module in modules:
                module_content = " ".join(module.functions + module.classes).lower()
                if any(keyword in module_content for keyword in keywords):
                    found_in_code = True
                    break
            
            # Проверяем наличие в документации
            for section in blueprint.values():
                if any(keyword in section.content.lower() for keyword in keywords):
                    found_in_docs = True
                    break
            
            coverage[component] = {
                "found_in_code": found_in_code,
                "found_in_docs": found_in_docs,
                "coverage_score": 1.0 if found_in_code and found_in_docs else 0.5 if found_in_code or found_in_docs else 0.0
            }
        
        return coverage
    
    def _calculate_architecture_score(self, sections_found: int, total_sections: int,
                                    code_analysis: Dict[str, Any], 
                                    component_coverage: Dict[str, Any]) -> float:
        """Расчёт общей оценки архитектурного соответствия"""
        
        # Оценка по секциям документа (40%)
        section_score = sections_found / total_sections if total_sections > 0 else 0
        
        # Оценка по архитектурным паттернам в коде (30%)
        pattern_score = 0
        pattern_weights = {
            "reasoning_patterns": 0.3,
            "error_handling": 0.25,
            "tool_integration": 0.2,
            "context_management": 0.15,
            "self_monitoring": 0.1
        }
        
        for pattern, weight in pattern_weights.items():
            if code_analysis[pattern] > 0:
                pattern_score += weight
        
        # Оценка по покрытию компонентов (30%)
        coverage_scores = [comp["coverage_score"] for comp in component_coverage.values()]
        coverage_score = sum(coverage_scores) / len(coverage_scores) if coverage_scores else 0
        
        # Итоговая оценка
        final_score = (section_score * 0.4 + pattern_score * 0.3 + coverage_score * 0.3)
        
        return round(final_score, 3)
    
    def _generate_recommendations(self, issues: List[str], code_analysis: Dict[str, Any],
                                component_coverage: Dict[str, Any]) -> List[str]:
        """Генерация рекомендаций по улучшению архитектуры"""
        recommendations = []
        
        # Рекомендации по отсутствующим секциям
        if issues:
            recommendations.append("Добавить отсутствующие секции в архитектурный документ")
        
        # Рекомендации по паттернам в коде
        if code_analysis["reasoning_patterns"] == 0:
            recommendations.append("Реализовать паттерны reasoning chain в коде")
        
        if code_analysis["error_handling"] == 0:
            recommendations.append("Добавить механизмы обработки ошибок")
        
        if code_analysis["self_monitoring"] == 0:
            recommendations.append("Реализовать системы самомониторинга")
        
        # Рекомендации по покрытию компонентов
        for component, coverage in component_coverage.items():
            if not coverage["found_in_code"] and coverage["found_in_docs"]:
                recommendations.append(f"Реализовать компонент {component} в коде")
            elif not coverage["found_in_docs"] and coverage["found_in_code"]:
                recommendations.append(f"Документировать компонент {component}")
        
        return recommendations
    
    def audit_architecture(self, blueprint_path: str) -> Dict[str, Any]:
        """Основная функция аудита архитектуры"""
        timestamp = datetime.datetime.now().isoformat()
        
        # Парсим архитектурный документ
        blueprint = self.parse_blueprint(blueprint_path)
        
        # Анализируем кодовую базу
        modules = self.analyze_codebase()
        
        # Проверяем соответствие
        compliance = self.check_architecture_compliance(blueprint, modules)
        
        # Формируем результат
        result = {
            "timestamp": timestamp,
            "audit_type": "architecture_blueprint",
            "blueprint_file": blueprint_path,
            "project_root": str(self.project_root),
            **compliance
        }
        
        return result


def verify(blueprint_path: str, output_dir: str = "audit_reports") -> Dict[str, Any]:
    """Публичная функция для запуска аудита архитектуры"""
    auditor = ArchitectureAuditor()
    result = auditor.audit_architecture(blueprint_path)
    
    # Сохраняем результат
    output_path = pathlib.Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    report_file = output_path / "architecture_audit.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"Архитектурный аудит завершён. Отчёт: {report_file}")
    print(f"Architecture Score: {result['architecture_score']:.3f}")
    print(f"Секций найдено: {result['sections_found']}/{result['sections_expected']}")
    print(f"Модулей проанализировано: {result['total_modules']}")
    
    return result


if __name__ == "__main__":
    import sys
    
    blueprint_path = sys.argv[1] if len(sys.argv) > 1 else "docs/audit/AUDIT_ARCHITECTURE.md"
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "audit_reports"
    
    result = verify(blueprint_path, output_dir)
    
    # Выводим JSON для интеграции с audit_runner.sh
    print("\n" + "="*50)
    print("JSON RESULT:")
    print(json.dumps(result, indent=2, ensure_ascii=False))


































