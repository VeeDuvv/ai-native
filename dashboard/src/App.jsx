// SPDX-License-Identifier: MIT
// Copyright (c) 2025 Vamsi Duvvuri

import React, { useState } from 'react';
import SubwayMap from './components/SubwayMap';
import { workflowLines, agents, activeCampaigns } from './data/workflows';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('map');
  const [activeCampaignCount, setActiveCampaignCount] = useState(activeCampaigns.length);
  const [agentCount, setAgentCount] = useState(agents.length);

  // Stats for dashboard
  const frontOfficeCount = agents.filter(a => a.filter === 'front').length;
  const middleOfficeCount = agents.filter(a => a.filter === 'middle').length;
  const backOfficeCount = agents.filter(a => a.filter === 'back').length;
  const executiveCount = agents.filter(a => a.filter === 'executive').length;

  // Calculate progress across all campaigns
  const averageProgress = Math.round(
    activeCampaigns.reduce((sum, campaign) => sum + campaign.progress, 0) / 
    activeCampaigns.length
  );

  // Count campaigns by status
  const campaignsByStatus = {
    'on-time': activeCampaigns.filter(c => c.status === 'on-time').length,
    'delayed': activeCampaigns.filter(c => c.status === 'delayed').length,
    'expedited': activeCampaigns.filter(c => c.status === 'expedited').length,
    'paused': activeCampaigns.filter(c => c.status === 'paused').length,
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Koya Command Center</h1>
        <div className="header-controls">
          <div className="time-display">
            {new Date().toLocaleDateString()} | {new Date().toLocaleTimeString()}
          </div>
          <div className="user-controls">
            <span className="user-name">Vee (CEO)</span>
            <div className="user-avatar"></div>
          </div>
        </div>
      </header>

      <nav className="main-nav">
        <ul>
          <li className={activeTab === 'map' ? 'active' : ''} onClick={() => setActiveTab('map')}>
            Workflow Map
          </li>
          <li className={activeTab === 'campaigns' ? 'active' : ''} onClick={() => setActiveTab('campaigns')}>
            Campaigns
          </li>
          <li className={activeTab === 'agents' ? 'active' : ''} onClick={() => setActiveTab('agents')}>
            Agents
          </li>
          <li className={activeTab === 'analytics' ? 'active' : ''} onClick={() => setActiveTab('analytics')}>
            Analytics
          </li>
        </ul>
      </nav>

      <main className="App-main">
        {activeTab === 'map' && (
          <>
            <div className="dashboard-stats">
              <div className="stat-card">
                <div className="stat-value">{activeCampaignCount}</div>
                <div className="stat-label">Active Campaigns</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{averageProgress}%</div>
                <div className="stat-label">Average Progress</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{campaignsByStatus['on-time']}</div>
                <div className="stat-label">On-time Campaigns</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{campaignsByStatus['delayed']}</div>
                <div className="stat-label">Delayed Campaigns</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{agentCount}</div>
                <div className="stat-label">Active Agents</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{workflowLines.length}</div>
                <div className="stat-label">Workflow Types</div>
              </div>
            </div>
            <div className="map-container">
              <SubwayMap />
            </div>
            <div className="dashboard-footer">
              <div className="system-status">System Status: <span className="status-normal">Normal</span></div>
              <div className="update-time">Last updated: {new Date().toLocaleTimeString()}</div>
            </div>
          </>
        )}

        {activeTab === 'campaigns' && (
          <div className="coming-soon">
            <h2>Campaigns View</h2>
            <p>Detailed campaign management coming soon.</p>
          </div>
        )}

        {activeTab === 'agents' && (
          <div className="coming-soon">
            <h2>Agents View</h2>
            <p>Agent management and monitoring coming soon.</p>
          </div>
        )}

        {activeTab === 'analytics' && (
          <div className="coming-soon">
            <h2>Analytics</h2>
            <p>Advanced analytics and reporting coming soon.</p>
          </div>
        )}
      </main>

      <footer className="App-footer">
        <div>&copy; 2025 Koya AI-Native Agency</div>
        <div>Version 0.1.0</div>
      </footer>
    </div>
  );
}

export default App;