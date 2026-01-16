#!/usr/bin/env python3
"""
Тесты для API server.py
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.api.server import app

client = TestClient(app)


class TestRootEndpoint:
    """Тесты для корневого endpoint"""
    
    def test_root_endpoint(self):
        """Тест корневого endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data


class TestMetricsEndpoint:
    """Тесты для /api/metrics"""
    
    @patch('src.api.server.get_metrics_snapshot')
    def test_metrics_endpoint(self, mock_metrics):
        """Тест endpoint метрик"""
        mock_metrics.return_value = {
            "RSS": 0.88,
            "COS": 0.86,
            "FAITH": 0.89
        }
        
        response = client.get("/api/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "RSS" in data
        assert "COS" in data


class TestHealthEndpoint:
    """Тесты для /api/health"""
    
    @patch('src.api.server.get_health')
    def test_health_endpoint(self, mock_health):
        """Тест health endpoint"""
        mock_health.return_value = {"status": "ok"}
        
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data


class TestGraphEndpoint:
    """Тесты для /api/graph"""
    
    @patch('src.api.server.Path')
    def test_graph_endpoint_no_data(self, mock_path):
        """Тест graph endpoint без данных"""
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = False
        mock_path.return_value = mock_path_instance
        
        response = client.get("/api/graph")
        assert response.status_code == 200
        data = response.json()
        assert "graph" in data
        assert "edges" in data


class TestQueryEndpoint:
    """Тесты для /api/query"""
    
    def test_query_endpoint(self):
        """Тест query endpoint"""
        response = client.get("/api/query?question=test")
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data or "error" in data


class TestLanguageEndpoints:
    """Тесты для language endpoints"""
    
    def test_set_language(self):
        """Тест установки языка"""
        response = client.post("/api/set_language", json={"lang": "ru"})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
    
    def test_get_language(self):
        """Тест получения языка"""
        response = client.get("/api/get_language")
        assert response.status_code == 200
        data = response.json()
        assert "language" in data














