# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file helps our website talk to the server where all our data is stored.
# It's like a messenger that knows how to ask for information and send back answers.

# High School Explanation:
# This module provides a centralized API client for communicating with the backend.
# It handles authentication headers, request formatting, response parsing, and error handling
# to provide a consistent interface for all API interactions throughout the application.

import axios from 'axios';

// Create an axios instance with default config
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request interceptor to add auth token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for global error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    
    // Handle 401 Unauthorized errors (expired token)
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      // Check if we have a refresh token
      const refreshToken = localStorage.getItem('refresh_token');
      
      if (refreshToken) {
        try {
          // Attempt to refresh the token
          const res = await axios.post(
            `${import.meta.env.VITE_API_URL || '/api'}/auth/refresh`,
            { refreshToken },
            { skipAuthRefresh: true }
          );
          
          if (res.data.token) {
            // Update tokens in storage
            localStorage.setItem('auth_token', res.data.token);
            if (res.data.refreshToken) {
              localStorage.setItem('refresh_token', res.data.refreshToken);
            }
            
            // Update the Authorization header for the original request
            api.defaults.headers.common['Authorization'] = `Bearer ${res.data.token}`;
            originalRequest.headers.Authorization = `Bearer ${res.data.token}`;
            
            // Retry the original request
            return api(originalRequest);
          }
        } catch (refreshError) {
          // If refresh fails, redirect to login
          localStorage.removeItem('auth_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
          return Promise.reject(refreshError);
        }
      } else {
        // No refresh token, redirect to login
        localStorage.removeItem('auth_token');
        window.location.href = '/login';
      }
    }
    
    // Handle other common errors
    if (error.response?.status === 403) {
      console.error('Access denied:', error.response.data.message || 'You do not have permission to access this resource');
    } else if (error.response?.status === 404) {
      console.error('Resource not found:', error.response.data.message || 'The requested resource was not found');
    } else if (error.response?.status === 500) {
      console.error('Server error:', error.response.data.message || 'An unexpected server error occurred');
    } else if (!error.response && error.request) {
      console.error('Network error:', 'Unable to connect to the server. Please check your internet connection');
    } else {
      console.error('Error:', error.message || 'An unexpected error occurred');
    }
    
    return Promise.reject(error);
  }
);

// API service object with methods for different endpoints
const apiService = {
  // Auth endpoints
  auth: {
    login: (credentials) => api.post('/auth/login', credentials),
    register: (userData) => api.post('/auth/register', userData),
    verifyToken: () => api.get('/auth/verify'),
    resetPassword: (email) => api.post('/auth/reset-password', { email }),
    updatePassword: (token, newPassword) => api.post('/auth/update-password', { token, newPassword })
  },
  
  // Dashboard
  dashboard: {
    getOverview: () => api.get('/dashboard/overview')
  },
  
  // Campaigns
  campaigns: {
    getAll: (params) => api.get('/campaigns', { params }),
    getById: (id) => api.get(`/campaigns/${id}`),
    create: (campaignData) => api.post('/campaigns', campaignData),
    update: (id, campaignData) => api.put(`/campaigns/${id}`, campaignData),
    delete: (id) => api.delete(`/campaigns/${id}`),
    getPerformance: (id) => api.get(`/campaigns/${id}/performance`)
  },
  
  // Creatives
  creatives: {
    getAll: (params) => api.get('/creatives', { params }),
    getById: (id) => api.get(`/creatives/${id}`),
    getByCampaign: (campaignId) => api.get(`/campaigns/${campaignId}/creatives`),
    create: (creativeData) => api.post('/creatives', creativeData),
    update: (id, creativeData) => api.put(`/creatives/${id}`, creativeData),
    delete: (id) => api.delete(`/creatives/${id}`)
  },
  
  // Approvals
  approvals: {
    getAll: (params) => api.get('/approvals', { params }),
    getById: (id) => api.get(`/approvals/${id}`),
    create: (approvalData) => api.post('/approvals', approvalData),
    approve: (id, feedback) => api.post(`/approvals/${id}/approve`, { feedback }),
    reject: (id, feedback) => api.post(`/approvals/${id}/reject`, { feedback })
  },
  
  // Analytics
  analytics: {
    getOverview: (params) => api.get('/analytics/overview', { params }),
    getCampaignPerformance: (campaignId, params) => api.get(`/analytics/campaigns/${campaignId}`, { params }),
    getChannelPerformance: (params) => api.get('/analytics/channels', { params }),
    getAudienceInsights: (params) => api.get('/analytics/audience', { params }),
    exportReport: (params) => api.get('/analytics/export', { params, responseType: 'blob' })
  },
  
  // User settings
  settings: {
    getProfile: () => api.get('/settings/profile'),
    updateProfile: (profileData) => api.put('/settings/profile', profileData),
    updatePassword: (passwordData) => api.put('/settings/password', passwordData),
    getNotificationPreferences: () => api.get('/settings/notifications'),
    updateNotificationPreferences: (preferences) => api.put('/settings/notifications', preferences),
    getApiAccess: () => api.get('/settings/api-access'),
    updateApiAccess: (apiAccessData) => api.put('/settings/api-access', apiAccessData),
    getDisplayPreferences: () => api.get('/settings/display'),
    updateDisplayPreferences: (preferences) => api.put('/settings/display', preferences)
  }
};

export default apiService;