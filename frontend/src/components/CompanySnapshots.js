import React, { useState, useEffect } from 'react';
import { parseAnalystDataFile } from '../utils/dataParser';

const CompanySnapshots = () => {
  const [companies, setCompanies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchCompanyData();
  }, []);

  const fetchCompanyData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Fetch data from dataParser
      const allData = await parseAnalystDataFile();
      const data = allData.sections.section1; // Section 1: Company Snapshots
      
      // Extract company snapshots from the section data
      if (data.slides && Array.isArray(data.slides)) {
        const companyData = data.slides.map(slide => ({
          name: slide.company,
          slide_id: slide.slide_id,
          color: '#0ea5e9',
          business_overview: slide.narrative?.business_overview?.statement || "",
          business_overview_explanation: slide.narrative?.business_overview?.explanation || "",
          business_model: slide.narrative?.business_model?.statement || "",
          business_model_explanation: slide.narrative?.business_model?.explanation || "",
          strategic_context: slide.narrative?.strategic_context?.statement || "",
          strategic_context_explanation: slide.narrative?.strategic_context?.explanation || ""
        }));
        setCompanies(companyData);
      }
    } catch (err) {
      setError(err.message);
      console.error('Error fetching company data:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="loading-container" style={{ textAlign: 'center', padding: '60px 20px' }}>
        <div className="spinner" style={{
          width: '50px',
          height: '50px',
          border: '5px solid #f3f3f3',
          borderTop: '5px solid #0ea5e9',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite',
          margin: '0 auto 20px'
        }}></div>
        <p style={{ color: '#666', fontSize: '16px' }}>Loading company data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-container" style={{
        background: '#fee',
        border: '1px solid #fcc',
        borderRadius: '8px',
        padding: '20px',
        margin: '20px 0',
        textAlign: 'center'
      }}>
        <p style={{ color: '#c00', fontSize: '16px', margin: '0 0 10px 0' }}>⚠️ Error loading data</p>
        <p style={{ color: '#666', fontSize: '14px', margin: '0 0 15px 0' }}>{error}</p>
        <button
          onClick={fetchCompanyData}
          style={{
            padding: '10px 20px',
            background: '#0ea5e9',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: '500'
          }}
        >
          Retry
        </button>
      </div>
    );
  }

  if (companies.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '60px 20px', color: '#666' }}>
        <p style={{ fontSize: '18px' }}>📭 No company data available</p>
      </div>
    );
  }

  return (
    <div>
      <div className="section-header">
        <h2>🏢 Company Snapshots</h2>
        <p>Overview of business operations, models, and strategic context</p>
      </div>

      <div className="grid-2">
        {companies.map((company, index) => (
          <CompanyCard key={index} company={company} />
        ))}
      </div>
    </div>
  );
};

// Separate component for each company card with expandable sections
const CompanyCard = ({ company }) => {
  const [expandedSections, setExpandedSections] = useState({
    overview: false,
    model: false,
    context: false
  });

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  return (
    <div className="card" style={{ borderTop: `4px solid ${company.color}` }}>
      <div className="card-header">
        <h3 className="card-title">{company.name}</h3>
        <span className="badge" style={{ 
          backgroundColor: `${company.color}20`, 
          color: company.color, 
          border: `1px solid ${company.color}` 
        }}>
          {company.slide_id}
        </span>
      </div>
      
      <div className="card-body">
        {/* Business Overview Section */}
        <div style={{ marginBottom: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
            <h4 style={{ color: 'var(--primary-color)', margin: 0, fontSize: '1rem' }}>
              📋 Business Overview
            </h4>
            {company.business_overview_explanation && (
              <button
                onClick={() => toggleSection('overview')}
                style={{
                  background: 'none',
                  border: 'none',
                  color: company.color,
                  cursor: 'pointer',
                  fontSize: '20px',
                  padding: '0 5px'
                }}
                title="Toggle explanation"
              >
                {expandedSections.overview ? '−' : '+'}
              </button>
            )}
          </div>
          <p style={{ lineHeight: '1.6', marginBottom: '8px' }}>{company.business_overview}</p>
          {expandedSections.overview && company.business_overview_explanation && (
            <div style={{
              background: `${company.color}08`,
              border: `1px solid ${company.color}30`,
              borderRadius: '8px',
              padding: '12px',
              marginTop: '8px',
              fontSize: '0.9rem',
              lineHeight: '1.6',
              color: '#555'
            }}>
              <strong style={{ color: company.color, display: 'block', marginBottom: '6px' }}>
                💡 Why this matters:
              </strong>
              {company.business_overview_explanation}
            </div>
          )}
        </div>

        {/* Business Model Section */}
        <div style={{ marginBottom: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
            <h4 style={{ color: 'var(--accent-color)', margin: 0, fontSize: '1rem' }}>
              💼 Business Model
            </h4>
            {company.business_model_explanation && (
              <button
                onClick={() => toggleSection('model')}
                style={{
                  background: 'none',
                  border: 'none',
                  color: company.color,
                  cursor: 'pointer',
                  fontSize: '20px',
                  padding: '0 5px'
                }}
                title="Toggle explanation"
              >
                {expandedSections.model ? '−' : '+'}
              </button>
            )}
          </div>
          <p style={{ lineHeight: '1.6', marginBottom: '8px' }}>{company.business_model}</p>
          {expandedSections.model && company.business_model_explanation && (
            <div style={{
              background: `${company.color}08`,
              border: `1px solid ${company.color}30`,
              borderRadius: '8px',
              padding: '12px',
              marginTop: '8px',
              fontSize: '0.9rem',
              lineHeight: '1.6',
              color: '#555'
            }}>
              <strong style={{ color: company.color, display: 'block', marginBottom: '6px' }}>
                💡 Why this matters:
              </strong>
              {company.business_model_explanation}
            </div>
          )}
        </div>

        {/* Strategic Context Section */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
            <h4 style={{ color: 'var(--secondary-color)', margin: 0, fontSize: '1rem' }}>
              🎯 Strategic Context
            </h4>
            {company.strategic_context_explanation && (
              <button
                onClick={() => toggleSection('context')}
                style={{
                  background: 'none',
                  border: 'none',
                  color: company.color,
                  cursor: 'pointer',
                  fontSize: '20px',
                  padding: '0 5px'
                }}
                title="Toggle explanation"
              >
                {expandedSections.context ? '−' : '+'}
              </button>
            )}
          </div>
          <p style={{ lineHeight: '1.6', marginBottom: '8px' }}>{company.strategic_context}</p>
          {expandedSections.context && company.strategic_context_explanation && (
            <div style={{
              background: `${company.color}08`,
              border: `1px solid ${company.color}30`,
              borderRadius: '8px',
              padding: '12px',
              marginTop: '8px',
              fontSize: '0.9rem',
              lineHeight: '1.6',
              color: '#555'
            }}>
              <strong style={{ color: company.color, display: 'block', marginBottom: '6px' }}>
                💡 Why this matters:
              </strong>
              {company.strategic_context_explanation}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CompanySnapshots;
