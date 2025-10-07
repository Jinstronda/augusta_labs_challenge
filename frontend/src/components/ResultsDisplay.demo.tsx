/**
 * ResultsDisplay Demo
 * 
 * Demonstrates all states of the ResultsDisplay component:
 * - Loading state
 * - Incentive results
 * - Company results
 * - Empty state
 * - Error states
 */

import React, { useState } from 'react';
import { ResultsDisplay } from './ResultsDisplay';
import type { QueryResponse } from '../types/api';

// Mock data
const mockIncentiveResponse: QueryResponse = {
  query_type: "INCENTIVE",
  query: "digital innovation funding",
  result_count: 1,
  processing_time: 0.45,
  confidence: "high",
  results: [
    {
      incentive_id: "INC001",
      title: "Digital Innovation Fund",
      description: "Support for digital transformation projects",
      ai_description: "This incentive provides funding for companies investing in digital technologies, including AI, cloud computing, and automation solutions.",
      eligibility_criteria: "Companies with digital transformation projects",
      sector: "Technology",
      geo_requirement: "Portugal",
      eligible_actions: "Software development, Cloud infrastructure, AI implementation",
      funding_rate: "50% non-refundable",
      investment_eur: "€10,000 - €500,000",
      start_date: "2024-01-01",
      end_date: "2024-12-31",
      total_budget: 5000000,
      source_link: "https://example.com/incentive",
      matched_companies: [
        {
          id: 1,
          name: "TechCorp Solutions",
          cae_classification: "62010 - Computer programming activities",
          activities: "Software development and IT consulting services",
          website: "https://techcorp.example.com",
          location_address: "Lisbon, Portugal",
          rank: 1,
          company_score: 0.92,
          semantic_score: 0.88,
          score_components: {}
        },
        {
          id: 2,
          name: "InnoSoft Ltd",
          cae_classification: "62020 - Computer consultancy activities",
          activities: "Cloud computing and digital transformation consulting",
          website: "https://innosoft.example.com",
          location_address: "Porto, Portugal",
          rank: 2,
          company_score: 0.87,
          semantic_score: 0.85,
          score_components: {}
        },
        {
          id: 3,
          name: "DataFlow Systems",
          cae_classification: "62030 - Computer facilities management",
          activities: "Data analytics and business intelligence solutions",
          website: "https://dataflow.example.com",
          location_address: "Braga, Portugal",
          rank: 3,
          company_score: 0.81,
          semantic_score: 0.79,
          score_components: {}
        }
      ]
    }
  ]
};

const mockCompanyResponse: QueryResponse = {
  query_type: "COMPANY",
  query: "TechCorp Solutions",
  result_count: 1,
  processing_time: 0.32,
  confidence: "high",
  results: [
    {
      company_id: 1,
      company_name: "TechCorp Solutions",
      cae_classification: "62010 - Computer programming activities",
      activities: "Software development, IT consulting, and digital transformation services for enterprise clients",
      website: "https://techcorp.example.com",
      location_address: "Lisbon, Portugal",
      location_lat: 38.7223,
      location_lon: -9.1393,
      eligible_incentives: [
        {
          incentive_id: "INC001",
          title: "Digital Innovation Fund",
          description: "Support for digital transformation",
          ai_description: "Funding for companies investing in digital technologies",
          sector: "Technology",
          geo_requirement: "Portugal",
          eligible_actions: "Software development, Cloud infrastructure",
          funding_rate: "50% non-refundable",
          start_date: "2024-01-01",
          end_date: "2024-12-31",
          source_link: "https://example.com/incentive1",
          rank: 1,
          company_score: 0.92
        },
        {
          incentive_id: "INC045",
          title: "Green Energy Transition",
          description: "Support for sustainable energy projects",
          ai_description: "Funding for companies adopting renewable energy solutions",
          sector: "Energy",
          geo_requirement: "EU",
          eligible_actions: "Solar panels, Energy efficiency",
          funding_rate: "40% non-refundable",
          start_date: "2024-01-01",
          end_date: "2025-12-31",
          source_link: "https://example.com/incentive2",
          rank: 2,
          company_score: 0.87
        }
      ]
    }
  ]
};

