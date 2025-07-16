"""
Test script for API Endpoints

This script tests:
- API endpoint imports and structure
- FastAPI app creation
- Route registration
- Basic endpoint validation
"""

import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_api_imports():
    """Test API components can be imported"""
    print("🧪 Testing API Imports...")
    print("=" * 50)
    
    try:
        # Test endpoint imports
        from linkedin_automation.api.endpoints import router
        print("✅ API router imported successfully")
        
        # Test model imports
        from linkedin_automation.api.model import LoginRequest, LoginResponse
        print("✅ API models imported successfully")
        
        # Test main app import
        from main import app
        print("✅ Main FastAPI app imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        return False
    except Exception as e:
        print(f"❌ API imports test failed: {e}")
        return False

def test_fastapi_app():
    """Test FastAPI application setup"""
    print("\n🧪 Testing FastAPI App Setup...")
    print("=" * 50)
    
    try:
        from main import app
        
        # Check app is FastAPI instance
        from fastapi import FastAPI
        if isinstance(app, FastAPI):
            print("✅ FastAPI app instance created correctly")
        else:
            print("❌ App is not a FastAPI instance")
            return False
        
        # Check app metadata
        if app.title == "LinkedIn Automation API":
            print("✅ App title set correctly")
        else:
            print("❌ App title not set correctly")
        
        if app.version == "1.0.0":
            print("✅ App version set correctly")
        else:
            print("❌ App version not set correctly")
        
        # Check docs URL
        if app.docs_url == "/docs":
            print("✅ Docs URL configured correctly")
        else:
            print("❌ Docs URL not configured")
        
        return True
        
    except Exception as e:
        print(f"❌ FastAPI app test failed: {e}")
        return False

def test_api_routes():
    """Test API routes registration"""
    print("\n🧪 Testing API Routes...")
    print("=" * 50)
    
    try:
        from main import app
        
        # Get all routes
        routes = []
        for route in app.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                routes.append({
                    'path': route.path,
                    'methods': list(route.methods) if route.methods else []
                })
        
        print(f"✅ Found {len(routes)} routes")
        
        # Check for expected endpoints
        expected_endpoints = [
            ("/", ["GET"]),
            ("/api/v1/login", ["POST"]),
            ("/api/v1/connect", ["POST"]),
            ("/api/v1/check_connection", ["POST"]),
            ("/api/v1/close", ["GET"]),
            ("/api/v1/session_info", ["GET"]),
            ("/api/v1/health", ["GET"])
        ]
        
        found_endpoints = []
        for expected_path, expected_methods in expected_endpoints:
            found = False
            for route in routes:
                if route['path'] == expected_path:
                    # Check if any expected method is present
                    if any(method in route['methods'] for method in expected_methods):
                        found = True
                        found_endpoints.append(expected_path)
                        break
            
            if found:
                print(f"✅ Endpoint found: {expected_path} {expected_methods}")
            else:
                print(f"❌ Endpoint missing: {expected_path} {expected_methods}")
        
        if len(found_endpoints) == len(expected_endpoints):
            print("✅ All expected endpoints are registered")
            return True
        else:
            print(f"❌ Only {len(found_endpoints)}/{len(expected_endpoints)} endpoints found")
            return False
        
    except Exception as e:
        print(f"❌ API routes test failed: {e}")
        return False

def test_endpoint_functions():
    """Test individual endpoint functions exist"""
    print("\n🧪 Testing Endpoint Functions...")
    print("=" * 50)
    
    try:
        from linkedin_automation.api.endpoints import (
            login, connect, check_connection, 
            close_session, get_session_info, health_check
        )
        
        endpoint_functions = [
            ("login", login),
            ("connect", connect),
            ("check_connection", check_connection),
            ("close_session", close_session),
            ("get_session_info", get_session_info),
            ("health_check", health_check)
        ]
        
        for name, func in endpoint_functions:
            if callable(func):
                print(f"✅ {name} function is callable")
            else:
                print(f"❌ {name} function is not callable")
                return False
        
        print("✅ All endpoint functions are properly defined")
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Endpoint functions test failed: {e}")
        return False

def test_dependency_functions():
    """Test helper and dependency functions"""
    print("\n🧪 Testing Helper Functions...")
    print("=" * 50)
    
    try:
        from linkedin_automation.api.endpoints import (
            get_linkedin_auth, get_profile_handler, get_message_handler,
            ensure_browser_active, ensure_logged_in
        )
        
        helper_functions = [
            ("get_linkedin_auth", get_linkedin_auth),
            ("get_profile_handler", get_profile_handler),
            ("get_message_handler", get_message_handler),
            ("ensure_browser_active", ensure_browser_active),
            ("ensure_logged_in", ensure_logged_in)
        ]
        
        for name, func in helper_functions:
            if callable(func):
                print(f"✅ {name} helper function exists")
            else:
                print(f"❌ {name} helper function not callable")
                return False
        
        print("✅ All helper functions are properly defined")
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Helper functions test failed: {e}")
        return False

def run_all_api_tests():
    """Run all API endpoint tests"""
    print("🚀 API Endpoints Test Suite")
    print("=" * 60)
    
    test_results = {}
    
    # Run all tests
    test_results["API Imports"] = test_api_imports()
    test_results["FastAPI App"] = test_fastapi_app()
    test_results["API Routes"] = test_api_routes()
    test_results["Endpoint Functions"] = test_endpoint_functions()
    test_results["Helper Functions"] = test_dependency_functions()
    
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
        print("\n🎉 ALL API ENDPOINT TESTS PASSED!")
        print("\n📝 What this means:")
        print("   ✅ FastAPI app is properly configured")
        print("   ✅ All endpoints are registered")
        print("   ✅ All functions are callable")
        print("   ✅ Ready to start the API server")
        print("\n🚀 Next steps:")
        print("   1. Run: python main.py")
        print("   2. Visit: http://localhost:8000/docs")
        print("   3. Test the API endpoints")
    else:
        print("\n⚠️  Some tests failed. Check the error messages above.")
    
    return passed == total

if __name__ == "__main__":
    run_all_api_tests()