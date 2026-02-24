import React, { useState, useEffect } from 'react';
import { getSectionData } from '../utils/dataParser';

const SwotAnalysis = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedCompany, setSelectedCompany] = useState(0);

  useEffect(() => {
    fetchSwotData();
  }, []);

  const fetchSwotData = async () => {
    try {
      setLoading(true);
      setError(null);
      const sectionData = await getSectionData(6);
      setData(sectionData);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching SWOT data:', err);
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
        <p style={{ color: '#666' }}>Loading SWOT analysis...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ background: '#fee', border: '1px solid #fcc', borderRadius: '8px', padding: '20px', margin: '20px 0' }}>
        <p style={{ color: '#c00', margin: '0 0 10px 0' }}>⚠️ {error}</p>
        <button onClick={fetchSwotData} style={{ padding: '10px 20px', background: '#0ea5e9', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer' }}>
          Retry
        </button>
      </div>
    );
  }

  if (!data || !data.slides || data.slides.length === 0) {
    return <div style={{ textAlign: 'center', padding: '60px', color: '#666' }}>No SWOT analysis data available</div>;
  }

  const companies = data.slides || [];
  const currentSlide = companies[selectedCompany];

  return (
    <div>
      <div className="section-header">
        <h2>🎯 SWOT Analysis</h2>
        <p>{currentSlide?.narrative?.what_this_section_does || 'Strategic analysis of strengths, weaknesses, opportunities, and threats'}</p>
      </div>

      {/* Company Selector */}
      <div style={{ display: 'flex', gap: '12px', marginBottom: '24px' }}>
        {companies.map((slide, idx) => (
          <button
            key={idx}
            onClick={() => setSelectedCompany(idx)}
            style={{
              padding: '12px 24px',
              background: selectedCompany === idx ? '#0ea5e9' : 'white',
              color: selectedCompany === idx ? 'white' : '#334155',
              border: '2px solid #0ea5e9',
              borderRadius: '8px',
              cursor: 'pointer',
              fontWeight: '600',
              transition: 'all 0.2s'
            }}
          >
            {slide.company}
          </button>
        ))}
      </div>

      {/* SWOT Grid */}
      <div className="grid-2" style={{ gap: '1.5rem', marginBottom: '2rem' }}>
        {/* Strengths */}
        <div className="card" style={{ borderTop: '4px solid #0ea5e9' }}>
          <div className="card-header" style={{ backgroundColor: 'rgba(14, 165, 233, 0.1)' }}>
            <h3 className="card-title" style={{ color: '#0ea5e9' }}>💪 Strengths</h3>
          </div>
          <div className="card-body">
            {currentSlide?.narrative?.strengths && (
              <div>
                <p style={{ fontWeight: '600', marginBottom: '8px', color: '#0ea5e9', fontSize: '15px' }}>
                  {currentSlide.narrative.strengths.statement}
                </p>
                <p style={{ fontSize: '14px', color: '#0ea5e9', lineHeight: '1.7' }}>
                  {currentSlide.narrative.strengths.explanation}
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Weaknesses */}
        <div className="card" style={{ borderTop: '4px solid #1e293b' }}>
          <div className="card-header" style={{ backgroundColor: 'rgba(30, 41, 59, 0.1)' }}>
            <h3 className="card-title" style={{ color: '#1e293b' }}>⚠️ Weaknesses</h3>
          </div>
          <div className="card-body">
            {currentSlide?.narrative?.weaknesses && (
              <div>
                <p style={{ fontWeight: '600', marginBottom: '8px', color: '#1e293b', fontSize: '15px' }}>
                  {currentSlide.narrative.weaknesses.statement}
                </p>
                <p style={{ fontSize: '14px', color: '#1e293b', lineHeight: '1.7' }}>
                  {currentSlide.narrative.weaknesses.explanation}
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Opportunities */}
        <div className="card" style={{ borderTop: '4px solid #0ea5e9' }}>
          <div className="card-header" style={{ backgroundColor: 'rgba(14, 165, 233, 0.1)' }}>
            <h3 className="card-title" style={{ color: '#0ea5e9' }}>🚀 Opportunities</h3>
          </div>
          <div className="card-body">
            {currentSlide?.narrative?.opportunities && (
              <div>
                <p style={{ fontWeight: '600', marginBottom: '8px', color: '#0ea5e9', fontSize: '15px' }}>
                  {currentSlide.narrative.opportunities.statement}
                </p>
                <p style={{ fontSize: '14px', color: '#0ea5e9', lineHeight: '1.7' }}>
                  {currentSlide.narrative.opportunities.explanation}
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Threats */}
        <div className="card" style={{ borderTop: '4px solid #1e293b' }}>
          <div className="card-header" style={{ backgroundColor: 'rgba(30, 41, 59, 0.1)' }}>
            <h3 className="card-title" style={{ color: '#1e293b' }}>🛡️ Threats</h3>
          </div>
          <div className="card-body">
            {currentSlide?.narrative?.threats && (
              <div>
                <p style={{ fontWeight: '600', marginBottom: '8px', color: '#1e293b', fontSize: '15px' }}>
                  {currentSlide.narrative.threats.statement}
                </p>
                <p style={{ fontSize: '14px', color: '#1e293b', lineHeight: '1.7' }}>
                  {currentSlide.narrative.threats.explanation}
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SwotAnalysis;
