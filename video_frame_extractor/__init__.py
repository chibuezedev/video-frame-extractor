"""
Video Frame Extractor Library

A Python library for downloading videos from URLs and extracting frames at specified intervals.
"""

__version__ = "1.0.0"
__author__ = "Paul Chibueze"
__email__ = "chibuezedeveloper@gmail.com"

from .extractor import VideoFrameExtractor
from .player import VideoPlayer
from .utils import validate_url, sanitize_filename

__all__ = [
    'VideoFrameExtractor',
    'VideoPlayer', 
    'validate_url',
    'sanitize_filename'
]
