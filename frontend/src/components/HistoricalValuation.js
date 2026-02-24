import React, { useState, useEffect } from 'react';
import { getSectionData } from '../utils/dataParser';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

const HistoricalValuation = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedInsights, setExpandedInsights] = useState({});

  const toggleInsight = (id) => {
    setExpandedInsights(prev => ({ ...prev, [id]: !prev[id] }));
  };

  useEffect(() => {
    fetchHistoricalData();
  }, []);

  const fetchHistoricalData = async () => {
    try {
      setLoading(true);
      setError(null);
      const sectionData = await getSectionData(5);
      setData(sectionData);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching historical valuation data:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '60px 20px' }}>
        <div className="spinner" style={{
          width: '50px', height: '50px', border: '5px solid #f3f3f3',
          borderTop: '5px solid #0ea5e9', borderRadius: '50%',
          animation: 'spin 1s linear infinite', margin: '0 auto 20px'
        }}></div>
        <p style={{ color: '#666' }}>Loading historical valuation data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ background: '#fee', border: '1px solid #fcc', borderRadius: '8px', padding: '20px', margin: '20px 0' }}>
        <p style={{ color: '#c00', margin: '0 0 10px 0' }}>⚠️ {error}</p>
        <button onClick={fetchHistoricalData} style={{ padding: '10px 20px', background: '#0ea5e9', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer' }}>
          Retry
        </button>
      </div>
    );
  }

  if (!data || !data.slides || data.slides.length === 0) {
    return <div style={{ textAlign: 'center', padding: '60px', color: '#666' }}>No historical valuation data available</div>;
  }

  const overview = data.slides[0]?.overview || {};
  const narrative = data.slides[0]?.narrative || {};
  const visualizations = data.slides[0]?.visualizations || [];

  console.log('Historical Valuation - Section 5 data:', data);
  console.log('Visualizations:', visualizations);
  console.log('Narrative:', narrative);

  return (
    <div>
      <div className="section-header">
        <h2>📈 Historical Valuation Trends</h2>
        <p>{overview.what_this_section_does || 'Analysis of historical valuation trends and their implications'}</p>
      </div>

      {/* Visualizations with Agent Insights */}
      {visualizations.length > 0 && (
        <div style={{ marginBottom: '32px' }}>
          <h3 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '20px', color: '#0ea5e9' }}>
            📊 Valuation Trends Analysis
          </h3>
          {visualizations.map((viz, idx) => {
            const color = '#0ea5e9'; // Use consistent theme color
            
            return (
              <div key={idx} className="card" style={{ marginBottom: '20px', borderTop: `3px solid ${color}` }}>
                <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <h4 className="card-title" style={{ margin: 0, color: '#0ea5e9' }}>{viz.title}</h4>
                  {viz.interpretation && (
                    <button
                      onClick={() => toggleInsight(`viz_${idx}`)}
                      style={{
                        background: '#0ea5e9',
                        color: 'white',
                        border: 'none',
                        borderRadius: '50%',
                        width: '32px',
                        height: '32px',
                        cursor: 'pointer',
                        fontSize: '18px',
                        fontWeight: 'bold',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        transition: 'all 0.2s'
                      }}
                      title="Agent Insights"
                    >
                      {expandedInsights[`viz_${idx}`] ? '−' : '+'}
                    </button>
                  )}
                </div>
                <div className="card-body">
                  <ResponsiveContainer width="100%" height={350}>
                    <LineChart data={viz.data.labels.map((label, i) => {
                      const point = { label };
                      viz.data.datasets.forEach(dataset => {
                        point[dataset.label] = dataset.data[i];
                      });
                      return point;
                    })}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="label" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      {viz.data.datasets.map((dataset, dsIdx) => (
                        <Line
                          key={dsIdx}
                          type="monotone"
                          dataKey={dataset.label}
                          stroke={dataset.borderColor}
                          strokeWidth={2}
                        />
                      ))}
                    </LineChart>
                  </ResponsiveContainer>
                  
                  {expandedInsights[`viz_${idx}`] && viz.interpretation && (
                    <div style={{
                      marginTop: '16px',
                      padding: '16px',
                      background: '#0ea5e908',
                      border: '2px solid #0ea5e930',
                      borderRadius: '8px',
                      borderLeft: '4px solid #0ea5e9'
                    }}>
                      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '10px' }}>
                        <span style={{ fontSize: '24px', flexShrink: 0 }}>🤖</span>
                        <div>
                          <strong style={{ color: '#0ea5e9', display: 'block', marginBottom: '8px', fontSize: '15px' }}>
                            Agent Insights:
                          </strong>
                          <p style={{ margin: 0, fontSize: '14px', lineHeight: '1.7', color: '#444' }}>
                            {viz.interpretation}
                          </p>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Narrative Analysis */}
      {(narrative.vodafone_trends || narrative.apollo_trends) && (
        <div style={{ marginBottom: '32px' }}>
          <h3 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '20px', color: '#0ea5e9' }}>
            💡 Detailed Company Analysis
          </h3>
          
          <div className="grid-2" style={{ gap: '20px' }}>
            {narrative.vodafone_trends && (
              <div className="card" style={{ borderTop: '4px solid #0ea5e9' }}>
                <div className="card-header" style={{ background: '#0ea5e908' }}>
                  <h4 className="card-title" style={{ color: '#0ea5e9', margin: 0 }}>📉 Vodafone Idea Analysis</h4>
                </div>
                <div className="card-body">
                  <p style={{ fontSize: '14px', lineHeight: '1.7', color: '#555', marginBottom: '16px' }}>
                    {narrative.vodafone_trends.explanation}
                  </p>
                  
                  <div style={{ padding: '12px', background: '#f0f9ff', borderRadius: '6px', borderLeft: '3px solid #0ea5e9' }}>
                    <p style={{ fontSize: '13px', color: '#0369a1', fontWeight: '500', marginBottom: '6px' }}>
                      💡 Investment Implication
                    </p>
                    <p style={{ fontSize: '13px', color: '#075985', lineHeight: '1.6', margin: 0 }}>
                      Volatility suggests caution - investors should monitor debt restructuring and 5G rollout progress closely before committing capital.
                    </p>
                  </div>
                </div>
              </div>
            )}

            {narrative.apollo_trends && (
              <div className="card" style={{ borderTop: '4px solid #0ea5e9' }}>
                <div className="card-header" style={{ background: '#0ea5e908' }}>
                  <h4 className="card-title" style={{ color: '#0ea5e9', margin: 0 }}>📈 Apollo Micro Systems Analysis</h4>
                </div>
                <div className="card-body">
                  <p style={{ fontSize: '14px', lineHeight: '1.7', color: '#555', marginBottom: '16px' }}>
                    {narrative.apollo_trends.explanation}
                  </p>
                  
                  <div style={{ padding: '12px', background: '#f0f9ff', borderRadius: '6px', borderLeft: '3px solid #0ea5e9' }}>
                    <p style={{ fontSize: '13px', color: '#0369a1', fontWeight: '500', marginBottom: '6px' }}>
                      💡 Investment Implication
                    </p>
                    <p style={{ fontSize: '13px', color: '#064e3b', lineHeight: '1.6', margin: 0 }}>
                      Premium valuation justified by consistent execution - suitable for growth investors with long-term horizon.
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Legacy content for backward compatibility */}
      {overview.valuation_analysis && !visualizations.length && (
        <div className="card" style={{ marginBottom: '24px' }}>
          <div className="card-header">
            <h3 className="card-title">Historical Valuation Analysis</h3>
          </div>
          <div className="card-body">
            <div style={{ padding: '16px', background: '#f9fafb', borderLeft: '4px solid #0ea5e9', borderRadius: '4px', marginBottom: '20px' }}>
              <p style={{ fontWeight: '600', marginBottom: '8px', color: '#111' }}>
                {overview.valuation_analysis.statement}
              </p>
              <p style={{ fontSize: '14px', color: '#666', lineHeight: '1.6' }}>
                {overview.valuation_analysis.explanation}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Key Takeaways */}
      <div className="card" style={{ marginTop: '24px', borderTop: '4px solid #0ea5e9' }}>
        <div className="card-header">
          <h3 className="card-title">🎯 Key Takeaways</h3>
        </div>
        <div className="card-body">
          <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
            <li style={{ marginBottom: '12px', paddingLeft: '24px', position: 'relative', lineHeight: '1.6' }}>
              <span style={{ position: 'absolute', left: 0, fontSize: '16px' }}>📊</span>
              <strong>Vodafone Idea:</strong> P/E ratio fluctuations (14x to 32x) reflect investor uncertainty about operational strategies and competitive positioning
            </li>
            <li style={{ marginBottom: '12px', paddingLeft: '24px', position: 'relative', lineHeight: '1.6' }}>
              <span style={{ position: 'absolute', left: 0, fontSize: '16px' }}>📈</span>
              <strong>Apollo Micro:</strong> P/E averaging around 25x demonstrates stable investor confidence in defense sector growth
            </li>
            <li style={{ paddingLeft: '24px', position: 'relative', lineHeight: '1.6' }}>
              <span style={{ position: 'absolute', left: 0, fontSize: '16px' }}>💰</span>
              <strong>Strategy:</strong> Investors must consider historical trajectories to inform future investment strategies given distinct market landscapes
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default HistoricalValuation;
