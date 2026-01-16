"""
TERAG System Context Memory
Модуль для сбора и сохранения информации о системной инфраструктуре
"""
import platform
import shutil
import json
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)

# Опциональные зависимости
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.warning("psutil not available, memory/CPU info will be limited")

try:
    import docker
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False
    logger.warning("docker not available, Docker info will be limited")


class SystemContext:
    """Класс для сбора системной информации"""
    
    def __init__(self):
        self.context_cache = None
        self.cache_ttl = 300  # 5 минут
    
    def get_system_context(self) -> Dict[str, Any]:
        """
        Собрать полную информацию о системе
        
        Returns:
            Словарь с информацией о системе
        """
        ctx = {
            "timestamp": datetime.utcnow().isoformat(),
            "host": {
                "os": platform.system(),
                "os_version": platform.version(),
                "platform": platform.platform(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "hostname": platform.node(),
            },
            "python": {
                "version": platform.python_version(),
                "implementation": platform.python_implementation(),
            },
            "resources": self._get_resources(),
            "docker": self._get_docker_info(),
            "services": self._detect_services(),
            "ports": self._check_ports(),
        }
        
        return ctx
    
    def _get_resources(self) -> Dict[str, Any]:
        """Получить информацию о ресурсах системы"""
        resources = {}
        
        # Диск
        try:
            disk = shutil.disk_usage("/")
            if os.name == 'nt':  # Windows
                disk = shutil.disk_usage("C:\\")
            resources["disk"] = {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": (disk.used / disk.total * 100) if disk.total > 0 else 0
            }
        except Exception as e:
            logger.warning(f"Could not get disk usage: {e}")
            resources["disk"] = {"error": str(e)}
        
        # CPU и память (требует psutil)
        if PSUTIL_AVAILABLE:
            try:
                resources["cpu"] = {
                    "count": psutil.cpu_count(),
                    "percent": psutil.cpu_percent(interval=1),
                    "freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
                }
                
                mem = psutil.virtual_memory()
                resources["memory"] = {
                    "total": mem.total,
                    "available": mem.available,
                    "used": mem.used,
                    "percent": mem.percent,
                    "free": mem.free
                }
            except Exception as e:
                logger.warning(f"Could not get CPU/memory info: {e}")
                resources["cpu"] = {"error": str(e)}
                resources["memory"] = {"error": str(e)}
        else:
            resources["cpu"] = {"note": "psutil not available"}
            resources["memory"] = {"note": "psutil not available"}
        
        return resources
    
    def _get_docker_info(self) -> Dict[str, Any]:
        """Получить информацию о Docker"""
        docker_info = {
            "available": False,
            "version": None,
            "containers": [],
            "images": []
        }
        
        if not DOCKER_AVAILABLE:
            docker_info["error"] = "docker library not installed"
            return docker_info
        
        try:
            client = docker.from_env()
            info = client.info()
            
            docker_info["available"] = True
            docker_info["version"] = info.get("ServerVersion")
            docker_info["containers_total"] = info.get("Containers", 0)
            docker_info["containers_running"] = info.get("ContainersRunning", 0)
            docker_info["images"] = info.get("Images", 0)
            
            # Список контейнеров
            containers = []
            for container in client.containers.list(all=True):
                containers.append({
                    "name": container.name,
                    "id": container.short_id,
                    "image": container.image.tags[0] if container.image.tags else str(container.image.id),
                    "status": container.status,
                    "created": container.attrs.get("Created", ""),
                    "ports": container.attrs.get("NetworkSettings", {}).get("Ports", {})
                })
            
            docker_info["containers"] = containers
            
            # Проверяем наличие ключевых контейнеров TERAG
            terag_containers = [c for c in containers if "terag" in c["name"].lower() or "neo4j" in c["name"].lower()]
            docker_info["terag_containers"] = [c["name"] for c in terag_containers]
            docker_info["terag_containers_running"] = [c["name"] for c in terag_containers if c["status"] == "running"]
            
        except docker.errors.DockerException as e:
            docker_info["error"] = f"Docker not running or not accessible: {str(e)}"
        except Exception as e:
            docker_info["error"] = str(e)
            logger.error(f"Error getting Docker info: {e}")
        
        return docker_info
    
    def _detect_services(self) -> Dict[str, Any]:
        """Обнаружить запущенные сервисы TERAG"""
        services = {
            "lm_studio": self._check_service("http://localhost:1234/v1/models", "LM Studio"),
            "neo4j": self._check_service("bolt://localhost:7687", "Neo4j"),
            "ollama": self._check_service("http://localhost:11434/api/tags", "Ollama"),
        }
        
        return services
    
    def _check_service(self, endpoint: str, name: str) -> Dict[str, Any]:
        """Проверить доступность сервиса"""
        import httpx
        
        service_info = {
            "name": name,
            "endpoint": endpoint,
            "available": False
        }
        
        try:
            if endpoint.startswith("http"):
                # HTTP сервис
                with httpx.Client(timeout=2.0) as client:
                    response = client.get(endpoint)
                    service_info["available"] = response.status_code == 200
                    service_info["status_code"] = response.status_code
            elif endpoint.startswith("bolt"):
                # Neo4j
                try:
                    from neo4j import GraphDatabase
                    driver = GraphDatabase.driver(endpoint, auth=("neo4j", "neo4j"))
                    driver.verify_connectivity()
                    driver.close()
                    service_info["available"] = True
                except:
                    service_info["available"] = False
        except Exception as e:
            service_info["error"] = str(e)
        
        return service_info
    
    def _check_ports(self) -> Dict[str, bool]:
        """Проверить занятые порты"""
        ports = {}
        
        if PSUTIL_AVAILABLE:
            try:
                connections = psutil.net_connections(kind='inet')
                used_ports = {conn.laddr.port for conn in connections if conn.status == 'LISTEN'}
                
                # Ключевые порты TERAG
                key_ports = {
                    1234: "LM Studio",
                    7687: "Neo4j",
                    7474: "Neo4j Browser",
                    11434: "Ollama",
                    8000: "TERAG API",
                }
                
                for port, name in key_ports.items():
                    ports[f"{port} ({name})"] = port in used_ports
            except Exception as e:
                logger.warning(f"Could not check ports: {e}")
        
        return ports
    
    def save_to_file(self, filepath: Optional[str] = None) -> str:
        """Сохранить контекст в файл"""
        if not filepath:
            filepath = "data/system_context.json"
        
        context = self.get_system_context()
        filepath_obj = Path(filepath)
        filepath_obj.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath_obj, 'w', encoding='utf-8') as f:
            json.dump(context, f, indent=2, ensure_ascii=False)
        
        logger.info(f"System context saved to {filepath}")
        return filepath
    
    def save_to_supabase(self, supabase_client=None) -> bool:
        """Сохранить контекст в Supabase"""
        if not supabase_client:
            try:
                from src.kag.storage.supabase_client import get_supabase_client
                supabase_client = get_supabase_client()
            except ImportError:
                logger.warning("Supabase client not available")
                return False
        
        context = self.get_system_context()
        
        try:
            # Подготовка данных для Supabase
            record = {
                "timestamp": context["timestamp"],
                "host": context["host"]["hostname"],
                "os": context["host"]["os"],
                "docker_version": context["docker"].get("version"),
                "containers_json": json.dumps(context["docker"].get("containers", [])),
                "cpu_count": context["resources"].get("cpu", {}).get("count"),
                "ram_total_gb": context["resources"].get("memory", {}).get("total", 0) / (1024**3) if context["resources"].get("memory", {}).get("total") else None,
                "disk_free_gb": context["resources"].get("disk", {}).get("free", 0) / (1024**3) if context["resources"].get("disk", {}).get("free") else None,
                "notes": json.dumps({
                    "services": context["services"],
                    "ports": context["ports"]
                })
            }
            
            result = supabase_client.table("system_state_log").insert(record).execute()
            logger.info("System context saved to Supabase")
            return True
        except Exception as e:
            logger.error(f"Error saving to Supabase: {e}")
            return False
    
    def format_for_telegram(self) -> str:
        """Форматировать контекст для Telegram"""
        ctx = self.get_system_context()
        
        lines = ["🧩 *System Context*", ""]
        
        # Host info
        host = ctx["host"]
        lines.append(f"*Host:* {host['hostname']}")
        lines.append(f"*OS:* {host['os']} {host['os_version'][:50]}")
        lines.append("")
        
        # Resources
        resources = ctx["resources"]
        if "cpu" in resources and "count" in resources["cpu"]:
            lines.append(f"*CPU:* {resources['cpu']['count']} cores")
        if "memory" in resources and "total" in resources["memory"]:
            ram_gb = resources["memory"]["total"] / (1024**3)
            lines.append(f"*RAM:* {ram_gb:.1f} GB")
        if "disk" in resources and "free" in resources["disk"]:
            disk_gb = resources["disk"]["free"] / (1024**3)
            lines.append(f"*Disk free:* {disk_gb:.1f} GB")
        lines.append("")
        
        # Docker
        docker_info = ctx["docker"]
        if docker_info.get("available"):
            lines.append(f"*Docker:* {docker_info.get('version', 'unknown')}")
            lines.append(f"*Containers:* {docker_info.get('containers_running', 0)}/{docker_info.get('containers_total', 0)} running")
            
            terag_containers = docker_info.get("terag_containers_running", [])
            if terag_containers:
                lines.append(f"*TERAG containers:* {', '.join(terag_containers)}")
        else:
            lines.append("*Docker:* не доступен")
        lines.append("")
        
        # Services
        services = ctx["services"]
        lines.append("*Services:*")
        for name, info in services.items():
            status = "✅" if info.get("available") else "❌"
            lines.append(f"{status} {info.get('name', name)}")
        
        return "\n".join(lines)


def get_system_context() -> Dict[str, Any]:
    """Удобная функция для получения контекста"""
    context = SystemContext()
    return context.get_system_context()


def save_system_snapshot(filepath: Optional[str] = None) -> str:
    """Удобная функция для сохранения снимка"""
    context = SystemContext()
    return context.save_to_file(filepath)













