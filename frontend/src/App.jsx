import React, { useState } from 'react';
import Dashboard from './components/Dashboard';
import UploadSection from './components/UploadSection';

function App() {
  const [jobStatus, setJobStatus] = useState(null); // null | 'uploading' | 'processing' | 'completed'
  const [results, setResults] = useState(null);

  const handleUpload = async (file) => {
    setJobStatus('uploading');
    
    // Simulate API call to FastAPI backend
    setTimeout(() => {
      setJobStatus('processing');
      
      // Simulate processing time
      setTimeout(() => {
        setJobStatus('completed');
        setResults({
          land_utilization_percent: 85,
          total_shelters: 450,
          avg_walking_distance_m: 42,
          facilities: {
            medical_centers: 2,
            water_points: 15,
            latrines: 30
          }
        });
      }, 3000);
    }, 1500);
  };

  return (
    <div className="app-container">
      <header className="glass-panel">
        <h1>ReliefPlan AI</h1>
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
