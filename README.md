# video-frame-extractor-cv

[![PyPI version](https://badge.fury.io/py/video-frame-extractor-cv.svg)](https://badge.fury.io/py/video-frame-extractor-cv)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

A lightweight Python library for downloading videos and extracting frames at precise intervals. It handles direct URLs, supports sub-second extraction, and includes metadata analysis and an interactive player for debugging.

## Features

- **Direct Download:** Process videos directly from URLs without manual downloading.
- **Precise Extraction:** Support for decimal intervals (e.g., every 0.5 seconds).
- **Smart resizing:** Resize frames on the fly to save storage.
- **Metadata:** Automatically extracts FPS, duration, and resolution data.
- **Interactive Mode:** Optional built-in player to preview or control the process.
- **Robust:** Includes retry logic, logging, and summary reports.

## Installation

```bash
pip install video-frame-extractor-cv
````

For development or building from source:

```bash
git clone https://github.com/chibuezedev/video-frame-extractor.git
cd video-frame-extractor
pip install -e .
```

## Quick Start

### Command Line Interface (CLI)

The library ships with a `video-extractor` entry point for quick operations.

```bash
# basic: download and extract frames every 5s (default)
video-extractor "https://example.com/video.mp4"

# advanced: extract every 0.5s, resize to width 1280px, skip playback
video-extractor "https://example.com/video.mp4" -i 0.5 -w 1280 --no-play

# specific range: extract from 00:30 to 01:00
video-extractor "https://example.com/video.mp4" -s 30 -e 60
```

### Python Usage

The recommended way to use the library is via the context manager, which handles cleanup automatically.

```python
from video_frame_extractor import VideoFrameExtractor

# use context manager to handle resources automatically
with VideoFrameExtractor("https://example.com/video.mp4") as extractor:
    # this downloads the video and extracts metadata
    extractor.download_video()
    
    # get info before processing
    meta = extractor.get_video_metadata()
    print(f"processing {meta['duration_seconds']}s video...")
    
    # run extraction
    count = extractor.extract_frames()
    print(f"done. extracted {count} frames.")
```

## Advanced Configuration

You can customize the extractor behavior extensively via the constructor.

```python
extractor = VideoFrameExtractor(
    video_url="https://example.com/video.mp4",
    output_folder="dataset/train",
    interval=2.5,    # extract frame every 2.5 seconds
    quality=90,      # jpeg quality (1-100)
    max_width=1280,  # downscale if width > 1280
    start_time=10,   # start at 10s mark
    end_time=60,     # stop at 60s mark
    log_level="DEBUG"
)

# run() wraps download, extraction, and reporting in one call
extractor.run(play_video=False, create_report=True)
```

## Output Structure

The library organizes outputs into a clean directory structure:

```text
output_folder/
├── frame_0000_time_0.0s.jpg    # extracted frames
├── frame_0001_time_2.5s.jpg
├── video_metadata.json         # resolution, fps, source info
├── extraction_report.txt       # human-readable summary
└── extraction_log.txt          # debug logs
```

## CLI Options Reference

| Flag | Short | Description | Default |
|------|-------|-------------|---------|
| `--output` | `-o` | Output directory | `frames` |
| `--interval` | `-i` | Time between frames (seconds) | `5` |
| `--quality` | `-q` | JPEG quality (1-100) | `95` |
| `--width` | `-w` | Max frame width (px) | `None` |
| `--start` | `-s` | Start timestamp (seconds) | `0` |
| `--end` | `-e` | End timestamp (seconds) | `None` |
| `--no-play` | | Disable interactive player | `False` |

## Interactive Player Controls

If you run without `--no-play`, an OpenCV window will open.

  * **`q`**: Quit
  * **`p`**: Pause/Resume
  * **`r`**: Restart
  * **`f` / `b`**: Seek forward/back 10s

## Recipes

### Batch Processing

Process a list of URLs and organize them into separate folders.

```python
urls = [
    "https://example.com/clip1.mp4",
    "https://example.com/clip2.mp4"
]

for i, url in enumerate(urls):
    folder = f"data/clip_{i}"
    
    # initialize and run in one go
    extractor = VideoFrameExtractor(url, output_folder=folder)
    if extractor.run(play_video=False):
        print(f"finished {url}")
    else:
        print(f"failed {url}")
```

### Scene Extraction

Extract frames from specific time ranges within a single video.

```python
# (start_time, end_time) tuples
scenes = [(30, 60), (120, 180)]

for start, end in scenes:
    extractor = VideoFrameExtractor(
        "https://example.com/movie.mp4",
        output_folder=f"frames/{start}_{end}",
        start_time=start,
        end_time=end,
        interval=1.0
    )
    extractor.run(play_video=False)
```
#### Individual Operations
```python
from video_frame_extractor import VideoFrameExtractor

extractor = VideoFrameExtractor("https://example.com/video.mp4", interval=1.0)

# download only
if extractor.download_video():
    print("Video downloaded successfully")

# metadata
metadata = extractor.get_video_metadata()
print(f"Video duration: {metadata.get('duration_seconds', 0):.1f} seconds")

# extract frames without playing
frames_extracted = extractor.extract_frames()
print(f"Extracted {frames_extracted} frames")

# play video separately
extractor.play_video(show_controls=True)

# create report
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

# validate video URL
is_valid = validate_url("https://example.com/video.mp4")
print(f"URL is valid: {is_valid}")

# clean filename
clean_name = sanitize_filename("my video [1080p].mp4")
print(f"Clean filename: {clean_name}")
```

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

## Error Handling

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

## Troubleshooting

**OpenCV Errors:**
If you see errors related to `cv2` or `libGL`, you might need the headless version of OpenCV for server environments:

```bash
pip install opencv-python-headless
```

**Download Failures:**
Ensure the URL is a direct link to a file (ends in .mp4, .avi, etc). For YouTube links, use a tool like `yt-dlp` to get the direct stream URL first.

## Contributing

1.  Fork the repo
2.  Create your feature branch (`git checkout -b feature/cool-feature`)
3.  Commit changes (`git commit -m 'add cool feature'`)
4.  Push to branch (`git push origin feature/cool-feature`)
5.  Open a Pull Request

For support, please:
1. Check the [troubleshooting section](#troubleshooting)
2. Search [existing issues](https://github.com/chibuezedev/video-frame-extractor/issues)
3. Create a [new issue](https://github.com/chibuezedev/video-frame-extractor/issues/new)

## License

Distributed under the MIT License. See `LICENSE` for more information.
