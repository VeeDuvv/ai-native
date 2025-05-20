// SPDX-License-Identifier: MIT
// Copyright (c) 2025 Vamsi Duvvuri

// Fifth Grade Explanation:
// This file creates a system that shows popup messages to users when something
// important happens, like when they successfully save something or when there's an error.

// High School Explanation:
// This component provides a global notification system using React Context.
// It renders a stack of notification alerts in the corner of the screen and
// exposes notification functions to any component in the application through
// the useNotification hook.

import React, { createContext, useContext } from 'react';
import useNotification from '../../hooks/useNotification';
import {
  RiCheckboxCircleLine,
  RiAlertLine,
  RiErrorWarningLine,
  RiInformationLine,
  RiCloseLine
} from 'react-icons/ri';

// Create the notification context
export const NotificationContext = createContext({
  notifications: [],
  addNotification: () => {},
  removeNotification: () => {},
  clearAll: () => {},
  success: () => {},
  error: () => {},
  warning: () => {},
  info: () => {}
});

// Hook for using notifications in components
export const useNotificationContext = () => {
  return useContext(NotificationContext);
};

const NotificationProvider = ({ children }) => {
  const notification = useNotification();
  
  return (
    <NotificationContext.Provider value={notification}>
      {children}
      <NotificationStack 
        notifications={notification.notifications}
        removeNotification={notification.removeNotification}
      />
    </NotificationContext.Provider>
  );
};

// Component to display a stack of notifications
const NotificationStack = ({ notifications, removeNotification }) => {
  if (notifications.length === 0) {
    return null;
  }
  
  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-2 w-80">
      {notifications.map(notification => (
        <NotificationItem 
          key={notification.id}
          notification={notification}
          onClose={() => removeNotification(notification.id)}
        />
      ))}
    </div>
  );
};

// Individual notification component
const NotificationItem = ({ notification, onClose }) => {
  const { type, message } = notification;
  
  // Type-based styling and icons
  const typeConfig = {
    success: {
      icon: RiCheckboxCircleLine,
      className: 'bg-green-50 dark:bg-green-900 border-green-200 dark:border-green-800 text-green-800 dark:text-green-200'
    },
    error: {
      icon: RiErrorWarningLine,
      className: 'bg-red-50 dark:bg-red-900 border-red-200 dark:border-red-800 text-red-800 dark:text-red-200'
    },
    warning: {
      icon: RiAlertLine,
      className: 'bg-yellow-50 dark:bg-yellow-900 border-yellow-200 dark:border-yellow-800 text-yellow-800 dark:text-yellow-200'
    },
    info: {
      icon: RiInformationLine,
      className: 'bg-blue-50 dark:bg-blue-900 border-blue-200 dark:border-blue-800 text-blue-800 dark:text-blue-200'
    }
  };
  
  const config = typeConfig[type] || typeConfig.info;
  const IconComponent = config.icon;
  
  return (
    <div 
      className={`p-4 rounded-lg border shadow-md flex items-start animate-slideIn ${config.className}`}
      role="alert"
    >
      <div className="flex-shrink-0 mr-3">
        <IconComponent className="w-5 h-5" />
      </div>
      <div className="flex-1 mr-2">
        <p className="text-sm font-medium">{message}</p>
      </div>
      <button 
        onClick={onClose}
        className="flex-shrink-0 p-1 rounded-full hover:bg-black hover:bg-opacity-10 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-black focus:ring-opacity-20"
      >
        <span className="sr-only">Close</span>
        <RiCloseLine className="w-4 h-4" />
      </button>
    </div>
  );
};

export default NotificationProvider;