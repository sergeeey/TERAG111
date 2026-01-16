"""
Planner Agent — планирование рассуждений
"""
import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    from src.integration.lmstudio_client import LMStudioClient
    LMSTUDIO_AVAILABLE = True
except ImportError:
    LMSTUDIO_AVAILABLE = False
    logger.warning("LMStudioClient not available")


class Planner:
    """
    Planner Agent — планирует стратегию рассуждения
    
    Функции:
    1. Анализирует запрос
    2. Определяет необходимые шаги
    3. Формирует план действий
    """
    
    def __init__(self, lm_client=None):
        """
        Инициализация Planner
        
        Args:
            lm_client: LMStudioClient для планирования
        """
        self.lm_client = lm_client
        logger.info("Planner agent initialized")
    
    async def plan(self, query: str) -> Dict[str, Any]:
        """
        Создать план рассуждения
        
        Args:
            query: Запрос пользователя
        
        Returns:
            План действий
        """
        logger.info(f"Planning for query: {query[:100]}")
        
        plan = {
            "query": query,
            "timestamp": datetime.utcnow().isoformat(),
            "steps": [],
            "estimated_complexity": "medium",
            "required_data": []
        }
        
        if self.lm_client:
            try:
                # Используем LM Studio для планирования
                prompt = f"""Проанализируй следующий запрос и создай план рассуждения.

Запрос: {query}

Верни план в формате:
1. Шаг 1: [описание]
2. Шаг 2: [описание]
...

План:"""
                
                response = await self.lm_client.generate(
                    prompt=prompt,
                    temperature=0.5,
                    max_tokens=200
                )
                
                text = response.get("text", "")
                plan["steps"] = self._parse_steps(text)
                plan["estimated_complexity"] = self._estimate_complexity(query, plan["steps"])
                plan["required_data"] = self._extract_required_data(query)
            
            except Exception as e:
                logger.warning(f"Error in LM planning: {e}, using fallback")
                plan["steps"] = self._fallback_plan(query)
        else:
            plan["steps"] = self._fallback_plan(query)
        
        logger.info(f"Plan created with {len(plan['steps'])} steps")
        
        return plan
    
    def _parse_steps(self, text: str) -> List[str]:
        """Парсить шаги из текста"""
        steps = []
        for line in text.split("\n"):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith("-")):
                # Убираем нумерацию
                step = line.split(":", 1)[-1].strip() if ":" in line else line
                if step:
                    steps.append(step)
        return steps if steps else self._fallback_plan("")
    
    def _fallback_plan(self, query: str) -> List[str]:
        """Резервный план без LM Studio"""
        return [
            "Извлечь релевантные концепты из запроса",
            "Найти связи в графе знаний",
            "Построить причинно-следственные цепочки",
            "Синтезировать вывод",
            "Проверить достоверность"
        ]
    
    def _estimate_complexity(self, query: str, steps: List[str]) -> str:
        """Оценить сложность запроса"""
        query_length = len(query.split())
        steps_count = len(steps)
        
        if query_length > 20 or steps_count > 5:
            return "high"
        elif query_length > 10 or steps_count > 3:
            return "medium"
        else:
            return "low"
    
    def _extract_required_data(self, query: str) -> List[str]:
        """Извлечь требуемые типы данных"""
        required = []
        
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["факт", "fact", "данные", "data"]):
            required.append("facts")
        
        if any(word in query_lower for word in ["связь", "relation", "связи", "connections"]):
            required.append("relations")
        
        if any(word in query_lower for word in ["причина", "cause", "следствие", "effect"]):
            required.append("causal_chains")
        
        if any(word in query_lower for word in ["практика", "practice", "лучший", "best"]):
            required.append("best_practices")
        
        return required if required else ["general_knowledge"]













