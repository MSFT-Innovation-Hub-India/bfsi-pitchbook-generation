import React, { useState, useEffect } from 'react';
import { parseAnalystDataFile } from '../utils/dataParser';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

const FinancialStatements = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedCompany, setSelectedCompany] = useState(0);
  const [expandedSections, setExpandedSections] = useState({});

  useEffect(() => {
    fetchFinancialData();
  }, []);

  const fetchFinancialData = async () => {
    try {
      setLoading(true);
      setError(null);
      const allData = await parseAnalystDataFile();
      setData(allData.sections.section3);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching financial data:', err);
    } finally {
      setLoading(false);
    }
  };

  const toggleSection = (section) => {
    setExpandedSections(prev => ({ ...prev, [section]: !prev[section] }));
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '60px 20px' }}>
        <div className="spinner" style={{
          width: '50px', height: '50px', border: '5px solid #f3f3f3',
          borderTop: '5px solid #0ea5e9', borderRadius: '50%',
          animation: 'spin 1s linear infinite', margin: '0 auto 20px'
        }}></div>
        <p style={{ color: '#666' }}>Loading financial statements...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ background: '#fee', border: '1px solid #fcc', borderRadius: '8px', padding: '20px', margin: '20px 0' }}>
        <p style={{ color: '#c00', margin: '0 0 10px 0' }}>⚠️ {error}</p>
        <button onClick={fetchFinancialData} style={{ padding: '10px 20px', background: '#0ea5e9', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer' }}>
          Retry
        </button>
      </div>
    );
  }

  if (!data || !data.slides || data.slides.length === 0) {
    return <div style={{ textAlign: 'center', padding: '60px', color: '#666' }}>No financial data available</div>;
  }

  const currentSlide = data.slides[selectedCompany];
  const companyColor = "#0ea5e9";

  const sections = [
    { key: 'revenue_analysis', icon: '📊', title: 'Revenue Analysis' },
    { key: 'margin_analysis', icon: '📈', title: 'Margin Analysis' },
    { key: 'leverage_analysis', icon: '⚖️', title: 'Leverage Analysis' },
    { key: 'cash_flow_analysis', icon: '💰', title: 'Cash Flow Analysis' }
  ];

  return (
    <div>
      <div className="section-header">
        <h2>📊 Financial Statements</h2>
        <p>{currentSlide.narrative?.what_this_section_does || 'Analysis of financial performance and health'}</p>
      </div>

      {/* Company Selector */}
      <div style={{ display: 'flex', gap: '12px', marginBottom: '24px' }}>
        {data.slides.map((slide, idx) => (
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

      {/* Visualizations with Agent Insights */}
      {currentSlide.visualizations && currentSlide.visualizations.length > 0 && (
        <div style={{ marginTop: '24px' }}>
          <h3 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '20px', color: companyColor }}>
            📊 Financial Trend Analysis
          </h3>
          {currentSlide.visualizations.map((viz, idx) => (
            <div key={idx} className="card" style={{ marginBottom: '20px', borderTop: `3px solid ${companyColor}` }}>
              <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h4 className="card-title" style={{ margin: 0 }}>{viz.title}</h4>
                {viz.interpretation && (
                  <button
                    onClick={() => toggleSection(`viz_${idx}`)}
                    style={{
                      background: companyColor,
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
                    {expandedSections[`viz_${idx}`] ? '−' : '+'}
                  </button>
                )}
              </div>
              <div className="card-body">
                <ResponsiveContainer width="100%" height={300}>
                  {viz.type === 'line_chart' ? (
                    <LineChart data={viz.data.labels.map((label, i) => ({
                      label,
                      ...viz.data.datasets.reduce((acc, dataset) => {
                        acc[dataset.label] = dataset.data[i];
                        return acc;
                      }, {})
                    }))}>
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
                  ) : (
                    <BarChart data={viz.data.labels.map((label, i) => ({
                      label,
                      ...viz.data.datasets.reduce((acc, dataset) => {
                        acc[dataset.label] = dataset.data[i];
                        return acc;
                      }, {})
                    }))}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="label" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      {viz.data.datasets.map((dataset, dsIdx) => (
                        <Bar
                          key={dsIdx}
                          dataKey={dataset.label}
                          fill={dataset.borderColor || dataset.backgroundColor}
                        />
                      ))}
                    </BarChart>
                  )}
                </ResponsiveContainer>
                
                {expandedSections[`viz_${idx}`] && viz.interpretation && (
                  <div style={{
                    marginTop: '16px',
                    padding: '16px',
                    background: `${companyColor}08`,
                    border: `2px solid ${companyColor}30`,
                    borderRadius: '8px',
                    borderLeft: `4px solid ${companyColor}`
                  }}>
                    <div style={{ display: 'flex', alignItems: 'flex-start', gap: '10px' }}>
                      <span style={{ fontSize: '24px', flexShrink: 0 }}>🤖</span>
                      <div>
                        <strong style={{ color: companyColor, display: 'block', marginBottom: '8px', fontSize: '15px' }}>
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
          ))}
        </div>
      )}

      {/* Financial Analysis Sections */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        {sections.map((section) => {
          const sectionData = currentSlide.narrative?.[section.key];
          if (!sectionData) return null;

          return (
            <div key={section.key} className="card" style={{ borderTop: `4px solid ${companyColor}` }}>
              <div className="card-body">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                  <h3 style={{ color: companyColor, margin: 0, fontSize: '18px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span>{section.icon}</span>
                    <span>{section.title}</span>
                  </h3>
                  {sectionData.explanation && (
                    <button
                      onClick={() => toggleSection(section.key)}
                      style={{
                        background: 'none',
                        border: 'none',
                        color: companyColor,
                        cursor: 'pointer',
                        fontSize: '20px',
                        padding: '0 5px',
                        fontWeight: 'bold'
                      }}
                      title="Toggle detailed explanation"
                    >
                      {expandedSections[section.key] ? '−' : '+'}
                    </button>
                  )}
                </div>

                <p style={{ fontSize: '16px', lineHeight: '1.6', marginBottom: '12px', fontWeight: '500' }}>
                  {sectionData.statement}
                </p>

                {expandedSections[section.key] && sectionData.explanation && (
                  <div style={{
                    background: `${companyColor}08`,
                    border: `1px solid ${companyColor}30`,
                    borderRadius: '8px',
                    padding: '16px',
                    marginTop: '12px',
                    fontSize: '14px',
                    lineHeight: '1.7',
                    color: '#555'
                  }}>
                    <strong style={{ color: companyColor, display: 'block', marginBottom: '8px' }}>
                      💡 Detailed Analysis:
                    </strong>
                    {sectionData.explanation}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Summary Box */}
      <div className="card" style={{ borderTop: `4px solid ${companyColor}`, marginTop: '24px', background: `${companyColor}05` }}>
        <div className="card-header">
          <h3 className="card-title">Key Takeaways</h3>
        </div>
        <div className="card-body">
          <ul style={{ margin: 0, paddingLeft: '20px', lineHeight: '1.8', color: '#555' }}>
            {currentSlide.narrative?.revenue_analysis && (
              <li><strong>Revenue:</strong> {currentSlide.narrative.revenue_analysis.statement}</li>
            )}
            {currentSlide.narrative?.margin_analysis && (
              <li><strong>Margins:</strong> {currentSlide.narrative.margin_analysis.statement}</li>
            )}
            {currentSlide.narrative?.leverage_analysis && (
              <li><strong>Leverage:</strong> {currentSlide.narrative.leverage_analysis.statement}</li>
            )}
            {currentSlide.narrative?.cash_flow_analysis && (
              <li><strong>Cash Flow:</strong> {currentSlide.narrative.cash_flow_analysis.statement}</li>
            )}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default FinancialStatements;
