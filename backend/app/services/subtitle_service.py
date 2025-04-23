"""
Subtitle Service Module
Provides functionality for handling video subtitles including extraction, parsing, and formatting.
"""

import os
import logging
from faster_whisper import WhisperModel
from ..utils.video_utils import generate_srt, extract_subtitles, timestamp_to_seconds

# Configure logging
logger = logging.getLogger(__name__)

class SubtitleService:
    """
    Service class for handling subtitle-related operations.
    Includes methods for extracting embedded subtitles, parsing SRT files,
    and formatting subtitle data.
    """
    
    def __init__(self, model_size="small"):
        """Initialize the subtitle service with default configurations."""
        self.model = WhisperModel(model_size)

    def transcribe_with_whisper(self, filepath, output_path):
        """Transcribe video using Whisper and save as SRT"""
        try:
            # Transcribe the video
            segments, info = self.model.transcribe(filepath)
            language = info.language
            segments = list(segments)
            
            # Generate SRT file
            generate_srt(segments, output_path)
            
            return True
        except Exception as e:
            logger.error(f"Error transcribing with Whisper: {str(e)}")
            return False

    def get_subtitles_json(self, filepath, subtitles_folder):
        """Get subtitles in JSON format"""
        try:
            # First try to extract embedded subtitles
            subtitle_path = extract_subtitles(filepath, os.path.basename(filepath), subtitles_folder)
            
            # If no embedded subtitles found, use Whisper to generate them
            if not subtitle_path:
                logger.info("No embedded subtitles found, using Whisper to generate subtitles")
                
                # Transcribe the video
                segments, info = self.model.transcribe(filepath)
                language = info.language
                segments = list(segments)
                
                # Format subtitles as a list of dictionaries
                formatted_subtitles = []
                for segment in segments:
                    formatted_subtitles.append({
                        'start': segment.start,
                        'end': segment.end,
                        'text': segment.text.strip()
                    })
                
                return {
                    'subtitles': formatted_subtitles,
                    'language': language,
                    'source': 'whisper'
                }
            
            # If embedded subtitles were found, parse the SRT file
            with open(subtitle_path, 'r', encoding='utf-8') as f:
                srt_content = f.read()
                
            # Parse SRT content into a structured format
            subtitle_blocks = srt_content.strip().split('\n\n')
            formatted_subtitles = []
            
            for block in subtitle_blocks:
                lines = block.strip().split('\n')
                if len(lines) >= 3:
                    # Parse timestamp line
                    timestamp_line = lines[1]
                    start_time, end_time = timestamp_line.split(' --> ')
                    
                    start_seconds = timestamp_to_seconds(start_time)
                    end_seconds = timestamp_to_seconds(end_time)
                    
                    # Get subtitle text
                    text = ' '.join(lines[2:])
                    
                    formatted_subtitles.append({
                        'start': start_seconds,
                        'end': end_seconds,
                        'text': text
                    })
            
            return {
                'subtitles': formatted_subtitles,
                'language': 'unknown',  # SRT doesn't typically include language info
                'source': 'embedded'
            }
            
        except Exception as e:
            logger.error(f"Error extracting subtitles: {str(e)}")
            raise 