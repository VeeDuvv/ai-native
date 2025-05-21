# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Koya Workflow Subway Map Dashboard

This dashboard visualizes the agent workflows of the Koya AI-native advertising agency using a subway map metaphor. It provides an intuitive, interactive view of how campaigns move through our specialized agents, making complex workflow interactions easy to understand at a glance.

## Features

- Interactive subway map visualization of agent workflows
- Different colored lines representing different workflow types (brand campaigns, digital campaigns, etc.)
- Stations representing our 26 specialized agents organized by office (front, middle, back)
- Animated "trains" representing active campaigns moving through the workflow
- Detailed information panels for both agents and campaigns
- Intuitive zoom and pan controls for exploring the map
- Visual highlighting of selected elements and their connections
- Real-time status indicators and progress tracking

## Getting Started

### Prerequisites

- Node.js 16+ and npm/yarn

### Installation

1. Clone the repository
2. Install dependencies:
```
cd dashboard
npm install
```

### Running the Dashboard

```
npm run dev
```

This will start the development server, typically on http://localhost:5173.

### Building for Production

```
npm run build
```

## Implementation Details

- Built with React and Vite
- Visualization implemented with D3.js
- Data sourced from our agent workflow documentation
- Responsive design for various screen sizes

## Future Enhancements

- Real-time data integration with agent monitoring systems
- Historical playback of workflow activity
- Predictive visualization of campaign progression
- Custom views by department and role
- Additional analytics and reporting features