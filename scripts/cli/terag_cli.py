#!/usr/bin/env python3
"""
TERAG CLI - утилита для управления API ключами
"""

import sys
import argparse
from pathlib import Path

# Добавляем src в путь
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.security.api_auth import TeragAuth
from src.security.roles import Role


def create_key(args):
    """Создать новый API ключ"""
    try:
        auth = TeragAuth()
        role = Role[args.role.upper()]
        
        api_key = auth.create_key(
            client_id=args.client_id,
            role=role,
            expires_days=args.expires_days
        )
        
        print("✅ API key created successfully!")
        print(f"\nKey: {api_key.key}")
        print(f"Role: {api_key.role.value}")
        print(f"Client ID: {api_key.client_id}")
        print(f"Expires: {api_key.expires_at}")
        print(f"\n⚠️  Save this key securely - it will not be shown again!")
        
    except Exception as e:
        print(f"❌ Error creating API key: {e}", file=sys.stderr)
        sys.exit(1)


def list_keys(args):
    """Показать список API ключей"""
    try:
        auth = TeragAuth()
        db = auth.db
        
        # Получаем все ключи
        all_keys = list(db.api_keys_collection.find({}))
        
        if not all_keys:
            print("No API keys found.")
            return
        
        print(f"\nFound {len(all_keys)} API key(s):\n")
        print(f"{'Client ID':<20} {'Role':<15} {'Created':<20} {'Expires':<20} {'Status':<10}")
        print("-" * 90)
        
        for key_doc in all_keys:
            client_id = key_doc.get("client_id", "N/A")
            role = key_doc.get("role", "N/A")
            created = key_doc.get("created_at", "N/A")
            if hasattr(created, 'strftime'):
                created = created.strftime("%Y-%m-%d")
            expires = key_doc.get("expires_at", "N/A")
            if hasattr(expires, 'strftime'):
                expires = expires.strftime("%Y-%m-%d")
            is_active = "Active" if key_doc.get("is_active", False) else "Inactive"
            
            print(f"{client_id:<20} {role:<15} {created:<20} {expires:<20} {is_active:<10}")
        
    except Exception as e:
        print(f"❌ Error listing API keys: {e}", file=sys.stderr)
        sys.exit(1)


def revoke_key(args):
    """Деактивировать API ключ"""
    try:
        auth = TeragAuth()
        
        # Находим ключ по client_id или по части ключа
        db = auth.db
        
        if args.client_id:
            # Деактивируем все ключи для клиента
            result = db.api_keys_collection.update_many(
                {"client_id": args.client_id},
                {"$set": {"is_active": False}}
            )
            print(f"✅ Deactivated {result.modified_count} API key(s) for client {args.client_id}")
        elif args.key_prefix:
            # Деактивируем ключи по префиксу
            # В реальности нужно проверять хеш, но для простоты используем client_id
            print("⚠️  Revoking by key prefix is not fully supported. Use --client-id instead.")
            sys.exit(1)
        else:
            print("❌ Please specify --client-id or --key-prefix", file=sys.stderr)
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error revoking API key: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Основная функция CLI"""
    parser = argparse.ArgumentParser(
        description="TERAG CLI - управление API ключами",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Создать API ключ для клиента
  terag-cli keys create --client-id "MFO-Example" --role analyst

  # Показать все ключи
  terag-cli keys list

  # Деактивировать ключи клиента
  terag-cli keys revoke --client-id "MFO-Example"
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Команда create
    create_parser = subparsers.add_parser("create", help="Create a new API key")
    create_parser.add_argument("--client-id", required=True, help="Client ID")
    create_parser.add_argument(
        "--role",
        choices=["admin", "analyst", "client"],
        default="client",
        help="Role (default: client)"
    )
    create_parser.add_argument(
        "--expires-days",
        type=int,
        default=365,
        help="Expiration in days (default: 365)"
    )
    create_parser.set_defaults(func=create_key)
    
    # Команда list
    list_parser = subparsers.add_parser("list", help="List all API keys")
    list_parser.set_defaults(func=list_keys)
    
    # Команда revoke
    revoke_parser = subparsers.add_parser("revoke", help="Revoke (deactivate) API key(s)")
    revoke_parser.add_argument("--client-id", help="Client ID to revoke keys for")
    revoke_parser.add_argument("--key-prefix", help="Key prefix to revoke (not fully supported)")
    revoke_parser.set_defaults(func=revoke_key)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == "__main__":
    main()
