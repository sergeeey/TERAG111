#!/usr/bin/env python3
"""
TERAG Mission Runner
Точка входа для запуска OSINT-миссий TERAG

Usage:
    python start_mission.py --config ./data/mission.yaml
    python start_mission.py --config ./data/mission.yaml --install-path E:\TERAG
"""

import argparse
import sys
import os
import logging
from pathlib import Path

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent / "app"))

from modules.mission_runner import MissionRunner
from modules.signal_mission_runner import SignalMissionRunner

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('mission_runner.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Основная функция запуска миссии"""
    parser = argparse.ArgumentParser(
        description="TERAG Cognitive OSINT Mission Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python start_mission.py --config ./data/mission.yaml
  python start_mission.py --config ./data/mission.yaml --install-path E:\\TERAG
  python start_mission.py --config ./data/mission.yaml --dry-run
        """
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='./data/mission.yaml',
        help='Path to mission configuration file (default: ./data/mission.yaml)'
    )
    
    parser.add_argument(
        '--install-path',
        type=str,
        default=None,
        help='TERAG installation path (default: from TERAG_INSTALL_PATH env or E:\\TERAG)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Dry run mode: validate config without executing mission'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Проверка существования конфигурации
    config_path = Path(args.config)
    if not config_path.exists():
        logger.error(f"Mission config not found: {config_path}")
        logger.error("Please create mission.yaml or specify correct path with --config")
        sys.exit(1)
    
    if args.dry_run:
        logger.info("=" * 60)
        logger.info("DRY RUN MODE - Validating configuration only")
        logger.info("=" * 60)
        
        try:
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            mission_name = config.get('mission', {}).get('name', 'Unknown')
            logger.info(f"✓ Mission config valid: {mission_name}")
            logger.info(f"✓ Components: {', '.join(config.get('mission', {}).get('components', []))}")
            logger.info("=" * 60)
            logger.info("Configuration is valid. Ready to run mission.")
            sys.exit(0)
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            sys.exit(1)
    
    # Запуск миссии
    logger.info("=" * 60)
    logger.info("TERAG Cognitive OSINT Mission Runner")
    logger.info("=" * 60)
    logger.info(f"Config: {config_path}")
    logger.info(f"Install path: {args.install_path or os.getenv('TERAG_INSTALL_PATH', 'E:\\TERAG')}")
    logger.info("=" * 60)
    
    try:
        # Загрузить конфигурацию для определения типа миссии
        import yaml
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        mission_type = config.get('mission', {}).get('type', 'standard')
        
        # Выбор runner в зависимости от типа миссии
        if mission_type == 'signals':
            logger.info("Running Signal Discovery Mission...")
            runner = SignalMissionRunner(
                mission_config_path=str(config_path),
                install_path=args.install_path
            )
        else:
            logger.info("Running Standard Mission...")
            runner = MissionRunner(
                mission_config_path=str(config_path),
                install_path=args.install_path
            )
        
        results = runner.run_mission()
        
        # Вывод итогов
        logger.info("")
        logger.info("=" * 60)
        logger.info("MISSION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Status: {results.get('status', 'unknown')}")
        logger.info(f"Started: {results.get('started_at', 'N/A')}")
        logger.info(f"Completed: {results.get('completed_at', 'N/A')}")
        
        if results.get('status') == 'completed':
            logger.info("")
            logger.info("Components executed:")
            for component_name, component_data in results.get('components', {}).items():
                status = "✓" if not component_data.get('error') else "✗"
                logger.info(f"  {status} {component_name}")
            
            logger.info("")
            logger.info("Output files:")
            logger.info(f"  - Daily report: {Path(runner.data_path) / 'daily_summary.md'}")
            logger.info(f"  - Graph snapshot: {Path(runner.data_path) / 'graph_snapshot.json'}")
            logger.info(f"  - Mission log: {Path(runner.data_path) / 'mission_log.jsonl'}")
        
        if results.get('error'):
            logger.error(f"Error: {results.get('error')}")
            sys.exit(1)
        
        logger.info("=" * 60)
        logger.info("Mission completed successfully!")
        logger.info("=" * 60)
        
    except KeyboardInterrupt:
        logger.warning("Mission interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Mission failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

