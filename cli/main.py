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
    video_path: Path = typer.Argument(..., help="Path to the video file", exists=True),
    platforms: Optional[str] = typer.Option(
        None,
        "--platforms", "-p",
        help="Comma-separated list of platforms (youtube,tiktok,instagram) or 'all'"
    ),
    metadata_file: Optional[Path] = typer.Option(
        None,
        "--metadata", "-m",
        help="JSON metadata file (CLI args override JSON values)"
    ),
    title: Optional[str] = typer.Option(None, "--title", "-t", help="Video title"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="Video description"),
    tags: Optional[str] = typer.Option(None, "--tags", help="Comma-separated tags"),
    publish_now: bool = typer.Option(False, "--publish-now", help="Publish immediately"),
    scheduled_time: Optional[str] = typer.Option(None, "--scheduled-time", help="Schedule publication time (ISO 8601)"),
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
    
    # Load from JSON file if provided
    if metadata_file:
        try:
            json_metadata = import_metadata(str(metadata_file))
            console.print(f"[green]✓[/green] Loaded metadata from {metadata_file.name}")
            metadata = json_metadata
        except Exception as e:
            console.print(f"[bold red]❌ Error loading metadata:[/bold red] {e}")
            raise typer.Exit(code=1)
    
    # CLI arguments override JSON values
    cli_metadata = {}
    if title:
        cli_metadata['title'] = title
    if description:
        cli_metadata['description'] = description
    if tags:
        cli_metadata['tags'] = [tag.strip() for tag in tags.split(',')]
    
    # Handle scheduling in CLI
    if publish_now or scheduled_time:
        cli_metadata['scheduling'] = {
            'publish_now': publish_now,
            'scheduled_time': scheduled_time
        }
    
    # Merge (CLI takes precedence)
    if cli_metadata:
        metadata = merge_metadata(metadata, cli_metadata)
    
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
