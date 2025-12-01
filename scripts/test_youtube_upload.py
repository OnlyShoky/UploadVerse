"""
Test YouTube Upload Script

This script uploads a test video to YouTube with sensible defaults.
It uploads as PRIVATE by default for safety.
"""
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich import print as rprint

# Add project to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from video_publisher import upload_video

console = Console()

def main():
    console.print("\n")
    console.print(Panel.fit(
        "[bold cyan]YouTube Test Upload[/bold cyan]\n"
        "Upload a video to YouTube (PRIVATE by default)",
        border_style="cyan"
    ))
    console.print("\n")
    
    # Get video file
    video_path = input("Enter path to video file (or press Enter for data/videos/my_video.mp4): ").strip()
    if not video_path:
        video_path = "data/videos/my_video.mp4"
    
    video_file = Path(video_path)
    if not video_file.exists():
        console.print(f"[bold red]❌ ERROR:[/bold red] Video file not found: {video_file}\n")
        return
    
    console.print(f"\n📹 Video: [cyan]{video_file.name}[/cyan]")
    
    # Get metadata
    title = input("Video title (or press Enter for default): ").strip()
    if not title:
        title = f"Test Upload - {video_file.stem}"
    
    description = input("Description (or press Enter for default): ").strip()
    if not description:
        description = "Video uploaded via Video Publisher - Automated upload test"
    
    tags_input = input("Tags (comma-separated, or press Enter to skip): ").strip()
    tags = [t.strip() for t in tags_input.split(",")] if tags_input else []
    
    # Privacy selection
    console.print("\n[bold]Privacy options:[/bold]")
    console.print("  1. Private (recommended for testing)")
    console.print("  2. Unlisted")
    console.print("  3. Public")
    
    privacy_choice = input("\nSelect privacy (1-3, default=1): ").strip()
    privacy_map = {"1": "private", "2": "unlisted", "3": "public", "": "private"}
    privacy = privacy_map.get(privacy_choice, "private")
    
    # Prepare metadata
    metadata = {
        'title': title,
        'description': description,
        'privacy_status': privacy,
        'category_id': '22'  # People & Blogs
    }
    
    if tags:
        metadata['tags'] = tags
    
    # Confirm
    console.print("\n[bold]Upload Summary:[/bold]")
    console.print(f"  Video: [cyan]{video_file.name}[/cyan]")
    console.print(f"  Title: {title}")
    console.print(f"  Privacy: [yellow]{privacy.upper()}[/yellow]")
    console.print(f"  Description: {description[:50]}...")
    if tags:
        console.print(f"  Tags: {', '.join(tags)}")
    
    confirm = input("\nProceed with upload? (yes/no): ").strip().lower()
    if confirm != 'yes':
        console.print("\n[yellow]Upload cancelled.[/yellow]\n")
        return
    
    # Upload
    console.print("\n[bold green]🚀 Starting upload...[/bold green]\n")
    
    try:
        results = upload_video(
            str(video_file),
            platforms=['youtube'],
            metadata=metadata
        )
        
        console.print("\n[bold]Upload Results:[/bold]\n")
        
        for result in results:
            if result.success:
                console.print(f"✅ [green]SUCCESS![/green]")
                console.print(f"   Platform: {result.platform.value}")
                console.print(f"   URL: [cyan]{result.url}[/cyan]")
                console.print(f"\n   [dim]Check your video at: https://studio.youtube.com/[/dim]")
            else:
                console.print(f"❌ [red]FAILED[/red]")
                console.print(f"   Platform: {result.platform.value}")
                console.print(f"   Error: {result.error}")
        
        console.print("\n")
        
    except Exception as e:
        console.print(f"\n[bold red]❌ ERROR:[/bold red] {e}\n")
        console.print("[dim]Make sure you've authenticated first:")
        console.print("  python scripts/setup_youtube_auth.py[/dim]\n")

if __name__ == "__main__":
    main()
