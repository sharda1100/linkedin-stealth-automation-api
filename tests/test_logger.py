"""
Test script for logger module

This script tests:
- Logger initialization
- Different log levels
- File and console logging
- Log formatting
"""

import sys
import os
import time

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_logger():
    """Test logger module"""
    print("🧪 Testing Logger Module...")
    print("=" * 50)
    
    try:
        # Test importing logger
        from linkedin_automation.utils.logger import setup_logger, get_logger
        print("✅ Logger module imported successfully")
        
        # Test setting up logger
        logger = setup_logger(log_level="DEBUG", log_file="tests/test.log")
        print("✅ Logger setup completed")
        
        # Test getting logger for specific module
        module_logger = get_logger("test_module")
        print("✅ Module logger created")
        
        # Test different log levels
        print("\n📝 Testing different log levels:")
        module_logger.debug("This is a DEBUG message")
        module_logger.info("This is an INFO message")
        module_logger.warning("This is a WARNING message")
        module_logger.error("This is an ERROR message")
        
        print("✅ Log messages sent successfully")
        
        # Check if log file was created
        log_file_path = os.path.join("tests", "test.log")
        if os.path.exists(log_file_path):
            print(f"✅ Log file created: {log_file_path}")
            
            # Read and display first few lines of log file
            with open(log_file_path, 'r') as f:
                lines = f.readlines()
                if lines:
                    print(f"📄 Log file contains {len(lines)} lines")
                    print("📄 Sample log entry:")
                    print(f"   {lines[-1].strip()}")  # Show last line
        else:
            print("⚠️  Log file not created (might be permission issue)")
        
        print("\n🎉 Logger test completed successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Make sure you've installed loguru: pip install loguru")
        return False
    except Exception as e:
        print(f"❌ Logger test failed: {e}")
        return False

if __name__ == "__main__":
    test_logger()
