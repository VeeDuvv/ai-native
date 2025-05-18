# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file helps our website get instant updates from the server without having to
# constantly ask for them. It's like having a walkie-talkie that's always listening.

# High School Explanation:
# This module implements a WebSocket client that maintains a persistent connection
# with the server for real-time bidirectional communication. It handles connection
# management, authentication, reconnection logic, and message processing.

import { EventEmitter } from 'events';

class SocketService {
  constructor() {
    this.socket = null;
    this.isConnected = false;
    this.isConnecting = false;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectInterval = 2000; // Starting interval in ms
    this.events = new EventEmitter();
    this.apiUrl = import.meta.env.VITE_API_URL || '/api';
    this.wsUrl = this.apiUrl.replace(/^http/, 'ws').replace(/\/api$/, '/ws');
  }

  // Connect to the WebSocket server
  connect() {
    if (this.isConnected || this.isConnecting) return;
    
    this.isConnecting = true;
    const token = localStorage.getItem('auth_token');
    
    if (!token) {
      console.error('No authentication token found for WebSocket connection');
      this.isConnecting = false;
      return;
    }
    
    try {
      // Create WebSocket connection with auth token
      this.socket = new WebSocket(`${this.wsUrl}?token=${token}`);
      
      // Connection opened
      this.socket.addEventListener('open', () => {
        this.isConnected = true;
        this.isConnecting = false;
        this.reconnectAttempts = 0;
        console.log('WebSocket connection established');
        this.events.emit('connected');
      });
      
      // Listen for messages
      this.socket.addEventListener('message', (event) => {
        try {
          const data = JSON.parse(event.data);
          this.handleMessage(data);
        } catch (err) {
          console.error('Error parsing WebSocket message:', err);
        }
      });
      
      // Connection closed
      this.socket.addEventListener('close', (event) => {
        this.isConnected = false;
        this.isConnecting = false;
        console.log(`WebSocket connection closed: ${event.code} ${event.reason}`);
        this.events.emit('disconnected', event);
        
        // Attempt to reconnect unless it was a deliberate closure
        if (event.code !== 1000 && event.code !== 1001) {
          this.attemptReconnect();
        }
      });
      
      // Connection error
      this.socket.addEventListener('error', (error) => {
        console.error('WebSocket error:', error);
        this.events.emit('error', error);
      });
      
    } catch (error) {
      console.error('Error creating WebSocket connection:', error);
      this.isConnecting = false;
    }
  }
  
  // Attempt to reconnect with exponential backoff
  attemptReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Maximum WebSocket reconnection attempts reached');
      this.events.emit('reconnect_failed');
      return;
    }
    
    const delay = this.reconnectInterval * Math.pow(1.5, this.reconnectAttempts);
    this.reconnectAttempts++;
    
    console.log(`Attempting to reconnect WebSocket in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
    
    setTimeout(() => {
      this.events.emit('reconnecting', this.reconnectAttempts);
      this.connect();
    }, delay);
  }
  
  // Close the connection
  disconnect() {
    if (this.socket && (this.isConnected || this.isConnecting)) {
      this.socket.close(1000, 'Deliberate disconnection');
      this.isConnected = false;
      this.isConnecting = false;
      console.log('WebSocket disconnected');
    }
  }
  
  // Send a message to the server
  send(type, payload) {
    if (!this.isConnected) {
      console.error('Cannot send message: WebSocket not connected');
      return false;
    }
    
    try {
      const message = JSON.stringify({
        type,
        payload,
        timestamp: new Date().toISOString()
      });
      
      this.socket.send(message);
      return true;
    } catch (error) {
      console.error('Error sending WebSocket message:', error);
      return false;
    }
  }
  
  // Handle incoming messages
  handleMessage(data) {
    const { type, payload } = data;
    
    // Emit event based on message type
    this.events.emit(type, payload);
    
    // Also emit a generic 'message' event
    this.events.emit('message', data);
    
    // Handle specific system messages
    switch (type) {
      case 'auth_error':
        console.error('WebSocket authentication error:', payload.message);
        this.disconnect();
        break;
        
      case 'ping':
        // Respond to keep-alive pings
        this.send('pong', { timestamp: new Date().toISOString() });
        break;
        
      case 'reconnect':
        // Server-initiated reconnect request
        console.log('Server requested WebSocket reconnect');
        this.disconnect();
        this.connect();
        break;
    }
  }
  
  // Subscribe to events
  on(event, callback) {
    this.events.on(event, callback);
  }
  
  // Unsubscribe from events
  off(event, callback) {
    this.events.off(event, callback);
  }
  
  // Subscribe to an event once
  once(event, callback) {
    this.events.once(event, callback);
  }
}

// Create a singleton instance
const socketService = new SocketService();

export default socketService;