import json
import logging
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configure Google Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Configure logging
logger = logging.getLogger(__name__)

class AnalysisService:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-flash',
            generation_config={
                'temperature': 0.7,
                'top_k': 1,
                'top_p': 0.8,
                'max_output_tokens': 2048,
            }
        )

    def analyze_subtitles(self, subtitles):
        """Analyze subtitles and find engaging sections"""
        if not subtitles:
            raise ValueError('No subtitles provided')
        
        # Calculate video duration from subtitles
        if subtitles:
            video_duration = max(subtitle['end'] for subtitle in subtitles)
            # Calculate number of sections based on video length
            # Formula: For every 5 minutes of video, we want 2-3 sections
            # Minimum 3 sections, maximum 10 sections
            sections_per_5min = 2.5  # Average number of sections per 5 minutes
            num_sections = min(max(3, int((video_duration / 300) * sections_per_5min)), 10)
        else:
            num_sections = 3  # Default if no subtitles
        
        # Prepare the prompt for Gemini with dynamic number of sections
        prompt = f"""You are a Shorts Editor AI. I will give you subtitles from a video with start and end timestamps in seconds. Find {num_sections} engaging sections that each last **60 to 70 seconds** (can cross subtitle boundaries). Each section should be either funny, emotionally engaging, or contain important information.

IMPORTANT: Your response must be a valid JSON array ONLY, with no markdown formatting, no code blocks, and no additional text.
The response must be in this exact format:
[
  {{"start": <start_time_in_seconds>, "end": <end_time_in_seconds>, "type": "funny/emotional/informative"}},
  {{"start": <start_time_in_seconds>, "end": <end_time_in_seconds>, "type": "funny/emotional/informative"}},
  ...
]

Subtitles:
{json.dumps(subtitles, indent=2)}
"""
        
        # Call Gemini API
        response = self.model.generate_content(prompt)
        
        # Extract and clean the response
        result = response.text.strip()
        
        # Remove any markdown code block formatting if present
        result = result.replace('```json', '').replace('```', '').strip()
        
        # Parse the JSON response
        try:
            result_json = json.loads(result)
            # Validate that we got an array of sections
            if not isinstance(result_json, list):
                raise json.JSONDecodeError("Response is not an array", result, 0)
            return result_json
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing Gemini response: {result}")
            logger.error(f"JSON decode error: {str(e)}")
            raise ValueError('Invalid response from Gemini') 