// SPDX-License-Identifier: MIT
// Copyright (c) 2025 Vamsi Duvvuri

// Fifth Grade Explanation:
// This file keeps track of information about how well our ads are performing.
// It collects numbers like how many people clicked on ads and how much money
// we're making, and helps show that information in charts and reports.

// High School Explanation:
// This module implements a global state store for analytics data using Zustand.
// It manages performance metrics, trend analysis, and reporting functionality,
// providing a centralized data source for analytics visualizations across the application.

import { create } from 'zustand';
import apiService from '../services/api';

export const useAnalyticsStore = create((set, get) => ({
  overview: null,
  campaignPerformance: null,
  channelPerformance: null,
  audienceInsights: null,
  isLoading: false,
  error: null,
  filters: {
    dateRange: 'last30',
    campaignId: 'all',
    channel: 'all',
    metrics: ['impressions', 'clicks', 'conversions', 'spend', 'revenue']
  },
  
  // Fetch analytics overview with filters
  fetchOverview: async (filters = null) => {
    try {
      set({ isLoading: true, error: null });
      
      // Use provided filters or current state
      const currentFilters = { ...get().filters, ...(filters || {}) };
      
      // Build params object
      const params = {
        dateRange: currentFilters.dateRange
      };
      
      // Add campaign filter if not "all"
      if (currentFilters.campaignId !== 'all') {
        params.campaignId = currentFilters.campaignId;
      }
      
      // Add channel filter if not "all"
      if (currentFilters.channel !== 'all') {
        params.channel = currentFilters.channel;
      }
      
      const response = await apiService.analytics.getOverview(params);
      
      set({
        overview: response.data,
        isLoading: false
      });
      
      return response.data;
    } catch (error) {
      console.error('Error fetching analytics overview:', error);
      set({
        isLoading: false,
        error: error.response?.data?.message || 'Failed to fetch analytics data'
      });
      return null;
    }
  },
  
  // Fetch campaign performance data
  fetchCampaignPerformance: async (campaignId, filters = null) => {
    try {
      set({ isLoading: true, error: null });
      
      // Use provided filters or current state
      const currentFilters = { ...get().filters, ...(filters || {}) };
      
      // Build params object
      const params = {
        dateRange: currentFilters.dateRange
      };
      
      const response = await apiService.analytics.getCampaignPerformance(campaignId, params);
      
      set({
        campaignPerformance: response.data,
        isLoading: false
      });
      
      return response.data;
    } catch (error) {
      console.error(`Error fetching campaign performance for ${campaignId}:`, error);
      set({
        isLoading: false,
        error: error.response?.data?.message || 'Failed to fetch campaign performance data'
      });
      return null;
    }
  },
  
  // Fetch channel performance data
  fetchChannelPerformance: async (filters = null) => {
    try {
      set({ isLoading: true, error: null });
      
      // Use provided filters or current state
      const currentFilters = { ...get().filters, ...(filters || {}) };
      
      // Build params object
      const params = {
        dateRange: currentFilters.dateRange
      };
      
      // Add campaign filter if not "all"
      if (currentFilters.campaignId !== 'all') {
        params.campaignId = currentFilters.campaignId;
      }
      
      const response = await apiService.analytics.getChannelPerformance(params);
      
      set({
        channelPerformance: response.data,
        isLoading: false
      });
      
      return response.data;
    } catch (error) {
      console.error('Error fetching channel performance:', error);
      set({
        isLoading: false,
        error: error.response?.data?.message || 'Failed to fetch channel performance data'
      });
      return null;
    }
  },
  
  // Fetch audience insights
  fetchAudienceInsights: async (filters = null) => {
    try {
      set({ isLoading: true, error: null });
      
      // Use provided filters or current state
      const currentFilters = { ...get().filters, ...(filters || {}) };
      
      // Build params object
      const params = {
        dateRange: currentFilters.dateRange
      };
      
      // Add campaign filter if not "all"
      if (currentFilters.campaignId !== 'all') {
        params.campaignId = currentFilters.campaignId;
      }
      
      const response = await apiService.analytics.getAudienceInsights(params);
      
      set({
        audienceInsights: response.data,
        isLoading: false
      });
      
      return response.data;
    } catch (error) {
      console.error('Error fetching audience insights:', error);
      set({
        isLoading: false,
        error: error.response?.data?.message || 'Failed to fetch audience insights data'
      });
      return null;
    }
  },
  
  // Export analytics report
  exportReport: async (format = 'csv', filters = null) => {
    try {
      set({ isLoading: true, error: null });
      
      // Use provided filters or current state
      const currentFilters = { ...get().filters, ...(filters || {}) };
      
      // Build params object
      const params = {
        dateRange: currentFilters.dateRange,
        format
      };
      
      // Add campaign filter if not "all"
      if (currentFilters.campaignId !== 'all') {
        params.campaignId = currentFilters.campaignId;
      }
      
      // Add channel filter if not "all"
      if (currentFilters.channel !== 'all') {
        params.channel = currentFilters.channel;
      }
      
      const response = await apiService.analytics.exportReport(params);
      
      // Create a download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `analytics_report_${new Date().toISOString().split('T')[0]}.${format}`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      set({ isLoading: false });
      return true;
    } catch (error) {
      console.error('Error exporting analytics report:', error);
      set({
        isLoading: false,
        error: error.response?.data?.message || 'Failed to export analytics report'
      });
      return false;
    }
  },
  
  // Update filters
  setFilters: (newFilters) => {
    set({ 
      filters: { ...get().filters, ...newFilters }
    });
  },
  
  // Clear any errors
  clearError: () => set({ error: null })
}));