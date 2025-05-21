# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Koya Workflow Subway Map: Technical Implementation Guide

## Fifth Grade Explanation:
This document explains how we'll build our digital subway map that shows our AI helpers working together. It describes the code and tools we'll use to make the map interactive and show real-time information.

## High School Explanation:
This technical guide outlines the implementation approach for Koya's workflow subway map visualization, including front-end technologies, data structures, API design, and integration points. It provides developers with a blueprint for building an interactive, real-time visualization of agent workflows and campaign progression.

## Overview

This document provides the technical specifications and implementation guidance for building the Koya Workflow Subway Map visualization as part of our agency's internal dashboard. It translates the conceptual design into actionable development requirements, covering front-end technologies, data architecture, API design, and integration patterns.

## Technology Stack

### Front-End Technologies

#### Core Framework
- **React.js**: Primary front-end library for component-based UI development
- **TypeScript**: For type safety and enhanced developer experience
- **Redux**: State management for complex application data
- **React Router**: Navigation management for different dashboard views

#### Visualization Libraries
- **D3.js**: Core data visualization library for custom subway map rendering
- **React-Force-Graph**: Network visualization for agent relationship views
- **Framer Motion**: Advanced animations for fluid transitions and effects
- **react-vis**: Complementary charts and graphs for metrics displays

#### UI Component Framework
- **Material-UI**: Base component library for dashboard UI elements
- **Styled Components**: CSS-in-JS styling solution for custom components
- **react-grid-layout**: Draggable and resizable grid for dashboard customization
- **nivo**: Data visualization components for supplementary charts

#### Real-Time Capabilities
- **Socket.IO**: WebSocket implementation for live data updates
- **RxJS**: Reactive programming library for handling real-time data streams
- **React Query**: Data fetching, caching, and state synchronization

### Back-End Technologies

#### API Layer
- **Node.js**: Runtime environment for API services
- **Express**: Web framework for REST API endpoints
- **GraphQL**: Query language for flexible data fetching
- **Apollo Server**: GraphQL implementation

#### Data Processing
- **Redis**: In-memory data store for real-time state management
- **Apache Kafka**: Event streaming platform for workflow events
- **Elasticsearch**: Search and analytics engine for historical data
- **Node-RED**: Flow-based programming for workflow orchestration visualization

#### Persistence
- **MongoDB**: NoSQL database for workflow and campaign data
- **TimescaleDB**: Time-series database for performance metrics
- **Neo4j**: Graph database for agent relationships and workflow paths

## Technical Architecture

### 1. Data Model

#### Core Entities

**Agent**
```typescript
interface Agent {
  id: string;
  name: string;
  role: string;
  office: 'front' | 'middle' | 'back' | 'executive';
  icon: string;
  position: {
    x: number;
    y: number;
  };
  status: 'available' | 'busy' | 'overloaded' | 'offline';
  capacity: {
    current: number;
    maximum: number;
  };
  metrics: {
    averageHandlingTime: number;
    qualityScore: number;
    onTimeDelivery: number;
  };
}
```

**WorkflowLine**
```typescript
interface WorkflowLine {
  id: string;
  name: string;
  type: 'brand' | 'digital' | 'content' | 'social' | 'analytics' | 'client';
  color: string;
  stations: string[]; // Agent IDs in sequence
  branches?: {
    condition: string;
    stationId: string;
    targetStations: string[];
  }[];
  metrics: {
    averageCompletionTime: number;
    activeWorkflows: number;
    throughput: number;
  };
}
```

**Campaign**
```typescript
interface Campaign {
  id: string;
  name: string;
  clientId: string;
  type: string;
  priority: 1 | 2 | 3 | 4 | 5;
  lineId: string;
  currentStationId: string;
  previousStations: {
    stationId: string;
    enteredAt: string;
    exitedAt: string;
    duration: number;
  }[];
  nextStationId: string;
  status: 'on-time' | 'delayed' | 'expedited' | 'paused';
  progress: number; // 0-100%
  startedAt: string;
  estimatedCompletion: string;
  actualPath: string[]; // Actual sequence of stations
}
```

**Handoff**
```typescript
interface Handoff {
  id: string;
  campaignId: string;
  sourceAgentId: string;
  targetAgentId: string;
  status: 'pending' | 'in-transit' | 'delivered' | 'accepted' | 'rejected';
  priority: number;
  createdAt: string;
  deliveredAt?: string;
  acceptedAt?: string;
  artifacts: {
    id: string;
    type: string;
    name: string;
    url: string;
  }[];
  notes: string;
}
```

**Station** (UI Representation)
```typescript
interface Station {
  id: string; // Same as Agent ID
  name: string;
  type: 'agent' | 'decision' | 'gateway' | 'integration' | 'terminal';
  position: {
    x: number;
    y: number;
  };
  connections: {
    targetStationId: string;
    lineId: string;
    direction: 'outbound' | 'inbound' | 'bidirectional';
    pathPoints: [number, number][]; // Bezier curve control points
  }[];
  size: number; // Relative size for visualization
  active: boolean;
  queue: number; // Number of waiting items
}
```

**Connection** (UI Representation)
```typescript
interface Connection {
  id: string;
  sourceStationId: string;
  targetStationId: string;
  lineId: string;
  pathType: 'direct' | 'curved' | 'angled';
  pathPoints: [number, number][]; // Control points for path drawing
  active: boolean;
  trafficVolume: number; // Current volume of traffic
  activeHandoffs: string[]; // Handoff IDs currently in transit
}
```

### 2. API Design

