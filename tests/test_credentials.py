"""
Credentials Testing Script for Video Publisher

Tests platform credentials without uploading any videos.
Provides clear feedback on what's ready and what needs setup.
"""
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import argparse
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

console = Console()

class CredentialsTester:
    """Test platform credentials safely."""
    
    def __init__(self, safe_mode: bool = True):
        self.safe_mode = safe_mode
        self.results = {}
        
        # Load .env file
        env_path = project_root / '.env'
        if env_path.exists():
            load_dotenv(env_path)
            console.print(f"✅ Loaded .env from {env_path}", style="green")
        else:
            console.print(f"⚠️ No .env file found at {env_path}", style="yellow")
            console.print(f"💡 Copy .env.example to .env and fill in your credentials", style="dim")
    
    def ensure_directories(self):
        """Create necessary directories if they don't exist."""
        sessions_dir = project_root / 'data' / 'sessions'
        videos_dir = project_root / 'data' / 'videos'
        
        for directory in [sessions_dir, videos_dir]:
            if not directory.exists():
                directory.mkdir(parents=True, exist_ok=True)
                console.print(f"📁 Created directory: {directory}", style="cyan")
            else:
                console.print(f"✅ Directory exists: {directory}", style="green dim")
    
    def test_youtube_safe(self) -> Tuple[bool, str, str]:
        """Test YouTube credentials in safe mode (check files exist)."""
        client_secrets = project_root / os.getenv('YOUTUBE_CLIENT_SECRETS_FILE', 'client_secrets.json')
        token_file = project_root / os.getenv('YOUTUBE_TOKEN_FILE', 'data/sessions/youtube_token.pickle')
        
        if not client_secrets.exists():
            return False, "❌", f"client_secrets.json not found at {client_secrets}"
        
        if not token_file.exists():
            return False, "⚠️", f"Not authenticated yet. Run authentication first."
        
        return True, "✅", "Credentials file and token found"
    
    def test_youtube_verify(self) -> Tuple[bool, str, str]:
        """Test YouTube credentials by attempting authentication."""
        try:
            from video_publisher.platforms.youtube.uploader import YouTubeUploader
            
            uploader = YouTubeUploader()
            
            if uploader.is_authenticated():
                return True, "✅", "Authenticated successfully"
            else:
                return False, "❌", "Authentication failed - token invalid or expired"
                
        except FileNotFoundError as e:
            return False, "❌", f"File not found: {str(e)}"
        except Exception as e:
            return False, "❌", f"Error: {str(e)}"
    
    def test_tiktok_safe(self) -> Tuple[bool, str, str]:
        """Test TikTok credentials in safe mode."""
        username = os.getenv('TIKTOK_USERNAME')
        password = os.getenv('TIKTOK_PASSWORD')
        
        if not username or not password:
            return False, "⚠️", "Credentials not set in .env"
        
        cookies_file = Path(os.getenv('TIKTOK_COOKIES_FILE', 'data/sessions/tiktok_session.pkl'))
        
        if cookies_file.exists():
            return True, "✅", f"Credentials set, session file exists"
        
        return False, "⚠️", "Credentials set but not authenticated yet"
    
    def test_tiktok_verify(self) -> Tuple[bool, str, str]:
        """Test TikTok credentials by attempting authentication."""
        console.print("\n⚠️ [yellow]WARNING: TikTok automation violates TOS and may result in account ban![/yellow]")
        console.print("Only proceed if using a test/burner account.\n")
        
        proceed = console.input("Proceed with TikTok authentication test? (yes/no): ")
        if proceed.lower() != 'yes':
            return False, "⏭️", "Skipped by user"
        
        try:
            from video_publisher.platforms.tiktok.uploader import TikTokUploader
            
            uploader = TikTokUploader()
            
            # This will open browser - very risky!
            console.print("[yellow]Opening browser for TikTok... This may trigger anti-bot measures![/yellow]")
            uploader.authenticate()
            
            if uploader.is_authenticated():
                return True, "✅", "Authentication successful (session saved)"
            else:
                return False, "❌", "Authentication failed"
                
        except Exception as e:
            return False, "❌", f"Error: {str(e)}"
    
    def test_instagram_safe(self) -> Tuple[bool, str, str]:
        """Test Instagram credentials in safe mode."""
        username = os.getenv('INSTAGRAM_USERNAME')
        password = os.getenv('INSTAGRAM_PASSWORD')
        
        if not username or not password:
            return False, "⚠️", "Credentials not set in .env"
        
        cookies_file = Path(os.getenv('INSTAGRAM_COOKIES_FILE', 'data/sessions/instagram_session.pkl'))
        
        if cookies_file.exists():
            return True, "✅", f"Credentials set, session file exists"
        
        return False, "⚠️", "Credentials set but not authenticated yet"
    
    def test_instagram_verify(self) -> Tuple[bool, str, str]:
        """Test Instagram credentials by attempting authentication."""
        console.print("\n🔴 [red]DANGER: Instagram VERY aggressively bans automation![/red]")
        console.print("Account ban is highly likely. Only use test accounts!\n")
        
        proceed = console.input("Proceed with Instagram authentication test? (yes/no): ")
        if proceed.lower() != 'yes':
            return False, "⏭️", "Skipped by user"
        
        try:
            from video_publisher.platforms.instagram.uploader import InstagramUploader
            
            uploader = InstagramUploader()
            
            console.print("[yellow]Opening browser for Instagram... Expect CAPTCHAs and challenges![/yellow]")
            uploader.authenticate()
            
            if uploader.is_authenticated():
                return True, "✅", "Authentication successful (session saved)"
            else:
                return False, "❌", "Authentication failed"
                
        except Exception as e:
            return False, "❌", f"Error: {str(e)}"
    
    def test_platform(self, platform: str, verify: bool = False) -> Dict[str, any]:
        """Test a specific platform."""
        if verify and self.safe_mode:
            console.print("[yellow]⚠️ Verification mode requires --verify flag (disables safe mode)[/yellow]")
            verify = False
        
        result = {
            'platform': platform,
            'tested': True,
            'success': False,
            'status': '❌',
            'message': 'Unknown error'
        }
        
        if platform == 'youtube':
            if verify:
                success, status, message = self.test_youtube_verify()
            else:
                success, status, message = self.test_youtube_safe()
        
        elif platform == 'tiktok':
            if verify:
                success, status, message = self.test_tiktok_verify()
            else:
                success, status, message = self.test_tiktok_safe()
        
        elif platform == 'instagram':
            if verify:
                success, status, message = self.test_instagram_verify()
            else:
                success, status, message = self.test_instagram_safe()
        
        else:
            result['tested'] = False
            result['message'] = f"Unknown platform: {platform}"
            return result
        
        result['success'] = success
        result['status'] = status
        result['message'] = message
        
        return result
    
    def test_all(self, verify: bool = False) -> Dict[str, Dict]:
        """Test all platforms."""
        platforms = ['youtube', 'tiktok', 'instagram']
        results = {}
        
        for platform in platforms:
            console.print(f"\n[bold cyan]Testing {platform.upper()}...[/bold cyan]")
            results[platform] = self.test_platform(platform, verify)
        
        return results
    
    def display_results(self, results: Dict[str, Dict]):
        """Display test results in a nice table."""
        table = Table(title="📊 Credentials Test Results", show_header=True, header_style="bold magenta")
        table.add_column("Platform", style="cyan", width=12)
        table.add_column("Status", justify="center", width=8)
        table.add_column("Details", style="white")
        
        for platform, result in results.items():
            if result['tested']:
                table.add_row(
                    platform.upper(),
                    result['status'],
                    result['message']
                )
        
        console.print("\n")
        console.print(table)
        console.print("\n")
    
    def print_recommendations(self, results: Dict[str, Dict]):
        """Print recommendations based on test results."""
        ready = []
        needs_setup = []
        
        for platform, result in results.items():
            if result['success']:
                ready.append(platform)
            else:
                needs_setup.append(platform)
        
        if ready:
            console.print(Panel(
                f"[green]✅ Ready to use: {', '.join(ready).upper()}[/green]",
                title="Ready",
                border_style="green"
            ))
        
        if needs_setup:
            console.print("\n")
            console.print(Panel(
                f"[yellow]⚠️ Needs setup: {', '.join(needs_setup).upper()}[/yellow]\n\n"
                "See USER_SETUP.md for detailed setup instructions.",
                title="Action Required",
                border_style="yellow"
            ))
        
        # Specific recommendations
        console.print("\n[bold]📝 Next Steps:[/bold]\n")
        
        for platform, result in results.items():
            if not result['success']:
                if platform == 'youtube':
                    console.print(f"  • {platform.upper()}: Get client_secrets.json from Google Cloud Console")
                    console.print(f"    → See USER_SETUP.md section 'YouTube Setup'\n")
                
                elif platform == 'tiktok':
                    console.print(f"  • {platform.upper()}: Add credentials to .env (use test account!)")
                    console.print(f"    → Run: python scripts/test_credentials.py --platform tiktok --verify\n")
                
                elif platform == 'instagram':
                    console.print(f"  • {platform.upper()}: Add credentials to .env (use test account!)")
                    console.print(f"    → Run: python scripts/test_credentials.py --platform instagram --verify\n")

