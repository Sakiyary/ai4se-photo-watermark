"""File and directory utility functions."""

import os
from pathlib import Path
from typing import List, Union, Iterator


def ensure_directory(path: Union[str, Path]) -> Path:
    """
    Ensure directory exists, create if necessary.
    
    Args:
        path: Directory path
        
    Returns:
        Path object for the directory
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_file_size(file_path: Union[str, Path]) -> int:
    """
    Get file size in bytes.
    
    Args:
        file_path: Path to file
        
    Returns:
        File size in bytes
    """
    return Path(file_path).stat().st_size


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def find_files_by_extension(
    directory: Union[str, Path], 
    extensions: Union[str, List[str]],
    recursive: bool = False
) -> List[Path]:
    """
    Find files with specific extensions in directory.
    
    Args:
        directory: Directory to search
        extensions: File extension(s) to search for
        recursive: Whether to search recursively
        
    Returns:
        List of matching file paths
    """
    directory = Path(directory)
    
    if isinstance(extensions, str):
        extensions = [extensions]
    
    # Normalize extensions (ensure they start with .)
    extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in extensions]
    extensions = [ext.lower() for ext in extensions]
    
    files = []
    
    if recursive:
        pattern = "**/*"
        iterator = directory.glob(pattern)
    else:
        iterator = directory.iterdir()
    
    for path in iterator:
        if path.is_file() and path.suffix.lower() in extensions:
            files.append(path)
    
    return sorted(files)


def is_safe_path(path: Union[str, Path], base_dir: Union[str, Path]) -> bool:
    """
    Check if path is safe (within base directory).
    
    Args:
        path: Path to check
        base_dir: Base directory
        
    Returns:
        True if path is safe
    """
    try:
        path = Path(path).resolve()
        base_dir = Path(base_dir).resolve()
        
        # Check if path is within base directory
        return str(path).startswith(str(base_dir))
    except Exception:
        return False


def create_backup_name(file_path: Union[str, Path]) -> Path:
    """
    Create a backup filename for a file.
    
    Args:
        file_path: Original file path
        
    Returns:
        Backup file path
    """
    path = Path(file_path)
    timestamp = int(os.path.getmtime(path)) if path.exists() else 0
    backup_name = f"{path.stem}_backup_{timestamp}{path.suffix}"
    return path.parent / backup_name


def get_available_space(path: Union[str, Path]) -> int:
    """
    Get available disk space for a path.
    
    Args:
        path: Path to check
        
    Returns:
        Available space in bytes
    """
    path = Path(path)
    if not path.exists():
        path = path.parent
    
    try:
        statvfs = os.statvfs(path)
        return statvfs.f_frsize * statvfs.f_bavail
    except AttributeError:
        # Windows doesn't have statvfs
        import shutil
        return shutil.disk_usage(path).free