'use client';

import { useState, ChangeEvent } from 'react';
import styles from './CutControls.module.css';

interface CutControlsProps {
  videoDuration: number;
  onCutVideo: (startTime: number, endTime: number) => Promise<void>;
  onGetSubtitles: () => Promise<void>;
  hasSubtitles: boolean;
  subtitleStatus: string;
}

export default function CutControls({ 
  videoDuration, 
  onCutVideo, 
  onGetSubtitles,
  hasSubtitles,
  subtitleStatus
}: CutControlsProps) {
  const [startTime, setStartTime] = useState(0);
  const [endTime, setEndTime] = useState(videoDuration);
  const [isCutting, setIsCutting] = useState(false);
  const [status, setStatus] = useState('');

  const handleStartTimeChange = (e: ChangeEvent<HTMLInputElement>) => {
    const value = parseFloat(e.target.value);
    if (value >= 0 && value < videoDuration) {
      setStartTime(value);
      if (value >= endTime) {
        setEndTime(Math.min(value + 1, videoDuration));
      }
    }
  };

  const handleEndTimeChange = (e: ChangeEvent<HTMLInputElement>) => {
    const value = parseFloat(e.target.value);
    if (value > startTime && value <= videoDuration) {
      setEndTime(value);
    }
  };

  const handleCutVideo = async () => {
    if (startTime >= endTime || startTime < 0 || endTime > videoDuration) {
      setStatus('Invalid time range');
      return;
    }

    setIsCutting(true);
    setStatus('Cutting video...');

    try {
      await onCutVideo(startTime, endTime);
      setStatus('Video cut successfully!');
    } catch (error) {
      setStatus('Error cutting video');
      console.error(error);
    } finally {
      setIsCutting(false);
    }
  };

  return (
    <div className={styles.cutControls}>
      <div className={styles.timeInputs}>
        <div className={styles.timeInput}>
          <label htmlFor="startTime">Start Time (seconds)</label>
          <input 
            type="number" 
            id="startTime" 
            min="0" 
            max={videoDuration - 0.1}
            step="0.1" 
            value={startTime} 
            onChange={handleStartTimeChange}
          />
        </div>
        <div className={styles.timeInput}>
          <label htmlFor="endTime">End Time (seconds)</label>
          <input 
            type="number" 
            id="endTime" 
            min={startTime + 0.1}
            max={videoDuration}
            step="0.1" 
            value={endTime} 
            onChange={handleEndTimeChange}
          />
        </div>
      </div>
      <button 
        className={styles.cutButton} 
        onClick={handleCutVideo}
        disabled={isCutting}
      >
        Cut Video
      </button>
      <button 
        className={styles.subtitleButton} 
        onClick={onGetSubtitles}
        disabled={!hasSubtitles}
      >
        Get Subtitles
      </button>
      {subtitleStatus && (
        <div className={styles.subtitleStatus}>{subtitleStatus}</div>
      )}
      {status && <div className={styles.status}>{status}</div>}
    </div>
  );
} 