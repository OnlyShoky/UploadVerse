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
        # Mobile user agent for better Reels support
        options.add_argument('--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15')
        
        self.driver = uc.Chrome(options=options)
        
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
        print("Waiting for manual login... (60 seconds timeout)")
        
        try:
            WebDriverWait(self.driver, 60).until(
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
        Upload a video to Instagram Reels.
        
        Args:
            video_path: Path to the video file.
            metadata: Dictionary with keys:
                - caption: Post caption
                - share_to_feed: Boolean (default: True)
        
        Returns:
            UploadResult object.
        """
        if not self.is_authenticated():
            self.authenticate()
        
        try:
            # Navigate to create page
            self.driver.get('https://www.instagram.com/create/story')
            self._human_delay(2, 4)
            
            # Check for CAPTCHA or challenges
            if 'challenge' in self.driver.current_url or 'checkpoint' in self.driver.current_url:
                return UploadResult(
                    platform=Platform.INSTAGRAM,
                    success=False,
                    error="Challenge/verification required. Please complete manually."
                )
            
            # Find file input
            try:
                file_input = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
                )
                
                # Upload file
                file_input.send_keys(str(Path(video_path).absolute()))
                self._human_delay(3, 5)
                
            except:
                # Alternative: try clicking "Create" button first
                create_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/create/')]"))
                )
                create_button.click()
                self._human_delay()
                
                file_input = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
                )
                file_input.send_keys(str(Path(video_path).absolute()))
                self._human_delay(3, 5)
            
            # Wait for processing
            print("Waiting for video to process...")
            time.sleep(10)
            
            # Click Next button(s)
            try:
                for _ in range(2):  # Usually need to click Next twice
                    next_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[text()='Next']"))
                    )
                    next_button.click()
                    self._human_delay(2, 3)
            except:
                print("Could not find Next button, continuing...")
            
            # Add caption
            caption = metadata.get('caption', '')
            if caption:
                try:
                    caption_input = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[aria-label*='caption']"))
                    )
                    caption_input.click()
                    self._human_delay()
                    caption_input.send_keys(caption)
                    self._human_delay()
                except:
                    print("Could not add caption")
            
            # Click Share button
            try:
                share_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[text()='Share']"))
                )
                share_button.click()
                self._human_delay(3, 5)
                
                # Wait for upload confirmation
                time.sleep(5)
                
                return UploadResult(
                    platform=Platform.INSTAGRAM,
                    success=True,
                    url="https://www.instagram.com/"  # Instagram doesn't give direct URL immediately
                )
            except:
                return UploadResult(
                    platform=Platform.INSTAGRAM,
                    success=False,
                    error="Failed to click share button"
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
