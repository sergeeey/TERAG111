#!/usr/bin/env python3
"""
TERAG Full Stack Health Check
Комплексная проверка всех компонентов системы TERAG:
- LM Studio (reasoning backend)
- OSINT pipeline (Brave Search, Bright Data)
- Graph Updater (Neo4j)
- Совместная работа компонентов
"""
import asyncio
import sys
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Загружаем переменные окружения из .env
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ Загружен .env файл: {env_path}")
except ImportError:
    pass  # python-dotenv не обязателен

# Добавляем пути для импорта модулей (от корня проекта)
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root / "installer" / "app" / "modules"))

# Импорты компонентов
try:
    from src.integration.lmstudio_client import LMStudioClient, ConnectionError as LMStudioConnectionError
    LM_STUDIO_AVAILABLE = True
except ImportError as e:
    LM_STUDIO_AVAILABLE = False
    print(f"⚠️  LM Studio client not available: {e}")

try:
    from installer.app.modules.brave_search import BraveSearchClient
    BRAVE_AVAILABLE = True
except ImportError as e:
    BRAVE_AVAILABLE = False
    print(f"⚠️  Brave Search client not available: {e}")

try:
    from installer.app.modules.bright_extractor import BrightDataExtractor
    BRIGHT_DATA_AVAILABLE = True
except ImportError as e:
    BRIGHT_DATA_AVAILABLE = False
    print(f"⚠️  Bright Data extractor not available: {e}")

try:
    from installer.app.modules.graph_updater import GraphUpdater
    GRAPH_UPDATER_AVAILABLE = True
except ImportError as e:
    GRAPH_UPDATER_AVAILABLE = False
    print(f"⚠️  Graph Updater not available: {e}")

try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False


class Colors:
    """ANSI цвета для терминала"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    """Печать заголовка"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}\n")


def print_success(text: str):
    """Печать успешного результата"""
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")


def print_error(text: str):
    """Печать ошибки"""
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")


