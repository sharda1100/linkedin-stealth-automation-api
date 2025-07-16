"""
LinkedIn Authentication Module

This module handles:
- LinkedIn login process
- Authentication validation
- Session management
- Login error handling
"""

import time
import random
from typing import Dict, Optional, Tuple
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from linkedin_automation.utils.logger import get_logger
from linkedin_automation.utils.config import get_config

logger = get_logger(__name__)
config = get_config()


class LinkedInAuth:
    """
    Handles LinkedIn authentication and login processes
    
    This class manages:
    - Login form interaction
    - Authentication validation
    - Error handling for login issues
    - Session persistence
    """
    
    def __init__(self, browser_manager):
        """
        Initialize LinkedIn authentication
        
        Args:
            browser_manager: BrowserManager instance
        """
        self.browser_manager = browser_manager
        self.login_url = config.get("LINKEDIN_LOGIN_URL")
        
        # Common selectors for LinkedIn login (multiple variations)
        self.login_selectors = {
            "email_input": [
                (By.ID, "username"),
                (By.NAME, "session_key"),
                (By.CSS_SELECTOR, "input[name='session_key']"),
                (By.CSS_SELECTOR, "input[autocomplete='username']")
            ],
            "password_input": [
                (By.ID, "password"),
                (By.NAME, "session_password"),
                (By.CSS_SELECTOR, "input[name='session_password']"),
                (By.CSS_SELECTOR, "input[type='password']")
            ],
            "login_button": [
                (By.CSS_SELECTOR, "button[type='submit']"),
                (By.CSS_SELECTOR, "button[data-id='sign-in-form__submit-btn']"),
                (By.CSS_SELECTOR, ".btn__primary--large"),
                (By.XPATH, "//button[contains(text(), 'Sign in')]"),
                (By.XPATH, "//button[contains(text(), 'Sign In')]")
            ],
            "captcha_challenge": [
                (By.CSS_SELECTOR, ".challenge-page"),
                (By.CSS_SELECTOR, ".captcha-challenge"),
                (By.ID, "captcha"),
                (By.CSS_SELECTOR, "[data-test-id='challenge-page']")
            ],
            "error_messages": [
                (By.CSS_SELECTOR, ".form__error--floating"),
                (By.CSS_SELECTOR, ".alert--error"),
                (By.CSS_SELECTOR, ".error-message"),
                (By.XPATH, "//*[contains(@class, 'error')]")
            ]
        }
    
    def login(self, username: str, password: str) -> Dict[str, any]:
        """
        Perform LinkedIn login
        
        Args:
            username: LinkedIn email/username
            password: LinkedIn password
            
        Returns:
            Dict with login result and details
        """
        try:
            logger.info("Starting LinkedIn login process...")
            
            # Navigate to login page
            if not self.browser_manager.navigate_to(self.login_url):
                return {
                    "success": False,
                    "error": "Failed to navigate to LinkedIn login page",
                    "error_type": "navigation_error"
                }
            
            # Wait for page to load
            time.sleep(random.uniform(2, 4))
            
            # Handle potential cookie banner
            self._handle_cookie_banner()
            
            # Fill login form
            form_result = self._fill_login_form(username, password)
            if not form_result["success"]:
                return form_result
            
            # Submit form
            submit_result = self._submit_login_form()
            if not submit_result["success"]:
                return submit_result
            
            # Wait for login completion and validate
            validation_result = self._validate_login()
            if validation_result["success"]:
                self.browser_manager.is_logged_in = True
                logger.info("LinkedIn login successful!")
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Unexpected error during login: {str(e)}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "error_type": "unexpected_error"
            }
    
    def _handle_cookie_banner(self):
        """Handle cookie consent banner if present"""
        try:
            cookie_selectors = [
                (By.CSS_SELECTOR, "button[action-type='ACCEPT']"),
                (By.XPATH, "//button[contains(text(), 'Accept')]"),
                (By.XPATH, "//button[contains(text(), 'Allow')]"),
                (By.CSS_SELECTOR, ".cookie-consent button")
            ]
            
            for selector in cookie_selectors:
                if self.browser_manager.smart_wait(selector, timeout=3):
                    self.browser_manager.smart_click(selector)
                    logger.debug("Cookie banner handled")
                    break
                    
        except Exception as e:
            logger.debug(f"No cookie banner found or failed to handle: {str(e)}")
    
    def _find_element_with_selectors(self, selectors: list, timeout: int = 10) -> Optional[tuple]:
        """
        Find element using multiple selector strategies
        
        Args:
            selectors: List of (By.METHOD, selector) tuples
            timeout: Maximum time to wait
            
        Returns:
            Tuple of (By.METHOD, selector) if found, None otherwise
        """
        for selector in selectors:
            if self.browser_manager.smart_wait(selector, timeout=2):
                return selector
        return None
    
    def _fill_login_form(self, username: str, password: str) -> Dict[str, any]:
        """
        Fill the login form with credentials
        
        Args:
            username: LinkedIn email/username
            password: LinkedIn password
            
        Returns:
            Dict with operation result
        """
        try:
            # Find and fill email field
            email_selector = self._find_element_with_selectors(
                self.login_selectors["email_input"]
            )
            if not email_selector:
                return {
                    "success": False,
                    "error": "Could not find email input field",
                    "error_type": "element_not_found"
                }
            
            if not self.browser_manager.smart_type(email_selector, username):
                return {
                    "success": False,
                    "error": "Failed to enter username",
                    "error_type": "input_error"
                }
            
            logger.debug("Username entered successfully")
            
            # Find and fill password field
            password_selector = self._find_element_with_selectors(
                self.login_selectors["password_input"]
            )
            if not password_selector:
                return {
                    "success": False,
                    "error": "Could not find password input field",
                    "error_type": "element_not_found"
                }
            
            if not self.browser_manager.smart_type(password_selector, password):
                return {
                    "success": False,
                    "error": "Failed to enter password",
                    "error_type": "input_error"
                }
            
            logger.debug("Password entered successfully")
            
            return {"success": True}
            
        except Exception as e:
            logger.error(f"Error filling login form: {str(e)}")
            return {
                "success": False,
                "error": f"Form filling error: {str(e)}",
                "error_type": "form_error"
            }
    
    def _submit_login_form(self) -> Dict[str, any]:
        """
        Submit the login form
        
        Returns:
            Dict with operation result
        """
        try:
            # Find and click login button
            login_button_selector = self._find_element_with_selectors(
                self.login_selectors["login_button"]
            )
            if not login_button_selector:
                return {
                    "success": False,
                    "error": "Could not find login button",
                    "error_type": "element_not_found"
                }
            
            if not self.browser_manager.smart_click(login_button_selector):
                return {
                    "success": False,
                    "error": "Failed to click login button",
                    "error_type": "click_error"
                }
            
            logger.debug("Login form submitted")
            
            # Wait for page transition
            time.sleep(random.uniform(3, 5))
            
            return {"success": True}
            
        except Exception as e:
            logger.error(f"Error submitting login form: {str(e)}")
            return {
                "success": False,
                "error": f"Form submission error: {str(e)}",
                "error_type": "submission_error"
            }
    
    def _validate_login(self) -> Dict[str, any]:
        """
        Validate if login was successful
        
        Returns:
            Dict with validation result
        """
        try:
            # Wait for page to load after login
            time.sleep(3)
            
            # Check for CAPTCHA challenge
            captcha_selector = self._find_element_with_selectors(
                self.login_selectors["captcha_challenge"], timeout=3
            )
            if captcha_selector:
                return {
                    "success": False,
                    "error": "CAPTCHA challenge detected. Manual intervention required.",
                    "error_type": "captcha_challenge",
                    "requires_manual_action": True
                }
            
            # Check for error messages
            error_selector = self._find_element_with_selectors(
                self.login_selectors["error_messages"], timeout=3
            )
            if error_selector:
                try:
                    error_element = self.browser_manager.driver.find_element(*error_selector)
                    error_text = error_element.text
                    return {
                        "success": False,
                        "error": f"Login error: {error_text}",
                        "error_type": "authentication_error"
                    }
                except:
                    return {
                        "success": False,
                        "error": "Authentication failed with unknown error",
                        "error_type": "authentication_error"
                    }
            
            # Check if we're redirected to feed or profile (success indicators)
            current_url = self.browser_manager.get_current_url()
            success_indicators = [
                "/feed/",
                "/in/",
                "/mynetwork/",
                "/messaging/",
                "/notifications/"
            ]
            
            if any(indicator in current_url for indicator in success_indicators):
                return {
                    "success": True,
                    "message": "Login successful",
                    "current_url": current_url
                }
            
            # Additional check: Look for LinkedIn navigation elements
            nav_selectors = [
                (By.CSS_SELECTOR, "nav.global-nav"),
                (By.CSS_SELECTOR, ".global-nav__nav"),
                (By.CSS_SELECTOR, "[data-test-global-nav]"),
                (By.XPATH, "//nav[contains(@class, 'global-nav')]")
            ]
            
            nav_found = self._find_element_with_selectors(nav_selectors, timeout=5)
            if nav_found:
                return {
                    "success": True,
                    "message": "Login successful - navigation found",
                    "current_url": current_url
                }
            
            # If we're still on login page, login likely failed
            if "/login" in current_url or "/challenge" in current_url:
                return {
                    "success": False,
                    "error": "Still on login page. Check credentials.",
                    "error_type": "authentication_error"
                }
            
            # Default success if no errors found and not on login page
            return {
                "success": True,
                "message": "Login appears successful",
                "current_url": current_url
            }
            
        except Exception as e:
            logger.error(f"Error validating login: {str(e)}")
            return {
                "success": False,
                "error": f"Login validation error: {str(e)}",
                "error_type": "validation_error"
            }
    
    def is_logged_in(self) -> bool:
        """
        Check if currently logged into LinkedIn
        
        Returns:
            bool: True if logged in, False otherwise
        """
        try:
            if not self.browser_manager.is_browser_active():
                return False
            
            current_url = self.browser_manager.get_current_url()
            
            # Simple check - if we're not on login page and have nav elements
            if "/login" in current_url:
                return False
            
            # Look for navigation elements that indicate logged-in state
            nav_selectors = [
                (By.CSS_SELECTOR, "nav.global-nav"),
                (By.CSS_SELECTOR, ".global-nav__nav"),
                (By.CSS_SELECTOR, "[data-test-global-nav]")
            ]
            
            nav_found = self._find_element_with_selectors(nav_selectors, timeout=3)
            return nav_found is not None
            
        except Exception as e:
            logger.debug(f"Error checking login status: {str(e)}")
            return False
    
    def logout(self) -> Dict[str, any]:
        """
        Logout from LinkedIn
        
        Returns:
            Dict with logout result
        """
        try:
            logger.info("Logging out of LinkedIn...")
            
            # Navigate to logout URL or use profile menu
            logout_url = f"{config.get('LINKEDIN_BASE_URL')}/m/logout/"
            if self.browser_manager.navigate_to(logout_url):
                time.sleep(2)
                self.browser_manager.is_logged_in = False
                return {"success": True, "message": "Logged out successfully"}
            
            return {"success": False, "error": "Failed to logout"}
            
        except Exception as e:
            logger.error(f"Error during logout: {str(e)}")
            return {"success": False, "error": f"Logout error: {str(e)}"}
