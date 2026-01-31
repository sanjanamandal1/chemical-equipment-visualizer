import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Bar, Pie, Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

function Dashboard({ data, isDarkMode }) {
  const [isDownloading, setIsDownloading] = useState(false);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [credentials, setCredentials] = useState({ username: 'admin', password: '' });
  const [history, setHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  const [activeView, setActiveView] = useState('grid'); // 'grid' or 'list'

  useEffect(() => {
    fetchHistory();
  }, [data]);

  const fetchHistory = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/datasets/');
      setHistory(response.data.slice(0, 5));
    } catch (error) {
      console.error('Error fetching history:', error);
    }
  };

  const downloadPDF = async () => {
    if (!credentials.password) {
      alert('Please enter your password');
      return;
    }

    setIsDownloading(true);
    
    try {
      const response = await fetch(
        `http://localhost:8000/api/datasets/${data.id}/generate_report/`,
        {
          headers: {
            'Authorization': 'Basic ' + btoa(credentials.username + ':' + credentials.password)
          }
        }
      );
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `equipment_report_${new Date().toISOString().split('T')[0]}.pdf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        setShowAuthModal(false);
        setCredentials({ username: 'admin', password: '' });
        
        // Success notification
        const successMsg = document.createElement('div');
        successMsg.innerHTML = '✅ PDF downloaded successfully!';
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
        `;
        document.body.appendChild(successMsg);
        setTimeout(() => successMsg.remove(), 3000);
      } else if (response.status === 401) {
        alert('❌ Authentication failed. Please check your credentials.');
      } else {
        alert('❌ Error generating PDF. Please try again.');
      }
    } catch (error) {
      console.error('PDF Download Error:', error);
      alert('❌ Network error. Make sure Django backend is running.');
    } finally {
      setIsDownloading(false);
    }
  };

  if (!data) {
    return (
      <div style={styles.emptyState(isDarkMode)}>
        <div style={styles.emptyStateIcon}>📊</div>
        <h3 style={styles.emptyStateTitle(isDarkMode)}>No Data Available</h3>
        <p style={styles.emptyStateText(isDarkMode)}>
          Upload a CSV file to see beautiful visualizations and comprehensive analytics
        </p>
        <div style={styles.emptyStateFeatures(isDarkMode)}>
          <div style={styles.feature(isDarkMode)}>
            <span style={styles.featureIcon}>📈</span>
            <span>Interactive Charts</span>
          </div>
          <div style={styles.feature(isDarkMode)}>
            <span style={styles.featureIcon}>📊</span>
            <span>Real-time Statistics</span>
          </div>
          <div style={styles.feature(isDarkMode)}>
            <span style={styles.featureIcon}>📄</span>
            <span>PDF Reports</span>
          </div>
        </div>
      </div>
    );
  }

  const { summary, data: tableData } = data;

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          padding: 15,
          font: {
            size: 12,
            family: "'Segoe UI', sans-serif"
          },
          color: isDarkMode ? '#e2e8f0' : '#134E4A'
        }
      },
      tooltip: {
        backgroundColor: isDarkMode ? 'rgba(45, 55, 72, 0.95)' : 'rgba(0,0,0,0.8)',
        padding: 12,
        titleFont: { size: 14 },
        bodyFont: { size: 13 },
        borderColor: '#14b8a6',
        borderWidth: 1
      }
    },
    scales: {
      y: {
        ticks: { color: isDarkMode ? '#94a3b8' : '#4a5568' },
        grid: { color: isDarkMode ? '#4a5568' : '#e2e8f0' }
      },
      x: {
        ticks: { color: isDarkMode ? '#94a3b8' : '#4a5568' },
        grid: { color: isDarkMode ? '#4a5568' : '#e2e8f0' }
      }
    }
  };

  const barData = {
    labels: ['Flowrate', 'Pressure', 'Temperature'],
    datasets: [{
      label: 'Average Values',
      data: [
        summary.avg_flowrate || 0,
        summary.avg_pressure || 0,
        summary.avg_temperature || 0
      ],
      backgroundColor: ['#14b8a6', '#0891b2', '#06b6d4'],
      borderRadius: 8,
      borderWidth: 0
    }]
  };

  const pieData = {
    labels: Object.keys(summary.equipment_types || {}),
    datasets: [{
      data: Object.values(summary.equipment_types || {}),
      backgroundColor: ['#14b8a6', '#0891b2', '#06b6d4', '#2dd4bf', '#5eead4', '#99f6e4'],
      borderWidth: 2,
      borderColor: isDarkMode ? '#2d3748' : '#ffffff',
      hoverOffset: 10
    }]
  };

  return (
    <div style={styles.container(isDarkMode)}>
      {/* Header with Actions */}
      <div style={styles.header}>
        <div>
          <h2 style={styles.title(isDarkMode)}>📊 Analytics Dashboard</h2>
          <p style={styles.subtitle(isDarkMode)}>
            Dataset #{data.id} • {summary.total_count} records • 
            {Object.keys(summary.equipment_types || {}).length} equipment types
          </p>
        </div>
        
        <div style={styles.headerActions}>
          <button
            onClick={() => setActiveView(activeView === 'grid' ? 'list' : 'grid')}
            style={styles.viewToggle(isDarkMode)}
            title="Toggle View"
          >
            {activeView === 'grid' ? '📋' : '📊'}
          </button>
          <button
            onClick={() => setShowAuthModal(true)}
            style={styles.pdfButton(isDarkMode)}
            onMouseOver={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
            onMouseOut={(e) => e.currentTarget.style.transform = 'translateY(0)'}
          >
            <span>📄</span>
            Download Report
          </button>
        </div>
      </div>

      {/* Auth Modal */}
      {showAuthModal && (
        <div style={styles.modalOverlay} onClick={() => setShowAuthModal(false)}>
          <div style={styles.modal(isDarkMode)} onClick={(e) => e.stopPropagation()}>
            <div style={styles.modalHeader(isDarkMode)}>
              <h3 style={styles.modalTitle(isDarkMode)}>🔐 Authentication Required</h3>
              <button 
                onClick={() => setShowAuthModal(false)} 
                style={styles.closeButton(isDarkMode)}
              >
                ✕
              </button>
            </div>
            <div style={styles.modalBody}>
              <p style={styles.modalText(isDarkMode)}>
                Enter your credentials to generate the PDF report
              </p>
              
              <div style={styles.inputGroup}>
                <label style={styles.label(isDarkMode)}>Username</label>
                <input
                  type="text"
                  value={credentials.username}
                  onChange={(e) => setCredentials({...credentials, username: e.target.value})}
                  style={styles.input(isDarkMode)}
                  placeholder="Enter username"
                />
              </div>

              <div style={styles.inputGroup}>
                <label style={styles.label(isDarkMode)}>Password</label>
                <input
                  type="password"
                  value={credentials.password}
                  onChange={(e) => setCredentials({...credentials, password: e.target.value})}
                  onKeyPress={(e) => e.key === 'Enter' && downloadPDF()}
                  style={styles.input(isDarkMode)}
                  placeholder="Enter password"
                  autoFocus
                />
              </div>

              <div style={styles.modalFooter}>
                <button
                  onClick={() => setShowAuthModal(false)}
                  style={styles.cancelButton(isDarkMode)}
                >
                  Cancel
                </button>
                <button
                  onClick={downloadPDF}
                  disabled={isDownloading}
                  style={styles.downloadButton(isDownloading)}
                >
                  {isDownloading ? '⏳ Generating...' : '📥 Download PDF'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* History Panel */}
      {history.length > 0 && (
        <div style={styles.historyContainer(isDarkMode)}>
          <div 
            style={styles.historyHeader(isDarkMode)} 
            onClick={() => setShowHistory(!showHistory)}
          >
            <h3 style={styles.historyTitle(isDarkMode)}>
              📚 Upload History ({history.length}/5)
            </h3>
            <span style={styles.historyToggle(isDarkMode)}>
              {showHistory ? '▼' : '▶'}
            </span>
          </div>
          
          {showHistory && (
            <div style={styles.historyList}>
              {history.map((item, index) => (
                <div 
                  key={item.id} 
                  style={styles.historyItem(isDarkMode, data.id === item.id)}
                >
                  <div style={styles.historyItemHeader}>
                    <span style={styles.historyBadge}>#{index + 1}</span>
                    <span style={styles.historyName(isDarkMode)}>{item.name}</span>
                    {data.id === item.id && (
                      <span style={styles.currentBadge}>CURRENT</span>
                    )}
                  </div>
                  <div style={styles.historyItemDetails(isDarkMode)}>
                    <span>📦 {item.total_count} items</span>
                    <span>📅 {new Date(item.uploaded_at).toLocaleDateString()}</span>
                    <span>⏰ {new Date(item.uploaded_at).toLocaleTimeString()}</span>
                  </div>
                  <div style={styles.historyStats}>
                    <div style={styles.statMini(isDarkMode)}>
                      <span>💧 Flowrate:</span>
                      <strong>{item.avg_flowrate?.toFixed(2)}</strong>
                    </div>
                    <div style={styles.statMini(isDarkMode)}>
                      <span>⚡ Pressure:</span>
                      <strong>{item.avg_pressure?.toFixed(2)}</strong>
                    </div>
                    <div style={styles.statMini(isDarkMode)}>
                      <span>🌡️ Temp:</span>
                      <strong>{item.avg_temperature?.toFixed(2)}</strong>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
      
      {/* Summary Cards */}
      <div style={styles.cardsGrid}>
        <div style={styles.card(isDarkMode, '#14b8a6')}>
          <div style={styles.cardIcon}>📦</div>
          <div>
            <h4 style={styles.cardTitle}>Total Equipment</h4>
            <p style={styles.cardValue}>{summary.total_count}</p>
            <p style={styles.cardChange}>100% of dataset</p>
          </div>
        </div>
        <div style={styles.card(isDarkMode, '#0891b2')}>
          <div style={styles.cardIcon}>💧</div>
          <div>
            <h4 style={styles.cardTitle}>Avg Flowrate</h4>
            <p style={styles.cardValue}>
              {summary.avg_flowrate?.toFixed(2) || 'N/A'}
            </p>
            <p style={styles.cardChange}>units/min</p>
          </div>
        </div>
        <div style={styles.card(isDarkMode, '#06b6d4')}>
          <div style={styles.cardIcon}>⚡</div>
          <div>
            <h4 style={styles.cardTitle}>Avg Pressure</h4>
            <p style={styles.cardValue}>
              {summary.avg_pressure?.toFixed(2) || 'N/A'}
            </p>
            <p style={styles.cardChange}>PSI</p>
          </div>
        </div>
        <div style={styles.card(isDarkMode, '#2dd4bf')}>
          <div style={styles.cardIcon}>🌡️</div>
          <div>
            <h4 style={styles.cardTitle}>Avg Temperature</h4>
            <p style={styles.cardValue}>
              {summary.avg_temperature?.toFixed(2) || 'N/A'}
            </p>
            <p style={styles.cardChange}>°C</p>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div style={styles.chartsGrid}>
        <div style={styles.chartCard(isDarkMode)}>
          <h3 style={styles.chartTitle(isDarkMode)}>📊 Average Parameters</h3>
          <div style={styles.chartContainer}><Bar data={barData} options={chartOptions} /></div>
        </div>
        <div style={styles.chartCard(isDarkMode)}>
          <h3 style={styles.chartTitle(isDarkMode)}>🥧 Equipment Distribution</h3>
          <div style={styles.chartContainer}>
            <Pie data={pieData} options={{...chartOptions, scales: undefined}} />
          </div>
        </div>
      </div>

      {/* Data Table */}
      <div style={styles.tableCard(isDarkMode)}>
        <h3 style={styles.tableTitle(isDarkMode)}>📋 Equipment Data Table</h3>
        <div style={styles.tableWrapper}>
          <table style={styles.table}>
            <thead>
              <tr style={styles.tableHeaderRow(isDarkMode)}>
                <th style={styles.tableHeader(isDarkMode)}>Equipment Name</th>
                <th style={styles.tableHeader(isDarkMode)}>Type</th>
                <th style={styles.tableHeader(isDarkMode)}>Flowrate</th>
                <th style={styles.tableHeader(isDarkMode)}>Pressure</th>
                <th style={styles.tableHeader(isDarkMode)}>Temperature</th>
              </tr>
            </thead>
            <tbody>
              {tableData && tableData.map((row, index) => (
                <tr key={index} style={styles.tableRow(isDarkMode, index)}>
                  <td style={styles.tableCell(isDarkMode)}>{row['Equipment Name']}</td>
                  <td style={styles.tableCell(isDarkMode)}>
                    <span style={styles.badge(isDarkMode)}>{row.Type}</span>
                  </td>
                  <td style={styles.tableCell(isDarkMode)}>{row.Flowrate}</td>
                  <td style={styles.tableCell(isDarkMode)}>{row.Pressure}</td>
                  <td style={styles.tableCell(isDarkMode)}>{row.Temperature}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

const styles = {
  container: (isDark) => ({
    padding: '24px',
    background: isDark ? '#1a202c' : 'transparent',
    borderRadius: '15px',
    transition: 'all 0.3s ease'
  }),
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: '32px',
    flexWrap: 'wrap',
    gap: '20px'
  },
  title: (isDark) => ({
    margin: '0',
    fontSize: '28px',
    fontWeight: '700',
    color: isDark ? '#e2e8f0' : '#134E4A',
    background: isDark ? 'none' : 'linear-gradient(135deg, #14b8a6 0%, #0891b2 100%)',
    WebkitBackgroundClip: isDark ? 'none' : 'text',
    WebkitTextFillColor: isDark ? '#e2e8f0' : 'transparent'
  }),
  subtitle: (isDark) => ({
    margin: '8px 0 0 0',
    fontSize: '14px',
    color: isDark ? '#94a3b8' : '#0d9488',
    fontWeight: '400'
  }),
  headerActions: {
    display: 'flex',
    gap: '12px',
    flexWrap: 'wrap'
  },
  viewToggle: (isDark) => ({
    padding: '12px 16px',
    background: isDark ? '#2d3748' : '#f0fdfa',
    color: isDark ? '#e2e8f0' : '#134E4A',
    border: isDark ? '2px solid #4a5568' : '2px solid #99f6e4',
    borderRadius: '10px',
    cursor: 'pointer',
    fontSize: '18px',
    transition: 'all 0.2s ease',
    fontWeight: '600'
  }),
  pdfButton: (isDark) => ({
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    padding: '12px 24px',
    background: 'linear-gradient(135deg, #14b8a6 0%, #0891b2 100%)',
    color: 'white',
    border: 'none',
    borderRadius: '10px',
    cursor: 'pointer',
    fontSize: '15px',
    fontWeight: '600',
    transition: 'all 0.3s ease',
    boxShadow: '0 4px 15px rgba(20, 184, 166, 0.4)'
  }),
  // Modal styles
  modalOverlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 1000,
    backdropFilter: 'blur(8px)'
  },
  modal: (isDark) => ({
    background: isDark ? '#2d3748' : 'white',
    borderRadius: '15px',
    width: '90%',
    maxWidth: '500px',
    boxShadow: '0 25px 80px rgba(0, 0, 0, 0.5)',
    animation: 'slideUp 0.3s ease',
    border: isDark ? '2px solid #4a5568' : 'none'
  }),
  modalHeader: (isDark) => ({
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '24px 24px 16px 24px',
    borderBottom: isDark ? '1px solid #4a5568' : '1px solid #e2e8f0'
  }),
  modalTitle: (isDark) => ({
    margin: 0,
    fontSize: '20px',
    fontWeight: '600',
    color: isDark ? '#e2e8f0' : '#134E4A'
  }),
  closeButton: (isDark) => ({
    background: 'none',
    border: 'none',
    fontSize: '24px',
    cursor: 'pointer',
    color: isDark ? '#94a3b8' : '#718096',
    padding: '4px 8px',
    lineHeight: 1,
    transition: 'color 0.2s ease'
  }),
  modalBody: {
    padding: '24px'
  },
  modalText: (isDark) => ({
    margin: '0 0 24px 0',
    fontSize: '14px',
    color: isDark ? '#cbd5e0' : '#4a5568'
  }),
  inputGroup: {
    marginBottom: '20px'
  },
  label: (isDark) => ({
    display: 'block',
    marginBottom: '8px',
    fontSize: '14px',
    fontWeight: '600',
    color: isDark ? '#e2e8f0' : '#2d3748'
  }),
  input: (isDark) => ({
    width: '100%',
    padding: '12px 16px',
    fontSize: '15px',
    border: isDark ? '2px solid #4a5568' : '2px solid #e2e8f0',
    borderRadius: '10px',
    boxSizing: 'border-box',
    transition: 'border-color 0.2s',
    background: isDark ? '#1a202c' : 'white',
    color: isDark ? '#e2e8f0' : '#2d3748'
  }),
  modalFooter: {
    display: 'flex',
    gap: '12px',
    marginTop: '24px'
  },
  cancelButton: (isDark) => ({
    flex: 1,
    padding: '12px',
    background: isDark ? '#1a202c' : '#f7fafc',
    color: isDark ? '#e2e8f0' : '#4a5568',
    border: isDark ? '2px solid #4a5568' : '2px solid #e2e8f0',
    borderRadius: '10px',
    cursor: 'pointer',
    fontSize: '15px',
    fontWeight: '600',
    transition: 'all 0.2s'
  }),
  downloadButton: (loading) => ({
    flex: 1,
    padding: '12px',
    background: loading ? '#94a3b8' : 'linear-gradient(135deg, #14b8a6 0%, #0891b2 100%)',
    color: 'white',
    border: 'none',
    borderRadius: '10px',
    cursor: loading ? 'not-allowed' : 'pointer',
    fontSize: '15px',
    fontWeight: '600',
    transition: 'all 0.2s',
    boxShadow: loading ? 'none' : '0 4px 15px rgba(20, 184, 166, 0.4)',
    opacity: loading ? 0.6 : 1
  }),
  // Empty state
  emptyState: (isDark) => ({
    textAlign: 'center',
    padding: '80px 20px',
    background: isDark ? '#2d3748' : 'white',
    borderRadius: '15px',
    border: isDark ? '2px solid #4a5568' : '2px solid #e2e8f0'
  }),
  emptyStateIcon: {
    fontSize: '80px',
    marginBottom: '20px',
    filter: 'grayscale(50%)'
  },
  emptyStateTitle: (isDark) => ({
    fontSize: '28px',
    fontWeight: '700',
    color: isDark ? '#e2e8f0' : '#134E4A',
    margin: '0 0 12px 0'
  }),
  emptyStateText: (isDark) => ({
    fontSize: '16px',
    color: isDark ? '#94a3b8' : '#0d9488',
    margin: '0 0 30px 0',
    maxWidth: '600px',
    marginLeft: 'auto',
    marginRight: 'auto'
  }),
  emptyStateFeatures: (isDark) => ({
    display: 'flex',
    justifyContent: 'center',
    gap: '30px',
    flexWrap: 'wrap',
    marginTop: '30px'
  }),
  feature: (isDark) => ({
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    padding: '15px 25px',
    background: isDark ? '#1a202c' : '#f0fdfa',
    borderRadius: '12px',
    border: isDark ? '2px solid #4a5568' : '2px solid #99f6e4',
    color: isDark ? '#e2e8f0' : '#134E4A',
    fontWeight: '600'
  }),
  featureIcon: {
    fontSize: '24px'
  },
  // History styles
  historyContainer: (isDark) => ({
    background: isDark ? '#2d3748' : 'white',
    borderRadius: '15px',
    boxShadow: isDark ? 'none' : '0 4px 20px rgba(0, 0, 0, 0.08)',
    marginBottom: '32px',
    overflow: 'hidden',
    border: isDark ? '2px solid #4a5568' : '2px solid #e2e8f0'
  }),
  historyHeader: (isDark) => ({
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '20px 24px',
    cursor: 'pointer',
    background: isDark ? '#1a202c' : '#f0fdfa',
    borderBottom: isDark ? '1px solid #4a5568' : '1px solid #e2e8f0',
    transition: 'background 0.2s'
  }),
  historyTitle: (isDark) => ({
    margin: 0,
    fontSize: '18px',
    fontWeight: '600',
    color: isDark ? '#e2e8f0' : '#134E4A'
  }),
  historyToggle: (isDark) => ({
    fontSize: '14px',
    color: isDark ? '#94a3b8' : '#0d9488',
    fontWeight: 'bold'
  }),
  historyList: {
    padding: '16px',
    maxHeight: '450px',
    overflowY: 'auto'
  },
  historyItem: (isDark, isCurrent) => ({
    padding: '16px',
    marginBottom: '12px',
    borderRadius: '12px',
    border: isDark ? '2px solid #4a5568' : '2px solid #e2e8f0',
    background: isCurrent ? (isDark ? '#2c5282' : '#ccfbf1') : (isDark ? '#1a202c' : 'white'),
    transition: 'all 0.2s'
  }),
  historyItemHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    marginBottom: '12px',
    flexWrap: 'wrap'
  },
  historyBadge: {
    background: 'linear-gradient(135deg, #14b8a6 0%, #0891b2 100%)',
    color: 'white',
    padding: '4px 12px',
    borderRadius: '12px',
    fontSize: '12px',
    fontWeight: 'bold'
  },
  historyName: (isDark) => ({
    fontSize: '15px',
    fontWeight: '600',
    color: isDark ? '#e2e8f0' : '#134E4A',
    flex: 1
  }),
  currentBadge: {
    background: '#06b6d4',
    color: 'white',
    padding: '4px 12px',
    borderRadius: '12px',
    fontSize: '11px',
    fontWeight: 'bold'
  },
  historyItemDetails: (isDark) => ({
    display: 'flex',
    gap: '16px',
    marginBottom: '12px',
    flexWrap: 'wrap',
    fontSize: '13px',
    color: isDark ? '#94a3b8' : '#0d9488'
  }),
  historyStats: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
    gap: '12px',
    marginTop: '12px',
    paddingTop: '12px',
    borderTop: '1px solid rgba(20, 184, 166, 0.2)'
  },
  statMini: (isDark) => ({
    display: 'flex',
    flexDirection: 'column',
    gap: '4px',
    fontSize: '13px',
    color: isDark ? '#cbd5e0' : '#4a5568'
  }),
  // Cards
  cardsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
    gap: '20px',
    marginBottom: '32px'
  },
  card: (isDark, color) => ({
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
    padding: '24px',
    borderRadius: '15px',
    background: isDark 
      ? `linear-gradient(135deg, ${color}15 0%, ${color}25 100%)` 
      : 'white',
    border: isDark ? `2px solid ${color}50` : `2px solid ${color}30`,
    boxShadow: isDark ? 'none' : `0 4px 20px ${color}20`,
    transition: 'transform 0.2s, box-shadow 0.2s',
    cursor: 'pointer'
  }),
  cardIcon: {
    fontSize: '42px'
  },
  cardTitle: {
    margin: '0 0 8px 0',
    fontSize: '14px',
    fontWeight: '500',
    color: '#94a3b8',
    textTransform: 'uppercase',
    letterSpacing: '0.5px'
  },
  cardValue: {
    margin: '8px 0',
    fontSize: '32px',
    fontWeight: '700',
    background: 'linear-gradient(135deg, #14b8a6 0%, #0891b2 100%)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent'
  },
  cardChange: {
    margin: 0,
    fontSize: '12px',
    color: '#0d9488',
    fontWeight: '500'
  },
  // Charts
  chartsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(500px, 1fr))',
    gap: '24px',
    marginBottom: '32px'
  },
  chartCard: (isDark) => ({
    background: isDark ? '#2d3748' : 'white',
    padding: '24px',
    borderRadius: '15px',
    boxShadow: isDark ? 'none' : '0 4px 20px rgba(0, 0, 0, 0.08)',
    border: isDark ? '2px solid #4a5568' : '2px solid #e2e8f0'
  }),
  chartTitle: (isDark) => ({
    margin: '0 0 20px 0',
    fontSize: '18px',
    fontWeight: '600',
    color: isDark ? '#e2e8f0' : '#134E4A'
  }),
  chartContainer: {
    position: 'relative',
    height: '320px'
  },
  // Table
  tableCard: (isDark) => ({
    background: isDark ? '#2d3748' : 'white',
    padding: '24px',
    borderRadius: '15px',
    boxShadow: isDark ? 'none' : '0 4px 20px rgba(0, 0, 0, 0.08)',
    border: isDark ? '2px solid #4a5568' : '2px solid #e2e8f0'
  }),
  tableTitle: (isDark) => ({
    margin: '0 0 20px 0',
    fontSize: '18px',
    fontWeight: '600',
    color: isDark ? '#e2e8f0' : '#134E4A'
  }),
  tableWrapper: {
    overflowX: 'auto',
    borderRadius: '10px'
  },
  table: {
    width: '100%',
    borderCollapse: 'separate',
    borderSpacing: 0,
    fontSize: '14px'
  },
  tableHeaderRow: (isDark) => ({
    background: isDark ? '#1a202c' : '#f0fdfa'
  }),
  tableHeader: (isDark) => ({
    padding: '16px',
    textAlign: 'left',
    fontWeight: '600',
    color: isDark ? '#e2e8f0' : '#134E4A',
    borderBottom: isDark ? '2px solid #4a5568' : '2px solid #14b8a6',
    whiteSpace: 'nowrap',
    position: 'sticky',
    top: 0,
    background: isDark ? '#1a202c' : '#f0fdfa',
    zIndex: 10
  }),
  tableRow: (isDark, index) => ({
    background: index % 2 === 0 ? (isDark ? '#2d3748' : '#ffffff') : (isDark ? '#1a202c' : '#f8f9fa'),
    transition: 'background-color 0.2s'
  }),
  tableCell: (isDark) => ({
    padding: '16px',
    borderBottom: isDark ? '1px solid #4a5568' : '1px solid #e2e8f0',
    color: isDark ? '#e2e8f0' : '#4a5568'
  }),
  badge: (isDark) => ({
    display: 'inline-block',
    padding: '6px 14px',
    background: isDark 
      ? 'linear-gradient(135deg, #14b8a615 0%, #0891b225 100%)' 
      : 'linear-gradient(135deg, #ccfbf1 0%, #f0fdfa 100%)',
    color: isDark ? '#5eead4' : '#0d9488',
    borderRadius: '12px',
    fontSize: '13px',
    fontWeight: '600',
    border: isDark ? '1px solid #14b8a650' : '1px solid #99f6e4'
  })
};

export default Dashboard;
