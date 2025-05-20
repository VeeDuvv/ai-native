// SPDX-License-Identifier: MIT
// Copyright (c) 2025 Vamsi Duvvuri

// Fifth Grade Explanation:
// This file creates the main page for our knowledge explorer. It's like a table
// of contents that helps people find and explore different parts of our knowledge brain.

// High School Explanation:
// This React component serves as the main entry point for the TISIT knowledge graph dashboard.
// It provides a navigation interface to explore entities, campaigns, and the knowledge graph
// visualization, integrating all the dashboard components.

import React, { useState } from 'react';
import { Routes, Route, Link, useNavigate, useLocation } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';

// Import UI components
import {
  Alert,
  AppBar,
  Box,
  Breadcrumbs,
  Button,
  Card,
  CardActionArea,
  CardContent,
  CardHeader,
  CardMedia,
  Chip,
  CircularProgress,
  Container,
  Divider,
  Drawer,
  Grid,
  IconButton,
  InputAdornment,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Menu,
  MenuItem,
  Paper,
  Stack,
  Tab,
  Tabs,
  TextField,
  Toolbar,
  Tooltip,
  Typography,
  useTheme,
} from '@mui/material';

// Import icons
import {
  Menu as MenuIcon,
  Search as SearchIcon,
  Dashboard as DashboardIcon,
  Campaign as CampaignIcon,
  Category as CategoryIcon,
  Tag as TagIcon,
  Explore as ExploreIcon,
  Settings as SettingsIcon,
  ArrowBack as BackIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';

// Import dashboard components
import KnowledgeGraphViewer from './KnowledgeGraphViewer';
import CampaignKnowledgeView from './CampaignKnowledgeView';

// Import API functions
import { 
  fetchEntityTypes, 
  searchEntities, 
  fetchGraphData,
  getEntity,
} from './api';

// Custom components
const DashboardCard = ({ title, description, icon, count, to, color = 'primary' }) => {
  const navigate = useNavigate();
  const theme = useTheme();
  
  return (
    <Card sx={{ height: '100%' }}>
      <CardActionArea 
        sx={{ height: '100%' }}
        onClick={() => navigate(to)}
      >
        <CardContent>
          <Box 
            sx={{ 
              display: 'flex',
              alignItems: 'center',
              mb: 2,
              color: theme.palette[color].main 
            }}
          >
            {icon}
            <Typography 
              variant="h6" 
              component="h2" 
              sx={{ ml: 1 }}
            >
              {title}
            </Typography>
          </Box>
          
          <Typography 
            variant="body2" 
            color="text.secondary" 
            sx={{ mb: 2 }}
          >
            {description}
          </Typography>
          
          {count !== undefined && (
            <Typography 
              variant="h4" 
              component="p" 
              sx={{ 
                textAlign: 'right',
                color: theme.palette[color].main
              }}
            >
              {count}
            </Typography>
          )}
        </CardContent>
      </CardActionArea>
    </Card>
  );
};

const EntityTypeCard = ({ type, count, color }) => {
  const navigate = useNavigate();
  const theme = useTheme();
  
  // Convert type to readable format
  const formatType = (type) => {
    return type
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };
  
  return (
    <Card>
      <CardActionArea onClick={() => navigate(`/knowledge/entities?type=${type}`)}>
        <CardContent>
          <Typography
            gutterBottom
            variant="h6"
            component="h2"
            sx={{ color: color || theme.palette.primary.main }}
          >
            {formatType(type)}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {count} entities
          </Typography>
        </CardContent>
      </CardActionArea>
    </Card>
  );
};

// Main dashboard component
const KnowledgeDashboard = () => {
  const theme = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  
  // State
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  
  // Get statistics and entity types
  const { data: statistics, isLoading: statsLoading } = useQuery({
    queryKey: ['graphStats'],
    queryFn: () => fetchGraphData({ limit: 0 }).then(data => ({
      entityCount: data.nodes.length,
      relationshipCount: data.links.length,
    })),
  });
  
  const { data: entityTypeData, isLoading: typesLoading } = useQuery({
    queryKey: ['entityTypes'],
    queryFn: fetchEntityTypes,
  });
  
  // Handle search
  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/knowledge/search?query=${encodeURIComponent(searchQuery)}`);
    }
  };
  
  // Toggle drawer
  const toggleDrawer = () => {
    setDrawerOpen(!drawerOpen);
  };
  
  // Drawer content
  const drawerContent = (
    <Box sx={{ width: 250 }} role="presentation">
      <List>
        <ListItem>
          <Typography variant="h6">Knowledge Explorer</Typography>
        </ListItem>
        
        <Divider />
        
        <ListItemButton 
          selected={location.pathname === '/knowledge'}
          onClick={() => navigate('/knowledge')}
        >
          <ListItemIcon>
            <DashboardIcon />
          </ListItemIcon>
          <ListItemText primary="Dashboard" />
        </ListItemButton>
        
        <ListItemButton 
          selected={location.pathname === '/knowledge/graph'}
          onClick={() => navigate('/knowledge/graph')}
        >
          <ListItemIcon>
            <ExploreIcon />
          </ListItemIcon>
          <ListItemText primary="Knowledge Graph" />
        </ListItemButton>
        
        <ListItemButton 
          selected={location.pathname === '/knowledge/entities'}
          onClick={() => navigate('/knowledge/entities')}
        >
          <ListItemIcon>
            <CategoryIcon />
          </ListItemIcon>
          <ListItemText primary="Entities" />
        </ListItemButton>
        
        <ListItemButton 
          selected={location.pathname === '/knowledge/campaigns'}
          onClick={() => navigate('/knowledge/campaigns')}
        >
          <ListItemIcon>
            <CampaignIcon />
          </ListItemIcon>
          <ListItemText primary="Campaigns" />
        </ListItemButton>
      </List>
    </Box>
  );
  
  // Dashboard home content
  const DashboardHome = () => (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Knowledge Graph Explorer
      </Typography>
      
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {/* Summary cards */}
        <Grid item xs={12} sm={6} md={3}>
          <DashboardCard
            title="Entities"
            description="Explore knowledge entities by type, tag, or name"
            icon={<CategoryIcon fontSize="large" />}
            count={statistics?.entityCount || 0}
            to="/knowledge/entities"
            color="primary"
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <DashboardCard
            title="Campaigns"
            description="View campaign knowledge and related entities"
            icon={<CampaignIcon fontSize="large" />}
            to="/knowledge/campaigns"
            color="secondary"
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <DashboardCard
            title="Explore Graph"
            description="Interactive visualization of the knowledge graph"
            icon={<ExploreIcon fontSize="large" />}
            to="/knowledge/graph"
            color="info"
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <DashboardCard
            title="Relationships"
            description="Connections between knowledge entities"
            icon={<ExploreIcon fontSize="large" />}
            count={statistics?.relationshipCount || 0}
            to="/knowledge/graph"
            color="success"
          />
        </Grid>
      </Grid>
      
      {/* Entity types */}
      <Typography variant="h5" gutterBottom sx={{ mt: 4 }}>
        Entity Types
      </Typography>
      
      <Grid container spacing={2}>
        {typesLoading ? (
          <Grid item xs={12}>
            <CircularProgress size={24} />
          </Grid>
        ) : (
          entityTypeData?.map((type, index) => (
            <Grid item xs={6} sm={4} md={3} lg={2} key={type}>
              <EntityTypeCard 
                type={type} 
                count={10} 
                color={theme.palette.primary.main}
              />
            </Grid>
          ))
        )}
      </Grid>
      
      {/* Quick graph visualization */}
      <Typography variant="h5" gutterBottom sx={{ mt: 4 }}>
        Knowledge Graph
      </Typography>
      
      <Paper sx={{ height: 400, p: 0 }}>
        <KnowledgeGraphViewer />
      </Paper>
    </Box>
  );
  
  return (
    <Box sx={{ display: 'flex' }}>
      {/* App Bar */}
      <AppBar 
        position="fixed" 
        sx={{ 
          zIndex: theme => theme.zIndex.drawer + 1,
          backgroundColor: theme.palette.background.paper,
          color: theme.palette.text.primary,
          boxShadow: 1
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            edge="start"
            onClick={toggleDrawer}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
          
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            TISIT Knowledge Explorer
          </Typography>
          
          <Box component="form" onSubmit={handleSearch} sx={{ mr: 2 }}>
            <TextField
              size="small"
              placeholder="Search knowledge..."
              variant="outlined"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
              sx={{
                backgroundColor: theme.palette.background.default,
                borderRadius: 1,
                width: { xs: 150, sm: 250 }
              }}
            />
          </Box>
        </Toolbar>
      </AppBar>
      
      {/* Drawer */}
      <Drawer
        variant="temporary"
        open={drawerOpen}
        onClose={toggleDrawer}
        ModalProps={{ keepMounted: true }}
      >
        {drawerContent}
      </Drawer>
      
      {/* Main content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 0,
          width: '100%',
          mt: '64px', // Toolbar height
        }}
      >
        <Routes>
          <Route path="/" element={<DashboardHome />} />
          <Route path="/graph" element={
            <Box sx={{ height: 'calc(100vh - 64px)' }}>
              <KnowledgeGraphViewer />
            </Box>
          } />
          <Route path="/entities" element={<Typography>Entities View</Typography>} />
          <Route path="/entities/:entityId" element={<Typography>Entity Detail</Typography>} />
          <Route path="/campaigns" element={<Typography>Campaigns List</Typography>} />
          <Route path="/campaigns/:campaignName" element={<CampaignKnowledgeView />} />
          <Route path="/search" element={<Typography>Search Results</Typography>} />
        </Routes>
      </Box>
    </Box>
  );
};

export default KnowledgeDashboard;