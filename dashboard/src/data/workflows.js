// SPDX-License-Identifier: MIT
// Copyright (c) 2025 Vamsi Duvvuri

/**
 * Static workflow data extracted from agent workflow documentation.
 * This data represents the core structure of our agency's workflow subway map.
 */

// Define our agents (stations)
export const agents = [
  // Front Office Agents
  {
    id: "rachel_client",
    name: "Rachel Client",
    role: "Account Manager",
    office: "front",
    icon: "account_circle",
    position: { x: 100, y: 200 },
    color: "#2196f3", // Blue for front office
    description: "Client relationship management, campaign oversight, client satisfaction"
  },
  {
    id: "david_business",
    name: "David Business",
    role: "Business Development",
    office: "front",
    icon: "business",
    position: { x: 100, y: 300 },
    color: "#2196f3",
    description: "New business opportunities, sales pipeline, proposal development"
  },
  {
    id: "paul_pr",
    name: "Paul PR",
    role: "Public Relations Manager",
    office: "front",
    icon: "record_voice_over",
    position: { x: 100, y: 400 },
    color: "#2196f3",
    description: "PR strategy, media relations, brand reputation"
  },

  // Middle Office - Creative
  {
    id: "lucas_director",
    name: "Lucas Director",
    role: "Creative Director",
    office: "middle",
    icon: "palette",
    position: { x: 300, y: 150 },
    color: "#4caf50", // Green for middle office
    description: "Creative direction, concept development, brand storytelling"
  },
  {
    id: "emma_designer",
    name: "Emma Designer",
    role: "Art Director",
    office: "middle",
    icon: "brush",
    position: { x: 300, y: 250 },
    color: "#4caf50",
    description: "Visual design, brand aesthetics, creative execution"
  },
  {
    id: "nina_writer",
    name: "Nina Writer",
    role: "Copywriter",
    office: "middle",
    icon: "create",
    position: { x: 300, y: 350 },
    color: "#4caf50",
    description: "Messaging, copywriting, content creation"
  },
  {
    id: "frank_video",
    name: "Frank Video",
    role: "Video Specialist",
    office: "middle",
    icon: "videocam",
    position: { x: 300, y: 450 },
    color: "#4caf50",
    description: "Video production, editing, motion design"
  },
  {
    id: "sam_producer",
    name: "Sam Producer",
    role: "Production Manager",
    office: "middle",
    icon: "movie",
    position: { x: 380, y: 380 },
    color: "#4caf50",
    description: "Production management, asset coordination, quality control"
  },

  // Middle Office - Strategy
  {
    id: "carlos_planner",
    name: "Carlos Planner",
    role: "Campaign Strategist",
    office: "middle",
    icon: "architecture",
    position: { x: 380, y: 120 },
    color: "#4caf50",
    description: "Campaign strategy, planning, coordination"
  },
  {
    id: "simon_strategist",
    name: "Simon Strategist",
    role: "Brand Strategist",
    office: "middle",
    icon: "psychology",
    position: { x: 380, y: 200 },
    color: "#4caf50",
    description: "Brand strategy, positioning, value proposition"
  },
  {
    id: "olivia_researcher",
    name: "Olivia Researcher",
    role: "Audience Specialist",
    office: "middle",
    icon: "groups",
    position: { x: 380, y: 280 },
    color: "#4caf50",
    description: "Audience research, segmentation, insights"
  },

  // Middle Office - Media & Technical
  {
    id: "james_planner",
    name: "James Planner",
    role: "Media Planner",
    office: "middle",
    icon: "insert_chart",
    position: { x: 460, y: 180 },
    color: "#4caf50",
    description: "Media strategy, channel selection, budget allocation"
  },
  {
    id: "zara_buyer",
    name: "Zara Buyer",
    role: "Media Buyer",
    office: "middle",
    icon: "shopping_cart",
    position: { x: 460, y: 260 },
    color: "#4caf50",
    description: "Media buying, negotiation, placement"
  },
  {
    id: "max_optimizer",
    name: "Max Optimizer",
    role: "Campaign Manager",
    office: "middle",
    icon: "trending_up",
    position: { x: 460, y: 340 },
    color: "#4caf50",
    description: "Campaign implementation, monitoring, optimization"
  },
  {
    id: "sarah_social",
    name: "Sarah Social",
    role: "Social Media Specialist",
    office: "middle",
    icon: "public",
    position: { x: 460, y: 420 },
    color: "#4caf50",
    description: "Social media strategy, content, community engagement"
  },
  {
    id: "ben_engineer",
    name: "Ben Engineer",
    role: "Technical Lead",
    office: "middle",
    icon: "code",
    position: { x: 540, y: 300 },
    color: "#4caf50",
    description: "Technical implementation, tracking, measurement"
  },

  // Back Office
  {
    id: "maya_analyzer",
    name: "Maya Analyzer",
    role: "Market Analyst",
    office: "back",
    icon: "analytics",
    position: { x: 650, y: 150 },
    color: "#ff9800", // Orange for back office
    description: "Market research, data analysis, insights"
  },
  {
    id: "tina_data",
    name: "Tina Data",
    role: "Data Scientist",
    office: "back",
    icon: "data_usage",
    position: { x: 650, y: 250 },
    color: "#ff9800",
    description: "Advanced data analysis, predictive modeling, insights"
  },
  {
    id: "tom_compliance",
    name: "Tom Compliance",
    role: "Legal Analyst",
    office: "back",
    icon: "gavel",
    position: { x: 650, y: 350 },
    color: "#ff9800",
    description: "Legal compliance, risk management, governance"
  },
  {
    id: "alex_finance",
    name: "Alex Finance",
    role: "Financial Analyst",
    office: "back",
    icon: "account_balance",
    position: { x: 650, y: 450 },
    color: "#ff9800",
    description: "Budget management, financial planning, ROI analysis"
  },
  {
    id: "percy_project",
    name: "Percy Project",
    role: "Project Manager",
    office: "back",
    icon: "assignment",
    position: { x: 750, y: 200 },
    color: "#ff9800",
    description: "Project coordination, timeline management, resource allocation"
  },
  {
    id: "ruby_resources",
    name: "Ruby Resources",
    role: "Resource Manager",
    office: "back",
    icon: "people",
    position: { x: 750, y: 350 },
    color: "#ff9800",
    description: "Workforce planning, talent allocation, capacity management"
  },

  // Executive Team
  {
    id: "vee_ceo",
    name: "Vee CEO",
    role: "Chief Executive Officer",
    office: "executive",
    icon: "stars",
    position: { x: 400, y: 50 },
    color: "#9c27b0", // Purple for executive team
    description: "Overall leadership, strategic direction, company vision"
  },
  {
    id: "faz_cmo",
    name: "Faz CMO",
    role: "Chief Marketing Officer",
    office: "executive",
    icon: "campaign",
    position: { x: 300, y: 50 },
    color: "#9c27b0",
    description: "Marketing strategy, client growth, agency positioning"
  },
  {
    id: "mindy_cco",
    name: "Mindy CCO",
    role: "Chief Creative Officer",
    office: "executive",
    icon: "auto_awesome",
    position: { x: 500, y: 50 },
    color: "#9c27b0",
    description: "Creative vision, brand storytelling, creative capability"
  },
  {
    id: "barry_cofo",
    name: "Barry COFO",
    role: "Chief Operations and Finance Officer",
    office: "executive",
    icon: "work",
    position: { x: 600, y: 50 },
    color: "#9c27b0",
    description: "Operational excellence, financial health, back office leadership"
  },
  {
    id: "cee_cto",
    name: "Cee CTO",
    role: "Chief Technology Officer",
    office: "executive",
    icon: "memory",
    position: { x: 200, y: 50 },
    color: "#9c27b0",
    description: "Technology strategy, platform development, technical innovation"
  }
];

