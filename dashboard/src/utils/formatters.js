// SPDX-License-Identifier: MIT
// Copyright (c) 2025 Vamsi Duvvuri

// Fifth Grade Explanation:
// This file helps make numbers and dates look nice on the dashboard.
// It turns big numbers into easy-to-read formats, and makes dates look pretty.

// High School Explanation:
// This utility module provides standardized formatting functions for various data types
// displayed throughout the application. It ensures consistent number, currency, percentage,
// and date formatting across all dashboard components.

// Format a number with commas for thousands
export const formatNumber = (value, maximumFractionDigits = 0) => {
  if (value === null || value === undefined) return '—';
  
  return new Intl.NumberFormat('en-US', {
    maximumFractionDigits
  }).format(value);
};

// Format currency values
export const formatCurrency = (value, currencyCode = 'USD', maximumFractionDigits = 2) => {
  if (value === null || value === undefined) return '—';
  
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currencyCode,
    maximumFractionDigits
  }).format(value);
};

// Format percentages
export const formatPercentage = (value, maximumFractionDigits = 2) => {
  if (value === null || value === undefined) return '—';
  
  return new Intl.NumberFormat('en-US', {
    style: 'percent',
    maximumFractionDigits
  }).format(value / 100);
};

// Format a date
export const formatDate = (dateString, format = 'medium') => {
  if (!dateString) return '—';
  
  const date = new Date(dateString);
  
  if (isNaN(date.getTime())) return '—';
  
  const options = {
    short: { month: 'short', day: 'numeric' },
    medium: { month: 'short', day: 'numeric', year: 'numeric' },
    long: { weekday: 'short', month: 'long', day: 'numeric', year: 'numeric' },
    full: { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' }
  };
  
  return new Intl.DateTimeFormat('en-US', options[format] || options.medium).format(date);
};

// Format a timestamp as a relative time ("5 minutes ago", "2 days ago", etc.)
export const formatRelativeTime = (timestamp) => {
  if (!timestamp) return '—';
  
  const date = new Date(timestamp);
  
  if (isNaN(date.getTime())) return '—';
  
  const now = new Date();
  const diffMs = now - date;
  const diffSecs = Math.floor(diffMs / 1000);
  const diffMins = Math.floor(diffSecs / 60);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffSecs < 60) {
    return 'just now';
  } else if (diffMins < 60) {
    return `${diffMins}m ago`;
  } else if (diffHours < 24) {
    return `${diffHours}h ago`;
  } else if (diffDays < 7) {
    return `${diffDays}d ago`;
  } else {
    return formatDate(timestamp);
  }
};

// Format a large number in a readable way (K, M, B)
export const formatCompactNumber = (value) => {
  if (value === null || value === undefined) return '—';
  
  return new Intl.NumberFormat('en-US', {
    notation: 'compact',
    compactDisplay: 'short',
    maximumFractionDigits: 1
  }).format(value);
};

// Format a duration in a readable way
export const formatDuration = (seconds) => {
  if (seconds === null || seconds === undefined) return '—';
  
  if (seconds < 60) {
    return `${seconds}s`;
  } else if (seconds < 3600) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return remainingSeconds ? `${minutes}m ${remainingSeconds}s` : `${minutes}m`;
  } else {
    const hours = Math.floor(seconds / 3600);
    const remainingMinutes = Math.floor((seconds % 3600) / 60);
    return remainingMinutes ? `${hours}h ${remainingMinutes}m` : `${hours}h`;
  }
};

// Format date range for filters
export const formatDateRange = (dateRange) => {
  const today = new Date();
  
  switch (dateRange) {
    case 'today':
      return 'Today';
    case 'yesterday':
      return 'Yesterday';
    case 'last7':
      return 'Last 7 Days';
    case 'last30':
      return 'Last 30 Days';
    case 'thisMonth': {
      return `${today.toLocaleString('default', { month: 'long' })} ${today.getFullYear()}`;
    }
    case 'lastMonth': {
      const lastMonth = new Date(today.getFullYear(), today.getMonth() - 1, 1);
      return `${lastMonth.toLocaleString('default', { month: 'long' })} ${lastMonth.getFullYear()}`;
    }
    case 'thisYear':
      return `${today.getFullYear()}`;
    case 'lastYear':
      return `${today.getFullYear() - 1}`;
    case 'allTime':
      return 'All Time';
    case 'custom':
      return 'Custom Range';
    default:
      return 'Select Date Range';
  }
};