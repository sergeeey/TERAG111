"""
FastAPI Router для PromptOps
Endpoints для управления промптами
"""
import logging
from fastapi import APIRouter, Query, HTTPException, Body
from typing import Dict, Any, Optional, List
from pydantic import BaseModel

logger = logging.getLogger(__name__)

try:
    from .loader_service import PromptLoaderService
    from .mlflow_registry import PromptRegistryManager
    PROMPTOPS_AVAILABLE = True
except ImportError:
    PROMPTOPS_AVAILABLE = False
    logger.warning("PromptOps components not available")


# Pydantic модели
class PromptLoadRequest(BaseModel):
    name: str
    alias: str = "@latest"
    version: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None


class PromptRegisterRequest(BaseModel):
    name: str
    content: str
    version: str = "1.0.0"
    description: Optional[str] = None
    variables: Optional[List[Dict[str, Any]]] = None
    tags: Optional[List[str]] = None
    aliases: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


# Создаем router
router = APIRouter(prefix="/api/prompts", tags=["prompts"])

# Инициализация сервисов (singleton)
_loader_service: Optional[PromptLoaderService] = None
_registry: Optional[PromptRegistryManager] = None


def get_loader_service() -> PromptLoaderService:
    """Получить экземпляр PromptLoaderService (singleton)"""
    global _loader_service
    if _loader_service is None:
        if not PROMPTOPS_AVAILABLE:
            raise HTTPException(status_code=503, detail="PromptOps not available")
        _loader_service = PromptLoaderService()
    return _loader_service


def get_registry() -> PromptRegistryManager:
    """Получить экземпляр PromptRegistryManager (singleton)"""
    global _registry
    if _registry is None:
        if not PROMPTOPS_AVAILABLE:
            raise HTTPException(status_code=503, detail="PromptOps not available")
        _registry = PromptRegistryManager()
    return _registry


@router.get("/{name}")
def get_prompt(
    name: str,
    alias: str = Query("@latest", description="Alias: @latest, @staging, @production"),
    version: Optional[str] = Query(None, description="Specific version (e.g., 1.0.0)")
) -> Dict[str, Any]:
    """
    Загрузить промпт по имени и алиасу
    
    Args:
        name: Имя промпта
        alias: Алиас (@latest, @staging, @production)
        version: Конкретная версия (опционально)
    
    Returns:
        Промпт с метаданными
    """
    try:
        loader = get_loader_service()
        prompt = loader.load_prompt(name, alias=alias, version=version)
        
        if not prompt:
            raise HTTPException(status_code=404, detail=f"Prompt not found: {name}")
        
        # Получаем метаданные из registry
        registry = get_registry()
        prompt_data = registry.get_prompt(name, alias=alias, version=version)
        
        return {
            "name": name,
            "content": prompt,
            "alias": alias,
            "version": prompt_data.get("version") if prompt_data else None,
            "metadata": prompt_data.get("metadata", {}) if prompt_data else {}
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading prompt {name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/load")
def load_prompt_with_variables(request: PromptLoadRequest) -> Dict[str, Any]:
    """
    Загрузить промпт с подстановкой переменных
    
    Args:
        request: Запрос с именем, алиасом и переменными
    
    Returns:
        Промпт с подставленными переменными
    """
    try:
        loader = get_loader_service()
        prompt = loader.load_prompt_with_variables(
            name=request.name,
            alias=request.alias,
            version=request.version,
            variables=request.variables
        )
        
        if not prompt:
            raise HTTPException(status_code=404, detail=f"Prompt not found: {request.name}")
        
        return {
            "name": request.name,
            "content": prompt,
            "alias": request.alias,
            "variables_used": request.variables or {}
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading prompt with variables: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reload")
def reload_prompt(
    name: str = Body(..., embed=True),
    alias: str = Body("@latest", embed=True)
) -> Dict[str, Any]:
    """
    Перезагрузить промпт (очистить кэш и загрузить заново)
    
    Args:
        name: Имя промпта
        alias: Алиас
    
    Returns:
        Статус перезагрузки
    """
    try:
        loader = get_loader_service()
        success = loader.reload_prompt(name, alias=alias)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Prompt not found: {name}")
        
        return {
            "status": "success",
            "message": f"Prompt {name} reloaded",
            "name": name,
            "alias": alias
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reloading prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/register")
def register_prompt(request: PromptRegisterRequest) -> Dict[str, Any]:
    """
    Зарегистрировать новый промпт в MLflow Registry
    
    Args:
        request: Данные промпта для регистрации
    
    Returns:
        Информация о зарегистрированном промпте
    """
    try:
        registry = get_registry()
        run_id = registry.register_prompt(
            name=request.name,
            content=request.content,
            version=request.version,
            description=request.description,
            variables=request.variables,
            tags=request.tags,
            aliases=request.aliases or ["@latest"],
            metadata=request.metadata
        )
        
        return {
            "status": "success",
            "message": f"Prompt {request.name} registered",
            "name": request.name,
            "version": request.version,
            "run_id": run_id
        }
    
    except Exception as e:
        logger.error(f"Error registering prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
def list_prompts(tags: Optional[List[str]] = Query(None)) -> Dict[str, Any]:
    """
    Получить список всех промптов
    
    Args:
        tags: Фильтр по тегам (опционально)
    
    Returns:
        Список промптов
    """
    try:
        registry = get_registry()
        prompts = registry.list_prompts(tags=tags)
        
        return {
            "total": len(prompts),
            "prompts": prompts
        }
    
    except Exception as e:
        logger.error(f"Error listing prompts: {e}")
        raise HTTPException(status_code=500, detail=str(e))