#### REST Endpoints

**Agent API**
```
GET /api/agents - List all agents
GET /api/agents/:id - Get agent details
GET /api/agents/:id/status - Get current agent status
GET /api/agents/:id/metrics - Get agent performance metrics
GET /api/agents/:id/campaigns - Get campaigns at this agent
```

**Workflow API**
```
GET /api/workflows - List all workflow types
GET /api/workflows/:id - Get workflow details
GET /api/workflows/:id/lines - Get lines for this workflow
GET /api/workflows/:id/metrics - Get workflow performance metrics
```

**Campaign API**
```
GET /api/campaigns - List active campaigns
GET /api/campaigns/:id - Get campaign details
GET /api/campaigns/:id/history - Get campaign journey history
GET /api/campaigns/:id/timeline - Get projected timeline
PUT /api/campaigns/:id/priority - Update campaign priority
```

**Handoff API**
```
GET /api/handoffs - List recent handoffs
GET /api/handoffs/:id - Get handoff details
GET /api/handoffs/active - Get currently active handoffs
GET /api/handoffs/agent/:agentId - Get handoffs for an agent
```

**Map API**
```
GET /api/map/layout - Get subway map layout data
GET /api/map/status - Get current system status
GET /api/map/hotspots - Get current activity hotspots
GET /api/map/metrics - Get map-wide performance metrics
```

#### GraphQL Schema (Partial)

```graphql
type Agent {
  id: ID!
  name: String!
  role: String!
  office: Office!
  status: AgentStatus!
  capacity: Capacity!
  metrics: AgentMetrics!
  currentCampaigns: [Campaign!]!
  incomingHandoffs: [Handoff!]!
  outgoingHandoffs: [Handoff!]!
}

type WorkflowLine {
  id: ID!
  name: String!
  type: LineType!
  color: String!
  stations: [Agent!]!
  branches: [Branch!]
  metrics: LineMetrics!
  activeCampaigns: [Campaign!]!
}

type Campaign {
  id: ID!
  name: String!
  client: Client!
  type: String!
  priority: Int!
  line: WorkflowLine!
  currentStation: Agent
  journey: [StationVisit!]!
  status: CampaignStatus!
  progress: Float!
  timeline: Timeline!
  handoffs: [Handoff!]!
}

type Query {
  agent(id: ID!): Agent
  agents(office: Office, status: AgentStatus): [Agent!]!
  workflowLine(id: ID!): WorkflowLine
  workflowLines(type: LineType): [WorkflowLine!]!
  campaign(id: ID!): Campaign
  activeCampaigns(clientId: ID, priority: Int): [Campaign!]!
  handoffs(status: HandoffStatus): [Handoff!]!
  mapStatus: MapStatus!
}

type Subscription {
  agentStatusChanged: Agent!
  newHandoff: Handoff!
  campaignMoved: Campaign!
  systemAlert: Alert!
}
```

#### WebSocket Events

```typescript
// Agent events
const AGENT_STATUS_CHANGED = 'agent:status:changed';
const AGENT_CAPACITY_UPDATED = 'agent:capacity:updated';
const AGENT_METRICS_UPDATED = 'agent:metrics:updated';

// Campaign events
const CAMPAIGN_STATION_CHANGED = 'campaign:station:changed';
const CAMPAIGN_PROGRESS_UPDATED = 'campaign:progress:updated';
const CAMPAIGN_STATUS_CHANGED = 'campaign:status:changed';
const CAMPAIGN_CREATED = 'campaign:created';
const CAMPAIGN_COMPLETED = 'campaign:completed';

// Handoff events
const HANDOFF_CREATED = 'handoff:created';
const HANDOFF_STATUS_CHANGED = 'handoff:status:changed';
const HANDOFF_DELIVERED = 'handoff:delivered';
const HANDOFF_ACCEPTED = 'handoff:accepted';
const HANDOFF_REJECTED = 'handoff:rejected';

// System events
const SYSTEM_ALERT = 'system:alert';
const BOTTLENECK_DETECTED = 'system:bottleneck:detected';
const PERFORMANCE_THRESHOLD_CROSSED = 'system:performance:threshold';
```

### 3. Front-End Implementation

#### Component Hierarchy

```
SubwayMapDashboard
├── MapControlPanel
│   ├── ViewControls
│   ├── FilterControls
│   └── SearchBox
├── SubwayMap
│   ├── MapCanvas
│   │   ├── LineLayer
│   │   ├── StationLayer
│   │   ├── ConnectionLayer
│   │   ├── CampaignLayer
│   │   └── AnnotationLayer
│   ├── Legend
│   └── MiniMap
├── DetailPanel
│   ├── AgentDetail
│   ├── LineDetail
│   ├── CampaignDetail
│   └── SystemStatusDetail
├── TimelineControls
│   ├── TimeRangeSelector
│   ├── PlaybackControls
│   └── TimeIndicator
└── AlertPanel
    ├── AlertList
    └── AlertDetail
```

#### Key Component Implementation (Example)

