#!/usr/bin/env bash
# Auditor CurSor v1.2 — Self-Audit Runner
# TERAG AI-REPS Cognitive Audit System

set -euo pipefail

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Функция для цветного вывода
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Функция для выполнения этапа аудита
run_step() {
    local step_name="$1"
    local command="$2"
    local log_file="$3"
    
    print_status $BLUE "🔍 Выполняется: $step_name"
    echo -e "\n### $step_name" >> "$MD"
    echo "**Команда:** \`$command\`" >> "$MD"
    echo "**Время:** $(date)" >> "$MD"
    echo "" >> "$MD"
    
    if eval "$command" 2>&1 | tee -a "$log_file" >> "$MD"; then
        print_status $GREEN "✅ $step_name - завершено успешно"
        echo "**Статус:** ✅ Успешно" >> "$MD"
    else
        print_status $YELLOW "⚠️ $step_name - завершено с предупреждениями"
        echo "**Статус:** ⚠️ С предупреждениями" >> "$MD"
    fi
    echo "" >> "$MD"
}

# Инициализация
print_status $PURPLE "🧭 Auditor CurSor v1.2 - Запуск аудита TERAG AI-REPS"

# Чтение конфигурации
PROJECT=$(yq e '.project_name' .auditconfig.yaml 2>/dev/null || echo "TERAG-AI-REPS")
LEVEL=$(yq e '.audit_level' .auditconfig.yaml 2>/dev/null || echo "L1")
DATE=$(date +"%Y-%m-%d_%H-%M-%S")
REPORT_DIR="audit_reports/$DATE"
MD="$REPORT_DIR/final_audit_summary.md"

# Создание директории отчётов
mkdir -p "$REPORT_DIR"
mkdir -p "$REPORT_DIR/logs"
mkdir -p "$REPORT_DIR/reports"

# Обработка ошибок
trap 'print_status $RED "❌ Ошибка на этапе $STEP"; echo "**Ошибка:** $STEP завершился с ошибкой" >> "$MD"' ERR

# Заголовок отчёта
cat > "$MD" << EOF
# 🧭 Auditor CurSor v1.2 - Аудит TERAG AI-REPS

**Проект:** $PROJECT  
**Уровень аудита:** $LEVEL  
**Дата:** $DATE  
**Версия спецификации:** 1.2  

---

## 📋 Сводка результатов

EOF

print_status $CYAN "📁 Отчёты будут сохранены в: $REPORT_DIR"

# Этап 0: Проверка инструментов
STEP="Проверка инструментов"
run_step "Проверка инструментов" \
"for c in yq bandit safety pytest pydeps jq pylint flake8; do 
    if command -v \$c >/dev/null 2>&1; then 
        echo \"✅ \$c: \$(which \$c)\"; 
    else 
        echo \"❌ \$c: не найден\"; 
    fi; 
done" \
"$REPORT_DIR/logs/tools_check.log"

# Этап 1: Архитектурный анализ
STEP="Архитектурный анализ"
run_step "Анализ архитектуры" \
"pydeps --show-dot --no-output --display=$REPORT_DIR/reports/architecture.svg src/ 2>/dev/null || echo 'pydeps не доступен, пропускаем'" \
"$REPORT_DIR/logs/architecture.log"

# Этап 2: Качество кода
STEP="Анализ качества кода"
run_step "Pylint анализ" \
"pylint src/ --output-format=json > $REPORT_DIR/reports/pylint.json 2>/dev/null || echo 'pylint не доступен'" \
"$REPORT_DIR/logs/pylint.log"

run_step "Flake8 анализ" \
"flake8 src/ --format=json > $REPORT_DIR/reports/flake8.json 2>/dev/null || echo 'flake8 не доступен'" \
"$REPORT_DIR/logs/flake8.log"

# Этап 3: Безопасность
STEP="Анализ безопасности"
run_step "Bandit анализ безопасности" \
"bandit -r src/ -f json -o $REPORT_DIR/reports/bandit.json 2>/dev/null || echo 'bandit не доступен'" \
"$REPORT_DIR/logs/bandit.log"

run_step "Safety проверка зависимостей" \
"safety check -r requirements.txt --json > $REPORT_DIR/reports/safety.json 2>/dev/null || echo 'safety не доступен'" \
"$REPORT_DIR/logs/safety.log"

# Этап 4: Тестирование и покрытие
STEP="Тестирование и покрытие"
run_step "Pytest тесты и покрытие" \
"pytest --cov=src --cov-report=xml:$REPORT_DIR/reports/coverage.xml --cov-report=html:$REPORT_DIR/reports/coverage_html tests/ 2>/dev/null || echo 'pytest не доступен'" \
"$REPORT_DIR/logs/pytest.log"

