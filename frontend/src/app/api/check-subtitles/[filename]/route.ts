import { NextRequest, NextResponse } from 'next/server';
import { join } from 'path';
import { existsSync } from 'fs';

export async function GET(
  request: NextRequest,
  { params }: { params: { filename: string } }
) {
  try {
    const { filename } = params;
    
    if (!filename) {
      return NextResponse.json(
        { error: 'Filename is required' },
        { status: 400 }
      );
    }

    // In a real application, you would check if the video has embedded subtitles
    // For now, we'll just return a placeholder response
    const hasSubtitles = true; // Placeholder value

    return NextResponse.json({
      has_subtitles: hasSubtitles
    });
  } catch (error) {
    console.error('Error checking subtitles:', error);
    return NextResponse.json(
      { error: 'Error checking subtitles' },
      { status: 500 }
    );
  }
} 