def print_warning(text: str):
    """Печать предупреждения"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")


def print_info(text: str):
    """Печать информации"""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.RESET}")


class TERAGHealthCheck:
    """Класс для проверки здоровья TERAG системы"""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "lm_studio": {},
            "brave_search": {},
            "bright_data": {},
            "neo4j": {},
            "integration": {},
            "overall_status": "unknown"
        }
    
    async def check_lm_studio(self) -> Dict[str, Any]:
        """Проверка LM Studio reasoning backend"""
        print_header("🧠 Проверка LM Studio (Reasoning Backend)")
        
        result = {
            "status": "unknown",
            "available": False,
            "models": [],
            "generation_works": False,
            "latency": None,
            "error": None
        }
        
        if not LM_STUDIO_AVAILABLE:
            print_error("LM Studio client не доступен (модуль не найден)")
            result["error"] = "Module not available"
            result["status"] = "failed"
            self.results["lm_studio"] = result
            return result
        
        try:
            base_url = os.getenv("LM_STUDIO_URL", "http://localhost:1234/v1")
            print_info(f"Подключение к LM Studio: {base_url}")
            
            async with LMStudioClient(base_url=base_url) as client:
                # Health check
                health = await client.health_check()
                if not health:
                    print_error("LM Studio API недоступен (сервер не отвечает)")
                    print_warning("💡 Убедитесь, что LM Studio запущен и сервер активен")
                    result["error"] = "API not responding"
                    result["status"] = "failed"
                    self.results["lm_studio"] = result
                    return result
                
                print_success("LM Studio API доступен")
                result["available"] = True
                
                # Получение списка моделей
                try:
                    models = await client.list_models()
                    if models:
                        print_success(f"Найдено моделей: {len(models)}")
                        for model in models[:5]:  # Показываем первые 5
                            print_info(f"  - {model}")
                        if len(models) > 5:
                            print_info(f"  ... и ещё {len(models) - 5} моделей")
                        result["models"] = models
                    else:
                        print_warning("Модели не найдены")
                except Exception as e:
                    print_error(f"Ошибка при получении списка моделей: {e}")
                    result["error"] = str(e)
                
                # Тест генерации
                try:
                    import time
                    start_time = time.time()
                    test_prompt = "Объясни в одном предложении, что такое когнитивная архитектура."
                    generation_result = await client.generate(
                        prompt=test_prompt,
                        temperature=0.7,
                        max_tokens=100
                    )
                    latency = time.time() - start_time
                    
                    if generation_result.get("text"):
                        print_success(f"Генерация работает (latency: {latency:.2f}s)")
                        print_info(f"Ответ модели: {generation_result['text'][:100]}...")
                        result["generation_works"] = True
                        result["latency"] = latency
                        result["status"] = "success"
                    else:
                        print_error("Генерация не вернула текст")
                        result["status"] = "partial"
                except LMStudioConnectionError as e:
                    print_error(f"Ошибка подключения: {e}")
                    result["error"] = str(e)
                    result["status"] = "failed"
                except Exception as e:
                    print_error(f"Ошибка генерации: {e}")
                    result["error"] = str(e)
                    result["status"] = "partial"
        
        except Exception as e:
            print_error(f"Критическая ошибка: {e}")
            result["error"] = str(e)
            result["status"] = "failed"
        
        self.results["lm_studio"] = result
        return result
    
    def check_brave_search(self) -> Dict[str, Any]:
        """Проверка Brave Search API"""
        print_header("🌐 Проверка Brave Search (OSINT Pipeline)")
        
        result = {
            "status": "unknown",
            "available": False,
            "api_key_set": False,
            "search_works": False,
            "error": None
        }
        
        if not BRAVE_AVAILABLE:
            print_warning("Brave Search client не доступен (модуль не найден)")
            result["status"] = "skipped"
            result["error"] = "Module not available"
            self.results["brave_search"] = result
            return result
        
        api_key = os.getenv("BRAVE_API_KEY")
        if not api_key:
            print_warning("BRAVE_API_KEY не установлен (проверка пропущена)")
            print_info("💡 Установите переменную окружения BRAVE_API_KEY для использования Brave Search")
            result["status"] = "skipped"
            result["error"] = "API key not set"
            self.results["brave_search"] = result
            return result
        
        result["api_key_set"] = True
        print_success("BRAVE_API_KEY установлен")
        
        try:
            client = BraveSearchClient(api_key=api_key)
            print_info("Выполнение тестового поискового запроса...")
            
            test_query = "AI governance trends 2025"
            search_result = client.search(query=test_query, count=3)
            
            # Проверяем разные форматы ответа
            results = None
            if isinstance(search_result, dict):
                if "web" in search_result and "results" in search_result["web"]:
                    results = search_result["web"]["results"]
                elif "results" in search_result:
                    results = search_result["results"]
                elif "data" in search_result:
                    results = search_result["data"]
            
            if results and len(results) > 0:
                results_count = len(results)
                print_success(f"Поиск работает (найдено результатов: {results_count})")
                # Показываем первый результат
                if results_count > 0:
                    first_result = results[0]
                    title = first_result.get("title", first_result.get("name", "N/A"))
                    print_info(f"  Пример: {title[:60]}...")
                result["available"] = True
                result["search_works"] = True
                result["status"] = "success"
            else:
                # Если нет результатов, но нет ошибки - API работает
                print_warning("Поиск выполнен, но результатов не найдено (возможно, проблема с запросом)")
                print_info(f"Ответ API: {str(search_result)[:100]}...")
                result["status"] = "partial"
                result["available"] = True  # API доступен, просто нет результатов
        
        except Exception as e:
            print_error(f"Ошибка Brave Search: {e}")
            result["error"] = str(e)
            result["status"] = "failed"
        
        self.results["brave_search"] = result
        return result
    
    def check_bright_data(self) -> Dict[str, Any]:
        """Проверка Bright Data extractor"""
        print_header("🔍 Проверка Bright Data (Content Extraction)")
        
        result = {
            "status": "unknown",
            "available": False,
            "proxy_http_set": False,
            "proxy_ws_set": False,
            "api_key_set": False,
            "mcp_server_set": False,
            "error": None
        }
        
        if not BRIGHT_DATA_AVAILABLE:
            print_warning("Bright Data extractor не доступен (модуль не найден)")
            result["status"] = "skipped"
            result["error"] = "Module not available"
            self.results["bright_data"] = result
            return result
        
        # Проверяем proxy настройки (приоритет)
        proxy_http = os.getenv("BRIGHTDATA_PROXY_HTTP")
        proxy_ws = os.getenv("BRIGHTDATA_PROXY_WS")
        api_key = os.getenv("BRIGHT_DATA_API_KEY")
        mcp_server = os.getenv("BRIGHT_DATA_MCP_SERVER", "bright_data")
        
        if proxy_http:
            result["proxy_http_set"] = True
            print_success("BRIGHTDATA_PROXY_HTTP установлен")
            result["available"] = True
        else:
            print_warning("BRIGHTDATA_PROXY_HTTP не установлен")
        
        if proxy_ws:
            result["proxy_ws_set"] = True
            print_success("BRIGHTDATA_PROXY_WS установлен")
            result["available"] = True
        else:
            print_info("BRIGHTDATA_PROXY_WS не установлен (опционально)")
        
        if api_key:
            result["api_key_set"] = True
            print_success("BRIGHT_DATA_API_KEY установлен")
            result["available"] = True
        
        if not proxy_http and not api_key:
            print_warning("Bright Data не настроен (проверка пропущена)")
            print_info("💡 Bright Data опционален, используется для извлечения контента с веб-страниц")
            print_info("💡 Установите BRIGHTDATA_PROXY_HTTP или BRIGHT_DATA_API_KEY")
            result["status"] = "skipped"
            result["error"] = "Not configured"
            self.results["bright_data"] = result
            return result
        
        result["mcp_server_set"] = bool(mcp_server)
        if mcp_server:
            print_info(f"MCP Server: {mcp_server}")
        
        print_info("💡 Полная проверка Bright Data требует настройки MCP сервера")
        result["status"] = "partial" if result["available"] else "skipped"
        
        self.results["bright_data"] = result
        return result
    
    def check_neo4j(self) -> Dict[str, Any]:
        """Проверка Neo4j графа знаний"""
        print_header("📊 Проверка Neo4j (Knowledge Graph)")
        
        result = {
            "status": "unknown",
            "available": False,
            "connected": False,
            "nodes_count": None,
            "relationships_count": None,
            "error": None
        }
        
        if not NEO4J_AVAILABLE:
            print_warning("Neo4j driver не установлен")
            print_info("💡 Установите: pip install neo4j")
            result["status"] = "skipped"
            result["error"] = "Driver not installed"
            self.results["neo4j"] = result
            return result
        
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "neo4j")
        
        print_info(f"Подключение к Neo4j: {uri}")
        
        try:
            driver = GraphDatabase.driver(uri, auth=(user, password))
            driver.verify_connectivity()
            print_success("Neo4j подключение установлено")
            result["connected"] = True
            result["available"] = True
            
            # Получение статистики графа через GraphUpdater
            try:
                from installer.app.modules.graph_updater import GraphUpdater
                updater = GraphUpdater(uri=uri, user=user, password=password)
                graph_stats = updater.get_graph_stats()
                updater.close()
                
                nodes_count = graph_stats.get("nodes", 0)
                rels_count = graph_stats.get("relations", 0)
                entities_count = graph_stats.get("entities", 0)
                signals_count = graph_stats.get("signals", 0)
                domains_count = graph_stats.get("domains", 0)
                
                print_success(f"Граф содержит: {nodes_count} узлов, {rels_count} связей")
                if entities_count > 0:
                    print_info(f"  • Entities: {entities_count}")
                if signals_count > 0:
                    print_info(f"  • Signals: {signals_count}")
                if domains_count > 0:
                    print_info(f"  • Domains: {domains_count}")
                
                result["nodes_count"] = nodes_count
                result["relationships_count"] = rels_count
                result["entities_count"] = entities_count
                result["signals_count"] = signals_count
                result["domains_count"] = domains_count
                result["status"] = "success"
            
            except Exception as e:
                print_warning(f"Не удалось получить статистику графа: {e}")
                # Fallback на прямой запрос
                try:
                    with driver.session() as session:
                        nodes_result = session.run("MATCH (n) RETURN count(n) as count")
                        nodes_count = nodes_result.single()["count"]
                        
                        rels_result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
                        rels_count = rels_result.single()["count"]
                        
                        print_success(f"Граф содержит: {nodes_count} узлов, {rels_count} связей")
                        result["nodes_count"] = nodes_count
                        result["relationships_count"] = rels_count
                except Exception as e2:
                    print_warning(f"Fallback запрос также не удался: {e2}")
                result["status"] = "partial"
            
            driver.close()
        
        except Exception as e:
            print_error(f"Ошибка подключения к Neo4j: {e}")
            print_warning("💡 Убедитесь, что Neo4j запущен и доступен")
            result["error"] = str(e)
            result["status"] = "failed"
        
        self.results["neo4j"] = result
        return result
    
    async def check_integration(self) -> Dict[str, Any]:
        """Проверка совместной работы компонентов"""
        print_header("🔗 Проверка интеграции компонентов")
        
        result = {
            "status": "unknown",
            "lm_studio_ready": False,
            "osint_ready": False,
            "graph_ready": False,
            "full_pipeline_ready": False,
            "error": None
        }
        
        # Проверяем готовность каждого компонента
        lm_studio_status = self.results.get("lm_studio", {}).get("status")
        brave_status = self.results.get("brave_search", {}).get("status")
        neo4j_status = self.results.get("neo4j", {}).get("status")
        
        if lm_studio_status == "success":
            print_success("LM Studio готов к reasoning")
            result["lm_studio_ready"] = True
        else:
            print_warning("LM Studio не готов (reasoning будет недоступен)")
        
        if brave_status in ["success", "partial"]:
            print_success("OSINT pipeline готов (Brave Search)")
            result["osint_ready"] = True
        else:
            print_warning("OSINT pipeline не готов (сбор данных будет ограничен)")
        
        if neo4j_status in ["success", "partial"]:
            print_success("Graph Updater готов (Neo4j)")
            result["graph_ready"] = True
            
            # Проверяем Pattern Memory
            try:
                from src.core.pattern_memory import PatternMemory
                pattern_mem = PatternMemory()
                pattern_stats = pattern_mem.get_pattern_stats()
                if pattern_stats["total"] > 0:
                    print_info(f"  🧠 Patterns: {pattern_stats['total']} ({pattern_stats['success']} успешных, {pattern_stats['failure']} ошибочных)")
                    if pattern_stats["avg_strength"] > 0:
                        print_info(f"  🔗 Средняя сила связей: {pattern_stats['avg_strength']:.2f}")
            except Exception:
                pass  # Pattern Memory опционален
        else:
            print_warning("Graph Updater не готов (граф не будет обновляться)")
        
        # Полный pipeline готов, если хотя бы reasoning работает
        if result["lm_studio_ready"]:
            result["full_pipeline_ready"] = True
            result["status"] = "success"
            print_success("🎉 TERAG готов к reasoning (основной функционал работает)")
        else:
            result["status"] = "partial"
            print_warning("⚠️  TERAG частично готов (reasoning недоступен)")
        
        self.results["integration"] = result
        return result
    
    def generate_report(self) -> str:
        """Генерация итогового отчёта"""
        print_header("📋 Итоговый отчёт")
        
        # Определяем общий статус
        lm_studio_ok = self.results["lm_studio"].get("status") == "success"
        integration_ok = self.results["integration"].get("status") == "success"
        
        if lm_studio_ok and integration_ok:
            overall = "success"
            status_icon = "✅"
            status_text = "TERAG готов к работе"
        elif lm_studio_ok:
            overall = "partial"
            status_icon = "⚠️"
            status_text = "TERAG частично готов (reasoning работает)"
        else:
            overall = "failed"
            status_icon = "❌"
            status_text = "TERAG не готов (reasoning недоступен)"
        
        self.results["overall_status"] = overall
        
        # Печать статуса
        print(f"\n{status_icon} {Colors.BOLD}{status_text}{Colors.RESET}\n")
        
        # Детальная таблица
        print(f"{Colors.BOLD}Компонент{' ' * 20}Статус{' ' * 15}Детали{Colors.RESET}")
        print("-" * 70)
        
        # LM Studio
        lm = self.results["lm_studio"]
        lm_status = lm.get("status", "unknown")
        lm_icon = "✅" if lm_status == "success" else "❌" if lm_status == "failed" else "⚠️"
        lm_details = f"{len(lm.get('models', []))} моделей" if lm.get("models") else "недоступен"
        if lm.get("latency"):
            lm_details += f", latency: {lm['latency']:.2f}s"
        print(f"{lm_icon} LM Studio{' ' * 20}{lm_status:15} {lm_details}")
        
        # Brave Search
        brave = self.results["brave_search"]
        brave_status = brave.get("status", "unknown")
        brave_icon = "✅" if brave_status == "success" else "⚠️" if brave_status == "skipped" else "❌"
        brave_details = "работает" if brave.get("search_works") else "не настроен"
        print(f"{brave_icon} Brave Search{' ' * 18}{brave_status:15} {brave_details}")
        
        # Bright Data
        bright = self.results["bright_data"]
        bright_status = bright.get("status", "unknown")
        bright_icon = "⚠️" if bright_status == "skipped" else "✅" if bright_status == "partial" else "❌"
        bright_details = "настроен" if bright.get("api_key_set") else "не настроен"
        print(f"{bright_icon} Bright Data{' ' * 19}{bright_status:15} {bright_details}")
        
        # Neo4j
        neo4j = self.results["neo4j"]
        neo4j_status = neo4j.get("status", "unknown")
        neo4j_icon = "✅" if neo4j_status == "success" else "⚠️" if neo4j_status == "skipped" else "❌"
        if neo4j.get("nodes_count") is not None:
            neo4j_details = f"{neo4j['nodes_count']} узлов, {neo4j['relationships_count']} связей"
        else:
            neo4j_details = "недоступен"
        print(f"{neo4j_icon} Neo4j{' ' * 25}{neo4j_status:15} {neo4j_details}")
        
        print("-" * 70)
        
        return overall
    
    def save_report(self, filename: str = "terag_health_check.json"):
        """Сохранение отчёта в JSON"""
        report_path = Path(__file__).parent / filename
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        print_info(f"Отчёт сохранён: {report_path}")


async def main():
    """Главная функция"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║     TERAG Full Stack Health Check                          ║")
    print("║     Комплексная проверка всех компонентов системы          ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}")
    
    checker = TERAGHealthCheck()
    
    # Проверка компонентов
    await checker.check_lm_studio()
    checker.check_brave_search()
    checker.check_bright_data()
    checker.check_neo4j()
    await checker.check_integration()
    
    # Генерация отчёта
    overall_status = checker.generate_report()
    
    # Сохранение отчёта
    checker.save_report()
    
    # Возвращаем код выхода
    if overall_status == "success":
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 Все критичные компоненты работают!{Colors.RESET}\n")
        return 0
    elif overall_status == "partial":
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  Система частично готова{Colors.RESET}\n")
        return 1
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ Критичные компоненты не работают{Colors.RESET}\n")
        return 2


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

