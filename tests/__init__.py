"""
Video Frame Extractor Library

A Python library for downloading videos from URLs and extracting frames at specified intervals.
"""

__version__ = "1.0.0"
__author__ = "Paul Chibueze"
__email__ = "chibuezedeveloper@gmail.com"

from video_frame_extractor.extractor import VideoFrameExtractor
from video_frame_extractor.player import VideoPlayer
from video_frame_extractor.utils import validate_url, sanitize_filename

__all__ = [
    'VideoFrameExtractor',
    'VideoPlayer', 
    'validate_url',
    'sanitize_filename'
]
