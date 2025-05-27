import argparse
import sys
from .extractor import VideoFrameExtractor

def main():
    """Command line interface for the video frame extractor"""
    parser = argparse.ArgumentParser(
        description='Video Frame Extractor Library - Extract frames from videos',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  video-extractor "https://example.com/video.mp4"
  video-extractor "url" -o frames -i 3 -q 90 -w 800
  video-extractor "url" -s 30 -e 120 -i 2 --no-play
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
    parser.add_argument('--no-play', action='store_true',
                       help='Skip video playback, only extract frames')
    parser.add_argument('--no-report', action='store_true',
                       help='Skip creating summary report')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       default='INFO', help='Logging level (default: INFO)')
    
    args = parser.parse_args()
    
    if args.interval <= 0:
        print("Error: Interval must be greater than 0")
        sys.exit(1)
    
    if args.start < 0:
        print("Error: Start time cannot be negative")
        sys.exit(1)
    
    if args.end and args.end <= args.start:
        print("Error: End time must be greater than start time")
        sys.exit(1)
    
    extractor = VideoFrameExtractor(
        video_url=args.url,
        output_folder=args.output,
        interval=args.interval,
        quality=args.quality,
        max_width=args.width,
        start_time=args.start,
        end_time=args.end,
        log_level=args.log_level
    )
    
    success = extractor.run(
        play_video=not args.no_play,
        create_report=not args.no_report
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()