**SubwayMap Component**
```jsx
import React, { useEffect, useRef, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import * as d3 from 'd3';
import { motion } from 'framer-motion';
import { LineLayer } from './LineLayer';
import { StationLayer } from './StationLayer';
import { ConnectionLayer } from './ConnectionLayer';
import { CampaignLayer } from './CampaignLayer';
import { AnnotationLayer } from './AnnotationLayer';
import { zoomToFeature, highlightElement } from '../actions/mapActions';
import { useMapData, useRealTimeUpdates } from '../hooks';

const SubwayMap = ({ width, height, filters }) => {
  const svgRef = useRef(null);
  const mapData = useMapData(filters);
  const dispatch = useDispatch();
  const selectedElement = useSelector(state => state.map.selectedElement);
  const [transform, setTransform] = useState({ x: 0, y: 0, k: 1 });

  // Set up D3 zoom behavior
  useEffect(() => {
    if (!svgRef.current) return;
    
    const svg = d3.select(svgRef.current);
    const zoom = d3.zoom()
      .scaleExtent([0.5, 5])
      .on('zoom', (event) => {
        setTransform(event.transform);
      });
      
    svg.call(zoom);
    
    // Reset if needed
    return () => svg.on('.zoom', null);
  }, [svgRef]);
  
  // Subscribe to real-time updates
  useRealTimeUpdates(mapData.timestamp);
  
  // Highlight selected element
  useEffect(() => {
    if (selectedElement) {
      dispatch(highlightElement(selectedElement.id, selectedElement.type));
    }
  }, [selectedElement, dispatch]);
  
  return (
    <div className="subway-map-container">
      <svg 
        ref={svgRef}
        width={width} 
        height={height}
        className="subway-map"
      >
        <motion.g
          animate={{
            x: transform.x,
            y: transform.y,
            scale: transform.k
          }}
        >
          <LineLayer lines={mapData.lines} />
          <ConnectionLayer connections={mapData.connections} />
          <StationLayer 
            stations={mapData.stations}
            onStationClick={(station) => dispatch(zoomToFeature(station.id, 'station'))}
          />
          <CampaignLayer 
            campaigns={mapData.activeCampaigns}
            connections={mapData.connections}
          />
          <AnnotationLayer annotations={mapData.annotations} />
        </motion.g>
      </svg>
      {/* Additional overlay elements */}
    </div>
  );
};

export default SubwayMap;
```

**StationLayer Component**
```jsx
import React, { useMemo } from 'react';
import { motion } from 'framer-motion';
import { useSelector } from 'react-redux';

export const StationLayer = ({ stations, onStationClick }) => {
  const highlightedStations = useSelector(state => state.map.highlightedStations);
  const hoveredStation = useSelector(state => state.map.hoveredStation);
  
  // Memoize to prevent unnecessary re-renders
  const stationElements = useMemo(() => {
    return stations.map(station => {
      const isHighlighted = highlightedStations.includes(station.id);
      const isHovered = hoveredStation === station.id;
      
      // Determine visual properties based on station attributes
      const size = station.size * (isHighlighted ? 1.5 : 1);
      const strokeWidth = isHighlighted || isHovered ? 3 : 1;
      const fillOpacity = station.active ? 1 : 0.6;
      
      return (
        <motion.g
          key={station.id}
          initial={{ opacity: 0, scale: 0 }}
          animate={{ 
            opacity: 1, 
            scale: 1,
            x: station.position.x,
            y: station.position.y
          }}
          whileHover={{ scale: 1.1 }}
          onClick={() => onStationClick(station)}
          className={`station station-${station.type}`}
          data-testid={`station-${station.id}`}
        >
          {/* Station background */}
          <circle
            r={size}
            fill={getStationColor(station)}
            stroke="#ffffff"
            strokeWidth={strokeWidth}
            opacity={fillOpacity}
          />
          
          {/* Station icon */}
          <image
            href={station.icon}
            x={-size/2}
            y={-size/2}
            width={size}
            height={size}
            opacity={station.active ? 1 : 0.7}
          />
          
          {/* Station label */}
          <text
            dy={size + 12}
            textAnchor="middle"
            className="station-label"
            fontSize={isHighlighted ? 14 : 12}
            fontWeight={isHighlighted ? 'bold' : 'normal'}
          >
            {station.name}
          </text>
          
          {/* Queue indicator if items are waiting */}
          {station.queue > 0 && (
            <circle
              r={size/3}
              cx={size * 0.7}
              cy={-size * 0.7}
              fill="#ff5722"
              className="queue-indicator"
            >
              <title>{station.queue} items in queue</title>
            </circle>
          )}
        </motion.g>
      );
    });
  }, [stations, highlightedStations, hoveredStation, onStationClick]);
  
  return <g className="stations-layer">{stationElements}</g>;
};

// Helper function to determine station color based on properties
const getStationColor = (station) => {
  if (!station.active) return '#cccccc';
  
  // Color by office
  const officeColors = {
    front: '#2196f3',  // Blue
    middle: '#4caf50', // Green
    back: '#ff9800',   // Orange
    executive: '#9c27b0' // Purple
  };
  
  // Modify based on status
  switch (station.status) {
    case 'overloaded': return '#f44336'; // Red
    case 'busy': return '#ffc107';      // Amber
    default: return officeColors[station.office];
  }
};
```

