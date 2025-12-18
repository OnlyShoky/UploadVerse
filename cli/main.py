"""
Video Publisher CLI - Command-line interface for video uploads.
"""
import typer
import json
from typing import Optional, List
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from video_publisher import upload_video, get_publisher, Platform
from video_publisher.metadata import (
    export_metadata,
    import_metadata,
    generate_template,
    validate_metadata,
    merge_metadata
)

app = typer.Typer(
    name="video-publisher",
    help="Multi-platform video upload automation CLI",
    add_completion=False
)
console = Console()

@app.command()
def upload(
    video_paths: List[Path] = typer.Argument(..., help="Path to video file(s)", exists=True),
    platforms: Optional[str] = typer.Option(
        None,
        "--platforms", "-p",
        help="Comma-separated list of platforms (youtube,tiktok,instagram) or 'all'"
    ),
    metadata: Optional[str] = typer.Option(
        None,
        "--metadata", "-m",
        help="JSON metadata file(s). Comma-separated for multiple (paired by position with videos)"
    ),
    thumbnails: Optional[str] = typer.Option(
        None,
        "--thumbnail",
        help="Custom thumbnail(s). Comma-separated for multiple (paired by position with videos)"
    ),
    title: Optional[str] = typer.Option(None, "--title", "-t", help="Video title (Applied to ALL videos)"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="Video description (Applied to ALL videos)"),
    tags: Optional[str] = typer.Option(None, "--tags", help="Comma-separated tags (Applied to ALL videos)"),
    publish_now: bool = typer.Option(False, "--publish-now", help="Publish immediately"),
    scheduled_time: Optional[str] = typer.Option(None, "--scheduled-time", help="Schedule publication time (ISO 8601)"),
):
    """
    Upload one or more videos to platforms.
    """
    # Parse platforms once
    platform_list = None
    if platforms:
        if platforms.lower() == 'all':
            platform_list = ['youtube', 'tiktok', 'instagram']
        else:
            platform_list = [p.strip() for p in platforms.split(',')]
    
    # Global metadata overrides (CLI args)
    global_cli_metadata = {}
    if title:
        global_cli_metadata['title'] = title
    if description:
        global_cli_metadata['description'] = description
    if tags:
        global_cli_metadata['tags'] = [tag.strip() for tag in tags.split(',')]
    if publish_now or scheduled_time:
        global_cli_metadata['scheduling'] = {
            'publish_now': publish_now,
            'scheduled_time': scheduled_time
        }
    # Note: thumbnails is now handled per-video below
    
    # Parse comma-separated metadata and thumbnail paths into lists
    metadata_files = []
    if metadata:
        metadata_files = [Path(p.strip()) for p in metadata.split(',') if p.strip()]
    
    thumbnail_paths = []
    if thumbnails:
        thumbnail_paths = [Path(p.strip()) for p in thumbnails.split(',') if p.strip()]

    # Process each video
    total_videos = len(video_paths)
    console.print(f"\n[bold blue]🚀 Starting batch upload for {total_videos} video(s)[/bold blue]")
    if platform_list:
        console.print(f"[bold]Platforms:[/bold] {', '.join(platform_list)}")
    else:
        console.print("[bold]Platforms:[/bold] Auto-detect based on video format")

    try:
        # We reuse the publisher logic implicitly because accessing the singleton 
        # inside the loop or just calling the sensitive functions usually keeps state if designed so.
        # However, `upload_video` function in `__init__.py` gets a publisher instance.
        # To ensure session persistence (reuse of browser), we should rely on the `get_publisher()` singleton behavior 
        # which is already implemented in `src/video_publisher/__init__.py`.
        
        for index, video_path in enumerate(video_paths, 1):
            console.print(f"\n[bold cyan]Processing [{index}/{total_videos}]:[/bold cyan] {video_path.name}")
            
            # Determine which metadata file to use for this video
            # If multiple metadata files provided, pair by position. If only one, use for all.
            video_metadata_file = None
            if metadata_files:
                if len(metadata_files) >= index:
                    video_metadata_file = metadata_files[index - 1]
                elif len(metadata_files) == 1:
                    video_metadata_file = metadata_files[0]
            
            # Determine which thumbnail to use for this video
            video_thumbnail_path = None
            if thumbnail_paths:
                if len(thumbnail_paths) >= index:
                    video_thumbnail_path = thumbnail_paths[index - 1]
                elif len(thumbnail_paths) == 1:
                    video_thumbnail_path = thumbnail_paths[0]
            
            # 1. Determine Metadata
            # Priority: CLI > --metadata file > {video}.json > default template
            current_metadata = {}
            
            # A. Load from --metadata if provided for this video
            if video_metadata_file:
                try:
                    current_metadata = import_metadata(str(video_metadata_file))
                    console.print(f"  [dim]• Loaded metadata: {video_metadata_file.name}[/dim]")
                except Exception as e:
                    console.print(f"  [bold red]❌ Error loading metadata:[/bold red] {e}")
                    continue

            # B. Auto-detect {video}.json if no metadata file provided
            elif not video_metadata_file:
                possible_json = video_path.with_suffix('.json')
                if possible_json.exists():
                    try:
                        current_metadata = import_metadata(str(possible_json))
                        console.print(f"  [dim]• Found local metadata: {possible_json.name}[/dim]")
                    except Exception as e:
                        console.print(f"  [red]⚠ Error loading local metadata: {e}[/red]")

            # C. Use provided thumbnail or auto-detect
            if video_thumbnail_path:
                current_metadata['thumbnail_path'] = str(video_thumbnail_path)
                console.print(f"  [dim]• Using thumbnail: {video_thumbnail_path.name}[/dim]")
            else:
                # Check for same name with typical image extensions
                for ext in ['.jpg', '.jpeg', '.png']:
                    possible_thumb = video_path.with_suffix(ext)
                    if possible_thumb.exists():
                        current_metadata['thumbnail_path'] = str(possible_thumb)
                        console.print(f"  [dim]• Found local thumbnail: {possible_thumb.name}[/dim]")
                        break

            # D. Merge CLI overrides (Highest priority)
            if global_cli_metadata:
                current_metadata = merge_metadata(current_metadata, global_cli_metadata)

            # 2. Upload
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task(f"Uploading {video_path.name}...", total=None)
                
                # Call upload - the singleton pattern in `get_publisher` ensures browser reuse
                try:
                    results = upload_video(str(video_path), platforms=platform_list, metadata=current_metadata)
                    progress.update(task, completed=True)
                except Exception as e:
                    # Catch individual upload errors so we don't crash the whole batch
                    progress.update(task, completed=True) # Stop spinner
                    console.print(f"  [bold red]❌ Upload Error:[/bold red] {e}")
                    continue

            # 3. Show Result for this video
            for result in results:
                status = "[green]Success[/green]" if result.success else "[red]Failed[/red]"
                url = result.url or (result.error if result.error else "N/A")
                console.print(f"  • {result.platform.value}: {status} - {url}")

    except Exception as e:
        console.print(f"\n[bold red]❌ Critical Batch Error:[/bold red] {e}")
        raise typer.Exit(code=1)

    console.print("\n[bold green]✨ Batch processing complete![/bold green]")

