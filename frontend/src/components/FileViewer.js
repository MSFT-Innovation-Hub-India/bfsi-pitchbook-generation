import React, { useState, useEffect } from 'react';
import './FileViewer.css';

const FileViewer = () => {
  const [loading, setLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileContent, setFileContent] = useState('');
  const [error, setError] = useState(null);

  // Static list of files in the public folder
  const files = [
    { name: 'ams_concall_transcript.pdf', type: 'pdf', size: 0, url: '/ams_concall_transcript.pdf', description: 'Apollo Micro Systems Conference Call Transcript' },
    { name: 'ams_quaterly_reports.pdf', type: 'pdf', size: 0, url: '/ams_quaterly_reports.pdf', description: 'Apollo Micro Systems Quarterly Reports' },
    { name: 'vodafone_concall_transcript.pdf', type: 'pdf', size: 0, url: '/vodafone_concall_transcript.pdf', description: 'Vodafone Idea Conference Call Transcript' },
    { name: 'vodafone_quaterly_reports.pdf', type: 'pdf', size: 0, url: '/vodafone_quaterly_reports.pdf', description: 'Vodafone Idea Quarterly Reports' },
  ];

  useEffect(() => {
    // Initialize - files are static, no need to fetch
    setLoading(false);
  }, []);

  const handleFileClick = async (file) => {
    setSelectedFile(file);
    setFileContent('');
    setError(null);

    // For PDF files, show inline viewer
    if (file.type === 'pdf') {
      setSelectedFile(file);
      return;
    }

    // For text files, fetch and display content
    if (file.type === 'txt') {
      try {
        setLoading(true);
        const response = await fetch(file.url);
        if (!response.ok) throw new Error('Failed to fetch file content');
        const content = await response.text();
        setFileContent(content);
      } catch (err) {
        setError(`Failed to load file: ${err.message}`);
      } finally {
        setLoading(false);
      }
    }
  };

  const downloadFile = (file) => {
    const link = document.createElement('a');
    link.href = file.url;
    link.download = file.name;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const openInNewTab = (file) => {
    window.open(file.url, '_blank');
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return 'N/A';
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  const getFileIcon = (type) => {
    switch (type) {
      case 'pdf':
        return '📄';
      case 'txt':
        return '📝';
      default:
        return '📎';
    }
  };

  if (loading) {
    return (
      <div className="file-viewer">
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading files...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="file-viewer">
      <div className="file-viewer-header">
        <h2>📁 Document Library</h2>
        <p className="subtitle">Reference documents and format specifications</p>
      </div>

      {error && (
        <div className="error-banner">
          <span className="error-icon">⚠️</span>
          <span>{error}</span>
          <button onClick={() => setError(null)} className="retry-btn">Dismiss</button>
        </div>
      )}

      <div className="files-grid">
        {files.map((file, index) => (
          <div key={index} className="file-card">
            <div className="file-icon">{getFileIcon(file.type)}</div>
            <div className="file-info">
              <h3 className="file-name" title={file.name}>{file.name}</h3>
              {file.description && (
                <p className="file-description">{file.description}</p>
              )}
              <p className="file-meta">
                <span className="file-type">{file.type.toUpperCase()}</span>
                {file.size > 0 && <span className="file-size">{formatFileSize(file.size)}</span>}
              </p>
            </div>
            <div className="file-actions">
              <button
                className="btn-view"
                onClick={() => handleFileClick(file)}
                title={file.type === 'pdf' ? 'View PDF' : 'View content'}
              >
                👁️ View
              </button>
              {file.type === 'pdf' && (
                <button
                  className="btn-open"
                  onClick={() => openInNewTab(file)}
                  title="Open in new tab"
                >
                  🗗 Open
                </button>
              )}
              <button
                className="btn-download"
                onClick={() => downloadFile(file)}
                title="Download file"
              >
                ⬇️ Download
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Text File Viewer */}
      {selectedFile && selectedFile.type === 'txt' && fileContent && (
        <div className="content-viewer">
          <div className="content-header">
            <h3>📄 {selectedFile.name}</h3>
            <button onClick={() => setSelectedFile(null)} className="close-btn">
              ✕
            </button>
          </div>
          <div className="content-body">
            <pre>{fileContent}</pre>
          </div>
        </div>
      )}

      {/* PDF Viewer Modal */}
      {selectedFile && selectedFile.type === 'pdf' && (
        <div className="pdf-viewer-modal">
          <div className="pdf-viewer-container">
            <div className="pdf-viewer-header">
              <div className="pdf-info">
                <h3>📄 {selectedFile.name}</h3>
                <p className="pdf-description">{selectedFile.description}</p>
              </div>
              <div className="pdf-actions">
                <button onClick={() => openInNewTab(selectedFile)} className="btn-new-tab">
                  🗗 Open in New Tab
                </button>
                <button onClick={() => downloadFile(selectedFile)} className="btn-download-pdf">
                  ⬇️ Download
                </button>
                <button onClick={() => setSelectedFile(null)} className="close-btn">
                  ✕
                </button>
              </div>
            </div>
            <div className="pdf-viewer-body">
              <iframe
                src={selectedFile.url}
                title={selectedFile.name}
                width="100%"
                height="100%"
                style={{ border: 'none' }}
              />
            </div>
          </div>
        </div>
      )}

      <div className="quick-links">
        <h3>📚 Document Categories</h3>
        <div className="quick-links-grid">
          <div className="category-card">
            <span className="link-icon">📋</span>
            <span className="link-text">Format Specifications</span>
            <span className="link-count">1 file</span>
          </div>
          <div className="category-card">
            <span className="link-icon">📊</span>
            <span className="link-text">Pitchbook Samples</span>
            <span className="link-count">1 file</span>
          </div>
          <div className="category-card">
            <span className="link-icon">📞</span>
            <span className="link-text">Conference Call Transcripts</span>
            <span className="link-count">2 files</span>
          </div>
          <div className="category-card">
            <span className="link-icon">📈</span>
            <span className="link-text">Quarterly Reports</span>
            <span className="link-count">2 files</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FileViewer;