**CampaignLayer Component (Animation Logic)**
```jsx
import React, { useEffect, useState } from 'react';
import { motion, useAnimation } from 'framer-motion';
import { useSelector } from 'react-redux';
import { findPathBetweenStations } from '../utils/pathFinding';

export const CampaignLayer = ({ campaigns, connections }) => {
  const selectedCampaign = useSelector(state => state.map.selectedCampaign);
  
  return (
    <g className="campaigns-layer">
      {campaigns.map(campaign => (
        <CampaignTrain
          key={campaign.id}
          campaign={campaign}
          connections={connections}
          isSelected={selectedCampaign === campaign.id}
        />
      ))}
    </g>
  );
};

const CampaignTrain = ({ campaign, connections, isSelected }) => {
  const controls = useAnimation();
  const [currentPosition, setCurrentPosition] = useState({ x: 0, y: 0 });
  
  // Find the path for this campaign between current and next station
  useEffect(() => {
    if (!campaign.currentStationId || !campaign.nextStationId) return;
    
    const path = findPathBetweenStations(
      campaign.currentStationId,
      campaign.nextStationId,
      connections
    );
    
    if (path && path.pathPoints && path.pathPoints.length > 0) {
      // Animate along the path
      const animate = async () => {
        // Create keyframes along the Bezier curve
        const keyframes = createKeyframesAlongPath(path.pathPoints, 20);
        
        // Determine duration based on priority and status
        const duration = calculateDuration(campaign);
        
        // Animate through each point
        for (let i = 0; i < keyframes.length; i++) {
          const point = keyframes[i];
          await controls.start({
            x: point[0],
            y: point[1],
            transition: { 
              duration: duration / keyframes.length,
              ease: "linear"
            }
          });
          setCurrentPosition({ x: point[0], y: point[1] });
        }
      };
      
      animate();
    }
  }, [campaign.currentStationId, campaign.nextStationId, campaign.progress, controls, connections]);
  
  // Train appearance based on campaign properties
  const size = isSelected ? 10 : 8;
  const campaignTypeColors = {
    brand: '#e91e63',    // Pink
    digital: '#2196f3',  // Blue
    content: '#4caf50',  // Green
    social: '#ff9800',   // Orange
    analytics: '#9c27b0' // Purple
  };
  const color = campaignTypeColors[campaign.type] || '#757575';
  
  return (
    <motion.g
      animate={controls}
      className={`campaign-train priority-${campaign.priority}`}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      whileHover={{ scale: 1.2 }}
    >
      {/* Campaign vehicle */}
      <rect
        x={-size/2}
        y={-size/2}
        width={size}
        height={size}
        rx={2}
        fill={color}
        stroke={isSelected ? '#ffffff' : 'none'}
        strokeWidth={2}
        className="campaign-vehicle"
      />
      
      {/* Priority indicator */}
      {campaign.priority <= 2 && (
        <circle
          cx={size/2}
          cy={-size/2}
          r={size/4}
          fill={campaign.priority === 1 ? '#f44336' : '#ff9800'}
          className="priority-indicator"
        />
      )}
      
      {/* Campaign label (shown when selected) */}
      {isSelected && (
        <text
          dy={-size - 5}
          textAnchor="middle"
          fill="#ffffff"
          stroke="#000000"
          strokeWidth={3}
          paintOrder="stroke"
          className="campaign-label"
          fontSize={12}
        >
          {campaign.name}
        </text>
      )}
      
      {/* Progress indicator */}
      {isSelected && (
        <rect
          x={-size}
          y={size}
          width={size * 2}
          height={2}
          fill="#dddddd"
          className="progress-track"
        >
          <rect
            width={size * 2 * (campaign.progress / 100)}
            height={2}
            fill={getStatusColor(campaign.status)}
            className="progress-indicator"
          />
        </rect>
      )}
    </motion.g>
  );
};

// Helper functions
const createKeyframesAlongPath = (pathPoints, numPoints) => {
  // Create points along a Bezier curve
  // Implementation depends on path representation
  // This is a simplified example
  return Array.from({ length: numPoints }, (_, i) => {
    const t = i / (numPoints - 1);
    // For a cubic Bezier curve with points p0, p1, p2, p3
    // This would calculate the point at parameter t
    // This is just placeholder logic
    return [
      /* x coordinate calculation */,
      /* y coordinate calculation */
    ];
  });
};

const calculateDuration = (campaign) => {
  // Base duration for animation
  let duration = 10; // seconds
  
  // Adjust based on priority
  if (campaign.priority === 1) duration *= 0.6;
  else if (campaign.priority === 2) duration *= 0.8;
  else if (campaign.priority === 4) duration *= 1.2;
  else if (campaign.priority === 5) duration *= 1.5;
  
  // Adjust based on status
  if (campaign.status === 'expedited') duration *= 0.7;
  else if (campaign.status === 'delayed') duration *= 1.5;
  
  return duration;
};

const getStatusColor = (status) => {
  switch (status) {
    case 'on-time': return '#4caf50';  // Green
    case 'delayed': return '#f44336';  // Red
    case 'expedited': return '#2196f3'; // Blue
    case 'paused': return '#ff9800';   // Orange
    default: return '#757575';         // Grey
  }
};
```

### 4. State Management

#### Redux Store Structure

```typescript
interface RootState {
  map: {
    layout: {
      stations: Station[];
      connections: Connection[];
      lines: WorkflowLine[];
    };
    viewport: {
      zoom: number;
      center: [number, number];
      bounds: [number, number, number, number];
    };
    selection: {
      selectedElement: {
        id: string;
        type: 'station' | 'line' | 'campaign' | 'handoff';
      } | null;
      highlightedStations: string[];
      highlightedConnections: string[];
      hoveredElement: {
        id: string;
        type: string;
      } | null;
    };
    filters: {
      offices: string[];
      lineTypes: string[];
      campaignTypes: string[];
      campaignStatuses: string[];
      clientIds: string[];
      timeRange: [Date, Date] | null;
    };
    timeControl: {
      mode: 'live' | 'historical' | 'forecast';
      currentTime: Date;
      playbackSpeed: number;
      playing: boolean;
    };
    detail: {
      detailType: 'station' | 'line' | 'campaign' | 'system' | null;
      detailId: string | null;
      detailData: any;
    };
  };
  agents: {
    items: Record<string, Agent>;
    loading: boolean;
    error: string | null;
  };
  campaigns: {
    items: Record<string, Campaign>;
    active: string[];
    loading: boolean;
    error: string | null;
  };
  handoffs: {
    items: Record<string, Handoff>;
    active: string[];
    recent: string[];
    loading: boolean;
    error: string | null;
  };
  alerts: {
    items: Alert[];
    unread: number;
  };
  system: {
    status: 'normal' | 'busy' | 'overloaded' | 'maintenance';
    metrics: {
      activeCampaigns: number;
      completedToday: number;
      averageCycleTime: number;
      systemLoad: number;
    };
  };
  ui: {
    sidebarOpen: boolean;
    detailPanelOpen: boolean;
    currentView: 'map' | 'list' | 'metrics';
    preferences: UserPreferences;
  };
}
```

