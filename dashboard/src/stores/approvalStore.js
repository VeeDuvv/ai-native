// SPDX-License-Identifier: MIT
// Copyright (c) 2025 Vamsi Duvvuri

// Fifth Grade Explanation:
// This file keeps track of things that need to be approved, like new ad designs.
// It remembers which items need approval, which ones are already approved or rejected,
// and helps other parts of the app know what to show.

// High School Explanation:
// This module implements a global state store for approval workflows using Zustand.
// It manages pending approvals, approval history, and the approval process workflow,
// centralizing approval data and operations across the application.

import { create } from 'zustand';
import apiService from '../services/api';

export const useApprovalStore = create((set, get) => ({
  approvals: [],
  currentApproval: null,
  isLoading: false,
  error: null,
  filters: {
    type: 'all',
    status: 'pending',
    search: ''
  },
  pagination: {
    page: 1,
    limit: 10,
    total: 0,
    totalPages: 0
  },
  
  // Fetch all approvals with optional filters
  fetchApprovals: async (filters = null, pagination = null) => {
    try {
      set({ isLoading: true, error: null });
      
      // Use provided filters or current state
      const currentFilters = filters || get().filters;
      const currentPagination = pagination || get().pagination;
      
      // Build params object
      const params = {
        page: currentPagination.page,
        limit: currentPagination.limit
      };
      
      // Add type filter if not "all"
      if (currentFilters.type !== 'all') {
        params.type = currentFilters.type;
      }
      
      // Add status filter if not "all"
      if (currentFilters.status !== 'all') {
        params.status = currentFilters.status;
      }
      
      // Add search term if not empty
      if (currentFilters.search) {
        params.search = currentFilters.search;
      }
      
      const response = await apiService.approvals.getAll(params);
      
      set({
        approvals: response.data.approvals,
        pagination: {
          ...currentPagination,
          total: response.data.total,
          totalPages: response.data.totalPages
        },
        isLoading: false
      });
      
      return response.data.approvals;
    } catch (error) {
      console.error('Error fetching approvals:', error);
      set({
        isLoading: false,
        error: error.response?.data?.message || 'Failed to fetch approvals'
      });
      return [];
    }
  },
  
  // Fetch a single approval by ID
  fetchApprovalById: async (id) => {
    try {
      set({ isLoading: true, error: null });
      
      const response = await apiService.approvals.getById(id);
      
      set({
        currentApproval: response.data,
        isLoading: false
      });
      
      return response.data;
    } catch (error) {
      console.error(`Error fetching approval ${id}:`, error);
      set({
        isLoading: false,
        error: error.response?.data?.message || 'Failed to fetch approval details'
      });
      return null;
    }
  },
  
  // Create a new approval request
  createApproval: async (approvalData) => {
    try {
      set({ isLoading: true, error: null });
      
      const response = await apiService.approvals.create(approvalData);
      
      // Update approvals list if this is a pending approval
      if (response.data.status === 'pending') {
        const approvals = [...get().approvals, response.data];
        set({
          approvals,
          currentApproval: response.data,
          isLoading: false
        });
      } else {
        set({
          currentApproval: response.data,
          isLoading: false
        });
      }
      
      return response.data;
    } catch (error) {
      console.error('Error creating approval request:', error);
      set({
        isLoading: false,
        error: error.response?.data?.message || 'Failed to create approval request'
      });
      return null;
    }
  },
  
  // Approve an approval request
  approveRequest: async (id, feedback = '') => {
    try {
      set({ isLoading: true, error: null });
      
      const response = await apiService.approvals.approve(id, feedback);
      
      // Update approvals list
      const approvals = get().approvals.filter(approval => approval.id !== id);
      
      set({
        approvals,
        currentApproval: response.data,
        isLoading: false
      });
      
      return response.data;
    } catch (error) {
      console.error(`Error approving request ${id}:`, error);
      set({
        isLoading: false,
        error: error.response?.data?.message || 'Failed to approve request'
      });
      return null;
    }
  },
  
  // Reject an approval request
  rejectRequest: async (id, feedback = '') => {
    try {
      set({ isLoading: true, error: null });
      
      const response = await apiService.approvals.reject(id, feedback);
      
      // Update approvals list
      const approvals = get().approvals.filter(approval => approval.id !== id);
      
      set({
        approvals,
        currentApproval: response.data,
        isLoading: false
      });
      
      return response.data;
    } catch (error) {
      console.error(`Error rejecting request ${id}:`, error);
      set({
        isLoading: false,
        error: error.response?.data?.message || 'Failed to reject request'
      });
      return null;
    }
  },
  
  // Get pending approval count
  getPendingCount: async () => {
    try {
      const response = await apiService.approvals.getAll({ status: 'pending', limit: 1 });
      return response.data.total;
    } catch (error) {
      console.error('Error getting pending approval count:', error);
      return 0;
    }
  },
  
  // Update filters
  setFilters: (newFilters) => {
    set({ 
      filters: { ...get().filters, ...newFilters },
      // Reset pagination when filters change
      pagination: { ...get().pagination, page: 1 }
    });
  },
  
  // Update pagination
  setPagination: (newPagination) => {
    set({ 
      pagination: { ...get().pagination, ...newPagination }
    });
  },
  
  // Clear the current approval
  clearCurrentApproval: () => {
    set({ currentApproval: null });
  },
  
  // Clear any errors
  clearError: () => set({ error: null })
}));