@app.command()
def status():
    """
    Show system status, authentication, and rate limits.
    """
    publisher = get_publisher()
    
    # 1. System Status
    console.print("\n[bold blue]🛡️  System Status[/bold blue]")
    if publisher.emergency_stop.is_triggered():
        console.print("🚨 [bold red]EMERGENCY STOP ACTIVE[/bold red] - Uploads are disabled")
    else:
        console.print("✅ [green]System Operational[/green]")
    console.print("")

    # 2. Platform Status
    console.print("[bold blue]🔐 Platform Status[/bold blue]")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Platform")
    table.add_column("Auth Status")
    table.add_column("Daily Usage")
    table.add_column("Remaining")
    
    # Map string names to Platform enum
    platforms_map = {
        "YouTube": Platform.YOUTUBE,
        "TikTok": Platform.TIKTOK,
        "Instagram": Platform.INSTAGRAM
    }
    
    for name, platform_enum in platforms_map.items():
        # Check Auth
        auth_status = "[red]Not Configured[/red]"
        if platform_enum in publisher.uploaders:
            uploader = publisher.uploaders[platform_enum]
            if uploader.is_authenticated():
                auth_status = "[green]Authenticated[/green]"
            else:
                auth_status = "[yellow]Needs Login[/yellow]"
        
        # Check Rate Limits
        remaining = publisher.rate_limiter.get_remaining(platform_enum)
        limit = publisher.rate_limiter.limits.get(platform_enum, 5)
        used = limit - remaining
        
        usage_str = f"{used}/{limit}"
        remaining_str = f"[green]{remaining}[/green]" if remaining > 0 else "[red]0[/red]"
        
        table.add_row(name, auth_status, usage_str, remaining_str)
    
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

