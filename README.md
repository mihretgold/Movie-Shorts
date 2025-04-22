# Movie Shorts

A web application that automatically creates engaging YouTube Shorts from longer videos by analyzing content and extracting the most interesting segments.

## Features

- Upload and process long-form videos
- Automatic content analysis using Whisper and FFmpeg
- Smart segment selection based on duration and content
- Automatic formatting for YouTube Shorts (9:16 aspect ratio)
- Modern, responsive web interface
- Real-time processing status updates

## Tech Stack

### Frontend
- Next.js 14
- TypeScript
- Tailwind CSS
- React

### Backend
- Python
- FastAPI
- FFmpeg
- Whisper (OpenAI)
- MoviePy

## Prerequisites

- Node.js 18+ and npm
- Python 3.8+
- FFmpeg (automatically downloaded if not present)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/movie-shorts.git
cd movie-shorts
```

2. Set up the backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Set up the frontend:
```bash
cd frontend
npm install
```

## Development

1. Start the backend server:
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python run.py
```

2. Start the frontend development server:
```bash
cd frontend
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Usage

1. Upload a video file through the web interface
2. Wait for the processing to complete
3. Download or share the generated Shorts

## Project Structure

```
movie-shorts/
├── frontend/           # Next.js frontend application
│   ├── src/           # Source code
│   ├── public/        # Static assets
│   └── package.json   # Frontend dependencies
├── backend/           # Python backend application
│   ├── app/          # Backend source code
│   ├── tests/        # Backend tests
│   └── requirements.txt  # Backend dependencies
└── README.md         # Project documentation
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for Whisper
- FFmpeg team
- MoviePy developers
- Next.js team 