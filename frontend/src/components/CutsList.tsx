'use client';

import CutVideo from './CutVideo';
import styles from './CutsList.module.css';

interface CutsListProps {
  cuts: string[];
}

export default function CutsList({ cuts }: CutsListProps) {
  return (
    <div className={styles.cutsContainer}>
      <h2 className={styles.cutsTitle}>Cut Videos</h2>
      <div className={styles.cutsList}>
        {cuts.length > 0 ? (
          cuts.map((filename, index) => (
            <CutVideo key={index} filename={filename} />
          ))
        ) : (
          <p>No cut videos available</p>
        )}
      </div>
    </div>
  );
} 