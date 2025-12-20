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
            print("Checking for popups...")
            popup_selectors = [
                "//div[@role='button' and text()='OK']",
                "//div[@role='button' and text()='Aceptar']",
                "//div[@role='button' and text()='Accept']",
                "//button[text()='Not Now']",
                "//button[text()='Ahora no']"
            ]
            
            for selector in popup_selectors:
                try:
                    btn = WebDriverWait(self.driver, 2).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    btn.click()
                    print(f"Dismissed popup using: {selector}")
                    self._human_delay(1, 2)
                except:
                    pass
            
            # Click Create button
            print("Clicking Create button...")
            try:
                # Primary: English (forced)
                # Try multiple selectors for the Create button link
                create_selectors = [
                    "//span[text()='Create']/ancestor::a",
                    "//span[text()='Crear']/ancestor::a",
                    "a[href='#'][role='link'] svg[aria-label='New post']", # SVG fallback
                    "a[href='#'][role='link'] svg[aria-label='Nueva publicación']"
                ]
                
                create_button = None
                for selector in create_selectors:
                    try:
                        if selector.startswith("//"):
                            create_button = WebDriverWait(self.driver, 5).until(
                                EC.presence_of_element_located((By.XPATH, selector))
                            )
                        else:
                            create_button = WebDriverWait(self.driver, 5).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                            )
                        
                        if create_button:
                            # Use JS click to bypass any overlays
                            self.driver.execute_script("arguments[0].click();", create_button)
                            print(f"Clicked Create button using: {selector}")
                            self._human_delay(2, 3)
                            break
                    except:
                        continue
                        
                if not create_button:
                    raise Exception("Create button not found")
                    
            except Exception as e:
                print(f"Could not find or click Create button: {e}")
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
            # We skip clicking this button because it opens the OS file explorer
            # Instead, we directly find the file input and send the keys
            
            # Find and interact with file input
            print("Uploading file via direct injection (avoiding OS dialog)...")
            try:
                # The file input is often present but hidden
                file_input = WebDriverWait(self.driver, 15).until(
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
                # Try English "OK" as browser is forced to EN
                accept_reels = WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'OK') or contains(text(), 'Accept') and @type='button']"))
                )
                accept_reels.click()
                print("Dismissed Reels notification dialog")
                self._human_delay(1, 2)
            except:
                # Try Spanish "Aceptar" button as fallback
                try:
                    accept_reels = WebDriverWait(self.driver, 1).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Aceptar') and @type='button']"))
                    )
                    accept_reels.click()
                    print("Dismissed Reels notification dialog")
                    self._human_delay(1, 2)
                except:
                    pass
            
            # Wait for video to process
            print("Waiting for video to process...")
            time.sleep(5)
            
            # Wait for "Crop" dialog to appear
            print("Waiting for crop dialog...")
            try:
                crop_dialog = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@role='dialog' and (@aria-label='Crop' or @aria-label='Recortar')]"))
                )
                print("Crop dialog opened")
                self._human_delay(1, 2)
                
                # Click "Select crop" button inside the dialog
                print("Clicking 'Select crop' button...")
                crop_clicked = False
                
                try:
                    # Strategy: Find all buttons in the dialog, excluding Back and Next buttons
                    all_buttons = self.driver.find_elements(By.XPATH, "//div[@role='dialog' and (@aria-label='Crop' or @aria-label='Recortar')]//button[@type='button']")
                    
                    print(f"Found {len(all_buttons)} buttons in crop dialog")
                    
                    for idx, button in enumerate(all_buttons):
                        try:
                            # Get button text and check if it contains Back/Next/Siguiente/Atrás
                            button_text = button.text.strip().lower()
                            
                            # Skip navigation buttons
                            if any(skip_word in button_text for skip_word in ['next', 'siguiente', 'back', 'atrás']):
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
                        # English "Original" (Primary)
                        "//div[@role='button']//span[text()='Original']",
                        "//span[text()='Original']/parent::div[@role='button']",
                        
                        # Spanish "Original"
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
                    EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and (.//text()='Next' or .//text()='Siguiente')]"))
                )
                next_button.click()
                self._human_delay(2, 3)
            except Exception as e:
                print(f"Could not find first Next button: {e}")
            
            # Handle Thumbnail Upload (if provided)
            thumbnail_path = metadata.get('thumbnail_path')
            if thumbnail_path and os.path.exists(thumbnail_path):
                print(f"Attempting to upload thumbnail: {thumbnail_path}")
                try:
                    # After first Next, we are in the Edit/Filters page or Cover page
                    # Directly look for the file input instead of clicking "Select from computer"
                    
                    print("Uploading thumbnail via direct injection...")
                    try:
                        # Find the hidden file input that appears in the cover selection stage
                        # There might be multiple file inputs, we should try to find the one that works for images
                        thumb_input = WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, "//input[@type='file' and contains(@accept, 'image')]"))
                        )
                        thumb_input.send_keys(str(Path(thumbnail_path).absolute()))
                        print("Thumbnail file sent successfully")
                        self._human_delay(5, 8)
                    except Exception as e:
                        print(f"Direct injection for thumbnail failed: {e}")
                        # Fallback: try clicking "Portada"/"Cover" tab first if something went wrong
                        try:
                            cover_tab = WebDriverWait(self.driver, 5).until(
                                EC.element_to_be_clickable((By.XPATH, "//span[text()='Cover' or text()='Portada']"))
                            )
                            cover_tab.click()
                            self._human_delay(1, 2)
                            
                            thumb_input = WebDriverWait(self.driver, 5).until(
                                EC.presence_of_element_located((By.XPATH, "//input[@type='file' and contains(@accept, 'image')]"))
                            )
                            thumb_input.send_keys(str(Path(thumbnail_path).absolute()))
                            print("Thumbnail file sent after clicking Cover tab")
                            self._human_delay(5, 8)
                        except Exception as e2:
                            print(f"Fallback thumbnail injection also failed: {e2}")
                except Exception as e:
                    print(f"Error during thumbnail upload: {e}")

            # Click Next button again (filters/editing page or after thumbnail)
            print("Clicking Next again...")
            try:
                next_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and (.//text()='Siguiente' or .//text()='Next')]"))
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
                    # Click caption area first - try English then Spanish
                    caption_area = None
                    # Since we forced English, English selector should be primary
                    selectors = [
                        "//div[@aria-label='Write a caption...']",
                        "//div[@aria-label='Escribe un pie de foto o vídeo…']",
                        "div[contenteditable='true'][role='textbox']" # Generic fallback
                    ]
                    
                    for selector in selectors:
                        try:
                            if selector.startswith("//"):
                                caption_area = WebDriverWait(self.driver, 5).until(
                                    EC.presence_of_element_located((By.XPATH, selector))
                                )
                            else:
                                caption_area = WebDriverWait(self.driver, 5).until(
                                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                                )
                            break
                        except:
                            continue
                    
                    if caption_area:
                        caption_area.click()
                        self._human_delay(0.5, 1)
                        
                        # Use TikTok method: Clipboard paste for React compatibility and special characters
                        print("Using clipboard paste for caption...")
                        self.driver.execute_script("""
                            // Copy text to clipboard
                            var text = arguments[1];
                            navigator.clipboard.writeText(text).then(function() {
                                // Focus the element
                                arguments[0].focus();
                            });
                        """, caption_area, caption)
                        self._human_delay(0.5, 1)
                        
                        # Paste from clipboard
                        caption_area.send_keys(Keys.CONTROL + "v")
                        self._human_delay(1, 2)
                        
                        # Fallback injection if paste didn't work (check if empty)
                        # We use textContent for div[contenteditable]
                        current_text = caption_area.text.strip()
                        if not current_text:
                            print("Clipboard paste may have failed, trying direct JS injection...")
                            self.driver.execute_script("""
                                arguments[0].textContent = arguments[1];
                                arguments[0].dispatchEvent(new Event('input', {bubbles: true}));
                                arguments[0].dispatchEvent(new Event('change', {bubbles: true}));
                            """, caption_area, caption)
                        
                    else:
                        print("Could not find caption area")
                        
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
                # Find Share button - try English then Spanish
                share_btn = None
                selectors = [
                    "//div[@role='button' and (text()='Share' or text()='Compartir')]",
                    "//button[text()='Share' or text()='Compartir']",
                    "//div[contains(text(), 'Share') and @role='button']"
                ]
                
                for selector in selectors:
                    try:
                        share_btn = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        break
                    except:
                        continue
                
                if share_btn:
                    # Use JS click to be safe
                    self.driver.execute_script("arguments[0].click();", share_btn)
                    print("Clicked Post button")
                    self._human_delay(2, 4)
                else:
                    print("Could not find Share button")
                    
            except Exception as e:
                print(f"Error clicking Post: {e}")

            # Wait for upload confirmation
            print("Waiting for upload confirmation (this may take a while for large videos)...")
            try:
                # 1. Wait for "Sharing" dialog to appear
                # This shows while the video is actually being transmitted/processed
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Sharing') or contains(text(), 'Compartiendo')]"))
                    )
                    print("Upload in progress: 'Sharing' dialog detected")
                except:
                    print("Did not detect 'Sharing' label, but proceeding to wait for success...")

                # 2. Wait for success message or dialog to close
                # Success messages: "Your post has been shared.", "Your reel has been shared.", etc.
                success_selectors = [
                    "//*[contains(text(), 'Your post has been shared')]",
                    "//*[contains(text(), 'Your reel has been shared')]",
                    "//*[contains(text(), 'Shared')]",
                    "//*[contains(text(), 'Compartido')]",
                    "//div[@role='dialog' and .//text()[contains(., 'shared')]]"
                ]
                
                # We wait up to 90 seconds for large videos
                import time as time_module
                start_wait = time_module.time()
                timeout = 90
                confirmed = False
                
                print("Monitoring for success message...")
                while time_module.time() - start_wait < timeout:
                    for selector in success_selectors:
                        try:
                            # Use short timeout inside the loop
                            success_el = self.driver.find_elements(By.XPATH, selector)
                            if success_el and any(el.is_displayed() for el in success_el):
                                print(f"Success confirmation found: {selector}")
                                confirmed = True
                                break
                        except:
                            pass
                    
                    if confirmed:
                        break
                        
                    # Also check if the "Sharing" overlay is gone and we are back on main page
                    # If we can see the "Create" button again, it might be done
                    try:
                        # If sharing dialog is gone and we can't find it anymore
                        sharing_els = self.driver.find_elements(By.XPATH, "//div[contains(text(), 'Sharing') or contains(text(), 'Compartiendo')]")
                        if not sharing_els or not any(el.is_displayed() for el in sharing_els):
                            # Check for the close button [X] of the success dialog
                            close_btns = self.driver.find_elements(By.XPATH, "//div[@role='button']//p[text()='Done' or text()='Listo']")
                            if close_btns:
                                print("Found 'Done' button, upload definitely finished.")
                                confirmed = True
                                break
                    except:
                        pass
                        
                    time_module.sleep(2)
                
                if confirmed:
                    print("✅ Upload verified successfully!")
                    self._human_delay(2, 3)
                else:
                    print("⚠️  Warning: Could not verify upload completion via UI, but no error was thrown.")
                
            except Exception as e:
                print(f"Observation error during confirmation: {e}")
                
            return UploadResult(
                platform=Platform.INSTAGRAM,
                success=True,
                url="https://www.instagram.com/"
            )
            
        except Exception as e:
            return UploadResult(
                platform=Platform.INSTAGRAM,
                success=False,
                error=f"Instagram upload failed: {e}"
            )
        finally:
            self.close()

    def close(self):
        """Close the browser."""
        if self.driver:
            self.driver.quit()
