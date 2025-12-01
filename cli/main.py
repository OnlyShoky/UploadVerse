"""
Video Publisher CLI - Command-line interface for video uploads.
"""
import typer
from typing import Optional, List
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from video_publisher import upload_video, get_publisher, Platform

app = typer.Typer(
    name="video-publisher",
    help="Multi-platform video upload automation CLI",
    add_completion=False
)
console = Console()

@app.command()
def upload(
    video_path: Path = typer.Argument(..., help="Path to the video file", exists=True),
    platforms: Optional[str] = typer.Option(
        None,
        "--platforms", "-p",
        help="Comma-separated list of platforms (youtube,tiktok,instagram) or 'all'"
    ),
    title: Optional[str] = typer.Option(None, "--title", "-t", help="Video title"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="Video description"),
    tags: Optional[str] = typer.Option(None, "--tags", help="Comma-separated tags"),
):
    """
    Upload a video to one or more platforms.
    """
    console.print(f"\n[bold blue]📹 Uploading:[/bold blue] {video_path.name}")
    
    # Parse platforms
    platform_list = None
    if platforms:
        if platforms.lower() == 'all':
            platform_list = ['youtube', 'tiktok', 'instagram']
        else:
            platform_list = [p.strip() for p in platforms.split(',')]
        console.print(f"[bold]Platforms:[/bold] {', '.join(platform_list)}")
    else:
        console.print("[bold]Platforms:[/bold] Auto-detect based on video format")
    
    # Prepare metadata
    metadata = {}
    if title:
        metadata['title'] = title
    if description:
        metadata['description'] = description
    if tags:
        metadata['tags'] = [tag.strip() for tag in tags.split(',')]
    
    # Upload
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Uploading video...", total=None)
            results = upload_video(str(video_path), platforms=platform_list, metadata=metadata)
            progress.update(task, completed=True)
        
        # Display results
        console.print("\n[bold green]✅ Upload Results:[/bold green]")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Platform")
        table.add_column("Status")
        table.add_column("URL")
        
        for result in results:
            status = "[green]Success[/green]" if result.success else "[red]Failed[/red]"
            url = result.url or (result.error if result.error else "N/A")
            table.add_row(result.platform.value, status, url)
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[bold red]❌ Error:[/bold red] {e}")
        raise typer.Exit(code=1)

@app.command()
def status():
    """
    Show authentication status for all platforms.
    """
    console.print("\n[bold blue]🔐 Platform Authentication Status[/bold blue]\n")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Platform")
    table.add_column("Authenticated")
    table.add_column("Notes")
    
    # Check each platform
    platforms_info = [
        ("YouTube", "OAuth2 token required"),
        ("TikTok", "Browser session required"),
        ("Instagram", "Browser session required"),
    ]
    
    for platform_name, notes in platforms_info:
        # This is a simplified status check
        # In a real implementation, you'd check actual authentication
        status = "[yellow]Unknown[/yellow]"
        table.add_row(platform_name, status, notes)
    
    console.print(table)
    console.print("\n[dim]Use 'video-publisher auth <platform>' to authenticate[/dim]")

@app.command()
def auth(
    platform: str = typer.Argument(..., help="Platform to authenticate (youtube, tiktok, instagram)")
):
    """
    Authenticate with a specific platform.
    """
    platform = platform.lower()
    
    if platform not in ['youtube', 'tiktok', 'instagram']:
        console.print(f"[bold red]❌ Invalid platform:[/bold red] {platform}")
        console.print("[dim]Valid platforms: youtube, tiktok, instagram[/dim]")
        raise typer.Exit(code=1)
    
    console.print(f"\n[bold blue]🔐 Authenticating with {platform}...[/bold blue]")
    
    try:
        from video_publisher.platforms.youtube.uploader import YouTubeUploader
        from video_publisher.platforms.tiktok.uploader import TikTokUploader
        from video_publisher.platforms.instagram.uploader import InstagramUploader
        
        uploader_map = {
            'youtube': YouTubeUploader,
            'tiktok': TikTokUploader,
            'instagram': InstagramUploader
        }
        
        uploader_class = uploader_map[platform]
        uploader = uploader_class()
        
        console.print(f"[yellow]Starting {platform} authentication...[/yellow]")
        uploader.authenticate()
        
        if uploader.is_authenticated():
            console.print(f"[bold green]✅ Successfully authenticated with {platform}![/bold green]")
        else:
            console.print(f"[bold red]❌ Authentication failed for {platform}[/bold red]")
            
    except Exception as e:
        console.print(f"[bold red]❌ Error:[/bold red] {e}")
        raise typer.Exit(code=1)

@app.command()
def version():
    """
    Show version information.
    """
    from video_publisher import __version__
    console.print(f"\n[bold]Video Publisher[/bold] version [cyan]{__version__}[/cyan]")
    console.print("[dim]Multi-platform video upload automation[/dim]\n")

if __name__ == "__main__":
    app()
