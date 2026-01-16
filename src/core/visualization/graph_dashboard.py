"""
Graph Dashboard — визуализация графа знаний и reasoning путей
"""
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    logger.warning("networkx not available, visualization will be limited")

try:
    from pyvis.network import Network
    PYVIS_AVAILABLE = True
except ImportError:
    PYVIS_AVAILABLE = False
    logger.warning("pyvis not available, HTML visualization disabled")

try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    logger.warning("Neo4j not available")


class GraphDashboard:
    """
    Graph Dashboard — создаёт визуализации графа знаний
    
    Функции:
    1. Визуализирует reasoning пути
    2. Создаёт интерактивные HTML-дашборды
    3. Экспортирует граф в различные форматы
    """
    
    def __init__(self, graph_driver=None, output_dir: Optional[Path] = None):
        """
        Инициализация Graph Dashboard
        
        Args:
            graph_driver: Neo4j driver
            output_dir: Папка для сохранения визуализаций
        """
        self.driver = graph_driver
        self.output_dir = output_dir or Path(__file__).parent.parent.parent.parent / "data" / "reports"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("GraphDashboard initialized")
    
    async def visualize_reasoning_paths(
        self,
        reasoning_result: Dict[str, Any],
        filename: Optional[str] = None
    ) -> Path:
        """
        Визуализировать пути рассуждения
        
        Args:
            reasoning_result: Результат рассуждения от KAGSolver
            filename: Имя файла (опционально)
        
        Returns:
            Путь к созданному HTML файлу
        """
        logger.info("Visualizing reasoning paths")
        
        if not PYVIS_AVAILABLE:
            logger.warning("pyvis not available, creating simple HTML")
            return self._create_simple_html(reasoning_result, filename)
        
        try:
            net = Network(height="800px", width="100%", bgcolor="#222222", font_color="white")
            net.set_options("""
            {
                "nodes": {
                    "font": {"size": 14},
                    "scaling": {"min": 10, "max": 30}
                },
                "edges": {
                    "smooth": {"type": "continuous"}
                },
                "physics": {
                    "enabled": true,
                    "stabilization": {"iterations": 100}
                }
            }
            """)
            
            # Добавляем узлы и рёбра из путей
            paths = reasoning_result.get("reasoning_paths", [])
            nodes_added = set()
            
            for path in paths[:20]:  # Ограничиваем для производительности
                nodes = path.get("nodes", [])
                relationships = path.get("relationships", [])
                
                # Добавляем узлы
                for node in nodes:
                    if node not in nodes_added:
                        net.add_node(node, label=node[:30], color="#97c2fc")
                        nodes_added.add(node)
                
                # Добавляем рёбра
                for rel in relationships:
                    start = rel.get("start")
                    end = rel.get("end")
                    rel_type = rel.get("type", "RELATES_TO")
                    
                    if start in nodes_added and end in nodes_added:
                        net.add_edge(start, end, label=rel_type[:20], color="#848484")
            
            # Добавляем вывод (если есть)
            conclusion = reasoning_result.get("conclusion", "")
            if conclusion:
                conclusion_node = "CONCLUSION"
                net.add_node(conclusion_node, label="Вывод", color="#ff6b6b", size=25)
                # Связываем с последними узлами
                if nodes_added:
                    last_nodes = list(nodes_added)[-3:]
                    for node in last_nodes:
                        net.add_edge(node, conclusion_node, color="#ff6b6b", dashes=True)
            
            # Сохраняем
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"reasoning_paths_{timestamp}.html"
            
            output_path = self.output_dir / filename
            net.save_graph(str(output_path))
            
            logger.info(f"Visualization saved to {output_path}")
            
            return output_path
        
        except Exception as e:
            logger.error(f"Error creating visualization: {e}")
            return self._create_simple_html(reasoning_result, filename)
    
    def _create_simple_html(self, reasoning_result: Dict[str, Any], filename: Optional[str] = None) -> Path:
        """Создать простой HTML без pyvis"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reasoning_paths_{timestamp}.html"
        
        output_path = self.output_dir / filename
        
        paths = reasoning_result.get("reasoning_paths", [])
        conclusion = reasoning_result.get("conclusion", "")
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>TERAG Reasoning Paths</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .path {{ background: white; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .conclusion {{ background: #e8f5e9; padding: 15px; margin: 20px 0; border-left: 4px solid #4caf50; }}
        .node {{ display: inline-block; background: #2196f3; color: white; padding: 5px 10px; margin: 2px; border-radius: 3px; }}
        .arrow {{ color: #666; margin: 0 5px; }}
    </style>
</head>
<body>
    <h1>TERAG Reasoning Paths</h1>
    <p><strong>Query:</strong> {reasoning_result.get('query', 'N/A')}</p>
    <p><strong>Confidence:</strong> {reasoning_result.get('confidence', 0.0):.2f}</p>
    
    <h2>Reasoning Paths</h2>
"""
        
        for i, path in enumerate(paths[:10], 1):
            nodes = path.get("nodes", [])
            html += f"""
    <div class="path">
        <h3>Path {i}</h3>
        <p>
            {' <span class="arrow">→</span> '.join(f'<span class="node">{node}</span>' for node in nodes[:10])}
        </p>
    </div>
"""
        
        if conclusion:
            html += f"""
    <div class="conclusion">
        <h2>Conclusion</h2>
        <p>{conclusion}</p>
    </div>
"""
        
        html += """
</body>
</html>
"""
        
        output_path.write_text(html, encoding="utf-8")
        logger.info(f"Simple HTML saved to {output_path}")
        
        return output_path













