#!/usr/bin/env python3
"""
Universal Config Loader for PROJ344 System
Works with: Streamlit, .env files, environment variables, shared secrets
Industry best practice for secret management across multiple repos
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any

class ConfigLoader:
    """
    Universal configuration loader that works across all environments.

    Priority order:
    1. Streamlit secrets.toml (if running in Streamlit)
    2. Specified .env file
    3. Local .env file in current directory
    4. Shared secrets directory (~/.proj344_secrets/.env)
    5. System environment variables
    """

    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize config loader

        Args:
            env_file: Optional path to specific .env file
        """
        self._secrets = {}
        self._loaded = False
        self._source = None
        self.env_file = env_file

    def load(self) -> Dict[str, Any]:
        """Load secrets from available sources"""
        if self._loaded:
            return self._secrets

        # 1. Try Streamlit secrets first
        secrets = self._try_streamlit()
        if secrets:
            self._secrets = secrets
            self._source = "Streamlit secrets.toml"
            self._loaded = True
            return self._secrets

        # 2. Try specified .env file
        if self.env_file:
            secrets = self._load_env_file(Path(self.env_file))
            if secrets:
                self._secrets = secrets
                self._source = f"Specified .env: {self.env_file}"
                self._loaded = True
                return self._secrets

        # 3. Try local .env
        local_env = Path('.env')
        if local_env.exists():
            secrets = self._load_env_file(local_env)
            if secrets:
                self._secrets = secrets
                self._source = "Local .env file"
                self._loaded = True
                return self._secrets

        # 4. Try shared secrets directory
        shared_env = Path.home() / '.proj344_secrets' / '.env'
        if shared_env.exists():
            secrets = self._load_env_file(shared_env)
            if secrets:
                self._secrets = secrets
                self._source = f"Shared secrets: {shared_env}"
                self._loaded = True
                return self._secrets

        # 5. Fall back to environment variables
        secrets = self._load_from_environment()
        if secrets:
            self._secrets = secrets
            self._source = "System environment variables"
            self._loaded = True
            return self._secrets

        # Nothing found
        self._source = "No secrets found"
        self._loaded = True
        return {}

    def _try_streamlit(self) -> Optional[Dict]:
        """Try to load from Streamlit secrets"""
        try:
            import streamlit as st
            if hasattr(st, 'secrets'):
                return dict(st.secrets)
        except ImportError:
            pass
        except Exception:
            pass
        return None

    def _load_env_file(self, filepath: Path) -> Optional[Dict]:
        """Load environment variables from .env file"""
        if not filepath.exists():
            return None

        secrets = {}
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if not line or line.startswith('#'):
                        continue
                    # Parse key=value
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        # Remove quotes if present
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        secrets[key] = value
            return secrets if secrets else None
        except Exception as e:
            print(f"[WARN] Error loading {filepath}: {e}")
            return None

    def _load_from_environment(self) -> Optional[Dict]:
        """Load from system environment variables"""
        secret_keys = [
            'SUPABASE_URL',
            'SUPABASE_KEY',
            'OPENAI_API_KEY',
            'ANTHROPIC_API_KEY',
            'TELEGRAM_BOT_TOKEN',
            'NEO4J_URI',
            'NEO4J_USER',
            'NEO4J_PASSWORD',
            'QDRANT_URL',
            'QDRANT_API_KEY',
            'PINECONE_API_KEY',
            'PINECONE_ENVIRONMENT'
        ]

        secrets = {}
        for key in secret_keys:
            value = os.getenv(key)
            if value:
                secrets[key] = value

        return secrets if secrets else None

    def get(self, key: str, default: Any = None) -> Any:
        """Get a specific secret value"""
        if not self._loaded:
            self.load()
        return self._secrets.get(key, default)

    def get_all(self) -> Dict[str, Any]:
        """Get all loaded secrets"""
        if not self._loaded:
            self.load()
        return self._secrets.copy()

    def get_source(self) -> str:
        """Get the source from which secrets were loaded"""
        if not self._loaded:
            self.load()
        return self._source

    def print_status(self):
        """Print configuration status (useful for debugging)"""
        if not self._loaded:
            self.load()

        print("=" * 80)
        print("CONFIGURATION STATUS")
        print("=" * 80)
        print(f"Source: {self._source}")
        print(f"Secrets loaded: {len(self._secrets)}")
        print()

        if self._secrets:
            print("Available secrets:")
            for key in sorted(self._secrets.keys()):
                value = self._secrets[key]
                # Mask sensitive values
                if len(value) > 20:
                    masked = f"{value[:10]}...{value[-10:]}"
                else:
                    masked = f"{value[:5]}..." if len(value) > 5 else "***"
                print(f"  {key}: {masked}")
        else:
            print("[WARN] No secrets found!")
            print()
            print("To configure secrets, create one of:")
            print("  1. .streamlit/secrets.toml (for Streamlit apps)")
            print("  2. .env (in current directory)")
            print("  3. ~/.proj344_secrets/.env (shared across repos)")
            print("  4. Set system environment variables")

        print("=" * 80)


# Convenience functions for easy usage
_global_config = None

def load_config(env_file: Optional[str] = None) -> ConfigLoader:
    """Load configuration (singleton pattern)"""
    global _global_config
    if _global_config is None:
        _global_config = ConfigLoader(env_file)
        _global_config.load()
    return _global_config

def get_secret(key: str, default: Any = None) -> Any:
    """Get a specific secret value"""
    config = load_config()
    return config.get(key, default)

def get_all_secrets() -> Dict[str, Any]:
    """Get all secrets"""
    config = load_config()
    return config.get_all()

def print_config_status():
    """Print configuration status"""
    config = load_config()
    config.print_status()


# Example usage and testing
if __name__ == "__main__":
    print("Testing Config Loader...")
    print()

    # Load configuration
    config = ConfigLoader()
    secrets = config.load()

    # Print status
    config.print_status()

    # Test individual access
    print()
    print("Testing individual secret access:")
    print(f"SUPABASE_URL: {config.get('SUPABASE_URL', 'NOT FOUND')}")
    print(f"OPENAI_API_KEY: {config.get('OPENAI_API_KEY', 'NOT FOUND')[:20]}...")
    print(f"Config source: {config.get_source()}")

    # Test convenience functions
    print()
    print("Testing convenience functions:")
    supabase_url = get_secret('SUPABASE_URL')
    print(f"get_secret('SUPABASE_URL'): {supabase_url}")
