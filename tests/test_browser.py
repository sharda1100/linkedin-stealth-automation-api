"""
Test script for browser manager module

This script tests:
- Browser manager import
- Stealth browser creation (basic test)
- Browser session management
- Basic navigation

WARNING: This test will open a browser window!
"""

import sys
import os
import time

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_browser_manager():
    """Test browser manager module"""
    print("🧪 Testing Browser Manager Module...")
    print("=" * 50)
    print("⚠️  This test will open a browser window!")
    
    try:
        # Test importing browser manager
        from linkedin_automation.core.browser_manager import BrowserManager
        print("✅ Browser Manager module imported successfully")
        
        # Create browser manager instance
        browser_manager = BrowserManager()
        print("✅ Browser Manager instance created")
        
        # Test browser creation (this will open a browser)
        print("\n🌐 Creating stealth browser...")
        print("   (This may take a few seconds...)")
        
        driver = browser_manager.create_stealth_browser()
        if driver:
            print("✅ Stealth browser created successfully!")
            
            # Test basic navigation
            print("\n🧭 Testing navigation...")
            success = browser_manager.navigate_to("https://www.google.com")
            if success:
                print("✅ Navigation to Google successful")
                
                # Get current URL
                current_url = browser_manager.get_current_url()
                print(f"📍 Current URL: {current_url}")
                
                # Test session info
                session_info = browser_manager.get_session_info()
                print(f"📊 Session ID: {session_info['session_id']}")
                print(f"📊 Browser Active: {session_info['is_active']}")
                
                # Wait a bit to see the browser
                print("\n⏳ Browser will close in 5 seconds...")
                time.sleep(5)
                
            else:
                print("❌ Navigation failed")
            
            # Test browser cleanup
            browser_manager.close_browser()
            print("✅ Browser closed successfully")
            
        else:
            print("❌ Failed to create browser")
            return False
        
        print("\n🎉 Browser Manager test completed successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Missing dependencies. Install with:")
        print("   pip install selenium undetected-chromedriver selenium-stealth webdriver-manager")
        return False
    except Exception as e:
        print(f"❌ Browser Manager test failed: {e}")
        print("💡 Make sure Chrome browser is installed on your system")
        return False

def test_browser_dependencies_only():
    """Test only if browser dependencies can be imported"""
    print("🧪 Testing Browser Dependencies...")
    print("=" * 50)
    
    dependencies = [
        ("selenium", "pip install selenium"),
        ("undetected_chromedriver", "pip install undetected-chromedriver"),
        ("selenium_stealth", "pip install selenium-stealth"),
        ("webdriver_manager", "pip install webdriver-manager")
    ]
    
    all_good = True
    for dep, install_cmd in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep} - Available")
        except ImportError:
            print(f"❌ {dep} - Missing")
            print(f"   Install with: {install_cmd}")
            all_good = False
    
    if all_good:
        print("\n🎉 All browser dependencies are available!")
        
        # Ask user if they want to run full browser test
        response = input("\nDo you want to test browser creation? (y/n): ").lower().strip()
        if response == 'y':
            return test_browser_manager()
    else:
        print("\n⚠️  Install missing dependencies before running browser tests")
    
    return all_good

if __name__ == "__main__":
    # First test dependencies only
    test_browser_dependencies_only()
