#!/usr/bin/env python3
"""
Нагрузочное тестирование SSE endpoints для TERAG
Измеряет производительность и стабильность потоковой передачи
"""
import asyncio
import aiohttp
import argparse
import json
import time
import statistics
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict


@dataclass
class LoadTestConfig:
    """Конфигурация нагрузочного теста"""
    endpoint: str = "http://localhost:8000/api/stream/reasoning"
    concurrent_connections: int = 10
    duration_seconds: int = 60
    query: str = "What is Graph-RAG?"
    show: Optional[List[str]] = None
    thread_id_prefix: str = "load_test"
    timeout: int = 30


@dataclass
class ConnectionMetrics:
    """Метрики одного подключения"""
    connection_id: str
    success: bool
    events_received: int
    first_event_latency_ms: float
    total_duration_ms: float
    error_message: Optional[str] = None


@dataclass
class LoadTestResults:
    """Результаты нагрузочного теста"""
    config: Dict[str, Any]
    total_connections: int
    successful_connections: int
    failed_connections: int
    total_events: int
    avg_events_per_connection: float
    avg_first_event_latency_ms: float
    median_first_event_latency_ms: float
    p95_first_event_latency_ms: float
    avg_duration_ms: float
    error_rate: float
    throughput_events_per_second: float
    timestamp: str