@app.command()
def metadata(
    action: str = typer.Argument(..., help="Action: export, template, validate"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path"),
    title: Optional[str] = typer.Option(None, "--title", "-t", help="Video title"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="Video description"),
    tags: Optional[str] = typer.Option(None, "--tags", help="Comma-separated tags"),
    publish_now: bool = typer.Option(False, "--publish-now", help="Publish immediately"),
    scheduled_time: Optional[str] = typer.Option(None, "--scheduled-time", help="Schedule publication time (ISO 8601)"),
    input_file: Optional[Path] = typer.Option(None, "--input", "-i", help="Input JSON file to validate"),
):
    """
    Manage video metadata (export, template, validate).
    """
    action = action.lower()
    
    if action == "template":
        # Generate empty template
        template = generate_template()
        
        if output:
            try:
                export_metadata(template, str(output))
                console.print(f"[green]✓[/green] Template saved to: {output}")
            except Exception as e:
                console.print(f"[bold red]❌ Error:[/bold red] {e}")
                raise typer.Exit(code=1)
        else:
            console.print("\n[bold blue]📄 Metadata Template:[/bold blue]")
            console.print(json.dumps(template, indent=2))
    
    elif action == "export":
        # Export metadata from CLI args
        metadata_dict = {}
        if title:
            metadata_dict['title'] = title
        if description:
            metadata_dict['description'] = description
        if tags:
            metadata_dict['tags'] = [tag.strip() for tag in tags.split(',')]
        
        # Handle scheduling
        if publish_now or scheduled_time:
            metadata_dict['scheduling'] = {
                'publish_now': publish_now,
                'scheduled_time': scheduled_time
            }
        
        if not metadata_dict:
            console.print("[bold yellow]⚠️  No metadata provided. Use --title, --description, or --tags[/bold yellow]")
            console.print("[dim]Or use 'metadata template' to generate a template[/dim]")
            raise typer.Exit(code=1)
        
        # Add defaults
        template = generate_template()
        for key in template:
            if key not in metadata_dict:
                metadata_dict[key] = template[key]
        
        if output:
            try:
                export_metadata(metadata_dict, str(output))
                console.print(f"[green]✓[/green] Metadata exported to: {output}")
            except Exception as e:
                console.print(f"[bold red]❌ Error:[/bold red] {e}")
                raise typer.Exit(code=1)
        else:
            console.print("\n[bold blue]📄 Metadata:[/bold blue]")
            console.print(json.dumps(metadata_dict, indent=2))
    
    elif action == "validate":
        # Validate JSON file
        if not input_file:
            console.print("[bold red]❌ Error:[/bold red] --input required for validate action")
            raise typer.Exit(code=1)
        
        try:
            metadata_dict = import_metadata(str(input_file))
            console.print(f"[green]✓[/green] Valid metadata file: {input_file}")
            
            # Show summary
            console.print("\n[bold blue]📋 Summary:[/bold blue]")
            if 'title' in metadata_dict:
                console.print(f"  Title: {metadata_dict['title']}")
            if 'tags' in metadata_dict and metadata_dict['tags']:
                console.print(f"  Tags: {len(metadata_dict['tags'])} tags")
            if 'privacy_status' in metadata_dict:
                console.print(f"  Privacy: {metadata_dict['privacy_status']}")
            if 'description' in metadata_dict:
                console.print(f"  Description: {metadata_dict['description']}")
            if 'scheduling' in metadata_dict:
                sched = metadata_dict['scheduling']
                console.print(f"  Scheduling: Publish Now={sched.get('publish_now')}, Time={sched.get('scheduled_time')}")
                
        except Exception as e:
            console.print(f"[bold red]❌ Invalid metadata file:[/bold red] {e}")
            raise typer.Exit(code=1)
    
    else:
        console.print(f"[bold red]❌ Unknown action:[/bold red] {action}")
        console.print("[dim]Valid actions: export, template, validate[/dim]")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
