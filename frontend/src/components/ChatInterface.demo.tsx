/**
 * ChatInterface Demo
 * 
 * Example usage of the ChatInterface component.
 * This shows how to integrate it into your application.
 */

import React from 'react';
import { ChatInterface } from './ChatInterface';

/**
 * Basic usage example
 */
export const BasicChatDemo: React.FC = () => {
  return (
    <div className="h-screen">
      <ChatInterface />
    </div>
  );
};

/**
 * With navigation handlers
 */
export const ChatWithNavigationDemo: React.FC = () => {
  const handleCompanyClick = (companyId: number) => {
    console.log('Navigate to company:', companyId);
    // In a real app, use React Router:
    // navigate(`/company/${companyId}`);
  };

  const handleIncentiveClick = (incentiveId: string) => {
    console.log('Navigate to incentive:', incentiveId);
    // In a real app, use React Router:
    // navigate(`/incentive/${incentiveId}`);
  };

  return (
    <div className="h-screen">
      <ChatInterface
        onCompanyClick={handleCompanyClick}
        onIncentiveClick={handleIncentiveClick}
      />
    </div>
  );
};

/**
 * Full-page layout example
 */
export const FullPageChatDemo: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <ChatInterface
        onCompanyClick={(id) => {
          // Navigate to company detail page
          window.location.href = `/company/${id}`;
        }}
        onIncentiveClick={(id) => {
          // Navigate to incentive detail page
          window.location.href = `/incentive/${id}`;
        }}
      />
    </div>
  );
};

export default BasicChatDemo;
