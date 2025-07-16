"""
Message Handler Module - LinkedIn Messaging Functionality

This module handles:
- Opening LinkedIn message interface
- Sending messages to connected users
- Detecting message capabilities
- Handling different messaging UI layouts
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


class MessageHandler:
    """
    Handles LinkedIn messaging functionality
    
    This class manages:
    - Message interface detection and navigation
    - Sending messages to connected profiles
    - Handling different messaging UI variations
    - Error handling for messaging operations
    """
    
    def __init__(self, browser_manager):
        """
        Initialize Message Handler
        
        Args:
            browser_manager: BrowserManager instance for browser control
        """
        self.browser_manager = browser_manager
        
        # Selectors for finding Message buttons on profiles
        self.message_button_selectors = [
            # Standard Message button on profile
            (By.CSS_SELECTOR, "button[aria-label*='Message']"),
            (By.CSS_SELECTOR, "button[data-control-name='message']"),
            (By.XPATH, "//button[contains(text(), 'Message')]"),
            (By.CSS_SELECTOR, ".pv-s-profile-actions button[aria-label*='Message']"),
            
            # Message button variations
            (By.CSS_SELECTOR, ".pv-top-card-v2-ctas button[aria-label*='Message']"),
            (By.CSS_SELECTOR, ".pvs-profile-actions button[aria-label*='Message']"),
            (By.CSS_SELECTOR, "a[data-control-name='message']"),
        ]
        
        # Selectors for the message compose interface
        self.message_compose_selectors = {
            "message_input": [
                (By.CSS_SELECTOR, "div[data-placeholder='Write a message...']"),
                (By.CSS_SELECTOR, ".msg-form__contenteditable"),
                (By.CSS_SELECTOR, "[data-placeholder*='message']"),
                (By.CSS_SELECTOR, "div[role='textbox']"),
                (By.XPATH, "//div[@contenteditable='true']"),
            ],
            
            "send_button": [
                (By.CSS_SELECTOR, "button[data-control-name='send']"),
                (By.CSS_SELECTOR, "button[type='submit'][aria-label*='Send']"),
                (By.XPATH, "//button[contains(@aria-label, 'Send')]"),
                (By.CSS_SELECTOR, ".msg-form__send-button"),
                (By.CSS_SELECTOR, "button.artdeco-button--primary"),
            ],
            
            "message_thread": [
                (By.CSS_SELECTOR, ".msg-thread"),
                (By.CSS_SELECTOR, ".msg-conversation-card"),
                (By.CSS_SELECTOR, "[data-control-name='overlay_conversation_thread']"),
            ]
        }
        
        # Selectors for detecting if messaging is available
        self.messaging_indicators = [
            (By.CSS_SELECTOR, ".msg-overlay-conversation-bubble"),
            (By.CSS_SELECTOR, ".messaging-thread-header"),
            (By.CSS_SELECTOR, "[data-test-id='messaging-thread']"),
        ]
    
    def can_send_message(self, profile_url: str) -> Dict[str, any]:
        """
        Check if we can send a message to this profile (i.e., if we're connected)
        
        Args:
            profile_url: LinkedIn profile URL
            
        Returns:
            Dict with messaging capability status
        """
        try:
            logger.debug(f"Checking messaging capability for: {profile_url}")
            
            # Ensure we're on the profile page
            current_url = self.browser_manager.get_current_url()
            if profile_url not in current_url:
                # Navigate to profile first
                if not self.browser_manager.navigate_to(profile_url):
                    return {
                        "success": False,
                        "error": "Failed to navigate to profile",
                        "error_type": "navigation_error"
                    }
                
                # Wait for page to load
                time.sleep(random.uniform(2, 3))
            
            # Look for Message button
            message_button = self._find_element_with_selectors(
                self.message_button_selectors, timeout=5
            )
            
            if message_button:
                return {
                    "success": True,
                    "can_message": True,
                    "message": "Message button found - user is connected",
                    "profile_url": profile_url
                }
            else:
                return {
                    "success": True,
                    "can_message": False,
                    "message": "No Message button found - user might not be connected",
                    "profile_url": profile_url
                }
                
        except Exception as e:
            logger.error(f"Error checking messaging capability: {str(e)}")
            return {
                "success": False,
                "error": f"Messaging check error: {str(e)}",
                "error_type": "messaging_check_error"
            }
    
    def send_message(self, profile_url: str, message: str) -> Dict[str, any]:
        """
        Send a message to a LinkedIn profile
        
        Args:
            profile_url: LinkedIn profile URL
            message: Message text to send
            
        Returns:
            Dict with message sending result
        """
        try:
            logger.info(f"Attempting to send message to profile: {profile_url}")
            
            # First check if we can message this profile
            capability_check = self.can_send_message(profile_url)
            if not capability_check["success"]:
                return capability_check
            
            if not capability_check["can_message"]:
                return {
                    "success": False,
                    "error": "Cannot send message - not connected to this profile",
                    "error_type": "not_connected",
                    "profile_url": profile_url
                }
            
            # Open message interface
            message_interface_result = self._open_message_interface()
            if not message_interface_result["success"]:
                return message_interface_result
            
            # Type the message
            type_result = self._type_message(message)
            if not type_result["success"]:
                return type_result
            
            # Send the message
            send_result = self._send_message()
            if not send_result["success"]:
                return send_result
            
            logger.info("Message sent successfully")
            return {
                "success": True,
                "message": "Message sent successfully",
                "profile_url": profile_url,
                "message_text": message
            }
            
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            return {
                "success": False,
                "error": f"Message sending error: {str(e)}",
                "error_type": "unexpected_error"
            }
    
    def _open_message_interface(self) -> Dict[str, any]:
        """Open the LinkedIn message interface"""
        try:
            logger.debug("Opening message interface...")
            
            # Find and click the Message button
            message_button = self._find_element_with_selectors(
                self.message_button_selectors, timeout=10
            )
            
            if not message_button:
                return {
                    "success": False,
                    "error": "Could not find Message button",
                    "error_type": "message_button_not_found"
                }
            
            # Click the Message button
            if not self.browser_manager.smart_click(message_button):
                return {
                    "success": False,
                    "error": "Failed to click Message button",
                    "error_type": "message_button_click_error"
                }
            
            logger.debug("Clicked Message button")
            
            # Wait for message interface to load
            time.sleep(random.uniform(2, 4))
            
            # Verify message interface opened
            message_thread = self._find_element_with_selectors(
                self.message_compose_selectors["message_thread"], timeout=10
            )
            
            if message_thread:
                logger.debug("Message interface opened successfully")
                return {"success": True}
            else:
                # Sometimes the interface takes longer to load
                time.sleep(random.uniform(2, 3))
                message_thread = self._find_element_with_selectors(
                    self.message_compose_selectors["message_thread"], timeout=5
                )
                
                if message_thread:
                    logger.debug("Message interface opened after additional wait")
                    return {"success": True}
                else:
                    return {
                        "success": False,
                        "error": "Message interface did not open properly",
                        "error_type": "interface_not_loaded"
                    }
                
        except Exception as e:
            logger.error(f"Error opening message interface: {str(e)}")
            return {
                "success": False,
                "error": f"Interface opening error: {str(e)}",
                "error_type": "interface_error"
            }
    
    def _type_message(self, message: str) -> Dict[str, any]:
        """Type message in the message input field"""
        try:
            logger.debug("Typing message...")
            
            # Find message input field
            input_selector = self._find_element_with_selectors(
                self.message_compose_selectors["message_input"], timeout=10
            )
            
            if not input_selector:
                return {
                    "success": False,
                    "error": "Could not find message input field",
                    "error_type": "input_field_not_found"
                }
            
            # Click to focus on input field
            if not self.browser_manager.smart_click(input_selector):
                return {
                    "success": False,
                    "error": "Failed to click message input field",
                    "error_type": "input_click_error"
                }
            
            # Wait a moment for field to focus
            time.sleep(random.uniform(0.5, 1.0))
            
            # Type the message with human-like behavior
            if self._type_message_with_realistic_behavior(input_selector, message):
                logger.debug("Message typed successfully")
                return {"success": True}
            else:
                return {
                    "success": False,
                    "error": "Failed to type message",
                    "error_type": "typing_error"
                }
                
        except Exception as e:
            logger.error(f"Error typing message: {str(e)}")
            return {
                "success": False,
                "error": f"Message typing error: {str(e)}",
                "error_type": "typing_error"
            }
    
    def _type_message_with_realistic_behavior(self, selector: tuple, message: str) -> bool:
        """Type message with realistic human-like behavior"""
        try:
            element = self.browser_manager.driver.find_element(*selector)
            
            # Clear any existing content
            element.clear()
            time.sleep(random.uniform(0.2, 0.5))
            
            # Type message character by character with realistic delays
            for i, char in enumerate(message):
                element.send_keys(char)
                
                # Variable typing speed - faster for common words, slower for complex parts
                if char == ' ':
                    # Slightly longer pause at spaces (word boundaries)
                    time.sleep(random.uniform(0.1, 0.3))
                elif char in '.,!?':
                    # Pause at punctuation
                    time.sleep(random.uniform(0.2, 0.4))
                else:
                    # Normal character typing
                    time.sleep(random.uniform(0.05, 0.15))
                
                # Occasional longer pauses (like thinking)
                if i > 0 and i % random.randint(10, 20) == 0:
                    time.sleep(random.uniform(0.5, 1.5))
            
            # Final pause after typing
            time.sleep(random.uniform(0.5, 1.0))
            
            return True
            
        except Exception as e:
            logger.error(f"Error in realistic typing: {str(e)}")
            return False
    
    def _send_message(self) -> Dict[str, any]:
        """Send the typed message"""
        try:
            logger.debug("Sending message...")
            
            # Find Send button
            send_button = self._find_element_with_selectors(
                self.message_compose_selectors["send_button"], timeout=10
            )
            
            if not send_button:
                return {
                    "success": False,
                    "error": "Could not find Send button",
                    "error_type": "send_button_not_found"
                }
            
            # Click Send button
            if not self.browser_manager.smart_click(send_button):
                return {
                    "success": False,
                    "error": "Failed to click Send button",
                    "error_type": "send_button_click_error"
                }
            
            logger.debug("Clicked Send button")
            
            # Wait for message to be sent
            time.sleep(random.uniform(2, 4))
            
            # Verify message was sent (optional - message input should be cleared)
            try:
                input_element = self.browser_manager.driver.find_element(
                    *self.message_compose_selectors["message_input"][0]
                )
                if input_element.text.strip() == "":
                    logger.debug("Message input cleared - message likely sent")
            except:
                # If we can't verify, that's okay - just continue
                pass
            
            return {"success": True}
            
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            return {
                "success": False,
                "error": f"Message send error: {str(e)}",
                "error_type": "send_error"
            }
    
    def _find_element_with_selectors(self, selectors: List[Tuple], timeout: int = 3) -> Optional[Tuple]:
        """Find element using multiple selector strategies"""
        for selector in selectors:
            if self.browser_manager.smart_wait(selector, timeout=timeout):
                return selector
        return None
    
    def close_message_interface(self) -> Dict[str, any]:
        """Close the message interface/overlay"""
        try:
            logger.debug("Closing message interface...")
            
            # Look for close buttons
            close_selectors = [
                (By.CSS_SELECTOR, "button[aria-label*='Close']"),
                (By.CSS_SELECTOR, ".msg-overlay-conversation-bubble__controls button"),
                (By.CSS_SELECTOR, "[data-control-name='overlay.close_conversation_window']"),
                (By.XPATH, "//button[contains(@aria-label, 'Close')]"),
            ]
            
            close_button = self._find_element_with_selectors(close_selectors, timeout=5)
            
            if close_button:
                if self.browser_manager.smart_click(close_button):
                    logger.debug("Message interface closed")
                    time.sleep(random.uniform(1, 2))
                    return {"success": True}
                else:
                    return {
                        "success": False,
                        "error": "Failed to click close button",
                        "error_type": "close_click_error"
                    }
            else:
                # If no close button found, try pressing Escape key
                try:
                    from selenium.webdriver.common.keys import Keys
                    self.browser_manager.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                    time.sleep(random.uniform(1, 2))
                    logger.debug("Pressed Escape to close message interface")
                    return {"success": True}
                except:
                    return {
                        "success": False,
                        "error": "Could not close message interface",
                        "error_type": "close_failed"
                    }
                
        except Exception as e:
            logger.error(f"Error closing message interface: {str(e)}")
            return {
                "success": False,
                "error": f"Close error: {str(e)}",
                "error_type": "close_error"
            }