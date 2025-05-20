// SPDX-License-Identifier: MIT
// Copyright (c) 2025 Vamsi Duvvuri

// Fifth Grade Explanation:
// This file shows all the information about an advertising campaign in an
// organized way. It's like a big poster board with all the important notes
// and pictures about a project.

// High School Explanation:
// This React component provides a structured view of campaign knowledge from the TISIT
// knowledge graph. It displays campaign details, audiences, creative approaches,
// assets, channels, and metrics in an organized, hierarchical format.

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';

// Import UI components
import {
  Alert,
  Avatar,
  Box,
  Breadcrumbs,
  Button,
  Card,
  CardContent,
  CardHeader,
  Chip,
  CircularProgress,
  Collapse,
  Divider,
  Grid,
  IconButton,
  Link,
  List,
  ListItem,
  ListItemAvatar,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Paper,
  Stack,
  Tab,
  Tabs,
  Tooltip,
  Typography,
  useTheme,
} from '@mui/material';

// Import icons
import {
  Campaign as CampaignIcon,
  Group as AudienceIcon,
  Brush as CreativeIcon,
  Image as AssetIcon,
  Router as ChannelIcon,
  Analytics as MetricIcon,
  Lightbulb as InsightIcon,
  Settings as StrategyIcon,
  Visibility as ViewIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  ArrowBack as ArrowBackIcon,
} from '@mui/icons-material';

// Import API functions
import { getCampaignKnowledge } from './api';

// Import knowledge graph viewer
import KnowledgeGraphViewer from './KnowledgeGraphViewer';

// Entity type to icon mapping
const ENTITY_ICONS = {
  campaign: <CampaignIcon />,
  audience_segment: <AudienceIcon />,
  creative_approach: <CreativeIcon />,
  channel: <ChannelIcon />,
  strategy: <StrategyIcon />,
  metric: <MetricIcon />,
  brand: <CampaignIcon />,
  message: <InsightIcon />,
  asset: <AssetIcon />,
};

// Entity type to color mapping
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
};

