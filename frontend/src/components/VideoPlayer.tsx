'use client';

import { useRef, useEffect } from 'react';
import styles from './VideoPlayer.module.css';

interface VideoPlayerProps {
  src: string;
  title: string;
  onDurationChange?: (duration: number) => void;
}

export default function VideoPlayer({ src, title, onDurationChange }: VideoPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    const video = videoRef.current;
    if (video && onDurationChange) {
      const handleLoadedMetadata = () => {
        onDurationChange(video.duration);
      };

      video.addEventListener('loadedmetadata', handleLoadedMetadata);
      return () => {
        video.removeEventListener('loadedmetadata', handleLoadedMetadata);
      };
    }
  }, [onDurationChange]);

  return (
    <div className={styles.videoContainer}>
      <div className={styles.videoTitle}>{title}</div>
      <video 
        className={styles.videoPlayer} 
        ref={videoRef}
        controls
        src={src}
      >
        Your browser does not support the video tag.
      </video>
    </div>
  );
} 