"""
API Endpoints - FastAPI Route Handlers

This module defines:
- REST API endpoints for LinkedIn automation
- Route handlers that use core business logic
- Request/response handling
- Error handling and status codes
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, Any
import time
from datetime import datetime

# Import our models
from linkedin_automation.api.model import (
    LoginRequest, LoginResponse,
    ConnectRequest, ConnectResponse,
    CheckConnectionRequest, CheckConnectionResponse,
    CloseSessionResponse, SessionInfoResponse,
    HealthCheckResponse, ErrorResponse
)

# Import core business logic
from linkedin_automation.core.browser_manager import browser_manager
from linkedin_automation.core.linkedin_auth import LinkedInAuth
from linkedin_automation.core.profile_handler import ProfileHandler
from linkedin_automation.core.message_handler import MessageHandler
from linkedin_automation.utils.logger import get_logger
from linkedin_automation.utils.config import get_config

# Initialize components
logger = get_logger(__name__)
config = get_config()
router = APIRouter()

# Global instances (will be properly initialized when needed)
linkedin_auth = None
profile_handler = None
message_handler = None


def get_linkedin_auth():
    """Get or create LinkedIn authentication instance"""
    global linkedin_auth
    if linkedin_auth is None:
        linkedin_auth = LinkedInAuth(browser_manager)
    return linkedin_auth


def get_profile_handler():
    """Get or create Profile handler instance"""
    global profile_handler
    if profile_handler is None:
        profile_handler = ProfileHandler(browser_manager)
    return profile_handler


def get_message_handler():
    """Get or create Message handler instance"""
    global message_handler
    if message_handler is None:
        message_handler = MessageHandler(browser_manager)
    return message_handler


def ensure_browser_active():
    """Ensure browser session is active"""
    if not browser_manager.is_browser_active():
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": "No active browser session. Please login first.",
                "error_type": "no_session"
            }
        )


def ensure_logged_in():
    """Ensure user is logged into LinkedIn"""
    ensure_browser_active()
    if not browser_manager.is_logged_in:
        raise HTTPException(
            status_code=401,
            detail={
                "success": False,
                "error": "Not logged into LinkedIn. Please login first.",
                "error_type": "not_authenticated"
            }
        )


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest) -> LoginResponse:
    """
    Login to LinkedIn
    
    This endpoint:
    1. Creates a stealth browser session
    2. Logs into LinkedIn with provided credentials
    3. Returns session information
    """
    try:
        logger.info(f"Login attempt for user: {request.username}")
        
        # Create browser if not exists
        if not browser_manager.is_browser_active():
            logger.info("Creating new browser session...")
            browser_manager.create_stealth_browser()
        
        # Get authentication handler
        auth_handler = get_linkedin_auth()
        
        # Attempt login
        login_result = auth_handler.login(request.username, request.password)
        
        if login_result["success"]:
            session_info = browser_manager.get_session_info()
            
            return LoginResponse(
                success=True,
                message=login_result["message"],
                session_id=session_info["session_id"],
                current_url=session_info["current_url"]
            )
        else:
            return LoginResponse(
                success=False,
                message="Login failed",
                error=login_result["error"],
                error_type=login_result["error_type"]
            )
            
    except Exception as e:
        logger.error(f"Login endpoint error: {str(e)}")
        return LoginResponse(
            success=False,
            message="Login failed due to system error",
            error=str(e),
            error_type="system_error"
        )


@router.post("/connect", response_model=ConnectResponse)
async def connect(request: ConnectRequest) -> ConnectResponse:
    """
    Send connection request to a LinkedIn profile
    
    This endpoint:
    1. Navigates to the specified profile
    2. Checks current connection status
    3. Sends connection request if possible
    4. Returns operation result
    """
    try:
        logger.info(f"Connection request to: {request.profile_url}")
        
        # Ensure user is logged in
        ensure_logged_in()
        
        # Get profile handler
        handler = get_profile_handler()
        
        # Send connection request
        result = handler.send_connection_request(
            profile_url=request.profile_url,
            note=request.note
        )
        
        if result["success"]:
            return ConnectResponse(
                success=True,
                message=result["message"],
                profile_url=request.profile_url,
                connection_status="pending",
                had_note=request.note is not None,
                profile_info=result.get("profile_info")
            )
        else:
            return ConnectResponse(
                success=False,
                message="Connection request failed",
                profile_url=request.profile_url,
                error=result["error"],
                error_type=result["error_type"]
            )
            
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"Connect endpoint error: {str(e)}")
        return ConnectResponse(
            success=False,
            message="Connection request failed due to system error",
            profile_url=request.profile_url,
            error=str(e),
            error_type="system_error"
        )


@router.post("/check_connection", response_model=CheckConnectionResponse)
async def check_connection(request: CheckConnectionRequest) -> CheckConnectionResponse:
    """
    Check connection status and send message if connected
    
    This endpoint:
    1. Checks if we're connected to the profile
    2. If connected, sends the provided message
    3. Returns operation result and connection status
    """
    try:
        logger.info(f"Checking connection and messaging: {request.profile_url}")
        
        # Ensure user is logged in
        ensure_logged_in()
        
        # Get handlers
        profile_handler = get_profile_handler()
        message_handler = get_message_handler()
        
        # Check connection status first
        status_result = profile_handler.check_connection_status(request.profile_url)
        
        if not status_result["success"]:
            return CheckConnectionResponse(
                success=False,
                message="Failed to check connection status",
                profile_url=request.profile_url,
                connection_status="unknown",
                error=status_result["error"],
                error_type=status_result["error_type"]
            )
        
        connection_status = status_result["connection_status"]
        
        # If connected, try to send message
        message_sent = False
        if connection_status == "connected":
            message_result = message_handler.send_message(
                profile_url=request.profile_url,
                message=request.message
            )
            
            if message_result["success"]:
                message_sent = True
                return CheckConnectionResponse(
                    success=True,
                    message="Message sent successfully",
                    profile_url=request.profile_url,
                    connection_status=connection_status,
                    message_sent=True,
                    message_text=request.message
                )
            else:
                return CheckConnectionResponse(
                    success=False,
                    message="Connected but failed to send message",
                    profile_url=request.profile_url,
                    connection_status=connection_status,
                    message_sent=False,
                    error=message_result["error"],
                    error_type=message_result["error_type"]
                )
        else:
            # Not connected - can't send message
            return CheckConnectionResponse(
                success=False,
                message=f"Cannot send message - connection status: {connection_status}",
                profile_url=request.profile_url,
                connection_status=connection_status,
                message_sent=False,
                error=f"Not connected (status: {connection_status})",
                error_type="not_connected"
            )
            
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"Check connection endpoint error: {str(e)}")
        return CheckConnectionResponse(
            success=False,
            message="Check connection failed due to system error",
            profile_url=request.profile_url,
            connection_status="unknown",
            error=str(e),
            error_type="system_error"
        )


@router.get("/close", response_model=CloseSessionResponse)
async def close_session() -> CloseSessionResponse:
    """
    Close the browser session and cleanup resources
    
    This endpoint:
    1. Closes the browser session
    2. Cleans up resources
    3. Returns operation result
    """
    try:
        logger.info("Closing browser session...")
        
        session_info = browser_manager.get_session_info()
        session_id = session_info.get("session_id")
        
        # Close browser session
        browser_manager.close_browser()
        
        # Reset global handlers
        global linkedin_auth, profile_handler, message_handler
        linkedin_auth = None
        profile_handler = None
        message_handler = None
        
        logger.info("Browser session closed successfully")
        
        return CloseSessionResponse(
            success=True,
            message="Session closed successfully",
            session_id=session_id
        )
        
    except Exception as e:
        logger.error(f"Close session endpoint error: {str(e)}")
        return CloseSessionResponse(
            success=False,
            message="Failed to close session",
            error=str(e)
        )


@router.get("/session_info", response_model=SessionInfoResponse)
async def get_session_info() -> SessionInfoResponse:
    """
    Get current session information
    
    Returns:
    - Session ID
    - Browser status
    - Login status
    - Current URL
    """
    try:
        session_info = browser_manager.get_session_info()
        
        return SessionInfoResponse(
            session_id=session_info.get("session_id"),
            is_active=session_info.get("is_active", False),
            is_logged_in=session_info.get("is_logged_in", False),
            current_url=session_info.get("current_url"),
            uptime=None  # Could calculate uptime if needed
        )
        
    except Exception as e:
        logger.error(f"Session info endpoint error: {str(e)}")
        return SessionInfoResponse(
            session_id=None,
            is_active=False,
            is_logged_in=False,
            current_url=None
        )


@router.get("/health", response_model=HealthCheckResponse)
async def health_check() -> HealthCheckResponse:
    """
    Health check endpoint
    
    Returns:
    - System status
    - Component status
    - Timestamp
    """
    try:
        # Check component status
        components = {
            "browser_manager": "ready" if browser_manager else "not_initialized",
            "configuration": "loaded" if config else "error",
            "logging": "active",
        }
        
        # Add browser-specific status if available
        if browser_manager.is_browser_active():
            components["browser_session"] = "active"
            components["authentication"] = "logged_in" if browser_manager.is_logged_in else "not_authenticated"
        else:
            components["browser_session"] = "inactive"
            components["authentication"] = "no_session"
        
        return HealthCheckResponse(
            status="healthy",
            message="LinkedIn Automation API is operational",
            timestamp=datetime.now(),
            components=components
        )
        
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return HealthCheckResponse(
            status="unhealthy",
            message="System error detected",
            timestamp=datetime.now(),
            components={"error": str(e)}
        )