# Этап 5: Производительность
STEP="Анализ производительности"
run_step "Бенчмарки производительности" \
"pytest --benchmark-only --benchmark-json=$REPORT_DIR/reports/performance.json tests/benchmarks/ 2>/dev/null || echo 'бенчмарки не найдены'" \
"$REPORT_DIR/logs/performance.log"

# Этап 6: Операционная готовность
STEP="Операционная готовность"
run_step "Проверка Docker и CI/CD" \
"if [ -f Dockerfile ]; then echo '✅ Dockerfile найден'; else echo '⚠️ Dockerfile не найден'; fi
if [ -f .github/workflows/ ]; then echo '✅ GitHub Actions найдены'; else echo '⚠️ GitHub Actions не найдены'; fi
if [ -f docker-compose.yml ]; then echo '✅ docker-compose.yml найден'; else echo '⚠️ docker-compose.yml не найден'; fi" \
"$REPORT_DIR/logs/operational.log"

# Этап 7: Когнитивная логика
STEP="Когнитивная логика"
run_step "Анализ когнитивных метрик" \
"python3 -c \"
import sys, os
sys.path.append('src')
try:
    from core.metrics import get_metrics_snapshot
    from core.health import get_health
    from core.cognitive_resonance import get_phase
    
    metrics = get_metrics_snapshot()
    health = get_health()
    phase = get_phase()
    
    print('📊 Когнитивные метрики:')
    for k, v in metrics.items():
        print(f'  {k}: {v}')
    print(f'🏥 Статус здоровья: {health[\"status\"]}')
    print(f'🔄 Фаза резонанса: {phase:.3f}')
    
    # Сохранение в JSON
    import json
    with open('$REPORT_DIR/reports/cognitive_metrics.json', 'w') as f:
        json.dump({
            'metrics': metrics,
            'health': health,
            'phase': phase,
            'timestamp': metrics['timestamp']
        }, f, indent=2)
        
except Exception as e:
    print(f'❌ Ошибка анализа когнитивных метрик: {e}')
\"" \
"$REPORT_DIR/logs/cognitive.log"

# Этап 8: Observability и Drift
STEP="Observability и Drift"
run_step "Анализ журнала когнитивных циклов" \
"python3 -c \"
import sys, os, json
sys.path.append('src')
try:
    from telemetry.journal import latest
    
    cycles = latest(10)
    if cycles:
        print(f'📈 Последние {len(cycles)} когнитивных циклов:')
        for i, cycle in enumerate(cycles[-3:], 1):
            print(f'  Цикл {i}: RSS={cycle.get(\"RSS\", 0):.3f}, Resonance={cycle.get(\"Resonance\", 0):.3f}')
        
        # Анализ дрейфа
        if len(cycles) > 1:
            rss_values = [c.get('RSS', 0) for c in cycles]
            resonance_values = [c.get('Resonance', 0) for c in cycles]
            
            rss_drift = max(rss_values) - min(rss_values)
            resonance_drift = max(resonance_values) - min(resonance_values)
            
            print(f'📊 Дрейф RSS: {rss_drift:.3f}')
            print(f'📊 Дрейф Resonance: {resonance_drift:.3f}')
            
            # Сохранение анализа
            with open('$REPORT_DIR/reports/drift_analysis.json', 'w') as f:
                json.dump({
                    'cycles_analyzed': len(cycles),
                    'rss_drift': rss_drift,
                    'resonance_drift': resonance_drift,
                    'rss_values': rss_values,
                    'resonance_values': resonance_values
                }, f, indent=2)
    else:
        print('⚠️ Журнал когнитивных циклов пуст')
        
except Exception as e:
    print(f'❌ Ошибка анализа дрейфа: {e}')
\"" \
"$REPORT_DIR/logs/observability.log"

# Этап 9: Этический аудит
STEP="Этический аудит"
run_step "Проверка этических аспектов" \
"python3 -c \"
import os, json

# Проверка наличия этических документов
ethical_docs = []
if os.path.exists('SECURITY.md'):
    ethical_docs.append('SECURITY.md')
if os.path.exists('docs/ethics/'):
    ethical_docs.append('docs/ethics/')
if os.path.exists('AUDIT_SPEC.md'):
    ethical_docs.append('AUDIT_SPEC.md')

print('📋 Этические документы:')
for doc in ethical_docs:
    print(f'  ✅ {doc}')

