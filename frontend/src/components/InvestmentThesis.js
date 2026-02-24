import React, { useState, useEffect } from 'react';
import { getSectionData } from '../utils/dataParser';

const InvestmentThesis = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchThesisData();
  }, []);

  const fetchThesisData = async () => {
    try {
      setLoading(true);
      setError(null);
      const sectionData = await getSectionData(8);
      setData(sectionData);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching investment thesis data:', err);
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
        <p style={{ color: '#666' }}>Loading investment thesis...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ background: '#fee', border: '1px solid #fcc', borderRadius: '8px', padding: '20px', margin: '20px 0' }}>
        <p style={{ color: '#c00', margin: '0 0 10px 0' }}>⚠️ {error}</p>
        <button onClick={fetchThesisData} style={{ padding: '10px 20px', background: '#0ea5e9', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer' }}>
          Retry
        </button>
      </div>
    );
  }

  if (!data || !data.slides || data.slides.length === 0) {
    return <div style={{ textAlign: 'center', padding: '60px', color: '#666' }}>No investment thesis data available</div>;
  }

  const narrative = data.slides[0]?.narrative || {};

  const getRecommendationStyle = (recommendation) => {
    const rec = recommendation?.toLowerCase() || '';
    if (rec.includes('buy')) {
      return { color: '#10b981', bgColor: 'rgba(16, 185, 129, 0.1)', icon: '📈' };
    } else if (rec.includes('hold')) {
      return { color: '#f59e0b', bgColor: 'rgba(245, 158, 11, 0.1)', icon: '⏸️' };
    } else if (rec.includes('sell')) {
      return { color: '#dc2626', bgColor: 'rgba(220, 38, 38, 0.1)', icon: '📉' };
    }
    return { color: '#6b7280', bgColor: 'rgba(107, 114, 128, 0.1)', icon: '💡' };
  };

  return (
    <div>
      <div className="section-header">
        <h2>💡 Investment Thesis & Recommendations</h2>
        <p>{narrative.what_this_section_does || 'Investment recommendations and strategic outlook'}</p>
      </div>

      {/* Investment Recommendations */}
      <div className="grid-2" style={{ gap: '1.5rem', marginBottom: '2rem' }}>
        {/* Vodafone Idea */}
        {narrative.vodafone_thesis && (
          <div className="card" style={{ borderTop: '4px solid #dc2626' }}>
            <div className="card-header" style={{ backgroundColor: getRecommendationStyle(narrative.vodafone_thesis.recommendation).bgColor }}>
              <h3 className="card-title" style={{ color: '#dc2626' }}>
                📱 Vodafone Idea
              </h3>
            </div>
            <div className="card-body">
              {/* Recommendation */}
              <div style={{ marginBottom: '16px', padding: '12px', background: getRecommendationStyle(narrative.vodafone_thesis.recommendation).bgColor, borderRadius: '6px', borderLeft: `4px solid ${getRecommendationStyle(narrative.vodafone_thesis.recommendation).color}` }}>
                <div style={{ fontSize: '18px', fontWeight: '700', color: getRecommendationStyle(narrative.vodafone_thesis.recommendation).color, marginBottom: '4px' }}>
                  {getRecommendationStyle(narrative.vodafone_thesis.recommendation).icon} {narrative.vodafone_thesis.recommendation}
                </div>
              </div>

              {/* Core Thesis */}
              <div style={{ marginBottom: '12px' }}>
                <h4 style={{ fontSize: '14px', fontWeight: '600', color: '#111', marginBottom: '6px' }}>Core Thesis</h4>
                <p style={{ fontSize: '14px', color: '#555', lineHeight: '1.6', marginBottom: '8px' }}>
                  {narrative.vodafone_thesis.core_thesis}
                </p>
                <p style={{ fontSize: '13px', color: '#666', lineHeight: '1.6' }}>
                  {narrative.vodafone_thesis.thesis_explanation}
                </p>
              </div>

              {/* Investor Suitability */}
              <div style={{ marginBottom: '12px' }}>
                <h4 style={{ fontSize: '14px', fontWeight: '600', color: '#111', marginBottom: '6px' }}>Investor Suitability</h4>
                <p style={{ fontSize: '13px', color: '#666', lineHeight: '1.6' }}>
                  {narrative.vodafone_thesis.investor_suitability}
                </p>
              </div>

              {/* Decision Logic */}
              <div style={{ padding: '10px', background: '#f9fafb', borderRadius: '4px', border: '1px solid #e5e7eb' }}>
                <h4 style={{ fontSize: '13px', fontWeight: '600', color: '#374151', marginBottom: '6px' }}>🎯 Decision Logic</h4>
                <p style={{ fontSize: '13px', color: '#6b7280', lineHeight: '1.6' }}>
                  {narrative.vodafone_thesis.decision_logic}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Apollo Micro Systems */}
        {narrative.apollo_thesis && (
          <div className="card" style={{ borderTop: '4px solid #2563eb' }}>
            <div className="card-header" style={{ backgroundColor: getRecommendationStyle(narrative.apollo_thesis.recommendation).bgColor }}>
              <h3 className="card-title" style={{ color: '#2563eb' }}>
                🛡️ Apollo Micro Systems
              </h3>
            </div>
            <div className="card-body">
              {/* Recommendation */}
              <div style={{ marginBottom: '16px', padding: '12px', background: getRecommendationStyle(narrative.apollo_thesis.recommendation).bgColor, borderRadius: '6px', borderLeft: `4px solid ${getRecommendationStyle(narrative.apollo_thesis.recommendation).color}` }}>
                <div style={{ fontSize: '18px', fontWeight: '700', color: getRecommendationStyle(narrative.apollo_thesis.recommendation).color, marginBottom: '4px' }}>
                  {getRecommendationStyle(narrative.apollo_thesis.recommendation).icon} {narrative.apollo_thesis.recommendation}
                </div>
              </div>

              {/* Core Thesis */}
              <div style={{ marginBottom: '12px' }}>
                <h4 style={{ fontSize: '14px', fontWeight: '600', color: '#111', marginBottom: '6px' }}>Core Thesis</h4>
                <p style={{ fontSize: '14px', color: '#555', lineHeight: '1.6', marginBottom: '8px' }}>
                  {narrative.apollo_thesis.core_thesis}
                </p>
                <p style={{ fontSize: '13px', color: '#666', lineHeight: '1.6' }}>
                  {narrative.apollo_thesis.thesis_explanation}
                </p>
              </div>

              {/* Investor Suitability */}
              <div style={{ marginBottom: '12px' }}>
                <h4 style={{ fontSize: '14px', fontWeight: '600', color: '#111', marginBottom: '6px' }}>Investor Suitability</h4>
                <p style={{ fontSize: '13px', color: '#666', lineHeight: '1.6' }}>
                  {narrative.apollo_thesis.investor_suitability}
                </p>
              </div>

              {/* Decision Logic */}
              <div style={{ padding: '10px', background: '#f9fafb', borderRadius: '4px', border: '1px solid #e5e7eb' }}>
                <h4 style={{ fontSize: '13px', fontWeight: '600', color: '#374151', marginBottom: '6px' }}>🎯 Decision Logic</h4>
                <p style={{ fontSize: '13px', color: '#6b7280', lineHeight: '1.6' }}>
                  {narrative.apollo_thesis.decision_logic}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Risk Disclaimer */}
      <div style={{ padding: '16px', backgroundColor: '#fef3c7', borderRadius: '8px', border: '2px solid #fbbf24' }}>
        <p style={{ margin: 0, fontSize: '13px', color: '#78350f', lineHeight: '1.6' }}>
          <strong>⚠️ Investment Disclaimer:</strong> This analysis is for informational purposes only and should not be considered as investment advice. 
          Past performance is not indicative of future results. Market conditions, regulatory changes, and company-specific factors can significantly impact investment outcomes. 
          Please consult with a qualified financial advisor before making any investment decisions.
        </p>
      </div>
    </div>
  );
};

export default InvestmentThesis;
