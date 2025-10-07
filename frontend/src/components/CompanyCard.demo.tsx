/**
 * CompanyCard Demo
 * 
 * Example usage of the CompanyCard component with sample data.
 * This demonstrates how to use the component in your application.
 * 
 * To run this demo:
 * 1. Import this component in your App.tsx
 * 2. Render it: <CompanyCardDemo />
 */

import React from 'react';
import { CompanyCard } from './CompanyCard';
import type { CompanyResult } from '../types/api';

export const CompanyCardDemo: React.FC = () => {
  // Sample company data matching the backend API structure
  const sampleCompany: CompanyResult = {
    company_id: 12345,
    company_name: "TechInnovate Solutions, Lda",
    cae_classification: "62010 - Atividades de programação informática",
    activities: "Desenvolvimento de software empresarial, consultoria em transformação digital, implementação de soluções cloud, desenvolvimento de aplicações móveis e web, serviços de integração de sistemas, e formação em tecnologias de informação. A empresa especializa-se em soluções para PMEs nos setores de comércio, indústria e serviços.",
    website: "https://www.techinnovate.pt",
    location_address: "Avenida da Liberdade, 123, 1250-140 Lisboa, Portugal",
    location_lat: 38.7223,
    location_lon: -9.1393,
    eligible_incentives: [
      {
        incentive_id: "INC001",
        title: "Programa de Apoio à Digitalização de PME",
        description: "Apoio financeiro para projetos de transformação digital",
        ai_description: "Este incentivo visa apoiar pequenas e médias empresas na sua transformação digital, financiando projetos de implementação de novas tecnologias, desenvolvimento de plataformas digitais, e modernização de processos empresariais.",
        sector: "Tecnologia e Inovação",
        geo_requirement: "Portugal Continental",
        eligible_actions: "Desenvolvimento de software, implementação de sistemas ERP/CRM, criação de plataformas e-commerce",
        funding_rate: "50% a 75% das despesas elegíveis",
        start_date: "2024-01-01",
        end_date: "2025-12-31",
        source_link: "https://www.iapmei.pt/digitalizacao",
        rank: 1,
        company_score: 0.92
      },
      {
        incentive_id: "INC045",
        title: "Incentivo à Inovação Tecnológica",
        description: "Financiamento para projetos de I&D em tecnologia",
        ai_description: "Programa de apoio a projetos de investigação e desenvolvimento tecnológico, com foco em inovação de produto, processo e serviço.",
        sector: "Investigação e Desenvolvimento",
        geo_requirement: "Todo o território nacional",
        eligible_actions: "Investigação aplicada, desenvolvimento experimental, prototipagem",
        funding_rate: "60% a 80% das despesas elegíveis",
        start_date: "2024-03-01",
        end_date: "2026-02-28",
        source_link: "https://www.ani.pt/inovacao",
        rank: 2,
        company_score: 0.87
      },
      {
        incentive_id: "INC023",
        title: "Apoio à Internacionalização de Empresas Tech",
        description: "Suporte para expansão internacional de empresas tecnológicas",
        ai_description: "Incentivo destinado a apoiar empresas do setor tecnológico na sua expansão para mercados internacionais, incluindo participação em feiras, missões empresariais e desenvolvimento de estratégias de marketing internacional.",
        sector: "Internacionalização",
        geo_requirement: "Empresas sediadas em Portugal",
        eligible_actions: "Participação em feiras internacionais, missões empresariais, marketing internacional",
        funding_rate: "45% a 65% das despesas elegíveis",
        start_date: "2024-02-01",
        end_date: "2025-12-31",
        source_link: "https://www.aicep.pt/apoios",
        rank: 3,
        company_score: 0.85
      },
      {
        incentive_id: "INC078",
        title: "Programa de Formação em Competências Digitais",
        description: "Financiamento para formação de colaboradores em áreas digitais",
        ai_description: "Apoio à formação profissional de trabalhadores em competências digitais, incluindo programação, análise de dados, cibersegurança e gestão de projetos tecnológicos.",
        sector: "Formação Profissional",
        geo_requirement: "Portugal Continental e Regiões Autónomas",
        eligible_actions: "Formação certificada, workshops, cursos especializados",
        funding_rate: "70% a 90% das despesas elegíveis",
        start_date: "2024-01-15",
        end_date: "2025-06-30",
        source_link: "https://www.iefp.pt/formacao",
        rank: 4,
        company_score: 0.78
      },
      {
        incentive_id: "INC112",
        title: "Incentivo à Eficiência Energética em Empresas",
        description: "Apoio a projetos de eficiência energética e sustentabilidade",
        ai_description: "Programa de apoio a investimentos em eficiência energética, incluindo implementação de sistemas de gestão de energia, utilização de energias renováveis e otimização de processos produtivos.",
        sector: "Ambiente e Sustentabilidade",
        geo_requirement: "Todo o território nacional",
        eligible_actions: "Instalação de painéis solares, sistemas de gestão energética, equipamentos eficientes",
        funding_rate: "40% a 60% das despesas elegíveis",
        start_date: "2024-04-01",
        end_date: "2026-03-31",
        source_link: "https://www.fundoambiental.pt/apoios",
        rank: 5,
        company_score: 0.72
      }
    ]
  };

  const handleIncentiveClick = (incentiveId: string) => {
    console.log(`Navigating to incentive detail: ${incentiveId}`);
    // In a real app, this would navigate to the incentive detail page
    // Example: navigate(`/incentive/${incentiveId}`);
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            CompanyCard Component Demo
          </h1>
          <p className="text-gray-600">
            This demonstrates the CompanyCard component with sample data.
            Click on any incentive card to trigger the navigation handler.
          </p>
        </div>

        <CompanyCard 
          company={sampleCompany} 
          onIncentiveClick={handleIncentiveClick}
        />

        <div className="mt-8 p-4 bg-white rounded-lg shadow">
          <h2 className="text-lg font-semibold mb-2">Usage Example:</h2>
          <pre className="bg-gray-50 p-4 rounded text-sm overflow-x-auto">
{`import { CompanyCard } from './components/CompanyCard';
import { CompanyResult } from './types/api';

function MyComponent() {
  const company: CompanyResult = {
    // ... company data from API
  };

  const handleIncentiveClick = (incentiveId: string) => {
    navigate(\`/incentive/\${incentiveId}\`);
  };

  return (
    <CompanyCard 
      company={company}
      onIncentiveClick={handleIncentiveClick}
    />
  );
}`}
          </pre>
        </div>
      </div>
    </div>
  );
};
