"""
Profile Handler Module - LinkedIn Profile Interactions

This module handles:
- Navigating to LinkedIn profiles
- Finding Connect buttons across different UI layouts
- Clicking Connect with human-like behavior
- Detecting connection status
- Handling UI variations and edge cases
"""

import time
import random
from typing import Dict, Optional, List, Tuple
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from linkedin_automation.utils.logger import get_logger
from linkedin_automation.utils.config import get_config

logger = get_logger(__name__)
config = get_config()


class ProfileHandler:
    """
    Handles LinkedIn profile interactions and connection requests
    
    This class manages:
    - Profile navigation and validation
    - Connect button detection across UI variations
    - Connection status checking
    - Error handling for profile-related operations
    """
    
    def __init__(self, browser_manager):
        """
        Initialize Profile Handler
        
        Args:
            browser_manager: BrowserManager instance for browser control
        """
        self.browser_manager = browser_manager
        
        # Multiple selector strategies for Connect buttons
        # LinkedIn uses different layouts for different users
        self.connect_selectors = {
            "primary_connect": [
                # Standard Connect button
                (By.CSS_SELECTOR, "button[aria-label*='Connect']"),
                (By.CSS_SELECTOR, "button[data-control-name='connect']"),
                (By.XPATH, "//button[contains(text(), 'Connect')]"),
                (By.XPATH, "//button[contains(@aria-label, 'Connect')]"),
                
                # Connect button variations
                (By.CSS_SELECTOR, ".pv-s-profile-actions button[data-control-name='connect']"),
                (By.CSS_SELECTOR, ".pv-top-card-v2-ctas button[aria-label*='Connect']"),
                (By.CSS_SELECTOR, ".pvs-profile-actions button[aria-label*='Connect']"),
            ],
            
            "dropdown_connect": [
                # Connect button inside "More" dropdown
                (By.CSS_SELECTOR, "button[aria-label*='More actions']"),
                (By.CSS_SELECTOR, "button[data-control-name='more-actions']"),
                (By.CSS_SELECTOR, ".pv-s-profile-actions__overflow-toggle"),
                (By.XPATH, "//button[contains(@aria-label, 'More')]"),
            ],
            
            "dropdown_connect_option": [
                # Connect option inside dropdown menu
                (By.XPATH, "//div[contains(@class, 'dropdown')]//button[contains(text(), 'Connect')]"),
                (By.CSS_SELECTOR, ".artdeco-dropdown__content button[aria-label*='Connect']"),
                (By.CSS_SELECTOR, "[role='menu'] button[data-control-name='connect']"),
            ]
        }
        
        # Selectors for checking connection status
        self.connection_status_selectors = {
            "connected": [
                (By.CSS_SELECTOR, "button[aria-label*='Message']"),
                (By.CSS_SELECTOR, "button[data-control-name='message']"),
                (By.XPATH, "//button[contains(text(), 'Message')]"),
                (By.CSS_SELECTOR, ".pv-s-profile-actions button[aria-label*='Message']"),
            ],
            
            "pending": [
                (By.CSS_SELECTOR, "button[aria-label*='Pending']"),
                (By.XPATH, "//button[contains(text(), 'Pending')]"),
                (By.CSS_SELECTOR, "button[data-control-name='pending']"),
            ],
            
            "follow": [
                (By.CSS_SELECTOR, "button[aria-label*='Follow']"),
                (By.XPATH, "//button[contains(text(), 'Follow')]"),
                (By.CSS_SELECTOR, "button[data-control-name='follow']"),
            ]
        }
    
    def navigate_to_profile(self, profile_url: str) -> Dict[str, any]:
        """
        Navigate to a LinkedIn profile and validate it loaded correctly
        
        Args:
            profile_url: Full LinkedIn profile URL
            
        Returns:
            Dict with navigation result and profile info
        """
        try:
            logger.info(f"Navigating to profile: {profile_url}")
            
            # Validate URL format
            if not self._is_valid_linkedin_profile_url(profile_url):
                return {
                    "success": False,
                    "error": "Invalid LinkedIn profile URL format",
                    "error_type": "invalid_url"
                }
            
            # Navigate to profile
            if not self.browser_manager.navigate_to(profile_url):
                return {
                    "success": False,
                    "error": "Failed to navigate to profile",
                    "error_type": "navigation_error"
                }
            
            # Wait for profile to load
            time.sleep(random.uniform(2, 4))
            
            # Validate we're on a profile page
            validation_result = self._validate_profile_page()
            if not validation_result["success"]:
                return validation_result
            
            # Extract basic profile info
            profile_info = self._extract_profile_info()
            
            logger.info("Successfully navigated to profile")
            return {
                "success": True,
                "message": "Profile loaded successfully",
                "profile_info": profile_info,
                "current_url": self.browser_manager.get_current_url()
            }
            
        except Exception as e:
            logger.error(f"Error navigating to profile: {str(e)}")
            return {
                "success": False,
                "error": f"Navigation error: {str(e)}",
                "error_type": "unexpected_error"
            }
    
    def send_connection_request(self, profile_url: str, note: str = None) -> Dict[str, any]:
        """
        Send connection request to a LinkedIn profile
        
        Args:
            profile_url: LinkedIn profile URL
            note: Optional connection note message
            
        Returns:
            Dict with connection request result
        """
        try:
            logger.info(f"Attempting to connect with profile: {profile_url}")
            
            # Navigate to profile if not already there
            current_url = self.browser_manager.get_current_url()
            if profile_url not in current_url:
                nav_result = self.navigate_to_profile(profile_url)
                if not nav_result["success"]:
                    return nav_result
            
            # Check current connection status
            status_result = self.check_connection_status(profile_url)
            if not status_result["success"]:
                return status_result
            
            connection_status = status_result["connection_status"]
            
            # Handle different connection states
            if connection_status == "connected":
                return {
                    "success": False,
                    "error": "Already connected to this profile",
                    "error_type": "already_connected",
                    "connection_status": "connected"
                }
            
            if connection_status == "pending":
                return {
                    "success": False,
                    "error": "Connection request already pending",
                    "error_type": "request_pending",
                    "connection_status": "pending"
                }
            
            # Try to find and click Connect button
            connect_result = self._find_and_click_connect_button()
            if not connect_result["success"]:
                return connect_result
            
            # Handle connection note dialog if it appears
            if note:
                note_result = self._handle_connection_note(note)
                if not note_result["success"]:
                    logger.warning(f"Failed to add note, but connection might still work: {note_result['error']}")
            
            # Confirm connection request
            confirm_result = self._confirm_connection_request()
            if not confirm_result["success"]:
                return confirm_result
            
            logger.info("Connection request sent successfully")
            return {
                "success": True,
                "message": "Connection request sent successfully",
                "had_note": note is not None,
                "profile_url": profile_url
            }
            
        except Exception as e:
            logger.error(f"Error sending connection request: {str(e)}")
            return {
                "success": False,
                "error": f"Connection request error: {str(e)}",
                "error_type": "unexpected_error"
            }
    
    def check_connection_status(self, profile_url: str) -> Dict[str, any]:
        """
        Check the current connection status with a profile
        
        Args:
            profile_url: LinkedIn profile URL
            
        Returns:
            Dict with connection status information
        """
        try:
            logger.debug(f"Checking connection status for: {profile_url}")
            
            # Ensure we're on the profile page
            current_url = self.browser_manager.get_current_url()
            if profile_url not in current_url:
                nav_result = self.navigate_to_profile(profile_url)
                if not nav_result["success"]:
                    return nav_result
            
            # Check for different connection states
            status = "unknown"
            
            # Check if connected (Message button present)
            if self._find_element_with_selectors(self.connection_status_selectors["connected"]):
                status = "connected"
            
            # Check if request is pending
            elif self._find_element_with_selectors(self.connection_status_selectors["pending"]):
                status = "pending"
            
            # Check if we can follow (not connected, no pending request)
            elif self._find_element_with_selectors(self.connection_status_selectors["follow"]):
                status = "not_connected"
            
            # Check if Connect button is available
            elif self._find_element_with_selectors(self.connect_selectors["primary_connect"]):
                status = "not_connected"
            
            # Check if Connect is in dropdown
            elif self._find_element_with_selectors(self.connect_selectors["dropdown_connect"]):
                status = "not_connected"
            
            logger.debug(f"Connection status determined: {status}")
            return {
                "success": True,
                "connection_status": status,
                "profile_url": profile_url
            }
            
        except Exception as e:
            logger.error(f"Error checking connection status: {str(e)}")
            return {
                "success": False,
                "error": f"Status check error: {str(e)}",
                "error_type": "status_check_error"
            }
    
    def _is_valid_linkedin_profile_url(self, url: str) -> bool:
        """Validate if URL is a proper LinkedIn profile URL"""
        linkedin_patterns = [
            "linkedin.com/in/",
            "www.linkedin.com/in/",
            "https://linkedin.com/in/",
            "https://www.linkedin.com/in/"
        ]
        return any(pattern in url.lower() for pattern in linkedin_patterns)
    
    def _validate_profile_page(self) -> Dict[str, any]:
        """Validate that we're on a valid LinkedIn profile page"""
        try:
            # Check for profile page indicators
            profile_indicators = [
                (By.CSS_SELECTOR, ".pv-top-card"),
                (By.CSS_SELECTOR, ".pv-text-details__left-panel"),
                (By.CSS_SELECTOR, "[data-section='topCard']"),
                (By.CSS_SELECTOR, ".ph5.pb5"),  # Profile container
                (By.XPATH, "//h1[contains(@class, 'text-heading-xlarge')]"),  # Name heading
            ]
            
            if self._find_element_with_selectors(profile_indicators):
                return {"success": True}
            
            # Check for error pages
            current_url = self.browser_manager.get_current_url()
            if "/authwall" in current_url:
                return {
                    "success": False,
                    "error": "LinkedIn authwall detected - login required",
                    "error_type": "auth_required"
                }
            
            if "/unavailable" in current_url:
                return {
                    "success": False,
                    "error": "Profile unavailable or doesn't exist",
                    "error_type": "profile_unavailable"
                }
            
            return {
                "success": False,
                "error": "Could not validate profile page",
                "error_type": "validation_failed"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Profile validation error: {str(e)}",
                "error_type": "validation_error"
            }
    
    def _extract_profile_info(self) -> Dict[str, str]:
        """Extract basic profile information"""
        profile_info = {
            "name": "Unknown",
            "headline": "Unknown",
            "location": "Unknown"
        }
        
        try:
            # Try to extract name
            name_selectors = [
                (By.CSS_SELECTOR, "h1.text-heading-xlarge"),
                (By.CSS_SELECTOR, ".pv-text-details__left-panel h1"),
                (By.CSS_SELECTOR, ".ph5 h1"),
            ]
            name_element = self._find_element_with_selectors(name_selectors)
            if name_element:
                name = self.browser_manager.driver.find_element(*name_element).text.strip()
                if name:
                    profile_info["name"] = name
            
            # Try to extract headline
            headline_selectors = [
                (By.CSS_SELECTOR, ".text-body-medium.break-words"),
                (By.CSS_SELECTOR, ".pv-text-details__left-panel .text-body-medium"),
            ]
            headline_element = self._find_element_with_selectors(headline_selectors)
            if headline_element:
                headline = self.browser_manager.driver.find_element(*headline_element).text.strip()
                if headline:
                    profile_info["headline"] = headline
            
        except Exception as e:
            logger.debug(f"Could not extract full profile info: {str(e)}")
        
        return profile_info
    
    def _find_element_with_selectors(self, selectors: List[Tuple], timeout: int = 3) -> Optional[Tuple]:
        """Find element using multiple selector strategies"""
        for selector in selectors:
            if self.browser_manager.smart_wait(selector, timeout=timeout):
                return selector
        return None
    
    def _find_and_click_connect_button(self) -> Dict[str, any]:
        """Find and click the Connect button using various strategies"""
        try:
            # Strategy 1: Look for direct Connect button
            connect_selector = self._find_element_with_selectors(
                self.connect_selectors["primary_connect"]
            )
            
            if connect_selector:
                if self.browser_manager.smart_click(connect_selector):
                    logger.debug("Clicked primary Connect button")
                    return {"success": True, "method": "primary_button"}
                else:
                    logger.warning("Found Connect button but failed to click")
            
            # Strategy 2: Look for Connect in dropdown menu
            dropdown_selector = self._find_element_with_selectors(
                self.connect_selectors["dropdown_connect"]
            )
            
            if dropdown_selector:
                # Click the dropdown/More button
                if self.browser_manager.smart_click(dropdown_selector):
                    logger.debug("Opened dropdown menu")
                    
                    # Wait for dropdown to appear
                    time.sleep(random.uniform(1, 2))
                    
                    # Look for Connect option in dropdown
                    dropdown_connect = self._find_element_with_selectors(
                        self.connect_selectors["dropdown_connect_option"]
                    )
                    
                    if dropdown_connect:
                        if self.browser_manager.smart_click(dropdown_connect):
                            logger.debug("Clicked Connect from dropdown")
                            return {"success": True, "method": "dropdown_button"}
            
            return {
                "success": False,
                "error": "Could not find Connect button in any location",
                "error_type": "connect_button_not_found"
            }
            
        except Exception as e:
            logger.error(f"Error finding Connect button: {str(e)}")
            return {
                "success": False,
                "error": f"Connect button error: {str(e)}",
                "error_type": "connect_button_error"
            }
    
    def _handle_connection_note(self, note: str) -> Dict[str, any]:
        """Handle adding a note to connection request"""
        try:
            # Look for note input field
            note_selectors = [
                (By.CSS_SELECTOR, "textarea[name='message']"),
                (By.CSS_SELECTOR, "#custom-message"),
                (By.CSS_SELECTOR, "textarea[placeholder*='Add a note']"),
                (By.XPATH, "//textarea[contains(@placeholder, 'note')]"),
            ]
            
            note_selector = self._find_element_with_selectors(note_selectors, timeout=5)
            if note_selector:
                if self.browser_manager.smart_type(note_selector, note):
                    logger.debug("Added connection note")
                    return {"success": True}
                else:
                    return {
                        "success": False,
                        "error": "Failed to type connection note",
                        "error_type": "note_input_error"
                    }
            else:
                logger.debug("No note input field found - sending without note")
                return {"success": True}  # Not an error if no note field
                
        except Exception as e:
            logger.warning(f"Error adding connection note: {str(e)}")
            return {
                "success": False,
                "error": f"Note error: {str(e)}",
                "error_type": "note_error"
            }
    
    def _confirm_connection_request(self) -> Dict[str, any]:
        """Confirm the connection request by clicking Send button"""
        try:
            # Look for Send/Submit button
            send_selectors = [
                (By.CSS_SELECTOR, "button[aria-label*='Send']"),
                (By.XPATH, "//button[contains(text(), 'Send')]"),
                (By.CSS_SELECTOR, "button[data-control-name='send-invite']"),
                (By.CSS_SELECTOR, ".artdeco-button--primary[type='submit']"),
            ]
            
            send_selector = self._find_element_with_selectors(send_selectors, timeout=10)
            if send_selector:
                if self.browser_manager.smart_click(send_selector):
                    logger.debug("Clicked Send button")
                    
                    # Wait for request to be processed
                    time.sleep(random.uniform(2, 3))
                    
                    return {"success": True}
                else:
                    return {
                        "success": False,
                        "error": "Failed to click Send button",
                        "error_type": "send_button_error"
                    }
            else:
                return {
                    "success": False,
                    "error": "Could not find Send button",
                    "error_type": "send_button_not_found"
                }
                
        except Exception as e:
            logger.error(f"Error confirming connection request: {str(e)}")
            return {
                "success": False,
                "error": f"Confirmation error: {str(e)}",
                "error_type": "confirmation_error"
            }