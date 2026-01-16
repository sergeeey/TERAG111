"""
Streamlit Demo Web Interface для TERAG
Простой веб-интерфейс для демонстрации Auto Linker и Fraud Detection
"""

import streamlit as st
import requests
import json
from typing import List, Dict, Any
from datetime import datetime

# Конфигурация страницы
st.set_page_config(
    page_title="TERAG Demo",
    page_icon="🧠",
    layout="wide"
)

# API URL (можно настроить через .env или переменные окружения)
import os
API_URL = os.getenv("TERAG_API_URL", st.secrets.get("TERAG_API_URL", "http://localhost:8001") if hasattr(st, 'secrets') else "http://localhost:8001")

# Заголовок
st.title("🧠 TERAG - Traceable Reasoning Architecture Graph")
st.markdown("**Demo версия для демонстрации возможностей**")

# Sidebar для настройки
st.sidebar.header("⚙️ Настройки")
api_key = st.sidebar.text_input("API Key", type="password", help="Введите ваш TERAG API key")
demo_mode = st.sidebar.checkbox("Demo Mode (без API)", value=False)

# Основные вкладки
tab1, tab2, tab3 = st.tabs(["🔗 Auto Linker", "🚨 Fraud Detection", "📊 About"])

# ========== TAB 1: Auto Linker ==========
with tab1:
    st.header("Auto Linker - Автоматическое связывание клиентов")
    st.markdown("Найдите похожих клиентов по ФИО и телефону")
    
    # Пример данных
    st.subheader("📝 Введите данные клиентов")
    
    # Загрузка из файла или ручной ввод
    upload_option = st.radio(
        "Выберите способ ввода:",
        ["📤 Загрузить JSON файл", "✍️ Ручной ввод"]
    )
    
    clients_data = []
    
    if upload_option == "📤 Загрузить JSON файл":
        uploaded_file = st.file_uploader("Выберите JSON файл", type=["json"])
        if uploaded_file:
            try:
                clients_data = json.load(uploaded_file)
                st.success(f"✅ Загружено {len(clients_data)} клиентов")
            except Exception as e:
                st.error(f"❌ Ошибка загрузки файла: {e}")
    else:
        # Ручной ввод через форму
        num_clients = st.number_input("Количество клиентов", min_value=2, max_value=10, value=2)
        
        for i in range(num_clients):
            with st.expander(f"Клиент {i+1}"):
                client_id = st.text_input(f"ID клиента {i+1}", value=f"CLIENT-{i+1:03d}", key=f"id_{i}")
                full_name = st.text_input(f"ФИО клиента {i+1}", value="", key=f"name_{i}")
                phone = st.text_input(f"Телефон клиента {i+1}", value="", key=f"phone_{i}")
                
                if client_id and full_name:
                    clients_data.append({
                        "id": client_id,
                        "full_name": full_name,
                        "phone": phone if phone else None
                    })
    
    # Кнопка запуска
    if st.button("🔍 Найти похожих клиентов", disabled=len(clients_data) < 2):
        if demo_mode:
            # Demo режим - показываем пример результата
            st.info("🎭 Demo Mode: Показываем пример результата")
            demo_result = {
                "status": "success",
                "total_clients": len(clients_data),
                "linked_pairs": [
                    {
                        "client1_id": clients_data[0]["id"],
                        "client2_id": clients_data[1]["id"] if len(clients_data) > 1 else clients_data[0]["id"],
                        "confidence": 0.92,
                        "match_reason": "fio"
                    }
                ] if len(clients_data) >= 2 else [],
                "total_links": 1 if len(clients_data) >= 2 else 0
            }
            st.json(demo_result)
        else:
            # Реальный API запрос
            if not api_key:
                st.error("❌ Введите API Key в настройках")
            else:
                try:
                    with st.spinner("⏳ Обработка запроса..."):
                        response = requests.post(
                            f"{API_URL}/api/v2/auto-link",
                            json={
                                "clients": clients_data,
                                "min_confidence": 0.85,
                                "create_links": False
                            },
                            headers={"Authorization": f"Bearer {api_key}"},
                            timeout=30
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.success(f"✅ Найдено {result['total_links']} связей")
                            st.json(result)
                        else:
                            st.error(f"❌ Ошибка API: {response.status_code} - {response.text}")
                except Exception as e:
                    st.error(f"❌ Ошибка запроса: {e}")

# ========== TAB 2: Fraud Detection ==========
with tab2:
    st.header("Fraud Detection - Детекция мошенничества")
    st.markdown("Обнаружение подозрительных паттернов по правилам")
    
    days = st.slider("Период анализа (дни)", min_value=1, max_value=90, value=30)
    
    if st.button("🚨 Запустить детекцию мошенничества"):
        if demo_mode:
            # Demo режим
            st.info("🎭 Demo Mode: Показываем пример результата")
            demo_result = {
                "status": "success",
                "analysis_date": datetime.now().isoformat(),
                "time_window_days": days,
                "total_alerts": 2,
                "alerts": [
                    {
                        "type": "fraud_ring",
                        "ring_id": "RING-001",
                        "member_count": 5,
                        "risk_level": "critical"
                    },
                    {
                        "type": "high_link_count",
                        "client_id": "CLIENT-001",
                        "link_count": 8,
                        "risk_level": "high"
                    }
                ],
                "summary": {
                    "total_alerts": 2,
                    "by_type": {"fraud_ring": 1, "high_link_count": 1},
                    "by_risk_level": {"critical": 1, "high": 1, "medium": 0}
                }
            }
            st.json(demo_result)
        else:
            # Реальный API запрос
            if not api_key:
                st.error("❌ Введите API Key в настройках")
            else:
                try:
                    with st.spinner("⏳ Анализ данных..."):
                        response = requests.get(
                            f"{API_URL}/api/v2/fraud-detection",
                            params={"days": days},
                            headers={"Authorization": f"Bearer {api_key}"},
                            timeout=60
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.success(f"✅ Обнаружено {result['total_alerts']} подозрительных паттернов")
                            
                            # Показываем сводку
                            st.subheader("📊 Сводка")
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Всего алертов", result['total_alerts'])
                            with col2:
                                st.metric("Critical", result['summary']['by_risk_level'].get('critical', 0))
                            with col3:
                                st.metric("High", result['summary']['by_risk_level'].get('high', 0))
                            
                            # Показываем детали
                            st.subheader("🔍 Детали алертов")
                            st.json(result)
                        else:
                            st.error(f"❌ Ошибка API: {response.status_code} - {response.text}")
                except Exception as e:
                    st.error(f"❌ Ошибка запроса: {e}")

# ========== TAB 3: About ==========
with tab3:
    st.header("📊 О TERAG")
    st.markdown("""
    ### TERAG - Traceable Reasoning Architecture Graph
    
    **TERAG** - это когнитивная инфраструктура на основе Graph-RAG для:
    - 🔗 Автоматического связывания связанных сущностей
    - 🚨 Детекции мошеннических паттернов
    - 🧠 Графового рассуждения на основе знаний
    
    ### Возможности Demo версии:
    
    1. **Auto Linker**: Находит похожих клиентов по ФИО и телефону
    2. **Fraud Detection**: Обнаруживает подозрительные паттерны по 3 правилам:
       - Высокое количество связей
       - Fraud rings (группы связанных клиентов)
       - Общий телефон у многих клиентов
    
    ### Как использовать:
    
    1. Получите API Key через `terag-cli keys create`
    2. Введите API Key в настройках (sidebar)
    3. Используйте вкладки для тестирования функций
    
    ### Demo Mode:
    
    Включите "Demo Mode" в настройках для просмотра примеров результатов без подключения к API.
    
    ---
    
    **Версия:** 2.0.0  
    **Статус:** Demo / MVP
    """)