#### Redux Actions (Examples)

```typescript
// Map navigation actions
const ZOOM_TO_FEATURE = 'map/ZOOM_TO_FEATURE';
const PAN_TO_COORDINATES = 'map/PAN_TO_COORDINATES';
const SET_VIEWPORT = 'map/SET_VIEWPORT';
const RESET_VIEW = 'map/RESET_VIEW';

// Selection actions
const SELECT_ELEMENT = 'map/SELECT_ELEMENT';
const HIGHLIGHT_ELEMENT = 'map/HIGHLIGHT_ELEMENT';
const CLEAR_SELECTION = 'map/CLEAR_SELECTION';
const HOVER_ELEMENT = 'map/HOVER_ELEMENT';

// Filter actions
const SET_FILTER = 'map/SET_FILTER';
const CLEAR_FILTERS = 'map/CLEAR_FILTERS';
const SAVE_FILTER_PRESET = 'map/SAVE_FILTER_PRESET';
const LOAD_FILTER_PRESET = 'map/LOAD_FILTER_PRESET';

// Time control actions
const SET_TIME_MODE = 'map/SET_TIME_MODE';
const SET_CURRENT_TIME = 'map/SET_CURRENT_TIME';
const START_PLAYBACK = 'map/START_PLAYBACK';
const STOP_PLAYBACK = 'map/STOP_PLAYBACK';
const SET_PLAYBACK_SPEED = 'map/SET_PLAYBACK_SPEED';

// Campaign actions
const FETCH_CAMPAIGNS = 'campaigns/FETCH_CAMPAIGNS';
const UPDATE_CAMPAIGN_STATUS = 'campaigns/UPDATE_CAMPAIGN_STATUS';
const UPDATE_CAMPAIGN_POSITION = 'campaigns/UPDATE_CAMPAIGN_POSITION';
const SET_CAMPAIGN_PRIORITY = 'campaigns/SET_CAMPAIGN_PRIORITY';

// Agent actions
const FETCH_AGENTS = 'agents/FETCH_AGENTS';
const UPDATE_AGENT_STATUS = 'agents/UPDATE_AGENT_STATUS';
const UPDATE_AGENT_CAPACITY = 'agents/UPDATE_AGENT_CAPACITY';
const UPDATE_AGENT_METRICS = 'agents/UPDATE_AGENT_METRICS';

// Handoff actions
const FETCH_HANDOFFS = 'handoffs/FETCH_HANDOFFS';
const CREATE_HANDOFF = 'handoffs/CREATE_HANDOFF';
const UPDATE_HANDOFF_STATUS = 'handoffs/UPDATE_HANDOFF_STATUS';
const COMPLETE_HANDOFF = 'handoffs/COMPLETE_HANDOFF';
```

### 5. Integration Points

#### WebSocket Connection

```typescript
// websocketService.js
import io from 'socket.io-client';
import { store } from '../store';
import {
  updateAgentStatus,
  updateAgentCapacity,
  updateCampaignPosition,
  updateCampaignStatus,
  createHandoff,
  updateHandoffStatus,
  addSystemAlert
} from '../actions';

let socket = null;

export const initializeWebSocket = () => {
  socket = io(process.env.REACT_APP_WEBSOCKET_URL, {
    auth: {
      token: store.getState().auth.token
    }
  });
  
  // Agent events
  socket.on('agent:status:changed', (data) => {
    store.dispatch(updateAgentStatus(data.agentId, data.status));
  });
  
  socket.on('agent:capacity:updated', (data) => {
    store.dispatch(updateAgentCapacity(data.agentId, data.capacity));
  });
  
  // Campaign events
  socket.on('campaign:station:changed', (data) => {
    store.dispatch(updateCampaignPosition(
      data.campaignId,
      data.previousStationId,
      data.currentStationId,
      data.nextStationId
    ));
  });
  
  socket.on('campaign:status:changed', (data) => {
    store.dispatch(updateCampaignStatus(
      data.campaignId,
      data.status,
      data.reason
    ));
  });
  
  // Handoff events
  socket.on('handoff:created', (data) => {
    store.dispatch(createHandoff(data.handoff));
  });
  
  socket.on('handoff:status:changed', (data) => {
    store.dispatch(updateHandoffStatus(
      data.handoffId,
      data.status,
      data.timestamp
    ));
  });
  
  // System events
  socket.on('system:alert', (data) => {
    store.dispatch(addSystemAlert(data.alert));
  });
  
  socket.on('disconnect', () => {
    console.log('WebSocket disconnected');
    // Handle reconnection logic
  });
  
  return socket;
};

export const closeWebSocket = () => {
  if (socket) {
    socket.disconnect();
    socket = null;
  }
};
```

