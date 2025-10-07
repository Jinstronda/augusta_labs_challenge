/**
 * IncentiveDetailPage Component
 * 
 * Detail view for a specific incentive showing its information and top matching companies.
 * Fetches incentive data by ID from the backend API.
 * 
 * Route: /incentive/:id
 * Requirements: 2.5, 4.6
 */

import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { IncentiveCard } from '../components/IncentiveCard';
import { getIncentiveDetail, ApiError } from '../services/api';
import type { IncentiveResult } from '../types/api';

export const IncentiveDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [incentive, setIncentive] = useState<IncentiveResult | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchIncentive = async () => {
      if (!id) {
        setError('No incentive ID provided');
        setIsLoading(false);
        return;
      }

      setIsLoading(true);
      setError(null);

      try {
        const data = await getIncentiveDetail(id);
        setIncentive(data);
      } catch (err) {
        if (err instanceof ApiError) {
          if (err.statusCode === 404) {
            setError(`Incentive "${id}" not found`);
          } else {
            setError(err.message);
          }
        } else {
          setError('An unexpected error occurred');
        }
      } finally {
        setIsLoading(false);
      }
    };

    fetchIncentive();
  }, [id]);

  const handleCompanyClick = (companyId: number) => {
    navigate(`/company/${companyId}`);
  };

  const handleBackClick = () => {
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-white dark:bg-[#0A0A0A]">
      {/* Minimal Header */}
      <header className="border-b border-gray-100 dark:border-gray-800 px-4 py-3 flex items-center justify-between backdrop-blur-sm bg-white/80 dark:bg-[#0A0A0A]/80 sticky top-0 z-50">
        <div className="flex items-center gap-4">
          {/* Back button */}
          <button
            onClick={handleBackClick}
            className="flex items-center gap-2 px-3 py-1.5 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-50 dark:hover:bg-gray-800 rounded-lg transition-all duration-200"
            aria-label="Back to home"
          >
            <svg
              className="w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 19l-7-7 7-7"
              />
            </svg>
            Back
          </button>

          {/* Logo */}
          <Link to="/" className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-emerald-400 to-cyan-500 flex items-center justify-center shadow-lg shadow-emerald-500/20">
              <svg
                className="w-4 h-4 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2.5}
                  d="M13 10V3L4 14h7v7l9-11h-7z"
                />
              </svg>
            </div>
            <h1 className="text-lg font-semibold text-gray-900 dark:text-white tracking-tight">
              Incentive AI
            </h1>
          </Link>
        </div>

        {/* New Chat button */}
        <Link
          to="/"
          className="flex items-center gap-2 px-3 py-1.5 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-50 dark:hover:bg-gray-800 rounded-lg transition-all duration-200"
        >
          <svg
            className="w-4 h-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 4v16m8-8H4"
            />
          </svg>
          New
        </Link>
      </header>

      {/* Main content */}
      <main className="max-w-5xl mx-auto px-4 py-8">
        {isLoading && (
          <div className="flex flex-col items-center justify-center py-20">
            <div className="w-12 h-12 border-3 border-emerald-500 border-t-transparent rounded-full animate-spin mb-4"></div>
            <p className="text-gray-500 dark:text-gray-400 text-sm">Loading...</p>
          </div>
        )}

        {error && (
          <div className="bg-red-50 dark:bg-red-900/10 border border-red-100 dark:border-red-900/30 rounded-2xl p-6">
            <div className="flex items-start gap-3">
              <svg
                className="w-6 h-6 text-red-500 mt-0.5 flex-shrink-0"
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
              <div>
                <h3 className="text-lg font-semibold text-red-900 dark:text-red-300 mb-1">
                  Error Loading Incentive
                </h3>
                <p className="text-red-700 dark:text-red-400 mb-4">{error}</p>
                <button
                  onClick={handleBackClick}
                  className="px-4 py-2 bg-gradient-to-r from-emerald-500 to-cyan-500 hover:from-emerald-600 hover:to-cyan-600 text-white rounded-lg transition-all text-sm font-medium shadow-lg"
                >
                  Return to Home
                </button>
              </div>
            </div>
          </div>
        )}

        {!isLoading && !error && incentive && (
          <IncentiveCard
            incentive={incentive}
            onCompanyClick={handleCompanyClick}
          />
        )}
      </main>
    </div>
  );
};

export default IncentiveDetailPage;
