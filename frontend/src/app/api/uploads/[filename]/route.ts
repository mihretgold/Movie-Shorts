import { NextRequest, NextResponse } from 'next/server';
import { join } from 'path';
import { existsSync } from 'fs';
import { readFile } from 'fs/promises';

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

    const filepath = join(process.cwd(), 'public', 'uploads', filename);
    
    if (!existsSync(filepath)) {
      return NextResponse.json(
        { error: 'File not found' },
        { status: 404 }
      );
    }

    const fileBuffer = await readFile(filepath);
    
    // Determine the content type based on the file extension
    const contentType = filename.endsWith('.mp4') 
      ? 'video/mp4' 
      : 'application/octet-stream';

    return new NextResponse(fileBuffer, {
      headers: {
        'Content-Type': contentType
      }
    });
  } catch (error) {
    console.error('Error serving uploaded video:', error);
    return NextResponse.json(
      { error: 'Error serving uploaded video' },
      { status: 500 }
    );
  }
} 