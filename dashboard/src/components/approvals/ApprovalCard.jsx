# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file creates a card that shows something that needs the client's approval,
# like a new ad design or a request to spend more money on advertising.

# High School Explanation:
# This component renders a card for approval requests that require client action.
# It displays approval details, deadline information, and action buttons for
# approving or rejecting requests, with different visual styles based on approval type.

import { Link } from 'react-router-dom';
import { 
  RiFileTextLine, 
  RiMoneyDollarCircleLine, 
  RiImageLine,
  RiCalendarEventLine,
  RiTargetLine 
} from 'react-icons/ri';

// Calculate time remaining until deadline
const getTimeRemaining = (deadline) => {
  const now = new Date();
  const deadlineDate = new Date(deadline);
  const diffMs = deadlineDate - now;
  
  // If deadline has passed
  if (diffMs <= 0) {
    return { text: 'Overdue', urgent: true };
  }
  
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  
  // Less than 24 hours
  if (diffHours < 24) {
    return { 
      text: diffHours === 0 ? 'Due today' : `${diffHours}h remaining`, 
      urgent: diffHours < 12
    };
  }
  
  // Days remaining
  const diffDays = Math.floor(diffHours / 24);
  return { 
    text: `${diffDays}d remaining`, 
    urgent: false
  };
};

// Format date for display
const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleDateString(undefined, { 
    month: 'short', 
    day: 'numeric' 
  });
};

const ApprovalCard = ({ approval }) => {
  const timeRemaining = getTimeRemaining(approval.deadline);
  
  // Type-specific settings
  const typeConfig = {
    creative: {
      icon: RiImageLine,
      color: 'text-blue-500 bg-blue-100 dark:bg-blue-900 dark:text-blue-200',
      borderColor: 'border-blue-200 dark:border-blue-800'
    },
    budget: {
      icon: RiMoneyDollarCircleLine,
      color: 'text-green-500 bg-green-100 dark:bg-green-900 dark:text-green-200',
      borderColor: 'border-green-200 dark:border-green-800'
    },
    target: {
      icon: RiTargetLine,
      color: 'text-purple-500 bg-purple-100 dark:bg-purple-900 dark:text-purple-200',
      borderColor: 'border-purple-200 dark:border-purple-800'
    },
    schedule: {
      icon: RiCalendarEventLine,
      color: 'text-amber-500 bg-amber-100 dark:bg-amber-900 dark:text-amber-200',
      borderColor: 'border-amber-200 dark:border-amber-800'
    },
    document: {
      icon: RiFileTextLine,
      color: 'text-gray-500 bg-gray-100 dark:bg-gray-700 dark:text-gray-300',
      borderColor: 'border-gray-200 dark:border-gray-700'
    }
  };
  
  const config = typeConfig[approval.type] || typeConfig.document;
  const IconComponent = config.icon;
  
  // Deadline styling
  const deadlineClass = timeRemaining.urgent 
    ? 'text-red-600 dark:text-red-400 font-medium' 
    : 'text-gray-500 dark:text-gray-400';
  
  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg shadow border ${config.borderColor} overflow-hidden`}>
      <div className="p-4">
        <div className="flex items-start">
          {/* Icon */}
          <div className={`flex-shrink-0 p-2 rounded-full ${config.color} mr-3`}>
            <IconComponent className="w-5 h-5" />
          </div>
          
          {/* Content */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between">
              <h4 className="text-sm font-medium text-gray-900 dark:text-white truncate">
                {approval.title}
              </h4>
              <span className={`inline-flex items-center text-xs ${deadlineClass}`}>
                {timeRemaining.text}
              </span>
            </div>
            
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Campaign: <Link to={`/campaigns/${approval.campaignId}`} className="text-primary hover:text-primary-dark">
                {approval.campaign}
              </Link>
            </p>
            
            <div className="mt-2 flex items-center text-xs text-gray-500 dark:text-gray-400">
              <span>Created {formatDate(approval.createdAt)} • Due {formatDate(approval.deadline)}</span>
            </div>
          </div>
        </div>
      </div>
      
      {/* Actions footer */}
      <div className="px-4 py-3 bg-gray-50 dark:bg-gray-700 border-t border-gray-200 dark:border-gray-600 flex justify-end space-x-2">
        <Link
          to={`/approvals/${approval.id}`}
          className="inline-flex items-center px-3 py-1.5 border border-gray-300 dark:border-gray-600 shadow-sm text-xs font-medium rounded text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
        >
          View Details
        </Link>
        <button
          className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded shadow-sm text-white bg-primary hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
        >
          Approve
        </button>
      </div>
    </div>
  );
};

export default ApprovalCard;