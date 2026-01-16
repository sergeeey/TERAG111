#!/usr/bin/env python3
"""
Cursor Environment Audit — проверяет, видит ли IDE реальный проект,
активны ли MCP-интеграции и нет ли дрейфа путей.
"""

import json
import os
import pathlib
import shutil
import datetime
import subprocess
import sys
from typing import Dict, List, Any, Optional

class CursorEnvironmentAuditor:
    """Аудитор Cursor-окружения и IDE-интеграций"""
    
    def __init__(self):
        self.workspace = pathlib.Path.cwd().resolve()
        self.home = pathlib.Path.home()
        self.cursor_dir = self.home / ".cursor"
        self.projects_dir = self.cursor_dir / "projects"
        self.mcp_dir = self.cursor_dir / "mcp"
        self.cache_dir = self.cursor_dir / "cache"
        
    def load_cursor_settings(self) -> Dict[str, Any]:
        """Загрузка настроек Cursor"""
        settings_paths = [
            self.cursor_dir / "settings.json",
            self.workspace / ".cursor" / "settings.json",
            self.workspace / ".vscode" / "settings.json"
        ]
        
        for settings_path in settings_paths:
            if settings_path.exists():
                try:
                    with open(settings_path, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except Exception as e:
                    print(f"⚠️ Ошибка загрузки {settings_path}: {e}")
                    continue
        
        return {}
    
    def check_workspace_consistency(self) -> Dict[str, Any]:
        """Проверка согласованности рабочего пространства"""
        issues = []
        recommendations = []
        
        # Проверка наличия .git в корне
        git_dir = self.workspace / ".git"
        if not git_dir.exists():
            issues.append("no_git_repository")
            recommendations.append("Инициализируйте git репозиторий: git init")
        
        # Проверка наличия .cursor в проекте
        cursor_project_dir = self.workspace / ".cursor"
        if not cursor_project_dir.exists():
            issues.append("no_cursor_project_config")
            recommendations.append("Создайте .cursor директорию для конфигурации проекта")
        
        # Проверка workspace root в настройках
        settings = self.load_cursor_settings()
        workspace_root = settings.get("workspaceRoot")
        
        if workspace_root:
            if str(self.workspace) != workspace_root:
                issues.append("workspace_mismatch")
                recommendations.append(f"Обновите workspaceRoot: {workspace_root} -> {self.workspace}")
        else:
            issues.append("no_workspace_root_setting")
            recommendations.append("Установите workspaceRoot в настройках Cursor")
        
        return {
            "issues": issues,
            "recommendations": recommendations,
            "workspace_path": str(self.workspace),
            "configured_workspace_root": workspace_root,
            "git_available": git_dir.exists(),
            "cursor_project_config": cursor_project_dir.exists()
        }
    
    def check_mcp_integrations(self) -> Dict[str, Any]:
        """Проверка MCP-интеграций"""
        issues = []
        recommendations = []
        active_mcp = []
        stale_mcp = []
        
        if not self.mcp_dir.exists():
            issues.append("mcp_dir_missing")
            recommendations.append("Создайте MCP директорию: mkdir -p ~/.cursor/mcp")
        else:
            # Поиск активных MCP подключений
            for mcp_item in self.mcp_dir.iterdir():
                if mcp_item.is_dir():
                    token_file = mcp_item / "token"
                    config_file = mcp_item / "config.json"
                    
                    if token_file.exists() and config_file.exists():
                        try:
                            with open(config_file, 'r', encoding='utf-8') as f:
                                config = json.load(f)
                            
                            # Проверка актуальности токена
                            token_age = datetime.datetime.now() - datetime.datetime.fromtimestamp(token_file.stat().st_mtime)
                            if token_age.days > 30:
                                stale_mcp.append(mcp_item.name)
                                issues.append(f"stale_mcp_token_{mcp_item.name}")
                                recommendations.append(f"Обновите токен для MCP: {mcp_item.name}")
                            else:
                                active_mcp.append({
                                    "name": mcp_item.name,
                                    "config": config,
                                    "token_age_days": token_age.days
                                })
                        except Exception as e:
                            issues.append(f"corrupted_mcp_config_{mcp_item.name}")
                            recommendations.append(f"Исправьте конфигурацию MCP: {mcp_item.name}")
                    else:
                        issues.append(f"incomplete_mcp_{mcp_item.name}")
                        recommendations.append(f"Завершите настройку MCP: {mcp_item.name}")
        
        return {
            "issues": issues,
            "recommendations": recommendations,
            "active_mcp": active_mcp,
            "stale_mcp": stale_mcp,
            "mcp_dir_exists": self.mcp_dir.exists(),
            "total_mcp_dirs": len(list(self.mcp_dir.iterdir())) if self.mcp_dir.exists() else 0
        }
    
    def check_cursor_cache(self) -> Dict[str, Any]:
        """Проверка кэша Cursor"""
        issues = []
        recommendations = []
        cache_info = {}
        
        if self.cache_dir.exists():
            cache_size = sum(f.stat().st_size for f in self.cache_dir.rglob('*') if f.is_file())
            cache_files_count = len(list(self.cache_dir.rglob('*')))
            
            # Проверка размера кэша
            if cache_size > 1024 * 1024 * 1024:  # > 1GB
                issues.append("large_cache_size")
                recommendations.append("Очистите кэш Cursor: rm -rf ~/.cursor/cache")
            
            cache_info = {
                "size_bytes": cache_size,
                "size_mb": round(cache_size / (1024 * 1024), 2),
                "files_count": cache_files_count
            }
        else:
            issues.append("no_cache_dir")
            recommendations.append("Кэш Cursor не найден - это может быть нормально")
        
        return {
            "issues": issues,
            "recommendations": recommendations,
            "cache_info": cache_info,
            "cache_dir_exists": self.cache_dir.exists()
        }
    
    def check_project_structure(self) -> Dict[str, Any]:
        """Проверка структуры проекта"""
        issues = []
        recommendations = []
        
        # Ключевые файлы проекта
        key_files = [
            "package.json", "requirements.txt", "pyproject.toml",
            "README.md", ".gitignore", "src/"
        ]
        
        missing_files = []
        for file_path in key_files:
            if not (self.workspace / file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            issues.append("missing_key_files")
            recommendations.append(f"Добавьте недостающие файлы: {', '.join(missing_files)}")
        
        # Проверка дублирования структур
        src_exists = (self.workspace / "src").exists()
        app_exists = (self.workspace / "app").exists()
        
        if src_exists and app_exists:
            issues.append("duplicate_structure")
            recommendations.append("Удалите дублирующую структуру src/ или app/")
        
        return {
            "issues": issues,
            "recommendations": recommendations,
            "missing_key_files": missing_files,
            "has_src": src_exists,
            "has_app": app_exists,
            "structure_conflict": src_exists and app_exists
        }
    
    def check_cursor_processes(self) -> Dict[str, Any]:
        """Проверка процессов Cursor"""
        issues = []
        recommendations = []
        processes = []
        
        try:
            # Поиск процессов Cursor
            if sys.platform == "win32":
                result = subprocess.run(["tasklist", "/FI", "IMAGENAME eq Cursor.exe"], 
                                      capture_output=True, text=True)
                if "Cursor.exe" in result.stdout:
                    processes.append("Cursor.exe")
            else:
                result = subprocess.run(["pgrep", "-f", "cursor"], 
                                      capture_output=True, text=True)
                if result.stdout.strip():
                    processes.append("cursor")
            
            if not processes:
                issues.append("no_cursor_process")
                recommendations.append("Запустите Cursor IDE")
            
        except Exception as e:
            issues.append("process_check_failed")
            recommendations.append(f"Ошибка проверки процессов: {e}")
        
        return {
            "issues": issues,
            "recommendations": recommendations,
            "running_processes": processes,
            "cursor_running": len(processes) > 0
        }
    
    def check_environment_variables(self) -> Dict[str, Any]:
        """Проверка переменных окружения"""
        issues = []
        recommendations = []
        env_vars = {}
        
        # Ключевые переменные для разработки
        key_vars = ["PATH", "PYTHONPATH", "NODE_PATH", "CURSOR_API_KEY"]
        
        for var in key_vars:
            value = os.environ.get(var)
            env_vars[var] = "SET" if value else "NOT_SET"
            
            if not value and var in ["PATH", "PYTHONPATH"]:
                issues.append(f"missing_env_var_{var}")
                recommendations.append(f"Установите переменную окружения: {var}")
        
        return {
            "issues": issues,
            "recommendations": recommendations,
            "environment_variables": env_vars
        }
    
    def audit_environment(self) -> Dict[str, Any]:
        """Полный аудит Cursor-окружения"""
        try:
            # Выполнение всех проверок
            workspace_check = self.check_workspace_consistency()
            mcp_check = self.check_mcp_integrations()
            cache_check = self.check_cursor_cache()
            project_check = self.check_project_structure()
            process_check = self.check_cursor_processes()
            env_check = self.check_environment_variables()
            
            # Агрегация всех проблем
            all_issues = []
            all_recommendations = []
            
            for check in [workspace_check, mcp_check, cache_check, project_check, process_check, env_check]:
                all_issues.extend(check.get("issues", []))
                all_recommendations.extend(check.get("recommendations", []))
            
            # Расчёт общей оценки
            total_checks = 6
            failed_checks = sum(1 for check in [workspace_check, mcp_check, cache_check, project_check, process_check, env_check] 
                              if check.get("issues"))
            
            environment_score = (total_checks - failed_checks) / total_checks
            
            # Классификация статуса
            if environment_score >= 0.8:
                status = "excellent"
                status_icon = "🟢"
            elif environment_score >= 0.6:
                status = "good"
                status_icon = "🟡"
            elif environment_score >= 0.4:
                status = "fair"
                status_icon = "🟠"
            else:
                status = "poor"
                status_icon = "🔴"
            
            return {
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "audit_type": "cursor_environment",
                "workspace_path": str(self.workspace),
                "environment_score": environment_score,
                "status": status,
                "status_icon": status_icon,
                "total_issues": len(all_issues),
                "total_recommendations": len(all_recommendations),
                "checks": {
                    "workspace_consistency": workspace_check,
                    "mcp_integrations": mcp_check,
                    "cursor_cache": cache_check,
                    "project_structure": project_check,
                    "cursor_processes": process_check,
                    "environment_variables": env_check
                },
                "all_issues": all_issues,
                "all_recommendations": all_recommendations
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "status": "failed"
            }

def main():
    """Основная функция для запуска аудита Cursor-окружения"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Аудит Cursor-окружения TERAG AI-REPS')
    parser.add_argument('--output', '-o', help='Директория для сохранения отчёта')
    parser.add_argument('--format', '-f', choices=['json', 'markdown'], default='json', help='Формат вывода')
    
    args = parser.parse_args()
    
    auditor = CursorEnvironmentAuditor()
    result = auditor.audit_environment()
    
    if args.output:
        output_dir = pathlib.Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if args.format == 'json':
            output_file = output_dir / "cursor_env.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"Отчёт сохранён: {output_file}")
        elif args.format == 'markdown':
            output_file = output_dir / "cursor_env.md"
            markdown_report = generate_markdown_report(result)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(markdown_report)
            print(f"Отчёт сохранён: {output_file}")
    else:
        if args.format == 'json':
            print(json.dumps(result, indent=2, ensure_ascii=False), flush=True)
        elif args.format == 'markdown':
            print(generate_markdown_report(result), flush=True)

def generate_markdown_report(result: Dict[str, Any]) -> str:
    """Генерация Markdown отчёта"""
    if 'error' in result:
        return f"# ❌ Ошибка аудита Cursor-окружения\n\n{result['error']}"
    
    status_icon = result.get('status_icon', '❓')
    status = result.get('status', 'unknown')
    score = result.get('environment_score', 0.0)
    
    report = f"""# 🔧 Cursor Environment Audit

**Статус:** {status_icon} {status}  
**Оценка окружения:** {score:.3f}  
**Время аудита:** {result['timestamp']}  
**Рабочее пространство:** `{result['workspace_path']}`  

## 📊 Сводка

- **Всего проблем:** {result['total_issues']}
- **Рекомендаций:** {result['total_recommendations']}

## 🔍 Детальные проверки

### 🏠 Согласованность рабочего пространства
- **Git репозиторий:** {'✅' if result['checks']['workspace_consistency']['git_available'] else '❌'}
- **Конфигурация Cursor:** {'✅' if result['checks']['workspace_consistency']['cursor_project_config'] else '❌'}
- **Проблемы:** {len(result['checks']['workspace_consistency']['issues'])}

### 🔌 MCP-интеграции
- **Активных MCP:** {len(result['checks']['mcp_integrations']['active_mcp'])}
- **Устаревших MCP:** {len(result['checks']['mcp_integrations']['stale_mcp'])}
- **Проблемы:** {len(result['checks']['mcp_integrations']['issues'])}

### 💾 Кэш Cursor
- **Размер кэша:** {result['checks']['cursor_cache']['cache_info'].get('size_mb', 0)} MB
- **Файлов в кэше:** {result['checks']['cursor_cache']['cache_info'].get('files_count', 0)}
- **Проблемы:** {len(result['checks']['cursor_cache']['issues'])}

### 📁 Структура проекта
- **Конфликт структур:** {'⚠️' if result['checks']['project_structure']['structure_conflict'] else '✅'}
- **Недостающих файлов:** {len(result['checks']['project_structure']['missing_key_files'])}
- **Проблемы:** {len(result['checks']['project_structure']['issues'])}

### 🖥️ Процессы Cursor
- **Cursor запущен:** {'✅' if result['checks']['cursor_processes']['cursor_running'] else '❌'}
- **Проблемы:** {len(result['checks']['cursor_processes']['issues'])}

### 🌍 Переменные окружения
- **Проблемы:** {len(result['checks']['environment_variables']['issues'])}

## 🎯 Рекомендации

"""
    
    for i, rec in enumerate(result['all_recommendations'], 1):
        report += f"{i}. {rec}\n"
    
    if not result['all_recommendations']:
        report += "✅ Все проверки пройдены успешно!\n"
    
    return report

if __name__ == "__main__":
    main()
