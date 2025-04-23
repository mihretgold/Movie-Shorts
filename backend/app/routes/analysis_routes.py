from flask import Blueprint, request, jsonify
import logging
import traceback
from ..services.analysis_service import AnalysisService

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
analysis_bp = Blueprint('analysis', __name__)

# Initialize services
analysis_service = AnalysisService()

@analysis_bp.route('/analyze-subtitles', methods=['POST'])
def analyze_subtitles():
    try:
        data = request.json
        subtitles = data.get('subtitles', [])
        
        sections = analysis_service.analyze_subtitles(subtitles)
        return jsonify({"sections": sections})
            
    except ValueError as e:
        logger.error(f"Error analyzing subtitles: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error analyzing subtitles: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500 