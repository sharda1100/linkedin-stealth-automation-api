"""
Configuration Management Module

This module handles:
- Environment variable loading
- Default configuration values
- Configuration validation
- Application settings
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration manager for the application"""
    
    def __init__(self):
        """Initialize configuration with default values"""
        self._config = {
            # Browser Configuration
            "HEADLESS_MODE": os.getenv("HEADLESS_MODE", "False"),
            "BROWSER_TIMEOUT": int(os.getenv("BROWSER_TIMEOUT", "30")),
            "IMPLICIT_WAIT": int(os.getenv("IMPLICIT_WAIT", "10")),
            
            # LinkedIn URLs
            "LINKEDIN_BASE_URL": os.getenv("LINKEDIN_BASE_URL", "https://www.linkedin.com"),
            "LINKEDIN_LOGIN_URL": os.getenv("LINKEDIN_LOGIN_URL", "https://www.linkedin.com/login"),
            
            # Session Configuration
            "SESSION_TIMEOUT": int(os.getenv("SESSION_TIMEOUT", "1800")),  # 30 minutes
            "MAX_RETRY_ATTEMPTS": int(os.getenv("MAX_RETRY_ATTEMPTS", "3")),
            
            # Logging Configuration
            "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
            "LOG_FILE": os.getenv("LOG_FILE", "logs/linkedin_automation.log"),
            
            # Browser Profile
            "BROWSER_PROFILE_PATH": os.getenv("BROWSER_PROFILE_PATH", ""),
            
            # Development Settings
            "DEBUG": os.getenv("DEBUG", "True").lower() == "true",
            
            # API Configuration
            "API_HOST": os.getenv("API_HOST", "0.0.0.0"),
            "API_PORT": int(os.getenv("API_PORT", "8000")),
            
            # Delays (in seconds) for human-like behavior
            "MIN_DELAY": float(os.getenv("MIN_DELAY", "0.5")),
            "MAX_DELAY": float(os.getenv("MAX_DELAY", "2.0")),
            "TYPING_DELAY": float(os.getenv("TYPING_DELAY", "0.1")),
        }
        
        # Validate critical configurations
        self._validate_config()
    
    def _validate_config(self):
        """Validate configuration values"""
        # Ensure log directory exists
        log_file = self._config.get("LOG_FILE")
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Validate timeout values
        if self._config["BROWSER_TIMEOUT"] < 10:
            self._config["BROWSER_TIMEOUT"] = 10
            
        if self._config["IMPLICIT_WAIT"] < 5:
            self._config["IMPLICIT_WAIT"] = 5
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any):
        """
        Set configuration value
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        self._config[key] = value
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values"""
        return self._config.copy()
    
    def is_debug(self) -> bool:
        """Check if debug mode is enabled"""
        return self._config.get("DEBUG", False)
    
    def is_headless(self) -> bool:
        """Check if headless mode is enabled"""
        return self._config.get("HEADLESS_MODE", "False").lower() == "true"


# Global configuration instance
_config_instance = None


def get_config() -> Config:
    """
    Get global configuration instance (singleton pattern)
    
    Returns:
        Config: Global configuration instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance


def reload_config():
    """Reload configuration from environment variables"""
    global _config_instance
    _config_instance = None
    load_dotenv(override=True)
    return get_config()
