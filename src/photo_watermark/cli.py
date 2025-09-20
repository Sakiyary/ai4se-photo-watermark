"""Command line interface for photo watermark tool."""

import logging
import sys
from pathlib import Path
from typing import Optional

import click

from .core.image_processor import ImageProcessor
from .core.watermark import WatermarkConfig, WatermarkPosition
from .utils.validators import (
    validate_font_size, validate_color, validate_position,
    validate_opacity, validate_margin
)
from .exceptions import PhotoWatermarkError


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


def print_progress(current: int, total: int, filename: str, success: bool):
  """Print progress information."""
  status = "✓" if success else "✗"
  percentage = (current / total) * 100
  click.echo(f"[{current}/{total}] {status} {filename} ({percentage:.1f}%)")


@click.command()
@click.argument('input_path', type=click.Path(exists=True, path_type=Path))
@click.option('--font-size', '-s', default=32, help='Font size for watermark text')
@click.option('--color', '-c', default='white', help='Color for watermark text')
@click.option('--position', '-p', default='bottom-right', help='Position of watermark')
@click.option('--margin', '-m', default=10, help='Margin from edges in pixels')
@click.option('--opacity', default=255, help='Opacity of watermark (0-255)')
@click.option('--outline-width', default=1, help='Width of text outline')
@click.option('--outline-color', default='black', help='Color of text outline')
@click.option('--font-path', help='Path to custom font file', type=click.Path(exists=True, path_type=Path))
@click.option('--output', '-o', help='Output path', type=click.Path(path_type=Path))
@click.option('--quality', '-q', default=95, help='JPEG quality (1-100)', type=click.IntRange(1, 100))
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--quiet', is_flag=True, help='Suppress progress output')
@click.version_option(version='1.0.0', prog_name='photo-watermark')
def main(
    input_path: Path,
    font_size: int,
    color: str,
    position: str,
    margin: int,
    opacity: float,
    outline_width: int,
    outline_color: str,
    font_path: Optional[Path],
    output: Optional[Path],
    quality: int,
    verbose: bool,
    quiet: bool
):
  """Add date watermarks to photos using EXIF data."""

  # Configure logging level
  if verbose:
    logging.getLogger().setLevel(logging.DEBUG)
  elif quiet:
    logging.getLogger().setLevel(logging.WARNING)

  try:
    # Validate parameters
    font_size = validate_font_size(font_size)
    color = validate_color(color)
    position_enum = validate_position(position)
    margin = validate_margin(margin)
    opacity = validate_opacity(opacity)
    outline_color = validate_color(outline_color)

    # Create watermark configuration
    config = WatermarkConfig(
        font_size=font_size,
        color=color,
        position=position_enum,
        margin=margin,
        opacity=opacity,
        outline_width=outline_width,
        outline_color=outline_color,
        font_path=str(font_path) if font_path else None
    )

    # Initialize image processor
    processor = ImageProcessor()

    # Show configuration if verbose
    if verbose:
      click.echo("Configuration:")
      click.echo(f"  Font size: {config.font_size}")
      click.echo(f"  Color: {config.color}")
      click.echo(f"  Position: {config.position.value}")
      click.echo(f"  Margin: {config.margin}")
      click.echo(f"  Opacity: {config.opacity}")
      click.echo(f"  Outline: {config.outline_width}px {config.outline_color}")
      if config.font_path:
        click.echo(f"  Font: {config.font_path}")
      click.echo("")

    # Check if input is supported
    if input_path.is_file() and not processor.is_supported_format(input_path):
      click.echo(
          f"Error: Unsupported file format: {input_path.suffix}", err=True)
      click.echo("Supported formats: .jpg, .jpeg, .tiff, .tif", err=True)
      sys.exit(1)

    # Setup progress callback
    progress_callback = None if quiet else print_progress

    # Process images
    click.echo(f"Processing: {input_path}")

    processed, total = processor.process_path(
        input_path,
        config,
        output_path=output,
        progress_callback=progress_callback
    )

    # Show summary
    if not quiet:
      click.echo("\\nSummary:")
      click.echo(f"  Processed: {processed} images")
      if total > processed:
        click.echo(f"  Skipped: {total - processed} images")
      click.echo(f"  Total: {total} images")

      if input_path.is_dir():
        output_dir = input_path.parent / f"{input_path.name}_watermark"
        click.echo(f"  Output directory: {output_dir}")
      elif output:
        click.echo(f"  Output file: {output}")

    if processed == 0:
      if total == 0:
        click.echo("No supported image files found.", err=True)
      else:
        click.echo("No images were processed successfully.", err=True)
      sys.exit(1)

    click.echo("Completed successfully!")

  except PhotoWatermarkError as e:
    click.echo(f"Error: {str(e)}", err=True)
    sys.exit(1)
  except KeyboardInterrupt:
    click.echo("\\nOperation cancelled by user.", err=True)
    sys.exit(1)
  except Exception as e:
    if verbose:
      import traceback
      traceback.print_exc()
    click.echo(f"Unexpected error: {str(e)}", err=True)
    sys.exit(1)


if __name__ == '__main__':
  main()
