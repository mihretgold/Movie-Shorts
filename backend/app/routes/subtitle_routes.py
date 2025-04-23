"""
Subtitle Routes Module
Handles all subtitle-related endpoints including extraction, checking, and retrieval.
"""

from flask import Blueprint, request, jsonify, send_from_directory
import os
from pathlib import Path
import logging
from werkzeug.utils import secure_filename
from ..services.subtitle_service import SubtitleService
from ..utils.video_utils import check_subtitles, allowed_file

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
subtitle_bp = Blueprint('subtitles', __name__)

# Initialize services
subtitle_service = SubtitleService()

@subtitle_bp.route('/check/<filename>')
def check_video_subtitles(filename):
    """
    Check if a video file has embedded subtitles or if AI transcription is available.
    Returns a boolean indicating subtitle availability.
    """
    try:
        filepath = os.path.join('uploads', filename)
        if not os.path.exists(filepath):
            return jsonify({'error': 'Video file not found'}), 404
        
        has_subtitles = check_subtitles(filepath)
        return jsonify({
            'has_subtitles': has_subtitles
        }), 200
    except Exception as e:
        logger.error(f"Error checking subtitles: {str(e)}")
        return jsonify({'error': str(e)}), 500

@subtitle_bp.route('/extract/<filename>')
def get_subtitles(filename):
    try:
        filepath = os.path.join('uploads', filename)
        if not os.path.exists(filepath):
            return jsonify({'error': 'Video file not found'}), 404
        
        # First try to extract embedded subtitles
        subtitle_path = subtitle_service.extract_subtitles(filepath, filename)
        
        # If no embedded subtitles found, use Whisper to generate them
        if not subtitle_path:
            logger.info("No embedded subtitles found, using Whisper to generate subtitles")
            subtitle_path = os.path.join('subtitles', f"{os.path.splitext(filename)[0]}_whisper.srt")
            if subtitle_service.transcribe_with_whisper(filepath, subtitle_path):
                return send_from_directory(
                    'subtitles',
                    os.path.basename(subtitle_path),
                    as_attachment=True
                )
            else:
                return jsonify({'error': 'Failed to generate subtitles'}), 500
        
        return send_from_directory(
            'subtitles',
            os.path.basename(subtitle_path),
            as_attachment=True
        )
    except Exception as e:
        logger.error(f"Error extracting subtitles: {str(e)}")
        return jsonify({'error': str(e)}), 500

@subtitle_bp.route('/get/<filename>')
def get_subtitles_json(filename):
    try:
        filepath = os.path.join('uploads', filename)
        if not os.path.exists(filepath):
            return jsonify({'error': 'Video file not found'}), 404
        
        result = subtitle_service.get_subtitles_json(filepath, 'subtitles')
        return jsonify(result), 200
            
    except Exception as e:
        logger.error(f"Error extracting subtitles: {str(e)}")
        return jsonify({'error': str(e)}), 500 