def main():
    parser = argparse.ArgumentParser(
        description='Test Video Publisher platform credentials',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Safe mode - just check if files exist (default)
  python scripts/test_credentials.py
  
  # Test specific platform
  python scripts/test_credentials.py --platform youtube
  
  # Verify credentials (actually attempts authentication)
  python scripts/test_credentials.py --verify
  
  # Verify specific platform
  python scripts/test_credentials.py --platform youtube --verify
        """
    )
    
    parser.add_argument(
        '--platform',
        choices=['youtube', 'tiktok', 'instagram'],
        help='Test specific platform only'
    )
    
    parser.add_argument(
        '--verify',
        action='store_true',
        help='Actually attempt authentication (WARNING: May trigger anti-bot measures for TikTok/Instagram)'
    )
    
    parser.add_argument(
        '--safe',
        action='store_true',
        default=True,
        help='Safe mode - only check if credential files exist (default)'
    )
    
    args = parser.parse_args()
    
    # Header
    console.print("\n")
    console.print(Panel.fit(
        "[bold cyan]Video Publisher - Credentials Tester[/bold cyan]\n"
        "Test your platform credentials safely",
        border_style="cyan"
    ))
    console.print("\n")
    
    # Initialize tester
    safe_mode = not args.verify
    if args.verify:
        console.print("[yellow]⚠️ VERIFICATION MODE: Will attempt actual authentication[/yellow]\n")
    else:
        console.print("[green]✅ SAFE MODE: Only checking if credential files exist[/green]\n")
    
    tester = CredentialsTester(safe_mode=safe_mode)
    
    # Ensure directories exist
    console.print("[bold]Checking directories...[/bold]")
    tester.ensure_directories()
    
    # Run tests
    if args.platform:
        console.print(f"\n[bold cyan]Testing {args.platform.upper()} only...[/bold cyan]\n")
        result = tester.test_platform(args.platform, verify=args.verify)
        results = {args.platform: result}
    else:
        console.print("\n[bold cyan]Testing all platforms...[/bold cyan]")
        results = tester.test_all(verify=args.verify)
    
    # Display results
    tester.display_results(results)
    
    # Recommendations
    tester.print_recommendations(results)
    
    # Final note
    if safe_mode:
        console.print("\n[dim]💡 Tip: Use --verify flag to test actual authentication (risky for TikTok/Instagram)[/dim]\n")
    
    console.print("[green]✅ Credentials test complete![/green]\n")

if __name__ == '__main__':
    main()
