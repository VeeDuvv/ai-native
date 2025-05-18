# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file creates a page that shows a list of all your advertising campaigns,
# so you can see which ones are active and how they're doing.

# High School Explanation:
# This component implements the campaigns list page where users can view all their
# campaigns with filtering and sorting capabilities. It displays campaign cards in a 
# grid layout with search functionality and status filtering options.

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

// Components
import CampaignCard from '../components/campaigns/CampaignCard';

const API_URL = import.meta.env.VITE_API_URL || '/api';

const CampaignsPage = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [campaigns, setCampaigns] = useState([]);
  const [error, setError] = useState(null);
  
  // Filtering and sorting
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [sortBy, setSortBy] = useState('recent');

  useEffect(() => {
    const fetchCampaigns = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        const token = localStorage.getItem('auth_token');
        
        if (!token) {
          throw new Error('No authentication token found');
        }
        
        const response = await axios.get(`${API_URL}/campaigns`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        
        setCampaigns(response.data);
      } catch (err) {
        console.error('Error fetching campaigns:', err);
        setError('Failed to load campaigns. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchCampaigns();
  }, []);

  // Demo data for development
  const demoCampaigns = [
    { id: 1, name: 'Summer Collection Launch', status: 'active', progress: 75, budget: 25000, spent: 18750, impressions: 1200000, clicks: 48000, conversions: 960, createdAt: '2025-04-15' },
    { id: 2, name: 'Holiday Season Promotions', status: 'planning', progress: 30, budget: 40000, spent: 0, impressions: 0, clicks: 0, conversions: 0, createdAt: '2025-05-10' },
    { id: 3, name: 'Brand Awareness Campaign', status: 'active', progress: 50, budget: 15000, spent: 7500, impressions: 600000, clicks: 12000, conversions: 0, createdAt: '2025-04-20' },
    { id: 4, name: 'Q2 Sales Drive', status: 'paused', progress: 60, budget: 20000, spent: 12000, impressions: 800000, clicks: 24000, conversions: 480, createdAt: '2025-03-01' },
    { id: 5, name: 'Product Launch - Echo Series', status: 'draft', progress: 10, budget: 35000, spent: 0, impressions: 0, clicks: 0, conversions: 0, createdAt: '2025-05-15' },
    { id: 6, name: 'Email Retargeting', status: 'completed', progress: 100, budget: 5000, spent: 5000, impressions: 250000, clicks: 12500, conversions: 625, createdAt: '2025-02-01' }
  ];

  // Use campaignsData or fallback to demoCampaigns
  const campaignsData = campaigns.length ? campaigns : demoCampaigns;
  
  // Filter campaigns
  const filteredCampaigns = campaignsData.filter(campaign => {
    const matchesSearch = campaign.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === 'all' || campaign.status === statusFilter;
    return matchesSearch && matchesStatus;
  });
  
  // Sort campaigns
  const sortedCampaigns = [...filteredCampaigns].sort((a, b) => {
    switch (sortBy) {
      case 'name':
        return a.name.localeCompare(b.name);
      case 'budget':
        return b.budget - a.budget;
      case 'performance':
        const aConvRate = a.clicks ? (a.conversions / a.clicks) * 100 : 0;
        const bConvRate = b.clicks ? (b.conversions / b.clicks) * 100 : 0;
        return bConvRate - aConvRate;
      case 'recent':
      default:
        return new Date(b.createdAt) - new Date(a.createdAt);
    }
  });

  // Status filter options
  const statusOptions = [
    { value: 'all', label: 'All Campaigns' },
    { value: 'active', label: 'Active' },
    { value: 'paused', label: 'Paused' },
    { value: 'planning', label: 'Planning' },
    { value: 'completed', label: 'Completed' },
    { value: 'draft', label: 'Draft' }
  ];
  
  // Sort options
  const sortOptions = [
    { value: 'recent', label: 'Most Recent' },
    { value: 'name', label: 'Name' },
    { value: 'budget', label: 'Budget (High to Low)' },
    { value: 'performance', label: 'Performance' }
  ];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="w-10 h-10 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="mt-3 text-gray-600 dark:text-gray-400">Loading campaigns...</p>
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
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Campaigns</h2>
        <Link
          to="/campaigns/new"
          className="inline-flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
        >
          New Campaign
        </Link>
      </div>
      
      {/* Filters & Search */}
      <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow border border-gray-200 dark:border-gray-700">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Search */}
          <div>
            <label htmlFor="search" className="sr-only">Search</label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg className="h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                  <path fillRule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clipRule="evenodd" />
                </svg>
              </div>
              <input
                id="search"
                name="search"
                className="block w-full pl-10 pr-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-gray-900 dark:text-white dark:bg-gray-700 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-primary focus:border-primary sm:text-sm"
                placeholder="Search campaigns"
                type="search"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          </div>
          
          {/* Status Filter */}
          <div>
            <label htmlFor="status" className="sr-only">Status</label>
            <select
              id="status"
              name="status"
              className="block w-full pl-3 pr-10 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-gray-900 dark:text-white dark:bg-gray-700 focus:outline-none focus:ring-primary focus:border-primary sm:text-sm"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              {statusOptions.map(option => (
                <option key={option.value} value={option.value}>{option.label}</option>
              ))}
            </select>
          </div>
          
          {/* Sort */}
          <div>
            <label htmlFor="sort" className="sr-only">Sort by</label>
            <select
              id="sort"
              name="sort"
              className="block w-full pl-3 pr-10 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-gray-900 dark:text-white dark:bg-gray-700 focus:outline-none focus:ring-primary focus:border-primary sm:text-sm"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
            >
              {sortOptions.map(option => (
                <option key={option.value} value={option.value}>{option.label}</option>
              ))}
            </select>
          </div>
        </div>
      </div>
      
      {/* Campaigns Grid */}
      <div>
        {sortedCampaigns.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {sortedCampaigns.map(campaign => (
              <CampaignCard key={campaign.id} campaign={campaign} />
            ))}
          </div>
        ) : (
          <div className="bg-white dark:bg-gray-800 p-8 rounded-lg shadow border border-gray-200 dark:border-gray-700 text-center">
            <p className="text-gray-600 dark:text-gray-400 mb-4">No campaigns found matching your filters.</p>
            <button
              onClick={() => {
                setSearchQuery('');
                setStatusFilter('all');
              }}
              className="px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-200 dark:hover:bg-gray-600"
            >
              Clear filters
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default CampaignsPage;