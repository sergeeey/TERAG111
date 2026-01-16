#!/usr/bin/env python3
"""
CLI утилита для создания API ключей TERAG
"""

import sys
import argparse
from pathlib import Path

# Добавляем src в путь
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.security.api_auth import TeragAuth
from src.security.roles import Role


def main():
    """Основная функция"""
    parser = argparse.ArgumentParser(description="Create TERAG API key")
    parser.add_argument("--client-id", required=True, help="Client ID")
    parser.add_argument(
        "--role",
        choices=["admin", "analyst", "client"],
        default="client",
        help="Role (default: client)"
    )
    parser.add_argument(
        "--expires-days",
        type=int,
        default=365,
        help="Expiration in days (default: 365)"
    )
    
    args = parser.parse_args()
    
    # Создаем ключ
    try:
        auth = TeragAuth()
        role = Role(args.role.upper())
        
        api_key = auth.create_key(
            client_id=args.client_id,
            role=role,
            expires_days=args.expires_days
        )
        
        print(f"✅ API key created successfully!")
        print(f"\nKey: {api_key.key}")
        print(f"Role: {api_key.role.value}")
        print(f"Client ID: {api_key.client_id}")
        print(f"Expires: {api_key.expires_at}")
        print(f"\n⚠️  Save this key securely - it will not be shown again!")
        
    except Exception as e:
        print(f"❌ Error creating API key: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
