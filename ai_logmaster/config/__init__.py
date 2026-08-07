"""
Configuration management for AI Triage
Loads config from ~/.ai-triage/config.yaml or package default
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any
import json

# Default config location
DEFAULT_CONFIG_DIR = Path.home() / ".ai-logmaster"
DEFAULT_CONFIG_FILE_JSON = DEFAULT_CONFIG_DIR / "config.json"
DEFAULT_CONFIG_FILE_YAML = DEFAULT_CONFIG_DIR / "config.yaml"
PACKAGE_CONFIG_JSON = Path(__file__).parent / "config.json"

class Config:
    """Configuration manager"""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        
        config_file = None
        is_json = False
        
        if self.config_path and os.path.exists(self.config_path):
            config_file = Path(self.config_path)
            is_json = config_file.suffix == '.json'
        elif os.path.exists(DEFAULT_CONFIG_FILE_JSON):
            config_file = DEFAULT_CONFIG_FILE_JSON
            is_json = True
        elif os.path.exists(DEFAULT_CONFIG_FILE_YAML):
            config_file = DEFAULT_CONFIG_FILE_YAML
            is_json = False
        elif os.path.exists(PACKAGE_CONFIG_JSON):
            # Use package config as fallback
            config_file = PACKAGE_CONFIG_JSON
            is_json = True
            print(f"[CONFIG] Using config from {PACKAGE_CONFIG_JSON}")
        else:
            # Return minimal default config
            return self._get_default_config()
        
        try:
            with open(config_file, 'r') as f:
                if is_json:
                    config = json.load(f)
                else:
                    config = yaml.safe_load(f)
            
            # Expand environment variables
            config = self._expand_env_vars(config)
            
            return config
        except Exception as e:
            print(f"[CONFIG] Error loading config: {e}")
            return self._get_default_config()
    
    def _expand_env_vars(self, config: Any) -> Any:
        """Recursively expand environment variables in config"""
        if isinstance(config, dict):
            return {k: self._expand_env_vars(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._expand_env_vars(item) for item in config]
        elif isinstance(config, str):
            # Expand ${VAR} or $VAR
            if config.startswith("${") and config.endswith("}"):
                var_name = config[2:-1]
                return os.environ.get(var_name, config)
            elif config.startswith("$"):
                var_name = config[1:]
                return os.environ.get(var_name, config)
        return config
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return minimal default configuration"""
        return {
            "ai": {
                "provider": "groq",
                "model": "llama-3.1-8b-instant",
                "api_key": os.environ.get("GROQ_API_KEY", ""),
                "temperature": 0.2,
                "max_tokens": 1024,
            },
            "agent": {
                "use_cached_solutions": True,
                "fetch_documentation": True,
                "use_ai_analysis": True,
                "auto_fix": False,
                "cached_error_types": ["connection", "import", "memory", "timeout", "permission"],
                "complex_error_types": ["syntax", "type", "value", "unknown"],
            },
            "documentation": {
                "enable_search": True,
                "search_engine": "duckduckgo",
            },
            "output": {
                "verbose": True,
                "show_api_calls": True,
            },
        }
    
    def get(self, key: str, default=None):
        """Get config value by dot-notation key (e.g., 'ai.model')"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        
        return value if value is not None else default
    
    def get_ai_config(self) -> Dict[str, Any]:
        """Get AI configuration"""
        return self.config.get("ai", {})
    
    def get_agent_config(self) -> Dict[str, Any]:
        """Get agent configuration"""
        return self.config.get("agent", {})

# Global config instance
_config = None

def get_config(config_path: str = None) -> Config:
    """Get global config instance"""
    global _config
    if _config is None:
        _config = Config(config_path)
    return _config

def init_config():
    """Initialize config directory and file"""
    if not DEFAULT_CONFIG_DIR.exists():
        DEFAULT_CONFIG_DIR.mkdir(parents=True)
        print(f"[CONFIG] Created config directory: {DEFAULT_CONFIG_DIR}")
    
    if not DEFAULT_CONFIG_FILE_JSON.exists() and PACKAGE_CONFIG_JSON.exists():
        import shutil
        shutil.copy(PACKAGE_CONFIG_JSON, DEFAULT_CONFIG_FILE_JSON)
        print(f"[CONFIG] Created config file: {DEFAULT_CONFIG_FILE_JSON}")
        print(f"[CONFIG] Please edit this file to set your API key")
        return False
    
    return True