const mockEmptyResponse: QueryResponse = {
  query_type: "INCENTIVE",
  query: "nonexistent incentive xyz123",
  result_count: 0,
  processing_time: 0.15,
  confidence: null,
  results: []
};

export const ResultsDisplayDemo: React.FC = () => {
  const [currentState, setCurrentState] = useState<string>('loading');

  const getStateProps = () => {
    switch (currentState) {
      case 'loading':
        return {
          response: null,
          isLoading: true,
          error: null
        };
      
      case 'incentive':
        return {
          response: mockIncentiveResponse,
          isLoading: false,
          error: null
        };
      
      case 'company':
        return {
          response: mockCompanyResponse,
          isLoading: false,
          error: null
        };
      
      case 'empty':
        return {
          response: mockEmptyResponse,
          isLoading: false,
          error: null
        };
      
      case 'error-network':
        return {
          response: null,
          isLoading: false,
          error: 'Network error: Failed to fetch. Service unavailable.'
        };
      
      case 'error-timeout':
        return {
          response: null,
          isLoading: false,
          error: 'Request timeout: The request took too long to complete.'
        };
      
      case 'error-generic':
        return {
          response: null,
          isLoading: false,
          error: 'An unexpected error occurred while processing your request.'
        };
      
      default:
        return {
          response: null,
          isLoading: false,
          error: null
        };
    }
  };

  const handleCompanyClick = (companyId: number) => {
    console.log('Company clicked:', companyId);
    alert(`Navigate to company detail: ${companyId}`);
  };

  const handleIncentiveClick = (incentiveId: string) => {
    console.log('Incentive clicked:', incentiveId);
    alert(`Navigate to incentive detail: ${incentiveId}`);
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">
          ResultsDisplay Component Demo
        </h1>

        {/* State Selector */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Select State to Preview:
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
            <button
              onClick={() => setCurrentState('loading')}
              className={`px-4 py-2 rounded font-medium transition-colors ${
                currentState === 'loading'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Loading
            </button>
            <button
              onClick={() => setCurrentState('incentive')}
              className={`px-4 py-2 rounded font-medium transition-colors ${
                currentState === 'incentive'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Incentive Results
            </button>
            <button
              onClick={() => setCurrentState('company')}
              className={`px-4 py-2 rounded font-medium transition-colors ${
                currentState === 'company'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Company Results
            </button>
            <button
              onClick={() => setCurrentState('empty')}
              className={`px-4 py-2 rounded font-medium transition-colors ${
                currentState === 'empty'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Empty State
            </button>
            <button
              onClick={() => setCurrentState('error-network')}
              className={`px-4 py-2 rounded font-medium transition-colors ${
                currentState === 'error-network'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Network Error
            </button>
            <button
              onClick={() => setCurrentState('error-timeout')}
              className={`px-4 py-2 rounded font-medium transition-colors ${
                currentState === 'error-timeout'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Timeout Error
            </button>
            <button
              onClick={() => setCurrentState('error-generic')}
              className={`px-4 py-2 rounded font-medium transition-colors ${
                currentState === 'error-generic'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Generic Error
            </button>
          </div>
        </div>

        {/* Current State Display */}
        <div className="bg-gray-50 rounded-lg p-4 mb-6">
          <p className="text-sm text-gray-600">
            <span className="font-semibold">Current State:</span>{' '}
            <span className="font-mono text-blue-600">{currentState}</span>
          </p>
        </div>

        {/* Component Preview */}
        <ResultsDisplay
          {...getStateProps()}
          onCompanyClick={handleCompanyClick}
          onIncentiveClick={handleIncentiveClick}
        />
      </div>
    </div>
  );
};

export default ResultsDisplayDemo;
