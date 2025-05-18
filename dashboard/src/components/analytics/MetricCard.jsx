# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file creates a card that shows one important number about how well
# advertising campaigns are doing, like how many people saw the ads.

# High School Explanation:
# This component displays a single metric in a card format with optional 
# percentage indicator and trend visualization. It's designed to highlight 
# key performance indicators in the dashboard with visual indicators for
# quick performance assessment.

import { RiArrowUpSLine, RiArrowDownSLine } from 'react-icons/ri';

const MetricCard = ({ title, value, percentage = null, trend = null, previousValue = null }) => {
  // Determine if trend is positive (true), negative (false), or neutral (null)
  const trendDirection = trend !== null 
    ? trend 
    : previousValue !== null 
      ? parseFloat(value) > previousValue 
      : null;
  
  // Colors for positive/negative trends
  const trendColors = {
    positive: 'text-green-500',
    negative: 'text-red-500',
    neutral: 'text-gray-500 dark:text-gray-400'
  };
  
  const trendColor = trendDirection === true 
    ? trendColors.positive 
    : trendDirection === false 
      ? trendColors.negative 
      : trendColors.neutral;
      
  // Format percentage if needed
  const formattedPercentage = percentage !== null 
    ? typeof percentage === 'number' 
      ? percentage.toFixed(1) + '%' 
      : percentage 
    : null;

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-5 border border-gray-200 dark:border-gray-700">
      <div className="flex justify-between">
        <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
          {title}
        </h3>
        {trendDirection !== null && (
          <div className={`flex items-center ${trendColor}`}>
            {trendDirection ? (
              <RiArrowUpSLine className="w-4 h-4" />
            ) : (
              <RiArrowDownSLine className="w-4 h-4" />
            )}
          </div>
        )}
      </div>
      
      <div className="mt-2 flex items-baseline">
        <p className="text-2xl font-semibold text-gray-900 dark:text-white">
          {value}
        </p>
        {formattedPercentage && (
          <p className="ml-2 text-sm font-medium text-gray-500 dark:text-gray-400">
            {formattedPercentage}
          </p>
        )}
      </div>
      
      {percentage !== null && (
        <div className="mt-3">
          <div className="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
            <div 
              className="h-full bg-primary" 
              style={{ width: `${Math.min(100, Math.max(0, percentage))}%` }}
            ></div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MetricCard;