// Define our workflow lines (subway lines)
export const workflowLines = [
  {
    id: "brand_campaign",
    name: "Brand Campaign",
    type: "brand",
    color: "#e91e63", // Pink
    description: "Full marketing campaigns with comprehensive brand strategy"
  },
  {
    id: "digital_campaign",
    name: "Digital Campaign",
    type: "digital",
    color: "#2196f3", // Blue
    description: "Digital-focused campaigns with emphasis on online channels"
  },
  {
    id: "content_production",
    name: "Content Production",
    type: "content",
    color: "#4caf50", // Green
    description: "Content-centric workflows focused on asset creation"
  },
  {
    id: "social_media",
    name: "Social Media",
    type: "social",
    color: "#ff9800", // Orange
    description: "Social media campaign workflows"
  },
  {
    id: "analytics",
    name: "Analytics",
    type: "analytics",
    color: "#9c27b0", // Purple
    description: "Data-driven research and reporting workflows"
  },
  {
    id: "client_service",
    name: "Client Service",
    type: "client",
    color: "#795548", // Brown
    description: "Account management and client relationship workflows"
  }
];

// Define connections between agents (subway tracks)
export const connections = [
  // Brand Campaign Route - Primary path
  // Business Development → Rachel Client → Carlos Planner
  { id: "conn_1", source: "david_business", target: "rachel_client", lineId: "brand_campaign" },
  { id: "conn_2", source: "rachel_client", target: "carlos_planner", lineId: "brand_campaign" },
  
  // Research & Strategy Phase
  // Carlos Planner → Maya Analyzer
  { id: "conn_3", source: "carlos_planner", target: "maya_analyzer", lineId: "brand_campaign" },
  // Maya Analyzer → Olivia Researcher
  { id: "conn_4", source: "maya_analyzer", target: "olivia_researcher", lineId: "brand_campaign" },
  // Olivia Researcher → Simon Strategist
  { id: "conn_5", source: "olivia_researcher", target: "simon_strategist", lineId: "brand_campaign" },
  // Simon Strategist → Carlos Planner
  { id: "conn_6", source: "simon_strategist", target: "carlos_planner", lineId: "brand_campaign" },
  
  // Creative Development Phase
  // Carlos Planner → Lucas Director
  { id: "conn_7", source: "carlos_planner", target: "lucas_director", lineId: "brand_campaign" },
  // Lucas Director → Emma Designer
  { id: "conn_8", source: "lucas_director", target: "emma_designer", lineId: "brand_campaign" },
  // Lucas Director → Nina Writer
  { id: "conn_9", source: "lucas_director", target: "nina_writer", lineId: "brand_campaign" },
  // Emma Designer → Nina Writer (collaboration)
  { id: "conn_10", source: "emma_designer", target: "nina_writer", lineId: "brand_campaign" },
  // Nina Writer → Lucas Director (review)
  { id: "conn_11", source: "nina_writer", target: "lucas_director", lineId: "brand_campaign" },
  // Emma Designer → Lucas Director (review)
  { id: "conn_12", source: "emma_designer", target: "lucas_director", lineId: "brand_campaign" },
  
  // Media Planning Phase
  // Carlos Planner → James Planner
  { id: "conn_13", source: "carlos_planner", target: "james_planner", lineId: "brand_campaign" },
  // James Planner → Zara Buyer
  { id: "conn_14", source: "james_planner", target: "zara_buyer", lineId: "brand_campaign" },
  
  // Production & Implementation Phase
  // Lucas Director → Sam Producer
  { id: "conn_15", source: "lucas_director", target: "sam_producer", lineId: "brand_campaign" },
  // Sam Producer → Frank Video
  { id: "conn_16", source: "sam_producer", target: "frank_video", lineId: "brand_campaign" },
  // Sam Producer → Ben Engineer
  { id: "conn_17", source: "sam_producer", target: "ben_engineer", lineId: "brand_campaign" },
  // Lucas Director, James Planner → Max Optimizer
  { id: "conn_18", source: "lucas_director", target: "max_optimizer", lineId: "brand_campaign" },
  { id: "conn_19", source: "james_planner", target: "max_optimizer", lineId: "brand_campaign" },
  { id: "conn_20", source: "zara_buyer", target: "max_optimizer", lineId: "brand_campaign" },
  
  // Analysis & Reporting Phase
  // Max Optimizer → Maya Analyzer
  { id: "conn_21", source: "max_optimizer", target: "maya_analyzer", lineId: "brand_campaign" },
  // Maya Analyzer → Tina Data
  { id: "conn_22", source: "maya_analyzer", target: "tina_data", lineId: "brand_campaign" },
  // Tina Data → Carlos Planner
  { id: "conn_23", source: "tina_data", target: "carlos_planner", lineId: "brand_campaign" },
  // Carlos Planner → Rachel Client
  { id: "conn_24", source: "carlos_planner", target: "rachel_client", lineId: "brand_campaign" },
  
  // Digital Campaign Route
  // Rachel Client → Carlos Planner
  { id: "conn_25", source: "rachel_client", target: "carlos_planner", lineId: "digital_campaign" },
  // Carlos Planner → Maya Analyzer
  { id: "conn_26", source: "carlos_planner", target: "maya_analyzer", lineId: "digital_campaign" },
  // Carlos Planner → Ben Engineer
  { id: "conn_27", source: "carlos_planner", target: "ben_engineer", lineId: "digital_campaign" },
  // Maya Analyzer → Olivia Researcher
  { id: "conn_28", source: "maya_analyzer", target: "olivia_researcher", lineId: "digital_campaign" },
  // Olivia Researcher → Carlos Planner
  { id: "conn_29", source: "olivia_researcher", target: "carlos_planner", lineId: "digital_campaign" },
  // Carlos Planner → James Planner
  { id: "conn_30", source: "carlos_planner", target: "james_planner", lineId: "digital_campaign" },
  // Carlos Planner → Lucas Director
  { id: "conn_31", source: "carlos_planner", target: "lucas_director", lineId: "digital_campaign" },
  // Lucas Director → Emma Designer
  { id: "conn_32", source: "lucas_director", target: "emma_designer", lineId: "digital_campaign" },
  // Lucas Director → Nina Writer
  { id: "conn_33", source: "lucas_director", target: "nina_writer", lineId: "digital_campaign" },
  // Emma Designer, Nina Writer → Ben Engineer
  { id: "conn_34", source: "emma_designer", target: "ben_engineer", lineId: "digital_campaign" },
  { id: "conn_35", source: "nina_writer", target: "ben_engineer", lineId: "digital_campaign" },
  // Ben Engineer, James Planner → Max Optimizer
  { id: "conn_36", source: "ben_engineer", target: "max_optimizer", lineId: "digital_campaign" },
  { id: "conn_37", source: "james_planner", target: "max_optimizer", lineId: "digital_campaign" },
  // Max Optimizer → Maya Analyzer
  { id: "conn_38", source: "max_optimizer", target: "maya_analyzer", lineId: "digital_campaign" },
  // Maya Analyzer → Carlos Planner
  { id: "conn_39", source: "maya_analyzer", target: "carlos_planner", lineId: "digital_campaign" },
  // Carlos Planner → Rachel Client
  { id: "conn_40", source: "carlos_planner", target: "rachel_client", lineId: "digital_campaign" },
  
  // Content Production Route
  // Rachel Client → Carlos Planner
  { id: "conn_41", source: "rachel_client", target: "carlos_planner", lineId: "content_production" },
  // Carlos Planner → Lucas Director
  { id: "conn_42", source: "carlos_planner", target: "lucas_director", lineId: "content_production" },
  // Lucas Director → Nina Writer
  { id: "conn_43", source: "lucas_director", target: "nina_writer", lineId: "content_production" },
  // Lucas Director → Emma Designer
  { id: "conn_44", source: "lucas_director", target: "emma_designer", lineId: "content_production" },
  // Lucas Director → Frank Video
  { id: "conn_45", source: "lucas_director", target: "frank_video", lineId: "content_production" },
  // Nina Writer, Emma Designer, Frank Video → Sam Producer
  { id: "conn_46", source: "nina_writer", target: "sam_producer", lineId: "content_production" },
  { id: "conn_47", source: "emma_designer", target: "sam_producer", lineId: "content_production" },
  { id: "conn_48", source: "frank_video", target: "sam_producer", lineId: "content_production" },
  // Sam Producer → Lucas Director
  { id: "conn_49", source: "sam_producer", target: "lucas_director", lineId: "content_production" },
  // Lucas Director → Rachel Client
  { id: "conn_50", source: "lucas_director", target: "rachel_client", lineId: "content_production" },
  
  // Social Media Route
  // Rachel Client → Carlos Planner
  { id: "conn_51", source: "rachel_client", target: "carlos_planner", lineId: "social_media" },
  // Carlos Planner → Sarah Social
  { id: "conn_52", source: "carlos_planner", target: "sarah_social", lineId: "social_media" },
  // Sarah Social → Maya Analyzer
  { id: "conn_53", source: "sarah_social", target: "maya_analyzer", lineId: "social_media" },
  // Maya Analyzer → Olivia Researcher
  { id: "conn_54", source: "maya_analyzer", target: "olivia_researcher", lineId: "social_media" },
  // Olivia Researcher → Sarah Social
  { id: "conn_55", source: "olivia_researcher", target: "sarah_social", lineId: "social_media" },
  // Sarah Social → Lucas Director
  { id: "conn_56", source: "sarah_social", target: "lucas_director", lineId: "social_media" },
  // Lucas Director → Emma Designer
  { id: "conn_57", source: "lucas_director", target: "emma_designer", lineId: "social_media" },
  // Lucas Director → Nina Writer
  { id: "conn_58", source: "lucas_director", target: "nina_writer", lineId: "social_media" },
  // Emma Designer, Nina Writer → Sarah Social
  { id: "conn_59", source: "emma_designer", target: "sarah_social", lineId: "social_media" },
  { id: "conn_60", source: "nina_writer", target: "sarah_social", lineId: "social_media" },
  // Sarah Social → Max Optimizer
  { id: "conn_61", source: "sarah_social", target: "max_optimizer", lineId: "social_media" },
  // Max Optimizer → Maya Analyzer
  { id: "conn_62", source: "max_optimizer", target: "maya_analyzer", lineId: "social_media" },
  // Maya Analyzer → Carlos Planner
  { id: "conn_63", source: "maya_analyzer", target: "carlos_planner", lineId: "social_media" },
  // Carlos Planner → Rachel Client
  { id: "conn_64", source: "carlos_planner", target: "rachel_client", lineId: "social_media" },
  
  // Analytics Route
  // Rachel Client → Maya Analyzer
  { id: "conn_65", source: "rachel_client", target: "maya_analyzer", lineId: "analytics" },
  // Maya Analyzer → Tina Data
  { id: "conn_66", source: "maya_analyzer", target: "tina_data", lineId: "analytics" },
  // Tina Data → Olivia Researcher
  { id: "conn_67", source: "tina_data", target: "olivia_researcher", lineId: "analytics" },
  // Olivia Researcher → Tina Data
  { id: "conn_68", source: "olivia_researcher", target: "tina_data", lineId: "analytics" },
  // Tina Data → Maya Analyzer
  { id: "conn_69", source: "tina_data", target: "maya_analyzer", lineId: "analytics" },
  // Maya Analyzer → Rachel Client
  { id: "conn_70", source: "maya_analyzer", target: "rachel_client", lineId: "analytics" },
  
  // Client Service Route
  // Rachel Client → Paul PR
  { id: "conn_71", source: "rachel_client", target: "paul_pr", lineId: "client_service" },
  // Rachel Client → Carlos Planner
  { id: "conn_72", source: "rachel_client", target: "carlos_planner", lineId: "client_service" },
  // Rachel Client → Alex Finance
  { id: "conn_73", source: "rachel_client", target: "alex_finance", lineId: "client_service" },
  // Carlos Planner → Percy Project
  { id: "conn_74", source: "carlos_planner", target: "percy_project", lineId: "client_service" },
  // Percy Project → Ruby Resources
  { id: "conn_75", source: "percy_project", target: "ruby_resources", lineId: "client_service" },
  // Percy Project → Alex Finance
  { id: "conn_76", source: "percy_project", target: "alex_finance", lineId: "client_service" },
  // Alex Finance → Rachel Client
  { id: "conn_77", source: "alex_finance", target: "rachel_client", lineId: "client_service" },
  
  // Executive oversight connections
  // Faz CMO → Carlos Planner
  { id: "conn_78", source: "faz_cmo", target: "carlos_planner", lineId: "brand_campaign" },
  // Mindy CCO → Lucas Director
  { id: "conn_79", source: "mindy_cco", target: "lucas_director", lineId: "content_production" },
  // Barry COFO → Percy Project
  { id: "conn_80", source: "barry_cofo", target: "percy_project", lineId: "client_service" },
  // Cee CTO → Ben Engineer
  { id: "conn_81", source: "cee_cto", target: "ben_engineer", lineId: "digital_campaign" },
  // Vee CEO connections to other executives
  { id: "conn_82", source: "vee_ceo", target: "faz_cmo", lineId: "brand_campaign" },
  { id: "conn_83", source: "vee_ceo", target: "mindy_cco", lineId: "content_production" },
  { id: "conn_84", source: "vee_ceo", target: "barry_cofo", lineId: "client_service" },
  { id: "conn_85", source: "vee_ceo", target: "cee_cto", lineId: "digital_campaign" },
  
  // Cross-functional connections
  { id: "conn_86", source: "tom_compliance", target: "lucas_director", lineId: "brand_campaign" },
  { id: "conn_87", source: "tom_compliance", target: "max_optimizer", lineId: "digital_campaign" },
  { id: "conn_88", source: "tom_compliance", target: "paul_pr", lineId: "client_service" },
  
  // Add more connections here as needed...
];

