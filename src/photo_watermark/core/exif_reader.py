"""EXIF information reader for extracting photo date taken."""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Union

import exifread
from PIL import Image
from PIL.ExifTags import TAGS


class ExifReader:
    """Reads EXIF information from image files and extracts date taken."""

    def __init__(self):
        """Initialize the EXIF reader."""
        pass

    def extract_date_taken(self, image_path: Union[str, Path]) -> Optional[datetime]:
        """
        Extract the date taken from image EXIF data.

        Args:
            image_path: Path to the image file

        Returns:
            datetime object if date found, None otherwise
        """
        image_path = Path(image_path)
        
        if not image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Try PIL first (faster and more reliable for common formats)
        date_taken = self._extract_with_pil(image_path)
        
        # Fallback to exifread if PIL fails
        if date_taken is None:
            date_taken = self._extract_with_exifread(image_path)
        
        return date_taken

    def _extract_with_pil(self, image_path: Path) -> Optional[datetime]:
        """Extract date using PIL/Pillow."""
        try:
            with Image.open(image_path) as image:
                exifdata = image.getexif()
                
                if not exifdata:
                    return None
                
                # Priority order: DateTimeOriginal > DateTime > DateTimeDigitized
                date_tags = [
                    "DateTimeOriginal",
                    "DateTime", 
                    "DateTimeDigitized"
                ]
                
                for tag_name in date_tags:
                    for tag_id, value in exifdata.items():
                        tag = TAGS.get(tag_id, tag_id)
                        if tag == tag_name and value:
                            return self._parse_datetime_string(str(value))
                            
        except Exception:
            # PIL failed, will try exifread
            pass
        
        return None

    def _extract_with_exifread(self, image_path: Path) -> Optional[datetime]:
        """Extract date using exifread library as fallback."""
        try:
            with open(image_path, 'rb') as f:
                tags = exifread.process_file(f, stop_tag="EXIF DateTimeOriginal")
                
                # Priority order for exifread tags
                exif_date_tags = [
                    "EXIF DateTimeOriginal",
                    "EXIF DateTime",
                    "EXIF DateTimeDigitized",
                    "Image DateTime"
                ]
                
                for tag_name in exif_date_tags:
                    if tag_name in tags:
                        date_str = str(tags[tag_name])
                        if date_str and date_str != "0000:00:00 00:00:00":
                            return self._parse_datetime_string(date_str)
                            
        except Exception:
            # Both methods failed
            pass
        
        return None

    def _parse_datetime_string(self, date_str: str) -> Optional[datetime]:
        """
        Parse various datetime string formats from EXIF.
        
        Args:
            date_str: Date string from EXIF
            
        Returns:
            datetime object if parsing successful, None otherwise
        """
        if not date_str or date_str.strip() == "":
            return None
            
        # Common EXIF datetime formats
        formats = [
            "%Y:%m:%d %H:%M:%S",  # Standard EXIF format
            "%Y-%m-%d %H:%M:%S",  # Alternative format
            "%Y:%m:%d",           # Date only
            "%Y-%m-%d",           # Date only alternative
        ]
        
        date_str = date_str.strip()
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        return None

    def format_date(self, date_obj: datetime) -> str:
        """
        Format datetime object to YYYY-MM-DD string.
        
        Args:
            date_obj: datetime object
            
        Returns:
            Formatted date string (YYYY-MM-DD)
        """
        return date_obj.strftime("%Y-%m-%d")

    def get_formatted_date(self, image_path: Union[str, Path]) -> Optional[str]:
        """
        Extract and format date from image in one step.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Formatted date string (YYYY-MM-DD) or None
        """
        date_taken = self.extract_date_taken(image_path)
        if date_taken:
            return self.format_date(date_taken)
        return None

    def is_supported_format(self, image_path: Union[str, Path]) -> bool:
        """
        Check if the image format is supported for EXIF reading.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            True if format is supported, False otherwise
        """
        image_path = Path(image_path)
        supported_extensions = {'.jpg', '.jpeg', '.tiff', '.tif'}
        return image_path.suffix.lower() in supported_extensions