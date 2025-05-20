// SPDX-License-Identifier: MIT
// Copyright (c) 2025 Vamsi Duvvuri

// Fifth Grade Explanation:
// This file creates a notification bell icon that shows you when you have new messages
// or alerts. It counts how many notifications you have and lets you click to see them.

// High School Explanation:
// This component renders a notification bell with a badge counter for unread notifications.
// It manages the notification list, mark-as-read functionality, and integrates with the
// WebSocket system to display real-time updates to the user.

import { useState, useEffect, useRef } from 'react';
import { RiNotification3Line, RiCloseLine, RiCheckLine } from 'react-icons/ri';
import { useSocketEvent } from '../../context/SocketContext';
import { formatRelativeTime } from '../../utils/formatters';

const NotificationBell = () => {
  const [notifications, setNotifications] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const dropdownRef = useRef(null);
  
  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setShowDropdown(false);
      }
    };
    
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);
  
  // Calculate unread count when notifications change
  useEffect(() => {
    const count = notifications.filter(notification => !notification.read).length;
    setUnreadCount(count);
    
    // Update document title if there are unread notifications
    if (count > 0) {
      document.title = `(${count}) AI-Native Ad Agency`;
    } else {
      document.title = 'AI-Native Ad Agency';
    }
  }, [notifications]);
  
  // Load initial notifications from localStorage or API
  useEffect(() => {
    try {
      const savedNotifications = localStorage.getItem('notifications');
      if (savedNotifications) {
        setNotifications(JSON.parse(savedNotifications));
      }
    } catch (error) {
      console.error('Error loading notifications from localStorage:', error);
    }
  }, []);
  
  // Save notifications to localStorage when they change
  useEffect(() => {
    try {
      localStorage.setItem('notifications', JSON.stringify(notifications));
    } catch (error) {
      console.error('Error saving notifications to localStorage:', error);
    }
  }, [notifications]);
  
  // Socket event handler for new notifications
  const handleNewNotification = (payload) => {
    // Generate a unique ID for the notification
    const id = `notification-${Date.now()}-${Math.floor(Math.random() * 1000)}`;
    
    // Create the notification object
    const notification = {
      id,
      title: payload.title,
      message: payload.message,
      type: payload.type || 'info',
      timestamp: payload.timestamp || new Date().toISOString(),
      read: false,
      link: payload.link
    };
    
    // Add to notifications array (limit to 50 items)
    setNotifications(prev => [notification, ...prev].slice(0, 50));
    
    // Play notification sound if enabled
    const notificationSound = document.getElementById('notification-sound');
    if (notificationSound) {
      notificationSound.play().catch(error => {
        // Autoplay may be blocked by browser policy
        console.log('Notification sound playback prevented:', error);
      });
    }
  };
  
  // Subscribe to notification events from WebSockets
  useSocketEvent('notification', handleNewNotification);
  
  // Toggle notification dropdown
  const toggleDropdown = () => {
    setShowDropdown(!showDropdown);
  };
  
  // Mark a notification as read
  const markAsRead = (id) => {
    setNotifications(prev => 
      prev.map(notification => 
        notification.id === id ? { ...notification, read: true } : notification
      )
    );
  };
  
  // Mark all notifications as read
  const markAllAsRead = () => {
    setNotifications(prev => 
      prev.map(notification => ({ ...notification, read: true }))
    );
  };
  
  // Remove a notification
  const removeNotification = (id) => {
    setNotifications(prev => 
      prev.filter(notification => notification.id !== id)
    );
  };
  
  // Clear all notifications
  const clearAllNotifications = () => {
    setNotifications([]);
  };
  
  // Get notification icon based on type
  const getNotificationIcon = (type) => {
    const iconClasses = {
      success: 'bg-green-100 text-green-600 dark:bg-green-900 dark:text-green-300',
      error: 'bg-red-100 text-red-600 dark:bg-red-900 dark:text-red-300',
      warning: 'bg-yellow-100 text-yellow-600 dark:bg-yellow-900 dark:text-yellow-300',
      info: 'bg-blue-100 text-blue-600 dark:bg-blue-900 dark:text-blue-300'
    };
    
    return iconClasses[type] || iconClasses.info;
  };
  
  return (
    <div className="relative" ref={dropdownRef}>
      {/* Hidden audio element for notification sound */}
      <audio id="notification-sound" src="/notification.mp3" preload="auto" />
      
      {/* Notification bell button */}
      <button 
        className="p-1.5 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700 relative"
        onClick={toggleDropdown}
      >
        <RiNotification3Line className="w-5 h-5 text-gray-600 dark:text-gray-300" />
        
        {/* Notification badge */}
        {unreadCount > 0 && (
          <span className="absolute top-0 right-0 flex items-center justify-center w-4 h-4 text-xs font-bold text-white bg-red-500 rounded-full">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>
      
      {/* Notification dropdown */}
      {showDropdown && (
        <div className="absolute right-0 mt-2 w-80 max-h-[30rem] overflow-y-auto bg-white dark:bg-gray-800 rounded-md shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none z-50">
          <div className="p-3 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white">Notifications</h3>
            <div className="flex gap-2">
              {unreadCount > 0 && (
                <button 
                  className="text-xs text-primary hover:text-primary-dark"
                  onClick={markAllAsRead}
                >
                  Mark all as read
                </button>
              )}
              {notifications.length > 0 && (
                <button 
                  className="text-xs text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
                  onClick={clearAllNotifications}
                >
                  Clear all
                </button>
              )}
            </div>
          </div>
          
          <div className="py-1">
            {notifications.length === 0 ? (
              <div className="px-4 py-6 text-center text-gray-500 dark:text-gray-400">
                <p>No notifications</p>
              </div>
            ) : (
              notifications.map(notification => (
                <div 
                  key={notification.id} 
                  className={`px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700 transition duration-150 ease-in-out ${!notification.read ? 'bg-gray-50 dark:bg-gray-700' : ''}`}
                >
                  <div className="flex items-start">
                    {/* Icon */}
                    <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center mr-3 ${getNotificationIcon(notification.type)}`}>
                      <RiNotification3Line className="w-4 h-4" />
                    </div>
                    
                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 dark:text-white">
                        {notification.title}
                      </p>
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        {notification.message}
                      </p>
                      <p className="mt-1 text-xs text-gray-400 dark:text-gray-500">
                        {formatRelativeTime(notification.timestamp)}
                      </p>
                      
                      {/* Action buttons */}
                      <div className="mt-2 flex space-x-2">
                        {notification.link && (
                          <a 
                            href={notification.link} 
                            className="text-xs text-primary hover:text-primary-dark"
                            onClick={() => markAsRead(notification.id)}
                          >
                            View details
                          </a>
                        )}
                        
                        {!notification.read && (
                          <button 
                            className="text-xs text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 flex items-center"
                            onClick={() => markAsRead(notification.id)}
                          >
                            <RiCheckLine className="w-3 h-3 mr-1" />
                            Mark as read
                          </button>
                        )}
                        
                        <button 
                          className="text-xs text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 flex items-center"
                          onClick={() => removeNotification(notification.id)}
                        >
                          <RiCloseLine className="w-3 h-3 mr-1" />
                          Dismiss
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default NotificationBell;