// Define sample active campaigns (trains)
export const activeCampaigns = [
  {
    id: "campaign_1",
    name: "TechCorp Rebrand",
    clientId: "client_1",
    type: "brand",
    priority: 1,
    lineId: "brand_campaign",
    currentStationId: "lucas_director",
    previousStations: [
      { stationId: "david_business", enteredAt: "2025-04-01T09:00:00Z", exitedAt: "2025-04-01T11:30:00Z", duration: 9000 },
      { stationId: "rachel_client", enteredAt: "2025-04-01T11:30:00Z", exitedAt: "2025-04-02T14:00:00Z", duration: 95400 },
      { stationId: "carlos_planner", enteredAt: "2025-04-02T14:00:00Z", exitedAt: "2025-04-05T10:00:00Z", duration: 241200 },
      { stationId: "maya_analyzer", enteredAt: "2025-04-05T10:00:00Z", exitedAt: "2025-04-08T16:30:00Z", duration: 282600 },
      { stationId: "olivia_researcher", enteredAt: "2025-04-08T16:30:00Z", exitedAt: "2025-04-12T11:15:00Z", duration: 326700 },
      { stationId: "simon_strategist", enteredAt: "2025-04-12T11:15:00Z", exitedAt: "2025-04-18T09:45:00Z", duration: 512700 },
      { stationId: "carlos_planner", enteredAt: "2025-04-18T09:45:00Z", exitedAt: "2025-04-20T15:30:00Z", duration: 198300 }
    ],
    nextStationId: "emma_designer",
    status: "on-time",
    progress: 45,
    startedAt: "2025-04-01T09:00:00Z",
    estimatedCompletion: "2025-06-15T17:00:00Z"
  },
  {
    id: "campaign_2",
    name: "FoodHub App Launch",
    clientId: "client_2",
    type: "digital",
    priority: 2,
    lineId: "digital_campaign",
    currentStationId: "ben_engineer",
    previousStations: [
      { stationId: "rachel_client", enteredAt: "2025-04-05T13:15:00Z", exitedAt: "2025-04-06T16:45:00Z", duration: 99000 },
      { stationId: "carlos_planner", enteredAt: "2025-04-06T16:45:00Z", exitedAt: "2025-04-09T11:30:00Z", duration: 235500 },
      { stationId: "maya_analyzer", enteredAt: "2025-04-09T11:30:00Z", exitedAt: "2025-04-12T14:00:00Z", duration: 269400 },
      { stationId: "olivia_researcher", enteredAt: "2025-04-12T14:00:00Z", exitedAt: "2025-04-15T09:30:00Z", duration: 241800 },
      { stationId: "carlos_planner", enteredAt: "2025-04-15T09:30:00Z", exitedAt: "2025-04-16T16:15:00Z", duration: 110700 },
      { stationId: "lucas_director", enteredAt: "2025-04-16T16:15:00Z", exitedAt: "2025-04-20T11:45:00Z", duration: 326700 },
      { stationId: "emma_designer", enteredAt: "2025-04-20T11:45:00Z", exitedAt: "2025-04-25T15:30:00Z", duration: 455700 }
    ],
    nextStationId: "max_optimizer",
    status: "expedited",
    progress: 60,
    startedAt: "2025-04-05T13:15:00Z",
    estimatedCompletion: "2025-05-20T17:00:00Z"
  },
  {
    id: "campaign_3",
    name: "EcoStyle Summer Content",
    clientId: "client_3",
    type: "content",
    priority: 3,
    lineId: "content_production",
    currentStationId: "sam_producer",
    previousStations: [
      { stationId: "rachel_client", enteredAt: "2025-04-10T10:00:00Z", exitedAt: "2025-04-11T14:30:00Z", duration: 102600 },
      { stationId: "carlos_planner", enteredAt: "2025-04-11T14:30:00Z", exitedAt: "2025-04-13T16:15:00Z", duration: 184500 },
      { stationId: "lucas_director", enteredAt: "2025-04-13T16:15:00Z", exitedAt: "2025-04-17T10:45:00Z", duration: 325800 },
      { stationId: "nina_writer", enteredAt: "2025-04-17T10:45:00Z", exitedAt: "2025-04-21T15:30:00Z", duration: 373500 },
      { stationId: "emma_designer", enteredAt: "2025-04-21T15:30:00Z", exitedAt: "2025-04-26T11:15:00Z", duration: 413700 }
    ],
    nextStationId: "lucas_director",
    status: "on-time",
    progress: 70,
    startedAt: "2025-04-10T10:00:00Z",
    estimatedCompletion: "2025-05-15T17:00:00Z"
  },
  {
    id: "campaign_4",
    name: "SportBrand Social Campaign",
    clientId: "client_4",
    type: "social",
    priority: 2,
    lineId: "social_media",
    currentStationId: "sarah_social",
    previousStations: [
      { stationId: "rachel_client", enteredAt: "2025-04-15T09:30:00Z", exitedAt: "2025-04-16T11:45:00Z", duration: 94500 },
      { stationId: "carlos_planner", enteredAt: "2025-04-16T11:45:00Z", exitedAt: "2025-04-18T14:15:00Z", duration: 180000 }
    ],
    nextStationId: "maya_analyzer",
    status: "on-time",
    progress: 30,
    startedAt: "2025-04-15T09:30:00Z",
    estimatedCompletion: "2025-05-10T17:00:00Z"
  },
  {
    id: "campaign_5",
    name: "FinTech Market Analysis",
    clientId: "client_5",
    type: "analytics",
    priority: 3,
    lineId: "analytics",
    currentStationId: "tina_data",
    previousStations: [
      { stationId: "rachel_client", enteredAt: "2025-04-18T14:00:00Z", exitedAt: "2025-04-19T16:30:00Z", duration: 95400 },
      { stationId: "maya_analyzer", enteredAt: "2025-04-19T16:30:00Z", exitedAt: "2025-04-23T10:15:00Z", duration: 323700 }
    ],
    nextStationId: "olivia_researcher",
    status: "delayed",
    progress: 25,
    startedAt: "2025-04-18T14:00:00Z",
    estimatedCompletion: "2025-05-05T17:00:00Z"
  }
];

