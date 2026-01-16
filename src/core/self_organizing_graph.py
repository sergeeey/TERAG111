"""
Self-Organizing Knowledge Graph — живой, саморазвивающийся граф смыслов

Концепция:
- Граф не использует жёсткие типы узлов, а создаёт их динамически
- Новые концепты появляются при низкой семантической схожести
- Правила роста применяются для эволюции графа
- Система сама балансирует свою память
"""
import logging
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np

logger = logging.getLogger(__name__)

# Импорты (опциональные)
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    logger.warning("sentence-transformers not available, embeddings will be disabled")

try:
    from src.integration.lmstudio_client import LMStudioClient
    LMSTUDIO_AVAILABLE = True
except ImportError:
    LMSTUDIO_AVAILABLE = False
    logger.warning("LMStudioClient not available")

try:
    from installer.app.modules.graph_updater import GraphUpdater
    GRAPH_UPDATER_AVAILABLE = True
except ImportError:
    GRAPH_UPDATER_AVAILABLE = False
    logger.warning("GraphUpdater not available")


class SelfOrganizingGraph:
    """
    Самоорганизующийся граф знаний
    
    Функции:
    1. Динамическая категоризация через embeddings
    2. Создание emergent концептов при низкой схожести
    3. Применение правил роста для эволюции
    4. Decay старых концептов
    5. Объединение похожих кластеров
    """
    
    def __init__(
        self,
        graph_updater: Optional[Any] = None,
        lm_client: Optional[Any] = None,
        embedder: Optional[Any] = None,
        similarity_threshold: float = 0.65,
        decay_days: int = 30
    ):
        """
        Инициализация Self-Organizing Graph
        
        Args:
            graph_updater: Экземпляр GraphUpdater
            lm_client: Экземпляр LMStudioClient (опционально)
            embedder: Экземпляр SentenceTransformer (опционально)
            similarity_threshold: Порог схожести для создания нового кластера (0.0-1.0)
            decay_days: Количество дней до начала decay неиспользуемых концептов
        """
        self.graph_updater = graph_updater
        self.lm_client = lm_client
        self.similarity_threshold = similarity_threshold
        self.decay_days = decay_days
        
        # Инициализация embedder
        if embedder:
            self.embedder = embedder
        elif EMBEDDINGS_AVAILABLE:
            try:
                self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("SentenceTransformer initialized")
            except Exception as e:
                logger.warning(f"Could not initialize SentenceTransformer: {e}")
                self.embedder = None
        else:
            self.embedder = None
        
        # Кэш для кластеров
        self.cluster_cache: Dict[str, np.ndarray] = {}
        self.cluster_metadata: Dict[str, Dict[str, Any]] = {}
        
        logger.info(f"SelfOrganizingGraph initialized (threshold={similarity_threshold})")
    
    def _get_embedding(self, text: str) -> Optional[np.ndarray]:
        """
        Получить embedding текста
        
        Args:
            text: Текст для векторизации
        
        Returns:
            Embedding вектор или None
        """
        if not self.embedder:
            return None
        
        try:
            embedding = self.embedder.encode(text, convert_to_numpy=True)
            return embedding
        except Exception as e:
            logger.error(f"Error getting embedding: {e}")
            return None
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Вычислить cosine similarity между двумя векторами
        
        Args:
            vec1: Первый вектор
            vec2: Второй вектор
        
        Returns:
            Cosine similarity (0.0-1.0)
        """
        try:
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
        except Exception as e:
            logger.error(f"Error computing cosine similarity: {e}")
            return 0.0
    
    async def _load_clusters_from_graph(self) -> Dict[str, np.ndarray]:
        """
        Загрузить кластеры из графа с их embeddings
        
        Returns:
            Словарь {cluster_name: embedding}
        """
        if not self.graph_updater or not self.graph_updater.driver:
            return {}
        
        clusters = {}
        
        try:
            with self.graph_updater.driver.session() as session:
                # Получаем все концепты с их описаниями
                query = """
                MATCH (c:Entity)
                WHERE c.description IS NOT NULL OR c.name IS NOT NULL
                RETURN c.name as name, c.description as description, c.type as type
                LIMIT 100
                """
                
                result = session.run(query)
                
                for record in result:
                    name = record["name"]
                    description = record.get("description", name)
                    text = f"{name} {description}"
                    
                    embedding = self._get_embedding(text)
                    if embedding is not None:
                        clusters[name] = embedding
                        self.cluster_metadata[name] = {
                            "type": record.get("type", "Concept"),
                            "description": description
                        }
                
                logger.debug(f"Loaded {len(clusters)} clusters from graph")
                return clusters
        
        except Exception as e:
            logger.error(f"Error loading clusters from graph: {e}")
            return {}
    
    async def find_similar_clusters(
        self,
        embedding: np.ndarray,
        limit: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Найти похожие кластеры по embedding
        
        Args:
            embedding: Embedding для поиска
            limit: Максимальное количество результатов
        
        Returns:
            Список кортежей (cluster_name, similarity)
        """
        # Загружаем кластеры, если кэш пуст
        if not self.cluster_cache:
            self.cluster_cache = await self._load_clusters_from_graph()
        
        similarities = []
        
        for cluster_name, cluster_embedding in self.cluster_cache.items():
            similarity = self._cosine_similarity(embedding, cluster_embedding)
            similarities.append((cluster_name, similarity))
        
        # Сортируем по убыванию схожести
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:limit]
    
    async def should_create_new_cluster(
        self,
        text: str,
        embedding: Optional[np.ndarray] = None
    ) -> Tuple[bool, Optional[str], float]:
        """
        Решить, нужно ли создавать новый кластер
        
        Args:
            text: Текст для анализа
            embedding: Embedding текста (если уже вычислен)
        
        Returns:
            Кортеж (should_create, best_cluster_name, max_similarity)
        """
        if embedding is None:
            embedding = self._get_embedding(text)
        
        if embedding is None:
            # Fallback: если embeddings недоступны, всегда создаём новый
            logger.warning("Embeddings not available, creating new cluster by default")
            return (True, None, 0.0)
        
        # Ищем похожие кластеры
        similar_clusters = await self.find_similar_clusters(embedding, limit=1)
        
        if not similar_clusters:
            # Нет существующих кластеров → создаём новый
            return (True, None, 0.0)
        
        best_cluster, max_similarity = similar_clusters[0]
        
        if max_similarity < self.similarity_threshold:
            # Схожесть ниже порога → создаём новый кластер
            return (True, None, max_similarity)
        else:
            # Схожесть достаточна → связываем с существующим
            return (False, best_cluster, max_similarity)
    
    async def create_emergent_concept(
        self,
        name: str,
        description: str,
        confidence: float = 0.75,
        source_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Создать emergent концепт (новый кластер)
        
        Args:
            name: Название концепта
            description: Описание концепта
            confidence: Уровень уверенности
            source_url: URL источника
        
        Returns:
            Информация о созданном концепте
        """
        if not self.graph_updater:
            logger.warning("GraphUpdater not available, cannot create emergent concept")
            return {"created": False, "error": "GraphUpdater not available"}
        
        try:
            # Создаём узел Entity с типом Emergent
            with self.graph_updater.driver.session() as session:
                query = """
                MERGE (c:Entity {name: $name})
                ON CREATE SET
                    c.type = 'Emergent',
                    c.description = $description,
                    c.confidence = $confidence,
                    c.source_url = $source_url,
                    c.created_at = datetime(),
                    c.is_emergent = true
                ON MATCH SET
                    c.description = CASE 
                        WHEN $description IS NOT NULL THEN $description 
                        ELSE c.description 
                    END,
                    c.updated_at = datetime()
                RETURN c
                """
                
                result = session.run(query, {
                    "name": name,
                    "description": description,
                    "confidence": confidence,
                    "source_url": source_url
                })
                
                record = result.single()
                
                if record:
                    # Обновляем кэш
                    embedding = self._get_embedding(f"{name} {description}")
                    if embedding is not None:
                        self.cluster_cache[name] = embedding
                        self.cluster_metadata[name] = {
                            "type": "Emergent",
                            "description": description
                        }
                    
                    logger.info(f"Created emergent concept: {name}")
                    return {
                        "created": True,
                        "name": name,
                        "type": "Emergent"
                    }
                
                return {"created": False, "error": "Failed to create concept"}
        
        except Exception as e:
            logger.error(f"Error creating emergent concept: {e}")
            return {"created": False, "error": str(e)}
    
    async def categorize_and_store(
        self,
        text: str,
        source_url: Optional[str] = None,
        confidence: float = 0.8
    ) -> Dict[str, Any]:
        """
        Категоризировать и сохранить текст в граф
        
        Args:
            text: Текст для категоризации
            source_url: URL источника
            confidence: Уровень уверенности
        
        Returns:
            Информация о действии (создан новый кластер или связан с существующим)
        """
        # Получаем embedding
        embedding = self._get_embedding(text)
        
        # Решаем, создавать ли новый кластер
        should_create, best_cluster, max_similarity = await self.should_create_new_cluster(
            text, embedding
        )
        
        if should_create:
            # Создаём новый emergent концепт
            # Извлекаем название из текста (первые слова)
            name = text[:50].strip()
            if len(text) > 50:
                name += "..."
            
            # Опрашиваем LM Studio для лучшего названия (если доступен)
            if self.lm_client:
                try:
                    prompt = f"""Extract a concise concept name (2-4 words) from this text:
"{text[:200]}"

Respond with only the concept name, no explanations."""
                    
                    result = await self.lm_client.generate(
                        prompt=prompt,
                        temperature=0.3,
                        max_tokens=20
                    )
                    
                    if result.get("text"):
                        name = result["text"].strip().split()[0:4]  # Первые 4 слова
                        name = " ".join(name)
                except Exception as e:
                    logger.warning(f"Could not get concept name from LM Studio: {e}")
            
            # Создаём emergent концепт
            create_result = await self.create_emergent_concept(
                name=name,
                description=text[:500],  # Первые 500 символов
                confidence=confidence,
                source_url=source_url
            )
            
            return {
                "action": "create_new_cluster",
                "cluster_name": name,
                "cluster_type": "Emergent",
                "similarity": max_similarity,
                "result": create_result
            }
        else:
            # Связываем с существующим кластером
            # Создаём факт, связывающий текст с кластером
            fact = {
                "subject": best_cluster,
                "predicate": "RELATED_TO",
                "object": text[:100]  # Первые 100 символов как объект
            }
            
            if self.graph_updater:
                self.graph_updater.add_fact(
                    fact,
                    source=source_url or "",
                    confidence=confidence * max_similarity  # Учитываем схожесть
                )
            
            return {
                "action": "link_to_cluster",
                "cluster_name": best_cluster,
                "similarity": max_similarity,
                "result": {"linked": True}
            }
    
    def apply_growth_rules(self):
        """
        Применить правила роста графа
        
        Правила:
        - Если два узла часто встречаются вместе → добавить связь :RELATED_TO
        - Если ветка быстро растёт → повысить priority
        """
        if not self.graph_updater or not self.graph_updater.driver:
            return
        
        try:
            with self.graph_updater.driver.session() as session:
                # Находим пары узлов, которые часто встречаются вместе
                query = """
                MATCH (a:Entity)-[r1:RELATION]->(b:Entity)
                MATCH (a)-[r2:RELATION]->(c:Entity)
                WHERE b <> c
                WITH a, b, c, count(*) as cooccurrence
                WHERE cooccurrence > 2
                MERGE (b)-[r:RELATED_TO]->(c)
                ON CREATE SET
                    r.cooccurrence = cooccurrence,
                    r.created_at = datetime()
                ON MATCH SET
                    r.cooccurrence = CASE 
                        WHEN cooccurrence > r.cooccurrence THEN cooccurrence 
                        ELSE r.cooccurrence 
                    END,
                    r.updated_at = datetime()
                RETURN count(r) as new_relations
                """
                
                result = session.run(query)
                new_relations = result.single()["new_relations"]
                
                logger.info(f"Applied growth rules: {new_relations} new relations created")
        
        except Exception as e:
            logger.error(f"Error applying growth rules: {e}")
    
    def decay_old_concepts(self):
        """
        Уменьшить вес неиспользуемых концептов
        
        Правило:
        - Если концепт не обновлялся > decay_days дней → уменьшить confidence
        """
        if not self.graph_updater or not self.graph_updater.driver:
            return
        
        try:
            with self.graph_updater.driver.session() as session:
                cutoff_date = datetime.utcnow() - timedelta(days=self.decay_days)
                
                query = """
                MATCH (c:Entity)
                WHERE c.updated_at < $cutoff_date OR c.updated_at IS NULL
                SET c.decay_score = COALESCE(c.decay_score, 1.0) * 0.95,
                    c.last_decay = datetime()
                RETURN count(c) as decayed_concepts
                """
                
                result = session.run(query, cutoff_date=cutoff_date)
                decayed = result.single()["decayed_concepts"]
                
                logger.info(f"Decayed {decayed} old concepts")
        
        except Exception as e:
            logger.error(f"Error decaying old concepts: {e}")


async def example_usage():
    """Пример использования Self-Organizing Graph"""
    from src.integration.lmstudio_client import LMStudioClient
    from installer.app.modules.graph_updater import GraphUpdater
    from sentence_transformers import SentenceTransformer
    
    # Инициализация
    lm_client = LMStudioClient()
    await lm_client.connect()
    
    graph_updater = GraphUpdater()
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    
    sog = SelfOrganizingGraph(
        graph_updater=graph_updater,
        lm_client=lm_client,
        embedder=embedder,
        similarity_threshold=0.65
    )
    
    # Новый факт
    text = "В психологии код-ревью усиливает эмпатию"
    
    # Динамическая категоризация
    result = await sog.categorize_and_store(
        text=text,
        source_url="https://example.com/article",
        confidence=0.8
    )
    
    if result['action'] == 'create_new_cluster':
        print(f"✅ Created new cluster: {result['cluster_name']}")
        print(f"   Type: {result['cluster_type']}")
    else:
        print(f"✅ Linked to existing cluster: {result['cluster_name']}")
        print(f"   Similarity: {result['similarity']:.2f}")
    
    # Применение правил роста
    sog.apply_growth_rules()
    
    # Decay старых концептов
    sog.decay_old_concepts()
    
    await lm_client.close()
    graph_updater.close()













