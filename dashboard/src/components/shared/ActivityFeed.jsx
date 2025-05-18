# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file creates a list that shows all the recent things that happened with
# your ad campaigns, like when a new ad was created or when someone approved
# something.

# High School Explanation:
# This component displays a chronological feed of activities related to campaigns,
# approvals, and system events. It formats timestamps, categorizes activities by
# type, and provides visual indicators for different event statuses.

import { Link } from 'react-router-dom';
import { 
  RiCheckboxCircleLine, 
  RiTimeLine, 
  RiAlertLine,
  RiFileTextLine, 
  RiLineChartLine,
  RiNotification3Line,
  RiChat3Line,
  RiRocketLine
} from 'react-icons/ri';

// Format a timestamp for display
const formatTimestamp = (timestamp) => {
  const date = new Date(timestamp);
  const now = new Date();
  const diffMs = now - date;
  const diffSecs = Math.floor(diffMs / 1000);
  const diffMins = Math.floor(diffSecs / 60);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffSecs < 60) {
    return 'just now';
  } else if (diffMins < 60) {
    return `${diffMins}m ago`;
  } else if (diffHours < 24) {
    return `${diffHours}h ago`;
  } else if (diffDays < 7) {
    return `${diffDays}d ago`;
  } else {
    return date.toLocaleDateString();
  }
};

// Icon and color mappings for activity types
const activityConfig = {
  approval_request: {
    icon: RiFileTextLine,
    color: 'text-blue-500 bg-blue-100 dark:bg-blue-900',
    title: (activity) => `New ${activity.title}`
  },
  approval_complete: {
    icon: RiCheckboxCircleLine,
    color: 'text-green-500 bg-green-100 dark:bg-green-900',
    title: (activity) => `${activity.title} Approved`
  },
  campaign_status: {
    icon: RiRocketLine,
    color: 'text-purple-500 bg-purple-100 dark:bg-purple-900',
    title: (activity) => activity.title
  },
  analytics: {
    icon: RiLineChartLine,
    color: 'text-yellow-500 bg-yellow-100 dark:bg-yellow-900',
    title: (activity) => activity.title
  },
  client_feedback: {
    icon: RiChat3Line,
    color: 'text-indigo-500 bg-indigo-100 dark:bg-indigo-900',
    title: (activity) => `Client Feedback: ${activity.title}`
  },
  notification: {
    icon: RiNotification3Line,
    color: 'text-gray-500 bg-gray-100 dark:bg-gray-700',
    title: (activity) => activity.title
  }
};

// Status indicator component
const StatusIndicator = ({ status }) => {
  const statusConfig = {
    pending: {
      icon: RiTimeLine,
      color: 'text-yellow-500'
    },
    completed: {
      icon: RiCheckboxCircleLine,
      color: 'text-green-500'
    },
    alert: {
      icon: RiAlertLine,
      color: 'text-red-500'
    }
  };

  const config = statusConfig[status] || statusConfig.pending;
  const IconComponent = config.icon;

  return (
    <span className={`inline-flex ${config.color}`}>
      <IconComponent className="w-4 h-4" />
    </span>
  );
};

const ActivityFeed = ({ activities }) => {
  if (!activities || activities.length === 0) {
    return (
      <div className="p-4 text-center text-gray-500 dark:text-gray-400">
        No recent activity
      </div>
    );
  }

  return (
    <div className="flow-root">
      <ul className="divide-y divide-gray-200 dark:divide-gray-700">
        {activities.map((activity) => {
          const config = activityConfig[activity.type] || activityConfig.notification;
          const IconComponent = config.icon;
          
          return (
            <li key={activity.id} className="py-4 px-4">
              <div className="flex items-start space-x-3">
                <div className={`flex-shrink-0 p-1.5 rounded-full ${config.color}`}>
                  <IconComponent className="w-5 h-5" />
                </div>
                <div className="min-w-0 flex-1">
                  <div className="text-sm font-medium text-gray-900 dark:text-white">
                    {config.title(activity)}
                    <StatusIndicator status={activity.status} />
                  </div>
                  <div className="mt-0.5 text-sm text-gray-500 dark:text-gray-400">
                    Campaign: <Link to={`/campaigns/${activity.campaignId}`} className="text-primary hover:text-primary-dark">
                      {activity.campaign}
                    </Link>
                  </div>
                  <time className="mt-0.5 text-xs text-gray-500 dark:text-gray-400">
                    {formatTimestamp(activity.timestamp)}
                  </time>
                </div>
                <div className="flex-shrink-0 self-center">
                  <button className="p-1 rounded-full text-gray-400 hover:text-gray-500 dark:hover:text-gray-300">
                    <span className="sr-only">View details</span>
                    <svg className="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                    </svg>
                  </button>
                </div>
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
};

export default ActivityFeed;