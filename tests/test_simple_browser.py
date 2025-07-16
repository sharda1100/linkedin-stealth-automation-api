"""
Simple browser test to verify basic functionality

This test creates a basic browser without advanced stealth options
to verify that Chrome and Selenium are working properly.
"""

import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_simple_browser():
    """Test basic browser functionality"""
    print("🧪 Testing Simple Browser...")
    print("=" * 50)
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        print("✅ Selenium imported successfully")
        
        # Create simple Chrome options
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        print("🌐 Creating basic Chrome browser...")
        driver = webdriver.Chrome(options=options)
        
        if driver:
            print("✅ Basic Chrome browser created successfully!")
            
            # Test navigation
            driver.get("https://www.google.com")
            print(f"✅ Navigated to: {driver.current_url}")
            
            # Test page title
            title = driver.title
            print(f"✅ Page title: {title}")
            
            print("\n⏳ Browser will close in 3 seconds...")
            import time
            time.sleep(3)
            
            driver.quit()
            print("✅ Browser closed successfully")
            
            return True
        
    except Exception as e:
        print(f"❌ Browser test failed: {e}")
        print("\n💡 Possible solutions:")
        print("   • Make sure Chrome browser is installed")
        print("   • Try updating Chrome to latest version")
        print("   • Check if Windows Defender is blocking Chrome automation")
        return False

if __name__ == "__main__":
    test_simple_browser()
