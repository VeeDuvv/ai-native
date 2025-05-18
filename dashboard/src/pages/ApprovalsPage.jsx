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
import { Link, useParams, useNavigate } from 'react-router-dom';
import { useApprovalStore } from '../stores/approvalStore';
import { useNotificationContext } from '../components/shared/NotificationProvider';
import { useSocketEvent } from '../context/SocketContext';

// Components
import ApprovalCard from '../components/approvals/ApprovalCard';
import ApprovalDetail from '../components/approvals/ApprovalDetail';

const ApprovalsPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [selectedApprovalId, setSelectedApprovalId] = useState(id || null);
  const [viewMode, setViewMode] = useState(id ? 'detail' : 'list');
  
  const { 
    approvals, 
    currentApproval, 
    isLoading, 
    error, 
    filters, 
    pagination,
    fetchApprovals,
    fetchApprovalById,
    setFilters,
    setPagination,
    clearCurrentApproval,
    clearError
  } = useApprovalStore();
  
  const { error: showError } = useNotificationContext();
  
  // Fetch approvals on initial load and when filters change
  useEffect(() => {
    fetchApprovals();
  }, [fetchApprovals, filters, pagination.page]);
  
  // Show error notification when approval store error changes
  useEffect(() => {
    if (error) {
      showError(error);
      clearError();
    }
  }, [error, showError, clearError]);
  
  // Fetch approval details when ID changes
  useEffect(() => {
    if (selectedApprovalId) {
      fetchApprovalById(selectedApprovalId);
      setViewMode('detail');
    } else {
      clearCurrentApproval();
      setViewMode('list');
    }
  }, [selectedApprovalId, fetchApprovalById, clearCurrentApproval]);
  
  // Update URL when selected approval changes
  useEffect(() => {
    if (selectedApprovalId && viewMode === 'detail') {
      navigate(`/approvals/${selectedApprovalId}`, { replace: true });
    } else if (!selectedApprovalId && viewMode === 'list') {
      navigate('/approvals', { replace: true });
    }
  }, [selectedApprovalId, viewMode, navigate]);
  
  // Handle new approvals from WebSocket
  const handleNewApproval = (payload) => {
    // Refresh approvals list when a new approval is received
    fetchApprovals();
  };
  
  // Listen for new approval events
  useSocketEvent('new_approval', handleNewApproval);
  
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
  
  // Handle filter changes
  const handleFilterChange = (key, value) => {
    setFilters({ [key]: value });
  };
  
  // Handle search input change
  const handleSearchChange = (e) => {
    setFilters({ search: e.target.value });
  };
  
  // Handle approval selection
  const handleApprovalSelect = (id) => {
    setSelectedApprovalId(id);
  };
  
  // Handle going back to list view
  const handleBackToList = () => {
    setSelectedApprovalId(null);
    setViewMode('list');
    navigate('/approvals', { replace: true });
  };

  // If in detail view, show only the selected approval
  if (viewMode === 'detail') {
    return (
      <div className="max-w-4xl mx-auto">
        <button 
          onClick={handleBackToList}
          className="flex items-center mb-4 text-sm text-primary hover:text-primary-dark"
        >
          <svg className="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back to approvals
        </button>
        
        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="w-10 h-10 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto"></div>
              <p className="mt-3 text-gray-600 dark:text-gray-400">Loading approval details...</p>
            </div>
          </div>
        ) : (
          <ApprovalDetail approval={currentApproval} onClose={handleBackToList} />
        )}
      </div>
    );
  }

  // Otherwise, show the list view
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
                value={filters.search}
                onChange={handleSearchChange}
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
              value={filters.type}
              onChange={(e) => handleFilterChange('type', e.target.value)}
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
              value={filters.status}
              onChange={(e) => handleFilterChange('status', e.target.value)}
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
        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="w-10 h-10 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto"></div>
              <p className="mt-3 text-gray-600 dark:text-gray-400">Loading approval requests...</p>
            </div>
          </div>
        ) : approvals.length > 0 ? (
          approvals.map(approval => (
            <div 
              key={approval.id}
              onClick={() => handleApprovalSelect(approval.id)}
              className="cursor-pointer"
            >
              <ApprovalCard 
                approval={approval}
                onClick={() => handleApprovalSelect(approval.id)}
              />
            </div>
          ))
        ) : (
          <div className="bg-white dark:bg-gray-800 p-8 rounded-lg shadow border border-gray-200 dark:border-gray-700 text-center">
            <p className="text-gray-600 dark:text-gray-400 mb-4">No approval requests found matching your filters.</p>
            <button
              onClick={() => {
                setFilters({
                  search: '',
                  type: 'all',
                  status: 'pending'
                });
              }}
              className="px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-200 dark:hover:bg-gray-600"
            >
              Clear filters
            </button>
          </div>
        )}
      </div>
      
      {/* Pagination */}
      {pagination.totalPages > 1 && (
        <div className="flex justify-between items-center border-t border-gray-200 dark:border-gray-700 px-4 py-3 sm:px-6">
          <div className="flex-1 flex justify-between sm:hidden">
            <button
              onClick={() => setPagination({ page: pagination.page - 1 })}
              disabled={pagination.page === 1}
              className="relative inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50"
            >
              Previous
            </button>
            <button
              onClick={() => setPagination({ page: pagination.page + 1 })}
              disabled={pagination.page === pagination.totalPages}
              className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50"
            >
              Next
            </button>
          </div>
          <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
            <div>
              <p className="text-sm text-gray-700 dark:text-gray-300">
                Showing <span className="font-medium">{((pagination.page - 1) * pagination.limit) + 1}</span> to <span className="font-medium">{Math.min(pagination.page * pagination.limit, pagination.total)}</span> of{' '}
                <span className="font-medium">{pagination.total}</span> results
              </p>
            </div>
            <div>
              <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                <button
                  onClick={() => setPagination({ page: pagination.page - 1 })}
                  disabled={pagination.page === 1}
                  className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm font-medium text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50"
                >
                  <span className="sr-only">Previous</span>
                  <svg className="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                    <path fillRule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </button>
                
                {/* Page numbers */}
                {[...Array(pagination.totalPages).keys()].map((page) => {
                  const pageNumber = page + 1;
                  
                  // Show directly adjacent pages, first, last, and current page
                  const showPageNumber = 
                    pageNumber === 1 || 
                    pageNumber === pagination.totalPages ||
                    pageNumber === pagination.page ||
                    pageNumber === pagination.page - 1 ||
                    pageNumber === pagination.page + 1;
                  
                  // Show ellipsis for page gaps
                  const showEllipsisBefore = 
                    pageNumber === pagination.page - 2 && pagination.page > 3;
                  
                  const showEllipsisAfter = 
                    pageNumber === pagination.page + 2 && pagination.page < pagination.totalPages - 2;
                  
                  if (showEllipsisBefore) {
                    return (
                      <span
                        key={`ellipsis-before-${pageNumber}`}
                        className="relative inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm font-medium text-gray-700 dark:text-gray-300"
                      >
                        ...
                      </span>
                    );
                  }
                  
                  if (showEllipsisAfter) {
                    return (
                      <span
                        key={`ellipsis-after-${pageNumber}`}
                        className="relative inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm font-medium text-gray-700 dark:text-gray-300"
                      >
                        ...
                      </span>
                    );
                  }
                  
                  if (showPageNumber) {
                    return (
                      <button
                        key={pageNumber}
                        onClick={() => setPagination({ page: pageNumber })}
                        className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${
                          pagination.page === pageNumber
                            ? 'z-10 bg-primary border-primary text-white'
                            : 'bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
                        }`}
                      >
                        {pageNumber}
                      </button>
                    );
                  }
                  
                  return null;
                })}
                
                <button
                  onClick={() => setPagination({ page: pagination.page + 1 })}
                  disabled={pagination.page === pagination.totalPages}
                  className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm font-medium text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50"
                >
                  <span className="sr-only">Next</span>
                  <svg className="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                    <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                  </svg>
                </button>
              </nav>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ApprovalsPage;