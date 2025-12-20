import os
import time
import random
import pickle
from pathlib import Path
from typing import Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import undetected_chromedriver as uc

from ..base import BasePlatform
from ...core.models import UploadResult, Platform

class TikTokUploader(BasePlatform):
    """
    TikTok uploader using stealth browser automation.
    """
    
    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self.cookies_file = self.config.get('cookies_file', 'data/sessions/tiktok_session.pkl')
        self.headless = self.config.get('headless', False)
        
        # Ensure sessions directory exists
        cookie_path = Path(self.cookies_file)
        if not cookie_path.parent.exists():
            cookie_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.driver = None
        
    def _init_driver(self):
        """Initialize undetected Chrome driver."""
        options = uc.ChromeOptions()
        if self.headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        # Force English Language
        options.add_argument('--lang=en-US')
        options.add_argument('--accept-lang=en-US')
        
        # Set preferences for language
        prefs = {
            "intl.accept_languages": "en-US,en",
            "profile.default_content_settings.popups": 0
        }
        options.add_experimental_option("prefs", prefs)
        
        self.driver = uc.Chrome(options=options, version_main=142)
        
    def _human_delay(self, min_seconds=1, max_seconds=3):
        """Simulate human-like delay."""
        time.sleep(random.uniform(min_seconds, max_seconds))
    
    def _save_cookies(self):
        """Save cookies for session persistence."""
        if self.driver:
            cookies = self.driver.get_cookies()
            with open(self.cookies_file, 'wb') as f:
                pickle.dump(cookies, f)
    
    def _load_cookies(self):
        """Load cookies from file."""
        if os.path.exists(self.cookies_file) and self.driver:
            with open(self.cookies_file, 'rb') as f:
                cookies = pickle.load(f)
                for cookie in cookies:
                    self.driver.add_cookie(cookie)
    
    def authenticate(self) -> None:
        """
        Authenticate with TikTok.
        Opens browser for manual login if no valid session exists.
        """
        if not self.driver:
            self._init_driver()
        
        # Navigate to TikTok
        self.driver.get('https://www.tiktok.com/en/') # Force EN URL
        self._human_delay(2, 4)
        
        # Try to load existing cookies
        self._load_cookies()
        self.driver.refresh()
        self._human_delay(2, 4)
        
        # Check if logged in by verifying no login button exists and profile is accessible
        def is_logged_in(driver):
            try:
                # English only checks
                if driver.find_elements(By.XPATH, "//button[contains(., 'Log in')]"):
                    return False
                if driver.find_elements(By.XPATH, "//a[contains(., 'Log in')]"):
                    return False
                if driver.find_elements(By.ID, "header-login-button"):
                    return False
                    
                # Must find profile link/icon to be sure
                return bool(driver.find_elements(By.XPATH, "//a[contains(@href, '/@')]"))
            except:
                return False

        if is_logged_in(self.driver):
            print("Already authenticated with TikTok")
            return

        print("Not authenticated. Please log in manually in the browser window.")
        print("Waiting for manual login... (120 seconds timeout)")
        
        # Wait for user to log in manually
        try:
            WebDriverWait(self.driver, 120).until(is_logged_in)
            print("Login successful!")
            # Wait a bit more for cookies to settle
            time.sleep(3)
            self._save_cookies()
        except TimeoutException:
            raise Exception("Login timeout. Please try again.")
    
    def is_authenticated(self) -> bool:
        """Check if authenticated with TikTok."""
        if not self.driver:
            return False
        
        try:
            # English only checks
            if self.driver.find_elements(By.XPATH, "//button[contains(., 'Log in')]"):
                return False
            if self.driver.find_elements(By.XPATH, "//a[contains(., 'Log in')]"):
                return False
                
            # Look for link to own profile
            return bool(self.driver.find_elements(By.XPATH, "//a[contains(@href, '/@')]"))
        except:
            return False
    
    def upload(self, video_path: str, metadata: dict) -> UploadResult:
        """
        Upload a video to TikTok.
        """
        if not self.is_authenticated():
            self.authenticate()
        
        # Maximize for better element targeting
        try:
            self.driver.maximize_window()
        except:
            pass

        try:
            # Navigate to upload page (EN)
            self.driver.get('https://www.tiktok.com/upload?lang=en')
            print("Navigating to TikTok upload page...")
            self._human_delay(5, 8)
            
            # Find and interact with file input
            try:
                # First ensure "Select video" button or specific text is present to confirm page load
                try:
                    WebDriverWait(self.driver, 15).until(
                        EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Select video to upload')]"))
                    )
                except:
                    print("Warning: 'Select video' text not found, proceeding anyway...")

                # Find the file input - increased timeout for slow loads
                file_input = WebDriverWait(self.driver, 60).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
                )
            except TimeoutException:
                 return UploadResult(
                    platform=Platform.TIKTOK,
                    success=False,
                    error="Timeout waiting for upload area (file input not found after 60s)"
                )
            
            # Upload file
            file_input.send_keys(str(Path(video_path).absolute()))
            self._human_delay(5, 8)
            
            # Wait for video to process
            print("Waiting for video to process...")
            time.sleep(10)
            
            # Add caption (TikTok uses 'description' as caption)
            caption = metadata.get('title') or metadata.get('description')
            tags = metadata.get('tags', '')

            if tags:
                formatted_tags = " ".join([f"#{tag.strip().replace(' ', '_')}" for tag in tags if tag.strip()])
                if caption:
                    caption += f" {formatted_tags}"
                else:
                    caption = formatted_tags
            
            if caption:
                try:
                    # Try multiple selectors for caption input
                    caption_input = None
                    selectors = [
                        ".public-DraftEditor-content",
                        "div[contenteditable='true']",
                        "div[data-contents='true']"
                    ]
                    
                    for selector in selectors:
                        try:
                            caption_input = WebDriverWait(self.driver, 5).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                            )
                            break
                        except:
                            continue
                            
                    if caption_input:
                        caption_input.click()
                        self._human_delay()
                        # Clear existing text
                        caption_input.send_keys(Keys.CONTROL + "a")
                        caption_input.send_keys(Keys.DELETE)
                        self._human_delay(0.5, 1)
                        
                        # Type caption using clipboard paste for React/Draft.js compatibility
                        # This properly triggers React's synthetic events
                        self.driver.execute_script("""
                            // Copy text to clipboard
                            navigator.clipboard.writeText(arguments[1]).then(function() {
                                // Focus the element
                                arguments[0].focus();
                            });
                        """, caption_input, caption)
                        self._human_delay(0.5, 1)
                        
                        # Paste from clipboard using keyboard shortcut
                        caption_input.send_keys(Keys.CONTROL + "v")
                        self._human_delay(1, 2)
                        
                        # Fallback: if paste didn't work, try character-by-character
                        # but escape special characters first
                        current_text = caption_input.text.strip() if hasattr(caption_input, 'text') else ''
                        if not current_text:
                            print("Clipboard paste may have failed, trying direct input...")
                            # Type each character, escaping special Selenium keys
                            for char in caption:
                                if char in '[]{}':
                                    # These can cause issues, use JS to insert
                                    self.driver.execute_script(
                                        "arguments[0].textContent += arguments[1];",
                                        caption_input, char
                                    )
                                else:
                                    caption_input.send_keys(char)
                                time.sleep(random.uniform(0.02, 0.08))
                            # Trigger input event
                            self.driver.execute_script("""
                                arguments[0].dispatchEvent(new Event('input', {bubbles: true}));
                                arguments[0].dispatchEvent(new Event('change', {bubbles: true}));
                            """, caption_input)
                        
                        self._human_delay(1, 2)
                        
                        # Dismiss any hashtag/mention suggestion popups by clicking elsewhere
                        try:
                            self.driver.execute_script("document.body.click();")
                            self._human_delay(0.5, 1)
                        except:
                            pass
                    else:
                        print("Could not find caption input field")
                except Exception as e:
                    print(f"Could not add caption: {e}")
            
            # Handle Thumbnail Upload
            thumbnail_path = metadata.get('thumbnail_path')
            if thumbnail_path and os.path.exists(thumbnail_path):
                print(f"Uploading thumbnail: {thumbnail_path}")
                try:
                    # 1. Click "Edit cover"
                    try:
                        # User provided class: edit-container
                        edit_cover_btn = WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, ".edit-container"))
                        )
                        self.driver.execute_script("arguments[0].click();", edit_cover_btn)
                        self._human_delay(2, 3)
                        
                        # 2. Click "Upload cover" tab
                        # User provided class: cover-edit-tab
                        upload_tab_btn = WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'cover-edit-tab') and contains(., 'Upload cover')]"))
                        )
                        self.driver.execute_script("arguments[0].click();", upload_tab_btn)
                        self._human_delay(2, 3)
                        
                        # 3. Wait for the upload area to signal tab switch
                        # User provided class: upload-image-upload-area
                        upload_area = WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, ".upload-image-upload-area"))
                        )
                        print("Upload cover tab active")
                        
                        # 4. Find the file input within the modal/upload area
                        # There's usually a hidden input inside or near the upload area
                        try:
                            cover_file_input = self.driver.find_element(By.XPATH, "//div[contains(@class, 'upload-image-upload-area')]//input[@type='file']")
                        except:
                            # Fallback to any image file input if specific one not found
                            cover_file_input = WebDriverWait(self.driver, 5).until(
                                EC.presence_of_element_located((By.XPATH, "//input[@type='file' and contains(@accept, 'image')]"))
                            )
                            
                        cover_file_input.send_keys(str(Path(thumbnail_path).absolute()))
                        print("Thumbnail file sent, waiting for processing (12-15s)...")
                        self._human_delay(12, 15)
                        
                        # 5. Wait for image preview to appear (confirms image is loaded)
                        try:
                            WebDriverWait(self.driver, 15).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, ".upload-image-cover-viewer-container"))
                            )
                            print("Image preview loaded")
                        except:
                            print("Warning: Image preview not detected, proceeding anyway")
                        
                        # 6. Click Confirm button
                        # IMPORTANT: There are TWO cover-edit-footer elements!
                        # - First one: in jsx-623769667 (for "Select cover" tab) - WRONG
                        # - Second one: in jsx-2328539565 (for "Upload cover" tab) - CORRECT
                        # The correct one has "Upload new" button as sibling to "Confirm"
                        print("Looking for Confirm button in Upload cover footer...")
                        
                        confirm_selectors = [
                            # Working selector: button next to "Upload new" button
                            "//button[.//div[text()='Upload new']]/following-sibling::button[contains(@class, 'TUXButton--primary')]"
                        ]
                        
                        
                        clicked_confirm = False
                        try:
                            print("Looking for Confirm button...")
                            btn = WebDriverWait(self.driver, 10).until(
                                EC.presence_of_element_located((By.XPATH, confirm_selectors[0]))
                            )
                            
                            if not btn.is_displayed():
                                print("Confirm button found but not visible")
                            else:
                                print("Found visible Confirm button")
                                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                                self._human_delay(0.5, 1)
                                
                                # Check if disabled
                                if btn.get_attribute("aria-disabled") == "true":
                                    print("Button disabled, waiting 5s...")
                                    self._human_delay(5, 6)
                                
                                # Try standard click, fallback to JS
                                try:
                                    btn.click()
                                    print("✓ Clicked via standard click")
                                    clicked_confirm = True
                                except Exception as e:
                                    print(f"Standard click failed, trying JS: {e}")
                                    self.driver.execute_script("arguments[0].click();", btn)
                                    print("✓ Clicked via JS")
                                    clicked_confirm = True
                                    
                                self._human_delay(2, 3)
                        except Exception as e:
                            print(f"Confirm button failed: {str(e)[:50]}")
                            
                        self._human_delay(2, 3) 
                        
                        # Ensure modal is gone
                        try:
                            WebDriverWait(self.driver, 10).until(
                                EC.invisibility_of_element_located((By.CLASS_NAME, "TUXModal-overlay"))
                            )
                            print("Modal successfully closed")
                        except:
                            print("Modal still visible, forcing ESC")
                            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
                            self._human_delay(1, 2)
                                
                    except Exception as e:
                        print(f"Thumbnail upload sequence failed: {e}")
                        try:
                            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
                            self._human_delay(1, 2)
                        except:
                            pass
                except Exception as e:
                    print(f"Failed to upload thumbnail: {e}")
            
            # Handle scheduling
            scheduling = metadata.get('scheduling', {})
            publish_now = scheduling.get('publish_now', True)
            
            if not publish_now:
                print("Switching to Schedule mode...")
                try:
                    # Click Schedule radio button
                    schedule_radio = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "input[value='schedule']"))
                    )
                    self.driver.execute_script("arguments[0].click();", schedule_radio)
                    self._human_delay()
                    
                    # Handle date/time selection if scheduled_time is provided
                    scheduled_time = scheduling.get('scheduled_time')
                    if scheduled_time:
                        from datetime import datetime
                        try:
                            dt = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
                        except:
                            print(f"Warning: Could not parse scheduled_time: {scheduled_time}")
                            dt = None
                        
                        if dt:
                            print(f"Setting scheduled time to: {dt}")
                            
                            # Set TIME
                            try:
                                # Ensure no overlays are blocking
                                try:
                                    WebDriverWait(self.driver, 5).until(
                                        EC.invisibility_of_element_located((By.CLASS_NAME, "TUXModal-overlay"))
                                    )
                                except:
                                    pass

                                time_input = WebDriverWait(self.driver, 5).until(
                                    EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='text'][readonly][value*=':']"))
                                )
                                try:
                                    time_input.click()
                                except:
                                    self.driver.execute_script("arguments[0].click();", time_input)
                                    
                                self._human_delay(1, 2)
                                
                                hour = dt.strftime('%H')
                                minute = (dt.minute // 5) * 5
                                minute_str = f"{minute:02d}"
                                
                                # Find hour option using exact TikTok class names
                                # The element exists but may be hidden by scroll container
                                hour_selector = f"//span[contains(@class, 'tiktok-timepicker-left') and text()='{hour}']"
                                
                                try:
                                    hour_option = self.driver.find_element(By.XPATH, hour_selector)
                                    # Scroll the parent container to bring element into view
                                    self.driver.execute_script("""
                                        var el = arguments[0];
                                        var container = el.closest('.tiktok-timepicker-time-scroll-container');
                                        if (container) {
                                            container.scrollTop = el.offsetTop - container.offsetHeight / 2;
                                        }
                                    """, hour_option)
                                    self._human_delay(0.5, 1)
                                    self.driver.execute_script("arguments[0].click();", hour_option)
                                    print(f"Selected hour: {hour}")
                                except Exception as e:
                                    print(f"Warning: Could not find/click hour {hour}: {e}")
                                    
                                self._human_delay(0.5, 1)
                                
                                # Find minute option using exact TikTok class names
                                minute_selector = f"//span[contains(@class, 'tiktok-timepicker-right') and text()='{minute_str}']"
                                
                                try:
                                    minute_option = self.driver.find_element(By.XPATH, minute_selector)
                                    # Scroll the parent container to bring element into view
                                    self.driver.execute_script("""
                                        var el = arguments[0];
                                        var container = el.closest('.tiktok-timepicker-time-scroll-container');
                                        if (container) {
                                            container.scrollTop = el.offsetTop - container.offsetHeight / 2;
                                        }
                                    """, minute_option)
                                    self._human_delay(0.5, 1)
                                    self.driver.execute_script("arguments[0].click();", minute_option)
                                    print(f"Selected minute: {minute_str}")
                                except Exception as e:
                                    print(f"Warning: Could not find/click minute {minute_str}: {e}")
                                    
                                self._human_delay(0.5, 1)
                            except Exception as e:
                                print(f"Failed to set time: {e}")
                            
                            # Set DATE
                            try:
                                date_input = WebDriverWait(self.driver, 5).until(
                                    EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='text'][readonly][value*='-']"))
                                )
                                try:
                                    date_input.click()
                                except:
                                    self.driver.execute_script("arguments[0].click();", date_input)
                                    
                                self._human_delay(0.5, 1)
                                
                                day_number = str(dt.day)
                                day_element = WebDriverWait(self.driver, 3).until(
                                    EC.element_to_be_clickable((By.XPATH, f"//span[contains(@class, 'day') and contains(@class, 'valid') and text()='{day_number}']"))
                                )
                                try:
                                    day_element.click()
                                except:
                                    self.driver.execute_script("arguments[0].click();", day_element)
                                    
                                self._human_delay(0.5, 1)
                            except Exception as e:
                                print(f"Failed to set date: {e}")
                    
                except Exception as e:
                    print(f"Failed to switch to schedule mode: {e}")

            # Click post button
            try:
                # English Strict Selectors
                post_button = None
                
                # Check for "Post" or "Schedule" button using data-e2e attribute first (most reliable)
                # When scheduling is enabled, the button text changes from "Post" to "Schedule"
                xpath_selectors = [
                    "//button[@data-e2e='post_video_button']",
                    "//button[.//div[text()='Schedule']]",
                    "//button[.//div[text()='Post']]",
                    "//button[contains(@class, 'Button__root--type-primary')]"
                ]
                
                for xpath in xpath_selectors:
                    try:
                        post_button = WebDriverWait(self.driver, 2).until(
                            EC.element_to_be_clickable((By.XPATH, xpath))
                        )
                        break
                    except:
                        continue
                
                if not post_button:
                     # Fallback to CSS
                     try:
                        post_button = WebDriverWait(self.driver, 2).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-e2e='post_video_button']"))
                        )
                     except:
                        pass

                if post_button:
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", post_button)
                    self._human_delay()
                    
                    if os.environ.get('DRY_RUN', 'false').lower() == 'true' or os.environ.get('TEST_MODE', 'false').lower() == 'true':
                        print("[DRY RUN / TEST MODE] Skipping actual post/schedule click")
                        return UploadResult(platform=Platform.TIKTOK, success=True, url="DRY RUN")
                    
                    # Ensure button is clickable by waiting for overlay to disappear
                    try:
                        post_button.click()
                    except Exception as e:
                         # Retry logic often helps with "element click intercepted"
                         print(f"Click intercepted? Retrying via JS... {e}")
                         self.driver.execute_script("arguments[0].click();", post_button)
                         
                    self._human_delay(2, 4)

                    # Handle "Continue to post?" modal if it appears
                    try:
                        print("Checking for 'Continue to post?' modal...")
                        post_now_btn = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[.//div[text()='Post now']]"))
                        )
                        print("Detected 'Continue to post?' modal. Clicking 'Post now'...")
                        self.driver.execute_script("arguments[0].click();", post_now_btn)
                        self._human_delay(1, 2)
                    except TimeoutException:
                        # No modal appeared, which is normal in most cases
                        pass
                    except Exception as e:
                        print(f"Error handling 'Continue to post?' modal: {e}")
                    
                    time.sleep(5)
                    
                    return UploadResult(
                        platform=Platform.TIKTOK,
                        success=True,
                        url="https://www.tiktok.com/@your_profile"
                    )
                else:
                    return UploadResult(
                        platform=Platform.TIKTOK,
                        success=False,
                        error="Could not find Post/Schedule button"
                    )
            except Exception as e:
                return UploadResult(
                    platform=Platform.TIKTOK,
                    success=False,
                    error=f"Failed to click post button: {e}"
                )
        except Exception as e:
            return UploadResult(
                platform=Platform.TIKTOK,
                success=False,
                error=str(e)
            )
                
        except Exception as e:
            return UploadResult(
                platform=Platform.TIKTOK,
                success=False,
                error=str(e)
            )
    
    def __del__(self):
        """Clean up driver on deletion."""
        if self.driver:
            self.driver.quit()
