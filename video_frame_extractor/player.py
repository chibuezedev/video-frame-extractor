import cv2
import logging
from typing import Optional

class VideoPlayer:
    """Video player with enhanced controls"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.is_playing = False
    
    def play(self, 
             video_path: str,
             start_time: float = 0,
             end_time: Optional[float] = None,
             show_controls: bool = True) -> None:
        """
        Play video with controls.
        
        Args:
            video_path (str): Path to video file
            start_time (float): Start time in seconds
            end_time (Optional[float]): End time in seconds
            show_controls (bool): Whether to show control instructions
        """
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                self.logger.error("Could not open video file for playback")
                return
            
            self.is_playing = True
            fps = cap.get(cv2.CAP_PROP_FPS)
            delay = int(1000 / fps) if fps > 0 else 33
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            if start_time > 0:
                start_frame = int(start_time * fps)
                cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
            
            if show_controls:
                self.logger.info("Playing video... Controls:")
                self.logger.info("'q' - quit, 'p' - pause/unpause, 'r' - restart")
                self.logger.info("'f' - fast forward 10s, 'b' - rewind 10s")
            
            paused = False
            current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
            
            while self.is_playing:
                if not paused:
                    ret, frame = cap.read()
                    current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
                    
                    if not ret or (end_time and current_frame >= end_time * fps):
                        break
                    
                    # Resize frame for display
                    display_frame = frame.copy()
                    height, width = display_frame.shape[:2]
                    if width > 1200:
                        scale = 1200 / width
                        new_width = int(width * scale)
                        new_height = int(height * scale)
                        display_frame = cv2.resize(display_frame, (new_width, new_height))
                    
                    # Add time overlay
                    current_time = current_frame / fps
                    time_text = f"Time: {current_time:.1f}s"
                    cv2.putText(display_frame, time_text, (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    
                    cv2.imshow('Video Player', display_frame)
                
                key = cv2.waitKey(delay) & 0xFF
                
                if key == ord('q'):
                    break
                elif key == ord('p'):
                    paused = not paused
                    if show_controls:
                        status = "Paused" if paused else "Resumed"
                        self.logger.info(status)
                elif key == ord('r'):
                    start_frame = int(start_time * fps) if start_time > 0 else 0
                    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
                    paused = False
                    if show_controls:
                        self.logger.info("Video restarted")
                elif key == ord('f'):  # forward 10 seconds
                    new_frame = min(current_frame + int(10 * fps), total_frames - 1)
                    cap.set(cv2.CAP_PROP_POS_FRAMES, new_frame)
                    if show_controls:
                        self.logger.info("Fast forward 10s")
                elif key == ord('b'):  # Rewind 10 seconds
                    new_frame = max(current_frame - int(10 * fps), 0)
                    cap.set(cv2.CAP_PROP_POS_FRAMES, new_frame)
                    if show_controls:
                        self.logger.info("Rewind 10s")
            
            cap.release()
            cv2.destroyAllWindows()
            self.is_playing = False
            
        except Exception as e:
            self.logger.error(f"Error playing video: {e}")