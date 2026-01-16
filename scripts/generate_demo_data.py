#!/usr/bin/env python3
"""
Генерация demo данных для TERAG
Создает примеры клиентов и транзакций для демонстрации
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path

# Список русских имен для генерации
FIRST_NAMES = ["Иван", "Петр", "Сергей", "Александр", "Дмитрий", "Андрей", "Михаил", "Алексей"]
LAST_NAMES = ["Иванов", "Петров", "Сидоров", "Смирнов", "Кузнецов", "Попов", "Соколов", "Лебедев"]
MIDDLE_NAMES = ["Иванович", "Петрович", "Сергеевич", "Александрович", "Дмитриевич"]

# Телефоны для генерации
PHONE_PREFIXES = ["+7700", "+7701", "+7702", "+7705", "+7707", "+7708"]


def generate_client_id(index: int) -> str:
    """Генерировать ID клиента"""
    return f"CLIENT-{index:03d}"


def generate_full_name() -> str:
    """Генерировать случайное ФИО"""
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    middle = random.choice(MIDDLE_NAMES)
    return f"{last} {first} {middle}"


def generate_phone() -> str:
    """Генерировать случайный телефон"""
    prefix = random.choice(PHONE_PREFIXES)
    number = ''.join([str(random.randint(0, 9)) for _ in range(7)])
    return f"{prefix}{number}"


def generate_clients(count: int = 20, with_duplicates: bool = True) -> list:
    """
    Генерировать список клиентов
    
    Args:
        count: Количество клиентов
        with_duplicates: Создать несколько похожих клиентов для тестирования Auto Linker
    
    Returns:
        Список клиентов
    """
    clients = []
    
    for i in range(count):
        client = {
            "id": generate_client_id(i + 1),
            "full_name": generate_full_name(),
            "phone": generate_phone()
        }
        clients.append(client)
    
    # Добавляем несколько похожих клиентов для тестирования
    if with_duplicates:
        # Копируем несколько клиентов с небольшими изменениями
        base_clients = clients[:5]
        for base_client in base_clients:
            # Вариант 1: Точно такой же
            duplicate = {
                "id": generate_client_id(len(clients) + 1),
                "full_name": base_client["full_name"],  # Точно такой же
                "phone": base_client["phone"]  # Точно такой же
            }
            clients.append(duplicate)
            
            # Вариант 2: Похожий ФИО, другой телефон
            similar = {
                "id": generate_client_id(len(clients) + 1),
                "full_name": base_client["full_name"].replace("Иван", "И."),  # Сокращение
                "phone": generate_phone()  # Другой телефон
            }
            clients.append(similar)
    
    return clients


def generate_transactions(clients: list, count: int = 50) -> list:
    """
    Генерировать список транзакций
    
    Args:
        clients: Список клиентов
        count: Количество транзакций
    
    Returns:
        Список транзакций
    """
    transactions = []
    start_date = datetime.now() - timedelta(days=30)
    
    for i in range(count):
        client = random.choice(clients)
        transaction_date = start_date + timedelta(
            days=random.randint(0, 30),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        transaction = {
            "id": f"TXN-{i+1:05d}",
            "client_id": client["id"],
            "client_name": client["full_name"],
            "amount": round(random.uniform(1000, 100000), 2),
            "currency": "KZT",
            "transaction_date": transaction_date.isoformat(),
            "type": random.choice(["loan", "repayment", "transfer"]),
            "status": random.choice(["completed", "pending", "failed"])
        }
        transactions.append(transaction)
    
    return transactions


def main():
    """Основная функция"""
    output_dir = Path("data/demo")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("🎯 Генерация demo данных для TERAG...")
    
    # Генерируем клиентов
    print("📝 Генерация клиентов...")
    clients = generate_clients(count=20, with_duplicates=True)
    clients_file = output_dir / "mfo_clients_sample.json"
    with open(clients_file, "w", encoding="utf-8") as f:
        json.dump(clients, f, ensure_ascii=False, indent=2)
    print(f"✅ Создано {len(clients)} клиентов: {clients_file}")
    
    # Генерируем транзакции
    print("💳 Генерация транзакций...")
    transactions = generate_transactions(clients, count=50)
    transactions_file = output_dir / "transactions_sample.json"
    with open(transactions_file, "w", encoding="utf-8") as f:
        json.dump(transactions, f, ensure_ascii=False, indent=2)
    print(f"✅ Создано {len(transactions)} транзакций: {transactions_file}")
    
    # Создаем README
    readme_file = output_dir / "README.md"
    with open(readme_file, "w", encoding="utf-8") as f:
        f.write("""# TERAG Demo Data

Этот каталог содержит demo данные для тестирования TERAG.

## Файлы:

- `mfo_clients_sample.json` - Примеры клиентов MFO (20 клиентов, включая похожих для тестирования Auto Linker)
- `transactions_sample.json` - Примеры транзакций (50 транзакций за последние 30 дней)

## Использование:

1. **Auto Linker Demo**: Загрузите `mfo_clients_sample.json` в Streamlit app для тестирования связывания клиентов
2. **Fraud Detection Demo**: Используйте транзакции для тестирования детекции мошенничества

## Генерация новых данных:

```bash
python scripts/generate_demo_data.py
```

Это создаст новые случайные данные в `data/demo/`.
""")
    print(f"✅ Создан README: {readme_file}")
    
    print("\n🎉 Demo данные успешно созданы!")
    print(f"📁 Расположение: {output_dir.absolute()}")

if __name__ == "__main__":
    main()
