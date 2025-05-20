// SPDX-License-Identifier: MIT
// Copyright (c) 2025 Vamsi Duvvuri

// Fifth Grade Explanation:
// This file helps show notifications to users, like pop-up messages when
// something important happens or when they need to take action on something.

// High School Explanation:
// This module implements a custom React hook for managing notifications in the application.
// It provides a standardized system for displaying success, error, warning and info messages
// with consistent styling and behavior across the entire dashboard.

import { useState, useCallback } from 'react';

// Default notification timeout in milliseconds
const DEFAULT_TIMEOUT = 5000;

const useNotification = () => {
  // Array of active notifications
  const [notifications, setNotifications] = useState([]);
  
  // Generate a unique ID for each notification
  const generateId = useCallback(() => {
    return `notification-${Date.now()}-${Math.floor(Math.random() * 1000)}`;
  }, []);
  
  // Add a new notification
  const addNotification = useCallback((message, type = 'info', timeout = DEFAULT_TIMEOUT) => {
    const id = generateId();
    
    const notification = {
      id,
      message,
      type, // 'success', 'error', 'warning', 'info'
      timestamp: Date.now()
    };
    
    setNotifications(prev => [notification, ...prev]);
    
    // Automatically remove notification after timeout
    if (timeout !== 0) {
      setTimeout(() => {
        removeNotification(id);
      }, timeout);
    }
    
    return id;
  }, [generateId]);
  
  // Shorthand methods for different notification types
  const success = useCallback((message, timeout = DEFAULT_TIMEOUT) => {
    return addNotification(message, 'success', timeout);
  }, [addNotification]);
  
  const error = useCallback((message, timeout = DEFAULT_TIMEOUT) => {
    return addNotification(message, 'error', timeout);
  }, [addNotification]);
  
  const warning = useCallback((message, timeout = DEFAULT_TIMEOUT) => {
    return addNotification(message, 'warning', timeout);
  }, [addNotification]);
  
  const info = useCallback((message, timeout = DEFAULT_TIMEOUT) => {
    return addNotification(message, 'info', timeout);
  }, [addNotification]);
  
  // Remove a notification by ID
  const removeNotification = useCallback((id) => {
    setNotifications(prev => prev.filter(notification => notification.id !== id));
  }, []);
  
  // Clear all notifications
  const clearAll = useCallback(() => {
    setNotifications([]);
  }, []);
  
  // Format and return the hook API
  return {
    notifications,
    addNotification,
    removeNotification,
    clearAll,
    success,
    error,
    warning,
    info
  };
};

export default useNotification;