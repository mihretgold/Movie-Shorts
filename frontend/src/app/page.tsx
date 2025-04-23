'use client';

import { useState, useEffect } from 'react';
import VideoUploader from '@/components/VideoUploader';
import VideoPlayer from '@/components/VideoPlayer';
import CutControls from '@/components/CutControls';
import CutsList from '@/components/CutsList';
import SubtitlesData from '@/components/SubtitlesData';
import AiAnalysis from '@/components/AiAnalysis';
import ShareModal from '@/components/ShareModal';
import styles from './page.module.css';

export default function Home() {
  const [currentVideo, setCurrentVideo] = useState<{
    filename: string;
    duration: number;
  } | null>(null);
  const [cuts, setCuts] = useState<string[]>([]);
  const [hasSubtitles, setHasSubtitles] = useState(false);
  const [subtitleStatus, setSubtitleStatus] = useState('');
  const [aiSections, setAiSections] = useState<any[]>([]);
  const [isShareModalOpen, setIsShareModalOpen] = useState(false);
  const [shareUrl, setShareUrl] = useState('');

  // Handle video upload
  const handleVideoUploaded = (filename: string, duration: number) => {
    setCurrentVideo({ filename, duration });
    setCuts([]);
    setAiSections([]);
    checkSubtitles(filename);
  };

  // Check if video has subtitles
  const checkSubtitles = async (filename: string) => {
    try {
      const response = await fetch(`/api/check-subtitles/${filename}`);
      const data = await response.json();
      
      if (data.has_subtitles) {
        setHasSubtitles(true);
        setSubtitleStatus('Subtitles available');
      } else {
        setHasSubtitles(true);
        setSubtitleStatus('No embedded subtitles found. Click to generate subtitles using AI.');
      }
    } catch (error) {
      setHasSubtitles(false);
      setSubtitleStatus('Error checking for subtitles');
      console.error(error);
    }
  };

  // Handle video cutting
  const handleCutVideo = async (startTime: number, endTime: number) => {
    if (!currentVideo) return;

    try {
      const response = await fetch('/api/cut', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          filename: currentVideo.filename,
          startTime: startTime,
          endTime: endTime
        })
      });

      const data = await response.json();

      if (response.ok) {
        setCuts(prev => [data.cut_filename, ...prev]);
        return data.cut_filename;
      } else {
        throw new Error(data.error);
      }
    } catch (error) {
      console.error('Error cutting video:', error);
      throw error;
    }
  };

  // Handle getting subtitles
  const handleGetSubtitles = async () => {
    if (!currentVideo) return;

    try {
      setSubtitleStatus('Processing... This may take a few minutes for AI transcription.');
      
      const response = await fetch(`/api/extract-subtitles/${currentVideo.filename}`);
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${currentVideo.filename.split('.')[0]}.srt`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        setSubtitleStatus('Subtitles downloaded successfully!');
      } else {
        const data = await response.json();
        setSubtitleStatus('Error: ' + data.error);
      }
    } catch (error) {
      setSubtitleStatus('Error extracting subtitles');
      console.error(error);
    }
  };

  // Handle getting subtitles data
  const handleGetSubtitlesData = async () => {
    if (!currentVideo) return null;

    try {
      const response = await fetch(`/api/get-subtitles/${currentVideo.filename}`);
      if (response.ok) {
        return await response.json();
      } else {
        const errorData = await response.json();
        throw new Error(errorData.error);
      }
    } catch (error) {
      console.error('Error getting subtitles data:', error);
      throw error;
    }
  };

  // Handle analyzing subtitles
  const handleAnalyzeSubtitles = async (subtitles: any) => {
    try {
      const response = await fetch('/api/analyze-subtitles', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ subtitles })
      });
      
      if (response.ok) {
        const data = await response.json();
        setAiSections(data.sections);
      } else {
        const errorData = await response.json();
        throw new Error(errorData.error);
      }
    } catch (error) {
      console.error('Error analyzing subtitles:', error);
      throw error;
    }
  };

  // Handle applying AI cut
  const handleApplyAiCut = async (start: number, end: number) => {
    return handleCutVideo(start, end);
  };

  // Handle downloading cut video
  const handleDownloadCut = async (filename: string) => {
    try {
      const response = await fetch(`/api/cuts/${filename}`);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Error downloading video:', error);
    }
  };

  // Handle sharing video
  const handleShareVideo = (filename: string, platform: string) => {
    const url = `${window.location.origin}/api/cuts/${filename}`;
    setShareUrl(url);
    setIsShareModalOpen(true);
  };

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Movie Shorts</h1>
      
      <VideoUploader onVideoUploaded={handleVideoUploaded} />
      
      {currentVideo && (
        <>
          <VideoPlayer 
            src={`/api/uploads/${currentVideo.filename}`} 
            title={currentVideo.filename}
            onDurationChange={(duration) => {
              if (currentVideo.duration !== duration) {
                setCurrentVideo({ ...currentVideo, duration });
              }
            }}
          />
          
          <CutControls 
            videoDuration={currentVideo.duration}
            onCutVideo={handleCutVideo}
            onGetSubtitles={handleGetSubtitles}
            hasSubtitles={hasSubtitles}
            subtitleStatus={subtitleStatus}
          />
          
          <CutsList cuts={cuts} />
          
          <SubtitlesData 
            onGetSubtitles={handleGetSubtitlesData}
            onAnalyzeSubtitles={handleAnalyzeSubtitles}
          />
          
          {aiSections.length > 0 && (
            <AiAnalysis 
              sections={aiSections}
              onApplyCut={handleApplyAiCut}
              onDownloadCut={handleDownloadCut}
              onShareVideo={handleShareVideo}
              currentFilename={currentVideo.filename}
            />
          )}
        </>
      )}
      
      <ShareModal 
        isOpen={isShareModalOpen}
        onClose={() => setIsShareModalOpen(false)}
        shareUrl={shareUrl}
      />
    </div>
  );
}
