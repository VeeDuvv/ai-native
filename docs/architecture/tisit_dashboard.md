# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# TISIT Knowledge Graph Dashboard

## Overview

The TISIT Knowledge Graph Dashboard provides an interactive user interface for exploring, visualizing, and managing the TISIT knowledge graph. It enables users to navigate the interconnected knowledge entities, view detailed information about campaigns and other entities, and visualize relationships between different pieces of knowledge.

## Architecture

The dashboard is built using React and follows a component-based architecture. It leverages React Router for navigation, React Query for data fetching, and Material-UI for the user interface components. The dashboard communicates with the TISIT API to retrieve and manipulate knowledge graph data.

### Key Components

1. **KnowledgeDashboard**: The main container component that handles navigation and provides the overall layout.

2. **KnowledgeGraphViewer**: Interactive visualization of the knowledge graph using a force-directed graph layout with the react-force-graph library.

3. **CampaignKnowledgeView**: Detailed view of a campaign and its related entities, providing both a structured view and a graph visualization.

4. **API Client**: Utility functions for communicating with the TISIT API, handling data transformation, and caching.

## Features

### Knowledge Graph Visualization

The KnowledgeGraphViewer component provides an interactive visualization of the knowledge graph:

- **Force-directed Graph**: Automatically arranges nodes and links based on their relationships
- **Node Highlighting**: Highlights connected nodes and relationships when hovering or selecting a node
- **Filtering**: Filter by entity type, search query, or specific attributes
- **Zooming and Panning**: Navigate through the graph with intuitive controls
- **Node Details**: View detailed information about entities when selected
- **Relationship Labels**: Display relationship types between entities

### Campaign Knowledge View

The CampaignKnowledgeView component provides a structured view of a campaign's knowledge:

- **Campaign Overview**: Display key campaign information and metadata
- **Related Entities**: Organized sections for audiences, creative approaches, assets, channels, metrics, and insights
- **Entity Details**: Quick access to detailed information about related entities
- **Graph Visualization**: Alternative view showing the campaign's network of relationships

### Navigation and Search

The dashboard provides robust navigation and search capabilities:

- **Main Navigation**: Access different sections of the dashboard through the navigation menu
- **Search**: Search for entities across the knowledge graph by name, type, or content
- **Breadcrumbs**: Track and navigate your exploration path
- **Entity Types**: Browse entities by their type categories

## Integration with Main Application

The dashboard can be integrated into the main application in several ways:

1. **Standalone Mode**: Run as a separate single-page application accessed through a dedicated URL

2. **Embedded Mode**: Integrate specific components into existing dashboard pages

3. **Hybrid Mode**: Load the dashboard within an iframe or modal in the main application

### Integration Code Example

```jsx
import { KnowledgeGraphViewer, CampaignKnowledgeView } from '@/tisit/dashboard';

// Embed knowledge graph visualization on a campaign page
const CampaignPage = ({ campaignId }) => {
  return (
    <div>
      <h1>Campaign Insights</h1>
      <div className="campaign-knowledge-section">
        <h2>Knowledge Graph</h2>
        <KnowledgeGraphViewer initialEntityId={campaignId} height={400} />
      </div>
    </div>
  );
};
```

## Dashboard Customization

The dashboard supports several customization options:

1. **Theming**: Customize colors, typography, and component styles through Material-UI theming

2. **Layout**: Configure the layout and visibility of different dashboard sections

3. **API Connection**: Modify the API endpoint and authentication settings

4. **Visualization Settings**: Adjust graph physics, node appearance, and interaction behavior

## User Experience Design

The dashboard is designed with the following UX principles:

1. **Progressive Disclosure**: Present the most relevant information first, with details available on demand

2. **Contextual Navigation**: Provide navigation options based on the current context

3. **Visual Hierarchy**: Use size, color, and position to guide attention to important elements

4. **Consistent Patterns**: Maintain consistent interaction patterns throughout the application

## Development Workflow

To extend or modify the dashboard:

1. **Component Development**: Create or modify React components in the `src/tisit/dashboard` directory

2. **API Integration**: Update API client functions in `api.js` as needed

3. **Testing**: Test components in isolation using the standalone test page

4. **Building**: Build the dashboard using Vite for production deployment

## Deployment

The dashboard can be deployed in several ways:

1. **Static Site**: Build and deploy as a static web application

2. **Server-rendered**: Integrate with a server-side rendering framework

3. **Embedded**: Include built assets in the main application bundle

## Future Enhancements

Planned enhancements for the dashboard include:

1. **Advanced Filtering**: More sophisticated filtering options with complex queries

2. **Saved Views**: Allow users to save and share specific graph views

3. **Annotation**: Add notes and annotations to knowledge graph visualizations

4. **Edit Capabilities**: Direct editing of entities and relationships through the dashboard

5. **Time-based Visualization**: Show how the knowledge graph evolves over time