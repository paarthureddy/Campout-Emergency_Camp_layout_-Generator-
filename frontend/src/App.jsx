import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import UploadSection from './components/UploadSection';
import Developers from './components/Developers';

function Home() {
  const [jobStatus, setJobStatus] = useState(null); // null | 'uploading' | 'processing' | 'completed'
  const [results, setResults] = useState(null);

  const handleUpload = async (file, modelName) => {
    setJobStatus('uploading');
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('model', modelName);

    try {
      setJobStatus('processing');
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
    <main>
      {jobStatus === null ? (
        <UploadSection onUpload={handleUpload} />
      ) : (
        <Dashboard status={jobStatus} results={results} />
      )}
    </main>
  );
}

function App() {
  return (
    <Router>
      <div className="app-container">
        <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <img src="/camp-logo.png" alt="ReliefPlan AI Logo" style={{ width: '40px', height: '40px', borderRadius: '8px' }} />
              <h1>ReliefPlan AI</h1>
            </div>
            <p className="glow-text" style={{ margin: 0 }}>Disaster Camp Layout Optimization</p>
          </div>
          <nav style={{ display: 'flex', gap: '1.5rem' }}>
            <Link to="/" style={{ color: 'white', textDecoration: 'none', fontWeight: 'bold' }}>Dashboard</Link>
            <Link to="/developers" style={{ color: '#00d2ff', textDecoration: 'none', fontWeight: 'bold' }}>Developers</Link>
          </nav>
        </header>

        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/developers" element={<Developers />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
