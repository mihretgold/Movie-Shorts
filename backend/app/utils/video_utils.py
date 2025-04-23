import os
from pathlib import Path
import subprocess
import json
import logging
from moviepy.video.io.VideoFileClip import VideoFileClip
import traceback

# Configure logging
logger = logging.getLogger(__name__)

def format_timestamp(seconds):
    """Convert seconds to SRT timestamp format"""
    from datetime import timedelta
    td = timedelta(seconds=seconds)
    hours = td.seconds // 3600
    minutes = (td.seconds % 3600) // 60
    seconds = td.seconds % 60
    milliseconds = int(td.microseconds / 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

def generate_srt(segments, output_path):
    """Generate SRT file from Whisper segments"""
    with open(output_path, 'w', encoding='utf-8') as f:
        for i, segment in enumerate(segments, 1):
            start_time = format_timestamp(segment.start)
            end_time = format_timestamp(segment.end)
            text = segment.text.strip()
            f.write(f"{i}\n{start_time} --> {end_time}\n{text}\n\n")

def allowed_file(filename):
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_video_info(filepath):
    """Get video metadata"""
    try:
        with VideoFileClip(filepath) as clip:
            return {
                'duration': clip.duration,
                'fps': clip.fps,
                'size': (clip.w, clip.h)
            }
    except Exception as e:
        logger.error(f"Error getting video info: {str(e)}")
        logger.error(traceback.format_exc())
        raise

def check_subtitles(filepath):
    """Check if video has embedded subtitles"""
    try:
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_streams',
            filepath
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        data = json.loads(result.stdout)
        
        subtitle_streams = [
            stream for stream in data.get('streams', [])
            if stream.get('codec_type') == 'subtitle'
        ]
        
        return len(subtitle_streams) > 0
    except Exception as e:
        logger.error(f"Error checking subtitles: {str(e)}")
        return False

def extract_subtitles(filepath, filename, subtitles_folder):
    """Extract embedded subtitles from video"""
    try:
        subtitle_path = os.path.join(subtitles_folder, f"{os.path.splitext(filename)[0]}.srt")
        
        cmd = [
            'ffmpeg',
            '-i', filepath,
            '-map', '0:s:0',
            subtitle_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if os.path.exists(subtitle_path) and os.path.getsize(subtitle_path) > 0:
            return subtitle_path
        return None
    except Exception as e:
        logger.error(f"Error extracting subtitles: {str(e)}")
        return None

def timestamp_to_seconds(timestamp):
    """Convert SRT timestamp to seconds"""
    h, m, s = timestamp.replace(',', '.').split(':')
    return int(h) * 3600 + int(m) * 60 + float(s) 