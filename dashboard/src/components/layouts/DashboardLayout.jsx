# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file creates the main frame of our dashboard - with the menu on the side,
# the header at the top, and a space in the middle for the different pages.

# High School Explanation:
# This component provides the main layout structure for all dashboard pages.
# It includes the sidebar navigation, header with user controls, and content area
# where different page components will be rendered based on the current route.

import { useState } from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../stores/authStore';

// Icons (placeholder import - replace with your icon library)
import { 
  RiDashboardLine, 
  RiCampaignLine, 
  RiCheckboxCircleLine, 
  RiLineChartLine, 
  RiSettings4Line, 
  RiMenuFoldLine, 
  RiMenuUnfoldLine,
  RiLogoutBoxLine,
  RiNotification3Line,
  RiUser3Line
} from 'react-icons/ri';

const DashboardLayout = () => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItems = [
    { 
      path: '/', 
      label: 'Dashboard', 
      icon: <RiDashboardLine className="w-5 h-5" /> 
    },
    { 
      path: '/campaigns', 
      label: 'Campaigns', 
      icon: <RiCampaignLine className="w-5 h-5" /> 
    },
    { 
      path: '/approvals', 
      label: 'Approvals', 
      icon: <RiCheckboxCircleLine className="w-5 h-5" /> 
    },
    { 
      path: '/analytics', 
      label: 'Analytics', 
      icon: <RiLineChartLine className="w-5 h-5" /> 
    },
    { 
      path: '/settings', 
      label: 'Settings', 
      icon: <RiSettings4Line className="w-5 h-5" /> 
    }
  ];

  return (
    <div className="flex h-screen bg-gray-100 dark:bg-gray-900">
      {/* Sidebar */}
      <aside 
        className={`bg-white dark:bg-gray-800 shadow-md transition-all duration-300 ${
          sidebarCollapsed ? 'w-16' : 'w-64'
        }`}
      >
        {/* Logo area */}
        <div className="h-16 flex items-center justify-between px-4 border-b dark:border-gray-700">
          {!sidebarCollapsed && (
            <div className="text-xl font-semibold dark:text-white">AI-Native</div>
          )}
          <button 
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            className="p-1 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700"
          >
            {sidebarCollapsed ? (
              <RiMenuUnfoldLine className="w-5 h-5 text-gray-600 dark:text-gray-300" />
            ) : (
              <RiMenuFoldLine className="w-5 h-5 text-gray-600 dark:text-gray-300" />
            )}
          </button>
        </div>

        {/* Navigation */}
        <nav className="py-4">
          <ul className="space-y-1">
            {navItems.map((item) => (
              <li key={item.path}>
                <NavLink
                  to={item.path}
                  className={({ isActive }) => 
                    `flex items-center py-2 px-4 ${
                      isActive 
                        ? 'bg-gray-100 dark:bg-gray-700 text-primary dark:text-white' 
                        : 'text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
                    }`
                  }
                >
                  <span className="mr-3">{item.icon}</span>
                  {!sidebarCollapsed && <span>{item.label}</span>}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>
      </aside>

      {/* Main content */}
      <div className="flex flex-col flex-1 overflow-hidden">
        {/* Header */}
        <header className="h-16 bg-white dark:bg-gray-800 shadow-sm flex items-center justify-between px-4 lg:px-6">
          <h1 className="text-xl font-semibold text-gray-800 dark:text-white">
            AI-Native Ad Agency
          </h1>
          
          <div className="flex items-center space-x-3">
            {/* Notifications */}
            <button className="p-1.5 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700 relative">
              <RiNotification3Line className="w-5 h-5 text-gray-600 dark:text-gray-300" />
              <span className="absolute top-0 right-0 w-2 h-2 bg-red-500 rounded-full"></span>
            </button>
            
            {/* User menu */}
            <div className="flex items-center">
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300 mr-2">
                {user?.name || 'User'}
              </span>
              <div className="w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-600 flex items-center justify-center">
                <RiUser3Line className="w-5 h-5 text-gray-600 dark:text-gray-300" />
              </div>
            </div>
            
            {/* Logout */}
            <button 
              onClick={handleLogout}
              className="p-1.5 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700"
            >
              <RiLogoutBoxLine className="w-5 h-5 text-gray-600 dark:text-gray-300" />
            </button>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-auto p-4 lg:p-6 bg-gray-50 dark:bg-gray-900">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default DashboardLayout;