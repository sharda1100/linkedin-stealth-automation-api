"""
Complete Test Runner

This script runs all tests in sequence and provides a summary.
Use this to check if your LinkedIn automation system is working.
"""

import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def run_all_tests():
    """Run all tests and provide summary"""
    print("🚀 LinkedIn Automation - System Test")
    print("=" * 60)
    
    test_results = {}
    
    # Test 1: Configuration
    print("\n1️⃣  CONFIGURATION TEST")
    print("-" * 30)
    try:
        from tests.test_config import test_config
        test_results["Configuration"] = test_config()
    except Exception as e:
        print(f"❌ Configuration test failed to run: {e}")
        test_results["Configuration"] = False
    
    # Test 2: Logger
    print("\n2️⃣  LOGGER TEST")
    print("-" * 30)
    try:
        from tests.test_logger import test_logger
        test_results["Logger"] = test_logger()
    except Exception as e:
        print(f"❌ Logger test failed to run: {e}")
        test_results["Logger"] = False
    
    # Test 3: Browser Dependencies
    print("\n3️⃣  BROWSER DEPENDENCIES TEST")
    print("-" * 30)
    try:
        from tests.test_browser import test_browser_dependencies_only
        test_results["Browser Dependencies"] = test_browser_dependencies_only()
    except Exception as e:
        print(f"❌ Browser dependencies test failed to run: {e}")
        test_results["Browser Dependencies"] = False
    
    # Summary
    print("\n📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:.<40} {status}")
        if result:
            passed += 1
    
    print("-" * 60)
    print(f"TOTAL: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Your system is ready!")
        print("\n📝 Next Steps:")
        print("   1. Install missing dependencies (if any)")
        print("   2. Continue with Milestone 3: Profile Interaction Module")
        print("   3. Test the complete LinkedIn automation workflow")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        print("\n🔧 Common Solutions:")
        print("   • Install missing Python packages with pip")
        print("   • Check if Chrome browser is installed")
        print("   • Verify your Python environment is activated")
    
    return passed == total

def check_project_structure():
    """Check if project structure is correct"""
    print("\n🏗️  PROJECT STRUCTURE CHECK")
    print("-" * 30)
    
    required_files = [
        "main.py",
        "requirements.txt",
        "linkedin_automation/__init__.py",
        "linkedin_automation/core/__init__.py",
        "linkedin_automation/core/browser_manager.py",
        "linkedin_automation/core/linkedin_auth.py",
        "linkedin_automation/api/__init__.py",
        "linkedin_automation/utils/__init__.py",
        "linkedin_automation/utils/config.py",
        "linkedin_automation/utils/logger.py"
    ]
    
    missing_files = []
    existing_files = []
    
    for file_path in required_files:
        full_path = os.path.join(project_root, file_path)
        if os.path.exists(full_path):
            existing_files.append(file_path)
            print(f"✅ {file_path}")
        else:
            missing_files.append(file_path)
            print(f"❌ {file_path}")
    
    print(f"\n📊 Project Structure: {len(existing_files)}/{len(required_files)} files found")
    
    if missing_files:
        print(f"\n⚠️  Missing files:")
        for file in missing_files:
            print(f"   • {file}")
    
    return len(missing_files) == 0

if __name__ == "__main__":
    print("🔍 Checking project structure first...")
    structure_ok = check_project_structure()
    
    if structure_ok:
        print("\n✅ Project structure looks good!")
        run_all_tests()
    else:
        print("\n❌ Project structure is incomplete. Please create missing files first.")
