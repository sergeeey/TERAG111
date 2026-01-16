# 🧭 Auditor CurSor Unified AI-Audit Spec v1.2

## Назначение
Воспроизводимый, измеримый и саморефлексивный аудит AI-систем — от инженерных основ до когнитивной целостности.

## Применение
- LLM-агенты
- ML-модели
- Когнитивные пайплайны
- Мультиагентные системы

## Стандарты
- COBIT 2019
- ISO 27001 / 42010 / 12207 / 25010
- ITAF 4.0
- DORA
- OWASP Top-10 for LLM
- CSA 2.0
- NIST AI RMF

---

## 💠 0. Подготовка среды

```bash
git clone <repository_url> project && cd project
pip install -r requirements.txt
pip install bandit safety pytest pydeps pylint flake8 jq
```

Создать `.auditconfig.yaml`:
```yaml
audit_level: L3
project_name: "TERAG"
source_dirs: ["src/", "core/"]
test_dir: "tests/"
thresholds:
  coverage: 80
  security_issues: 5
  coupling: 0.4

meta_audit:
  version: 1.2
  spec_hash: <SHA256_of_spec>
  self_validation:
    - internal_consistency
    - metric_coherence
    - reproducibility_score

update_policy:
  feedback_loop: enabled
  report_channel: "AI-Governance/Spec-Feedback"
```

---

## 🚀 1. Уровни аудита

| Уровень | Время | Цель |
|---------|-------|------|
| L1 | 15 мин | Базовая жизнеспособность |
| L2 | 1–2 ч | Готовность к развёртыванию |
| L3 | 4+ ч | Когнитивная и операционная зрелость, сертификация |

---

## 🧱 2. Полная структура аудита

| № | Этап | Проверяется | Инструменты / логика | Метрики |
|---|------|-------------|----------------------|---------|
| 0 | Подготовка среды | Конфигурация и зависимости | yq, pip, .auditconfig.yaml | env_integrity |
| 1 | Архитектура | Модульность, связи | pydeps, audittools.architecture | architecture_score, coupling |
| 2 | Качество кода | PEP8, ошибки, логика | pylint, flake8 | code_quality, logic_consistency |
| 3 | Безопасность | Уязвимости, prompt injection | bandit, safety | security_ratio, risk_level |
| 4 | Тестирование | Покрытие и достоверность | pytest --cov | coverage, verification_confidence |
| 5 | Производительность | Нагрузка и стабильность | pytest --benchmark-only | performance_score |
| 6 | Операционная готовность | CI/CD, Docker, мониторинг | проверка Dockerfile, healthcheck | operational_readiness |
| 7 | Когнитивная логика | Observe → Decide → Act | audittools.cognitive | rss, cos, self_validation |
| 8 | Observability / Drift | Наблюдаемость, старение | audittools.observability, drift | drift_index, stability_trend |
| 9 | Этика и ценности | Справедливость, приватность | audittools.ethics | bias_index, alignment_score |
| 10 | Explainability | Применение SHAP/LIME | audittools.explainability | transparency, explain_use |
| 11 | Resilience | Восстановление после сбоя | тесты failover / recovery | recovery_time, graceful_degradation |
| 12 | Socio-Technical Context | Human-in-loop, роли | анализ ролей / логов решений | human_feedback_ratio |
| 13 | Governance Continuity | Политики, RACI, миссия | audittools.governance | mission_integrity |
| 14 | Meta-Audit Loop | Сравнение истории аудитов | анализ audit_history | delta_score, improvement_rate |
| 15 | Агрегация / Отчёт | Сбор всех результатов | audittools.aggregate | overall_score |
| 16 | Интерпретация и прогноз | Анализ трендов | rss, drift | future_stability |

---

## 🔧 3. Скрипт запуска audit_runner.sh

