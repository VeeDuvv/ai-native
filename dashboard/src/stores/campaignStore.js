# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file keeps track of all the advertising campaigns in our system. It remembers
# which campaigns exist, their details, and helps other parts of the app work with them.

# High School Explanation:
# This module implements a global state store for campaign data using Zustand.
# It manages campaign listings, filtering, sorting, and CRUD operations,
# centralizing campaign data access across the application.

import { create } from 'zustand';
import apiService from '../services/api';

export const useCampaignStore = create((set, get) => ({
  campaigns: [],
  currentCampaign: null,
  isLoading: false,
  error: null,
  filters: {
    status: 'all',
    search: '',
    sort: 'recent'
  },
  pagination: {
    page: 1,
    limit: 10,
    total: 0,
    totalPages: 0
  },
  
  // Fetch all campaigns with optional filters
  fetchCampaigns: async (filters = null, pagination = null) => {
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
      
      // Add status filter if not "all"
      if (currentFilters.status !== 'all') {
        params.status = currentFilters.status;
      }
      
      // Add search term if not empty
      if (currentFilters.search) {
        params.search = currentFilters.search;
      }
      
      // Add sort parameter
      params.sort = currentFilters.sort;
      
      const response = await apiService.campaigns.getAll(params);
      
      set({
        campaigns: response.data.campaigns,
        pagination: {
          ...currentPagination,
          total: response.data.total,
          totalPages: response.data.totalPages
        },
        isLoading: false
      });
      
      return response.data.campaigns;
    } catch (error) {
      console.error('Error fetching campaigns:', error);
      set({
        isLoading: false,
        error: error.response?.data?.message || 'Failed to fetch campaigns'
      });
      return [];
    }
  },
  
  // Fetch a single campaign by ID
  fetchCampaignById: async (id) => {
    try {
      set({ isLoading: true, error: null });
      
      const response = await apiService.campaigns.getById(id);
      
      set({
        currentCampaign: response.data,
        isLoading: false
      });
      
      return response.data;
    } catch (error) {
      console.error(`Error fetching campaign ${id}:`, error);
      set({
        isLoading: false,
        error: error.response?.data?.message || 'Failed to fetch campaign details'
      });
      return null;
    }
  },
  
  // Create a new campaign
  createCampaign: async (campaignData) => {
    try {
      set({ isLoading: true, error: null });
      
      const response = await apiService.campaigns.create(campaignData);
      
      // Update campaigns list
      const campaigns = [...get().campaigns, response.data];
      set({
        campaigns,
        currentCampaign: response.data,
        isLoading: false
      });
      
      return response.data;
    } catch (error) {
      console.error('Error creating campaign:', error);
      set({
        isLoading: false,
        error: error.response?.data?.message || 'Failed to create campaign'
      });
      return null;
    }
  },
  
  // Update an existing campaign
  updateCampaign: async (id, campaignData) => {
    try {
      set({ isLoading: true, error: null });
      
      const response = await apiService.campaigns.update(id, campaignData);
      
      // Update campaigns list
      const campaigns = get().campaigns.map(campaign => 
        campaign.id === id ? response.data : campaign
      );
      
      set({
        campaigns,
        currentCampaign: response.data,
        isLoading: false
      });
      
      return response.data;
    } catch (error) {
      console.error(`Error updating campaign ${id}:`, error);
      set({
        isLoading: false,
        error: error.response?.data?.message || 'Failed to update campaign'
      });
      return null;
    }
  },
  
  // Delete a campaign
  deleteCampaign: async (id) => {
    try {
      set({ isLoading: true, error: null });
      
      await apiService.campaigns.delete(id);
      
      // Remove from campaigns list
      const campaigns = get().campaigns.filter(campaign => campaign.id !== id);
      
      set({
        campaigns,
        isLoading: false
      });
      
      // If current campaign is the deleted one, clear it
      if (get().currentCampaign?.id === id) {
        set({ currentCampaign: null });
      }
      
      return true;
    } catch (error) {
      console.error(`Error deleting campaign ${id}:`, error);
      set({
        isLoading: false,
        error: error.response?.data?.message || 'Failed to delete campaign'
      });
      return false;
    }
  },
  
  // Change campaign status
  changeCampaignStatus: async (id, status) => {
    try {
      set({ isLoading: true, error: null });
      
      const response = await apiService.campaigns.update(id, { status });
      
      // Update campaigns list
      const campaigns = get().campaigns.map(campaign => 
        campaign.id === id ? { ...campaign, status: response.data.status } : campaign
      );
      
      set({
        campaigns,
        isLoading: false
      });
      
      // If this is the current campaign, update it too
      if (get().currentCampaign?.id === id) {
        set({ 
          currentCampaign: { ...get().currentCampaign, status: response.data.status }
        });
      }
      
      return true;
    } catch (error) {
      console.error(`Error changing campaign status ${id}:`, error);
      set({
        isLoading: false,
        error: error.response?.data?.message || 'Failed to update campaign status'
      });
      return false;
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
  
  // Clear the current campaign
  clearCurrentCampaign: () => {
    set({ currentCampaign: null });
  },
  
  // Clear any errors
  clearError: () => set({ error: null })
}));