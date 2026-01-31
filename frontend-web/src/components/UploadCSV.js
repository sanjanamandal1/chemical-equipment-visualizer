import React, { useState } from 'react';
import axios from 'axios';

function UploadCSV({ onUploadSuccess, isDarkMode }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [dragActive, setDragActive] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      alert('Please select a file');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    setLoading(true);
    try {
      const response = await axios.post(
        'http://localhost:8000/api/datasets/upload/',
        formData
      );
      onUploadSuccess(response.data);
      
      // Success animation
      const successMsg = document.createElement('div');
      successMsg.innerHTML = '✅ File uploaded successfully!';
      successMsg.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: linear-gradient(135deg, #14b8a6 0%, #0891b2 100%);
        color: white;
        padding: 15px 25px;
        border-radius: 10px;
        font-weight: 600;
        box-shadow: 0 4px 20px rgba(20, 184, 166, 0.4);
        z-index: 10000;
        animation: slideIn 0.3s ease;
      `;
      document.body.appendChild(successMsg);
      setTimeout(() => successMsg.remove(), 3000);
      
      setFile(null);
    } catch (error) {
      alert('Error uploading file: ' + (error.response?.data?.error || error.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container(isDarkMode)}>
      <h2 style={styles.title(isDarkMode)}>
        📁 Upload Dataset
      </h2>
      
      {/* Drag and Drop Zone */}
      <div
        style={styles.dropZone(isDarkMode, dragActive)}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          type="file"
          accept=".csv"
          onChange={handleFileChange}
          style={styles.hiddenInput}
          id="file-upload"
        />
        
        <label htmlFor="file-upload" style={styles.dropZoneLabel}>
          <div style={styles.uploadIcon(dragActive)}>
            📊
          </div>
          <p style={styles.dropText(isDarkMode)}>
            {dragActive ? 'Drop your CSV file here' : 'Drag & drop CSV file here'}
          </p>
          <p style={styles.dropSubtext(isDarkMode)}>
            or click to browse
          </p>
        </label>
      </div>

      {/* Selected File Display */}
      {file && (
        <div style={styles.filePreview(isDarkMode)}>
          <div style={styles.fileIcon}>📄</div>
          <div style={styles.fileInfo}>
            <p style={styles.fileName(isDarkMode)}>{file.name}</p>
            <p style={styles.fileSize(isDarkMode)}>
              {(file.size / 1024).toFixed(2)} KB
            </p>
          </div>
          <button
            onClick={() => setFile(null)}
            style={styles.removeButton(isDarkMode)}
          >
            ✕
          </button>
        </div>
      )}

      {/* Upload Button */}
      <button
        onClick={handleUpload}
        disabled={loading || !file}
        style={styles.uploadButton(loading, !file)}
        onMouseOver={(e) => !loading && file && (e.currentTarget.style.transform = 'translateY(-2px)')}
        onMouseOut={(e) => (e.currentTarget.style.transform = 'translateY(0)')}
      >
        {loading ? (
          <>
            <span style={styles.spinner}>⏳</span>
            Uploading...
          </>
        ) : (
          <>
            <span>🚀</span>
            Upload & Analyze
          </>
        )}
      </button>
    </div>
  );
}

const styles = {
  container: (isDark) => ({
    padding: '30px',
    background: isDark ? '#1a202c' : 'linear-gradient(135deg, #f0fdfa 0%, #ffffff 100%)',
    borderRadius: '15px',
    marginBottom: '30px',
    border: isDark ? '2px solid #4a5568' : '2px solid #99f6e4',
    transition: 'all 0.3s ease'
  }),
  title: (isDark) => ({
    margin: '0 0 25px 0',
    fontSize: '24px',
    fontWeight: '700',
    color: isDark ? '#e2e8f0' : '#134E4A',
    display: 'flex',
    alignItems: 'center',
    gap: '10px'
  }),
  dropZone: (isDark, active) => ({
    border: active 
      ? '3px dashed #14b8a6' 
      : isDark ? '3px dashed #4a5568' : '3px dashed #99f6e4',
    borderRadius: '15px',
    padding: '50px 20px',
    textAlign: 'center',
    background: active 
      ? 'rgba(20, 184, 166, 0.1)' 
      : isDark ? '#2d3748' : '#ffffff',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    position: 'relative'
  }),
  hiddenInput: {
    display: 'none'
  },
  dropZoneLabel: {
    cursor: 'pointer',
    display: 'block'
  },
  uploadIcon: (active) => ({
    fontSize: '64px',
    marginBottom: '15px',
    transform: active ? 'scale(1.1)' : 'scale(1)',
    transition: 'transform 0.2s ease'
  }),
  dropText: (isDark) => ({
    fontSize: '18px',
    fontWeight: '600',
    color: isDark ? '#e2e8f0' : '#134E4A',
    margin: '10px 0'
  }),
  dropSubtext: (isDark) => ({
    fontSize: '14px',
    color: isDark ? '#94a3b8' : '#0d9488',
    margin: '5px 0'
  }),
  filePreview: (isDark) => ({
    display: 'flex',
    alignItems: 'center',
    gap: '15px',
    padding: '15px 20px',
    background: isDark ? '#2d3748' : '#f0fdfa',
    borderRadius: '12px',
    margin: '20px 0',
    border: isDark ? '2px solid #4a5568' : '2px solid #99f6e4'
  }),
  fileIcon: {
    fontSize: '32px'
  },
  fileInfo: {
    flex: 1
  },
  fileName: (isDark) => ({
    margin: '0 0 5px 0',
    fontSize: '15px',
    fontWeight: '600',
    color: isDark ? '#e2e8f0' : '#134E4A'
  }),
  fileSize: (isDark) => ({
    margin: 0,
    fontSize: '13px',
    color: isDark ? '#94a3b8' : '#0d9488'
  }),
  removeButton: (isDark) => ({
    background: isDark ? '#4a5568' : '#fee2e2',
    color: isDark ? '#e2e8f0' : '#ef4444',
    border: 'none',
    borderRadius: '8px',
    width: '32px',
    height: '32px',
    cursor: 'pointer',
    fontSize: '16px',
    fontWeight: 'bold',
    transition: 'all 0.2s ease'
  }),
  uploadButton: (loading, disabled) => ({
    width: '100%',
    padding: '15px',
    background: disabled 
      ? '#94a3b8' 
      : 'linear-gradient(135deg, #14b8a6 0%, #0891b2 100%)',
    color: 'white',
    border: 'none',
    borderRadius: '12px',
    fontSize: '16px',
    fontWeight: '700',
    cursor: disabled ? 'not-allowed' : 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '10px',
    marginTop: '20px',
    transition: 'all 0.3s ease',
    boxShadow: disabled ? 'none' : '0 4px 20px rgba(20, 184, 166, 0.3)',
    opacity: disabled ? 0.6 : 1
  }),
  spinner: {
    display: 'inline-block',
    animation: 'spin 1s linear infinite'
  }
};

export default UploadCSV;