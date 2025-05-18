# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file creates the main dashboard page that shows a summary of all your
# advertising campaigns, including how they're performing and what needs attention.

# High School Explanation:
# This component implements the main dashboard overview page with key performance
# metrics, campaign status summaries, and activity feeds. It shows aggregated data
# from multiple campaigns and highlights items requiring client attention or approval.

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

// Components
import CampaignCard from '../components/campaigns/CampaignCard';
import MetricCard from '../components/analytics/MetricCard';
import ActivityFeed from '../components/shared/ActivityFeed';
import ApprovalCard from '../components/approvals/ApprovalCard';

const API_URL = import.meta.env.VITE_API_URL || '/api';

const DashboardPage = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState({
    campaigns: [],
    metrics: {},
    activities: [],
    pendingApprovals: []
  });
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        const token = localStorage.getItem('auth_token');
        
        if (!token) {
          throw new Error('No authentication token found');
        }
        
        const response = await axios.get(`${API_URL}/dashboard/overview`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        
        setDashboardData(response.data);
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError('Failed to load dashboard data. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchDashboardData();
  }, []);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="w-10 h-10 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="mt-3 text-gray-600 dark:text-gray-400">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="text-red-500 text-xl mb-2">⚠️</div>
          <p className="text-gray-800 dark:text-gray-200 mb-2">{error}</p>
          <button 
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-primary text-white rounded-md hover:bg-primary-dark"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  // For development/demo purposes
  const demoData = {
    campaigns: [
      { id: 1, name: 'Summer Collection Launch', status: 'active', progress: 75, budget: 25000, spent: 18750, impressions: 1200000, clicks: 48000, conversions: 960 },
      { id: 2, name: 'Holiday Season Promotions', status: 'planning', progress: 30, budget: 40000, spent: 0, impressions: 0, clicks: 0, conversions: 0 },
      { id: 3, name: 'Brand Awareness Campaign', status: 'active', progress: 50, budget: 15000, spent: 7500, impressions: 600000, clicks: 12000, conversions: 0 }
    ],
    metrics: {
      totalBudget: 80000,
      totalSpent: 26250,
      totalImpressions: 1800000,
      totalClicks: 60000,
      totalConversions: 960,
      avgCPC: 0.44,
      avgCTR: 3.33,
      avgCVR: 1.6
    },
    activities: [
      { id: 1, type: 'approval_request', title: 'Creative Approval', campaign: 'Summer Collection Launch', timestamp: '2025-05-17T14:30:00Z', status: 'pending' },
      { id: 2, type: 'campaign_status', title: 'Campaign Launched', campaign: 'Summer Collection Launch', timestamp: '2025-05-15T09:00:00Z', status: 'completed' },
      { id: 3, type: 'analytics', title: 'Performance Alert', campaign: 'Brand Awareness Campaign', timestamp: '2025-05-16T16:45:00Z', status: 'alert' }
    ],
    pendingApprovals: [
      { id: 1, title: 'Ad Creative Review', campaign: 'Summer Collection Launch', type: 'creative', createdAt: '2025-05-17T11:20:00Z', deadline: '2025-05-19T11:20:00Z' },
      { id: 2, title: 'Budget Increase Request', campaign: 'Brand Awareness Campaign', type: 'budget', createdAt: '2025-05-16T15:30:00Z', deadline: '2025-05-18T15:30:00Z' }
    ]
  };

  // Use dashboardData or fallback to demoData
  const { campaigns, metrics, activities, pendingApprovals } = dashboardData.campaigns?.length ? dashboardData : demoData;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Dashboard</h2>
        <Link
          to="/campaigns/new"
          className="inline-flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
        >
          New Campaign
        </Link>
      </div>
      
      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard title="Total Budget" value={`$${metrics.totalBudget.toLocaleString()}`} />
        <MetricCard title="Total Spent" value={`$${metrics.totalSpent.toLocaleString()}`} percentage={metrics.totalSpent / metrics.totalBudget * 100} />
        <MetricCard title="Total Impressions" value={metrics.totalImpressions.toLocaleString()} />
        <MetricCard title="Conversions" value={metrics.totalConversions.toLocaleString()} />
      </div>
      
      {/* Active Campaigns */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">Active Campaigns</h3>
          <Link to="/campaigns" className="text-sm font-medium text-primary hover:text-primary-dark">
            View all campaigns
          </Link>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {campaigns.filter(c => c.status === 'active').map(campaign => (
            <CampaignCard key={campaign.id} campaign={campaign} />
          ))}
          
          {campaigns.filter(c => c.status === 'active').length === 0 && (
            <div className="col-span-full p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 text-center">
              <p className="text-gray-600 dark:text-gray-400">No active campaigns</p>
            </div>
          )}
        </div>
      </div>
      
      {/* Pending Approvals & Activity Feed in 2 columns */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pending Approvals */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">Pending Approvals</h3>
            <Link to="/approvals" className="text-sm font-medium text-primary hover:text-primary-dark">
              View all
            </Link>
          </div>
          
          <div className="space-y-4">
            {pendingApprovals.map(approval => (
              <ApprovalCard key={approval.id} approval={approval} />
            ))}
            
            {pendingApprovals.length === 0 && (
              <div className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 text-center">
                <p className="text-gray-600 dark:text-gray-400">No pending approvals</p>
              </div>
            )}
          </div>
        </div>
        
        {/* Activity Feed */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">Recent Activity</h3>
          </div>
          
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
            <ActivityFeed activities={activities} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;