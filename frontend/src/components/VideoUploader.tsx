'use client';

import { useState, useRef, ChangeEvent, DragEvent } from 'react';
import styles from './VideoUploader.module.css';

interface VideoUploaderProps {
  onVideoUploaded: (filename: string, duration: number) => void;
}

export default function VideoUploader({ onVideoUploaded }: VideoUploaderProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [status, setStatus] = useState('');
  const [fileSize, setFileSize] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const handleFiles = (files: FileList | null) => {
    if (files && files.length > 0) {
      const file = files[0];
      if (file.type.startsWith('video/')) {
        uploadFile(file);
      } else {
        setStatus('Please upload a video file');
      }
    }
  };

  const uploadFile = (file: File) => {
    setUploadProgress(0);
    setStatus('Uploading...');
    setFileSize(`File size: ${formatFileSize(file.size)}`);

    const formData = new FormData();
    formData.append('video', file);

    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/api/upload', true);

    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable) {
        const percentComplete = (e.loaded / e.total) * 100;
        setUploadProgress(percentComplete);
        
        // Update status with upload details
        const uploaded = formatFileSize(e.loaded);
        const total = formatFileSize(e.total);
        setStatus(`Uploading: ${uploaded} of ${total} (${Math.round(percentComplete)}%)`);
      }
    };

    xhr.onload = function() {
      if (xhr.status === 200) {
        const response = JSON.parse(xhr.responseText);
        setStatus(response.message);
        onVideoUploaded(response.filename, response.duration);
      } else {
        const response = JSON.parse(xhr.responseText);
        setStatus('Error: ' + response.error);
      }
      setFileSize(null);
    };

    xhr.onerror = function() {
      setStatus('Upload failed. Please try again.');
      setFileSize(null);
    };

    xhr.send(formData);
  };

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    handleFiles(e.dataTransfer.files);
  };

  const handleFileInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    handleFiles(e.target.files);
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className={styles.container}>
      <div 
        className={`${styles.uploadArea} ${isDragging ? styles.dragover : ''}`}
        onClick={handleClick}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <div className={styles.uploadIcon}>📁</div>
        <div className={styles.uploadText}>Drag and drop your video here</div>
        <div className={styles.uploadHint}>or click to select a file</div>
        <input 
          type="file" 
          ref={fileInputRef}
          onChange={handleFileInputChange}
          accept="video/*"
          className={styles.fileInput}
        />
        {fileSize && <div className={styles.fileSize}>{fileSize}</div>}
      </div>
      
      {uploadProgress > 0 && (
        <div className={styles.progressBar}>
          <div 
            className={styles.progress} 
            style={{ width: `${uploadProgress}%` }}
          ></div>
        </div>
      )}
      
      {status && <div className={styles.status}>{status}</div>}
    </div>
  );
} 