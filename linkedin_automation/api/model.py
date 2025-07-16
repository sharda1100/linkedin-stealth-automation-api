"""
API Models - Request and Response Models for FastAPI

This module defines:
- Request models (what clients send to our API)
- Response models (what our API sends back)
- Data validation using Pydantic
- Type hints for better code quality
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime


class LoginRequest(BaseModel):
    """Request model for login endpoint"""
    username: str = Field(..., description="LinkedIn email/username", min_length=1)
    password: str = Field(..., description="LinkedIn password", min_length=1)
    
    @validator('username')
    def validate_username(cls, v):
        if '@' in v and '.' in v:  # Basic email validation
            return v
        elif len(v) >= 3:  # Username validation
            return v
        else:
            raise ValueError('Username must be a valid email or username')


class LoginResponse(BaseModel):
    """Response model for login endpoint"""
    success: bool
    message: str
    session_id: Optional[str] = None
    error: Optional[str] = None
    error_type: Optional[str] = None
    current_url: Optional[str] = None


class ConnectRequest(BaseModel):
    """Request model for connect endpoint"""
    profile_url: str = Field(..., description="LinkedIn profile URL")
    note: Optional[str] = Field(None, description="Optional connection note", max_length=300)
    
    @validator('profile_url')
    def validate_profile_url(cls, v):
        if 'linkedin.com/in/' not in v.lower():
            raise ValueError('Must be a valid LinkedIn profile URL')
        return v


class ConnectResponse(BaseModel):
    """Response model for connect endpoint"""
    success: bool
    message: str
    profile_url: str
    connection_status: Optional[str] = None
    had_note: Optional[bool] = None
    error: Optional[str] = None
    error_type: Optional[str] = None
    profile_info: Optional[Dict[str, str]] = None


class CheckConnectionRequest(BaseModel):
    """Request model for check connection and message endpoint"""
    profile_url: str = Field(..., description="LinkedIn profile URL")
    message: str = Field(..., description="Message to send if connected", min_length=1, max_length=8000)
    
    @validator('profile_url')
    def validate_profile_url(cls, v):
        if 'linkedin.com/in/' not in v.lower():
            raise ValueError('Must be a valid LinkedIn profile URL')
        return v
    
    @validator('message')
    def validate_message(cls, v):
        if len(v.strip()) < 1:
            raise ValueError('Message cannot be empty')
        return v.strip()


class CheckConnectionResponse(BaseModel):
    """Response model for check connection and message endpoint"""
    success: bool
    message: str
    profile_url: str
    connection_status: str
    message_sent: Optional[bool] = None
    message_text: Optional[str] = None
    error: Optional[str] = None
    error_type: Optional[str] = None
    profile_info: Optional[Dict[str, str]] = None


class CloseSessionResponse(BaseModel):
    """Response model for close session endpoint"""
    success: bool
    message: str
    session_id: Optional[str] = None
    error: Optional[str] = None


class SessionInfoResponse(BaseModel):
    """Response model for session info"""
    session_id: Optional[str]
    is_active: bool
    is_logged_in: bool
    current_url: Optional[str]
    uptime: Optional[str] = None


class HealthCheckResponse(BaseModel):
    """Response model for health check endpoint"""
    status: str
    message: str
    timestamp: datetime
    version: str = "1.0.0"
    components: Dict[str, str]


class ErrorResponse(BaseModel):
    """Standard error response model"""
    success: bool = False
    error: str
    error_type: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)


# Additional utility models

class ProfileInfo(BaseModel):
    """Model for profile information"""
    name: str = "Unknown"
    headline: str = "Unknown"  
    location: str = "Unknown"
    profile_url: str


class ConnectionStatus(BaseModel):
    """Model for connection status information"""
    status: str  # connected, pending, not_connected, unknown
    can_message: bool
    can_connect: bool
    profile_url: str


class MessageCapability(BaseModel):
    """Model for messaging capability"""
    can_send_message: bool
    reason: str
    profile_url: str


# Response wrapper for consistent API responses
class ApiResponse(BaseModel):
    """Generic API response wrapper"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    error_type: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)