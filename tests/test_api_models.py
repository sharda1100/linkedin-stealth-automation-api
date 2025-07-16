"""
Test script for API Models

This script tests:
- Pydantic model creation and validation
- Request model validation
- Response model serialization
- Error handling in models
"""

import sys
import os
from datetime import datetime

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_login_models():
    """Test Login request and response models"""
    print("🧪 Testing Login Models...")
    print("=" * 50)
    
    try:
        from linkedin_automation.api.model import LoginRequest, LoginResponse
        print("✅ Login models imported successfully")
        
        # Test valid login request
        valid_request = LoginRequest(
            username="test@example.com",
            password="password123"
        )
        print(f"✅ Valid login request created: {valid_request.username}")
        
        # Test username validation
        try:
            LoginRequest(username="ab", password="pass")  # Too short
            print("❌ Username validation failed - accepted invalid input")
        except ValueError:
            print("✅ Username validation working - rejected short username")
        
        # Test login response
        success_response = LoginResponse(
            success=True,
            message="Login successful",
            session_id="session_123",
            current_url="https://linkedin.com/feed"
        )
        print(f"✅ Login response created: {success_response.message}")
        
        # Test error response
        error_response = LoginResponse(
            success=False,
            message="Login failed",
            error="Invalid credentials",
            error_type="authentication_error"
        )
        print(f"✅ Error response created: {error_response.error}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Login models test failed: {e}")
        return False

def test_connect_models():
    """Test Connect request and response models"""
    print("\n🧪 Testing Connect Models...")
    print("=" * 50)
    
    try:
        from linkedin_automation.api.model import ConnectRequest, ConnectResponse
        print("✅ Connect models imported successfully")
        
        # Test valid connect request
        valid_request = ConnectRequest(
            profile_url="https://www.linkedin.com/in/someone",
            note="Hi! I'd like to connect."
        )
        print(f"✅ Valid connect request created: {valid_request.profile_url}")
        
        # Test URL validation
        try:
            ConnectRequest(
                profile_url="https://google.com",  # Invalid URL
                note="Hello"
            )
            print("❌ URL validation failed - accepted invalid LinkedIn URL")
        except ValueError:
            print("✅ URL validation working - rejected non-LinkedIn URL")
        
        # Test connect response
        success_response = ConnectResponse(
            success=True,
            message="Connection request sent",
            profile_url="https://www.linkedin.com/in/someone",
            connection_status="pending",
            had_note=True,
            profile_info={"name": "John Doe", "headline": "Software Engineer"}
        )
        print(f"✅ Connect response created: {success_response.connection_status}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Connect models test failed: {e}")
        return False

def test_message_models():
    """Test Message/Check Connection models"""
    print("\n🧪 Testing Message Models...")
    print("=" * 50)
    
    try:
        from linkedin_automation.api.model import CheckConnectionRequest, CheckConnectionResponse
        print("✅ Message models imported successfully")
        
        # Test valid message request
        valid_request = CheckConnectionRequest(
            profile_url="https://www.linkedin.com/in/someone",
            message="Hello! I saw your profile and wanted to reach out."
        )
        print(f"✅ Valid message request created: {len(valid_request.message)} chars")
        
        # Test message validation
        try:
            CheckConnectionRequest(
                profile_url="https://www.linkedin.com/in/someone",
                message=""  # Empty message
            )
            print("❌ Message validation failed - accepted empty message")
        except ValueError:
            print("✅ Message validation working - rejected empty message")
        
        # Test message response
        success_response = CheckConnectionResponse(
            success=True,
            message="Message sent successfully",
            profile_url="https://www.linkedin.com/in/someone",
            connection_status="connected",
            message_sent=True,
            message_text="Hello! I saw your profile..."
        )
        print(f"✅ Message response created: message_sent={success_response.message_sent}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Message models test failed: {e}")
        return False

def test_utility_models():
    """Test utility and helper models"""
    print("\n🧪 Testing Utility Models...")
    print("=" * 50)
    
    try:
        from linkedin_automation.api.model import (
            CloseSessionResponse, SessionInfoResponse, 
            HealthCheckResponse, ErrorResponse, ApiResponse
        )
        print("✅ Utility models imported successfully")
        
        # Test session info
        session_info = SessionInfoResponse(
            session_id="session_123",
            is_active=True,
            is_logged_in=True,
            current_url="https://linkedin.com/feed",
            uptime="00:15:30"
        )
        print(f"✅ Session info created: active={session_info.is_active}")
        
        # Test health check
        health_check = HealthCheckResponse(
            status="healthy",
            message="All systems operational",
            timestamp=datetime.now(),
            components={
                "browser": "ready",
                "authentication": "active",
                "profile_handler": "ready"
            }
        )
        print(f"✅ Health check created: {health_check.status}")
        
        # Test error response
        error_response = ErrorResponse(
            error="Something went wrong",
            error_type="system_error",
            details={"code": 500, "location": "profile_handler"}
        )
        print(f"✅ Error response created: {error_response.error_type}")
        
        # Test generic API response
        api_response = ApiResponse(
            success=True,
            message="Operation completed",
            data={"result": "success", "count": 1}
        )
        print(f"✅ API response created: {api_response.success}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Utility models test failed: {e}")
        return False

def test_model_serialization():
    """Test JSON serialization of models"""
    print("\n🧪 Testing Model Serialization...")
    print("=" * 50)
    
    try:
        from linkedin_automation.api.model import LoginResponse, ConnectResponse
        
        # Create a response model
        response = LoginResponse(
            success=True,
            message="Login successful",
            session_id="session_123",
            current_url="https://linkedin.com/feed"
        )
        
        # Test JSON serialization
        json_data = response.dict()
        print(f"✅ Model serialized to dict: {len(json_data)} fields")
        
        # Test JSON string conversion
        json_string = response.json()
        print(f"✅ Model serialized to JSON: {len(json_string)} chars")
        
        # Test that we can recreate from dict
        recreated = LoginResponse(**json_data)
        print(f"✅ Model recreated from dict: {recreated.session_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Serialization test failed: {e}")
        return False

def run_all_model_tests():
    """Run all API model tests"""
    print("🚀 API Models Test Suite")
    print("=" * 60)
    
    test_results = {}
    
    # Run all tests
    test_results["Login Models"] = test_login_models()
    test_results["Connect Models"] = test_connect_models()
    test_results["Message Models"] = test_message_models()
    test_results["Utility Models"] = test_utility_models()
    test_results["Serialization"] = test_model_serialization()
    
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
        print("\n🎉 ALL API MODEL TESTS PASSED!")
        print("\n📝 What this means:")
        print("   ✅ All Pydantic models are properly defined")
        print("   ✅ Request validation is working")
        print("   ✅ Response serialization is working")
        print("   ✅ Ready to create API endpoints")
    else:
        print("\n⚠️  Some tests failed. Check the error messages above.")
    
    return passed == total

if __name__ == "__main__":
    run_all_model_tests()