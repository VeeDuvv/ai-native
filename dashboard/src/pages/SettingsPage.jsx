// SPDX-License-Identifier: MIT
// Copyright (c) 2025 Vamsi Duvvuri

// Fifth Grade Explanation:
// This file creates a page where users can change their preferences and settings
// for the dashboard, like their password, notification preferences, and other options.

// High School Explanation:
// This component implements a settings page with user profile management,
// notification preferences, API access configuration, and dashboard customization
// options. It handles form validation and settings persistence.

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useAuthStore } from '../stores/authStore';

const API_URL = import.meta.env.VITE_API_URL || '/api';

const SettingsPage = () => {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  const [activeTab, setActiveTab] = useState('profile');
  
  // Profile form state
  const [profile, setProfile] = useState({
    name: '',
    email: '',
    company: '',
    role: '',
    phone: '',
    bio: ''
  });
  
  // Password form state
  const [passwords, setPasswords] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });
  
  // Notification settings
  const [notifications, setNotifications] = useState({
    email: {
      campaignUpdates: true,
      performanceAlerts: true,
      approvalRequests: true,
      weeklyReports: true,
      newFeatures: false
    },
    dashboard: {
      campaignUpdates: true,
      performanceAlerts: true,
      approvalRequests: true,
      teamMessages: true,
      systemNotifications: true
    }
  });
  
  // API access settings
  const [apiAccess, setApiAccess] = useState({
    enabled: false,
    apiKey: '',
    allowedEndpoints: [],
    rateLimit: 60
  });
  
  // Display preferences
  const [displayPreferences, setDisplayPreferences] = useState({
    theme: 'system',
    defaultDashboard: 'overview',
    dateFormat: 'MM/DD/YYYY',
    dataRefreshRate: 5
  });

  useEffect(() => {
    const fetchSettings = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        const token = localStorage.getItem('auth_token');
        
        if (!token) {
          throw new Error('No authentication token found');
        }
        
        // In a real app, you'd fetch these settings from the API
        // const response = await axios.get(`${API_URL}/settings`, {
        //   headers: { Authorization: `Bearer ${token}` }
        // });
        
        // For demo purposes, we'll just populate with sample data
        const demoUser = {
          id: 1,
          name: user?.name || 'John Smith',
          email: user?.email || 'john.smith@example.com',
          company: 'Acme Inc.',
          role: 'Marketing Director',
          phone: '+1 (555) 123-4567',
          bio: 'Marketing professional with 10+ years of experience in digital advertising.'
        };
        
        setProfile(demoUser);
        
        // Simulate API delay
        setTimeout(() => {
          setIsLoading(false);
        }, 500);
      } catch (err) {
        console.error('Error fetching settings:', err);
        setError('Failed to load settings. Please try again.');
        setIsLoading(false);
      }
    };
    
    fetchSettings();
  }, [user]);

  const handleProfileSubmit = async (e) => {
    e.preventDefault();
    
    try {
      setIsSaving(true);
      setError(null);
      setSuccessMessage(null);
      
      const token = localStorage.getItem('auth_token');
      
      if (!token) {
        throw new Error('No authentication token found');
      }
      
      // In a real app, this would be a real API call
      // await axios.put(`${API_URL}/settings/profile`, profile, {
      //   headers: { Authorization: `Bearer ${token}` }
      // });
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setSuccessMessage('Profile updated successfully');
    } catch (err) {
      console.error('Error updating profile:', err);
      setError('Failed to update profile. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    
    // Basic validation
    if (passwords.newPassword !== passwords.confirmPassword) {
      setError('New passwords do not match');
      return;
    }
    
    try {
      setIsSaving(true);
      setError(null);
      setSuccessMessage(null);
      
      const token = localStorage.getItem('auth_token');
      
      if (!token) {
        throw new Error('No authentication token found');
      }
      
      // In a real app, this would be a real API call
      // await axios.put(`${API_URL}/settings/password`, {
      //   currentPassword: passwords.currentPassword,
      //   newPassword: passwords.newPassword
      // }, {
      //   headers: { Authorization: `Bearer ${token}` }
      // });
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Clear password fields
      setPasswords({
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      });
      
      setSuccessMessage('Password updated successfully');
    } catch (err) {
      console.error('Error updating password:', err);
      setError('Failed to update password. Please check your current password and try again.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleNotificationsSubmit = async (e) => {
    e.preventDefault();
    
    try {
      setIsSaving(true);
      setError(null);
      setSuccessMessage(null);
      
      const token = localStorage.getItem('auth_token');
      
      if (!token) {
        throw new Error('No authentication token found');
      }
      
      // In a real app, this would be a real API call
      // await axios.put(`${API_URL}/settings/notifications`, notifications, {
      //   headers: { Authorization: `Bearer ${token}` }
      // });
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setSuccessMessage('Notification preferences updated successfully');
    } catch (err) {
      console.error('Error updating notifications:', err);
      setError('Failed to update notification preferences. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleApiAccessSubmit = async (e) => {
    e.preventDefault();
    
    try {
      setIsSaving(true);
      setError(null);
      setSuccessMessage(null);
      
      const token = localStorage.getItem('auth_token');
      
      if (!token) {
        throw new Error('No authentication token found');
      }
      
      // In a real app, this would be a real API call
      // await axios.put(`${API_URL}/settings/api-access`, apiAccess, {
      //   headers: { Authorization: `Bearer ${token}` }
      // });
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setSuccessMessage('API access settings updated successfully');
    } catch (err) {
      console.error('Error updating API access:', err);
      setError('Failed to update API access settings. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleDisplayPreferencesSubmit = async (e) => {
    e.preventDefault();
    
    try {
      setIsSaving(true);
      setError(null);
      setSuccessMessage(null);
      
      const token = localStorage.getItem('auth_token');
      
      if (!token) {
        throw new Error('No authentication token found');
      }
      
      // In a real app, this would be a real API call
      // await axios.put(`${API_URL}/settings/display-preferences`, displayPreferences, {
      //   headers: { Authorization: `Bearer ${token}` }
      // });
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setSuccessMessage('Display preferences updated successfully');
    } catch (err) {
      console.error('Error updating display preferences:', err);
      setError('Failed to update display preferences. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  // Tabs configuration
  const tabs = [
    { id: 'profile', label: 'Profile' },
    { id: 'password', label: 'Password' },
    { id: 'notifications', label: 'Notifications' },
    { id: 'api', label: 'API Access' },
    { id: 'preferences', label: 'Preferences' }
  ];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="w-10 h-10 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="mt-3 text-gray-600 dark:text-gray-400">Loading settings...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Settings</h2>
      </div>
      
      {/* Tabs navigation */}
      <div className="border-b border-gray-200 dark:border-gray-700">
        <div className="flex overflow-x-auto">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => {
                setActiveTab(tab.id);
                setError(null);
                setSuccessMessage(null);
              }}
              className={`whitespace-nowrap px-4 py-2 border-b-2 text-sm font-medium ${
                activeTab === tab.id
                  ? 'border-primary text-primary'
                  : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>
      
      {/* Success message */}
      {successMessage && (
        <div className="p-4 bg-green-50 dark:bg-green-900 border border-green-200 dark:border-green-800 rounded-md">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-green-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-green-800 dark:text-green-200">
                {successMessage}
              </p>
            </div>
          </div>
        </div>
      )}
      
      {/* Error message */}
      {error && (
        <div className="p-4 bg-red-50 dark:bg-red-900 border border-red-200 dark:border-red-800 rounded-md">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-red-800 dark:text-red-200">
                {error}
              </p>
            </div>
          </div>
        </div>
      )}
      
      {/* Tab content */}
      <div className="mt-6">
        {/* Profile Settings */}
        {activeTab === 'profile' && (
          <form onSubmit={handleProfileSubmit} className="space-y-6">
            <div className="bg-white dark:bg-gray-800 shadow sm:rounded-lg overflow-hidden">
              <div className="px-4 py-5 sm:p-6">
                <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
                  <div className="sm:col-span-3">
                    <label htmlFor="name" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      Full name
                    </label>
                    <div className="mt-1">
                      <input
                        type="text"
                        name="name"
                        id="name"
                        value={profile.name}
                        onChange={(e) => setProfile({ ...profile, name: e.target.value })}
                        className="shadow-sm focus:ring-primary focus:border-primary block w-full sm:text-sm border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md"
                      />
                    </div>
                  </div>

                  <div className="sm:col-span-3">
                    <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      Email address
                    </label>
                    <div className="mt-1">
                      <input
                        type="email"
                        name="email"
                        id="email"
                        value={profile.email}
                        onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                        className="shadow-sm focus:ring-primary focus:border-primary block w-full sm:text-sm border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md"
                      />
                    </div>
                  </div>

                  <div className="sm:col-span-3">
                    <label htmlFor="company" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      Company
                    </label>
                    <div className="mt-1">
                      <input
                        type="text"
                        name="company"
                        id="company"
                        value={profile.company}
                        onChange={(e) => setProfile({ ...profile, company: e.target.value })}
                        className="shadow-sm focus:ring-primary focus:border-primary block w-full sm:text-sm border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md"
                      />
                    </div>
                  </div>

                  <div className="sm:col-span-3">
                    <label htmlFor="role" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      Job title
                    </label>
                    <div className="mt-1">
                      <input
                        type="text"
                        name="role"
                        id="role"
                        value={profile.role}
                        onChange={(e) => setProfile({ ...profile, role: e.target.value })}
                        className="shadow-sm focus:ring-primary focus:border-primary block w-full sm:text-sm border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md"
                      />
                    </div>
                  </div>

                  <div className="sm:col-span-3">
                    <label htmlFor="phone" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      Phone number
                    </label>
                    <div className="mt-1">
                      <input
                        type="text"
                        name="phone"
                        id="phone"
                        value={profile.phone}
                        onChange={(e) => setProfile({ ...profile, phone: e.target.value })}
                        className="shadow-sm focus:ring-primary focus:border-primary block w-full sm:text-sm border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md"
                      />
                    </div>
                  </div>

                  <div className="sm:col-span-6">
                    <label htmlFor="bio" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      Bio
                    </label>
                    <div className="mt-1">
                      <textarea
                        id="bio"
                        name="bio"
                        rows={3}
                        value={profile.bio}
                        onChange={(e) => setProfile({ ...profile, bio: e.target.value })}
                        className="shadow-sm focus:ring-primary focus:border-primary block w-full sm:text-sm border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md"
                      />
                    </div>
                    <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                      Brief description about yourself and your role.
                    </p>
                  </div>
                </div>
              </div>
              
              <div className="px-4 py-3 bg-gray-50 dark:bg-gray-700 text-right sm:px-6">
                <button
                  type="submit"
                  disabled={isSaving}
                  className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary disabled:opacity-50"
                >
                  {isSaving ? 'Saving...' : 'Save'}
                </button>
              </div>
            </div>
          </form>
        )}
        
        {/* Password Settings */}
        {activeTab === 'password' && (
          <form onSubmit={handlePasswordSubmit} className="space-y-6">
            <div className="bg-white dark:bg-gray-800 shadow sm:rounded-lg overflow-hidden">
              <div className="px-4 py-5 sm:p-6">
                <div className="space-y-6">
                  <div>
                    <label htmlFor="current-password" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      Current password
                    </label>
                    <div className="mt-1">
                      <input
                        id="current-password"
                        name="current-password"
                        type="password"
                        autoComplete="current-password"
                        required
                        value={passwords.currentPassword}
                        onChange={(e) => setPasswords({ ...passwords, currentPassword: e.target.value })}
                        className="shadow-sm focus:ring-primary focus:border-primary block w-full sm:text-sm border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md"
                      />
                    </div>
                  </div>

                  <div>
                    <label htmlFor="new-password" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      New password
                    </label>
                    <div className="mt-1">
                      <input
                        id="new-password"
                        name="new-password"
                        type="password"
                        autoComplete="new-password"
                        required
                        value={passwords.newPassword}
                        onChange={(e) => setPasswords({ ...passwords, newPassword: e.target.value })}
                        className="shadow-sm focus:ring-primary focus:border-primary block w-full sm:text-sm border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md"
                      />
                    </div>
                  </div>

                  <div>
                    <label htmlFor="confirm-password" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      Confirm password
                    </label>
                    <div className="mt-1">
                      <input
                        id="confirm-password"
                        name="confirm-password"
                        type="password"
                        autoComplete="new-password"
                        required
                        value={passwords.confirmPassword}
                        onChange={(e) => setPasswords({ ...passwords, confirmPassword: e.target.value })}
                        className="shadow-sm focus:ring-primary focus:border-primary block w-full sm:text-sm border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md"
                      />
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="px-4 py-3 bg-gray-50 dark:bg-gray-700 text-right sm:px-6">
                <button
                  type="submit"
                  disabled={isSaving}
                  className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary disabled:opacity-50"
                >
                  {isSaving ? 'Updating...' : 'Update password'}
                </button>
              </div>
            </div>
          </form>
        )}
        
        {/* Notification Settings */}
        {activeTab === 'notifications' && (
          <form onSubmit={handleNotificationsSubmit} className="space-y-6">
            <div className="bg-white dark:bg-gray-800 shadow sm:rounded-lg overflow-hidden">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white">Email Notifications</h3>
                <div className="mt-4 space-y-4">
                  <div className="flex items-start">
                    <div className="flex items-center h-5">
                      <input
                        id="email-campaign-updates"
                        name="email-campaign-updates"
                        type="checkbox"
                        checked={notifications.email.campaignUpdates}
                        onChange={(e) => 
                          setNotifications({
                            ...notifications,
                            email: {
                              ...notifications.email,
                              campaignUpdates: e.target.checked
                            }
                          })
                        }
                        className="focus:ring-primary h-4 w-4 text-primary border-gray-300 dark:border-gray-600 rounded"
                      />
                    </div>
                    <div className="ml-3 text-sm">
                      <label htmlFor="email-campaign-updates" className="font-medium text-gray-700 dark:text-gray-300">
                        Campaign updates
                      </label>
                      <p className="text-gray-500 dark:text-gray-400">
                        Receive email notifications when campaigns are launched, paused, or completed.
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-start">
                    <div className="flex items-center h-5">
                      <input
                        id="email-performance-alerts"
                        name="email-performance-alerts"
                        type="checkbox"
                        checked={notifications.email.performanceAlerts}
                        onChange={(e) => 
                          setNotifications({
                            ...notifications,
                            email: {
                              ...notifications.email,
                              performanceAlerts: e.target.checked
                            }
                          })
                        }
                        className="focus:ring-primary h-4 w-4 text-primary border-gray-300 dark:border-gray-600 rounded"
                      />
                    </div>
                    <div className="ml-3 text-sm">
                      <label htmlFor="email-performance-alerts" className="font-medium text-gray-700 dark:text-gray-300">
                        Performance alerts
                      </label>
                      <p className="text-gray-500 dark:text-gray-400">
                        Get notified when campaigns exceed or fall below performance thresholds.
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-start">
                    <div className="flex items-center h-5">
                      <input
                        id="email-approval-requests"
                        name="email-approval-requests"
                        type="checkbox"
                        checked={notifications.email.approvalRequests}
                        onChange={(e) => 
                          setNotifications({
                            ...notifications,
                            email: {
                              ...notifications.email,
                              approvalRequests: e.target.checked
                            }
                          })
                        }
                        className="focus:ring-primary h-4 w-4 text-primary border-gray-300 dark:border-gray-600 rounded"
                      />
                    </div>
                    <div className="ml-3 text-sm">
                      <label htmlFor="email-approval-requests" className="font-medium text-gray-700 dark:text-gray-300">
                        Approval requests
                      </label>
                      <p className="text-gray-500 dark:text-gray-400">
                        Receive emails when campaign changes or creatives need approval.
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-start">
                    <div className="flex items-center h-5">
                      <input
                        id="email-weekly-reports"
                        name="email-weekly-reports"
                        type="checkbox"
                        checked={notifications.email.weeklyReports}
                        onChange={(e) => 
                          setNotifications({
                            ...notifications,
                            email: {
                              ...notifications.email,
                              weeklyReports: e.target.checked
                            }
                          })
                        }
                        className="focus:ring-primary h-4 w-4 text-primary border-gray-300 dark:border-gray-600 rounded"
                      />
                    </div>
                    <div className="ml-3 text-sm">
                      <label htmlFor="email-weekly-reports" className="font-medium text-gray-700 dark:text-gray-300">
                        Weekly reports
                      </label>
                      <p className="text-gray-500 dark:text-gray-400">
                        Receive weekly email summaries of campaign performance.
                      </p>
                    </div>
                  </div>
                </div>
                
                <div className="mt-8">
                  <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white">Dashboard Notifications</h3>
                  <div className="mt-4 space-y-4">
                    <div className="flex items-start">
                      <div className="flex items-center h-5">
                        <input
                          id="dashboard-campaign-updates"
                          name="dashboard-campaign-updates"
                          type="checkbox"
                          checked={notifications.dashboard.campaignUpdates}
                          onChange={(e) => 
                            setNotifications({
                              ...notifications,
                              dashboard: {
                                ...notifications.dashboard,
                                campaignUpdates: e.target.checked
                              }
                            })
                          }
                          className="focus:ring-primary h-4 w-4 text-primary border-gray-300 dark:border-gray-600 rounded"
                        />
                      </div>
                      <div className="ml-3 text-sm">
                        <label htmlFor="dashboard-campaign-updates" className="font-medium text-gray-700 dark:text-gray-300">
                          Campaign updates
                        </label>
                        <p className="text-gray-500 dark:text-gray-400">
                          Show notifications for campaign status changes.
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex items-start">
                      <div className="flex items-center h-5">
                        <input
                          id="dashboard-performance-alerts"
                          name="dashboard-performance-alerts"
                          type="checkbox"
                          checked={notifications.dashboard.performanceAlerts}
                          onChange={(e) => 
                            setNotifications({
                              ...notifications,
                              dashboard: {
                                ...notifications.dashboard,
                                performanceAlerts: e.target.checked
                              }
                            })
                          }
                          className="focus:ring-primary h-4 w-4 text-primary border-gray-300 dark:border-gray-600 rounded"
                        />
                      </div>
                      <div className="ml-3 text-sm">
                        <label htmlFor="dashboard-performance-alerts" className="font-medium text-gray-700 dark:text-gray-300">
                          Performance alerts
                        </label>
                        <p className="text-gray-500 dark:text-gray-400">
                          Display notifications for performance milestones and issues.
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="px-4 py-3 bg-gray-50 dark:bg-gray-700 text-right sm:px-6">
                <button
                  type="submit"
                  disabled={isSaving}
                  className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary disabled:opacity-50"
                >
                  {isSaving ? 'Saving...' : 'Save preferences'}
                </button>
              </div>
            </div>
          </form>
        )}
        
        {/* API Access */}
        {activeTab === 'api' && (
          <form onSubmit={handleApiAccessSubmit} className="space-y-6">
            <div className="bg-white dark:bg-gray-800 shadow sm:rounded-lg overflow-hidden">
              <div className="px-4 py-5 sm:p-6">
                <div className="flex items-start">
                  <div className="flex items-center h-5">
                    <input
                      id="api-access-enable"
                      name="api-access-enable"
                      type="checkbox"
                      checked={apiAccess.enabled}
                      onChange={(e) => 
                        setApiAccess({
                          ...apiAccess,
                          enabled: e.target.checked
                        })
                      }
                      className="focus:ring-primary h-4 w-4 text-primary border-gray-300 dark:border-gray-600 rounded"
                    />
                  </div>
                  <div className="ml-3 text-sm">
                    <label htmlFor="api-access-enable" className="font-medium text-gray-700 dark:text-gray-300">
                      Enable API access
                    </label>
                    <p className="text-gray-500 dark:text-gray-400">
                      Allow third-party applications to access campaign data through our API.
                    </p>
                  </div>
                </div>
                
                {apiAccess.enabled && (
                  <div className="mt-6 space-y-6">
                    <div>
                      <label htmlFor="api-key" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                        API Key
                      </label>
                      <div className="mt-1 flex rounded-md shadow-sm">
                        <input
                          type="text"
                          name="api-key"
                          id="api-key"
                          disabled
                          value={apiAccess.apiKey || 'sk_live_51KdsfI2EhDFGertSdfweYGSdT54'}
                          className="flex-1 min-w-0 block w-full px-3 py-2 rounded-none rounded-l-md sm:text-sm border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white bg-gray-50"
                        />
                        <button
                          type="button"
                          className="inline-flex items-center px-3 py-2 border border-gray-300 dark:border-gray-600 shadow-sm text-sm leading-4 font-medium rounded-r-md text-gray-700 dark:text-gray-300 bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
                        >
                          Copy
                        </button>
                      </div>
                    </div>
                    
                    <div>
                      <label htmlFor="rate-limit" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                        Rate limit (requests per minute)
                      </label>
                      <div className="mt-1">
                        <input
                          type="number"
                          min="1"
                          max="1000"
                          name="rate-limit"
                          id="rate-limit"
                          value={apiAccess.rateLimit}
                          onChange={(e) => 
                            setApiAccess({
                              ...apiAccess,
                              rateLimit: parseInt(e.target.value) || 60
                            })
                          }
                          className="shadow-sm focus:ring-primary focus:border-primary block w-full sm:text-sm border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md"
                        />
                      </div>
                    </div>
                    
                    <div>
                      <fieldset>
                        <legend className="text-sm font-medium text-gray-700 dark:text-gray-300">
                          Allowed endpoints
                        </legend>
                        <div className="mt-2 space-y-4">
                          <div className="flex items-start">
                            <div className="flex items-center h-5">
                              <input
                                id="endpoint-campaigns"
                                name="endpoint-campaigns"
                                type="checkbox"
                                className="focus:ring-primary h-4 w-4 text-primary border-gray-300 dark:border-gray-600 rounded"
                              />
                            </div>
                            <div className="ml-3 text-sm">
                              <label htmlFor="endpoint-campaigns" className="font-medium text-gray-700 dark:text-gray-300">
                                Campaigns
                              </label>
                              <p className="text-gray-500 dark:text-gray-400">
                                Access to campaign data and management.
                              </p>
                            </div>
                          </div>
                          
                          <div className="flex items-start">
                            <div className="flex items-center h-5">
                              <input
                                id="endpoint-analytics"
                                name="endpoint-analytics"
                                type="checkbox"
                                className="focus:ring-primary h-4 w-4 text-primary border-gray-300 dark:border-gray-600 rounded"
                              />
                            </div>
                            <div className="ml-3 text-sm">
                              <label htmlFor="endpoint-analytics" className="font-medium text-gray-700 dark:text-gray-300">
                                Analytics
                              </label>
                              <p className="text-gray-500 dark:text-gray-400">
                                Access to performance data and metrics.
                              </p>
                            </div>
                          </div>
                          
                          <div className="flex items-start">
                            <div className="flex items-center h-5">
                              <input
                                id="endpoint-creatives"
                                name="endpoint-creatives"
                                type="checkbox"
                                className="focus:ring-primary h-4 w-4 text-primary border-gray-300 dark:border-gray-600 rounded"
                              />
                            </div>
                            <div className="ml-3 text-sm">
                              <label htmlFor="endpoint-creatives" className="font-medium text-gray-700 dark:text-gray-300">
                                Creatives
                              </label>
                              <p className="text-gray-500 dark:text-gray-400">
                                Access to creative assets and management.
                              </p>
                            </div>
                          </div>
                        </div>
                      </fieldset>
                    </div>
                  </div>
                )}
              </div>
              
              <div className="px-4 py-3 bg-gray-50 dark:bg-gray-700 text-right sm:px-6">
                <button
                  type="submit"
                  disabled={isSaving}
                  className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary disabled:opacity-50"
                >
                  {isSaving ? 'Saving...' : 'Save API settings'}
                </button>
              </div>
            </div>
          </form>
        )}
        
        {/* Display Preferences */}
        {activeTab === 'preferences' && (
          <form onSubmit={handleDisplayPreferencesSubmit} className="space-y-6">
            <div className="bg-white dark:bg-gray-800 shadow sm:rounded-lg overflow-hidden">
              <div className="px-4 py-5 sm:p-6">
                <div className="space-y-6">
                  <div>
                    <label htmlFor="theme" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      Theme
                    </label>
                    <select
                      id="theme"
                      name="theme"
                      value={displayPreferences.theme}
                      onChange={(e) => 
                        setDisplayPreferences({
                          ...displayPreferences,
                          theme: e.target.value
                        })
                      }
                      className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-primary focus:border-primary sm:text-sm rounded-md"
                    >
                      <option value="light">Light</option>
                      <option value="dark">Dark</option>
                      <option value="system">System preference</option>
                    </select>
                  </div>
                  
                  <div>
                    <label htmlFor="default-dashboard" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      Default dashboard view
                    </label>
                    <select
                      id="default-dashboard"
                      name="default-dashboard"
                      value={displayPreferences.defaultDashboard}
                      onChange={(e) => 
                        setDisplayPreferences({
                          ...displayPreferences,
                          defaultDashboard: e.target.value
                        })
                      }
                      className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-primary focus:border-primary sm:text-sm rounded-md"
                    >
                      <option value="overview">Overview</option>
                      <option value="campaigns">Campaigns</option>
                      <option value="analytics">Analytics</option>
                      <option value="approvals">Approvals</option>
                    </select>
                  </div>
                  
                  <div>
                    <label htmlFor="date-format" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      Date format
                    </label>
                    <select
                      id="date-format"
                      name="date-format"
                      value={displayPreferences.dateFormat}
                      onChange={(e) => 
                        setDisplayPreferences({
                          ...displayPreferences,
                          dateFormat: e.target.value
                        })
                      }
                      className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-primary focus:border-primary sm:text-sm rounded-md"
                    >
                      <option value="MM/DD/YYYY">MM/DD/YYYY</option>
                      <option value="DD/MM/YYYY">DD/MM/YYYY</option>
                      <option value="YYYY-MM-DD">YYYY-MM-DD</option>
                    </select>
                  </div>
                  
                  <div>
                    <label htmlFor="data-refresh" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      Data refresh rate (minutes)
                    </label>
                    <select
                      id="data-refresh"
                      name="data-refresh"
                      value={displayPreferences.dataRefreshRate}
                      onChange={(e) => 
                        setDisplayPreferences({
                          ...displayPreferences,
                          dataRefreshRate: parseInt(e.target.value)
                        })
                      }
                      className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-primary focus:border-primary sm:text-sm rounded-md"
                    >
                      <option value="1">1 minute</option>
                      <option value="5">5 minutes</option>
                      <option value="15">15 minutes</option>
                      <option value="30">30 minutes</option>
                      <option value="60">1 hour</option>
                    </select>
                  </div>
                </div>
              </div>
              
              <div className="px-4 py-3 bg-gray-50 dark:bg-gray-700 text-right sm:px-6">
                <button
                  type="submit"
                  disabled={isSaving}
                  className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary disabled:opacity-50"
                >
                  {isSaving ? 'Saving...' : 'Save preferences'}
                </button>
              </div>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};

export default SettingsPage;