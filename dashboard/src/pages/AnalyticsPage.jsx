# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file creates a page with charts and numbers that show how well your
# advertising campaigns are performing, like how many people clicked on ads
# and how much money you're making.

# High School Explanation:
# This component implements an analytics dashboard with performance metrics,
# trend visualization, and campaign comparison features. It provides insights
# into advertising effectiveness across channels and campaigns with interactive
# data visualizations.

import { useState, useEffect } from 'react';
import axios from 'axios';

// Components (these would be imported from your component library)
import MetricCard from '../components/analytics/MetricCard';

const API_URL = import.meta.env.VITE_API_URL || '/api';

const AnalyticsPage = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [analyticsData, setAnalyticsData] = useState(null);
  const [error, setError] = useState(null);
  
  // Filtering and date ranges
  const [dateRange, setDateRange] = useState('last30');
  const [campaignFilter, setCampaignFilter] = useState('all');
  const [channelFilter, setChannelFilter] = useState('all');

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        const token = localStorage.getItem('auth_token');
        
        if (!token) {
          throw new Error('No authentication token found');
        }
        
        const response = await axios.get(`${API_URL}/analytics`, {
          headers: { Authorization: `Bearer ${token}` },
          params: { 
            dateRange, 
            campaignId: campaignFilter !== 'all' ? campaignFilter : undefined,
            channel: channelFilter !== 'all' ? channelFilter : undefined
          }
        });
        
        setAnalyticsData(response.data);
      } catch (err) {
        console.error('Error fetching analytics:', err);
        setError('Failed to load analytics data. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchAnalytics();
  }, [dateRange, campaignFilter, channelFilter]);

  // Demo data for development
  const demoData = {
    overview: {
      impressions: 5800000,
      clicks: 174000,
      conversions: 3480,
      spend: 69750,
      revenue: 208800,
      ctr: 3.0,
      cpc: 0.40,
      cvr: 2.0,
      roas: 2.99
    },
    campaigns: [
      { id: 1, name: 'Summer Collection Launch', impressions: 1200000, clicks: 48000, conversions: 960, spend: 18750, revenue: 57600 },
      { id: 2, name: 'Holiday Season Promotions', impressions: 0, clicks: 0, conversions: 0, spend: 0, revenue: 0 },
      { id: 3, name: 'Brand Awareness Campaign', impressions: 600000, clicks: 12000, conversions: 0, spend: 7500, revenue: 0 },
      { id: 4, name: 'Q2 Sales Drive', impressions: 800000, clicks: 24000, conversions: 480, spend: 12000, revenue: 28800 },
      { id: 5, name: 'Product Launch - Echo Series', impressions: 0, clicks: 0, conversions: 0, spend: 0, revenue: 0 },
      { id: 6, name: 'Email Retargeting', impressions: 250000, clicks: 12500, conversions: 625, spend: 5000, revenue: 37500 },
      { id: 7, name: 'Seasonal Discount Campaign', impressions: 1200000, clicks: 36000, conversions: 540, spend: 14400, revenue: 32400 },
      { id: 8, name: 'Social Media Contest', impressions: 1750000, clicks: 41500, conversions: 875, spend: 12100, revenue: 52500 }
    ],
    channels: [
      { name: 'Instagram', impressions: 2100000, clicks: 73500, conversions: 1470, spend: 29400, revenue: 88200 },
      { name: 'Facebook', impressions: 1800000, clicks: 45000, conversions: 900, spend: 18000, revenue: 54000 },
      { name: 'Google Search', impressions: 450000, clicks: 22500, conversions: 675, spend: 11250, revenue: 40500 },
      { name: 'Google Display', impressions: 950000, clicks: 19000, conversions: 285, spend: 7600, revenue: 17100 },
      { name: 'YouTube', impressions: 500000, clicks: 14000, conversions: 150, spend: 3500, revenue: 9000 }
    ],
    // These would be time series data for charts
    timeSeries: {
      impressions: Array.from({ length: 30 }, () => Math.floor(Math.random() * 50000) + 150000),
      clicks: Array.from({ length: 30 }, () => Math.floor(Math.random() * 1500) + 4500),
      conversions: Array.from({ length: 30 }, () => Math.floor(Math.random() * 30) + 90),
      spend: Array.from({ length: 30 }, () => Math.floor(Math.random() * 500) + 2000),
      revenue: Array.from({ length: 30 }, () => Math.floor(Math.random() * 1200) + 6000)
    }
  };

  // Campaign options for filter
  const campaignOptions = [
    { value: 'all', label: 'All Campaigns' },
    ...demoData.campaigns.map(campaign => ({ 
      value: campaign.id.toString(), 
      label: campaign.name 
    }))
  ];
  
  // Channel options for filter
  const channelOptions = [
    { value: 'all', label: 'All Channels' },
    ...demoData.channels.map(channel => ({ 
      value: channel.name, 
      label: channel.name 
    }))
  ];
  
  // Date range options
  const dateRangeOptions = [
    { value: 'last7', label: 'Last 7 Days' },
    { value: 'last30', label: 'Last 30 Days' },
    { value: 'last90', label: 'Last 90 Days' },
    { value: 'year', label: 'Year to Date' },
    { value: 'custom', label: 'Custom Range' }
  ];

  // Use analyticsData or fallback to demoData
  const data = analyticsData || demoData;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="w-10 h-10 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="mt-3 text-gray-600 dark:text-gray-400">Loading analytics data...</p>
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

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Analytics</h2>
        
        {/* Date Range Filter */}
        <div className="flex items-center space-x-3">
          <label htmlFor="dateRange" className="text-sm font-medium text-gray-700 dark:text-gray-300">
            Date Range:
          </label>
          <select
            id="dateRange"
            name="dateRange"
            className="pl-3 pr-10 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-md text-gray-900 dark:text-white dark:bg-gray-700 focus:outline-none focus:ring-primary focus:border-primary"
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value)}
          >
            {dateRangeOptions.map(option => (
              <option key={option.value} value={option.value}>{option.label}</option>
            ))}
          </select>
        </div>
      </div>
      
      {/* Additional Filters */}
      <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow border border-gray-200 dark:border-gray-700">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Campaign Filter */}
          <div>
            <label htmlFor="campaign" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Campaign
            </label>
            <select
              id="campaign"
              name="campaign"
              className="block w-full pl-3 pr-10 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-gray-900 dark:text-white dark:bg-gray-700 focus:outline-none focus:ring-primary focus:border-primary sm:text-sm"
              value={campaignFilter}
              onChange={(e) => setCampaignFilter(e.target.value)}
            >
              {campaignOptions.map(option => (
                <option key={option.value} value={option.value}>{option.label}</option>
              ))}
            </select>
          </div>
          
          {/* Channel Filter */}
          <div>
            <label htmlFor="channel" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Channel
            </label>
            <select
              id="channel"
              name="channel"
              className="block w-full pl-3 pr-10 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-gray-900 dark:text-white dark:bg-gray-700 focus:outline-none focus:ring-primary focus:border-primary sm:text-sm"
              value={channelFilter}
              onChange={(e) => setChannelFilter(e.target.value)}
            >
              {channelOptions.map(option => (
                <option key={option.value} value={option.value}>{option.label}</option>
              ))}
            </select>
          </div>
        </div>
      </div>
      
      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard 
          title="Impressions" 
          value={data.overview.impressions.toLocaleString()} 
        />
        <MetricCard 
          title="Clicks" 
          value={data.overview.clicks.toLocaleString()} 
        />
        <MetricCard 
          title="Conversions" 
          value={data.overview.conversions.toLocaleString()} 
        />
        <MetricCard 
          title="Spend" 
          value={`$${data.overview.spend.toLocaleString()}`} 
        />
      </div>
      
      {/* Performance Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard 
          title="CTR" 
          value={`${data.overview.ctr}%`} 
        />
        <MetricCard 
          title="CPC" 
          value={`$${data.overview.cpc}`} 
        />
        <MetricCard 
          title="Conversion Rate" 
          value={`${data.overview.cvr}%`} 
        />
        <MetricCard 
          title="ROAS" 
          value={data.overview.roas.toFixed(2)} 
        />
      </div>
      
      {/* Performance Over Time Chart */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Performance Over Time</h3>
        <div className="h-80">
          {/* This would be replaced with your chart component */}
          <div className="flex items-center justify-center h-full bg-gray-100 dark:bg-gray-700 rounded">
            <p className="text-gray-500 dark:text-gray-400">Performance Chart Placeholder</p>
          </div>
        </div>
      </div>
      
      {/* Top Campaigns */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Top Campaigns</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Campaign
                </th>
                <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Impressions
                </th>
                <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Clicks
                </th>
                <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  CTR
                </th>
                <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Conversions
                </th>
                <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Spend
                </th>
                <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Revenue
                </th>
                <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  ROAS
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {data.campaigns
                .filter(campaign => campaign.spend > 0) // Only show active campaigns
                .sort((a, b) => b.revenue - a.revenue) // Sort by revenue
                .slice(0, 5) // Top 5
                .map((campaign, index) => {
                  const ctr = campaign.impressions ? (campaign.clicks / campaign.impressions * 100).toFixed(2) : '0.00';
                  const roas = campaign.spend ? (campaign.revenue / campaign.spend).toFixed(2) : '0.00';
                  
                  return (
                    <tr key={campaign.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                        {campaign.name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-500 dark:text-gray-400">
                        {campaign.impressions.toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-500 dark:text-gray-400">
                        {campaign.clicks.toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-500 dark:text-gray-400">
                        {ctr}%
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-500 dark:text-gray-400">
                        {campaign.conversions.toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-500 dark:text-gray-400">
                        ${campaign.spend.toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-500 dark:text-gray-400">
                        ${campaign.revenue.toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-500 dark:text-gray-400">
                        {roas}
                      </td>
                    </tr>
                  );
                })}
            </tbody>
          </table>
        </div>
      </div>
      
      {/* Channel Performance */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Channel Performance</h3>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Channel comparison chart */}
          <div className="h-64 bg-gray-100 dark:bg-gray-700 rounded flex items-center justify-center">
            <p className="text-gray-500 dark:text-gray-400">Channel Performance Chart Placeholder</p>
          </div>
          
          {/* Channel metrics table */}
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Channel
                  </th>
                  <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Spend
                  </th>
                  <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Conversions
                  </th>
                  <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    CPA
                  </th>
                  <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    ROAS
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                {data.channels.map((channel, index) => {
                  const cpa = channel.conversions ? (channel.spend / channel.conversions).toFixed(2) : 'N/A';
                  const roas = channel.spend ? (channel.revenue / channel.spend).toFixed(2) : 'N/A';
                  
                  return (
                    <tr key={index}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                        {channel.name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-500 dark:text-gray-400">
                        ${channel.spend.toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-500 dark:text-gray-400">
                        {channel.conversions.toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-500 dark:text-gray-400">
                        ${cpa}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-500 dark:text-gray-400">
                        {roas}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
      
      {/* Download Reports */}
      <div className="flex justify-end space-x-3">
        <button className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-sm font-medium text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700">
          Export to CSV
        </button>
        <button className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-sm font-medium text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700">
          Generate PDF Report
        </button>
      </div>
    </div>
  );
};

export default AnalyticsPage;