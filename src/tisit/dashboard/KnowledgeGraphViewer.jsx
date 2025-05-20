// SPDX-License-Identifier: MIT
// Copyright (c) 2025 Vamsi Duvvuri

// Fifth Grade Explanation:
// This file creates a cool map of our knowledge that you can zoom into and explore.
// It shows how different ideas are connected, like a treasure map of information.

// High School Explanation:
// This React component renders an interactive visualization of the TISIT knowledge graph
// using React Force Graph. It enables users to explore entity relationships, filter by
// entity types, and inspect individual entities in detail.

import React, { useState, useEffect, useRef, useCallback } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { useNavigate, useLocation } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';

// Import UI components
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Divider,
  FormControl,
  Grid,
  IconButton,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  Stack,
  Tab,
  Tabs,
  TextField,
  Typography,
  useTheme,
} from '@mui/material';

// Import icons
import {
  Search as SearchIcon,
  Refresh as RefreshIcon,
  ZoomIn as ZoomInIcon,
  ZoomOut as ZoomOutIcon,
  FilterList as FilterIcon,
  Info as InfoIcon,
  Close as CloseIcon,
} from '@mui/icons-material';

// API client for fetching knowledge graph data
import { fetchGraphData, fetchEntityTypes, searchEntities } from './api';

// Entity type color mapping
const ENTITY_COLORS = {
  campaign: '#4CAF50', // Green
  audience_segment: '#2196F3', // Blue
  creative_approach: '#FFC107', // Amber
  channel: '#FF9800', // Orange
  strategy: '#9C27B0', // Purple
  metric: '#F44336', // Red
  brand: '#3F51B5', // Indigo
  message: '#00BCD4', // Cyan
  asset: '#009688', // Teal
  concept: '#673AB7', // Deep Purple
  framework: '#8BC34A', // Light Green
  person: '#E91E63', // Pink
  company: '#795548', // Brown
  product: '#607D8B', // Blue Grey
  default: '#9E9E9E', // Grey
};

const NODE_RADIUS = 8;
const HIGHLIGHTED_NODE_RADIUS = 12;

