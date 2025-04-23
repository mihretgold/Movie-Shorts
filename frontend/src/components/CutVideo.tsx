'use client';

import styles from './CutVideo.module.css';

interface CutVideoProps {
  filename: string;
}

export default function CutVideo({ filename }: CutVideoProps) {
  return (
    <div className={styles.cutItem}>
      <div className={styles.videoTitle}>{filename}</div>
      <video className={styles.videoPlayer} controls>
        <source src={`/api/cuts/${filename}`} type="video/mp4" />
        Your browser does not support the video tag.
      </video>
    </div>
  );
} 