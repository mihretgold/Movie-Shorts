from flask import Blueprint, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
from pathlib import Path
from moviepy.video.io.VideoFileClip import VideoFileClip
import uuid
import logging
import traceback

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
video_bp = Blueprint('video', __name__)

# Configure upload folder
UPLOAD_FOLDER = Path(__file__).parent.parent / 'uploads'
CUTS_FOLDER = Path(__file__).parent.parent / 'cuts'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_video_info(filepath):
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

@video_bp.route('/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400
    
    file = request.files['video']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            
            # Save file in chunks
            file.save(filepath)
            
            # Get video information
            video_info = get_video_info(filepath)
            
            return jsonify({
                'message': 'Video uploaded successfully',
                'filename': filename,
                'duration': video_info['duration'],
                'fps': video_info['fps'],
                'size': video_info['size']
            }), 200
        except Exception as e:
            logger.error(f"Error during upload: {str(e)}")
            logger.error(traceback.format_exc())
            # Clean up the file if it exists
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'error': f'Error processing video: {str(e)}'}), 500
    
    return jsonify({'error': 'Invalid file type'}), 400

@video_bp.route('/cut', methods=['POST'])
def cut_video():
    try:
        data = request.json
        filename = data.get('filename')
        start_time = float(data.get('startTime', 0))
        end_time = float(data.get('endTime', 0))
        
        if not filename:
            return jsonify({'error': 'No filename provided'}), 400
        
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        
        if not os.path.exists(input_path):
            return jsonify({'error': 'Video file not found'}), 404
        
        # Generate unique filename for the cut
        cut_filename = f"cut_{uuid.uuid4().hex[:8]}_{filename}"
        output_path = os.path.join(CUTS_FOLDER, cut_filename)
        
        logger.info(f"Starting video cut: {input_path} -> {output_path}")
        logger.info(f"Time range: {start_time} - {end_time}")
        
        with VideoFileClip(input_path) as video:
            # Validate time range
            if start_time < 0 or end_time > video.duration or start_time >= end_time:
                return jsonify({'error': 'Invalid time range'}), 400
            
            # Cut the video
            cut = video.subclipped(start_time, end_time)
            
            # Use specific codec settings
            cut.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                threads=4,
                preset='ultrafast'
            )
            
            logger.info(f"Video cut completed successfully: {cut_filename}")
            
            return jsonify({
                'message': 'Video cut successfully',
                'cut_filename': cut_filename
            }), 200
            
    except Exception as e:
        logger.error(f"Error during video cut: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': f'Error cutting video: {str(e)}'}), 500

@video_bp.route('/uploads/<filename>')
def serve_video(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@video_bp.route('/cuts/<filename>')
def serve_cut(filename):
    return send_from_directory(CUTS_FOLDER, filename) 