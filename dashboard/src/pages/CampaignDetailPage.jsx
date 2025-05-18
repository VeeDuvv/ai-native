# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file creates a page that shows everything about one specific advertising
# campaign, including its performance, what ads are being shown, and how much
# money is being spent.

# High School Explanation:
# This component implements the detailed view of a single campaign with performance
# metrics, creative assets, audience targeting information, and timeline views.
# It allows users to manage campaign settings and monitor real-time performance data.

import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import axios from 'axios';

// Components (these would be imported from your component library)
import MetricCard from '../components/analytics/MetricCard';
import CreativeAssetCard from '../components/campaigns/CreativeAssetCard';
import PerformanceChart from '../components/analytics/PerformanceChart';
import ActivityFeed from '../components/shared/ActivityFeed';
import TabNavigation from '../components/shared/TabNavigation';

const API_URL = import.meta.env.VITE_API_URL || '/api';

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

const CampaignDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(true);
  const [campaign, setCampaign] = useState(null);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    const fetchCampaign = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        const token = localStorage.getItem('auth_token');
        
        if (!token) {
          throw new Error('No authentication token found');
        }
        
        const response = await axios.get(`${API_URL}/campaigns/${id}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        
        setCampaign(response.data);
      } catch (err) {
        console.error('Error fetching campaign:', err);
        setError('Failed to load campaign data. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchCampaign();
  }, [id]);
  
  // Demo data for development
  const demoCampaign = {
    id: 1,
    name: 'Summer Collection Launch',
    description: 'Promotional campaign for our new summer fashion collection targeting young adults.',
    status: 'active',
    startDate: '2025-05-01',
    endDate: '2025-07-31',
    budget: 25000,
    spent: 18750,
    remaining: 6250,
    progress: 75,
    objective: 'conversions',
    targetAudience: {
      demographics: {
        ageRange: '18-35',
        gender: 'all',
        locations: ['New York', 'Los Angeles', 'Chicago', 'Miami']
      },
      interests: ['Fashion', 'Summer trends', 'Beach lifestyle', 'Outdoor activities'],
      behaviors: ['Online shoppers', 'Fashion enthusiasts', 'Instagram users']
    },
    channels: [
      { name: 'Instagram', budget: 10000, spent: 7500 },
      { name: 'Facebook', budget: 8000, spent: 6000 },
      { name: 'Google Search', budget: 7000, spent: 5250 }
    ],
    metrics: {
      impressions: 1200000,
      clicks: 48000,
      ctr: 4.0,
      conversions: 960,
      costPerClick: 0.39,
      costPerConversion: 19.53,
      conversionRate: 2.0
    },
    creatives: [
      { id: 1, name: 'Summer Banner 1', type: 'image', status: 'active', performance: 'high' },
      { id: 2, name: 'Product Showcase Video', type: 'video', status: 'active', performance: 'medium' },
      { id: 3, name: 'Collection Lookbook', type: 'carousel', status: 'active', performance: 'high' },
      { id: 4, name: 'Limited Edition Promo', type: 'image', status: 'paused', performance: 'low' }
    ],
    activities: [
      { id: 1, type: 'campaign_status', title: 'Campaign Launched', timestamp: '2025-05-01T09:00:00Z', status: 'completed' },
      { id: 2, type: 'creative_update', title: 'New Creative Added', timestamp: '2025-05-10T14:30:00Z', status: 'completed' },
      { id: 3, type: 'analytics', title: 'Performance Milestone Reached', timestamp: '2025-05-15T16:45:00Z', status: 'completed' },
      { id: 4, type: 'budget_update', title: 'Budget Adjustment', timestamp: '2025-05-18T11:20:00Z', status: 'completed' }
    ]
  };

  // Use campaign data or fallback to demoCampaign
  const campaignData = campaign || demoCampaign;

  // Tabs configuration
  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'creatives', label: 'Creatives' },
    { id: 'audience', label: 'Audience' },
    { id: 'channels', label: 'Channels' },
    { id: 'analytics', label: 'Analytics' },
    { id: 'settings', label: 'Settings' }
  ];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="w-10 h-10 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="mt-3 text-gray-600 dark:text-gray-400">Loading campaign...</p>
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
          <div className="flex justify-center space-x-3">
            <button 
              onClick={() => window.location.reload()}
              className="px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-200 dark:hover:bg-gray-600"
            >
              Retry
            </button>
            <button
              onClick={() => navigate('/campaigns')}
              className="px-4 py-2 bg-primary text-white rounded-md hover:bg-primary-dark"
            >
              Back to Campaigns
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">{campaignData.name}</h2>
            <StatusBadge status={campaignData.status} />
          </div>
          <p className="mt-1 text-gray-600 dark:text-gray-400">{campaignData.description}</p>
        </div>
        
        <div className="flex items-center space-x-3">
          <button className="px-3 py-1.5 border border-gray-300 dark:border-gray-600 rounded-md text-sm font-medium text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700">
            Edit
          </button>
          
          {campaignData.status === 'active' ? (
            <button className="px-3 py-1.5 border border-gray-300 dark:border-gray-600 rounded-md text-sm font-medium text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700">
              Pause
            </button>
          ) : campaignData.status === 'paused' ? (
            <button className="px-3 py-1.5 border border-transparent rounded-md text-sm font-medium text-white bg-green-600 hover:bg-green-700">
              Resume
            </button>
          ) : campaignData.status === 'draft' || campaignData.status === 'planning' ? (
            <button className="px-3 py-1.5 border border-transparent rounded-md text-sm font-medium text-white bg-primary hover:bg-primary-dark">
              Launch
            </button>
          ) : null}
          
          <div className="relative">
            <button className="px-3 py-1.5 border border-gray-300 dark:border-gray-600 rounded-md text-sm font-medium text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700">
              More
            </button>
            {/* Dropdown menu would go here */}
          </div>
        </div>
      </div>
      
      {/* Campaign timeline */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 border border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-500 dark:text-gray-400">Campaign timeline</p>
            <p className="text-base font-medium text-gray-900 dark:text-white">
              {new Date(campaignData.startDate).toLocaleDateString()} - {new Date(campaignData.endDate).toLocaleDateString()}
            </p>
          </div>
          <div>
            <div className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
              <div 
                className="h-full bg-primary" 
                style={{ width: `${campaignData.progress}%` }}
              ></div>
            </div>
            <p className="mt-1 text-xs text-right text-gray-500 dark:text-gray-400">
              {campaignData.progress}% complete
            </p>
          </div>
        </div>
      </div>
      
      {/* Key metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard 
          title="Budget" 
          value={`$${campaignData.budget.toLocaleString()}`} 
        />
        <MetricCard 
          title="Spent" 
          value={`$${campaignData.spent.toLocaleString()}`} 
          percentage={campaignData.spent / campaignData.budget * 100} 
        />
        <MetricCard 
          title="Impressions" 
          value={campaignData.metrics.impressions.toLocaleString()} 
        />
        <MetricCard 
          title="Conversions" 
          value={campaignData.metrics.conversions.toLocaleString()} 
        />
      </div>
      
      {/* Tabs navigation */}
      <div className="border-b border-gray-200 dark:border-gray-700">
        <div className="flex overflow-x-auto">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`whitespace-nowrap px-4 py-2 border-b-2 text-sm font-medium ${
                activeTab === tab.id
                  ? 'border-primary text-primary'
                  : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>
      
      {/* Tab content */}
      <div className="mt-6">
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Performance overview */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 border border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Performance Overview</h3>
              <div className="h-64">
                {/* This would be replaced with your chart component */}
                <div className="flex items-center justify-center h-full bg-gray-100 dark:bg-gray-700 rounded">
                  <p className="text-gray-500 dark:text-gray-400">Performance Chart Placeholder</p>
                </div>
              </div>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                <div className="text-center">
                  <p className="text-sm text-gray-500 dark:text-gray-400">CTR</p>
                  <p className="text-lg font-semibold text-gray-900 dark:text-white">{campaignData.metrics.ctr}%</p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-gray-500 dark:text-gray-400">CPC</p>
                  <p className="text-lg font-semibold text-gray-900 dark:text-white">${campaignData.metrics.costPerClick}</p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-gray-500 dark:text-gray-400">Conv. Rate</p>
                  <p className="text-lg font-semibold text-gray-900 dark:text-white">{campaignData.metrics.conversionRate}%</p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-gray-500 dark:text-gray-400">Cost/Conv.</p>
                  <p className="text-lg font-semibold text-gray-900 dark:text-white">${campaignData.metrics.costPerConversion}</p>
                </div>
              </div>
            </div>
            
            {/* Top creatives */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">Top Creatives</h3>
                <button 
                  onClick={() => setActiveTab('creatives')}
                  className="text-sm font-medium text-primary hover:text-primary-dark"
                >
                  View all
                </button>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {campaignData.creatives
                  .filter(creative => creative.performance === 'high')
                  .slice(0, 3)
                  .map(creative => (
                    <div key={creative.id} className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-4">
                      <div className="flex justify-between items-start">
                        <div>
                          <p className="font-medium text-gray-900 dark:text-white">{creative.name}</p>
                          <p className="text-sm text-gray-500 dark:text-gray-400 capitalize">{creative.type}</p>
                        </div>
                        <StatusBadge status={creative.status} />
                      </div>
                      <div className="mt-3 h-32 bg-gray-100 dark:bg-gray-700 rounded flex items-center justify-center">
                        <p className="text-gray-500 dark:text-gray-400 text-sm">Creative Preview</p>
                      </div>
                    </div>
                  ))}
              </div>
            </div>
            
            {/* Recent activity */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Recent Activity</h3>
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 overflow-hidden">
                <ActivityFeed activities={campaignData.activities} />
              </div>
            </div>
          </div>
        )}
        
        {activeTab === 'creatives' && (
          <div>
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">Campaign Creatives</h3>
              <button className="px-3 py-1.5 border border-transparent rounded-md text-sm font-medium text-white bg-primary hover:bg-primary-dark">
                Add Creative
              </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {campaignData.creatives.map(creative => (
                <div key={creative.id} className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-4">
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white">{creative.name}</p>
                      <p className="text-sm text-gray-500 dark:text-gray-400 capitalize">{creative.type}</p>
                    </div>
                    <StatusBadge status={creative.status} />
                  </div>
                  <div className="mt-3 h-40 bg-gray-100 dark:bg-gray-700 rounded flex items-center justify-center">
                    <p className="text-gray-500 dark:text-gray-400 text-sm">Creative Preview</p>
                  </div>
                  <div className="mt-3 flex justify-end space-x-2">
                    <button className="px-2 py-1 text-xs text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 rounded">
                      Edit
                    </button>
                    {creative.status === 'active' ? (
                      <button className="px-2 py-1 text-xs text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 rounded">
                        Pause
                      </button>
                    ) : (
                      <button className="px-2 py-1 text-xs text-white bg-green-600 rounded">
                        Activate
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
        
        {activeTab === 'audience' && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-6">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Target Audience</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Demographics */}
              <div>
                <h4 className="font-medium text-gray-800 dark:text-gray-200 mb-2">Demographics</h4>
                <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                  <div className="mb-3">
                    <p className="text-sm text-gray-500 dark:text-gray-400">Age Range</p>
                    <p className="font-medium text-gray-900 dark:text-white">{campaignData.targetAudience.demographics.ageRange}</p>
                  </div>
                  <div className="mb-3">
                    <p className="text-sm text-gray-500 dark:text-gray-400">Gender</p>
                    <p className="font-medium text-gray-900 dark:text-white capitalize">{campaignData.targetAudience.demographics.gender}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Locations</p>
                    <div className="mt-1 flex flex-wrap gap-1">
                      {campaignData.targetAudience.demographics.locations.map((location, index) => (
                        <span 
                          key={index}
                          className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 dark:bg-gray-600 text-gray-800 dark:text-gray-200"
                        >
                          {location}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Interests */}
              <div>
                <h4 className="font-medium text-gray-800 dark:text-gray-200 mb-2">Interests</h4>
                <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                  <div className="flex flex-wrap gap-1">
                    {campaignData.targetAudience.interests.map((interest, index) => (
                      <span 
                        key={index}
                        className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200"
                      >
                        {interest}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
              
              {/* Behaviors */}
              <div>
                <h4 className="font-medium text-gray-800 dark:text-gray-200 mb-2">Behaviors</h4>
                <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                  <div className="flex flex-wrap gap-1">
                    {campaignData.targetAudience.behaviors.map((behavior, index) => (
                      <span 
                        key={index}
                        className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200"
                      >
                        {behavior}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
            
            <div className="mt-6 flex justify-end">
              <button className="px-3 py-1.5 border border-transparent rounded-md text-sm font-medium text-white bg-primary hover:bg-primary-dark">
                Edit Audience
              </button>
            </div>
          </div>
        )}
        
        {activeTab === 'channels' && (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">Media Channels</h3>
              <button className="px-3 py-1.5 border border-transparent rounded-md text-sm font-medium text-white bg-primary hover:bg-primary-dark">
                Add Channel
              </button>
            </div>
            
            {campaignData.channels.map((channel, index) => (
              <div key={index} className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-4">
                <div className="flex items-center justify-between">
                  <h4 className="font-medium text-gray-900 dark:text-white">{channel.name}</h4>
                  <button className="text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300">
                    Edit
                  </button>
                </div>
                
                <div className="mt-3">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-sm text-gray-500 dark:text-gray-400">Budget allocation</span>
                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      ${channel.spent.toLocaleString()} / ${channel.budget.toLocaleString()}
                    </span>
                  </div>
                  <div className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-primary" 
                      style={{ width: `${(channel.spent / channel.budget) * 100}%` }}
                    ></div>
                  </div>
                  <p className="mt-1 text-xs text-right text-gray-500 dark:text-gray-400">
                    {Math.round((channel.spent / channel.budget) * 100)}% spent
                  </p>
                </div>
                
                <div className="mt-4 grid grid-cols-3 gap-4">
                  <div className="bg-gray-50 dark:bg-gray-700 p-2 rounded">
                    <p className="text-xs text-gray-500 dark:text-gray-400">Impressions</p>
                    <p className="text-sm font-semibold text-gray-900 dark:text-white">450,000</p>
                  </div>
                  <div className="bg-gray-50 dark:bg-gray-700 p-2 rounded">
                    <p className="text-xs text-gray-500 dark:text-gray-400">CTR</p>
                    <p className="text-sm font-semibold text-gray-900 dark:text-white">3.8%</p>
                  </div>
                  <div className="bg-gray-50 dark:bg-gray-700 p-2 rounded">
                    <p className="text-xs text-gray-500 dark:text-gray-400">CPC</p>
                    <p className="text-sm font-semibold text-gray-900 dark:text-white">$0.42</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
        
        {/* Additional tab content would be implemented here */}
      </div>
    </div>
  );
};

export default CampaignDetailPage;