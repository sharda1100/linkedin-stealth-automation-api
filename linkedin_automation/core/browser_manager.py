"""
Browser Manager - Stealth Browser Session Management

This module handles:
- Creating stealth-enabled browser instances
- Managing browser sessions across API requests
- Anti-detection techniques
- Browser configuration and options
"""

import os
import time
import random
from typing import Optional, Dict, Any
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import undetected_chromedriver as uc
from selenium_stealth import stealth
from webdriver_manager.chrome import ChromeDriverManager
from linkedin_automation.utils.logger import get_logger
from linkedin_automation.utils.config import get_config

logger = get_logger(__name__)
config = get_config()


class BrowserManager:
    """
    Manages stealth browser sessions for LinkedIn automation
    
    This class creates and manages Chrome browser instances with:
    - Anti-detection features
    - Session persistence
    - Smart waiting strategies
    - Error handling
    """
    
    def __init__(self):
        self.driver: Optional[webdriver.Chrome] = None
        self.session_id: Optional[str] = None
        self.is_logged_in: bool = False
        self.current_url: str = ""
        
    def create_stealth_browser(self) -> webdriver.Chrome:
        """
        Create a stealth-enabled Chrome browser instance
        
        Returns:
            webdriver.Chrome: Configured Chrome driver with stealth features
        """
        try:
            logger.info("Creating stealth browser instance...")
            
            # Use undetected-chromedriver for better stealth
            options = uc.ChromeOptions()
            
            # Basic stealth options
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Mimic real user behavior
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-plugins-discovery")
            options.add_argument("--disable-web-security")
            options.add_argument("--allow-running-insecure-content")
            
            # Set realistic window size
            options.add_argument("--window-size=1366,768")
            
            # User agent to appear as regular Chrome browser
            options.add_argument(
                "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            # Headless mode (if configured)
            if config.get("HEADLESS_MODE", "False").lower() == "true":
                options.add_argument("--headless")
                logger.info("Running in headless mode")
            
            # Create browser with undetected-chromedriver
            self.driver = uc.Chrome(options=options, version_main=None)
            
            # Additional stealth configuration using selenium-stealth
            stealth(
                self.driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
            )
            
            # Set timeouts
            self.driver.implicitly_wait(config.get("IMPLICIT_WAIT", 10))
            self.driver.set_page_load_timeout(config.get("BROWSER_TIMEOUT", 30))
            
            # Execute additional stealth scripts
            self._execute_stealth_scripts()
            
            # Generate session ID
            self.session_id = f"session_{int(time.time())}_{random.randint(1000, 9999)}"
            
            logger.info(f"Stealth browser created successfully. Session ID: {self.session_id}")
            return self.driver
            
        except Exception as e:
            logger.error(f"Failed to create stealth browser: {str(e)}")
            raise WebDriverException(f"Browser creation failed: {str(e)}")
    
    def _execute_stealth_scripts(self):
        """Execute additional JavaScript to enhance stealth capabilities"""
        try:
            # Remove webdriver property
            self.driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )
            
            # Override the plugins property
            self.driver.execute_script(
                """
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                """
            )
            
            # Override the languages property
            self.driver.execute_script(
                """
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
                """
            )
            
            logger.debug("Stealth scripts executed successfully")
            
        except Exception as e:
            logger.warning(f"Some stealth scripts failed to execute: {str(e)}")
    
    def smart_wait(self, locator: tuple, timeout: int = 10, poll_frequency: float = 0.5) -> bool:
        """
        Smart waiting strategy that mimics human behavior
        
        Args:
            locator: Tuple of (By.METHOD, "selector")
            timeout: Maximum time to wait
            poll_frequency: How often to check
            
        Returns:
            bool: True if element found, False otherwise
        """
        try:
            # Add random delay to mimic human behavior
            time.sleep(random.uniform(0.5, 1.5))
            
            wait = WebDriverWait(self.driver, timeout, poll_frequency)
            element = wait.until(EC.presence_of_element_located(locator))
            
            # Additional random delay
            time.sleep(random.uniform(0.3, 0.8))
            
            return element is not None
            
        except TimeoutException:
            logger.debug(f"Element not found with locator: {locator}")
            return False
    
    def smart_click(self, locator: tuple, timeout: int = 10) -> bool:
        """
        Click element with human-like behavior
        
        Args:
            locator: Tuple of (By.METHOD, "selector")
            timeout: Maximum time to wait
            
        Returns:
            bool: True if clicked successfully, False otherwise
        """
        try:
            if self.smart_wait(locator, timeout):
                element = self.driver.find_element(*locator)
                
                # Scroll element into view
                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                time.sleep(random.uniform(0.5, 1.0))
                
                # Wait for element to be clickable
                wait = WebDriverWait(self.driver, timeout)
                clickable_element = wait.until(EC.element_to_be_clickable(locator))
                
                # Human-like delay before clicking
                time.sleep(random.uniform(0.3, 0.7))
                
                clickable_element.click()
                
                # Post-click delay
                time.sleep(random.uniform(0.5, 1.2))
                
                logger.debug(f"Successfully clicked element: {locator}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to click element {locator}: {str(e)}")
            return False
    
    def smart_type(self, locator: tuple, text: str, timeout: int = 10) -> bool:
        """
        Type text with human-like behavior
        
        Args:
            locator: Tuple of (By.METHOD, "selector")
            text: Text to type
            timeout: Maximum time to wait
            
        Returns:
            bool: True if typed successfully, False otherwise
        """
        try:
            if self.smart_wait(locator, timeout):
                element = self.driver.find_element(*locator)
                
                # Clear existing text
                element.clear()
                time.sleep(random.uniform(0.2, 0.5))
                
                # Type with human-like delays
                for char in text:
                    element.send_keys(char)
                    time.sleep(random.uniform(0.05, 0.15))
                
                # Final delay
                time.sleep(random.uniform(0.3, 0.6))
                
                logger.debug(f"Successfully typed text into element: {locator}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to type into element {locator}: {str(e)}")
            return False
    
    def navigate_to(self, url: str) -> bool:
        """
        Navigate to URL with error handling
        
        Args:
            url: URL to navigate to
            
        Returns:
            bool: True if navigation successful, False otherwise
        """
        try:
            logger.info(f"Navigating to: {url}")
            self.driver.get(url)
            self.current_url = url
            
            # Wait for page to load
            time.sleep(random.uniform(2, 4))
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to navigate to {url}: {str(e)}")
            return False
    
    def get_current_url(self) -> str:
        """Get current page URL"""
        try:
            return self.driver.current_url
        except:
            return self.current_url
    
    def is_browser_active(self) -> bool:
        """Check if browser session is still active"""
        try:
            if self.driver is None:
                return False
            
            # Try to get current URL to test if browser is responsive
            _ = self.driver.current_url
            return True
            
        except:
            return False
    
    def close_browser(self):
        """Safely close browser and cleanup resources"""
        try:
            if self.driver:
                logger.info(f"Closing browser session: {self.session_id}")
                self.driver.quit()
                self.driver = None
                self.session_id = None
                self.is_logged_in = False
                logger.info("Browser session closed successfully")
                
        except Exception as e:
            logger.error(f"Error closing browser: {str(e)}")
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get current session information"""
        return {
            "session_id": self.session_id,
            "is_active": self.is_browser_active(),
            "is_logged_in": self.is_logged_in,
            "current_url": self.get_current_url()
        }


# Global browser manager instance
browser_manager = BrowserManager()