#### GraphQL Integration

```typescript
// graphqlClient.js
import { ApolloClient, InMemoryCache, HttpLink, split } from '@apollo/client';
import { getMainDefinition } from '@apollo/client/utilities';
import { WebSocketLink } from '@apollo/client/link/ws';

// Create an HTTP link for regular queries and mutations
const httpLink = new HttpLink({
  uri: process.env.REACT_APP_GRAPHQL_URL,
  headers: {
    authorization: localStorage.getItem('token') || ''
  }
});

// Create a WebSocket link for subscriptions
const wsLink = new WebSocketLink({
  uri: process.env.REACT_APP_GRAPHQL_WS_URL,
  options: {
    reconnect: true,
    connectionParams: {
      authorization: localStorage.getItem('token') || ''
    }
  }
});

// Use split to direct traffic based on operation type
const splitLink = split(
  ({ query }) => {
    const definition = getMainDefinition(query);
    return (
      definition.kind === 'OperationDefinition' &&
      definition.operation === 'subscription'
    );
  },
  wsLink,
  httpLink
);

// Create the Apollo Client
export const client = new ApolloClient({
  link: splitLink,
  cache: new InMemoryCache({
    typePolicies: {
      // Define how to merge and update cache entries
      Agent: {
        keyFields: ['id'],
        fields: {
          metrics: {
            merge: true
          }
        }
      },
      Campaign: {
        keyFields: ['id'],
        fields: {
          journey: {
            merge(existing = [], incoming) {
              return [...existing, ...incoming];
            }
          }
        }
      }
    }
  })
});

// Example query hooks
export const useAgentQuery = (agentId) => {
  return useQuery(GET_AGENT, {
    variables: { id: agentId },
    pollInterval: 30000 // Refresh every 30 seconds
  });
};

export const useActiveCampaignsQuery = (filters) => {
  return useQuery(GET_ACTIVE_CAMPAIGNS, {
    variables: filters,
    pollInterval: 10000 // Refresh every 10 seconds
  });
};

// Example subscription hook
export const useCampaignMovementSubscription = (campaignId) => {
  return useSubscription(CAMPAIGN_MOVEMENT_SUBSCRIPTION, {
    variables: { campaignId }
  });
};
```

#### REST API Integration

```typescript
// apiService.js
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL;

// Create axios instance with common configuration
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add auth token to all requests
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle common response processing
api.interceptors.response.use(
  response => response.data,
  error => {
    // Handle common error cases
    if (error.response && error.response.status === 401) {
      // Unauthorized - redirect to login
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Map API endpoints
export const mapApi = {
  getLayout: () => api.get('/api/map/layout'),
  getStatus: () => api.get('/api/map/status'),
  getHotspots: () => api.get('/api/map/hotspots'),
  getMetrics: (timeRange) => api.get('/api/map/metrics', { params: { timeRange } })
};

// Agent API endpoints
export const agentApi = {
  getAll: (filters) => api.get('/api/agents', { params: filters }),
  getById: (id) => api.get(`/api/agents/${id}`),
  getStatus: (id) => api.get(`/api/agents/${id}/status`),
  getMetrics: (id, timeRange) => api.get(`/api/agents/${id}/metrics`, { params: { timeRange } }),
  getCampaigns: (id) => api.get(`/api/agents/${id}/campaigns`)
};

// Campaign API endpoints
export const campaignApi = {
  getAll: (filters) => api.get('/api/campaigns', { params: filters }),
  getById: (id) => api.get(`/api/campaigns/${id}`),
  getHistory: (id) => api.get(`/api/campaigns/${id}/history`),
  getTimeline: (id) => api.get(`/api/campaigns/${id}/timeline`),
  updatePriority: (id, priority) => api.put(`/api/campaigns/${id}/priority`, { priority })
};

// Custom hooks
export const useMapData = (filters) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const layout = await mapApi.getLayout();
        const status = await mapApi.getStatus();
        
        // Combine and process data
        setData({
          ...layout,
          stations: layout.stations.map(station => ({
            ...station,
            status: status.agents[station.id]?.status || 'offline',
            active: status.agents[station.id]?.active || false,
            queue: status.agents[station.id]?.queue || 0
          })),
          activeCampaigns: status.campaigns,
          timestamp: status.timestamp
        });
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, [filters]);
  
  return { data, loading, error };
};
```

## Performance Optimization

### 1. Rendering Strategies

To maintain smooth performance even with complex visualizations:

```typescript
// High-performance rendering approaches

// 1. Canvas-based rendering for high-density elements
const CanvasLayer = ({ elements, renderFunction }) => {
  const canvasRef = useRef(null);
  
  useEffect(() => {
    if (!canvasRef.current) return;
    const canvas = canvasRef.current;
    const context = canvas.getContext('2d');
    
    // Clear canvas
    context.clearRect(0, 0, canvas.width, canvas.height);
    
    // Render elements
    elements.forEach(element => {
      renderFunction(context, element);
    });
  }, [elements, renderFunction]);
  
  return <canvas ref={canvasRef} className="canvas-layer" />;
};

// 2. Virtualized rendering for large datasets
import { FixedSizeList } from 'react-window';

const VirtualizedList = ({ items, height, width }) => {
  const Row = ({ index, style }) => (
    <div style={style} className="virtualized-item">
      {items[index].name}
    </div>
  );
  
  return (
    <FixedSizeList
      height={height}
      width={width}
      itemCount={items.length}
      itemSize={35}
    >
      {Row}
    </FixedSizeList>
  );
};

// 3. Windowed rendering for map elements
const WinderedMapElements = ({ elements, viewport }) => {
  // Only render elements within the current viewport plus a buffer
  const visibleElements = useMemo(() => {
    const buffer = 100; // pixels
    const bounds = {
      minX: viewport.x - buffer,
      maxX: viewport.x + viewport.width + buffer,
      minY: viewport.y - buffer,
      maxY: viewport.y + viewport.height + buffer
    };
    
    return elements.filter(element => {
      return (
        element.position.x >= bounds.minX &&
        element.position.x <= bounds.maxX &&
        element.position.y >= bounds.minY &&
        element.position.y <= bounds.maxY
      );
    });
  }, [elements, viewport]);
  
  return (
    <React.Fragment>
      {visibleElements.map(element => (
        <MapElement key={element.id} element={element} />
      ))}
    </React.Fragment>
  );
};
```

