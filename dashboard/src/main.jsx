// SPDX-License-Identifier: MIT
// Copyright (c) 2025 Vamsi Duvvuri

// Fifth Grade Explanation:
// This file starts up our dashboard website. It's like the "on" button for the 
// whole app that makes everything work together.

// High School Explanation:
// This is the main entry point for the React application. It renders the root
// App component inside the React StrictMode wrapper and sets up the router
// and global state providers that will be available throughout the application.

import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>
);