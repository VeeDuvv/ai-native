// SPDX-License-Identifier: MIT
// Copyright (c) 2025 Vamsi Duvvuri

// Fifth Grade Explanation:
// This file is the starting point for our knowledge explorer dashboard. It's like
// the front door to a house that lets people in to see all the different rooms.

// High School Explanation:
// This module serves as the entry point for the TISIT dashboard components. It exports
// the main dashboard component and related utilities for integration into the main
// application, setting up necessary providers and configuration.

import React from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

// Import dashboard components
import KnowledgeDashboard from './KnowledgeDashboard';
import KnowledgeGraphViewer from './KnowledgeGraphViewer';
import CampaignKnowledgeView from './CampaignKnowledgeView';

// Create Query Client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

// Create theme
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#3f51b5',
    },
    secondary: {
      main: '#f50057',
    },
  },
});

// Standalone dashboard app
const TisitDashboardApp = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <BrowserRouter>
          <Routes>
            <Route path="/*" element={<KnowledgeDashboard />} />
          </Routes>
        </BrowserRouter>
        <ReactQueryDevtools initialIsOpen={false} />
      </ThemeProvider>
    </QueryClientProvider>
  );
};

// Mount standalone app if running directly
if (typeof window !== 'undefined' && document.getElementById('tisit-dashboard-root')) {
  const rootElement = document.getElementById('tisit-dashboard-root');
  const root = createRoot(rootElement);
  root.render(<TisitDashboardApp />);
}

// Export components for integration
export {
  KnowledgeDashboard,
  KnowledgeGraphViewer,
  CampaignKnowledgeView,
  TisitDashboardApp,
};

// Export standalone app mount function
export const mountTisitDashboard = (elementId = 'tisit-dashboard-root') => {
  const rootElement = document.getElementById(elementId);
  if (!rootElement) {
    console.error(`Element with ID "${elementId}" not found in the DOM`);
    return;
  }
  
  const root = createRoot(rootElement);
  root.render(<TisitDashboardApp />);
};