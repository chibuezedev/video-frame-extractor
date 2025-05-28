import os
import cv2
import requests
import threading
import time
import json
from urllib.parse import urlparse
import argparse
from pathlib import Path
import logging
from datetime import datetime
import re

class VideoFrameExtractor:
    def __init__(self, video_url, output_folder="frames", interval=5, quality=95, 
                 max_width=None, start_time=0, end_time=None):
        self.video_url = video_url
        self.output_folder = output_folder
        self.interval = interval
        self.quality = quality
        self.max_width = max_width
        self.start_time = start_time
        self.end_time = end_time
        self.video_path = None
        self.is_playing = False
        self.metadata = {}
        
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging configuration"""
        log_file = os.path.join(self.output_folder, 'extraction_log.txt')
        os.makedirs(self.output_folder, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def validate_url(self, url):
        """Validate if URL is accessible and appears to be a video"""
        try:
            response = requests.head(url, timeout=10)
            content_type = response.headers.get('content-type', '').lower()
            
            if 'video' in content_type:
                return True
            
            video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm']
            parsed_url = urlparse(url)
            if any(parsed_url.path.lower().endswith(ext) for ext in video_extensions):
                return True
                
            return False
            
        except Exception as e:
            self.logger.warning(f"Could not validate URL: {e}")
            return True
    
    def download_video(self):
        """Download video from URL with progress tracking"""
        try:
            if not self.validate_url(self.video_url):
                self.logger.warning("URL might not be a video file")
            
            self.logger.info(f"Downloading video from: {self.video_url}")
            
            parsed_url = urlparse(self.video_url)
            filename = os.path.basename(parsed_url.path)
            if not filename or '.' not in filename:
                filename = f"downloaded_video_{int(time.time())}.mp4"
            
            filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
            self.video_path = filename
            
            response = requests.get(self.video_url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            
            with open(self.video_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
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
    
    def create_output_folder(self):
        """Create output folder for frames"""
        Path(self.output_folder).mkdir(parents=True, exist_ok=True)
        self.logger.info(f"Output folder ready: {self.output_folder}")
    
    def get_video_metadata(self):
        """Extract and store video metadata"""
        try:
            cap = cv2.VideoCapture(self.video_path)
            
            if not cap.isOpened():
                return False
            
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
                'end_time': self.end_time
            }
            
            cap.release()
            
            metadata_file = os.path.join(self.output_folder, 'video_metadata.json')
            with open(metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
            
            self.logger.info(f"Video metadata: {width}x{height}, {fps:.1f} FPS, {duration:.1f}s")
            return True
            
        except Exception as e:
            self.logger.error(f"Error getting video metadata: {e}")
            return False
    
    def extract_frames(self):
        """Extract frames every specified interval with enhanced options"""
        try:
            cap = cv2.VideoCapture(self.video_path)
            
            if not cap.isOpened():
                self.logger.error("Could not open video file")
                return False
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps
            
            start_frame = int(self.start_time * fps) if self.start_time > 0 else 0
            end_frame = int(self.end_time * fps) if self.end_time else total_frames
            end_frame = min(end_frame, total_frames)
            
            self.logger.info(f"Extracting frames from {self.start_time}s to {self.end_time or duration:.1f}s")
            self.logger.info(f"Frame range: {start_frame} to {end_frame}")
            
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
                    self.logger.info(f"Saved: {frame_filename}")
                    saved_count += 1
                
                frame_count += 1
                
                if frame_count % (fps * 10) == 0:
                    progress = ((frame_count - start_frame) / (end_frame - start_frame)) * 100
                    print(f"Extraction progress: {progress:.1f}%")
            
            cap.release()
            self.logger.info(f"Frame extraction completed. Total frames saved: {saved_count}")
            
            self.metadata['frames_extracted'] = saved_count
            self.metadata['actual_end_time'] = frame_count / fps
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error extracting frames: {e}")
            return False
    
    def play_video(self):
        """Play video with enhanced controls"""
        try:
            cap = cv2.VideoCapture(self.video_path)
            
            if not cap.isOpened():
                self.logger.error("Could not open video file for playback")
                return
            
            self.is_playing = True
            fps = cap.get(cv2.CAP_PROP_FPS)
            delay = int(1000 / fps) if fps > 0 else 33
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            if self.start_time > 0:
                start_frame = int(self.start_time * fps)
                cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
            
            self.logger.info("Playing video... Controls:")
            self.logger.info("'q' - quit, 'p' - pause/unpause, 'r' - restart")
            self.logger.info("'f' - fast forward 10s, 'b' - rewind 10s")
            
            paused = False
            current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
            
            while self.is_playing:
                if not paused:
                    ret, frame = cap.read()
                    current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
                    
                    if not ret or (self.end_time and current_frame >= self.end_time * fps):
                        break
                    
                    display_frame = frame.copy()
                    height, width = display_frame.shape[:2]
                    if width > 1200:
                        scale = 1200 / width
                        new_width = int(width * scale)
                        new_height = int(height * scale)
                        display_frame = cv2.resize(display_frame, (new_width, new_height))
                    
                    current_time = current_frame / fps
                    time_text = f"Time: {current_time:.1f}s"
                    cv2.putText(display_frame, time_text, (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    
                    cv2.imshow('Enhanced Video Player', display_frame)
                
                key = cv2.waitKey(delay) & 0xFF
                
                if key == ord('q'):
                    break
                elif key == ord('p'):
                    paused = not paused
                    status = "Paused" if paused else "Resumed"
                    self.logger.info(status)
                elif key == ord('r'):
                    start_frame = int(self.start_time * fps) if self.start_time > 0 else 0
                    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
                    paused = False
                    self.logger.info("Video restarted")
                elif key == ord('f'):
                    new_frame = min(current_frame + int(10 * fps), total_frames - 1)
                    cap.set(cv2.CAP_PROP_POS_FRAMES, new_frame)
                    self.logger.info("Fast forward 10s")
                elif key == ord('b'):
                    new_frame = max(current_frame - int(10 * fps), 0)
                    cap.set(cv2.CAP_PROP_POS_FRAMES, new_frame)
                    self.logger.info("Rewind 10s")
            
            cap.release()
            cv2.destroyAllWindows()
            self.is_playing = False
            
        except Exception as e:
            self.logger.error(f"Error playing video: {e}")
    
    def create_summary_report(self):
        """Create a summary report of the extraction"""
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
                
                if self.start_time > 0 or self.end_time:
                    f.write(f"Time Range: {self.start_time}s to {self.end_time or 'end'}s\n")
                
                f.write(f"\nImage Quality: {self.quality}%\n")
                if self.max_width:
                    f.write(f"Max Width: {self.max_width}px\n")
            
            self.logger.info(f"Summary report created: {report_file}")
            
        except Exception as e:
            self.logger.error(f"Error creating summary report: {e}")
    
    def run(self):
        """Main execution function with enhanced error handling"""
        self.logger.info("=== Enhanced Video Frame Extractor ===")
        
        try:

            if not self.download_video():
                return False

            self.create_output_folder()
            
            if not self.get_video_metadata():
                self.logger.warning("Could not extract video metadata")
            
            if self.end_time and self.end_time <= self.start_time:
                self.logger.error("End time must be greater than start time")
                return False
            
            extraction_thread = threading.Thread(target=self.extract_frames)
            extraction_thread.start()
            
            self.play_video()
            
            extraction_thread.join()
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

def main():
    parser = argparse.ArgumentParser(
        description='Enhanced video frame extractor with advanced features',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python enhanced_extractor.py "https://example.com/video.mp4"
  python enhanced_extractor.py "url" -o frames -i 3 -q 90 -w 800
  python enhanced_extractor.py "url" -s 30 -e 120 -i 2
        """
    )
    
    parser.add_argument('url', help='Video URL to download')
    parser.add_argument('-o', '--output', default='frames', 
                       help='Output folder for frames (default: frames)')
    parser.add_argument('-i', '--interval', type=float, default=5, 
                       help='Interval in seconds between frame captures (default: 5)')
    parser.add_argument('-q', '--quality', type=int, default=95, choices=range(1, 101),
                       help='JPEG quality 1-100 (default: 95)')
    parser.add_argument('-w', '--width', type=int, 
                       help='Maximum width for extracted frames (maintains aspect ratio)')
    parser.add_argument('-s', '--start', type=float, default=0,
                       help='Start time in seconds (default: 0)')
    parser.add_argument('-e', '--end', type=float,
                       help='End time in seconds (default: full video)')
    
    args = parser.parse_args()
    
    if args.interval <= 0:
        print("Error: Interval must be greater than 0")
        return
    
    if args.start < 0:
        print("Error: Start time cannot be negative")
        return
    
    if args.end and args.end <= args.start:
        print("Error: End time must be greater than start time")
        return
    
    extractor = VideoFrameExtractor(
        video_url=args.url,
        output_folder=args.output,
        interval=args.interval,
        quality=args.quality,
        max_width=args.width,
        start_time=args.start,
        end_time=args.end
    )
    
    success = extractor.run()
    exit(0 if success else 1)

if __name__ == "__main__":
    if len(os.sys.argv) == 1:
        print("Enhanced Video Frame Extractor")
        print("=" * 30)
        print("\nUsage examples:")
        print('python enhanced_extractor.py "https://example.com/video.mp4"')
        print('python enhanced_extractor.py "url" -o my_frames -i 3 -q 90')
        print('python enhanced_extractor.py "url" -s 30 -e 120 -w 800')
        print("\nFor help: python enhanced_extractor.py -h")
        print("\nOr modify the script to set parameters directly:")
        
        video_url = "https://v1.pinimg.com/videos/mc/expMp4/32/3b/3d/323b3d37101ba1300ba331e3d9ed8413_t3.mp4"
        extractor = VideoFrameExtractor(
            video_url=video_url,
            output_folder="extracted_frames",
            interval=5,
            quality=95,
            max_width=1920,
            start_time=0,
            end_time=None
        )
        extractor.run()
    else:
        main()