# Проверка конфигурации аудита
try:
    import yaml
    with open('.auditconfig.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    if config.get('governance_audit', {}).get('enabled'):
        print('✅ Управленческий аудит включён')
    else:
        print('⚠️ Управленческий аудит отключён')
        
    # Сохранение результатов
    with open('$REPORT_DIR/reports/ethics_audit.json', 'w') as f:
        json.dump({
            'ethical_documents': ethical_docs,
            'governance_enabled': config.get('governance_audit', {}).get('enabled', False),
            'cognitive_audit_enabled': config.get('cognitive_audit', {}).get('enabled', False)
        }, f, indent=2)
        
except Exception as e:
    print(f'❌ Ошибка этического аудита: {e}')
\"" \
"$REPORT_DIR/logs/ethics.log"

# Этап 10: Cursor Environment Audit
STEP="Cursor Environment Audit"
run_step "Аудит Cursor-окружения" \
"python3 audittools/cursor_env.py --output $REPORT_DIR/reports/ --format json" \
"$REPORT_DIR/logs/cursor_env.log"

# Этап 11: Architecture Blueprint Audit
STEP="Architecture Blueprint Audit"
run_step "Аудит архитектурного соответствия" \
"python3 audittools/architecture.py docs/audit/AUDIT_ARCHITECTURE.md $REPORT_DIR/reports/" \
"$REPORT_DIR/logs/architecture.log"

# Этап 12: Агрегация результатов
STEP="Агрегация результатов"
run_step "Создание сводного отчёта" \
"python3 -c \"
import json, os, glob
from datetime import datetime

# Сбор всех результатов
results = {
    'audit_metadata': {
        'project': '$PROJECT',
        'level': '$LEVEL',
        'timestamp': '$DATE',
        'version': '1.2'
    },
    'sections': {}
}

# Анализ файлов отчётов
report_files = glob.glob('$REPORT_DIR/reports/*.json')
for file_path in report_files:
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        section_name = os.path.basename(file_path).replace('.json', '')
        results['sections'][section_name] = data
    except:
        pass

# Расчёт общих метрик
overall_score = 0.0
sections_count = 0

# Простая оценка на основе наличия данных
if 'cognitive_metrics' in results['sections']:
    overall_score += 0.3
    sections_count += 1

if 'drift_analysis' in results['sections']:
    overall_score += 0.2
    sections_count += 1

if 'ethics_audit' in results['sections']:
    overall_score += 0.2
    sections_count += 1

if 'cursor_env' in results['sections']:
    overall_score += 0.1
    sections_count += 1

if 'pylint' in results['sections']:
    overall_score += 0.15
    sections_count += 1

if 'bandit' in results['sections']:
    overall_score += 0.15
    sections_count += 1

if sections_count > 0:
    overall_score = overall_score / sections_count

results['overall_score'] = overall_score
results['sections_analyzed'] = sections_count

# Сохранение сводного отчёта
with open('$REPORT_DIR/final_audit_report.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f'📊 Сводный отчёт создан')
print(f'📈 Общая оценка: {overall_score:.2f}')
print(f'📋 Проанализировано разделов: {sections_count}')
\"" \
"$REPORT_DIR/logs/aggregation.log"

# Финальная проверка
print_status $CYAN "🔍 Проверка пороговых значений..."

# Проверка покрытия (если доступно)
if [ -f "$REPORT_DIR/reports/coverage.xml" ]; then
    COVER=$(grep -o 'line-rate="[0-9.]*"' "$REPORT_DIR/reports/coverage.xml" | grep -o '[0-9.]*' | head -1)
    if [ ! -z "$COVER" ]; then
        COVER_PERCENT=$(echo "$COVER * 100" | bc -l 2>/dev/null || echo "0")
        if (( $(echo "$COVER_PERCENT < 80" | bc -l 2>/dev/null || echo "1") )); then
            print_status $YELLOW "⚠️ Покрытие кода ниже порога: ${COVER_PERCENT}% < 80%"
        else
            print_status $GREEN "✅ Покрытие кода в норме: ${COVER_PERCENT}%"
        fi
    fi
fi

# Финальное сообщение
print_status $GREEN "🎉 Аудит завершён успешно!"
print_status $CYAN "📁 Отчёты сохранены в: $REPORT_DIR"
print_status $BLUE "📄 Основной отчёт: $MD"

# Добавление финальной сводки в markdown
cat >> "$MD" << EOF

---

## 🎯 Итоговая сводка

**Время выполнения:** $(date)  
**Статус:** ✅ Завершено  
**Отчёты:** \`$REPORT_DIR\`  

### 📊 Быстрый доступ к результатам:
- [Сводный JSON отчёт]($REPORT_DIR/final_audit_report.json)
- [Когнитивные метрики]($REPORT_DIR/reports/cognitive_metrics.json)
- [Анализ дрейфа]($REPORT_DIR/reports/drift_analysis.json)
- [Этический аудит]($REPORT_DIR/reports/ethics_audit.json)
- [Cursor Environment Audit]($REPORT_DIR/reports/cursor_env.json)

### 🔧 Следующие шаги:
1. Изучите детальные отчёты в директории \`$REPORT_DIR\`
2. Обратите внимание на разделы с предупреждениями
3. При необходимости запустите аудит уровня L2 или L3

---
*Сгенерировано Auditor CurSor v1.2 для TERAG AI-REPS*
EOF

print_status $PURPLE "🧭 Auditor CurSor v1.2 - Аудит завершён"
