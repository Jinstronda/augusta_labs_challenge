/**
 * IncentiveCard Demo
 * 
 * Demonstrates the IncentiveCard component with sample data
 * matching the backend API structure.
 * 
 * To run this demo:
 * 1. Import this component in your App.tsx
 * 2. Render <IncentiveCardDemo />
 */

import React from 'react';
import { IncentiveCard } from './IncentiveCard';
import type { IncentiveResult } from '../types/api';

// Sample data matching backend structure
const sampleIncentive: IncentiveResult = {
  incentive_id: "INC001",
  title: "Digital Innovation Fund",
  description: null,
  ai_description: "Support for companies investing in digital transformation, including AI, cloud computing, and automation technologies. Funding covers up to 50% of eligible costs.",
  eligibility_criteria: null,
  sector: "Technology, Digital Services",
  geo_requirement: "Portugal Continental",
  eligible_actions: "Software development, Cloud infrastructure, AI implementation, Digital training",
  funding_rate: "50% of eligible costs",
  investment_eur: "€10,000 - €500,000",
  start_date: "2024-01-01",
  end_date: "2025-12-31",
  total_budget: 5000000,
  source_link: "https://example.com/incentive/001",
  matched_companies: [
    {
      id: 12345,
      name: "TechCorp Solutions S.A.",
      cae_classification: "62010 - Computer programming activities",
      activities: "Development of custom software solutions, cloud infrastructure management, and AI consulting services for enterprise clients.",
      website: "https://techcorp.example.com",
      location_address: "Avenida da Liberdade, 123, 1250-096 Lisboa, Portugal",
      rank: 1,
      company_score: 0.92,
      semantic_score: 0.88,
      score_components: {
        s: 0.88,
        m: 0.75,
        g: 1.0,
        o_prime: 1.0,
        w: 1.0
      }
    },
    {
      id: 12346,
      name: "InnoSoft Lda.",
      cae_classification: "62020 - Computer consultancy activities",
      activities: "IT consulting, digital transformation projects, and software integration services.",
      website: "https://innosoft.example.com",
      location_address: "Rua do Comércio, 45, 4000-123 Porto, Portugal",
      rank: 2,
      company_score: 0.87,
      semantic_score: 0.85,
      score_components: {
        s: 0.85,
        m: 0.70,
        g: 1.0,
        o_prime: 0.70,
        w: 1.0
      }
    },
    {
      id: 12347,
      name: "DataFlow Technologies",
      cae_classification: "62030 - Computer facilities management activities",
      activities: "Data center management, cloud services, and IT infrastructure solutions.",
      website: null,
      location_address: "Parque Industrial, Lote 7, 3000-456 Coimbra, Portugal",
      rank: 3,
      company_score: 0.78,
      semantic_score: 0.82,
      score_components: {
        s: 0.82,
        m: 0.65,
        g: 1.0,
        o_prime: 0.70,
        w: 0.0
      }
    },
    {
      id: 12348,
      name: "SmartCode Unipessoal",
      cae_classification: "62010 - Computer programming activities",
      activities: "Mobile app development and web application design for small businesses.",
      website: "https://smartcode.example.com",
      location_address: "Rua das Flores, 89, 4700-123 Braga, Portugal",
      rank: 4,
      company_score: 0.65,
      semantic_score: 0.75,
      score_components: {
        s: 0.75,
        m: 0.60,
        g: 1.0,
        o_prime: 0.40,
        w: 1.0
      }
    },
    {
      id: 12349,
      name: "CloudNet Services",
      cae_classification: "62020 - Computer consultancy activities",
      activities: "Cloud migration services and IT infrastructure consulting.",
      website: "https://cloudnet.example.com",
      location_address: "Avenida Central, 234, 2700-123 Amadora, Portugal",
      rank: 5,
      company_score: 0.58,
      semantic_score: 0.70,
      score_components: {
        s: 0.70,
        m: 0.55,
        g: 1.0,
        o_prime: 0.70,
        w: 1.0
      }
    }
  ]
};

export const IncentiveCardDemo: React.FC = () => {
  const handleCompanyClick = (companyId: number) => {
    console.log('Company clicked:', companyId);
    alert(`Navigating to company detail page for company ID: ${companyId}`);
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            IncentiveCard Component Demo
          </h1>
          <p className="text-gray-600">
            Click on any company card to test the navigation handler
          </p>
        </div>

        <IncentiveCard 
          incentive={sampleIncentive} 
          onCompanyClick={handleCompanyClick}
        />

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4">Component Features</h2>
          <ul className="space-y-2 text-sm text-gray-700">
            <li>✅ Displays incentive metadata (title, sector, geo, actions, funding)</li>
            <li>✅ Shows AI-generated description</li>
            <li>✅ Renders top 5 companies with rank badges (gold, silver, bronze)</li>
            <li>✅ Color-coded score badges (green=excellent, blue=strong, yellow=moderate)</li>
            <li>✅ Progress bars showing company match scores</li>
            <li>✅ Clickable company cards with hover effects</li>
            <li>✅ Company location and website links</li>
            <li>✅ Activities preview with line clamping</li>
            <li>✅ Scoring formula explanation</li>
            <li>✅ Responsive design (mobile, tablet, desktop)</li>
          </ul>
        </div>
      </div>
    </div>
  );
};
