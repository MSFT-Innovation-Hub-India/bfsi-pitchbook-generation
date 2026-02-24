import React, { useState, useEffect } from 'react';
import { getSectionData } from '../utils/dataParser';

const ValuationTables = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedCompany, setSelectedCompany] = useState(0);
  const [selectedTable, setSelectedTable] = useState(0);
  const [expandedInsights, setExpandedInsights] = useState({});

  const toggleInsight = (slideId) => {
    setExpandedInsights(prev => ({ ...prev, [slideId]: !prev[slideId] }));
  };

  useEffect(() => {
    fetchValuationData();
  }, []);

  const fetchValuationData = async () => {
    try {
      setLoading(true);
      setError(null);
      const sectionData = await getSectionData(4);
      setData(sectionData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '60px 20px' }}>
        <div className="spinner" style={{ width: '50px', height: '50px', border: '5px solid #f3f3f3', borderTop: '5px solid #0ea5e9', borderRadius: '50%', animation: 'spin 1s linear infinite', margin: '0 auto 20px' }}></div>
        <p style={{ color: '#666' }}>Loading valuation data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ background: '#fee', border: '1px solid #fcc', borderRadius: '8px', padding: '20px', margin: '20px 0' }}>
        <p style={{ color: '#c00', margin: '0 0 10px 0' }}>⚠️ {error}</p>
        <button onClick={fetchValuationData} style={{ padding: '10px 20px', background: '#0ea5e9', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer' }}>Retry</button>
      </div>
    );
  }

  if (!data || !data.slides || data.slides.length === 0) {
    return <div style={{ textAlign: 'center', padding: '60px', color: '#666' }}>No valuation data available</div>;
  }

  const currentSlide = data.slides[selectedTable];
  const company = currentSlide?.company;

  // Group slides by company
  const companies = ['Vodafone Idea', 'Apollo Micro Systems'];
  const companyColors = {
    'Vodafone Idea': '#0ea5e9',
    'Apollo Micro Systems': '#0ea5e9'
  };

  // Filter slides by selected company
  const vodafoneSlides = data.slides.filter(s => s.company === 'Vodafone Idea');
  const apolloSlides = data.slides.filter(s => s.company === 'Apollo Micro Systems');
  const currentCompanySlides = selectedCompany === 0 ? vodafoneSlides : apolloSlides;
  const currentCompanyName = companies[selectedCompany];

  return (
    <div>
      <div className="section-header">
        <h2>💰 Valuation Tables</h2>
        <p>Comprehensive peer comparison across multiple valuation dimensions</p>
      </div>

      {/* Company Navigation - Compact Top Bar */}
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        gap: '12px', 
        marginBottom: '24px',
        padding: '12px 20px',
        background: '#f8fafc',
        borderRadius: '10px',
        border: '1px solid #e2e8f0'
      }}>
        <span style={{ fontSize: '14px', fontWeight: '600', color: '#64748b', marginRight: '8px' }}>
          Company:
        </span>
        {companies.map((companyName, idx) => (
          <button
            key={idx}
            onClick={() => {
              setSelectedCompany(idx);
              setSelectedTable(idx === 0 ? 0 : 4);
            }}
            style={{
              padding: '10px 24px',
              background: selectedCompany === idx ? companyColors[companyName] : 'white',
              color: selectedCompany === idx ? 'white' : '#334155',
              border: `2px solid ${companyColors[companyName]}`,
              borderRadius: '8px',
              cursor: 'pointer',
              fontWeight: '600',
              fontSize: '14px',
              transition: 'all 0.2s ease',
              boxShadow: selectedCompany === idx ? '0 2px 8px rgba(0,0,0,0.12)' : '0 1px 3px rgba(0,0,0,0.05)',
              flex: '0 0 auto'
            }}
          >
            {companyName}
          </button>
        ))}
      </div>

      {/* Sub-Navigation - Prominent Table Selector */}
      <div style={{ marginBottom: '32px' }}>
        <div style={{ 
          marginBottom: '16px',
          paddingBottom: '12px',
          borderBottom: `3px solid ${companyColors[currentCompanyName]}`
        }}>
          <h3 style={{ 
            fontSize: '16px', 
            fontWeight: '600', 
            color: companyColors[currentCompanyName],
            margin: 0
          }}>
            {currentCompanyName} - Valuation Analysis
          </h3>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px' }}>
          {currentCompanySlides.map((slide, idx) => {
            const slideIdx = data.slides.findIndex(s => s.slide_id === slide.slide_id);
            return (
              <button
                key={idx}
                onClick={() => setSelectedTable(slideIdx)}
                style={{
                  padding: '12px 24px',
                  background: selectedTable === slideIdx ? companyColors[currentCompanyName] : 'white',
                  color: selectedTable === slideIdx ? 'white' : '#334155',
                  border: `2px solid ${companyColors[currentCompanyName]}`,
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontWeight: '600',
                  fontSize: '13px',
                  textAlign: 'center',
                  transition: '0.2s',
                  position: 'relative',
                  overflow: 'hidden'
                }}
              >
                <div style={{ 
                  fontSize: '10px', 
                  opacity: selectedTable === slideIdx ? 0.95 : 0.6, 
                  marginBottom: '4px',
                  fontWeight: '700',
                  letterSpacing: '0.5px'
                }}>
                  {slide.slide_id}
                </div>
                <div style={{ fontSize: '13px' }}>{slide.slide_title}</div>
                {selectedTable === slideIdx && (
                  <div style={{
                    position: 'absolute',
                    top: 0,
                    right: 0,
                    padding: '4px 8px',
                    background: 'rgba(255,255,255,0.2)',
                    borderBottomLeftRadius: '8px',
                    fontSize: '9px',
                    fontWeight: '700'
                  }}>
                    ACTIVE
                  </div>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* Current Table Display */}
      {currentSlide && (
        <div className="card" style={{ borderTop: `4px solid ${companyColors[company] || '#0ea5e9'}` }}>
          <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3 className="card-title" style={{ margin: 0 }}>{currentSlide.slide_title}</h3>
            {currentSlide.narrative && (
              <button
                onClick={() => toggleInsight(currentSlide.slide_id)}
                style={{
                  background: companyColors[company] || '#0ea5e9',
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
                {expandedInsights[currentSlide.slide_id] ? '−' : '+'}
              </button>
            )}
          </div>
          
          <div className="card-body">
            {expandedInsights[currentSlide.slide_id] && currentSlide.narrative && (
              <div style={{
                marginBottom: '20px',
                padding: '16px',
                background: `${companyColors[company] || '#0ea5e9'}08`,
                border: `2px solid ${companyColors[company] || '#0ea5e9'}30`,
                borderRadius: '8px',
                borderLeft: `4px solid ${companyColors[company] || '#0ea5e9'}`
              }}>
                <div style={{ display: 'flex', alignItems: 'flex-start', gap: '10px' }}>
                  <span style={{ fontSize: '24px', flexShrink: 0 }}>🤖</span>
                  <div>
                    <strong style={{ color: companyColors[company] || '#0ea5e9', display: 'block', marginBottom: '8px', fontSize: '15px' }}>
                      Agent Insights:
                    </strong>
                    <p style={{ margin: '0 0 12px 0', fontSize: '15px', fontWeight: '600', color: '#111' }}>
                      {currentSlide.narrative.statement}
                    </p>
                    <p style={{ margin: 0, fontSize: '14px', lineHeight: '1.7', color: '#555' }}>
                      {currentSlide.narrative.explanation}
                    </p>
                  </div>
                </div>
              </div>
            )}
            
            {currentSlide.summary && (
              <div style={{ marginTop: '12px', padding: '12px', background: '#f8fafc', borderRadius: '6px' }}>
                <div style={{ fontSize: '13px', color: '#64748b', marginBottom: '4px' }}>
                  <strong>Rank:</strong> {currentSlide.summary.company_rank}
                </div>
                <div style={{ fontSize: '13px', color: '#64748b' }}>
                  <strong>Insight:</strong> {currentSlide.summary.key_insight}
                </div>
              </div>
            )}
            {currentSlide.peer_data && (
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '14px' }}>
                  <thead>
                    <tr style={{ background: '#f8fafc', borderBottom: '2px solid #e2e8f0' }}>
                      {currentSlide.peer_data.columns.map((col, idx) => (
                        <th key={idx} style={{ padding: '12px', textAlign: 'left', fontWeight: '600', color: '#334155' }}>
                          {col}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {currentSlide.peer_data.rows.map((row, idx) => {
                      const isTargetCompany = row.company === company;
                      return (
                        <tr 
                          key={idx}
                          style={{ 
                            borderBottom: '1px solid #e2e8f0',
                            background: isTargetCompany ? `${companyColors[company]}10` : 'white',
                            fontWeight: isTargetCompany ? '600' : 'normal'
                          }}
                        >
                          {Object.entries(row).map(([key, value], cellIdx) => (
                            <td key={cellIdx} style={{ padding: '12px', color: isTargetCompany ? companyColors[company] : '#334155' }}>
                              {value}
                            </td>
                          ))}
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ValuationTables;