### 2. Animation Optimization

```typescript
// Efficient animation approaches

// 1. Use requestAnimationFrame for smooth animations
const useAnimationFrame = (callback) => {
  const requestRef = useRef();
  const previousTimeRef = useRef();
  
  const animate = time => {
    if (previousTimeRef.current !== undefined) {
      const deltaTime = time - previousTimeRef.current;
      callback(deltaTime);
    }
    previousTimeRef.current = time;
    requestRef.current = requestAnimationFrame(animate);
  };
  
  useEffect(() => {
    requestRef.current = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(requestRef.current);
  }, []);
};

// 2. Use CSS transitions for simple animations
const CSSTransitionElement = ({ position, isActive }) => {
  return (
    <div 
      className={`transition-element ${isActive ? 'active' : ''}`}
      style={{
        transform: `translate(${position.x}px, ${position.y}px)`,
        transition: 'transform 0.5s ease-out, opacity 0.3s ease-in-out'
      }}
    />
  );
};

// 3. Throttle animations for performance
import { throttle } from 'lodash';

const ThrottledAnimation = ({ elements }) => {
  const [positions, setPositions] = useState({});
  
  // Update positions at most once per 100ms
  const updatePositions = useCallback(
    throttle((newPositions) => {
      setPositions(newPositions);
    }, 100),
    []
  );
  
  useEffect(() => {
    // Calculate new positions
    const newPositions = elements.reduce((acc, element) => {
      acc[element.id] = calculatePosition(element);
      return acc;
    }, {});
    
    updatePositions(newPositions);
  }, [elements, updatePositions]);
  
  return (
    <React.Fragment>
      {elements.map(element => (
        <AnimatedElement 
          key={element.id}
          element={element}
          position={positions[element.id] || element.initialPosition}
        />
      ))}
    </React.Fragment>
  );
};
```

### 3. Data Management

```typescript
// Efficient data handling approaches

// 1. Implement pagination for large datasets
const usePaginatedData = (fetchFunction, pageSize = 20) => {
  const [data, setData] = useState([]);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  
  const loadMore = useCallback(async () => {
    if (loading || !hasMore) return;
    
    setLoading(true);
    try {
      const newData = await fetchFunction(page, pageSize);
      if (newData.length < pageSize) {
        setHasMore(false);
      }
      setData(prev => [...prev, ...newData]);
      setPage(prev => prev + 1);
    } catch (error) {
      console.error("Error loading data:", error);
    } finally {
      setLoading(false);
    }
  }, [fetchFunction, page, pageSize, loading, hasMore]);
  
  return { data, loading, hasMore, loadMore };
};

// 2. Use memoization for expensive calculations
const useMapLayout = (stations, connections) => {
  return useMemo(() => {
    // Expensive layout calculation
    const layout = calculateOptimalLayout(stations, connections);
    return layout;
  }, [stations, connections]);
};

// 3. Implement data caching
const useDataWithCache = (fetchFunction, cacheKey, ttl = 60000) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    // Check cache first
    const cachedData = localStorage.getItem(`cache_${cacheKey}`);
    if (cachedData) {
      const { data: cachedValue, timestamp } = JSON.parse(cachedData);
      const age = Date.now() - timestamp;
      
      if (age < ttl) {
        setData(cachedValue);
        setLoading(false);
        return;
      }
    }
    
    // Fetch fresh data
    const fetchData = async () => {
      try {
        setLoading(true);
        const result = await fetchFunction();
        setData(result);
        
        // Save to cache
        localStorage.setItem(
          `cache_${cacheKey}`,
          JSON.stringify({
            data: result,
            timestamp: Date.now()
          })
        );
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, [fetchFunction, cacheKey, ttl]);
  
  return { data, loading, error };
};
```

## Testing Strategy

### 1. Component Tests

