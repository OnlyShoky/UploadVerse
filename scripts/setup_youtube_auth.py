"""
YouTube Authentication Setup Helper

This script helps you set up YouTube OAuth2 authentication.
Run this AFTER you've placed client_secrets.json in the project root.
"""
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

console = Console()

def main():
    console.print("\n")
    console.print(Panel.fit(
        "[bold cyan]YouTube Authentication Setup[/bold cyan]\n"
        "This will open a browser for OAuth2 authorization",
        border_style="cyan"
    ))
    console.print("\n")
    
    # Check if client_secrets.json exists
    secrets_file = Path("client_secrets.json")
    if not secrets_file.exists():
        console.print("[bold red]❌ ERROR:[/bold red] client_secrets.json not found!\n")
        console.print("Please follow these steps:")
        console.print("1. Go to https://console.cloud.google.com/")
        console.print("2. Create a project and enable YouTube Data API v3")
        console.print("3. Create OAuth2 credentials (Desktop app)")
        console.print("4. Download the JSON file as 'client_secrets.json'")
        console.print("5. Place it in the project root\n")
        console.print(f"Expected location: {secrets_file.absolute()}\n")
        return
    
    console.print(f"✅ Found client_secrets.json\n")
    
    # Import and authenticate
    try:
        from video_publisher.platforms.youtube.uploader import YouTubeUploader
        
        console.print("[yellow]Starting YouTube authentication...[/yellow]")
        console.print("[dim]A browser window will open. Please sign in and authorize.[/dim]\n")
        
        uploader = YouTubeUploader()
        uploader.authenticate()
        
        if uploader.is_authenticated():
            console.print("\n[bold green]✅ SUCCESS![/bold green]")
            console.print("YouTube authentication complete!\n")
            console.print("Your token has been saved to: [cyan]data/sessions/youtube_token.pickle[/cyan]\n")
            console.print("[bold]Next steps:[/bold]")
            console.print("1. Test upload: [cyan]video-publisher upload test.mp4 --platforms youtube[/cyan]")
            console.print("2. Check your video: [cyan]https://studio.youtube.com/[/cyan]\n")
        else:
            console.print("\n[bold red]❌ Authentication failed![/bold red]")
            console.print("Please try again or check the error messages above.\n")
            
    except FileNotFoundError as e:
        console.print(f"\n[bold red]❌ ERROR:[/bold red] {e}\n")
        console.print("Make sure client_secrets.json is valid and in the correct location.\n")
    except Exception as e:
        console.print(f"\n[bold red]❌ ERROR:[/bold red] {e}\n")

if __name__ == "__main__":
    main()
