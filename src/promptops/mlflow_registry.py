"""
MLflow Prompt Registry для TERAG
Единый источник правды для всех промптов системы
"""
import logging
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    import mlflow
    from mlflow.tracking import MlflowClient
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False
    logger.warning("MLflow not available")


class PromptRegistryManager:
    """
    Менеджер реестра промптов в MLflow
    
    Функции:
    1. Регистрация промптов с версионированием
    2. Извлечение промптов по алиасам (@latest, @staging, @production)
    3. Управление версиями через MLflow Model Registry
    4. Валидация промптов по схеме
    """
    
    def __init__(
        self,
        experiment_name: str = "TERAG_Prompts",
        registry_name: str = "TERAG_Prompt_Registry"
    ):
        """
        Инициализация Prompt Registry Manager
        
        Args:
            experiment_name: Имя эксперимента MLflow
            registry_name: Имя реестра моделей
        """
        if not MLFLOW_AVAILABLE:
            raise ImportError("MLflow not installed. Install with: pip install mlflow")
        
        self.experiment_name = experiment_name
        self.registry_name = registry_name
        self.client = MlflowClient()
        
        # Создаем эксперимент если не существует
        try:
            mlflow.set_experiment(experiment_name)
        except Exception as e:
            logger.warning(f"Could not set experiment: {e}")
        
        # Загружаем схему валидации
        schema_path = Path(__file__).parent.parent.parent / "configs" / "prompts" / "registry_schema.json"
        self.schema = self._load_schema(schema_path)
        
        logger.info(f"PromptRegistryManager initialized: {experiment_name}")
    
    def _load_schema(self, schema_path: Path) -> Optional[Dict[str, Any]]:
        """Загрузить JSON схему для валидации"""
        if schema_path.exists():
            try:
                with open(schema_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load schema: {e}")
        return None
    
    def _validate_prompt(self, prompt_data: Dict[str, Any]) -> bool:
        """
        Валидировать промпт по схеме
        
        Args:
            prompt_data: Данные промпта
        
        Returns:
            True если валиден
        """
        if not self.schema:
            logger.warning("Schema not loaded, skipping validation")
            return True
        
        # Простая валидация (в production используйте jsonschema)
        required_fields = self.schema.get("required", [])
        for field in required_fields:
            if field not in prompt_data:
                logger.error(f"Missing required field: {field}")
                return False
        
        return True
    
    def register_prompt(
        self,
        name: str,
        content: str,
        version: str = "1.0.0",
        description: Optional[str] = None,
        variables: Optional[List[Dict[str, Any]]] = None,
        tags: Optional[List[str]] = None,
        aliases: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Зарегистрировать промпт в MLflow
        
        Args:
            name: Имя промпта
            content: Содержимое промпта
            version: Версия (семантическое версионирование)
            description: Описание
            variables: Список переменных
            tags: Теги
            aliases: Алиасы (@latest, @staging, @production)
            metadata: Дополнительные метаданные
        
        Returns:
            Run ID промпта
        """
        logger.info(f"Registering prompt: {name} v{version}")
        
        # Формируем данные промпта
        prompt_data = {
            "name": name,
            "content": content,
            "version": version,
            "description": description or f"Prompt {name}",
            "variables": variables or [],
            "tags": tags or [],
            "aliases": aliases or ["@latest"],
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Валидация
        if not self._validate_prompt(prompt_data):
            raise ValueError(f"Invalid prompt data for {name}")
        
        # Регистрируем в MLflow
        with mlflow.start_run(run_name=f"{name}_v{version}"):
            # Логируем как параметры
            mlflow.log_param("prompt_name", name)
            mlflow.log_param("prompt_version", version)
            mlflow.log_param("prompt_description", prompt_data["description"])
            
            # Логируем как артефакт
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(prompt_data, f, indent=2, ensure_ascii=False)
                mlflow.log_artifact(f.name, artifact_path="prompt")
                os.unlink(f.name)
            
            # Логируем содержимое промпта
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(content)
                mlflow.log_artifact(f.name, artifact_path="prompt")
                os.unlink(f.name)
            
            run_id = mlflow.active_run().info.run_id
        
        logger.info(f"Prompt registered: {name} v{version} (run_id: {run_id})")
        
        return run_id
    
    def get_prompt(
        self,
        name: str,
        alias: str = "@latest",
        version: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Получить промпт по имени и алиасу
        
        Args:
            name: Имя промпта
            alias: Алиас (@latest, @staging, @production)
            version: Конкретная версия (опционально)
        
        Returns:
            Данные промпта или None
        """
        logger.info(f"Getting prompt: {name} (alias: {alias}, version: {version})")
        
        try:
            # Ищем в экспериментах
            experiment = mlflow.get_experiment_by_name(self.experiment_name)
            if not experiment:
                logger.warning(f"Experiment {self.experiment_name} not found")
                return None
            
            # Получаем все runs для этого промпта
            runs = mlflow.search_runs(
                experiment_ids=[experiment.experiment_id],
                filter_string=f"params.prompt_name = '{name}'",
                order_by=["start_time DESC"]
            )
            
            if runs.empty:
                logger.warning(f"No runs found for prompt: {name}")
                return None
            
            # Выбираем run по алиасу или версии
            selected_run = None
            
            if version:
                # Ищем конкретную версию
                version_runs = runs[runs["params.prompt_version"] == version]
                if not version_runs.empty:
                    selected_run = version_runs.iloc[0]
            else:
                # Используем алиас
                if alias == "@latest":
                    selected_run = runs.iloc[0]  # Последний
                elif alias == "@staging":
                    # Ищем с тегом staging
                    staging_runs = runs[runs["tags.mlflow.runName"].str.contains("staging", case=False, na=False)]
                    if not staging_runs.empty:
                        selected_run = staging_runs.iloc[0]
                elif alias == "@production":
                    # Ищем с тегом production
                    prod_runs = runs[runs["tags.mlflow.runName"].str.contains("production", case=False, na=False)]
                    if not prod_runs.empty:
                        selected_run = prod_runs.iloc[0]
            
            if selected_run is None:
                logger.warning(f"No run found for {name} with alias {alias}")
                return None
            
            # Загружаем артефакт
            run_id = selected_run["run_id"]
            artifact_path = f"prompt/{name}_v{selected_run['params.prompt_version']}.json"
            
            try:
                # Загружаем через MLflow client
                local_path = mlflow.artifacts.download_artifacts(
                    run_id=run_id,
                    artifact_path="prompt"
                )
                
                # Ищем JSON файл
                prompt_file = Path(local_path) / f"{name}_v{selected_run['params.prompt_version']}.json"
                if not prompt_file.exists():
                    # Пробуем найти любой JSON
                    json_files = list(Path(local_path).glob("*.json"))
                    if json_files:
                        prompt_file = json_files[0]
                    else:
                        logger.error(f"Prompt JSON not found in artifacts for {run_id}")
                        return None
                
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    prompt_data = json.load(f)
                
                logger.info(f"Prompt loaded: {name} v{prompt_data.get('version')}")
                return prompt_data
                
            except Exception as e:
                logger.error(f"Error loading prompt artifact: {e}")
                return None
        
        except Exception as e:
            logger.error(f"Error getting prompt: {e}")
            return None
    
    def list_prompts(self, tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Получить список всех промптов
        
        Args:
            tags: Фильтр по тегам (опционально)
        
        Returns:
            Список промптов
        """
        logger.info("Listing all prompts")
        
        try:
            experiment = mlflow.get_experiment_by_name(self.experiment_name)
            if not experiment:
                return []
            
            # Получаем все runs
            filter_string = None
            if tags:
                # Фильтр по тегам (упрощенная версия)
                pass
            
            runs = mlflow.search_runs(
                experiment_ids=[experiment.experiment_id],
                filter_string=filter_string,
                order_by=["start_time DESC"]
            )
            
            # Группируем по имени промпта
            prompts = {}
            for _, run in runs.iterrows():
                name = run.get("params.prompt_name", "unknown")
                if name not in prompts:
                    prompts[name] = {
                        "name": name,
                        "versions": [],
                        "latest_version": None
                    }
                
                version = run.get("params.prompt_version", "unknown")
                prompts[name]["versions"].append(version)
                
                if not prompts[name]["latest_version"]:
                    prompts[name]["latest_version"] = version
            
            return list(prompts.values())
        
        except Exception as e:
            logger.error(f"Error listing prompts: {e}")
            return []