```typescript
// Example Jest test for a component

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { Provider } from 'react-redux';
import configureStore from 'redux-mock-store';
import StationLayer from '../../components/StationLayer';

const mockStore = configureStore([]);

describe('StationLayer', () => {
  let store;
  
  const mockStations = [
    {
      id: 'station1',
      name: 'Test Station 1',
      type: 'agent',
      position: { x: 100, y: 100 },
      size: 10,
      active: true,
      office: 'front',
      status: 'available',
      queue: 0
    },
    {
      id: 'station2',
      name: 'Test Station 2',
      type: 'agent',
      position: { x: 200, y: 200 },
      size: 10,
      active: false,
      office: 'middle',
      status: 'busy',
      queue: 5
    }
  ];
  
  beforeEach(() => {
    store = mockStore({
      map: {
        highlightedStations: [],
        hoveredStation: null
      }
    });
  });
  
  test('renders all stations', () => {
    const mockOnClick = jest.fn();
    
    render(
      <Provider store={store}>
        <svg>
          <StationLayer 
            stations={mockStations}
            onStationClick={mockOnClick}
          />
        </svg>
      </Provider>
    );
    
    const station1 = screen.getByTestId('station-station1');
    const station2 = screen.getByTestId('station-station2');
    
    expect(station1).toBeInTheDocument();
    expect(station2).toBeInTheDocument();
  });
  
  test('calls onClick handler when station is clicked', () => {
    const mockOnClick = jest.fn();
    
    render(
      <Provider store={store}>
        <svg>
          <StationLayer 
            stations={mockStations}
            onStationClick={mockOnClick}
          />
        </svg>
      </Provider>
    );
    
    const station1 = screen.getByTestId('station-station1');
    fireEvent.click(station1);
    
    expect(mockOnClick).toHaveBeenCalledWith(mockStations[0]);
  });
  
  test('shows queue indicator for stations with queue', () => {
    render(
      <Provider store={store}>
        <svg>
          <StationLayer 
            stations={mockStations}
            onStationClick={() => {}}
          />
        </svg>
      </Provider>
    );
    
    const station1 = screen.getByTestId('station-station1');
    const station2 = screen.getByTestId('station-station2');
    
    expect(station1.querySelector('.queue-indicator')).toBeNull();
    expect(station2.querySelector('.queue-indicator')).toBeInTheDocument();
  });
});
```

### 2. Integration Tests

```typescript
// Example Cypress integration test

describe('Subway Map Dashboard', () => {
  beforeEach(() => {
    // Setup mock API responses
    cy.intercept('GET', '/api/map/layout', { fixture: 'mapLayout.json' }).as('getMapLayout');
    cy.intercept('GET', '/api/map/status', { fixture: 'mapStatus.json' }).as('getMapStatus');
    cy.intercept('GET', '/api/campaigns', { fixture: 'campaigns.json' }).as('getCampaigns');
    
    // Visit the dashboard
    cy.visit('/dashboard/map');
    cy.wait(['@getMapLayout', '@getMapStatus', '@getCampaigns']);
  });
  
  it('displays the subway map with all elements', () => {
    // Check that map elements are rendered
    cy.get('.subway-map').should('be.visible');
    cy.get('.stations-layer').should('exist');
    cy.get('.connections-layer').should('exist');
    cy.get('.campaigns-layer').should('exist');
    
    // Count stations
    cy.get('.station').should('have.length', 26);
  });
  
  it('highlights a station when clicked', () => {
    // Click on a station
    cy.get('[data-testid="station-agent1"]').click();
    
    // Verify the station is highlighted
    cy.get('[data-testid="station-agent1"]').should('have.class', 'highlighted');
    
    // Verify detail panel shows station information
    cy.get('.detail-panel').should('be.visible');
    cy.get('.detail-panel-title').should('contain', 'Rachel Client');
  });
  
  it('filters map elements based on selection', () => {
    // Open filter panel
    cy.get('[data-testid="filter-button"]').click();
    
    // Select only front office
    cy.get('[data-testid="filter-office-front"]').click();
    cy.get('[data-testid="apply-filters"]').click();
    
    // Verify only front office stations are visible
    cy.get('.station.office-front').should('be.visible');
    cy.get('.station.office-middle').should('not.be.visible');
    cy.get('.station.office-back').should('not.be.visible');
  });
  
  it('tracks a campaign through the workflow', () => {
    // Find a campaign train
    cy.get('.campaign-train').first().click();
    
    // Verify campaign is selected
    cy.get('.campaign-train.selected').should('exist');
    
    // Open campaign detail
    cy.get('.detail-panel').should('contain', 'Campaign Details');
    
    // Click "Track Campaign" button
    cy.get('[data-testid="track-campaign"]').click();
    
    // Verify tracking mode is enabled
    cy.get('.map-status-bar').should('contain', 'Tracking Campaign');
    
    // Verify campaign path is highlighted
    cy.get('.connection.highlighted').should('have.length.greaterThan', 0);
  });
});
```

## Conclusion

This technical implementation guide provides a comprehensive blueprint for building the Koya Workflow Subway Map visualization. By leveraging modern front-end technologies and performance optimization techniques, the visualization will offer an intuitive, real-time view of our AI-native agency's operations.

The implementation focuses on:

1. **Interactive Visualization**: Creating an engaging, subway-inspired map of agent workflows
2. **Real-Time Updates**: Tracking campaign progression and handoffs as they happen
3. **Performance Optimization**: Ensuring smooth operation even with complex visualizations
4. **Intuitive Navigation**: Providing drill-down capabilities and context-aware filtering
5. **Integration**: Connecting with our core agency systems for live data

This visualization will serve as the central monitoring interface for our agency, providing unprecedented visibility into the flow of work across our specialized agents while maintaining the intuitive visual language of a transit map that users can immediately understand.

## Next Steps

1. **Prototype Development**: Create a basic implementation of the subway map with static data
2. **Data Integration**: Connect to real-time data sources through APIs and WebSockets
3. **Performance Testing**: Validate performance with large datasets and complex workflows
4. **User Testing**: Gather feedback from agency staff on usability and intuitiveness
5. **Feature Iteration**: Incrementally add advanced features like what-if modeling and historical playback
6. **Dashboard Integration**: Incorporate the subway map into the broader agency dashboard