// SPDX-License-Identifier: MIT
// Copyright (c) 2025 Vamsi Duvvuri

// Fifth Grade Explanation:
// This file helps different parts of our website talk to each other using
// special messages that arrive instantly, instead of having to ask for updates.

// High School Explanation:
// This module creates a React Context for WebSocket functionality, making realtime
// communication available throughout the application. It manages the WebSocket connection
// lifecycle, authentication state, and provides hooks for components to subscribe to
// specific event types.

import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { useAuthStore } from '../stores/authStore';
import { useNotificationContext } from '../components/shared/NotificationProvider';
import socketService from '../services/socketService';

// Create context
const SocketContext = createContext({
  isConnected: false,
  connect: () => {},
  disconnect: () => {},
  send: () => false,
  lastMessage: null
});

// Provider component
export const SocketProvider = ({ children }) => {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState(null);
  const { isAuthenticated } = useAuthStore();
  const { info, warning, error } = useNotificationContext();
  
  // Connect to WebSocket
  const connect = useCallback(() => {
    socketService.connect();
  }, []);
  
  // Disconnect from WebSocket
  const disconnect = useCallback(() => {
    socketService.disconnect();
  }, []);
  
  // Send a message
  const send = useCallback((type, payload) => {
    return socketService.send(type, payload);
  }, []);
  
  // Handle connection events
  useEffect(() => {
    // Connection established handler
    const handleConnected = () => {
      setIsConnected(true);
    };
    
    // Disconnection handler
    const handleDisconnected = (event) => {
      setIsConnected(false);
      
      // Don't show warning for intentional disconnects
      if (event.code !== 1000 && event.code !== 1001) {
        warning('Real-time connection lost. Attempting to reconnect...');
      }
    };
    
    // Error handler
    const handleError = (err) => {
      error('WebSocket error: Unable to maintain real-time connection');
    };
    
    // Reconnecting handler
    const handleReconnecting = (attempt) => {
      info(`Reconnecting... (Attempt ${attempt})`);
    };
    
    // Failed reconnection handler
    const handleReconnectFailed = () => {
      error('Failed to reconnect. Please refresh the page to restore real-time updates.');
    };
    
    // Generic message handler
    const handleMessage = (data) => {
      setLastMessage(data);
    };
    
    // Subscribe to events
    socketService.on('connected', handleConnected);
    socketService.on('disconnected', handleDisconnected);
    socketService.on('error', handleError);
    socketService.on('reconnecting', handleReconnecting);
    socketService.on('reconnect_failed', handleReconnectFailed);
    socketService.on('message', handleMessage);
    
    // Connect if authenticated
    if (isAuthenticated) {
      connect();
    }
    
    // Cleanup on unmount
    return () => {
      socketService.off('connected', handleConnected);
      socketService.off('disconnected', handleDisconnected);
      socketService.off('error', handleError);
      socketService.off('reconnecting', handleReconnecting);
      socketService.off('reconnect_failed', handleReconnectFailed);
      socketService.off('message', handleMessage);
      
      disconnect();
    };
  }, [isAuthenticated, connect, disconnect, info, warning, error]);
  
  // Context value
  const value = {
    isConnected,
    connect,
    disconnect,
    send,
    lastMessage
  };
  
  return (
    <SocketContext.Provider value={value}>
      {children}
    </SocketContext.Provider>
  );
};

// Hook for using socket in components
export const useSocket = () => {
  const context = useContext(SocketContext);
  
  if (!context) {
    throw new Error('useSocket must be used within a SocketProvider');
  }
  
  return context;
};

// Custom hook to subscribe to specific event types
export const useSocketEvent = (eventType, callback) => {
  const { isConnected } = useSocket();
  
  useEffect(() => {
    if (!isConnected) return;
    
    socketService.on(eventType, callback);
    
    return () => {
      socketService.off(eventType, callback);
    };
  }, [eventType, callback, isConnected]);
  
  return isConnected;
};