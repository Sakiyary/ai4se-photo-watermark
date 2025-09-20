"""Custom exceptions for photo watermark application."""


class PhotoWatermarkError(Exception):
    """Base exception for photo watermark errors."""
    pass


class ImageProcessingError(PhotoWatermarkError):
    """Raised when image processing fails."""
    pass


class ExifReadError(PhotoWatermarkError):
    """Raised when EXIF data cannot be read."""
    pass


class WatermarkRenderError(PhotoWatermarkError):
    """Raised when watermark rendering fails."""
    pass


class InvalidConfigError(PhotoWatermarkError):
    """Raised when configuration is invalid."""
    pass


class UnsupportedFormatError(PhotoWatermarkError):
    """Raised when file format is not supported."""
    pass