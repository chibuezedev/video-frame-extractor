import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from video_frame_extractor import VideoFrameExtractor

class TestVideoFrameExtractor:
    
    def test_init(self):
        """Test initialization with default parameters"""
        extractor = VideoFrameExtractor("https://example.com/video.mp4")
        assert extractor.video_url == "https://example.com/video.mp4"
        assert extractor.output_folder == "frames"
        assert extractor.interval == 5.0
        assert extractor.quality == 95
    
    def test_init_with_params(self):
        """Test initialization with custom parameters"""
        extractor = VideoFrameExtractor(
            "https://example.com/video.mp4",
            output_folder="custom_frames",
            interval=2.5,
            quality=80,
            max_width=1280,
            start_time=10,
            end_time=60
        )
        assert extractor.output_folder == "custom_frames"
        assert extractor.interval == 2.5
        assert extractor.quality == 80
        assert extractor.max_width == 1280
        assert extractor.start_time == 10
        assert extractor.end_time == 60
    
    @patch('video_frame_extractor.extractor.requests.get')
    def test_download_video_success(self, mock_get):
        """Test successful video download"""
        mock_response = Mock()
        mock_response.headers = {'content-length': '1000'}
        mock_response.iter_content.return_value = [b'chunk1', b'chunk2']
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        extractor = VideoFrameExtractor("https://example.com/video.mp4")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            result = extractor.download_video()
            assert result is True
            assert extractor.video_path is not None
    
    @patch('video_frame_extractor.extractor.requests.get')
    def test_download_video_failure(self, mock_get):
        """Test failed video download"""
        mock_get.side_effect = Exception("Network error")
        
        extractor = VideoFrameExtractor("https://example.com/video.mp4")
        result = extractor.download_video()
        assert result is False
    
    @patch('video_frame_extractor.extractor.cv2.VideoCapture')
    def test_get_video_metadata(self, mock_cv2):
        """Test video metadata extraction"""
        mock_cap = Mock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = lambda prop: {
            0: 30.0,  # FPS
            7: 1800,  # Frame count
            3: 1920,  # Width
            4: 1080   # Height
        }.get(prop, 0)
        mock_cv2.return_value = mock_cap
        
        extractor = VideoFrameExtractor("https://example.com/video.mp4")
        extractor.video_path = "test_video.mp4"
        
        with tempfile.TemporaryDirectory() as temp_dir:
            extractor.output_folder = temp_dir
            metadata = extractor.get_video_metadata()
            
            assert metadata['fps'] == 30.0
            assert metadata['total_frames'] == 1800
            assert metadata['width'] == 1920
            assert metadata['height'] == 1080
            assert metadata['duration_seconds'] == 60.0
    
    def test_context_manager(self):
        """Test context manager functionality"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b"fake video content")
            temp_path = temp_file.name
        
        try:
            with VideoFrameExtractor("https://example.com/video.mp4") as extractor:
                extractor.video_path = temp_path
            
            assert not os.path.exists(temp_path)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)