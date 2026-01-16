from fastapi import FastAPI, Body, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from datetime import datetime, timezone
import os
import json
import hashlib
from pathlib import Path
from src.core.metrics import get_metrics_snapshot
from src.core.health import get_health
from src.core.self_learning import accept_feedback
from src.api.middleware.security import SecurityHeadersMiddleware, RateLimitMiddleware
from src.core.cache import get_cache

# PromptOps router (Phase 4)
try:
    from src.promptops.router import router as promptops_router
    PROMPTOPS_AVAILABLE = True
except ImportError:
    PROMPTOPS_AVAILABLE = False
    logger.warning("PromptOps router not available")

app = FastAPI(title='AI-REPS API', version='4.3')

# Инициализация кэша
cache = get_cache(
    redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    default_ttl=3600
)

# Security middleware (добавляется первым, чтобы обрабатывать все запросы)
app.add_middleware(SecurityHeadersMiddleware)

# Rate limiting middleware
# Настройки: 60 запросов/минуту, 1000/час, burst 10
app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=60,
    requests_per_hour=1000,
    burst_size=10
)

# CORS middleware
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])

# PromptOps router (Phase 4)
if PROMPTOPS_AVAILABLE:
    app.include_router(promptops_router)

# SSE Stream router (Phase 5)
try:
    from src.api.routes.stream import router as stream_router
    app.include_router(stream_router)
except ImportError:
    logger.warning("Stream router not available")

@app.get('/')
def root():
    return {'name':'AI-REPS API','version':'4.3','time':datetime.now(timezone.utc).isoformat()}

@app.get('/api/metrics')
def api_metrics():
    """Получение метрик AI-REPS с кэшированием (30 секунд)"""
    cache_key = "api:metrics"
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    metrics = get_metrics_snapshot()
    cache.set(cache_key, metrics, ttl=30)  # Кэш на 30 секунд
    return metrics

@app.get('/api/health')
def api_health():
    return get_health()

@app.post('/api/feedback')
def api_feedback(payload: dict = Body(...)):
    result = accept_feedback(payload)
    return {'status':'ok','accepted':result}

@app.get('/metrics/prometheus')
def prom():
    m = get_metrics_snapshot()
    lines = []
    for k in ['RSS','COS','FAITH','Growth','Resonance','confidence']:
        lines.append(f'ai_reps_{k.lower()} {m[k]}')
    body='\n'.join(lines)+'\n'
    return Response(content=body, media_type='text/plain')

