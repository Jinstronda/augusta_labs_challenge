/**
 * App Component
 * 
 * Main application component with routing setup.
 * 
 * Routes:
 * - / : Home page with ChatInterface
 * - /incentive/:id : Incentive detail page
 * - /company/:id : Company detail page
 * 
 * Requirements: 4.1, 4.6, 4.8, 2.5, 3.5
 */

import React from 'react';
import { BrowserRouter, Routes, Route, useNavigate, Navigate } from 'react-router-dom';
import { ChatInterface } from './components/ChatInterface';
import { IncentiveDetailPage } from './pages/IncentiveDetailPage';
import { CompanyDetailPage } from './pages/CompanyDetailPage';

/**
 * Home page component with ChatInterface
 */
const HomePage: React.FC = () => {
  const navigate = useNavigate();

  const handleCompanyClick = (companyId: number) => {
    navigate(`/company/${companyId}`);
  };

  const handleIncentiveClick = (incentiveId: string) => {
    navigate(`/incentive/${incentiveId}`);
  };

  return (
    <ChatInterface
      onCompanyClick={handleCompanyClick}
      onIncentiveClick={handleIncentiveClick}
    />
  );
};

/**
 * 404 Not Found page
 */
const NotFoundPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center px-6">
      <div className="text-center max-w-md">
        <div className="w-20 h-20 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center mx-auto mb-6">
          <svg
            className="w-12 h-12 text-white"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </div>
        <h1 className="text-6xl font-bold text-gray-900 dark:text-white mb-4">404</h1>
        <h2 className="text-2xl font-semibold text-gray-800 dark:text-gray-200 mb-3">
          Page Not Found
        </h2>
        <p className="text-gray-600 dark:text-gray-400 mb-8">
          The page you're looking for doesn't exist or has been moved.
        </p>
        <button
          onClick={() => navigate('/')}
          className="px-6 py-3 bg-gradient-to-br from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600 text-white rounded-lg transition-all duration-200 font-medium shadow-lg hover:shadow-xl"
        >
          Return to Home
        </button>
      </div>
    </div>
  );
};

/**
 * Main App component with routing
 */
function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Home page with chat interface */}
        <Route path="/" element={<HomePage />} />
        
        {/* Incentive detail page */}
        <Route path="/incentive/:id" element={<IncentiveDetailPage />} />
        
        {/* Company detail page */}
        <Route path="/company/:id" element={<CompanyDetailPage />} />
        
        {/* 404 Not Found */}
        <Route path="/404" element={<NotFoundPage />} />
        
        {/* Catch all - redirect to 404 */}
        <Route path="*" element={<Navigate to="/404" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
