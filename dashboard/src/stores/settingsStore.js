# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file keeps track of all the settings and preferences for your dashboard.
# It remembers things like what colors you prefer, what notifications you want,
# and your personal information.

# High School Explanation:
# This module implements a global state store for user preferences and settings using Zustand.
# It manages user profile data, notification preferences, display settings, and API access
# configuration, providing a centralized settings management system.

import { create } from 'zustand';
import apiService from '../services/api';

export const useSettingsStore = create((set, get) => ({
  profile: null,
  notificationPreferences: null,
  displayPreferences: null,
  apiAccess: null,
  isLoading: false,
  error: null,
  successMessage: null,
  
  // Fetch user profile
  fetchProfile: async () => {
    try {
      set({ isLoading: true, error: null });
      
      const response = await apiService.settings.getProfile();
      
      set({
        profile: response.data,
        isLoading: false
      });
      
      return response.data;
    } catch (error) {
      console.error('Error fetching user profile:', error);
      set({
        isLoading: false,
        error: error.response?.data?.message || 'Failed to fetch user profile'
      });
      return null;
    }
  },
  
  // Update user profile
  updateProfile: async (profileData) => {
    try {
      set({ isLoading: true, error: null, successMessage: null });
      
      const response = await apiService.settings.updateProfile(profileData);
      
      set({
        profile: response.data,
        isLoading: false,
        successMessage: 'Profile updated successfully'
      });
      
      return response.data;
    } catch (error) {
      console.error('Error updating user profile:', error);
      set({
        isLoading: false,
        error: error.response?.data?.message || 'Failed to update user profile'
      });
      return null;
    }
  },
  
  // Update password
  updatePassword: async (passwordData) => {
    try {
      set({ isLoading: true, error: null, successMessage: null });
      
      await apiService.settings.updatePassword(passwordData);
      
      set({
        isLoading: false,
        successMessage: 'Password updated successfully'
      });
      
      return true;
    } catch (error) {
      console.error('Error updating password:', error);
      set({
        isLoading: false,
        error: error.response?.data?.message || 'Failed to update password'
      });
      return false;
    }
  },
  
  // Fetch notification preferences
  fetchNotificationPreferences: async () => {
    try {
      set({ isLoading: true, error: null });
      
      const response = await apiService.settings.getNotificationPreferences();
      
      set({
        notificationPreferences: response.data,
        isLoading: false
      });
      
      return response.data;
    } catch (error) {
      console.error('Error fetching notification preferences:', error);
      set({
        isLoading: false,
        error: error.response?.data?.message || 'Failed to fetch notification preferences'
      });
      return null;
    }
  },
  
  // Update notification preferences
  updateNotificationPreferences: async (preferences) => {
    try {
      set({ isLoading: true, error: null, successMessage: null });
      
      const response = await apiService.settings.updateNotificationPreferences(preferences);
      
      set({
        notificationPreferences: response.data,
        isLoading: false,
        successMessage: 'Notification preferences updated successfully'
      });
      
      return response.data;
    } catch (error) {
      console.error('Error updating notification preferences:', error);
      set({
        isLoading: false,
        error: error.response?.data?.message || 'Failed to update notification preferences'
      });
      return null;
    }
  },
  
  // Fetch API access settings
  fetchApiAccess: async () => {
    try {
      set({ isLoading: true, error: null });
      
      const response = await apiService.settings.getApiAccess();
      
      set({
        apiAccess: response.data,
        isLoading: false
      });
      
      return response.data;
    } catch (error) {
      console.error('Error fetching API access settings:', error);
      set({
        isLoading: false,
        error: error.response?.data?.message || 'Failed to fetch API access settings'
      });
      return null;
    }
  },
  
  // Update API access settings
  updateApiAccess: async (apiAccessData) => {
    try {
      set({ isLoading: true, error: null, successMessage: null });
      
      const response = await apiService.settings.updateApiAccess(apiAccessData);
      
      set({
        apiAccess: response.data,
        isLoading: false,
        successMessage: 'API access settings updated successfully'
      });
      
      return response.data;
    } catch (error) {
      console.error('Error updating API access settings:', error);
      set({
        isLoading: false,
        error: error.response?.data?.message || 'Failed to update API access settings'
      });
      return null;
    }
  },
  
  // Fetch display preferences
  fetchDisplayPreferences: async () => {
    try {
      set({ isLoading: true, error: null });
      
      const response = await apiService.settings.getDisplayPreferences();
      
      set({
        displayPreferences: response.data,
        isLoading: false
      });
      
      return response.data;
    } catch (error) {
      console.error('Error fetching display preferences:', error);
      set({
        isLoading: false,
        error: error.response?.data?.message || 'Failed to fetch display preferences'
      });
      return null;
    }
  },
  
  // Update display preferences
  updateDisplayPreferences: async (preferences) => {
    try {
      set({ isLoading: true, error: null, successMessage: null });
      
      const response = await apiService.settings.updateDisplayPreferences(preferences);
      
      set({
        displayPreferences: response.data,
        isLoading: false,
        successMessage: 'Display preferences updated successfully'
      });
      
      // Apply theme preference
      if (preferences.theme) {
        if (preferences.theme === 'dark') {
          document.documentElement.classList.add('dark');
        } else if (preferences.theme === 'light') {
          document.documentElement.classList.remove('dark');
        } else if (preferences.theme === 'system') {
          const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
          if (prefersDark) {
            document.documentElement.classList.add('dark');
          } else {
            document.documentElement.classList.remove('dark');
          }
        }
      }
      
      return response.data;
    } catch (error) {
      console.error('Error updating display preferences:', error);
      set({
        isLoading: false,
        error: error.response?.data?.message || 'Failed to update display preferences'
      });
      return null;
    }
  },
  
  // Initialize settings on app load
  initializeSettings: async () => {
    try {
      // Load display preferences first to set theme quickly
      const displayPrefs = await get().fetchDisplayPreferences();
      
      // Apply theme preference
      if (displayPrefs?.theme) {
        if (displayPrefs.theme === 'dark') {
          document.documentElement.classList.add('dark');
        } else if (displayPrefs.theme === 'light') {
          document.documentElement.classList.remove('dark');
        } else if (displayPrefs.theme === 'system') {
          const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
          if (prefersDark) {
            document.documentElement.classList.add('dark');
          } else {
            document.documentElement.classList.remove('dark');
          }
        }
      }
      
      // Load other settings in parallel
      await Promise.all([
        get().fetchProfile(),
        get().fetchNotificationPreferences(),
        get().fetchApiAccess()
      ]);
      
      return true;
    } catch (error) {
      console.error('Error initializing settings:', error);
      return false;
    }
  },
  
  // Clear success message
  clearSuccessMessage: () => set({ successMessage: null }),
  
  // Clear error message
  clearError: () => set({ error: null })
}));