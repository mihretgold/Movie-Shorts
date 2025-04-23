"""
Movie Shorts - Video Processing Application
Main application entry point that configures Flask and registers blueprints.
"""

from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
from pathlib import Path
from moviepy.video.io.VideoFileClip import VideoFileClip
import uuid
import logging
import traceback
import subprocess
import json
import datetime
from faster_whisper import WhisperModel
import google.generativeai as genai
from dotenv import load_dotenv
from flask_cors import CORS
from app.routes.subtitle_routes import subtitle_bp
from app.routes.analysis_routes import analysis_bp
from app.routes.video_routes import video_bp

# Load environment variables
load_dotenv()

# Configure Google Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(subtitle_bp, url_prefix='/api/subtitles')
    app.register_blueprint(analysis_bp, url_prefix='/api/analysis')
    app.register_blueprint(video_bp, url_prefix='/api/video')
    
    # Ensure upload directories exist
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('cuts', exist_ok=True)
    os.makedirs('subtitles', exist_ok=True)
    
    # Configure upload folder
    UPLOAD_FOLDER = Path(__file__).parent / 'uploads'
    CUTS_FOLDER = Path(__file__).parent / 'cuts'
    SUBTITLES_FOLDER = Path(__file__).parent / 'subtitles'
    ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm'}

    # Create necessary directories
    UPLOAD_FOLDER.mkdir(exist_ok=True)
    CUTS_FOLDER.mkdir(exist_ok=True)
    SUBTITLES_FOLDER.mkdir(exist_ok=True)

    # Increase max file size to 2GB (2 * 1024 * 1024 * 1024 bytes)
    app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 * 1024
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['CUTS_FOLDER'] = CUTS_FOLDER
    app.config['SUBTITLES_FOLDER'] = SUBTITLES_FOLDER

    # Configure chunk size for large file uploads
    CHUNK_SIZE = 1024 * 1024  # 1MB chunks

    # Initialize Whisper model
    model = WhisperModel("small")

    def format_timestamp(seconds):
        """Convert seconds to SRT timestamp format"""
        td = datetime.timedelta(seconds=seconds)
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

    def transcribe_with_whisper(filepath, output_path):
        """Transcribe video using Whisper and save as SRT"""
        try:
            # Transcribe the video
            segments, info = model.transcribe(filepath)
            language = info.language
            segments = list(segments)
            
            # Generate SRT file
            generate_srt(segments, output_path)
            
            return True
        except Exception as e:
            logger.error(f"Error transcribing with Whisper: {str(e)}")
            return False

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

    def check_subtitles(filepath):
        try:
            # Use ffprobe to check for subtitles
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_streams',
                filepath
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            data = json.loads(result.stdout)
            
            # Check for subtitle streams
            subtitle_streams = [
                stream for stream in data.get('streams', [])
                if stream.get('codec_type') == 'subtitle'
            ]
            
            return len(subtitle_streams) > 0
        except Exception as e:
            logger.error(f"Error checking subtitles: {str(e)}")
            return False

    def extract_subtitles(filepath, filename):
        try:
            subtitle_path = os.path.join(app.config['SUBTITLES_FOLDER'], f"{os.path.splitext(filename)[0]}.srt")
            
            # Extract subtitles using ffmpeg
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

    @app.route('/health', methods=['GET'])
    def health_check():
        return {'status': 'healthy'}, 200

    @app.route('/')
    def serve_index():
        return send_from_directory('static', 'index.html')

    @app.route('/upload', methods=['POST'])
    def upload_video():
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
        
        file = request.files['video']
        
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if file and allowed_file(file.filename):
            try:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
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

    # Add error handler for large files
    @app.errorhandler(413)
    def request_entity_too_large(error):
        return jsonify({'error': 'File is too large. Maximum size is 2GB.'}), 413

    @app.route('/cut', methods=['POST'])
    def cut_video():
        try:
            data = request.json
            filename = data.get('filename')
            start_time = float(data.get('startTime', 0))
            end_time = float(data.get('endTime', 0))
            
            if not filename:
                return jsonify({'error': 'No filename provided'}), 400
            
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            if not os.path.exists(input_path):
                return jsonify({'error': 'Video file not found'}), 404
            
            # Generate unique filename for the cut
            cut_filename = f"cut_{uuid.uuid4().hex[:8]}_{filename}"
            output_path = os.path.join(app.config['CUTS_FOLDER'], cut_filename)
            
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

    @app.route('/uploads/<filename>')
    def serve_video(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    @app.route('/cuts/<filename>')
    def serve_cut(filename):
        return send_from_directory(app.config['CUTS_FOLDER'], filename)

    @app.route('/check-subtitles/<filename>')
    def check_video_subtitles(filename):
        try:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if not os.path.exists(filepath):
                return jsonify({'error': 'Video file not found'}), 404
            
            has_subtitles = check_subtitles(filepath)
            return jsonify({
                'has_subtitles': has_subtitles
            }), 200
        except Exception as e:
            logger.error(f"Error checking subtitles: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/extract-subtitles/<filename>')
    def get_subtitles(filename):
        try:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if not os.path.exists(filepath):
                return jsonify({'error': 'Video file not found'}), 404
            
            # First try to extract embedded subtitles
            subtitle_path = extract_subtitles(filepath, filename)
            
            # If no embedded subtitles found, use Whisper to generate them
            if not subtitle_path:
                logger.info("No embedded subtitles found, using Whisper to generate subtitles")
                subtitle_path = os.path.join(app.config['SUBTITLES_FOLDER'], f"{os.path.splitext(filename)[0]}_whisper.srt")
                if transcribe_with_whisper(filepath, subtitle_path):
                    return send_from_directory(
                        app.config['SUBTITLES_FOLDER'],
                        os.path.basename(subtitle_path),
                        as_attachment=True
                    )
                else:
                    return jsonify({'error': 'Failed to generate subtitles'}), 500
            
            return send_from_directory(
                app.config['SUBTITLES_FOLDER'],
                os.path.basename(subtitle_path),
                as_attachment=True
            )
        except Exception as e:
            logger.error(f"Error extracting subtitles: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/get-subtitles/<filename>')
    def get_subtitles_json(filename):
        try:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if not os.path.exists(filepath):
                return jsonify({'error': 'Video file not found'}), 404
            
            # First try to extract embedded subtitles
            subtitle_path = extract_subtitles(filepath, filename)
            
            # If no embedded subtitles found, use Whisper to generate them
            if not subtitle_path:
                logger.info("No embedded subtitles found, using Whisper to generate subtitles")
                
                # Transcribe the video
                segments, info = model.transcribe(filepath)
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
                
                return jsonify({
                    'subtitles': formatted_subtitles,
                    'language': language,
                    'source': 'whisper'
                })
            
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
                    
                    # Convert timestamp to seconds
                    def timestamp_to_seconds(timestamp):
                        h, m, s = timestamp.replace(',', '.').split(':')
                        return int(h) * 3600 + int(m) * 60 + float(s)
                    
                    start_seconds = timestamp_to_seconds(start_time)
                    end_seconds = timestamp_to_seconds(end_time)
                    
                    # Get subtitle text
                    text = ' '.join(lines[2:])
                    
                    formatted_subtitles.append({
                        'start': start_seconds,
                        'end': end_seconds,
                        'text': text
                    })
            
            return jsonify({
                'subtitles': formatted_subtitles,
                'language': 'unknown',  # SRT doesn't typically include language info
                'source': 'embedded'
            })
            
        except Exception as e:
            logger.error(f"Error extracting subtitles: {str(e)}")
            return jsonify({'error': str(e)}), 500

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000) 