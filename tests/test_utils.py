
import pytest
from unittest.mock import Mock, patch
from video_frame_extractor.utils import validate_url, sanitize_filename, setup_logging

class TestUtils:

    @patch('video_frame_extractor.utils.requests.head')
    def test_validate_url_with_video_content_type(self, mock_head):
        """Test URL validation with video content type"""
        mock_response = Mock()
        mock_response.headers = {'content-type': 'video/mp4'}
        mock_head.return_value = mock_response
        
        result = validate_url("https://example.com/video.mp4")
        assert result is True

    @patch('video_frame_extractor.utils.requests.head')
    def test_validate_url_with_video_extension(self, mock_head):
        """Test URL validation with video file extension"""
        mock_response = Mock()
        mock_response.headers = {'content-type': 'application/octet-stream'}
        mock_head.return_value = mock_response
        
        result = validate_url("https://example.com/video.mp4")
        assert result is True

    @patch('video_frame_extractor.utils.requests.head')
    def test_validate_url_exception(self, mock_head):
        """Test URL validation when request fails"""
        mock_head.side_effect = Exception("Network error")
        
        result = validate_url("https://example.com/video.mp4")
        assert result is True 
    
    def test_sanitize_filename(self):
        """Test filename sanitization"""
        result = sanitize_filename("video<>:\"|?*.mp4")
        assert '<' not in result
        assert '>' not in result
        assert ':' not in result
        assert '"' not in result
        assert '|' not in result
        assert '?' not in result
        assert '*' not in result
        
        result = sanitize_filename("normal_video.mp4")
        assert result == "normal_video.mp4"
        
        result = sanitize_filename("video___with___underscores.mp4")
        assert "___" not in result
    
    def test_setup_logging(self):
        """Test logging setup"""
        import tempfile
        
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = setup_logging(temp_dir, "DEBUG")
            
            assert logger.name == "video_frame_extractor"
            assert len(logger.handlers) == 2 
            logger.info("Test message")

            import os
            log_file = os.path.join(temp_dir, 'extraction_log.txt')
            assert os.path.exists(log_file)
