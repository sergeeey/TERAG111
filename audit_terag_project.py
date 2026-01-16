#!/usr/bin/env python3
"""
TERAG Project Audit — комплексный аудит всех компонентов системы
Проверяет: модули, интеграции, конфигурацию, зависимости, граф знаний
"""
import sys
import os
import json
import importlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

# Загружаем .env
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass

# Добавляем пути
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent / "installer" / "app" / "modules"))

class TERAGAudit:
    """Комплексный аудит проекта TERAG"""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "modules": {},
            "integrations": {},
            "config": {},
            "dependencies": {},
            "graph": {},
            "tasks": {},
            "overall_score": 0.0,
            "issues": [],
            "recommendations": []
        }
    
    def print_header(self, text: str):
        """Печать заголовка"""
        print(f"\n{'='*60}")
        print(f"{text}")
        print(f"{'='*60}\n")
    
    def print_success(self, text: str):
        """Печать успеха"""
        print(f"✅ {text}")
    
    def print_warning(self, text: str):
        """Печать предупреждения"""
        print(f"⚠️  {text}")
    
    def print_error(self, text: str):
        """Печать ошибки"""
        print(f"❌ {text}")
    
    def print_info(self, text: str):
        """Печать информации"""
        print(f"ℹ️  {text}")
    
    def check_module(self, module_path: str, module_name: str) -> Dict[str, Any]:
        """Проверить модуль"""
        result = {
            "available": False,
            "importable": False,
            "error": None
        }
        
        try:
            # Проверяем существование файла
            file_path = Path(module_path)
            if file_path.exists():
                result["available"] = True
            else:
                result["error"] = f"File not found: {module_path}"
                return result
            
            # Пытаемся импортировать
            try:
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    result["importable"] = True
            except Exception as e:
                result["error"] = str(e)
        
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def check_dependencies(self) -> Dict[str, Any]:
        """Проверить зависимости"""
        self.print_header("📦 Проверка зависимостей")
        
        dependencies = {
            "httpx": False,
            "aiogram": False,
            "neo4j": False,
            "sentence_transformers": False,
            "prometheus_client": False,
            "psutil": False,
            "docker": False,
            "dotenv": False
        }
        
        missing = []
        
        for dep in dependencies:
            try:
                __import__(dep.replace("-", "_"))
                dependencies[dep] = True
                self.print_success(f"{dep} установлен")
            except ImportError:
                dependencies[dep] = False
                missing.append(dep)
                self.print_warning(f"{dep} не установлен")
        
        if missing:
            self.print_info(f"Установите: pip install {' '.join(missing)}")
        
        self.results["dependencies"] = dependencies
        return dependencies
    
    def check_modules(self) -> Dict[str, Any]:
        """Проверить модули проекта"""
        self.print_header("🔧 Проверка модулей проекта")
        
        modules = {
            "LM Studio Client": "src/integration/lmstudio_client.py",
            "Graph Updater": "installer/app/modules/graph_updater.py",
            "Learning Bridge": "src/integration/learning_bridge.py",
            "Self-Organizing Graph": "src/core/self_organizing_graph.py",
            "Telegram Service": "src/integration/telegram_service.py",
            "OSINT Digest": "src/integration/osint_digest.py",
            "System Context": "src/core/system_context.py",
            "Graph Metrics": "src/core/graph_metrics.py"
        }
        
        module_results = {}
        
        for name, path in modules.items():
            result = self.check_module(path, name.lower().replace(" ", "_"))
            module_results[name] = result
            
            if result["available"] and result["importable"]:
                self.print_success(f"{name}: доступен и импортируется")
            elif result["available"]:
                self.print_warning(f"{name}: файл существует, но не импортируется ({result.get('error', 'unknown')})")
            else:
                self.print_error(f"{name}: файл не найден ({result.get('error', 'unknown')})")
        
        self.results["modules"] = module_results
        return module_results
    
    def check_integrations(self) -> Dict[str, Any]:
        """Проверить интеграции"""
        self.print_header("🔗 Проверка интеграций")
        
        integrations = {}
        
        # LM Studio
        try:
            from src.integration.lmstudio_client import LMStudioClient
            client = LMStudioClient()
            # Проверяем доступность (не блокируем)
            integrations["LM Studio"] = {"available": True, "status": "client_ready"}
            self.print_success("LM Studio: клиент доступен")
        except Exception as e:
            integrations["LM Studio"] = {"available": False, "error": str(e)}
            self.print_warning(f"LM Studio: {e}")
        
        # Neo4j
        try:
            from installer.app.modules.graph_updater import GraphUpdater
            updater = GraphUpdater()
            if updater.driver:
                stats = updater.get_graph_stats()
                integrations["Neo4j"] = {
                    "available": True,
                    "nodes": stats.get("nodes", 0),
                    "relations": stats.get("relations", 0)
                }
                self.print_success(f"Neo4j: подключен ({stats.get('nodes', 0)} узлов, {stats.get('relations', 0)} связей)")
            else:
                integrations["Neo4j"] = {"available": False, "error": "Driver not initialized"}
                self.print_warning("Neo4j: драйвер не инициализирован")
        except Exception as e:
            integrations["Neo4j"] = {"available": False, "error": str(e)}
            self.print_warning(f"Neo4j: {e}")
        
        # Telegram
        telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        telegram_chat = os.getenv("TELEGRAM_CHAT_ID")
        if telegram_token and telegram_chat:
            integrations["Telegram"] = {"available": True, "token_set": True, "chat_set": True}
            self.print_success("Telegram: токен и chat ID установлены")
        else:
            integrations["Telegram"] = {
                "available": False,
                "token_set": bool(telegram_token),
                "chat_set": bool(telegram_chat)
            }
            self.print_warning("Telegram: токен или chat ID не установлены")
        
        # Brave Search
        brave_key = os.getenv("BRAVE_API_KEY")
        if brave_key:
            integrations["Brave Search"] = {"available": True, "api_key_set": True}
            self.print_success("Brave Search: API ключ установлен")
        else:
            integrations["Brave Search"] = {"available": False, "api_key_set": False}
            self.print_warning("Brave Search: API ключ не установлен")
        
        # Bright Data
        bright_http = os.getenv("BRIGHTDATA_PROXY_HTTP")
        bright_ws = os.getenv("BRIGHTDATA_PROXY_WS")
        if bright_http or bright_ws:
            integrations["Bright Data"] = {
                "available": True,
                "proxy_http_set": bool(bright_http),
                "proxy_ws_set": bool(bright_ws)
            }
            self.print_success("Bright Data: proxy credentials установлены")
        else:
            integrations["Bright Data"] = {"available": False}
            self.print_warning("Bright Data: proxy credentials не установлены")
        
        self.results["integrations"] = integrations
        return integrations
    
    def check_config(self) -> Dict[str, Any]:
        """Проверить конфигурацию"""
        self.print_header("⚙️  Проверка конфигурации")
        
        config = {
            "env_file_exists": False,
            "required_vars": {},
            "optional_vars": {}
        }
        
        env_path = Path(".env")
        if env_path.exists():
            config["env_file_exists"] = True
            self.print_success(".env файл существует")
        else:
            self.print_error(".env файл не найден")
            self.results["issues"].append("Отсутствует .env файл")
        
        # Проверяем обязательные переменные
        required_vars = {
            "NEO4J_URI": os.getenv("NEO4J_URI"),
            "NEO4J_USER": os.getenv("NEO4J_USER"),
            "NEO4J_PASSWORD": os.getenv("NEO4J_PASSWORD")
        }
        
        for var, value in required_vars.items():
            if value:
                config["required_vars"][var] = True
                self.print_success(f"{var}: установлен")
            else:
                config["required_vars"][var] = False
                self.print_warning(f"{var}: не установлен")
                self.results["issues"].append(f"Отсутствует обязательная переменная: {var}")
        
        # Проверяем опциональные переменные
        optional_vars = {
            "TELEGRAM_BOT_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN"),
            "TELEGRAM_CHAT_ID": os.getenv("TELEGRAM_CHAT_ID"),
            "BRAVE_API_KEY": os.getenv("BRAVE_API_KEY"),
            "BRIGHTDATA_PROXY_HTTP": os.getenv("BRIGHTDATA_PROXY_HTTP")
        }
        
        for var, value in optional_vars.items():
            config["optional_vars"][var] = bool(value)
            if value:
                self.print_success(f"{var}: установлен")
            else:
                self.print_info(f"{var}: не установлен (опционально)")
        
        self.results["config"] = config
        return config
    
    def check_graph(self) -> Dict[str, Any]:
        """Проверить состояние графа знаний"""
        self.print_header("📊 Проверка графа знаний")
        
        graph_info = {
            "available": False,
            "nodes": 0,
            "relations": 0,
            "entities": 0,
            "signals": 0,
            "domains": 0,
            "error": None
        }
        
        try:
            from installer.app.modules.graph_updater import GraphUpdater
            updater = GraphUpdater()
            
            if updater.driver:
                stats = updater.get_graph_stats()
                graph_info.update(stats)
                graph_info["available"] = True
                
                self.print_success(f"Граф доступен: {stats.get('nodes', 0)} узлов, {stats.get('relations', 0)} связей")
                self.print_info(f"  • Entities: {stats.get('entities', 0)}")
                self.print_info(f"  • Signals: {stats.get('signals', 0)}")
                self.print_info(f"  • Domains: {stats.get('domains', 0)}")
            else:
                graph_info["error"] = "Driver not initialized"
                self.print_warning("Граф: драйвер не инициализирован")
        
        except Exception as e:
            graph_info["error"] = str(e)
            self.print_error(f"Граф: {e}")
        
        self.results["graph"] = graph_info
        return graph_info
    
    def check_tasks(self) -> Dict[str, Any]:
        """Проверить статус задач"""
        self.print_header("📋 Проверка статуса задач")
        
        tasks_dir = Path(".cursor/tasks")
        tasks = {}
        
        if not tasks_dir.exists():
            self.print_warning("Директория .cursor/tasks не найдена")
            return tasks
        
        task_files = [
            "08-graph-updater-integration.md",
            "09-telegram-integration.md",
            "10-learning-bridge-integration.md",
            "10a-signal-discovery-enhancement.md",
            "10b-self-organizing-knowledge-graph.md",
            "11-auto-eval-monitoring.md",
            "12-kag-solver-phase2.md",
            "13-system-context-memory.md"
        ]
        
        for task_file in task_files:
            task_path = tasks_dir / task_file
            if task_path.exists():
                # Читаем статус из файла (ищем ✅ или ⬜)
                content = task_path.read_text(encoding="utf-8")
                if "✅" in content or "Завершено" in content:
                    status = "completed"
                    self.print_success(f"{task_file}: завершена")
                else:
                    status = "pending"
                    self.print_info(f"{task_file}: ожидает выполнения")
                
                tasks[task_file] = {"exists": True, "status": status}
            else:
                tasks[task_file] = {"exists": False, "status": "missing"}
                self.print_warning(f"{task_file}: не найдена")
        
        self.results["tasks"] = tasks
        return tasks
    
    def calculate_score(self) -> float:
        """Вычислить общий score"""
        score = 0.0
        max_score = 0.0
        
        # Модули (30%)
        max_score += 30
        available_modules = sum(1 for m in self.results["modules"].values() if m.get("importable", False))
        total_modules = len(self.results["modules"])
        if total_modules > 0:
            score += 30 * (available_modules / total_modules)
        
        # Интеграции (25%)
        max_score += 25
        available_integrations = sum(1 for i in self.results["integrations"].values() if i.get("available", False))
        total_integrations = len(self.results["integrations"])
        if total_integrations > 0:
            score += 25 * (available_integrations / total_integrations)
        
        # Конфигурация (20%)
        max_score += 20
        if self.results["config"].get("env_file_exists", False):
            score += 10
        required_vars_set = sum(1 for v in self.results["config"].get("required_vars", {}).values() if v)
        total_required = len(self.results["config"].get("required_vars", {}))
        if total_required > 0:
            score += 10 * (required_vars_set / total_required)
        
        # Граф (15%)
        max_score += 15
        if self.results["graph"].get("available", False):
            score += 15
        
        # Зависимости (10%)
        max_score += 10
        installed_deps = sum(1 for d in self.results["dependencies"].values() if d)
        total_deps = len(self.results["dependencies"])
        if total_deps > 0:
            score += 10 * (installed_deps / total_deps)
        
        if max_score > 0:
            final_score = score / max_score
        else:
            final_score = 0.0
        
        self.results["overall_score"] = final_score
        return final_score
    
    def generate_recommendations(self):
        """Сгенерировать рекомендации"""
        recommendations = []
        
        # Проверяем зависимости
        missing_deps = [d for d, v in self.results["dependencies"].items() if not v]
        if missing_deps:
            recommendations.append(f"Установите недостающие зависимости: pip install {' '.join(missing_deps)}")
        
        # Проверяем модули
        missing_modules = [m for m, v in self.results["modules"].items() if not v.get("importable", False)]
        if missing_modules:
            recommendations.append(f"Проверьте модули: {', '.join(missing_modules)}")
        
        # Проверяем конфигурацию
        missing_vars = [v for v, s in self.results["config"].get("required_vars", {}).items() if not s]
        if missing_vars:
            recommendations.append(f"Установите обязательные переменные: {', '.join(missing_vars)}")
        
        # Проверяем граф
        if not self.results["graph"].get("available", False):
            recommendations.append("Проверьте подключение к Neo4j и убедитесь, что контейнер запущен")
        
        self.results["recommendations"] = recommendations
    
    def print_summary(self):
        """Печать итогового отчёта"""
        self.print_header("📋 Итоговый отчёт аудита")
        
        score = self.results["overall_score"]
        score_percent = score * 100
        
        if score >= 0.8:
            status = "🟢 Отлично"
            status_color = "Green"
        elif score >= 0.6:
            status = "🟡 Хорошо"
            status_color = "Yellow"
        elif score >= 0.4:
            status = "🟠 Удовлетворительно"
            status_color = "DarkYellow"
        else:
            status = "🔴 Требует внимания"
            status_color = "Red"
        
        print(f"\nОбщий score: {score_percent:.1f}% ({status})")
        print(f"\nМодули: {sum(1 for m in self.results['modules'].values() if m.get('importable', False))}/{len(self.results['modules'])} доступны")
        print(f"Интеграции: {sum(1 for i in self.results['integrations'].values() if i.get('available', False))}/{len(self.results['integrations'])} работают")
        print(f"Граф: {self.results['graph'].get('nodes', 0)} узлов, {self.results['graph'].get('relations', 0)} связей")
        
        if self.results["issues"]:
            print(f"\n⚠️  Проблемы ({len(self.results['issues'])}):")
            for issue in self.results["issues"]:
                print(f"   • {issue}")
        
        if self.results["recommendations"]:
            print(f"\n💡 Рекомендации ({len(self.results['recommendations'])}):")
            for rec in self.results["recommendations"]:
                print(f"   • {rec}")
    
    def save_report(self, path: str = "terag_audit_report.json"):
        """Сохранить отчёт"""
        report_path = Path(path)
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        self.print_info(f"Отчёт сохранён: {report_path}")
    
    def run_full_audit(self):
        """Запустить полный аудит"""
        print("\n" + "="*60)
        print("🔍 TERAG Project Audit")
        print("="*60 + "\n")
        
        # Проверяем компоненты
        self.check_dependencies()
        self.check_modules()
        self.check_integrations()
        self.check_config()
        self.check_graph()
        self.check_tasks()
        
        # Вычисляем score
        self.calculate_score()
        
        # Генерируем рекомендации
        self.generate_recommendations()
        
        # Печатаем итоги
        self.print_summary()
        
        # Сохраняем отчёт
        self.save_report()
        
        return self.results


def main():
    """Главная функция"""
    import importlib.util
    
    audit = TERAGAudit()
    results = audit.run_full_audit()
    
    # Возвращаем код выхода
    if results["overall_score"] >= 0.6:
        return 0
    elif results["overall_score"] >= 0.4:
        return 1
    else:
        return 2


if __name__ == "__main__":
    sys.exit(main())