const KnowledgeGraphViewer = () => {
  const theme = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const graphRef = useRef();
  
  // Parse query parameters
  const queryParams = new URLSearchParams(location.search);
  const initialEntityId = queryParams.get('entityId');
  const initialQuery = queryParams.get('query') || '';
  
  // State
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [highlightNodes, setHighlightNodes] = useState(new Set());
  const [highlightLinks, setHighlightLinks] = useState(new Set());
  const [selectedNode, setSelectedNode] = useState(null);
  const [searchQuery, setSearchQuery] = useState(initialQuery);
  const [filterType, setFilterType] = useState('');
  const [isFilterDialogOpen, setIsFilterDialogOpen] = useState(false);
  const [zoomLevel, setZoomLevel] = useState(1);
  
  // Fetch entity types for filtering
  const { data: entityTypes = [] } = useQuery({
    queryKey: ['entityTypes'],
    queryFn: fetchEntityTypes,
  });
  
  // Fetch graph data
  const { 
    data: fetchedGraphData, 
    isLoading, 
    isError, 
    refetch 
  } = useQuery({
    queryKey: ['graphData', filterType, searchQuery],
    queryFn: () => fetchGraphData({ entityType: filterType, query: searchQuery }),
  });
  
  // Update graph data when API response changes
  useEffect(() => {
    if (fetchedGraphData) {
      setGraphData(fetchedGraphData);
      
      // If we have an initial entity ID, highlight that node
      if (initialEntityId) {
        const node = fetchedGraphData.nodes.find(n => n.id === initialEntityId);
        if (node) {
          handleNodeClick(node);
          
          // Center the graph on the selected node
          if (graphRef.current) {
            graphRef.current.centerAt(node.x, node.y, 1000);
            graphRef.current.zoom(1.5, 1000);
          }
        }
      }
    }
  }, [fetchedGraphData, initialEntityId]);
  
  // Handle node hover
  const handleNodeHover = useCallback(node => {
    if (!node) {
      setHighlightNodes(new Set());
      setHighlightLinks(new Set());
      return;
    }
    
    // Find all connected nodes and links
    const connectedNodes = new Set([node.id]);
    const connectedLinks = new Set();
    
    graphData.links.forEach(link => {
      if (link.source.id === node.id || link.target.id === node.id) {
        connectedNodes.add(link.source.id);
        connectedNodes.add(link.target.id);
        connectedLinks.add(link);
      }
    });
    
    setHighlightNodes(connectedNodes);
    setHighlightLinks(connectedLinks);
  }, [graphData]);
  
  // Handle node click
  const handleNodeClick = useCallback(node => {
    setSelectedNode(node);
    
    // Update URL to include selected entity
    const params = new URLSearchParams(location.search);
    params.set('entityId', node.id);
    navigate({ search: params.toString() }, { replace: true });
    
    if (graphRef.current) {
      // Zoom in slightly on the clicked node
      const distance = 40;
      const distRatio = 1 + distance/Math.hypot(node.x, node.y);
      graphRef.current.centerAt(node.x, node.y, 1000);
      graphRef.current.zoom(1.5, 1000);
    }
  }, [location.search, navigate]);
  
  // Handle search
  const handleSearch = () => {
    // Update URL to include search query
    const params = new URLSearchParams(location.search);
    if (searchQuery) {
      params.set('query', searchQuery);
    } else {
      params.delete('query');
    }
    navigate({ search: params.toString() }, { replace: true });
    
    // Trigger refetch with new search parameters
    refetch();
  };
  
  // Handle filter change
  const handleFilterChange = (newFilter) => {
    setFilterType(newFilter);
    setIsFilterDialogOpen(false);
    
    // Trigger refetch with new filter
    refetch();
  };
  
  // Handle zoom
  const handleZoomIn = () => {
    if (graphRef.current) {
      const newZoom = zoomLevel * 1.2;
      graphRef.current.zoom(newZoom, 800);
      setZoomLevel(newZoom);
    }
  };
  
  const handleZoomOut = () => {
    if (graphRef.current) {
      const newZoom = zoomLevel / 1.2;
      graphRef.current.zoom(newZoom, 800);
      setZoomLevel(newZoom);
    }
  };
  
  // Node painting function
  const paintNode = useCallback((node, ctx) => {
    // Node color based on entity type
    const color = ENTITY_COLORS[node.type] || ENTITY_COLORS.default;
    
    // Set node size based on highlight state
    const size = highlightNodes.has(node.id) ? HIGHLIGHTED_NODE_RADIUS : NODE_RADIUS;
    
    // Draw filled circle
    ctx.beginPath();
    ctx.arc(node.x, node.y, size, 0, 2 * Math.PI);
    ctx.fillStyle = color;
    ctx.fill();
    
    // Draw border
    ctx.strokeStyle = theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.7)' : 'rgba(0,0,0,0.7)';
    ctx.lineWidth = highlightNodes.has(node.id) ? 2 : 1;
    ctx.stroke();
    
    // Draw label for highlighted nodes
    if (highlightNodes.has(node.id)) {
      ctx.fillStyle = theme.palette.mode === 'dark' ? '#fff' : '#000';
      ctx.font = '6px Arial';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(node.name, node.x, node.y + 15);
    }
  }, [highlightNodes, theme.palette.mode]);
  
  // Link painting function
  const paintLink = useCallback((link, ctx) => {
    // Set link color based on highlight state
    ctx.strokeStyle = highlightLinks.has(link) 
      ? theme.palette.primary.main 
      : theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.2)' : 'rgba(0,0,0,0.1)';
    
    ctx.lineWidth = highlightLinks.has(link) ? 2 : 1;
    
    // Draw link
    ctx.beginPath();
    ctx.moveTo(link.source.x, link.source.y);
    ctx.lineTo(link.target.x, link.target.y);
    ctx.stroke();
    
    // Draw link label if highlighted
    if (highlightLinks.has(link)) {
      const midX = (link.source.x + link.target.x) / 2;
      const midY = (link.source.y + link.target.y) / 2;
      
      ctx.fillStyle = theme.palette.mode === 'dark' ? '#fff' : '#000';
      ctx.font = '5px Arial';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(link.type, midX, midY);
    }
  }, [highlightLinks, theme]);
  
  // Close node details
  const handleCloseDetails = () => {
    setSelectedNode(null);
    
    // Remove entity ID from URL
    const params = new URLSearchParams(location.search);
    params.delete('entityId');
    navigate({ search: params.toString() }, { replace: true });
  };
  
  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Toolbar */}
      <Paper sx={{ mb: 2, p: 1 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={6}>
            <Stack direction="row" spacing={1}>
              <TextField
                size="small"
                placeholder="Search knowledge graph..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                fullWidth
                InputProps={{
                  endAdornment: (
                    <IconButton size="small" onClick={handleSearch}>
                      <SearchIcon />
                    </IconButton>
                  )
                }}
              />
              <Button 
                variant="outlined" 
                startIcon={<FilterIcon />}
                onClick={() => setIsFilterDialogOpen(true)}
              >
                Filter
              </Button>
            </Stack>
          </Grid>
          <Grid item xs={12} md={6}>
            <Stack direction="row" spacing={1} justifyContent={{ xs: 'flex-start', md: 'flex-end' }}>
              <IconButton onClick={handleZoomIn}>
                <ZoomInIcon />
              </IconButton>
              <IconButton onClick={handleZoomOut}>
                <ZoomOutIcon />
              </IconButton>
              <Button 
                variant="outlined" 
                startIcon={<RefreshIcon />}
                onClick={() => refetch()}
              >
                Refresh
              </Button>
            </Stack>
          </Grid>
          
          {/* Filter chips */}
          {filterType && (
            <Grid item xs={12}>
              <Stack direction="row" spacing={1}>
                <Typography variant="body2">Filters:</Typography>
                <Chip 
                  label={`Type: ${filterType}`} 
                  onDelete={() => handleFilterChange('')}
                  size="small"
                />
              </Stack>
            </Grid>
          )}
        </Grid>
      </Paper>
      
      {/* Graph visualization */}
      <Box sx={{ flex: 1, minHeight: 500, position: 'relative' }}>
        {isLoading ? (
          <Box 
            sx={{ 
              display: 'flex', 
              justifyContent: 'center', 
              alignItems: 'center',
              height: '100%'
            }}
          >
            <CircularProgress />
          </Box>
        ) : isError ? (
          <Box 
            sx={{ 
              display: 'flex', 
              justifyContent: 'center', 
              alignItems: 'center',
              height: '100%' 
            }}
          >
            <Typography color="error">Error loading knowledge graph data.</Typography>
            <Button onClick={() => refetch()} startIcon={<RefreshIcon />}>
              Retry
            </Button>
          </Box>
        ) : (
          <ForceGraph2D
            ref={graphRef}
            graphData={graphData}
            nodeId="id"
            nodeLabel="name"
            nodeColor={node => ENTITY_COLORS[node.type] || ENTITY_COLORS.default}
            linkSource="source"
            linkTarget="target"
            linkLabel="type"
            onNodeHover={handleNodeHover}
            onNodeClick={handleNodeClick}
            nodeCanvasObject={paintNode}
            linkCanvasObject={paintLink}
            cooldownTicks={100}
            onEngineStop={() => graphRef.current?.zoomToFit(400, 30)}
            linkDirectionalArrowLength={3}
            linkDirectionalArrowRelPos={0.9}
            linkCurvature={0.1}
            backgroundColor={theme.palette.mode === 'dark' ? '#1a1a1a' : '#ffffff'}
          />
        )}
      </Box>
      
      {/* Node details */}
      {selectedNode && (
        <Card sx={{ mt: 2 }}>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6" component="h2">
                {selectedNode.name}
              </Typography>
              <IconButton size="small" onClick={handleCloseDetails}>
                <CloseIcon />
              </IconButton>
            </Box>
            
            <Grid container spacing={2}>
              <Grid item xs={12} md={4}>
                <Typography variant="subtitle2" color="text.secondary">Entity Type</Typography>
                <Chip 
                  label={selectedNode.type} 
                  size="small" 
                  sx={{ 
                    mt: 0.5,
                    backgroundColor: ENTITY_COLORS[selectedNode.type] || ENTITY_COLORS.default
                  }} 
                />
              </Grid>
              
              {selectedNode.tags && selectedNode.tags.length > 0 && (
                <Grid item xs={12} md={8}>
                  <Typography variant="subtitle2" color="text.secondary">Tags</Typography>
                  <Box sx={{ mt: 0.5 }}>
                    {selectedNode.tags.map(tag => (
                      <Chip 
                        key={tag} 
                        label={tag} 
                        size="small" 
                        sx={{ mr: 0.5, mb: 0.5 }} 
                      />
                    ))}
                  </Box>
                </Grid>
              )}
              
              <Grid item xs={12}>
                <Typography variant="subtitle2" color="text.secondary">Description</Typography>
                <Typography variant="body2" sx={{ mt: 0.5 }}>
                  {selectedNode.description || 'No description available.'}
                </Typography>
              </Grid>
              
              <Grid item xs={12}>
                <Typography variant="subtitle2" color="text.secondary">Relationships</Typography>
                <Box sx={{ mt: 0.5 }}>
                  {graphData.links
                    .filter(link => link.source.id === selectedNode.id || link.target.id === selectedNode.id)
                    .map(link => {
                      const isSource = link.source.id === selectedNode.id;
                      const otherNode = isSource ? link.target : link.source;
                      
                      return (
                        <Box key={link.id} sx={{ mb: 1 }}>
                          <Typography variant="body2">
                            {isSource ? (
                              <>
                                <strong>{link.type}</strong> {otherNode.name}
                              </>
                            ) : (
                              <>
                                {otherNode.name} <strong>{link.type}</strong>
                              </>
                            )}
                          </Typography>
                        </Box>
                      );
                    })}
                </Box>
                
                {graphData.links.filter(link => 
                  link.source.id === selectedNode.id || link.target.id === selectedNode.id
                ).length === 0 && (
                  <Typography variant="body2">No relationships.</Typography>
                )}
              </Grid>
              
              {selectedNode.metadata && Object.keys(selectedNode.metadata).length > 0 && (
                <Grid item xs={12}>
                  <Typography variant="subtitle2" color="text.secondary">Metadata</Typography>
                  <Box sx={{ mt: 0.5 }}>
                    {Object.entries(selectedNode.metadata).map(([key, value]) => (
                      <Box key={key} sx={{ mb: 0.5 }}>
                        <Typography variant="body2">
                          <strong>{key}:</strong> {JSON.stringify(value)}
                        </Typography>
                      </Box>
                    ))}
                  </Box>
                </Grid>
              )}
            </Grid>
          </CardContent>
        </Card>
      )}
      
      {/* Filter Dialog */}
      <Dialog 
        open={isFilterDialogOpen} 
        onClose={() => setIsFilterDialogOpen(false)}
        maxWidth="xs"
        fullWidth
      >
        <DialogTitle>Filter Knowledge Graph</DialogTitle>
        <DialogContent>
          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel id="entity-type-filter-label">Entity Type</InputLabel>
            <Select
              labelId="entity-type-filter-label"
              id="entity-type-filter"
              value={filterType}
              label="Entity Type"
              onChange={(e) => setFilterType(e.target.value)}
            >
              <MenuItem value="">All Types</MenuItem>
              {entityTypes.map(type => (
                <MenuItem key={type} value={type}>{type}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsFilterDialogOpen(false)}>Cancel</Button>
          <Button 
            onClick={() => handleFilterChange(filterType)} 
            variant="contained"
          >
            Apply Filter
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default KnowledgeGraphViewer;