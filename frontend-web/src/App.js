import React, { useState } from 'react';
import UploadCSV from './components/UploadCSV';
import Dashboard from './components/Dashboard';
import './App.css';

function App() {
  const [uploadedData, setUploadedData] = useState(null);
  const [isDarkMode, setIsDarkMode] = useState(false);

  return (
    <div className="App" style={{ 
      minHeight: '100vh', 
      background: isDarkMode 
        ? 'linear-gradient(135deg, #1a202c 0%, #2d3748 100%)'
        : 'linear-gradient(135deg, #f0fdfa 0%, #e0f2fe 100%)',
      padding: '20px',
      transition: 'all 0.3s ease'
    }}>
      {/* Navigation Bar */}
      <div style={{
        maxWidth: '1600px',
        margin: '0 auto 20px auto',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '15px 30px',
        background: isDarkMode ? '#2d3748' : 'white',
        borderRadius: '15px',
        boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
        flexWrap: 'wrap',
        gap: '15px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
          <div style={{
            width: '50px',
            height: '50px',
            background: 'linear-gradient(135deg, #14b8a6 0%, #0891b2 100%)',
            borderRadius: '12px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '24px'
          }}>
            🧪
          </div>
          <div>
            <h3 style={{ 
              margin: 0, 
              color: isDarkMode ? '#e2e8f0' : '#134E4A',
              fontSize: '20px',
              fontWeight: '700'
            }}>
              Chemical Equipment Visualizer
            </h3>
            <p style={{ 
              margin: 0, 
              color: isDarkMode ? '#94a3b8' : '#0d9488',
              fontSize: '13px'
            }}>
              Advanced Analytics Platform
            </p>
          </div>
        </div>
        
        <button
          onClick={() => setIsDarkMode(!isDarkMode)}
          style={{
            padding: '10px 20px',
            background: isDarkMode ? '#4a5568' : '#f0fdfa',
            color: isDarkMode ? '#e2e8f0' : '#134E4A',
            border: isDarkMode ? '2px solid #718096' : '2px solid #99f6e4',
            borderRadius: '10px',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: '600',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            transition: 'all 0.2s ease'
          }}
          onMouseOver={(e) => {
            e.currentTarget.style.transform = 'scale(1.05)';
            e.currentTarget.style.background = isDarkMode ? '#5a6678' : '#ccfbf1';
          }}
          onMouseOut={(e) => {
            e.currentTarget.style.transform = 'scale(1)';
            e.currentTarget.style.background = isDarkMode ? '#4a5568' : '#f0fdfa';
          }}
        >
          {isDarkMode ? '☀️ Light Mode' : '🌙 Dark Mode'}
        </button>
      </div>

      <div style={{ 
        maxWidth: '1600px', 
        margin: '0 auto',
        background: isDarkMode ? '#2d3748' : 'white',
        borderRadius: '20px',
        padding: '40px',
        boxShadow: isDarkMode 
          ? '0 20px 60px rgba(0,0,0,0.4)' 
          : '0 20px 60px rgba(0,0,0,0.1)',
        transition: 'all 0.3s ease'
      }}>
        <UploadCSV onUploadSuccess={setUploadedData} isDarkMode={isDarkMode} />
        <Dashboard data={uploadedData} isDarkMode={isDarkMode} />
      </div>

      {/* Footer */}
      <div style={{
        maxWidth: '1600px',
        margin: '20px auto 0 auto',
        textAlign: 'center',
        color: isDarkMode ? '#94a3b8' : '#0d9488',
        fontSize: '14px',
        padding: '20px'
      }}>
        <p style={{ margin: '5px 0' }}>
          Made with ❤️ for Chemical Equipment Analysis
        </p>
        <p style={{ margin: '5px 0', fontSize: '12px', opacity: 0.8 }}>
          © 2026 Chemical Equipment Visualizer. All rights reserved.
        </p>
      </div>
    </div>
  );
}

export default App;