// Define workflow recipes (step-by-step journey definitions)
export const workflowRecipes = {
  brand_campaign: {
    name: "Brand Campaign Workflow",
    description: "Comprehensive branding campaign from strategy to execution",
    steps: [
      { step: 1, station: "david_business", name: "New Business Development" },
      { step: 2, station: "rachel_client", name: "Client Onboarding" },
      { step: 3, station: "carlos_planner", name: "Campaign Planning" },
      { step: 4, station: "maya_analyzer", name: "Market Research" },
      { step: 5, station: "olivia_researcher", name: "Audience Research" },
      { step: 6, station: "simon_strategist", name: "Brand Strategy" },
      { step: 7, station: "carlos_planner", name: "Strategy Integration" },
      { step: 8, station: "lucas_director", name: "Creative Direction" },
      { step: 9, station: "emma_designer", name: "Visual Design" },
      { step: 10, station: "nina_writer", name: "Copywriting" },
      { step: 11, station: "lucas_director", name: "Creative Review" },
      { step: 12, station: "james_planner", name: "Media Planning" },
      { step: 13, station: "zara_buyer", name: "Media Buying" },
      { step: 14, station: "sam_producer", name: "Production Management" },
      { step: 15, station: "ben_engineer", name: "Technical Implementation" },
      { step: 16, station: "max_optimizer", name: "Campaign Launch" },
      { step: 17, station: "maya_analyzer", name: "Performance Analysis" },
      { step: 18, station: "tina_data", name: "Data Analysis" },
      { step: 19, station: "carlos_planner", name: "Optimization Strategy" },
      { step: 20, station: "rachel_client", name: "Client Reporting" }
    ]
  },
  digital_campaign: {
    name: "Digital Campaign Workflow",
    description: "Digital-focused campaign workflow optimized for online channels",
    steps: [
      { step: 1, station: "rachel_client", name: "Campaign Brief" },
      { step: 2, station: "carlos_planner", name: "Digital Strategy" },
      { step: 3, station: "maya_analyzer", name: "Digital Channel Analysis" },
      { step: 4, station: "olivia_researcher", name: "Digital Audience Research" },
      { step: 5, station: "carlos_planner", name: "Digital Campaign Planning" },
      { step: 6, station: "james_planner", name: "Digital Media Planning" },
      { step: 7, station: "lucas_director", name: "Digital Creative Direction" },
      { step: 8, station: "emma_designer", name: "Digital Design" },
      { step: 9, station: "nina_writer", name: "Digital Copywriting" },
      { step: 10, station: "ben_engineer", name: "Technical Development" },
      { step: 11, station: "max_optimizer", name: "Digital Campaign Launch" },
      { step: 12, station: "maya_analyzer", name: "Digital Analytics" },
      { step: 13, station: "carlos_planner", name: "Campaign Optimization" },
      { step: 14, station: "rachel_client", name: "Performance Reporting" }
    ]
  },
  content_production: {
    name: "Content Production Workflow",
    description: "Content-focused workflow for producing various media assets",
    steps: [
      { step: 1, station: "rachel_client", name: "Content Brief" },
      { step: 2, station: "carlos_planner", name: "Content Strategy" },
      { step: 3, station: "lucas_director", name: "Content Direction" },
      { step: 4, station: "nina_writer", name: "Content Writing" },
      { step: 5, station: "emma_designer", name: "Visual Design" },
      { step: 6, station: "frank_video", name: "Video Production" },
      { step: 7, station: "sam_producer", name: "Production Management" },
      { step: 8, station: "lucas_director", name: "Content Review" },
      { step: 9, station: "rachel_client", name: "Client Approval" }
    ]
  },
  social_media: {
    name: "Social Media Campaign Workflow",
    description: "Social media focused campaign workflow",
    steps: [
      { step: 1, station: "rachel_client", name: "Social Campaign Brief" },
      { step: 2, station: "carlos_planner", name: "Social Strategy" },
      { step: 3, station: "sarah_social", name: "Social Channel Planning" },
      { step: 4, station: "maya_analyzer", name: "Social Audience Analysis" },
      { step: 5, station: "olivia_researcher", name: "Social Trends Research" },
      { step: 6, station: "sarah_social", name: "Content Calendar Planning" },
      { step: 7, station: "lucas_director", name: "Social Creative Direction" },
      { step: 8, station: "emma_designer", name: "Social Visual Design" },
      { step: 9, station: "nina_writer", name: "Social Copywriting" },
      { step: 10, station: "sarah_social", name: "Content Preparation" },
      { step: 11, station: "max_optimizer", name: "Campaign Launch & Monitoring" },
      { step: 12, station: "maya_analyzer", name: "Engagement Analysis" },
      { step: 13, station: "carlos_planner", name: "Strategy Refinement" },
      { step: 14, station: "rachel_client", name: "Performance Reporting" }
    ]
  },
  analytics: {
    name: "Analytics Project Workflow",
    description: "Data-driven research and analysis workflow",
    steps: [
      { step: 1, station: "rachel_client", name: "Analytics Brief" },
      { step: 2, station: "maya_analyzer", name: "Research Design" },
      { step: 3, station: "tina_data", name: "Data Collection Planning" },
      { step: 4, station: "olivia_researcher", name: "Audience Segmentation" },
      { step: 5, station: "tina_data", name: "Data Analysis" },
      { step: 6, station: "maya_analyzer", name: "Insight Development" },
      { step: 7, station: "rachel_client", name: "Insights Presentation" }
    ]
  },
  client_service: {
    name: "Client Service Workflow",
    description: "Account management and client relationship workflow",
    steps: [
      { step: 1, station: "rachel_client", name: "Client Engagement" },
      { step: 2, station: "paul_pr", name: "PR Planning" },
      { step: 3, station: "carlos_planner", name: "Strategic Planning" },
      { step: 4, station: "percy_project", name: "Project Setup" },
      { step: 5, station: "ruby_resources", name: "Resource Allocation" },
      { step: 6, station: "alex_finance", name: "Financial Planning" },
      { step: 7, station: "rachel_client", name: "Client Relationship Management" }
    ]
  }
};