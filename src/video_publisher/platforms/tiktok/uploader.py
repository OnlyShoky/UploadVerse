import os
import time
import random
import pickle
from pathlib import Path
from typing import Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
        self.driver.get('https://www.tiktok.com')
        self._human_delay(2, 4)
        
        # Try to load existing cookies
        self._load_cookies()
        self.driver.refresh()
        self._human_delay(2, 4)
        
        # Check if logged in by verifying no login button exists and profile is accessible
        def is_logged_in(driver):
            try:
                # If login buttons are present, we are definitely NOT logged in
                if driver.find_elements(By.XPATH, "//button[contains(., 'Log in')]"):
                    return False
                if driver.find_elements(By.XPATH, "//a[contains(., 'Log in')]"):
                    return False
                if driver.find_elements(By.ID, "header-login-button"):
                    return False
                    
                # Must find profile link/icon to be sure
                # Using a more specific check for the avatar container if possible, 
                # but sticking to the profile link as a positive signal combined with the negative signal above
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
            # If login buttons are present, we are definitely NOT logged in
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
        
        Args:
            video_path: Path to the video file.
            metadata: Dictionary with keys:
                - caption: Video caption/description
                - allow_comments: Boolean (default: True)
                - allow_duet: Boolean (default: True)
                - allow_stitch: Boolean (default: True)
        
        Returns:
            UploadResult object.
        """
        if not self.is_authenticated():
            self.authenticate()
        
        try:
            # Navigate to upload page
            self.driver.get('https://www.tiktok.com/upload')
            self._human_delay(2, 4)
            
            # Check for CAPTCHA
            if 'captcha' in self.driver.page_source.lower():
                return UploadResult(
                    platform=Platform.TIKTOK,
                    success=False,
                    error="CAPTCHA detected! Emergency stop triggered."
                )
            
            # Find and interact with file input
            file_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
            )
            
            # Upload file
            file_input.send_keys(str(Path(video_path).absolute()))
            self._human_delay(3, 5)
            
            # Wait for video to process
            print("Waiting for video to process...")
            time.sleep(10)
            
            # Add caption
            caption = metadata.get('caption', '')
            if caption:
                try:
                    caption_input = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div[contenteditable='true']"))
                    )
                    caption_input.click()
                    self._human_delay()
                    caption_input.send_keys(caption)
                    self._human_delay()
                except:
                    print("Could not add caption")
            
            # Click post button
            try:
                post_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Post')]"))
                )
                post_button.click()
                self._human_delay(2, 4)
                
                # Wait for upload confirmation
                time.sleep(5)
                
                return UploadResult(
                    platform=Platform.TIKTOK,
                    success=True,
                    url="https://www.tiktok.com/@your_profile"  # TikTok doesn't give direct URL immediately
                )
            except:
                return UploadResult(
                    platform=Platform.TIKTOK,
                    success=False,
                    error="Failed to click post button"
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
