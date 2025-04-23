'use client';

import { useState } from 'react';
import styles from './SubtitlesData.module.css';

interface SubtitlesDataProps {
  onGetSubtitles: () => Promise<any>;
  onAnalyzeSubtitles: (subtitles: any) => Promise<void>;
}

export default function SubtitlesData({ onGetSubtitles, onAnalyzeSubtitles }: SubtitlesDataProps) {
  const [subtitlesData, setSubtitlesData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const handleGetSubtitles = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const data = await onGetSubtitles();
      setSubtitlesData(data);
    } catch (error) {
      setError('Error fetching subtitles data');
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAnalyzeSubtitles = async () => {
    if (!subtitlesData || !subtitlesData.subtitles) {
      setError('No subtitles data available');
      return;
    }

    setIsAnalyzing(true);
    setError(null);
    
    try {
      await onAnalyzeSubtitles(subtitlesData.subtitles);
    } catch (error) {
      setError('Error analyzing subtitles');
      console.error(error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className={styles.subtitlesDataContainer}>
      <h2 className={styles.subtitlesDataTitle}>Subtitles Data</h2>
      <div className={styles.subtitlesDataControls}>
        <button 
          className={styles.getSubtitlesButton} 
          onClick={handleGetSubtitles}
          disabled={isLoading}
        >
          Get Subtitles Data
        </button>
        <button 
          className={styles.analyzeSubtitlesButton} 
          onClick={handleAnalyzeSubtitles}
          disabled={!subtitlesData || isAnalyzing}
        >
          Analyze with AI
        </button>
      </div>
      <div className={styles.subtitlesDataContent}>
        {isLoading ? (
          <p>Loading subtitles data...</p>
        ) : error ? (
          <p className={styles.error}>{error}</p>
        ) : subtitlesData ? (
          <pre className={styles.subtitlesDataDisplay}>
            {JSON.stringify(subtitlesData, null, 2)}
          </pre>
        ) : (
          <p>No subtitles data available</p>
        )}
      </div>
    </div>
  );
} 