import os
import re
import requests
import logging
from urllib.parse import urlparse
from pathlib import Path
from typing import Optional
import time

def validate_url(url: str, timeout: int = 10) -> bool:
    """
    Validate if URL is accessible and appears to be a video.
    
    Args:
        url (str): URL to validate
        timeout (int): Request timeout in seconds
        
    Returns:
        bool: True if URL appears to be a video, False otherwise
    """
    try:
        response = requests.head(url, timeout=timeout)
        content_type = response.headers.get('content-type', '').lower()
        
        if 'video' in content_type:
            return True
        
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm', '.m4v']
        parsed_url = urlparse(url)
        if any(parsed_url.path.lower().endswith(ext) for ext in video_extensions):
            return True
            
        return False
        
    except Exception:
        return True

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing invalid characters.
    
    Args:
        filename (str): Original filename
        
    Returns:
        str: Sanitized filename
    """
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    sanitized = re.sub(r'_+', '_', sanitized)
    
    if not sanitized or sanitized == '_':
        sanitized = f"video_{int(time.time())}.mp4"
    
    return sanitized

def setup_logging(output_folder: str, log_level: str = "INFO") -> logging.Logger:
    """
    Setup logging configuration.
    
    Args:
        output_folder (str): Directory for log files
        log_level (str): Logging level
        
    Returns:
        logging.Logger: Configured logger
    """
    
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    
    log_file = os.path.join(output_folder, 'extraction_log.txt')
    
    logger = logging.getLogger('video_frame_extractor')
    logger.setLevel(getattr(logging, log_level.upper()))
    
    logger.handlers.clear()
    
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger
