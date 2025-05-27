# Video Frame Extractor

A Python library for downloading videos from URLs and extracting frames at specified intervals with advanced features like video playback, metadata extraction, and customizable output options.

## Features

- 🎥 **Video Download**: Download from any direct video URL
- 🖼️ **Frame Extraction**: Extract frames at custom intervals (supports decimal seconds)
- ▶️ **Video Playback**: Interactive video player with controls
- 📊 **Metadata Extraction**: Comprehensive video information
- 🎛️ **Customizable Output**: Quality control, resizing, time ranges
- 📝 **Detailed Logging**: Progress tracking and error handling
- 📋 **Summary Reports**: Detailed extraction reports

## Installation

### From PyPI (when published)
```bash
pip install video-frame-extractor
```

### From Source
```bash
git clone https://github.com/chibuezedev/video-frame-extractor.git
cd video-frame-extractor
pip install -e .
```

### Development Installation
```bash
git clone https://github.com/chibuezedev/video-frame-extractor.git
cd video-frame-extractor
pip install -e ".[dev]"
```

## Quick Start

### Command Line Usage

```bash
# Basic usage
video-extractor "https://example.com/video.mp4"

# Advanced options
video-extractor "https://example.com/video.mp4" -o my_frames -i 2.5 -q 90 -w 1280

# Extract specific time range
video-extractor "https://example.com/video.mp4" -s 30 -e 120 -i 3

# Extract without playing video
video-extractor "https://example.com/video.mp4" --no-play
```

### Python API Usage

#### Basic Usage
```python
from video_frame_extractor import VideoFrameExtractor

# Simple extraction
extractor = VideoFrameExtractor("https://example.com/video.mp4")
extractor.run()
```

#### Advanced Usage
```python
from video_frame_extractor import VideoFrameExtractor

# Advanced configuration
extractor = VideoFrameExtractor(
    video_url="https://example.com/video.mp4",
    output_folder="my_frames",
    interval=2.5,  # Extract every 2.5 seconds
    quality=90,    # JPEG quality 90%
    max_width=1280,  # Resize to max 1280px width
    start_time=,   # Start once
    end_time=120,    # End at 120 seconds
    log_level="DEBUG"
)

success = extractor.run(play_video=True, create_report=True)
```

#### Context Manager Usage
```python
from video_frame_extractor import VideoFrameExtractor

# Automatic cleanup
with VideoFrameExtractor("https://example.com/video.mp4") as extractor:
    extractor.download_video()
    metadata = extractor.get_video_metadata()
    frames_count = extractor.extract_frames()
    print(f"Extracted {frames_count} frames")
```

#### Individual Operations
```python
from video_frame_extractor import VideoFrameExtractor

extractor = VideoFrameExtractor("https://example.com/video.mp4", interval=1.0)

# Download only
if extractor.download_video():
    print("Video downloaded successfully")

# Get metadata
metadata = extractor.get_video_metadata()
print(f"Video duration: {metadata.get('duration_seconds', 0):.1f} seconds")

# Extract frames without playing
frames_extracted = extractor.extract_frames()
print(f"Extracted {frames_extracted} frames")

# Play video separately
extractor.play_video(show_controls=True)

# Create report
report_path = extractor.create_summary_report()
print(f"Report saved to: {report_path}")
```

### Using the Video Player Separately
```python
from video_frame_extractor import VideoPlayer

player = VideoPlayer()
player.play("path/to/video.mp4", start_time=10, end_time=60)
```

### Utility Functions
```python
from video_frame_extractor import validate_url, sanitize_filename

# Validate video URL
is_valid = validate_url("https://example.com/video.mp4")
print(f"URL is valid: {is_valid}")

# Clean filename
clean_name = sanitize_filename("my video [1080p].mp4")
print(f"Clean filename: {clean_name}")
```

## Command Line Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--output` | `-o` | Output folder for frames | `frames` |
| `--interval` | `-i` | Interval between frames (seconds) | `5` |
| `--quality` | `-q` | JPEG quality (1-100) | `95` |
| `--width` | `-w` | Maximum frame width | `None` |
| `--start` | `-s` | Start time (seconds) | `0` |
| `--end` | `-e` | End time (seconds) | `None` |
| `--no-play` | | Skip video playback | `False` |
| `--no-report` | | Skip summary report | `False` |
| `--log-level` | | Logging level | `INFO` |

## Video Player Controls

When playing video (interactive mode):
- **`q`** - Quit playback
- **`p`** - Pause/unpause
- **`r`** - Restart from beginning
- **`f`** - Fast forward 10 seconds
- **`b`** - Rewind 10 seconds

## Output Files

The library creates several output files:

```
output_folder/
├── frame_0000_time_0.0s.jpg    # Extracted frames
├── frame_0001_time_5.0s.jpg
├── frame_0002_time_10.0s.jpg
├── ...
├── video_metadata.json         # Video information
├── extraction_report.txt       # Summary report
└── extraction_log.txt         # Detailed logs
```

### Metadata JSON Structure
```json
{
  "source_url": "https://example.com/video.mp4",
  "fps": 30.0,
  "total_frames": 1800,
  "width": 1920,
  "height": 1080,
  "duration_seconds": 60.0,
  "extraction_interval": 5.0,
  "extraction_time": "2024-01-15T10:30:00",
  "start_time": 0,
  "end_time": null,
  "quality": 95,
  "max_width": null,
  "frames_extracted": 12
}
```

## Requirements

- Python 3.7+
- OpenCV Python (cv2)
- Requests
- Pathlib2 (for Python < 3.4)

## Error Handling

The library includes comprehensive error handling:

```python
from video_frame_extractor import VideoFrameExtractor

try:
    extractor = VideoFrameExtractor("https://invalid-url.com/video.mp4")
    success = extractor.run()
    if not success:
        print("Extraction failed - check logs for details")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone and install in development mode
git clone https://github.com/chibuezedev/video-frame-extractor.git
cd video-frame-extractor
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run linting
flake8 video_frame_extractor/
black video_frame_extractor/
mypy video_frame_extractor/
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=video_frame_extractor

# Run specific test file
pytest tests/test_extractor.py
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### v1.0.0
- Initial release
- Video downloading and frame extraction
- Interactive video player
- Metadata extraction
- Command line interface
- Comprehensive logging and reporting

## Troubleshooting

### Common Issues

**1. OpenCV Installation Issues**
```bash
# Try installing with conda
conda install opencv

# Or use a specific OpenCV package
pip install opencv-python-headless
```

**2. Video Download Failures**
- Ensure the URL is a direct link to a video file
- Check internet connection
- Some servers may block automated downloads

**3. Frame Extraction Errors**
- Verify video file is not corrupted
- Check available disk space
- Ensure output directory permissions

**4. Video Playback Issues**
- Install OpenCV with GUI support
- On Linux, ensure X11 forwarding is enabled
- Use `--no-play` flag to skip playback

## Examples

### Extract Frames from YouTube-dl Downloaded Video
```python
# First download with youtube-dl
# youtube-dl -o "%(title)s.%(ext)s" "VIDEO_URL"

from video_frame_extractor import VideoFrameExtractor

# Then extract frames from local file
extractor = VideoFrameExtractor(
    "file:///path/to/downloaded_video.mp4",
    interval=1.0,
    output_folder="youtube_frames"
)
extractor.run()
```

### Batch Processing Multiple Videos
```python
from video_frame_extractor import VideoFrameExtractor
import os

video_urls = [
    "https://example.com/video1.mp4",
    "https://example.com/video2.mp4",
    "https://example.com/video3.mp4"
]

for i, url in enumerate(video_urls):
    output_folder = f"batch_frames_{i+1}"
    
    with VideoFrameExtractor(url, output_folder=output_folder) as extractor:
        success = extractor.run(play_video=False)
        if success:
            print(f"Successfully processed video {i+1}")
        else:
            print(f"Failed to process video {i+1}")
```

### Extract Specific Scenes
```python
from video_frame_extractor import VideoFrameExtractor

# Extract frames from multiple time ranges
scenes = [
    (30, 60),   # 30s to 60s
    (120, 180), # 2min to 3min
    (300, 360)  # 5min to 6min
]

for i, (start, end) in enumerate(scenes):
    extractor = VideoFrameExtractor(
        "https://example.com/movie.mp4",
        output_folder=f"scene_{i+1}",
        start_time=start,
        end_time=end,
        interval=0.5  # Extract every 0.5 seconds
    )
    extractor.run(play_video=False)
```

## API Reference

### VideoFrameExtractor Class

#### Constructor Parameters
- `video_url` (str): URL of the video to download and process
- `output_folder` (str, optional): Directory to save extracted frames (default: "frames")
- `interval` (float, optional): Time interval in seconds between frame extractions (default: 5.0)
- `quality` (int, optional): JPEG quality for saved frames, 1-100 (default: 95)
- `max_width` (int, optional): Maximum width for extracted frames (default: None)
- `start_time` (float, optional): Start time in seconds for extraction (default: 0)
- `end_time` (float, optional): End time in seconds for extraction (default: None)
- `log_level` (str, optional): Logging level (default: "INFO")

#### Methods
- `download_video(timeout=30, chunk_size=8192)`: Download video from URL
- `get_video_metadata()`: Extract and return video metadata
- `extract_frames()`: Extract frames at specified intervals
- `play_video(show_controls=True)`: Play the downloaded video
- `create_summary_report()`: Generate extraction report
- `run(play_video=True, create_report=True)`: Execute complete process

### VideoPlayer Class

#### Methods
- `play(video_path, start_time=0, end_time=None, show_controls=True)`: Play video file

### Utility Functions
- `validate_url(url, timeout=10)`: Check if URL is accessible video
- `sanitize_filename(filename)`: Clean filename for filesystem compatibility
- `setup_logging(output_folder, log_level="INFO")`: Configure logging

## Support

For support, please:
1. Check the [troubleshooting section](#troubleshooting)
2. Search [existing issues](https://github.com/chibuezedev/video-frame-extractor/issues)
3. Create a [new issue](https://github.com/chibuezedev/video-frame-extractor/issues/new) with:
   - Python version
   - Operating system
   - Error messages
   - Sample code that reproduces the issue

---

**Made with ❤️ for video processing enthusiasts**

# Additional Required Files

## LICENSE
```
MIT License

Copyright (c) 2024 Your Name

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```