class SSELoadTester:
    """Класс для нагрузочного тестирования SSE"""
    
    def __init__(self, config: LoadTestConfig):
        self.config = config
        self.metrics: List[ConnectionMetrics] = []
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
    
    async def connect_and_stream(
        self,
        session: aiohttp.ClientSession,
        connection_id: str
    ) -> ConnectionMetrics:
        """Подключиться к SSE endpoint и собрать метрики"""
        metrics = ConnectionMetrics(
            connection_id=connection_id,
            success=False,
            events_received=0,
            first_event_latency_ms=0.0,
            total_duration_ms=0.0
        )
        
        start_time = time.time()
        first_event_time: Optional[float] = None
        
        try:
            # Формируем URL с параметрами
            params = {"query": self.config.query}
            if self.config.show:
                params["show"] = ",".join(self.config.show)
            if self.config.thread_id_prefix:
                params["thread_id"] = f"{self.config.thread_id_prefix}_{connection_id}"
            
            # Подключаемся к SSE endpoint
            async with session.get(
                self.config.endpoint,
                params=params,
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            ) as response:
                if response.status != 200:
                    metrics.error_message = f"HTTP {response.status}"
                    metrics.total_duration_ms = (time.time() - start_time) * 1000
                    return metrics
                
                # Читаем SSE события
                async for line in response.content:
                    if first_event_time is None:
                        first_event_time = time.time()
                        metrics.first_event_latency_ms = (first_event_time - start_time) * 1000
                    
                    line_str = line.decode('utf-8').strip()
                    
                    # Проверяем что это SSE событие
                    if line_str.startswith('data:'):
                        metrics.events_received += 1
                        
                        # Парсим JSON если возможно
                        try:
                            data_str = line_str[5:].strip()  # Убираем 'data:'
                            if data_str:
                                event_data = json.loads(data_str)
                                # Проверяем завершение потока
                                if event_data.get('type') == 'done':
                                    break
                        except json.JSONDecodeError:
                            pass
                    
                    # Проверяем таймаут
                    if time.time() - start_time > self.config.duration_seconds:
                        break
            
            metrics.success = True
            metrics.total_duration_ms = (time.time() - start_time) * 1000
            
        except asyncio.TimeoutError:
            metrics.error_message = "Timeout"
            metrics.total_duration_ms = (time.time() - start_time) * 1000
        except aiohttp.ClientError as e:
            metrics.error_message = str(e)
            metrics.total_duration_ms = (time.time() - start_time) * 1000
        except Exception as e:
            metrics.error_message = f"Unexpected error: {str(e)}"
            metrics.total_duration_ms = (time.time() - start_time) * 1000
        
        return metrics
    
    async def run_load_test(self) -> LoadTestResults:
        """Запустить нагрузочный тест"""
        print(f"🚀 Starting load test...")
        print(f"   Endpoint: {self.config.endpoint}")
        print(f"   Concurrent connections: {self.config.concurrent_connections}")
        print(f"   Duration: {self.config.duration_seconds}s")
        print(f"   Query: {self.config.query}")
        
        self.start_time = time.time()
        
        # Создаем HTTP сессию
        connector = aiohttp.TCPConnector(limit=self.config.concurrent_connections * 2)
        async with aiohttp.ClientSession(connector=connector) as session:
            # Создаем задачи для параллельных подключений
            tasks = [
                self.connect_and_stream(session, str(i))
                for i in range(self.config.concurrent_connections)
            ]
            
            # Запускаем все подключения параллельно
            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Обрабатываем результаты
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.metrics.append(ConnectionMetrics(
                    connection_id=str(i),
                    success=False,
                    events_received=0,
                    first_event_latency_ms=0.0,
                    total_duration_ms=0.0,
                    error_message=str(result)
                ))
            else:
                self.metrics.append(result)
        
        self.end_time = time.time()
        
        # Вычисляем агрегированные метрики
        return self._calculate_results()
    
    def _calculate_results(self) -> LoadTestResults:
        """Вычислить агрегированные метрики"""
        total_connections = len(self.metrics)
        successful = [m for m in self.metrics if m.success]
        failed = [m for m in self.metrics if not m.success]
        
        successful_connections = len(successful)
        failed_connections = len(failed)
        
        total_events = sum(m.events_received for m in self.metrics)
        avg_events = total_events / total_connections if total_connections > 0 else 0
        
        # Latency метрики (только для успешных)
        latencies = [m.first_event_latency_ms for m in successful if m.first_event_latency_ms > 0]
        avg_latency = statistics.mean(latencies) if latencies else 0.0
        median_latency = statistics.median(latencies) if latencies else 0.0
        p95_latency = self._percentile(latencies, 95) if latencies else 0.0
        
        # Duration метрики
        durations = [m.total_duration_ms for m in self.metrics]
        avg_duration = statistics.mean(durations) if durations else 0.0
        
        # Error rate
        error_rate = (failed_connections / total_connections * 100) if total_connections > 0 else 0.0
        
        # Throughput
        test_duration = (self.end_time - self.start_time) if self.end_time and self.start_time else 1.0
        throughput = total_events / test_duration if test_duration > 0 else 0.0
        
        return LoadTestResults(
            config=asdict(self.config),
            total_connections=total_connections,
            successful_connections=successful_connections,
            failed_connections=failed_connections,
            total_events=total_events,
            avg_events_per_connection=avg_events,
            avg_first_event_latency_ms=avg_latency,
            median_first_event_latency_ms=median_latency,
            p95_first_event_latency_ms=p95_latency,
            avg_duration_ms=avg_duration,
            error_rate=error_rate,
            throughput_events_per_second=throughput,
            timestamp=datetime.utcnow().isoformat()
        )
    
    @staticmethod
    def _percentile(data: List[float], percentile: int) -> float:
        """Вычислить перцентиль"""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def print_results(self, results: LoadTestResults):
        """Вывести результаты в консоль"""
        print("\n" + "="*60)
        print("📊 Load Test Results")
        print("="*60)
        print(f"\n✅ Successful connections: {results.successful_connections}/{results.total_connections}")
        print(f"❌ Failed connections: {results.failed_connections}")
        print(f"📈 Total events received: {results.total_events}")
        print(f"📊 Avg events per connection: {results.avg_events_per_connection:.2f}")
        print(f"\n⏱️  Latency Metrics:")
        print(f"   Average: {results.avg_first_event_latency_ms:.2f} ms")
        print(f"   Median: {results.median_first_event_latency_ms:.2f} ms")
        print(f"   95th percentile: {results.p95_first_event_latency_ms:.2f} ms")
        print(f"\n⏳ Duration:")
        print(f"   Average: {results.avg_duration_ms:.2f} ms")
        print(f"\n📉 Error Rate: {results.error_rate:.2f}%")
        print(f"🚀 Throughput: {results.throughput_events_per_second:.2f} events/sec")
        print("\n" + "="*60)
        
        # Детали по ошибкам
        if results.failed_connections > 0:
            print("\n❌ Failed Connections Details:")
            for metric in self.metrics:
                if not metric.success:
                    print(f"   Connection {metric.connection_id}: {metric.error_message}")
    
    def save_results(self, results: LoadTestResults, output_dir: Path):
        """Сохранить результаты в JSON файл"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"load_test_results_{timestamp}.json"
        
        # Подготавливаем данные для сохранения
        output_data = {
            "results": asdict(results),
            "individual_metrics": [asdict(m) for m in self.metrics]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Results saved to: {output_file}")
        return output_file


async def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(description="SSE Load Test for TERAG")
    parser.add_argument(
        "--endpoint",
        default="http://localhost:8000/api/stream/reasoning",
        help="SSE endpoint URL"
    )
    parser.add_argument(
        "--connections",
        type=int,
        default=10,
        help="Number of concurrent connections"
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=60,
        help="Test duration in seconds"
    )
    parser.add_argument(
        "--query",
        default="What is Graph-RAG?",
        help="Query to test"
    )
    parser.add_argument(
        "--show",
        nargs="+",
        help="Node types to show (e.g., planner solver)"
    )
    parser.add_argument(
        "--output-dir",
        default="docs/load_test_results",
        help="Output directory for results"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Connection timeout in seconds"
    )
    
    args = parser.parse_args()
    
    # Создаем конфигурацию
    config = LoadTestConfig(
        endpoint=args.endpoint,
        concurrent_connections=args.connections,
        duration_seconds=args.duration,
        query=args.query,
        show=args.show,
        timeout=args.timeout
    )
    
    # Запускаем тест
    tester = SSELoadTester(config)
    results = await tester.run_load_test()
    
    # Выводим результаты
    tester.print_results(results)
    
    # Сохраняем результаты
    output_dir = Path(args.output_dir)
    tester.save_results(results, output_dir)
    
    # Возвращаем код выхода
    if results.error_rate > 10:  # Более 10% ошибок
        print("\n⚠️  Warning: High error rate detected!")
        return 1
    elif results.avg_first_event_latency_ms > 1000:  # Более 1 секунды
        print("\n⚠️  Warning: High latency detected!")
        return 1
    else:
        print("\n✅ Load test completed successfully!")
        return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)







