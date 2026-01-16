#!/usr/bin/env python3
"""
Скрипт для проверки уязвимостей в зависимостях
Проверяет Python и Node.js пакеты
"""
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


def run_command(cmd: List[str], capture_output: bool = True) -> tuple[int, str, str]:
    """Выполнить команду и вернуть результат"""
    try:
        result = subprocess.run(
            cmd,
            capture_output=capture_output,
            text=True,
            check=False
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)


def check_python_vulnerabilities() -> Dict[str, Any]:
    """Проверить уязвимости в Python пакетах"""
    print("🔍 Проверка Python зависимостей...")
    
    results = {
        "safety": {},
        "pip_audit": {},
        "outdated": []
    }
    
    # Safety check
    print("  → Запуск safety check...")
    code, stdout, stderr = run_command(["safety", "check", "--json"])
    if code == 0 or stdout:
        try:
            results["safety"] = json.loads(stdout) if stdout else {}
        except:
            results["safety"] = {"raw": stdout}
    else:
        results["safety"] = {"error": "safety не установлен или произошла ошибка"}
    
    # Pip audit (альтернатива)
    print("  → Запуск pip-audit...")
    code, stdout, stderr = run_command(["pip-audit", "--format=json"])
    if code == 0 or stdout:
        try:
            results["pip_audit"] = json.loads(stdout) if stdout else {}
        except:
            results["pip_audit"] = {"raw": stdout}
    else:
        results["pip_audit"] = {"error": "pip-audit не установлен"}
    
    # Устаревшие пакеты
    print("  → Проверка устаревших пакетов...")
    code, stdout, stderr = run_command(["pip", "list", "--outdated", "--format=json"])
    if code == 0 and stdout:
        try:
            results["outdated"] = json.loads(stdout)
        except:
            results["outdated"] = []
    
    return results


def check_node_vulnerabilities() -> Dict[str, Any]:
    """Проверить уязвимости в Node.js пакетах"""
    print("🔍 Проверка Node.js зависимостей...")
    
    results = {
        "npm_audit": {},
        "outdated": []
    }
    
    # NPM audit
    print("  → Запуск npm audit...")
    code, stdout, stderr = run_command(["npm", "audit", "--json"])
    if code == 0 or stdout:
        try:
            results["npm_audit"] = json.loads(stdout) if stdout else {}
        except:
            results["npm_audit"] = {"raw": stdout}
    
    # Устаревшие пакеты
    print("  → Проверка устаревших пакетов...")
    code, stdout, stderr = run_command(["npm", "outdated", "--json"])
    if code == 0 and stdout:
        try:
            results["outdated"] = json.loads(stdout) if stdout else {}
        except:
            results["outdated"] = {}
    
    return results


def generate_report(python_results: Dict, node_results: Dict) -> str:
    """Сгенерировать отчет"""
    report = f"""# 🔒 Отчет о проверке уязвимостей

**Дата:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📊 Python зависимости

### Safety Check
"""
    
    if "error" in python_results.get("safety", {}):
        report += f"⚠️ {python_results['safety']['error']}\n\n"
    elif python_results.get("safety"):
        vulns = python_results["safety"].get("vulnerabilities", [])
        if vulns:
            report += f"❌ Найдено уязвимостей: {len(vulns)}\n\n"
            for vuln in vulns[:10]:  # Первые 10
                report += f"- **{vuln.get('package', 'Unknown')}**: {vuln.get('vulnerability', 'Unknown')}\n"
        else:
            report += "✅ Уязвимостей не найдено\n\n"
    
    report += "\n### Устаревшие пакеты\n\n"
    outdated = python_results.get("outdated", [])
    if outdated:
        report += f"Найдено устаревших пакетов: {len(outdated)}\n\n"
        # Показываем критичные
        critical = ["fastapi", "pydantic", "redis", "cryptography", "urllib3", "requests"]
        for pkg in outdated[:20]:
            name = pkg.get("name", "")
            if name.lower() in critical or len(outdated) <= 20:
                report += f"- **{name}**: {pkg.get('version', '?')} → {pkg.get('latest_version', '?')}\n"
    else:
        report += "✅ Все пакеты актуальны\n\n"
    
    report += "\n---\n\n## 📦 Node.js зависимости\n\n"
    
    npm_audit = node_results.get("npm_audit", {})
    if "vulnerabilities" in npm_audit:
        vulns = npm_audit["vulnerabilities"]
        total = npm_audit.get("metadata", {}).get("vulnerabilities", {}).get("total", 0)
        if total > 0:
            report += f"❌ Найдено уязвимостей: {total}\n\n"
            # Показываем критичные
            critical_vulns = [
                v for v in vulns.values() 
                if v.get("severity") in ["critical", "high"]
            ][:10]
            for vuln in critical_vulns:
                report += f"- **{vuln.get('name', 'Unknown')}**: {vuln.get('severity', 'unknown')} - {vuln.get('title', '')}\n"
        else:
            report += "✅ Уязвимостей не найдено\n\n"
    else:
        report += "⚠️ Не удалось получить данные npm audit\n\n"
    
    return report


def main():
    """Главная функция"""
    print("=" * 60)
    print("🔒 Проверка уязвимостей в зависимостях TERAG")
    print("=" * 60)
    print()
    
    # Проверка Python
    python_results = check_python_vulnerabilities()
    print()
    
    # Проверка Node.js
    node_results = check_node_vulnerabilities()
    print()
    
    # Генерация отчета
    report = generate_report(python_results, node_results)
    
    # Сохранение отчета
    report_file = Path("reports") / f"vulnerabilities_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    report_file.parent.mkdir(exist_ok=True)
    report_file.write_text(report, encoding="utf-8")
    
    print("=" * 60)
    print(f"✅ Отчет сохранен: {report_file}")
    print("=" * 60)
    print()
    print(report)
    
    # Сохранение JSON для CI/CD
    json_file = Path("reports") / f"vulnerabilities_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    json_file.write_text(
        json.dumps({
            "python": python_results,
            "node": node_results,
            "timestamp": datetime.now().isoformat()
        }, indent=2),
        encoding="utf-8"
    )
    
    return 0


if __name__ == "__main__":
    sys.exit(main())









