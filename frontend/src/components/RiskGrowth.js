import React, { useState, useEffect } from 'react';
import { getSectionData } from '../utils/dataParser';

const RiskGrowth = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchRiskData();
  }, []);

  const fetchRiskData = async () => {
    try {
      setLoading(true);
      setError(null);
      const sectionData = await getSectionData(7);
      setData(sectionData);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching risk data:', err);
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
        <p style={{ color: '#666' }}>Loading risk & growth analysis...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ background: '#fee', border: '1px solid #fcc', borderRadius: '8px', padding: '20px', margin: '20px 0' }}>
        <p style={{ color: '#c00', margin: '0 0 10px 0' }}>⚠️ {error}</p>
        <button onClick={fetchRiskData} style={{ padding: '10px 20px', background: '#0ea5e9', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer' }}>
          Retry
        </button>
      </div>
    );
  }

  if (!data || !data.slides || data.slides.length === 0) {
    return <div style={{ textAlign: 'center', padding: '60px', color: '#666' }}>No risk & growth data available</div>;
  }

  const narrative = data.slides[0]?.narrative || {};
  const vodafoneDrivers = narrative.vodafone_drivers || {};
  const apolloDrivers = narrative.apollo_drivers || {};

  return (
    <div>
      <div className="section-header">
        <h2>⚠️ Risk & Growth Drivers</h2>
        <p>{narrative.what_this_section_does || 'Analysis of key risk factors and growth opportunities'}</p>
      </div>

      {/* Combined View for Both Companies */}
      <div className="grid-2" style={{ gap: '1.5rem', marginBottom: '2rem' }}>
        {/* Vodafone Idea */}
        <div className="card" style={{ borderTop: '4px solid #0ea5e9' }}>
          <div className="card-header" style={{ backgroundColor: 'rgba(14, 165, 233, 0.1)' }}>
            <h3 className="card-title" style={{ color: '#0ea5e9' }}>📱 Vodafone Idea</h3>
          </div>
          <div className="card-body">
            {/* Risk Drivers */}
            {vodafoneDrivers.risk_factors && (
              <div style={{ marginBottom: '20px', padding: '12px', background: '#f1f5f9', borderLeft: '3px solid #1e293b', borderRadius: '4px' }}>
                <h4 style={{ fontSize: '14px', fontWeight: '600', color: '#1e293b', marginBottom: '8px' }}>
                  ⚠️ Risk Factors
                </h4>
                <p style={{ fontWeight: '600', fontSize: '14px', marginBottom: '6px', color: '#1e293b' }}>
                  {vodafoneDrivers.risk_factors.statement}
                </p>
                <p style={{ fontSize: '13px', color: '#1e293b', lineHeight: '1.6' }}>
                  {vodafoneDrivers.risk_factors.explanation}
                </p>
              </div>
            )}
            
            {/* Growth Drivers */}
            {vodafoneDrivers.growth_drivers && (
              <div style={{ padding: '12px', background: '#f0f9ff', borderLeft: '3px solid #0ea5e9', borderRadius: '4px' }}>
                <h4 style={{ fontSize: '14px', fontWeight: '600', color: '#0ea5e9', marginBottom: '8px' }}>
                  🚀 Growth Drivers
                </h4>
                <p style={{ fontWeight: '600', fontSize: '14px', marginBottom: '6px', color: '#0ea5e9' }}>
                  {vodafoneDrivers.growth_drivers.statement}
                </p>
                <p style={{ fontSize: '13px', color: '#0ea5e9', lineHeight: '1.6' }}>
                  {vodafoneDrivers.growth_drivers.explanation}
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Apollo Micro Systems */}
        <div className="card" style={{ borderTop: '4px solid #0ea5e9' }}>
          <div className="card-header" style={{ backgroundColor: 'rgba(14, 165, 233, 0.1)' }}>
            <h3 className="card-title" style={{ color: '#0ea5e9' }}>🛡️ Apollo Micro Systems</h3>
          </div>
          <div className="card-body">
            {/* Risk Drivers */}
            {apolloDrivers.risk_factors && (
              <div style={{ marginBottom: '20px', padding: '12px', background: '#f1f5f9', borderLeft: '3px solid #1e293b', borderRadius: '4px' }}>
                <h4 style={{ fontSize: '14px', fontWeight: '600', color: '#1e293b', marginBottom: '8px' }}>
                  ⚠️ Risk Factors
                </h4>
                <p style={{ fontWeight: '600', fontSize: '14px', marginBottom: '6px', color: '#1e293b' }}>
                  {apolloDrivers.risk_factors.statement}
                </p>
                <p style={{ fontSize: '13px', color: '#1e293b', lineHeight: '1.6' }}>
                  {apolloDrivers.risk_factors.explanation}
                </p>
              </div>
            )}
            
            {/* Growth Drivers */}
            {apolloDrivers.growth_drivers && (
              <div style={{ padding: '12px', background: '#f0f9ff', borderLeft: '3px solid #0ea5e9', borderRadius: '4px' }}>
                <h4 style={{ fontSize: '14px', fontWeight: '600', color: '#0ea5e9', marginBottom: '8px' }}>
                  🚀 Growth Drivers
                </h4>
                <p style={{ fontWeight: '600', fontSize: '14px', marginBottom: '6px', color: '#0ea5e9' }}>
                  {apolloDrivers.growth_drivers.statement}
                </p>
                <p style={{ fontSize: '13px', color: '#0ea5e9', lineHeight: '1.6' }}>
                  {apolloDrivers.growth_drivers.explanation}
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Key Takeaways */}
      <div className="card" style={{ borderTop: '4px solid #0ea5e9' }}>
        <div className="card-header">
          <h3 className="card-title">🎯 Risk/Reward Assessment</h3>
        </div>
        <div className="card-body">
          <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
            <li style={{ marginBottom: '12px', paddingLeft: '24px', position: 'relative', lineHeight: '1.6' }}>
              <span style={{ position: 'absolute', left: 0, fontSize: '16px' }}>📊</span>
              <strong>Vodafone Idea:</strong> High-risk profile with asymmetric upside potential if 5G rollout and debt restructuring succeed
            </li>
            <li style={{ marginBottom: '12px', paddingLeft: '24px', position: 'relative', lineHeight: '1.6' }}>
              <span style={{ position: 'absolute', left: 0, fontSize: '16px' }}>📈</span>
              <strong>Apollo Micro:</strong> Moderate risk with steady growth trajectory supported by defense modernization programs
            </li>
            <li style={{ paddingLeft: '24px', position: 'relative', lineHeight: '1.6' }}>
              <span style={{ position: 'absolute', left: 0, fontSize: '16px' }}>💡</span>
              <strong>Strategy:</strong> Investors must weigh execution risks against growth potential in each company's respective market
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default RiskGrowth;