const CampaignKnowledgeView = () => {
  const theme = useTheme();
  const { campaignName } = useParams();
  const navigate = useNavigate();
  
  // State
  const [activeTab, setActiveTab] = useState(0);
  const [expandedSections, setExpandedSections] = useState({
    audiences: true,
    creative_approaches: true,
    assets: true,
    channels: true,
    metrics: false,
    insights: false,
  });
  
  // Fetch campaign knowledge
  const { 
    data: campaignKnowledge, 
    isLoading, 
    isError, 
    error,
    refetch 
  } = useQuery({
    queryKey: ['campaignKnowledge', campaignName],
    queryFn: () => getCampaignKnowledge(campaignName),
    enabled: !!campaignName,
  });
  
  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };
  
  // Handle section toggle
  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };
  
  // Navigate to entity detail
  const navigateToEntity = (entityId) => {
    navigate(`/knowledge/entities/${entityId}`);
  };
  
  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }
  
  if (isError) {
    return (
      <Box sx={{ p: 2 }}>
        <Alert severity="error">
          Error loading campaign knowledge: {error.message}
        </Alert>
        <Button 
          variant="outlined" 
          sx={{ mt: 2 }} 
          onClick={() => refetch()}
        >
          Retry
        </Button>
      </Box>
    );
  }
  
  // If campaign not found
  if (!campaignKnowledge || campaignKnowledge.error) {
    return (
      <Box sx={{ p: 2 }}>
        <Alert severity="warning">
          Campaign not found: {campaignName}
        </Alert>
        <Button 
          variant="outlined" 
          sx={{ mt: 2 }} 
          onClick={() => navigate('/knowledge/campaigns')}
          startIcon={<ArrowBackIcon />}
        >
          Back to Campaigns
        </Button>
      </Box>
    );
  }
  
  return (
    <Box sx={{ p: 2 }}>
      {/* Breadcrumbs navigation */}
      <Breadcrumbs sx={{ mb: 2 }}>
        <Link 
          component="button" 
          color="inherit" 
          onClick={() => navigate('/knowledge')}
        >
          Knowledge Graph
        </Link>
        <Link 
          component="button" 
          color="inherit" 
          onClick={() => navigate('/knowledge/campaigns')}
        >
          Campaigns
        </Link>
        <Typography color="text.primary">{campaignKnowledge.campaign.name}</Typography>
      </Breadcrumbs>
      
      {/* Campaign header */}
      <Card sx={{ mb: 3 }}>
        <CardHeader
          avatar={
            <Avatar sx={{ bgcolor: ENTITY_COLORS.campaign }}>
              <CampaignIcon />
            </Avatar>
          }
          title={
            <Typography variant="h5" component="h1">
              {campaignKnowledge.campaign.name}
            </Typography>
          }
          subheader={campaignKnowledge.campaign.description}
        />
        <CardContent>
          <Grid container spacing={2}>
            {/* Campaign metadata */}
            {campaignKnowledge.campaign.metadata && (
              <>
                {campaignKnowledge.campaign.metadata.client && (
                  <Grid item xs={12} sm={6} md={3}>
                    <Typography variant="subtitle2" color="text.secondary">Client</Typography>
                    <Typography variant="body1">{campaignKnowledge.campaign.metadata.client}</Typography>
                  </Grid>
                )}
                
                {campaignKnowledge.campaign.metadata.budget && (
                  <Grid item xs={12} sm={6} md={3}>
                    <Typography variant="subtitle2" color="text.secondary">Budget</Typography>
                    <Typography variant="body1">
                      ${Number(campaignKnowledge.campaign.metadata.budget).toLocaleString()}
                    </Typography>
                  </Grid>
                )}
                
                {campaignKnowledge.campaign.metadata.start_date && (
                  <Grid item xs={12} sm={6} md={3}>
                    <Typography variant="subtitle2" color="text.secondary">Start Date</Typography>
                    <Typography variant="body1">{campaignKnowledge.campaign.metadata.start_date}</Typography>
                  </Grid>
                )}
                
                {campaignKnowledge.campaign.metadata.end_date && (
                  <Grid item xs={12} sm={6} md={3}>
                    <Typography variant="subtitle2" color="text.secondary">End Date</Typography>
                    <Typography variant="body1">{campaignKnowledge.campaign.metadata.end_date}</Typography>
                  </Grid>
                )}
                
                {campaignKnowledge.campaign.metadata.status && (
                  <Grid item xs={12} sm={6} md={3}>
                    <Typography variant="subtitle2" color="text.secondary">Status</Typography>
                    <Chip 
                      label={campaignKnowledge.campaign.metadata.status.toUpperCase()} 
                      color={
                        campaignKnowledge.campaign.metadata.status === 'active' ? 'success' :
                        campaignKnowledge.campaign.metadata.status === 'draft' ? 'default' :
                        campaignKnowledge.campaign.metadata.status === 'completed' ? 'primary' :
                        'default'
                      }
                      size="small"
                    />
                  </Grid>
                )}
              </>
            )}
            
            {/* Brand */}
            {campaignKnowledge.brand && campaignKnowledge.brand.length > 0 && (
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="subtitle2" color="text.secondary">Brand</Typography>
                <Typography variant="body1">{campaignKnowledge.brand[0].name}</Typography>
              </Grid>
            )}
          </Grid>
        </CardContent>
      </Card>
      
      {/* Tab navigation */}
      <Paper sx={{ mb: 3 }}>
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          variant="scrollable"
          scrollButtons="auto"
        >
          <Tab label="Overview" />
          <Tab label="Knowledge Graph" />
        </Tabs>
      </Paper>
      
      {/* Tab content */}
      <Box role="tabpanel" hidden={activeTab !== 0}>
        {activeTab === 0 && (
          <Grid container spacing={3}>
            {/* Audiences */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardHeader
                  title={
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <AudienceIcon sx={{ mr: 1 }} />
                      <Typography variant="h6">Target Audiences</Typography>
                      <IconButton
                        onClick={() => toggleSection('audiences')}
                        sx={{ ml: 'auto' }}
                        size="small"
                      >
                        {expandedSections.audiences ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                      </IconButton>
                    </Box>
                  }
                />
                <Collapse in={expandedSections.audiences}>
                  <CardContent>
                    {campaignKnowledge.audiences && campaignKnowledge.audiences.length > 0 ? (
                      <List>
                        {campaignKnowledge.audiences.map(audience => (
                          <ListItem 
                            key={audience.id}
                            secondaryAction={
                              <IconButton 
                                edge="end" 
                                onClick={() => navigateToEntity(audience.id)}
                              >
                                <ViewIcon />
                              </IconButton>
                            }
                          >
                            <ListItemAvatar>
                              <Avatar sx={{ bgcolor: ENTITY_COLORS.audience_segment }}>
                                <AudienceIcon />
                              </Avatar>
                            </ListItemAvatar>
                            <ListItemText
                              primary={audience.name}
                              secondary={audience.description}
                            />
                          </ListItem>
                        ))}
                      </List>
                    ) : (
                      <Typography variant="body2" color="text.secondary">
                        No audience segments defined.
                      </Typography>
                    )}
                  </CardContent>
                </Collapse>
              </Card>
            </Grid>
            
            {/* Creative Approaches */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardHeader
                  title={
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <CreativeIcon sx={{ mr: 1 }} />
                      <Typography variant="h6">Creative Approaches</Typography>
                      <IconButton
                        onClick={() => toggleSection('creative_approaches')}
                        sx={{ ml: 'auto' }}
                        size="small"
                      >
                        {expandedSections.creative_approaches ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                      </IconButton>
                    </Box>
                  }
                />
                <Collapse in={expandedSections.creative_approaches}>
                  <CardContent>
                    {campaignKnowledge.creative_approaches && campaignKnowledge.creative_approaches.length > 0 ? (
                      <List>
                        {campaignKnowledge.creative_approaches.map(approach => (
                          <ListItem 
                            key={approach.id}
                            secondaryAction={
                              <IconButton 
                                edge="end" 
                                onClick={() => navigateToEntity(approach.id)}
                              >
                                <ViewIcon />
                              </IconButton>
                            }
                          >
                            <ListItemAvatar>
                              <Avatar sx={{ bgcolor: ENTITY_COLORS.creative_approach }}>
                                <CreativeIcon />
                              </Avatar>
                            </ListItemAvatar>
                            <ListItemText
                              primary={approach.name}
                              secondary={approach.description}
                            />
                          </ListItem>
                        ))}
                      </List>
                    ) : (
                      <Typography variant="body2" color="text.secondary">
                        No creative approaches defined.
                      </Typography>
                    )}
                  </CardContent>
                </Collapse>
              </Card>
            </Grid>
            
            {/* Assets */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardHeader
                  title={
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <AssetIcon sx={{ mr: 1 }} />
                      <Typography variant="h6">Creative Assets</Typography>
                      <IconButton
                        onClick={() => toggleSection('assets')}
                        sx={{ ml: 'auto' }}
                        size="small"
                      >
                        {expandedSections.assets ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                      </IconButton>
                    </Box>
                  }
                />
                <Collapse in={expandedSections.assets}>
                  <CardContent>
                    {campaignKnowledge.assets && campaignKnowledge.assets.length > 0 ? (
                      <List>
                        {campaignKnowledge.assets.map(asset => (
                          <ListItem 
                            key={asset.id}
                            secondaryAction={
                              <IconButton 
                                edge="end" 
                                onClick={() => navigateToEntity(asset.id)}
                              >
                                <ViewIcon />
                              </IconButton>
                            }
                          >
                            <ListItemAvatar>
                              <Avatar sx={{ bgcolor: ENTITY_COLORS.asset }}>
                                <AssetIcon />
                              </Avatar>
                            </ListItemAvatar>
                            <ListItemText
                              primary={asset.name}
                              secondary={asset.description}
                            />
                          </ListItem>
                        ))}
                      </List>
                    ) : (
                      <Typography variant="body2" color="text.secondary">
                        No creative assets defined.
                      </Typography>
                    )}
                  </CardContent>
                </Collapse>
              </Card>
            </Grid>
            
            {/* Channels */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardHeader
                  title={
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <ChannelIcon sx={{ mr: 1 }} />
                      <Typography variant="h6">Media Channels</Typography>
                      <IconButton
                        onClick={() => toggleSection('channels')}
                        sx={{ ml: 'auto' }}
                        size="small"
                      >
                        {expandedSections.channels ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                      </IconButton>
                    </Box>
                  }
                />
                <Collapse in={expandedSections.channels}>
                  <CardContent>
                    {campaignKnowledge.channels && campaignKnowledge.channels.length > 0 ? (
                      <List>
                        {campaignKnowledge.channels.map(channel => (
                          <ListItem 
                            key={channel.id}
                            secondaryAction={
                              <IconButton 
                                edge="end" 
                                onClick={() => navigateToEntity(channel.id)}
                              >
                                <ViewIcon />
                              </IconButton>
                            }
                          >
                            <ListItemAvatar>
                              <Avatar sx={{ bgcolor: ENTITY_COLORS.channel }}>
                                <ChannelIcon />
                              </Avatar>
                            </ListItemAvatar>
                            <ListItemText
                              primary={channel.name}
                              secondary={channel.description || 'No description available'}
                            />
                          </ListItem>
                        ))}
                      </List>
                    ) : (
                      <Typography variant="body2" color="text.secondary">
                        No media channels defined.
                      </Typography>
                    )}
                  </CardContent>
                </Collapse>
              </Card>
            </Grid>
            
            {/* Performance Metrics */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardHeader
                  title={
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <MetricIcon sx={{ mr: 1 }} />
                      <Typography variant="h6">Performance Metrics</Typography>
                      <IconButton
                        onClick={() => toggleSection('metrics')}
                        sx={{ ml: 'auto' }}
                        size="small"
                      >
                        {expandedSections.metrics ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                      </IconButton>
                    </Box>
                  }
                />
                <Collapse in={expandedSections.metrics}>
                  <CardContent>
                    {campaignKnowledge.metrics && campaignKnowledge.metrics.length > 0 ? (
                      <List>
                        {campaignKnowledge.metrics.map(metric => (
                          <ListItem 
                            key={metric.id}
                            secondaryAction={
                              <IconButton 
                                edge="end" 
                                onClick={() => navigateToEntity(metric.id)}
                              >
                                <ViewIcon />
                              </IconButton>
                            }
                          >
                            <ListItemAvatar>
                              <Avatar sx={{ bgcolor: ENTITY_COLORS.metric }}>
                                <MetricIcon />
                              </Avatar>
                            </ListItemAvatar>
                            <ListItemText
                              primary={metric.name}
                              secondary={metric.description}
                            />
                          </ListItem>
                        ))}
                      </List>
                    ) : (
                      <Typography variant="body2" color="text.secondary">
                        No performance metrics defined.
                      </Typography>
                    )}
                  </CardContent>
                </Collapse>
              </Card>
            </Grid>
            
            {/* Insights */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardHeader
                  title={
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <InsightIcon sx={{ mr: 1 }} />
                      <Typography variant="h6">Insights & Recommendations</Typography>
                      <IconButton
                        onClick={() => toggleSection('insights')}
                        sx={{ ml: 'auto' }}
                        size="small"
                      >
                        {expandedSections.insights ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                      </IconButton>
                    </Box>
                  }
                />
                <Collapse in={expandedSections.insights}>
                  <CardContent>
                    {campaignKnowledge.insights && campaignKnowledge.insights.length > 0 ? (
                      <List>
                        {campaignKnowledge.insights.map(insight => (
                          <ListItem 
                            key={insight.id}
                            secondaryAction={
                              <IconButton 
                                edge="end" 
                                onClick={() => navigateToEntity(insight.id)}
                              >
                                <ViewIcon />
                              </IconButton>
                            }
                          >
                            <ListItemAvatar>
                              <Avatar sx={{ bgcolor: ENTITY_COLORS.message }}>
                                <InsightIcon />
                              </Avatar>
                            </ListItemAvatar>
                            <ListItemText
                              primary={insight.name}
                              secondary={insight.description}
                            />
                          </ListItem>
                        ))}
                      </List>
                    ) : (
                      <Typography variant="body2" color="text.secondary">
                        No insights or recommendations available.
                      </Typography>
                    )}
                  </CardContent>
                </Collapse>
              </Card>
            </Grid>
          </Grid>
        )}
      </Box>
      
      <Box role="tabpanel" hidden={activeTab !== 1}>
        {activeTab === 1 && (
          <Box sx={{ height: 600 }}>
            <KnowledgeGraphViewer 
              initialEntityId={campaignKnowledge.campaign.id}
              initialQuery={campaignKnowledge.campaign.name}
            />
          </Box>
        )}
      </Box>
    </Box>
  );
};

export default CampaignKnowledgeView;