```bash
#!/usr/bin/env bash
# Auditor CurSor v1.2 — Self-Audit Runner
set -euo pipefail

PROJECT=$(yq e '.project_name' .auditconfig.yaml 2>/dev/null || echo "Unknown")
LEVEL=$(yq e '.audit_level' .auditconfig.yaml 2>/dev/null || echo "L1")
DATE=$(date +"%Y-%m-%d_%H-%M-%S")
REPORT_DIR="audit_reports/$DATE"
MD="$REPORT_DIR/final_audit_summary.md"

mkdir -p "$REPORT_DIR"
trap 'echo "❌ Ошибка на этапе $STEP" >> "$MD"' ERR

run_step() {
    STEP="$1"
    CMD="$2"
    echo -e "\n### $STEP" | tee -a "$MD"
    eval "$CMD" 2>&1 | tee -a "$MD" || true
}

echo "# 🧭 Auditor CurSor v1.2" | tee "$MD"
echo "**Проект:** $PROJECT | **Уровень:** $LEVEL | **Дата:** $DATE" >> "$MD"

run_step "Проверка инструментов" \
    "for c in yq bandit safety pytest pydeps jq pylint flake8; do command -v \$c >/dev/null || echo '⚠️ отсутствует '\$c; done"

run_step "Архитектура" \
    "pydeps --show-dot --no-output --display=$REPORT_DIR/arch.svg src/"

run_step "Качество кода" \
    "pylint src > $REPORT_DIR/pylint.log || true"

run_step "Безопасность" \
    "bandit -r src/ -f json -o $REPORT_DIR/bandit.json && safety check -r requirements.txt --json > $REPORT_DIR/safety.json"

run_step "Тесты и покрытие" \
    "pytest --cov=src --cov-report=xml:$REPORT_DIR/coverage.xml tests/ || true"

run_step "Бенчмарки" \
    "pytest --benchmark-only --benchmark-json=$REPORT_DIR/perf.json tests/benchmarks/ || true"

run_step "Когнитивная логика" \
    "python3 -m audittools.cognitive analyze reasoning_traces.log > $REPORT_DIR/cognitive.json || true"

run_step "Drift и Observability" \
    "python3 -m audittools.observability check > $REPORT_DIR/observability.json || true"

run_step "Этический слой" \
    "python3 -m audittools.ethics evaluate --config mission.yaml > $REPORT_DIR/ethics.json || true"

run_step "Агрегация" \
    "python3 -m audittools.aggregate $REPORT_DIR > $REPORT_DIR/final_audit_report.json"

COVER=$(grep -Eo '"coverage":[[:space:]]*[0-9]+' "$REPORT_DIR/final_audit_report.json" | grep -Eo '[0-9]+' || echo 0)
if [[ $COVER -lt 80 ]]; then echo "❌ Coverage ниже порога (80%)" | tee -a "$MD"; exit 1; fi

echo "✅ Аудит завершён. Отчёты: $REPORT_DIR" | tee -a "$MD"
```

---

## 📊 4. Цветовые статусы

| Балл | Статус | Интерпретация |
|------|--------|---------------|
| 0–0.59 | 🔴 | Требуется реструктуризация |
| 0.6–0.79 | 🟡 | Работоспособно, но требует улучшений |
| 0.8–1.0 | 🟢 | Готово к production и сертификации |

---

## 🧠 5. Когнитивная когерентность Spec

```
meta_consistency_index = (alignment_with_mission*0.5) + (metric_coherence*0.3) + (terminology_consistency*0.2)
```

Если < 0.8 → спецификация требует пересмотра.

---

## 🪞 6. Завершение и прогноз

После выполнения `audit_runner.sh` система формирует:

- **final_audit_report.json** — сводные метрики и оценки;
- **final_audit_summary.md** — человекочитаемый отчёт;
- **Cognitive_Audit_Card.md** — карта когнитивного состояния;
- **POA&M.xlsx** — план корректирующих действий;
- **Audit_Maturity_Model.md** — уровень зрелости проекта.

---

## ✅ 7. Как использовать

1. Скопируй `AUDIT_SPEC.md`, `.auditconfig.yaml` и `audit_runner.sh` в корень проекта.
2. Выполни:
```bash
chmod +x audit_runner.sh
./audit_runner.sh
```
3. Полученные отчёты появятся в `audit_reports/<дата>`.

---

## 💡 Смысл

**Auditor CurSor v1.2** — это не просто скрипт.
Это интеллектуальная экосистема проверки, где:

- код проверяется на логическую и архитектурную чистоту;
- ИИ — на последовательность и соответствие миссии;
- сама спецификация — на внутреннюю когерентность.

Аудит не только ищет ошибки, но и **учится на них**, превращаясь в саморефлексивный стандарт инженерной зрелости.