@app.get('/api/audit/latest')
def get_latest_audit():
    """Получение последнего отчёта environment-аудита для дашборда"""
    import json
    import pathlib
    from datetime import datetime
    
    try:
        # Ищем последний отчёт environment-аудита
        reports_dir = pathlib.Path("audit_reports/nightly")
        if not reports_dir.exists():
            return {"error": "No audit reports found", "timestamp": datetime.now().isoformat()}
        
        # Находим последний файл environment_audit_*.json
        env_reports = list(reports_dir.glob("environment_audit_*.json"))
        if not env_reports:
            return {"error": "No environment audit reports found", "timestamp": datetime.now().isoformat()}
        
        # Сортируем по времени создания и берём последний
        latest_report = max(env_reports, key=lambda x: x.stat().st_mtime)
        
        with open(latest_report, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Добавляем метаданные
        data['report_file'] = str(latest_report)
        data['report_timestamp'] = datetime.fromtimestamp(latest_report.stat().st_mtime).isoformat()
        
        return data
        
    except Exception as e:
        return {"error": f"Failed to load audit report: {str(e)}", "timestamp": datetime.now().isoformat()}

@app.get("/api/graph")
def get_knowledge_graph():
    """Получение графа знаний из обработанных документов с кэшированием (5 минут)"""
    cache_key = "api:graph:full"
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    try:
        # Читаем все графы из graph_results
        graph_results_dir = Path("data/graph_results")
        if not graph_results_dir.exists():
            return {'graph': [], 'edges': [], 'metadata': {'total_nodes': 0, 'total_edges': 0}}
        
        all_nodes = []
        all_edges = []
        total_triplets = 0
        processed_docs = 0
        
        # Собираем все триплеты из файлов графов
        for graph_file in graph_results_dir.glob("*_graph.json"):
            if graph_file.name == "processing_summary.json":
                continue
                
            try:
                with open(graph_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                triplets = data.get('triplets', [])
                total_triplets += len(triplets)
                processed_docs += 1
                
                # Преобразуем триплеты в узлы и связи
                for i, triplet in enumerate(triplets):
                    subject = triplet.get('subject', 'Unknown')
                    predicate = triplet.get('predicate', 'relates_to')
                    obj = triplet.get('object', 'Unknown')
                    confidence = triplet.get('confidence', 0.5)
                    
                    # Создаём узлы
                    subject_node = {
                        'id': f"{subject}_{i}",
                        'label': subject,
                        'type': 'entity',
                        'confidence': confidence
                    }
                    object_node = {
                        'id': f"{obj}_{i}",
                        'label': obj,
                        'type': 'entity', 
                        'confidence': confidence
                    }
                    
                    all_nodes.extend([subject_node, object_node])
                    
                    # Создаём связь
                    edge = {
                        'id': f"edge_{i}",
                        'source': subject_node['id'],
                        'target': object_node['id'],
                        'label': predicate,
                        'confidence': confidence
                    }
                    all_edges.append(edge)
                    
            except Exception as e:
                print(f"Ошибка чтения {graph_file}: {e}")
                continue
        
        # Удаляем дубликаты узлов
        unique_nodes = {}
        for node in all_nodes:
            key = node['label']
            if key not in unique_nodes or unique_nodes[key]['confidence'] < node['confidence']:
                unique_nodes[key] = node
        
        final_nodes = list(unique_nodes.values())
        
        # Обновляем ID в связях
        node_id_map = {node['label']: node['id'] for node in final_nodes}
        for edge in all_edges:
            source_label = next((n['label'] for n in all_nodes if n['id'] == edge['source']), edge['source'])
            target_label = next((n['label'] for n in all_nodes if n['id'] == edge['target']), edge['target'])
            
            if source_label in node_id_map and target_label in node_id_map:
                edge['source'] = node_id_map[source_label]
                edge['target'] = node_id_map[target_label]
        
        result = {
            'graph': final_nodes,
            'edges': all_edges,
            'metadata': {
                'total_nodes': len(final_nodes),
                'total_edges': len(all_edges),
                'total_triplets': total_triplets,
                'processed_documents': processed_docs,
                'last_updated': datetime.now().isoformat()
            }
        }
        
        # Сохраняем в кэш на 5 минут
        cache.set(cache_key, result, ttl=300)
        
        return result
        
    except Exception as e:
        return {'error': str(e), 'graph': [], 'edges': []}

@app.get("/api/graph/stats")
def get_graph_stats():
    """Статистика графа знаний с кэшированием (2 минуты)"""
    cache_key = "api:graph:stats"
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    try:
        graph_results_dir = Path("data/graph_results")
        if not graph_results_dir.exists():
            return {'nodes': 0, 'edges': 0, 'documents': 0, 'triplets': 0}
        
        # Читаем сводный отчёт
        summary_file = graph_results_dir / "processing_summary.json"
        if summary_file.exists():
            with open(summary_file, 'r', encoding='utf-8') as f:
                summary = json.load(f)
            
            result = {
                'nodes': summary.get('total_triplets', 0) * 2,  # Примерная оценка
                'edges': summary.get('total_triplets', 0),
                'documents': summary.get('processed_documents', 0),
                'triplets': summary.get('total_triplets', 0),
                'average_triplets_per_doc': summary.get('average_triplets_per_doc', 0)
            }
            # Кэшируем на 2 минуты
            cache.set(cache_key, result, ttl=120)
            return result
        
        result = {'nodes': 0, 'edges': 0, 'documents': 0, 'triplets': 0}
        cache.set(cache_key, result, ttl=120)
        return result
        
    except Exception as e:
        return {'error': str(e)}

@app.post("/api/set_language")
def set_language(payload: dict = Body(...)):
    """Устанавливает язык интерфейса"""
    try:
        lang = payload.get('lang', 'ru').lower()
        
        if lang not in ['ru', 'en']:
            return {'status': 'error', 'message': 'Unsupported language'}
        
        # Создаем директорию для конфигурации
        config_dir = Path("data/config")
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # Сохраняем язык
        lang_file = config_dir / "lang.txt"
        lang_file.write_text(lang, encoding='utf-8')
        
        return {'status': 'ok', 'language': lang, 'message': f'Language set to {lang}'}
        
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

@app.get("/api/get_language")
def get_language():
    """Получает текущий язык интерфейса"""
    try:
        lang_file = Path("data/config/lang.txt")
        if lang_file.exists():
            lang = lang_file.read_text(encoding='utf-8').strip()
            return {'language': lang}
        else:
            return {'language': 'ru'}  # По умолчанию русский
            
    except Exception as e:
        return {'language': 'ru', 'error': str(e)}

@app.get("/api/query")
def process_query(question: str):
    """Обработка вопросов к системе TERAG на основе графа знаний с кэшированием (5 минут)"""
    cache_key = f"query:{hashlib.md5(question.encode()).hexdigest()}"
    
    # Пробуем получить из кэша
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result
    
    try:
        from langdetect import detect
        
        # Определяем язык вопроса
        try:
            question_lang = detect(question)
            is_russian = question_lang == 'ru'
        except:
            is_russian = any(char in question for char in 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя')
        
        # Читаем граф знаний
        graph_results_dir = Path("data/graph_results")
        if not graph_results_dir.exists():
            return {
                'answer': 'Граф знаний не найден. Сначала обработайте документы.',
                'sources': [],
                'mini_graph': {'nodes': [], 'edges': []},
                'language': 'ru' if is_russian else 'en'
            }
        
        # Собираем релевантные триплеты
        relevant_triplets = []
        sources = []
        
        for graph_file in graph_results_dir.glob("*_graph.json"):
            if graph_file.name == "processing_summary.json":
                continue
                
            try:
                with open(graph_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                triplets = data.get('triplets', [])
                file_name = data.get('file', 'Unknown')
                
                # Простой поиск по ключевым словам
                question_words = question.lower().split()
                for triplet in triplets:
                    triplet_text = f"{triplet.get('subject', '')} {triplet.get('predicate', '')} {triplet.get('object', '')}".lower()
                    
                    # Проверяем пересечение слов
                    if any(word in triplet_text for word in question_words if len(word) > 3):
                        relevant_triplets.append(triplet)
                        if file_name not in sources:
                            sources.append(file_name)
                            
            except Exception as e:
                continue
        
        # Формируем ответ
        if not relevant_triplets:
            answer = "К сожалению, в базе знаний не найдено информации по вашему вопросу." if is_russian else "Sorry, no relevant information found in the knowledge base."
        else:
            # Простая генерация ответа на основе найденных триплетов
            if is_russian:
                answer = f"На основе анализа {len(relevant_triplets)} релевантных фрагментов знаний:\n\n"
                for i, triplet in enumerate(relevant_triplets[:5]):  # Берем первые 5
                    answer += f"{i+1}. {triplet.get('subject', '')} {triplet.get('predicate', '')} {triplet.get('object', '')}\n"
                if len(relevant_triplets) > 5:
                    answer += f"\n... и еще {len(relevant_triplets) - 5} связанных фактов."
            else:
                answer = f"Based on analysis of {len(relevant_triplets)} relevant knowledge fragments:\n\n"
                for i, triplet in enumerate(relevant_triplets[:5]):
                    answer += f"{i+1}. {triplet.get('subject', '')} {triplet.get('predicate', '')} {triplet.get('object', '')}\n"
                if len(relevant_triplets) > 5:
                    answer += f"\n... and {len(relevant_triplets) - 5} more related facts."
        
        # Создаем мини-граф для визуализации
        mini_graph_nodes = []
        mini_graph_edges = []
        
        # Берем первые несколько релевантных триплетов для визуализации
        for i, triplet in enumerate(relevant_triplets[:8]):
            subject = triplet.get('subject', 'Unknown')
            obj = triplet.get('object', 'Unknown')
            
            # Узлы
            subject_node = {
                'id': f"node_{i}_sub",
                'label': subject[:30] + '...' if len(subject) > 30 else subject,
                'type': 'entity'
            }
            object_node = {
                'id': f"node_{i}_obj", 
                'label': obj[:30] + '...' if len(obj) > 30 else obj,
                'type': 'entity'
            }
            
            mini_graph_nodes.extend([subject_node, object_node])
            
            # Связь
            edge = {
                'id': f"edge_{i}",
                'source': subject_node['id'],
                'target': object_node['id'],
                'label': triplet.get('predicate', 'relates_to')[:20]
            }
            mini_graph_edges.append(edge)
        
        # Удаляем дубликаты узлов
        unique_nodes = {}
        for node in mini_graph_nodes:
            if node['label'] not in unique_nodes:
                unique_nodes[node['label']] = node
        
        result = {
            'answer': answer,
            'sources': sources[:5],  # Первые 5 источников
            'mini_graph': {
                'nodes': list(unique_nodes.values()),
                'edges': mini_graph_edges
            },
            'language': 'ru' if is_russian else 'en',
            'confidence': min(0.9, len(relevant_triplets) / 10),  # Простая оценка уверенности
            'timestamp': datetime.now().isoformat()
        }
        
        # Сохраняем в кэш на 5 минут
        cache.set(cache_key, result, ttl=300)
        
        return result
        
    except Exception as e:
        return {
            'answer': f'Ошибка обработки запроса: {str(e)}',
            'sources': [],
            'mini_graph': {'nodes': [], 'edges': []},
            'language': 'ru',
            'error': str(e)
        }

@app.get("/api/llm_query")
def process_llm_query(question: str, model: str = "qwen2.5:7b-instruct", use_context: bool = True):
    """Обработка вопросов с использованием локальной LLM через Ollama"""
    try:
        from langdetect import detect
        from src.core.ollama_client import query_ollama, query_with_context
        
        # Определяем язык вопроса
        try:
            question_lang = detect(question)
            is_russian = question_lang == 'ru'
        except:
            is_russian = any(char in question for char in 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя')
        
        # Если нужно использовать контекст из графа знаний
        context = ""
        if use_context:
            graph_results_dir = Path("data/graph_results")
            if graph_results_dir.exists():
                relevant_triplets = []
                for graph_file in graph_results_dir.glob("*_graph.json"):
                    if graph_file.name == "processing_summary.json":
                        continue
                    
                    try:
                        with open(graph_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        triplets = data.get('triplets', [])
                        question_words = question.lower().split()
                        
                        for triplet in triplets:
                            triplet_text = f"{triplet.get('subject', '')} {triplet.get('predicate', '')} {triplet.get('object', '')}".lower()
                            if any(word in triplet_text for word in question_words if len(word) > 3):
                                relevant_triplets.append(triplet)
                                
                    except Exception as e:
                        continue
                
                # Формируем контекст из релевантных триплетов
                if relevant_triplets:
                    context = "\n".join([
                        f"- {t.get('subject', '')} {t.get('predicate', '')} {t.get('object', '')}"
                        for t in relevant_triplets[:10]  # Первые 10 триплетов
                    ])
        
        # Отправляем запрос в Ollama
        if context:
            answer = query_with_context(question, context, model)
        else:
            prompt = question if is_russian else question
            answer = query_ollama(prompt, model)
        
        return {
            'answer': answer,
            'model': model,
            'context_used': use_context and bool(context),
            'language': 'ru' if is_russian else 'en',
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            'answer': f'Ошибка LLM запроса: {str(e)}',
            'model': model,
            'context_used': False,
            'language': 'ru',
            'error': str(e)
        }

@app.get("/api/llm/models")
def list_llm_models():
    """Получает список доступных моделей Ollama"""
    try:
        from src.core.ollama_client import list_available_models
        models = list_available_models()
        return {'models': models, 'count': len(models)}
    except Exception as e:
        return {'models': [], 'error': str(e)}

# Добавляем поддержку статических файлов
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/api/static", StaticFiles(directory=static_dir), name="static")
