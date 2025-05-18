# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file creates a page where clients can see what things need their approval,
# like new ad designs or requests to change something in their campaigns.

# High School Explanation:
# This component displays a list of pending approval requests for creative assets,
# budget changes, targeting modifications, and other campaign elements. It allows
# clients to view, approve, or reject these requests with appropriate feedback.

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

// Components
import ApprovalCard from '../components/approvals/ApprovalCard';

const API_URL = import.meta.env.VITE_API_URL || '/api';

const ApprovalsPage = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [approvals, setApprovals] = useState([]);
  const [error, setError] = useState(null);
  
  // Filtering
  const [filterType, setFilterType] = useState('all');
  const [filterStatus, setFilterStatus] = useState('pending');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    const fetchApprovals = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        const token = localStorage.getItem('auth_token');
        
        if (!token) {
          throw new Error('No authentication token found');
        }
        
        const response = await axios.get(`${API_URL}/approvals`, {
          headers: { Authorization: `Bearer ${token}` },
          params: { status: filterStatus !== 'all' ? filterStatus : undefined }
        });
        
        setApprovals(response.data);
      } catch (err) {
        console.error('Error fetching approvals:', err);
        setError('Failed to load approval requests. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchApprovals();
  }, [filterStatus]);

  // Demo data for development
  const demoApprovals = [
    { 
      id: 1, 
      title: 'Summer Collection Banner Ad', 
      type: 'creative', 
      status: 'pending',
      campaign: 'Summer Collection Launch',
      campaignId: 1,
      createdAt: '2025-05-17T11:20:00Z', 
      deadline: '2025-05-19T11:20:00Z',
      description: 'New banner ad featuring the summer collection hero image.',
      requestedBy: 'Sophia Chen',
      requestedById: 101
    },
    { 
      id: 2, 
      title: 'Budget Increase Request', 
      type: 'budget', 
      status: 'pending',
      campaign: 'Brand Awareness Campaign',
      campaignId: 3,
      createdAt: '2025-05-16T15:30:00Z', 
      deadline: '2025-05-18T15:30:00Z',
      description: 'Request to increase campaign budget from $15,000 to $20,000.',
      requestedBy: 'Michael Johnson',
      requestedById: 102
    },
    { 
      id: 3, 
      title: 'Product Video Ad', 
      type: 'creative', 
      status: 'pending',
      campaign: 'Summer Collection Launch',
      campaignId: 1,
      createdAt: '2025-05-15T09:45:00Z', 
      deadline: '2025-05-17T09:45:00Z',
      description: '30-second product showcase video for Instagram and Facebook.',
      requestedBy: 'Sophia Chen',
      requestedById: 101
    },
    { 
      id: 4, 
      title: 'Audience Targeting Update', 
      type: 'target', 
      status: 'pending',
      campaign: 'Holiday Season Promotions',
      campaignId: 2,
      createdAt: '2025-05-17T14:15:00Z', 
      deadline: '2025-05-19T14:15:00Z',
      description: 'Proposed changes to audience targeting parameters to include additional geographic regions.',
      requestedBy: 'Alex Rodriguez',
      requestedById: 103
    },
    { 
      id: 5, 
      title: 'Campaign Timeline Extension', 
      type: 'schedule', 
      status: 'pending',
      campaign: 'Brand Awareness Campaign',
      campaignId: 3,
      createdAt: '2025-05-16T10:30:00Z', 
      deadline: '2025-05-18T10:30:00Z',
      description: 'Request to extend campaign end date by two weeks.',
      requestedBy: 'Michael Johnson',
      requestedById: 102
    }
  ];

  // Approval types for filter
  const approvalTypes = [
    { value: 'all', label: 'All Types' },
    { value: 'creative', label: 'Creative Assets' },
    { value: 'budget', label: 'Budget Changes' },
    { value: 'target', label: 'Audience Targeting' },
    { value: 'schedule', label: 'Campaign Schedule' },
    { value: 'document', label: 'Documents' }
  ];
  
  // Approval status for filter
  const approvalStatuses = [
    { value: 'all', label: 'All Statuses' },
    { value: 'pending', label: 'Pending' },
    { value: 'approved', label: 'Approved' },
    { value: 'rejected', label: 'Rejected' }
  ];

  // Use approvals data or fallback to demoApprovals
  const approvalsData = approvals.length ? approvals : demoApprovals;
  
  // Filter approvals
  const filteredApprovals = approvalsData.filter(approval => {
    const matchesType = filterType === 'all' || approval.type === filterType;
    const matchesSearch = approval.title.toLowerCase().includes(searchQuery.toLowerCase()) || 
                         approval.campaign.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesType && matchesSearch;
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="w-10 h-10 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="mt-3 text-gray-600 dark:text-gray-400">Loading approval requests...</p>
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
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Approvals</h2>
      </div>
      
      {/* Filters */}
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
                placeholder="Search approvals"
                type="search"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          </div>
          
          {/* Type Filter */}
          <div>
            <label htmlFor="type" className="sr-only">Type</label>
            <select
              id="type"
              name="type"
              className="block w-full pl-3 pr-10 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-gray-900 dark:text-white dark:bg-gray-700 focus:outline-none focus:ring-primary focus:border-primary sm:text-sm"
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
            >
              {approvalTypes.map(option => (
                <option key={option.value} value={option.value}>{option.label}</option>
              ))}
            </select>
          </div>
          
          {/* Status Filter */}
          <div>
            <label htmlFor="status" className="sr-only">Status</label>
            <select
              id="status"
              name="status"
              className="block w-full pl-3 pr-10 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-gray-900 dark:text-white dark:bg-gray-700 focus:outline-none focus:ring-primary focus:border-primary sm:text-sm"
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
            >
              {approvalStatuses.map(option => (
                <option key={option.value} value={option.value}>{option.label}</option>
              ))}
            </select>
          </div>
        </div>
      </div>
      
      {/* Approvals list */}
      <div className="space-y-4">
        {filteredApprovals.length > 0 ? (
          filteredApprovals.map(approval => (
            <ApprovalCard key={approval.id} approval={approval} />
          ))
        ) : (
          <div className="bg-white dark:bg-gray-800 p-8 rounded-lg shadow border border-gray-200 dark:border-gray-700 text-center">
            <p className="text-gray-600 dark:text-gray-400 mb-4">No approval requests found matching your filters.</p>
            <button
              onClick={() => {
                setSearchQuery('');
                setFilterType('all');
                setFilterStatus('pending');
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

export default ApprovalsPage;