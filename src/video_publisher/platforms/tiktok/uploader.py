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
        
        try:
            # Navigate to upload page (EN)
            self.driver.get('https://www.tiktok.com/upload?lang=en')
            self._human_delay(2, 4)
            
            # Find and interact with file input
            try:
                # Find the file input - standard timeout
                file_input = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
                )
            except TimeoutException:
                 return UploadResult(
                    platform=Platform.TIKTOK,
                    success=False,
                    error="Timeout waiting for upload area"
                )
            
            # Upload file
            file_input.send_keys(str(Path(video_path).absolute()))
            self._human_delay(3, 5)
            
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
                        
                        # Type caption
                        for char in caption:
                            caption_input.send_keys(char)
                            time.sleep(random.uniform(0.05, 0.15))
                        self._human_delay()
                    else:
                        print("Could not find caption input field")
                except Exception as e:
                    print(f"Could not add caption: {e}")
            
            # Handle Thumbnail Upload
            thumbnail_path = metadata.get('thumbnail_path')
            if thumbnail_path and os.path.exists(thumbnail_path):
                print(f"Uploading thumbnail: {thumbnail_path}")
                try:
                    # 1. Click "Edit cover" (Strict English)
                    try:
                        edit_cover_btn = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Edit cover')]"))
                        )
                        edit_cover_btn.click()
                        self._human_delay(1, 2)
                        
                        # 2. Click "Upload cover" (Strict English)
                        upload_tab_btn = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Upload cover')]"))
                        )
                        upload_tab_btn.click()
                        self._human_delay(1, 2)
                        
                        # 3. Upload file
                        cover_file_input = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, "//input[@type='file' and @accept='image/*']"))
                        )
                        cover_file_input.send_keys(str(Path(thumbnail_path).absolute()))
                        self._human_delay(3, 5) # Process image
                        
                        # 4. Click Confirm / Close / X
                        # Look for "Confirm" button (Strict English)
                        try:
                            confirm_btn = WebDriverWait(self.driver, 5).until(
                                EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Confirm')]"))
                            )
                            confirm_btn.click()
                        except:
                            print("Confirm button not found, trying Close icon")
                            # Fallback to close icon if Confirm doesn't exist
                            close_btn = WebDriverWait(self.driver, 3).until(
                                EC.element_to_be_clickable((By.XPATH, "//*[name()='svg' and contains(@class, 'close')]/ancestor::div[1]"))
                            )
                            close_btn.click()
                            
                        self._human_delay(2, 3) 
                        
                        # Wait for modal to disappear completely
                        try:
                            WebDriverWait(self.driver, 5).until(
                                EC.invisibility_of_element_located((By.CLASS_NAME, "TUXModal-overlay"))
                            )
                        except:
                            print("Warning: Modal might still be visible")
                            
                    except Exception as e:
                        print(f"Thumbnail upload logic failed: {e}")
                        # Ensure we try to close any open modal
                        try:
                            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
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
                                time_input = WebDriverWait(self.driver, 5).until(
                                    EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='text'][readonly][value*=':']"))
                                )
                                time_input.click()
                                self._human_delay(0.5, 1)
                                
                                hour = dt.strftime('%H')
                                hour_option = WebDriverWait(self.driver, 5).until(
                                    EC.element_to_be_clickable((By.XPATH, f"//span[contains(@class, 'tiktok-timepicker-left') and text()='{hour}']"))
                                )
                                hour_option.click()
                                self._human_delay(0.3, 0.6)
                                
                                minute = (dt.minute // 5) * 5
                                minute_str = f"{minute:02d}"
                                minute_option = WebDriverWait(self.driver, 5).until(
                                    EC.element_to_be_clickable((By.XPATH, f"//span[contains(@class, 'tiktok-timepicker-right') and text()='{minute_str}']"))
                                )
                                minute_option.click()
                                self._human_delay(0.5, 1)
                            except Exception as e:
                                print(f"Failed to set time: {e}")
                            
                            # Set DATE
                            try:
                                date_input = WebDriverWait(self.driver, 5).until(
                                    EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='text'][readonly][value*='-']"))
                                )
                                date_input.click()
                                self._human_delay(0.5, 1)
                                
                                day_number = str(dt.day)
                                day_element = WebDriverWait(self.driver, 3).until(
                                    EC.element_to_be_clickable((By.XPATH, f"//span[contains(@class, 'day') and contains(@class, 'valid') and text()='{day_number}']"))
                                )
                                day_element.click()
                                self._human_delay(0.5, 1)
                            except Exception as e:
                                print(f"Failed to set date: {e}")
                    
                except Exception as e:
                    print(f"Failed to switch to schedule mode: {e}")

            # Click post button
            try:
                # English Strict Selectors
                post_button = None
                
                # Check for "Post" or "Schedule" button texts
                xpath_selectors = [
                    "//button[contains(., 'Post')]",
                    "//button[div[text()='Post']]",
                    "//button[contains(., 'Schedule')]",
                    "//button[div[text()='Schedule']]"
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
                    
                    if os.environ.get('DRY_RUN', 'false').lower() == 'true':
                        print("[DRY RUN] Skipping actual post click")
                        return UploadResult(platform=Platform.TIKTOK, success=True, url="DRY RUN")
                    
                    # Ensure button is clickable by waiting for overlay to disappear
                    try:
                        post_button.click()
                    except Exception as e:
                         # Retry logic often helps with "element click intercepted"
                         print(f"Click intercepted? Retrying via JS... {e}")
                         self.driver.execute_script("arguments[0].click();", post_button)
                         
                    self._human_delay(2, 4)
                    
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
