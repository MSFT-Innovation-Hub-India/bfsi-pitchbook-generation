import React, { useState, useEffect } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { parseAnalystDataFile } from '../utils/dataParser';

const NewsSentiment = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedCompany, setSelectedCompany] = useState(0);
  const [expandedNews, setExpandedNews] = useState({});

  useEffect(() => {
    fetchNewsData();
  }, []);

  const fetchNewsData = async () => {
    try {
      setLoading(true);
      setError(null);
      const allData = await parseAnalystDataFile();
      setData(allData.sections.section2);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching news data:', err);
    } finally {
      setLoading(false);
    }
  };

  const toggleNews = (index) => {
    setExpandedNews(prev => ({ ...prev, [index]: !prev[index] }));
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '60px 20px' }}>
        <div className="spinner" style={{
          width: '50px', height: '50px', border: '5px solid #f3f3f3',
          borderTop: '5px solid #0ea5e9', borderRadius: '50%',
          animation: 'spin 1s linear infinite', margin: '0 auto 20px'
        }}></div>
        <p style={{ color: '#666' }}>Loading news & sentiment data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ background: '#fee', border: '1px solid #fcc', borderRadius: '8px', padding: '20px', margin: '20px 0' }}>
        <p style={{ color: '#c00', margin: '0 0 10px 0' }}>⚠️ {error}</p>
        <button onClick={fetchNewsData} style={{ padding: '10px 20px', background: '#0ea5e9', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer' }}>
          Retry
        </button>
      </div>
    );
  }

  if (!data || !data.slides || data.slides.length === 0) {
    return <div style={{ textAlign: 'center', padding: '60px', color: '#666' }}>No news data available</div>;
  }

  const currentSlide = data.slides[selectedCompany];
  const companyColor = "#0ea5e9";

  // Prepare sentiment data for pie chart
  const sentimentCounts = {
    HIGH: 0,
    MEDIUM: 0,
    LOW: 0
  };
  
  currentSlide.news_items?.forEach(item => {
    sentimentCounts[item.impact_level]++;
  });

  const chartData = [
    { name: 'High Impact', value: sentimentCounts.HIGH, color: '#dc2626' },
    { name: 'Medium Impact', value: sentimentCounts.MEDIUM, color: '#f59e0b' },
    { name: 'Low Impact', value: sentimentCounts.LOW, color: '#10b981' }
  ].filter(item => item.value > 0);

  return (
    <div>
      <div className="section-header">
        <h2>📰 News & Sentiment Analysis</h2>
        <p>{currentSlide.news_overview?.what_this_section_does || 'Analysis of recent news and market sentiment'}</p>
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

      {/* Overall Sentiment Card */}
      <div className="card" style={{ borderTop: `4px solid ${companyColor}`, marginBottom: '24px' }}>
        <div className="card-body">
          <h3 style={{ color: companyColor, marginBottom: '12px' }}>Overall Market Sentiment</h3>
          <p style={{ fontSize: '16px', lineHeight: '1.6', marginBottom: '12px' }}>
            <strong>{currentSlide.news_overview?.overall_sentiment_statement?.statement}</strong>
          </p>
          {currentSlide.news_overview?.overall_sentiment_statement?.explanation && (
            <div style={{
              background: `${companyColor}08`,
              border: `1px solid ${companyColor}30`,
              borderRadius: '8px',
              padding: '16px',
              fontSize: '14px',
              lineHeight: '1.6',
              color: '#555'
            }}>
              <strong style={{ color: companyColor, display: 'block', marginBottom: '8px' }}>💡 Analysis:</strong>
              {currentSlide.news_overview?.overall_sentiment_statement?.explanation}
            </div>
          )}
        </div>
      </div>

      {/* Sentiment Distribution Chart */}
      {chartData.length > 0 && (
        <div className="card" style={{ marginBottom: '24px' }}>
          <div className="card-header">
            <h3 className="card-title">Impact Distribution</h3>
          </div>
          <div className="card-body">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={chartData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* News Items */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {currentSlide.news_items?.map((item, index) => (
          <div
            key={index}
            className="card"
            style={{
              borderLeft: `4px solid ${
                item.impact_level === 'HIGH' ? '#dc2626' :
                item.impact_level === 'MEDIUM' ? '#f59e0b' : '#10b981'
              }`
            }}
          >
            <div className="card-body">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '12px' }}>
                <h4 style={{ fontSize: '16px', fontWeight: '600', color: '#1a1a1a', margin: 0, flex: 1 }}>
                  {item.headline}
                </h4>
                <span
                  style={{
                    padding: '4px 12px',
                    borderRadius: '12px',
                    fontSize: '12px',
                    fontWeight: '600',
                    marginLeft: '12px',
                    background: item.impact_level === 'HIGH' ? '#fee2e2' :
                               item.impact_level === 'MEDIUM' ? '#fef3c7' : '#d1fae5',
                    color: item.impact_level === 'HIGH' ? '#dc2626' :
                          item.impact_level === 'MEDIUM' ? '#f59e0b' : '#10b981'
                  }}
                >
                  {item.impact_level} IMPACT
                </span>
              </div>

              <p style={{ fontSize: '14px', lineHeight: '1.6', color: '#555', marginBottom: '12px' }}>
                {item.detailed_explanation}
              </p>

              <button
                onClick={() => toggleNews(index)}
                style={{
                  background: 'none',
                  border: `1px solid ${companyColor}`,
                  color: companyColor,
                  padding: '8px 16px',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '13px',
                  fontWeight: '500',
                  transition: 'all 0.2s'
                }}
              >
                {expandedNews[index] ? '− Hide' : '+ Show'} Investor Interpretation
              </button>

              {expandedNews[index] && (
                <div style={{
                  marginTop: '12px',
                  background: `${companyColor}08`,
                  border: `1px solid ${companyColor}30`,
                  borderRadius: '8px',
                  padding: '16px',
                  fontSize: '14px',
                  lineHeight: '1.6',
                  color: '#555'
                }}>
                  <strong style={{ color: companyColor, display: 'block', marginBottom: '8px' }}>
                    💼 Investment Perspective:
                  </strong>
                  {item.investor_interpretation}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Summary Conclusion */}
      {currentSlide.summary_conclusion && (
        <div className="card" style={{ borderTop: `4px solid ${companyColor}`, marginTop: '24px' }}>
          <div className="card-header">
            <h3 className="card-title">Summary & Conclusion</h3>
          </div>
          <div className="card-body">
            <p style={{ fontSize: '16px', lineHeight: '1.6', marginBottom: '12px', fontWeight: '600' }}>
              {currentSlide.summary_conclusion.statement}
            </p>
            <div style={{
              background: `${companyColor}08`,
              border: `1px solid ${companyColor}30`,
              borderRadius: '8px',
              padding: '16px',
              fontSize: '14px',
              lineHeight: '1.6',
              color: '#555'
            }}>
              {currentSlide.summary_conclusion.explanation}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default NewsSentiment;
