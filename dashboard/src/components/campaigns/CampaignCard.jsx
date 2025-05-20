// SPDX-License-Identifier: MIT
// Copyright (c) 2025 Vamsi Duvvuri

// Fifth Grade Explanation:
// This file creates a card that shows important information about one advertising
// campaign, like its name, how much money is spent, and how well it's doing.

// High School Explanation:
// This component renders a card displaying campaign information including name,
// status, budget metrics, and key performance indicators. It visualizes campaign
// progress and provides quick navigation to detailed campaign information.

import { Link } from 'react-router-dom';

// Status badge component
const StatusBadge = ({ status }) => {
  const statusStyles = {
    active: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    paused: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
    completed: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    planning: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
    draft: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
  };

  const style = statusStyles[status] || statusStyles.draft;

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${style}`}>
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  );
};

// Progress bar component
const ProgressBar = ({ value }) => {
  const clampedValue = Math.max(0, Math.min(100, value));
  
  let barColor = 'bg-blue-500';
  if (clampedValue > 90) {
    barColor = 'bg-red-500';
  } else if (clampedValue > 70) {
    barColor = 'bg-yellow-500';
  }

  return (
    <div className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
      <div 
        className={`h-full ${barColor}`} 
        style={{ width: `${clampedValue}%` }}
      ></div>
    </div>
  );
};

const CampaignCard = ({ campaign }) => {
  // Calculate KPIs
  const ctr = campaign.impressions ? (campaign.clicks / campaign.impressions * 100).toFixed(2) : '0.00';
  const cpc = campaign.clicks ? (campaign.spent / campaign.clicks).toFixed(2) : '0.00';
  const spentPercentage = campaign.budget ? (campaign.spent / campaign.budget * 100) : 0;
  
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 overflow-hidden">
      <div className="p-4">
        <div className="flex justify-between items-start mb-2">
          <Link to={`/campaigns/${campaign.id}`} className="text-lg font-medium text-gray-900 dark:text-white hover:text-primary">
            {campaign.name}
          </Link>
          <StatusBadge status={campaign.status} />
        </div>
        
        {/* Budget progress */}
        <div className="mt-4">
          <div className="flex justify-between items-center mb-1">
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Budget spent</span>
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
              ${campaign.spent.toLocaleString()} / ${campaign.budget.toLocaleString()}
            </span>
          </div>
          <ProgressBar value={spentPercentage} />
        </div>
        
        {/* Campaign progress */}
        <div className="mt-4">
          <div className="flex justify-between items-center mb-1">
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Campaign progress</span>
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{campaign.progress}%</span>
          </div>
          <ProgressBar value={campaign.progress} />
        </div>
        
        {/* KPIs */}
        <div className="grid grid-cols-3 gap-2 mt-4">
          <div className="text-center p-2 bg-gray-50 dark:bg-gray-700 rounded">
            <p className="text-xs text-gray-500 dark:text-gray-400">Impressions</p>
            <p className="text-sm font-semibold text-gray-900 dark:text-white">{campaign.impressions.toLocaleString()}</p>
          </div>
          <div className="text-center p-2 bg-gray-50 dark:bg-gray-700 rounded">
            <p className="text-xs text-gray-500 dark:text-gray-400">CTR</p>
            <p className="text-sm font-semibold text-gray-900 dark:text-white">{ctr}%</p>
          </div>
          <div className="text-center p-2 bg-gray-50 dark:bg-gray-700 rounded">
            <p className="text-xs text-gray-500 dark:text-gray-400">CPC</p>
            <p className="text-sm font-semibold text-gray-900 dark:text-white">${cpc}</p>
          </div>
        </div>
      </div>
      
      {/* Card footer with action button */}
      <div className="px-4 py-3 bg-gray-50 dark:bg-gray-700 border-t border-gray-200 dark:border-gray-600 text-right">
        <Link 
          to={`/campaigns/${campaign.id}`}
          className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded text-primary-foreground bg-primary hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
        >
          View Details
        </Link>
      </div>
    </div>
  );
};

export default CampaignCard;