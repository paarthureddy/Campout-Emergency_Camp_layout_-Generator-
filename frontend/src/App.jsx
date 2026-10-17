import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import UploadSection from './components/UploadSection';
import Developers from './components/Developers';

function Home({ jobStatus, setJobStatus, results, setResults, errorMessage, setErrorMessage, onReset }) {
  const handleUpload = async (file, modelName, scenarioParams = {}) => {
    setJobStatus('uploading');
    setErrorMessage('');
    
    // Create instant local URL as guarantee for uploaded image display
    const localImgUrl = scenarioParams.localPreviewUrl || URL.createObjectURL(file);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('model', modelName);

    try {
      setJobStatus('processing');
      let response;
      try {
        response = await fetch('/api/upload', {
          method: 'POST',
          body: formData,
        });
      } catch {
        response = await fetch('http://127.0.0.1:8000/api/upload', {
          method: 'POST',
          body: formData,
        });
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Backend processing failed');
      }

      const data = await response.json();
      
      setJobStatus('completed');
      setResults({
        metrics:          data.results,
        original_url:     data.original_url || localImgUrl,
        blueprint_url:    data.blueprint_url,
        segmentation_url: data.segmentation_url,
        scenarioParams:   scenarioParams,
      });
    } catch (error) {
      console.error('Error uploading file:', error);
      setErrorMessage(error.message || 'Image processing failed. Is the backend running?');
      setJobStatus('error');
    }
  };

  if (jobStatus === 'error') {
    return (
      <main>
        <div className="glass-panel" style={{ padding: '2.5rem', textAlign: 'center', maxWidth: '600px', margin: '2rem auto' }}>
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>⚠️</div>
          <h3 style={{ color: 'var(--danger)', marginBottom: '0.8rem' }}>Processing Error</h3>
          <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem', lineHeight: '1.6' }}>
            {errorMessage || 'Failed to process satellite image. Please verify the backend server is running on port 8000.'}
          </p>
          <button 
            onClick={onReset} 
            className="btn-primary"
            style={{ padding: '0.75rem 1.6rem', fontSize: '1rem', cursor: 'pointer' }}
          >
            ← Back to Create Map / Try Again
          </button>
        </div>
      </main>
    );
  }

  return (
    <main>
      {jobStatus === null ? (
        <UploadSection onUpload={handleUpload} />
      ) : (
        <Dashboard status={jobStatus} results={results} onBack={onReset} />
      )}
    </main>
  );
}

function NavigationHeader({ onReset }) {
  const navigate = useNavigate();

  const handleBrandClick = () => {
    onReset();
    navigate('/');
  };

  return (
    <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
      <div 
        onClick={handleBrandClick} 
        style={{ cursor: 'pointer', display: 'flex', flexDirection: 'column' }}
        title="Click to reset and create new map"
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
          <img src="/camp-logo.png" alt="ReliefPlan AI Logo" style={{ width: '40px', height: '40px', borderRadius: '8px' }} />
          <h1 style={{ margin: 0 }}>ReliefPlan AI</h1>
        </div>
        <p className="glow-text" style={{ margin: '0.2rem 0 0 0', fontSize: '0.85rem' }}>
          Disaster Camp Layout Optimization
        </p>
      </div>

      <nav style={{ display: 'flex', gap: '1.2rem', alignItems: 'center' }}>
        <button
          onClick={handleBrandClick}
          style={{
            background: 'none',
            border: 'none',
            color: 'var(--text-main)',
            textDecoration: 'none',
            fontWeight: '600',
            fontSize: '0.95rem',
            cursor: 'pointer',
            padding: '0.45rem 0.9rem',
            borderRadius: 'var(--radius-sm)'
          }}
        >
          Dashboard / Create Map
        </button>
        <Link 
          to="/developers" 
          style={{ 
            color: 'var(--accent)', 
            textDecoration: 'none', 
            fontWeight: '600',
            fontSize: '0.95rem',
            padding: '0.45rem 0.9rem',
            borderRadius: 'var(--radius-sm)'
          }}
        >
          Developers
        </Link>
      </nav>
    </header>
  );
}

function App() {
  const [jobStatus, setJobStatus] = useState(null); // null | 'uploading' | 'processing' | 'completed' | 'error'
  const [results, setResults] = useState(null);
  const [errorMessage, setErrorMessage] = useState('');

  const handleReset = () => {
    setJobStatus(null);
    setResults(null);
    setErrorMessage('');
  };

  return (
    <Router>
      <div className="app-container">
        <NavigationHeader onReset={handleReset} />

        <Routes>
          <Route 
            path="/" 
            element={
              <Home 
                jobStatus={jobStatus} 
                setJobStatus={setJobStatus} 
                results={results} 
                setResults={setResults}
                errorMessage={errorMessage}
                setErrorMessage={setErrorMessage}
                onReset={handleReset}
              />
            } 
          />
          <Route path="/developers" element={<Developers />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
