'use client';

import { useState, useEffect, useRef } from 'react';
import styles from './ShareModal.module.css';

interface ShareModalProps {
  isOpen: boolean;
  onClose: () => void;
  shareUrl: string;
}

export default function ShareModal({ isOpen, onClose, shareUrl }: ShareModalProps) {
  const [copied, setCopied] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.select();
    }
  }, [isOpen]);

  const handleCopyUrl = () => {
    if (inputRef.current) {
      inputRef.current.select();
      document.execCommand('copy');
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  if (!isOpen) return null;

  return (
    <div className={styles.shareModal} onClick={onClose}>
      <div className={styles.shareModalContent} onClick={e => e.stopPropagation()}>
        <h3 className={styles.shareModalTitle}>Share Video</h3>
        <input 
          type="text" 
          className={styles.shareModalInput} 
          value={shareUrl} 
          readOnly 
          ref={inputRef}
        />
        <div className={styles.shareModalButtons}>
          <button 
            className={`${styles.shareModalButton} ${styles.shareModalCancel}`} 
            onClick={onClose}
          >
            Cancel
          </button>
          <button 
            className={`${styles.shareModalButton} ${styles.shareModalShare}`} 
            onClick={handleCopyUrl}
          >
            {copied ? 'Copied!' : 'Copy Link'}
          </button>
        </div>
      </div>
    </div>
  );
} 