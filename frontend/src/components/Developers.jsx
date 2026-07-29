import React, { useState, useEffect } from 'react';

function Developers() {
  const [images, setImages] = useState([]);
  const [graphs, setGraphs] = useState({ unet: '', deeplabv3: '' });
  const [trainingStatus, setTrainingStatus] = useState('');

  useEffect(() => {
    // Fetch dataset images
    fetch('http://localhost:8000/api/dataset/images')
      .then(res => res.json())
      .then(data => setImages(data.images || []))
      .catch(err => console.error(err));

    // Fetch comparison graphs
    fetch('http://localhost:8000/api/models/compare')
      .then(res => res.json())
      .then(data => setGraphs(data))
      .catch(err => console.error(err));
  }, []);

  const startTraining = (model) => {
    setTrainingStatus(`Triggering automated Ablation Study for ${model.toUpperCase()}...`);
    fetch(`http://localhost:8000/api/train?model=${model}`, { method: 'POST' })
      .then(res => res.json())
      .then(data => {
        setTrainingStatus(`Training started in background for ${model.toUpperCase()} on RTX 4060 GPU.`);
      })
      .catch(err => {
        setTrainingStatus(`Error triggering training: ${err.message}`);
      });
  };

  return (
    <div className="developers-page" style={{ padding: '2rem' }}>
      <h2 className="glow-text">Developer Control Center</h2>
      
      {/* Training Controls */}
      <section className="glass-panel" style={{ padding: '2rem', marginBottom: '2rem' }}>
        <h3>1. Deep Learning Model Training</h3>
        <p>Trigger GPU-accelerated training directly from the UI.</p>
        <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
          <button className="primary-btn" onClick={() => startTraining('unet')}>Train U-Net (Ablation)</button>
          <button className="primary-btn" onClick={() => startTraining('deeplabv3')}>Train DeepLabV3+ (Ablation)</button>
        </div>
        {trainingStatus && (
          <div style={{ marginTop: '1rem', padding: '1rem', backgroundColor: 'rgba(0,255,0,0.1)', borderRadius: '8px' }}>
            <p className="glow-text">{trainingStatus}</p>
          </div>
        )}
      </section>

      {/* Model Comparison */}
      <section className="glass-panel" style={{ padding: '2rem', marginBottom: '2rem' }}>
        <h3>2. Architecture Comparison (Learning Curves)</h3>
        <p>Evaluate Validation IoU and Cross-Entropy Loss to prevent overfitting.</p>
        <div style={{ display: 'flex', gap: '2rem', overflowX: 'auto', marginTop: '1rem' }}>
          <div style={{ flex: 1, minWidth: '400px' }}>
            <h4>U-Net Results</h4>
            {graphs.unet ? <img src={graphs.unet} alt="U-Net Curves" style={{ width: '100%', borderRadius: '8px' }} /> : <p>No data</p>}
          </div>
          <div style={{ flex: 1, minWidth: '400px' }}>
            <h4>DeepLabV3+ Results</h4>
            {graphs.deeplabv3 ? <img src={graphs.deeplabv3} alt="DeepLabV3+ Curves" style={{ width: '100%', borderRadius: '8px' }} /> : <p>No data</p>}
          </div>
        </div>
      </section>

      {/* Dataset Visualization */}
      <section className="glass-panel" style={{ padding: '2rem' }}>
        <h3>3. Dataset Visualization (Train_256)</h3>
        <p>Previewing raw satellite images alongside their ground-truth segmentation masks.</p>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '1rem', marginTop: '1rem' }}>
          {images.map(filename => (
            <div key={filename} style={{ textAlign: 'center' }}>
              <p style={{ fontSize: '0.8rem', color: '#ccc' }}>{filename}</p>
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <img 
                  src={`http://localhost:8000/data/Train_256/images/${filename}`} 
                  alt="Raw" 
                  style={{ width: '50%', borderRadius: '4px', border: '1px solid #444' }} 
                  title="Satellite Image"
                />
                <img 
                  src={`http://localhost:8000/data/Train_256/masks/${filename}`} 
                  alt="Mask" 
                  style={{ width: '50%', borderRadius: '4px', border: '1px solid #444' }} 
                  title="Ground Truth Mask"
                />
              </div>
            </div>
          ))}
          {images.length === 0 && <p>No offline dataset images found.</p>}
        </div>
      </section>
    </div>
  );
}

export default Developers;
