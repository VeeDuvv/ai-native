// SPDX-License-Identifier: MIT
// Copyright (c) 2025 Vamsi Duvvuri

// Fifth Grade Explanation:
// This file keeps track of whether a user is logged in or not. It remembers
// information about the user across the whole app.

// High School Explanation:
// This module implements a global state store for authentication using Zustand.
// It manages the user's authentication state, login/logout operations, token storage
// and verification, and user profile data across the entire application.

import { create } from 'zustand';
import apiService from '../services/api';

export const useAuthStore = create((set, get) => ({
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,

  // Initialize auth state from stored token
  checkAuth: async () => {
    const token = localStorage.getItem('auth_token');
    
    if (!token) {
      set({ isAuthenticated: false, user: null });
      return false;
    }
    
    try {
      set({ isLoading: true });
      // Verify token with the server
      const response = await apiService.auth.verifyToken();

      if (response.data.valid) {
        set({ 
          user: response.data.user,
          isAuthenticated: true,
          isLoading: false,
          error: null
        });
        return true;
      } else {
        // Token invalid, clean up
        localStorage.removeItem('auth_token');
        localStorage.removeItem('refresh_token');
        set({ 
          isAuthenticated: false, 
          user: null,
          isLoading: false,
          error: 'Session expired'
        });
        return false;
      }
    } catch (error) {
      console.error('Authentication error:', error);
      localStorage.removeItem('auth_token');
      localStorage.removeItem('refresh_token');
      set({ 
        isAuthenticated: false, 
        user: null, 
        isLoading: false,
        error: error.response?.data?.message || 'Authentication failed'
      });
      return false;
    }
  },

  login: async (email, password) => {
    try {
      set({ isLoading: true, error: null });
      
      const response = await apiService.auth.login({ email, password });
      
      const { token, refreshToken, user } = response.data;
      
      // Store tokens
      localStorage.setItem('auth_token', token);
      if (refreshToken) {
        localStorage.setItem('refresh_token', refreshToken);
      }
      
      // Update state
      set({
        isAuthenticated: true,
        user,
        isLoading: false,
        error: null
      });
      
      return true;
    } catch (error) {
      console.error('Login error:', error);
      set({
        isLoading: false,
        error: error.response?.data?.message || 'Login failed'
      });
      return false;
    }
  },
  
  register: async (userData) => {
    try {
      set({ isLoading: true, error: null });
      
      const response = await apiService.auth.register(userData);
      
      const { token, refreshToken, user } = response.data;
      
      // Store tokens
      localStorage.setItem('auth_token', token);
      if (refreshToken) {
        localStorage.setItem('refresh_token', refreshToken);
      }
      
      // Update state
      set({
        isAuthenticated: true,
        user,
        isLoading: false,
        error: null
      });
      
      return true;
    } catch (error) {
      console.error('Registration error:', error);
      set({
        isLoading: false,
        error: error.response?.data?.message || 'Registration failed'
      });
      return false;
    }
  },
  
  logout: () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('refresh_token');
    set({
      isAuthenticated: false,
      user: null,
      error: null
    });
  },
  
  updateUserProfile: (updatedProfile) => {
    set({
      user: { ...get().user, ...updatedProfile }
    });
  },
  
  clearError: () => set({ error: null })
}));