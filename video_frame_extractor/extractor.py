import os
import cv2
import requests
import threading
import time
import json
from urllib.parse import urlparse
from pathlib import Path
import logging
from datetime import datetime
import re
from typing import Optional, Dict, Any

from .utils import validate_url, sanitize_filename, setup_logging
from .player import VideoPlayer

class VideoFrameExtractor:
    """
    A class for downloading videos and extracting frames at specified intervals.
    
    Args:
        video_url (str): URL of the video to download and process
        output_folder (str): Directory to save extracted frames (default: "frames")
        interval (float): Time interval in seconds between frame extractions (default: 5.0)
        quality (int): JPEG quality for saved frames, 1-100 (default: 95)
        max_width (Optional[int]): Maximum width for extracted frames (default: None)
        start_time (float): Start time in seconds for extraction (default: 0)
        end_time (Optional[float]): End time in seconds for extraction (default: None)
        log_level (str): Logging level (default: "INFO")
    """
    
    def __init__(self, 
                 video_url: str,
                 output_folder: str = "frames",
                 interval: float = 5.0,
                 quality: int = 95,
                 max_width: Optional[int] = None,
                 start_time: float = 0,
                 end_time: Optional[float] = None,
                 log_level: str = "INFO"):
        
        self.video_url = video_url
        self.output_folder = output_folder
        self.interval = interval
        self.quality = max(1, min(100, quality))
        self.max_width = max_width
        self.start_time = max(0, start_time)
        self.end_time = end_time
        self.video_path = None
        self.metadata = {}
        

        self.logger = setup_logging(self.output_folder, log_level)

        self.player = VideoPlayer(logger=self.logger)

    def download_video(self, timeout: int = 30, chunk_size: int = 8192) -> bool:
        """
        Download video from URL with progress tracking.
        
        Args:
            timeout (int): Request timeout in seconds
            chunk_size (int): Download chunk size in bytes
            
        Returns:
            bool: True if download successful, False otherwise
        """
        try:
            if not validate_url(self.video_url):
                self.logger.warning("URL might not be a video file")
            
            self.logger.info(f"Downloading video from: {self.video_url}")
            
            parsed_url = urlparse(self.video_url)
            filename = os.path.basename(parsed_url.path)
            if not filename or '.' not in filename:
                filename = f"downloaded_video_{int(time.time())}.mp4"
            
            filename = sanitize_filename(filename)
            self.video_path = filename
            
            response = requests.get(self.video_url, stream=True, timeout=timeout)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            
            with open(self.video_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        
                        if total_size > 0:
                            progress = (downloaded_size / total_size) * 100
                            print(f"\rDownload progress: {progress:.1f}%", end='', flush=True)
            
            print()
            self.logger.info(f"Video downloaded successfully: {self.video_path}")
            return True
            
        except requests.exceptions.Timeout:
            self.logger.error("Download timeout - try again later")
            return False
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Download error: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error downloading video: {e}")
            return False
    
    def get_video_metadata(self) -> Dict[str, Any]:
        """
        Extract video metadata.
        
        Returns:
            Dict[str, Any]: Dictionary containing video metadata
        """
        try:
            cap = cv2.VideoCapture(self.video_path)
            
            if not cap.isOpened():
                return {}
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = total_frames / fps if fps > 0 else 0
            
            self.metadata = {
                'source_url': self.video_url,
                'fps': fps,
                'total_frames': total_frames,
                'width': width,
                'height': height,
                'duration_seconds': duration,
                'extraction_interval': self.interval,
                'extraction_time': datetime.now().isoformat(),
                'start_time': self.start_time,
                'end_time': self.end_time,
                'quality': self.quality,
                'max_width': self.max_width
            }
            
            cap.release()
            
            metadata_file = os.path.join(self.output_folder, 'video_metadata.json')
            with open(metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
            
            self.logger.info(f"Video metadata: {width}x{height}, {fps:.1f} FPS, {duration:.1f}s")
            return self.metadata
            
        except Exception as e:
            self.logger.error(f"Error getting video metadata: {e}")
            return {}
    
    def extract_frames(self) -> int:
        """
        Extract frames at specified intervals.
        
        Returns:
            int: Number of frames extracted
        """
        try:
            Path(self.output_folder).mkdir(parents=True, exist_ok=True)
            
            cap = cv2.VideoCapture(self.video_path)
            
            if not cap.isOpened():
                self.logger.error("Could not open video file")
                return 0
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps
            
            start_frame = int(self.start_time * fps) if self.start_time > 0 else 0
            end_frame = int(self.end_time * fps) if self.end_time else total_frames
            end_frame = min(end_frame, total_frames)
            
            self.logger.info(f"Extracting frames from {self.start_time}s to {self.end_time or duration:.1f}s")
            
            cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
            
            frame_count = start_frame
            saved_count = 0
            interval_frames = int(fps * self.interval)
            
            while frame_count < end_frame:
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                if (frame_count - start_frame) % interval_frames == 0:
                    current_time = frame_count / fps
                    
                    if self.max_width and frame.shape[1] > self.max_width:
                        scale = self.max_width / frame.shape[1]
                        new_width = self.max_width
                        new_height = int(frame.shape[0] * scale)
                        frame = cv2.resize(frame, (new_width, new_height))
                    
                    frame_filename = f"frame_{saved_count:04d}_time_{current_time:.1f}s.jpg"
                    frame_path = os.path.join(self.output_folder, frame_filename)
                    
                    cv2.imwrite(frame_path, frame, [cv2.IMWRITE_JPEG_QUALITY, self.quality])
                    self.logger.debug(f"Saved: {frame_filename}")
                    saved_count += 1
                
                frame_count += 1
            
            cap.release()
            self.logger.info(f"Frame extraction completed. Total frames saved: {saved_count}")
            
            self.metadata['frames_extracted'] = saved_count
            return saved_count
            
        except Exception as e:
            self.logger.error(f"Error extracting frames: {e}")
            return 0
    
    def play_video(self, show_controls: bool = True) -> None:
        """
        Play the downloaded video.
        
        Args:
            show_controls (bool): Whether to show playback controls
        """
        if not self.video_path or not os.path.exists(self.video_path):
            self.logger.error("Video file not found. Download first.")
            return
        
        self.player.play(
            video_path=self.video_path,
            start_time=self.start_time,
            end_time=self.end_time,
            show_controls=show_controls
        )
    
    def create_summary_report(self) -> str:
        """
        Create a summary report of the extraction.
        
        Returns:
            str: Path to the created report file
        """
        try:
            report_file = os.path.join(self.output_folder, 'extraction_report.txt')
            
            with open(report_file, 'w') as f:
                f.write("VIDEO FRAME EXTRACTION REPORT\n")
                f.write("=" * 40 + "\n\n")
                f.write(f"Source URL: {self.video_url}\n")
                f.write(f"Extraction Time: {self.metadata.get('extraction_time', 'N/A')}\n")
                f.write(f"Video Duration: {self.metadata.get('duration_seconds', 0):.1f} seconds\n")
                f.write(f"Video Resolution: {self.metadata.get('width', 0)}x{self.metadata.get('height', 0)}\n")
                f.write(f"Video FPS: {self.metadata.get('fps', 0):.1f}\n")
                f.write(f"Extraction Interval: {self.interval} seconds\n")
                f.write(f"Frames Extracted: {self.metadata.get('frames_extracted', 0)}\n")
                f.write(f"Output Folder: {self.output_folder}\n")
                f.write(f"Image Quality: {self.quality}%\n")
                
                if self.max_width:
                    f.write(f"Max Width: {self.max_width}px\n")
                if self.start_time > 0 or self.end_time:
                    f.write(f"Time Range: {self.start_time}s to {self.end_time or 'end'}s\n")
            
            self.logger.info(f"Summary report created: {report_file}")
            return report_file
            
        except Exception as e:
            self.logger.error(f"Error creating summary report: {e}")
            return ""
    
    def run(self, play_video: bool = True, create_report: bool = True) -> bool:
        """
        Execute the complete extraction process.
        
        Args:
            play_video (bool): Whether to play the video during extraction
            create_report (bool): Whether to create a summary report
            
        Returns:
            bool: True if successful, False otherwise
        """
        self.logger.info("=== Video Frame Extractor ===")
        
        try:
            if not self.download_video():
                return False
            
            self.get_video_metadata()
            
            if self.end_time and self.end_time <= self.start_time:
                self.logger.error("End time must be greater than start time")
                return False
            
            if play_video:
                extraction_thread = threading.Thread(target=self.extract_frames)
                extraction_thread.start()
                
                self.play_video()
                
                extraction_thread.join()
            else:
                self.extract_frames()
            
            if create_report:
                self.create_summary_report()
            
            self.logger.info("Process completed successfully!")
            return True
            
        except KeyboardInterrupt:
            self.logger.info("Process interrupted by user")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return False
        finally:
            # Cleanup
            if self.video_path and os.path.exists(self.video_path):
                try:
                    os.remove(self.video_path)
                    self.logger.info(f"Cleaned up downloaded video: {self.video_path}")
                except Exception as e:
                    self.logger.warning(f"Could not remove temporary video file: {e}")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup"""
        if self.video_path and os.path.exists(self.video_path):
            try:
                os.remove(self.video_path)
            except:
                pass