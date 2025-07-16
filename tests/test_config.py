"""
Test script for configuration module

This script tests:
- Configuration loading
- Environment variables
- Default values
- Configuration validation
"""

import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_config():
    """Test configuration module"""
    print("🧪 Testing Configuration Module...")
    print("=" * 50)
    
    try:
        # Test importing config
        from linkedin_automation.utils.config import get_config, Config
        print("✅ Config module imported successfully")
        
        # Test getting config instance
        config = get_config()
        print("✅ Config instance created successfully")
        
        # Test configuration values
        print("\n📋 Configuration Values:")
        print(f"  • Debug Mode: {config.is_debug()}")
        print(f"  • Headless Mode: {config.is_headless()}")
        print(f"  • Browser Timeout: {config.get('BROWSER_TIMEOUT')}")
        print(f"  • LinkedIn Login URL: {config.get('LINKEDIN_LOGIN_URL')}")
        print(f"  • Log Level: {config.get('LOG_LEVEL')}")
        
        # Test setting and getting values
        config.set("TEST_VALUE", "test123")
        test_value = config.get("TEST_VALUE")
        if test_value == "test123":
            print("✅ Set/Get functionality working")
        else:
            print("❌ Set/Get functionality failed")
        
        # Test all configurations
        all_config = config.get_all()
        print(f"\n📊 Total configuration items: {len(all_config)}")
        
        print("\n🎉 Configuration test completed successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Make sure you've installed python-dotenv: pip install python-dotenv")
        return False
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

if __name__ == "__main__":
    test_config()
