import React, { useState } from 'react';
import Dashboard from './components/Dashboard';
import UploadSection from './components/UploadSection';

function App() {
  const [jobStatus, setJobStatus] = useState(null); // null | 'uploading' | 'processing' | 'completed'
  const [results, setResults] = useState(null);

  const handleUpload = async (file) => {
    setJobStatus('uploading');
    
    // Create FormData
    const formData = new FormData();
    formData.append('file', file);

    try {
      setJobStatus('processing');
      // Call the FastAPI backend
      const response = await fetch('http://localhost:8000/api/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const data = await response.json();
      
      setJobStatus('completed');
      setResults({
        metrics: data.results,
        blueprint_url: data.blueprint_url
      });
    } catch (error) {
      console.error('Error uploading file:', error);
      setJobStatus('error');
    }
  };

  return (
    <div className="app-container">
      <header>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <img src="/camp-logo.png" alt="ReliefPlan AI Logo" style={{ width: '40px', height: '40px', borderRadius: '8px' }} />
          <h1>ReliefPlan AI</h1>
        </div>
        <p className="glow-text">Disaster Camp Layout Optimization</p>
      </header>

      <main>
        {jobStatus === null ? (
          <UploadSection onUpload={handleUpload} />
        ) : (
          <Dashboard status={jobStatus} results={results} />
        )}
      </main>
    </div>
  );
}

export default App;
