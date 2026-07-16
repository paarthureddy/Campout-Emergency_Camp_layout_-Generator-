import React from 'react';
import MetricsCard from './MetricsCard';

function Dashboard({ status, results }) {
  const isProcessing = status === 'uploading' || status === 'processing';

  return (
    <div className="dashboard">
      <div className="blueprint-viewer glass-panel">
        {isProcessing ? (
          <div style={{ textAlign: 'center' }}>
            <div className="spinner" style={{ margin: '0 auto 1rem auto' }}></div>
            <h3 className="glow-text">
              {status === 'uploading' ? 'Uploading...' : 'AI optimizing camp layout...'}
            </h3>
          </div>
        ) : (
          <>
            <img 
              src="https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2072&auto=format&fit=crop" 
              alt="Satellite Blueprint" 
              className="blueprint-img"
            />
            <div className="overlay-status glass-panel glow-text">
              Blueprint Generation Complete
            </div>
          </>
        )}
      </div>

      <div className="metrics-grid">
        {!results ? (
          <div className="glass-panel" style={{ padding: '2rem', textAlign: 'center' }}>
            <p className="glow-text">Waiting for processing to finish...</p>
          </div>
        ) : (
          <>
            <MetricsCard 
              title="Land Utilization" 
              value={`${results.land_utilization_percent}%`} 
              accent="var(--primary)" 
            />
            <MetricsCard 
              title="Total Shelters" 
              value={results.total_shelters} 
              accent="var(--accent)" 
            />
            <MetricsCard 
              title="Avg Walking Distance" 
              value={`${results.avg_walking_distance_m}m`} 
              accent="var(--danger)" 
            />
            <MetricsCard 
              title="Essential Facilities" 
              value={`${results.facilities.medical_centers} Med, ${results.facilities.water_points} Water`} 
              accent="var(--text-main)" 
            />
          </>
        )}
      </div>
    </div>
  );
}

export default Dashboard;
