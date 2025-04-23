'use client';

import { useState } from 'react';
import styles from './AiAnalysis.module.css';

interface Section {
  type: string;
  start: number;
  end: number;
}

interface AiAnalysisProps {
  sections: Section[];
  onApplyCut: (start: number, end: number) => Promise<void>;
  onDownloadCut: (filename: string) => Promise<void>;
  onShareVideo: (filename: string, platform: string) => void;
  currentFilename: string;
}

export default function AiAnalysis({ 
  sections, 
  onApplyCut, 
  onDownloadCut,
  onShareVideo,
  currentFilename
}: AiAnalysisProps) {
  const [selectedSection, setSelectedSection] = useState<Section | null>(null);
  const [isProcessing, setIsProcessing] = useState<{[key: string]: boolean}>({});
  const [cutFilenames, setCutFilenames] = useState<{[key: string]: string}>({});

  const handleApplyCut = async (section: Section) => {
    const sectionKey = `${section.start}-${section.end}`;
    setIsProcessing(prev => ({ ...prev, [sectionKey]: true }));
    
    try {
      await onApplyCut(section.start, section.end);
      setSelectedSection(section);
    } catch (error) {
      console.error('Error applying cut:', error);
    } finally {
      setIsProcessing(prev => ({ ...prev, [sectionKey]: false }));
    }
  };

  const handleDownloadCut = async (sectionKey: string) => {
    const cutFilename = cutFilenames[sectionKey];
    if (cutFilename) {
      try {
        await onDownloadCut(cutFilename);
      } catch (error) {
        console.error('Error downloading cut:', error);
      }
    }
  };

  const handleShareVideo = (sectionKey: string, platform: string) => {
    const cutFilename = cutFilenames[sectionKey];
    if (cutFilename) {
      onShareVideo(cutFilename, platform);
    }
  };

  return (
    <div className={styles.aiSectionsContainer}>
      <h2 className={styles.aiSectionsTitle}>AI Recommended Sections</h2>
      <div className={styles.aiSectionsList}>
        {sections.length > 0 ? (
          sections.map((section, index) => {
            const sectionKey = `${section.start}-${section.end}`;
            const isSelected = selectedSection && 
              selectedSection.start === section.start && 
              selectedSection.end === section.end;
            
            return (
              <div key={index} className={styles.aiSectionItem}>
                <div className={styles.aiSectionHeader}>
                  <span className={styles.aiSectionType}>{section.type}</span>
                  <span className={styles.aiSectionTime}>
                    {section.start}s - {section.end}s
                  </span>
                </div>
                <button 
                  className={styles.aiSectionApply} 
                  onClick={() => handleApplyCut(section)}
                  disabled={isProcessing[sectionKey]}
                >
                  {isProcessing[sectionKey] ? 'Processing...' : 'Apply This Cut'}
                </button>
                
                {isSelected && cutFilenames[sectionKey] && (
                  <div className={styles.aiSectionPreview}>
                    <div className={styles.aiSectionPreviewTitle}>Preview:</div>
                    <video controls>
                      <source src={`/api/cuts/${cutFilenames[sectionKey]}`} type="video/mp4" />
                      Your browser does not support the video tag.
                    </video>
                    <div className={styles.aiSectionActions}>
                      <button 
                        className={styles.aiSectionDownload} 
                        onClick={() => handleDownloadCut(sectionKey)}
                      >
                        Download Cut Video
                      </button>
                      <div className={styles.shareButtons}>
                        <button 
                          className={`${styles.shareButton} ${styles.shareTwitter}`} 
                          onClick={() => handleShareVideo(sectionKey, 'twitter')}
                          title="Share on Twitter"
                        >
                          𝕏
                        </button>
                        <button 
                          className={`${styles.shareButton} ${styles.shareFacebook}`} 
                          onClick={() => handleShareVideo(sectionKey, 'facebook')}
                          title="Share on Facebook"
                        >
                          f
                        </button>
                        <button 
                          className={`${styles.shareButton} ${styles.shareInstagram}`} 
                          onClick={() => handleShareVideo(sectionKey, 'instagram')}
                          title="Share on Instagram"
                        >
                          📸
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })
        ) : (
          <p>No AI sections available</p>
        )}
      </div>
    </div>
  );
} 