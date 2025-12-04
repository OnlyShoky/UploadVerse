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
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import undetected_chromedriver as uc

from ..base import BasePlatform
from ...core.models import UploadResult, Platform

class InstagramUploader(BasePlatform):
    """
    Instagram uploader using stealth browser automation for Reels.
    """
    
    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self.username = self.config.get('username', '')
        self.password = self.config.get('password', '')
        self.cookies_file = self.config.get('cookies_file', 'data/sessions/instagram_session.pkl')
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
                    try:
                        self.driver.add_cookie(cookie)
                    except:
                        pass  # Some cookies might fail, that's ok
    
    def authenticate(self) -> None:
        """
        Authenticate with Instagram.
        Uses credentials if provided, otherwise loads cookies or prompts for manual login.
        """
        if not self.driver:
            self._init_driver()
        
        # Navigate to Instagram
        self.driver.get('https://www.instagram.com')
        self._human_delay(2, 4)
        
        # Try to load existing cookies
        self._load_cookies()
        self.driver.refresh()
        self._human_delay(2, 4)
        
        # Check if logged in
        if self._is_logged_in():
            print("Already authenticated with Instagram")
            return
        
        # Try to log in with credentials
        if self.username and self.password:
            try:
                username_input = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.NAME, "username"))
                )
                password_input = self.driver.find_element(By.NAME, "password")
                
                # Enter credentials with human-like typing
                for char in self.username:
                    username_input.send_keys(char)
                    time.sleep(random.uniform(0.1, 0.3))
                
                self._human_delay()
                
                for char in self.password:
                    password_input.send_keys(char)
                    time.sleep(random.uniform(0.1, 0.3))
                
                self._human_delay()
                
                # Click login button
                login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
                login_button.click()
                
                # Wait for login to complete
                time.sleep(5)
                
                if self._is_logged_in():
                    print("Login successful!")
                    self._save_cookies()
                    return
                else:
                    print("Login might have failed. Check for 2FA or other prompts.")
                    
            except Exception as e:
                print(f"Automated login failed: {e}")
        
        # Manual login fallback
        print("Please log in manually in the browser window.")
        print("Waiting for manual login... (120 seconds timeout)")
        
        try:
            WebDriverWait(self.driver, 120).until(
                lambda d: self._is_logged_in()
            )
            print("Login successful!")
            self._save_cookies()
        except TimeoutException:
            raise Exception("Login timeout. Please try again.")
    
    def _is_logged_in(self) -> bool:
        """Check if currently logged in to Instagram."""
        try:
            # Look for create post button or similar authenticated element
            self.driver.find_element(By.XPATH, "//a[contains(@href, '/direct/')]")
            return True
        except:
            return False
    
    def is_authenticated(self) -> bool:
        """Check if authenticated with Instagram."""
        if not self.driver:
            return False
        return self._is_logged_in()
    
    def upload(self, video_path: str, metadata: dict) -> UploadResult:
        """
        Upload a video to Instagram Reels/Feed.
        
        Args:
            video_path: Path to the video file.
            metadata: Dictionary with keys:
                - title: Video title (used as caption on Instagram)
                - description: Video description (appended to caption)
                - tags: List of tags (converted to hashtags)
        
        Returns:
            UploadResult object.
        """
        if not self.is_authenticated():
            self.authenticate()
        
        try:
            # Navigate to Instagram homepage
            self.driver.get('https://www.instagram.com')
            self._human_delay(2, 4)
            
            # Dismiss any popup dialogs (e.g., "New inbox look" notification)
            try:
                accept_button = WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and text()='Aceptar']"))
                )
                accept_button.click()
                print("Dismissed popup dialog")
                self._human_delay(1, 2)
            except:
                # No popup, continue
                pass
            
            # Also try English version
            try:
                accept_button = WebDriverWait(self.driver, 1).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and text()='Accept']"))
                )
                accept_button.click()
                print("Dismissed popup dialog")
                self._human_delay(1, 2)
            except:
                # No popup, continue
                pass
            
            # Click Create button
            print("Clicking Create button...")
            try:
                # Try Spanish first
                try:
                    create_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//span[text()='Crear']/ancestor::a"))
                    )
                    create_button.click()
                    self._human_delay(1, 2)
                except:
                    # Try English
                    create_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//span[text()='Create']/ancestor::a"))
                    )
                    create_button.click()
                    self._human_delay(1, 2)
            except Exception as e:
                print(f"Could not find Create button: {e}")
                return UploadResult(
                    platform=Platform.INSTAGRAM,
                    success=False,
                    error=f"Failed to find Create button: {e}"
                )
            
            # Click "Publicación" (Post) option
            print("Clicking 'Publicación' option...")
            try:
                # Try Spanish
                try:
                    post_option = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//span[text()='Publicación']/ancestor::a"))
                    )
                    post_option.click()
                    self._human_delay(1, 2)
                except:
                    # Try English "Post"
                    post_option = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//span[text()='Post']/ancestor::a"))
                    )
                    post_option.click()
                    self._human_delay(1, 2)
            except Exception as e:
                print(f"Could not find Post option: {e}")
            
            # Click "Select from computer"
            print("Clicking 'Select from computer'...")
            try:
                # Try Spanish
                try:
                    select_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[text()='Seleccionar desde la computadora']"))
                    )
                    select_button.click()
                    self._human_delay(0.5, 1)
                except:
                    # Try English
                    select_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[text()='Select from computer']"))
                    )
                    select_button.click()
                    self._human_delay(0.5, 1)
            except Exception as e:
                print(f"Could not find 'Select from computer' button: {e}")
            
            # Find and interact with file input
            print("Uploading file...")
            try:
                file_input = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
                )
                file_input.send_keys(str(Path(video_path).absolute()))
                self._human_delay(3, 5)
            except Exception as e:
                return UploadResult(
                    platform=Platform.INSTAGRAM,
                    success=False,
                    error=f"Failed to upload file: {e}"
                )
            
            # Dismiss Reels notification dialog if it appears
            try:
                # Try Spanish "Aceptar" button
                accept_reels = WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Aceptar') and @type='button']"))
                )
                accept_reels.click()
                print("Dismissed Reels notification dialog")
                self._human_delay(1, 2)
            except:
                # Try English "OK" or "Accept"
                try:
                    accept_reels = WebDriverWait(self.driver, 1).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'OK') or contains(text(), 'Accept') and @type='button']"))
                    )
                    accept_reels.click()
                    print("Dismissed Reels notification dialog")
                    self._human_delay(1, 2)
                except:
                    pass
            
            # Wait for video to process
            print("Waiting for video to process...")
            time.sleep(5)
            
            # Wait for "Recortar" (Crop) dialog to appear
            print("Waiting for crop dialog...")
            try:
                crop_dialog = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@role='dialog' and (@aria-label='Recortar' or @aria-label='Crop')]"))
                )
                print("Crop dialog opened")
                self._human_delay(1, 2)
                
                # Click "Select crop" button inside the dialog
                print("Clicking 'Select crop' button...")
                crop_clicked = False
                
                try:
                    # Strategy: Find all buttons in the dialog, excluding Back and Next buttons
                    all_buttons = self.driver.find_elements(By.XPATH, "//div[@role='dialog' and (@aria-label='Recortar' or @aria-label='Crop')]//button[@type='button']")
                    
                    print(f"Found {len(all_buttons)} buttons in crop dialog")
                    
                    for idx, button in enumerate(all_buttons):
                        try:
                            # Get button text and check if it contains Back/Next/Siguiente/Atrás
                            button_text = button.text.strip().lower()
                            
                            # Skip navigation buttons
                            if any(skip_word in button_text for skip_word in ['siguiente', 'next', 'atrás', 'back']):
                                print(f"Button {idx}: Skipping navigation button: {button_text}")
                                continue
                            
                            # Skip if button is too large (navigation buttons are larger)
                            size = button.size
                            if size['width'] > 100 or size['height'] > 50:
                                print(f"Button {idx}: Skipping large button ({size['width']}x{size['height']})")
                                continue
                            
                            # This should be the crop button - try to click it
                            print(f"Button {idx}: Attempting to click small button ({size['width']}x{size['height']})")
                            
                            # Scroll into view
                            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                            self._human_delay(0.5, 1)
                            
                            # Try click
                            try:
                                button.click()
                            except:
                                self.driver.execute_script("arguments[0].click();", button)
                            
                            print(f"Successfully clicked button {idx}")
                            crop_clicked = True
                            self._human_delay(1, 2)
                            break
                            
                        except Exception as e:
                            print(f"Button {idx}: Failed - {e}")
                            continue
                    
                except Exception as e:
                    print(f"Failed to find buttons in dialog: {e}")
                
                if not crop_clicked:
                    print("Crop button not found (may not be needed for this video)")
                    
            except Exception as e:
                print(f"Crop dialog not found or error: {e}")
            
            # Select "Original" dimension (only if crop was clicked)
            if crop_clicked:
                print("Selecting 'Original' dimension...")
                try:
                    # Wait a bit longer for the crop menu to fully open
                    self._human_delay(1, 2)
                    
                    # Try multiple selectors for "Original" button
                    original_selectors = [
                        # Spanish "Original"
                        "//span[text()='Original']/parent::div[@role='button']",
                        "//div[@role='button']//span[text()='Original']",
                        "//div[contains(@class, 'x1i10hfl')]//span[text()='Original']",
                        
                        # Try by looking for the photo icon SVG near "Original" text
                        "//span[text()='Original']/ancestor::div[contains(@class, 'x1i10hfl')]",
                        
                        # Fallback: any clickable element with "Original" text
                        "//*[text()='Original']/ancestor::*[@role='button']",
                    ]
                    
                    original_clicked = False
                    for selector in original_selectors:
                        try:
                            original_button = WebDriverWait(self.driver, 5).until(
                                EC.element_to_be_clickable((By.XPATH, selector))
                            )
                            original_button.click()
                            print(f"Selected 'Original' dimension using selector: {selector}")
                            original_clicked = True
                            self._human_delay(0.5, 1)
                            break
                        except Exception as e:
                            continue
                    
                    if not original_clicked:
                        print("Could not find 'Original' option - may already be selected or not needed")
                        
                except Exception as e:
                    print(f"Could not select 'Original' dimension: {e}")
            
            # Click Next button
            print("Clicking Next...")
            try:
                next_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and .//text()='Siguiente']"))
                )
                next_button.click()
                self._human_delay(2, 3)
            except Exception as e:
                print(f"Could not find first Next button: {e}")
            
            # Click Next button again (filters/editing page)
            print("Clicking Next again...")
            try:
                next_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and .//text()='Siguiente']"))
                )
                next_button.click()
                self._human_delay(2, 3)
            except Exception as e:
                print(f"Could not find second Next button: {e}")
            
            # Add caption/description with hashtags
            caption = metadata.get('title') or metadata.get('description') or metadata.get('caption', '')
            tags = metadata.get('tags', [])
            
            if tags:
                formatted_tags = " ".join([f"#{tag.strip().replace(' ', '_')}" for tag in tags if tag.strip()])
                if caption:
                    caption += f" {formatted_tags}"
                else:
                    caption = formatted_tags
            
            if caption:
                print("Adding caption...")
                try:
                    # Click caption area first - try Spanish then English
                    caption_area = None
                    try:
                        caption_area = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Escribe un pie de foto o vídeo…']"))
                        )
                    except:
                        caption_area = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Write a caption...']"))
                        )
                    
                    caption_area.click()
                    self._human_delay(0.5, 1)
                    
                    # Type caption character by character
                    for char in caption:
                        caption_area.send_keys(char)
                        time.sleep(random.uniform(0.05, 0.15))
                    self._human_delay()
                    
                except Exception as e:
                    print(f"Could not add caption: {e}")
            
            # Check for DRY_RUN or TEST_MODE
            if os.environ.get('DRY_RUN', 'false').lower() == 'true' or os.environ.get('TEST_MODE', 'false').lower() == 'true':
                print("[DRY RUN] Skipping actual post click")
                return UploadResult(
                    platform=Platform.INSTAGRAM,
                    success=True,
                    url="https://www.instagram.com/ (DRY RUN)"
                )
            
            # Click Post button
            print("Clicking Post...")
            try:
                # Try Spanish "Compartir" (Share) first
                try:
                    post_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and text()='Compartir']"))
                    )
                    # Scroll into view
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", post_button)
                    self._human_delay(0.5, 1)
                    post_button.click()
                    self._human_delay(3, 5)
                except:
                    # Try English "Post" or "Share"
                    try:
                        post_button = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and text()='Post']"))
                        )
                    except:
                        post_button = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and text()='Share']"))
                        )
                    
                    # Scroll into view
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", post_button)
                    self._human_delay(0.5, 1)
                    post_button.click()
                    self._human_delay(3, 5)
                
                # Wait for upload confirmation
                print("Waiting for upload confirmation...")
                time.sleep(5)
                
                return UploadResult(
                    platform=Platform.INSTAGRAM,
                    success=True,
                    url="https://www.instagram.com/"
                )
            except Exception as e:
                return UploadResult(
                    platform=Platform.INSTAGRAM,
                    success=False,
                    error=f"Failed to click post button: {e}"
                )
                
        except Exception as e:
            return UploadResult(
                platform=Platform.INSTAGRAM,
                success=False,
                error=str(e)
            )
    
    def __del__(self):
        """Clean up driver on deletion."""
        if self.driver:
            self.driver.quit()
