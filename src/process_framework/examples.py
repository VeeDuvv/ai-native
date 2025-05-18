# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file shows how to use our business process system with real examples.
# It's like a demonstration that shows people how to follow the business recipes 
# we've created using our AI helpers.

# High School Explanation:
# This module provides example usage of the process framework integration. It
# demonstrates how to define, parse, and execute business processes using the
# framework, including agent integration and workflow execution.

import os
import json
import tempfile
import shutil
from typing import Dict, Any, List, Optional
import logging
import time

from .core import (
    ProcessFramework, Process, Activity, ProcessInput, ProcessOutput,
    ProcessRole, ProcessMetric, ProcessStatus
)
from .repository import ProcessRepository
from .interpreter import ProcessInterpreter
from .workflow import WorkflowEngine, WorkflowEvent
from .interface import BaseProcessAwareAgent, AgentWorkflowManager
from .parsers.json import JsonFrameworkParser


def create_example_framework() -> ProcessFramework:
    """Create an example process framework for demonstration.
    
    Returns:
        A sample process framework
    """
    # Create the framework
    framework = ProcessFramework(
        framework_id="example_framework",
        name="Example Ad Campaign Process Framework",
        version="1.0",
        description="A simple process framework for advertising campaigns",
        organization="AI-Native Ad Agency",
        website="https://ai-native-ad-agency.example.com",
        source="Generated example"
    )
    
    # Create inputs, outputs, and metrics
    target_audience_input = ProcessInput(
        id="target_audience",
        name="target_audience",
        description="Target audience for the campaign",
        data_type="object"
    )
    
    budget_input = ProcessInput(
        id="budget",
        name="budget",
        description="Campaign budget",
        data_type="number"
    )
    
    timeline_input = ProcessInput(
        id="timeline",
        name="timeline",
        description="Campaign timeline",
        data_type="object"
    )
    
    brand_guidelines_input = ProcessInput(
        id="brand_guidelines",
        name="brand_guidelines",
        description="Brand guidelines",
        data_type="object"
    )
    
    campaign_plan_output = ProcessOutput(
        id="campaign_plan",
        name="campaign_plan",
        description="Completed campaign plan",
        data_type="object"
    )
    
    creative_concepts_output = ProcessOutput(
        id="creative_concepts",
        name="creative_concepts",
        description="Creative concepts for the campaign",
        data_type="array"
    )
    
    media_plan_output = ProcessOutput(
        id="media_plan",
        name="media_plan",
        description="Media placement plan",
        data_type="object"
    )
    
    engagement_metric = ProcessMetric(
        id="engagement_rate",
        name="Engagement Rate",
        description="Percentage of audience that engages with the campaign",
        unit="percentage",
        target_value=5.0
    )
    
    conversion_metric = ProcessMetric(
        id="conversion_rate",
        name="Conversion Rate",
        description="Percentage of engaged users that convert",
        unit="percentage",
        target_value=2.0
    )
    
    # Create roles
    strategist_role = ProcessRole(
        id="campaign_strategist",
        name="Campaign Strategist",
        description="Responsible for overall campaign strategy"
    )
    
    creative_role = ProcessRole(
        id="creative_director",
        name="Creative Director",
        description="Responsible for creative direction and content"
    )
    
    media_role = ProcessRole(
        id="media_planner",
        name="Media Planner",
        description="Responsible for media planning and buying"
    )
    
    # Create the campaign process
    campaign_process = Process(
        process_id="campaign_process",
        name="Advertising Campaign Process",
        description="End-to-end process for creating and executing an ad campaign",
        inputs=[target_audience_input, budget_input, timeline_input, brand_guidelines_input],
        outputs=[campaign_plan_output],
        metrics=[engagement_metric, conversion_metric],
        roles=[strategist_role, creative_role, media_role]
    )
    
    # Create planning sub-process
    planning_process = Process(
        process_id="planning_process",
        name="Campaign Planning",
        description="Plan the overall campaign strategy and approach",
        inputs=[target_audience_input, budget_input, timeline_input, brand_guidelines_input],
        outputs=[campaign_plan_output],
        roles=[strategist_role]
    )
    
    # Create planning activities
    market_analysis_activity = Activity(
        activity_id="market_analysis",
        name="Market Analysis",
        description="Analyze the market landscape and competition",
        inputs=[target_audience_input],
        outputs=[
            ProcessOutput(
                id="market_analysis",
                name="market_analysis",
                description="Analysis of the market landscape",
                data_type="object"
            )
        ],
        agent_capabilities=["strategy.market_analysis"]
    )
    
    audience_segmentation_activity = Activity(
        activity_id="audience_segmentation",
        name="Audience Segmentation",
        description="Segment the target audience for targeted messaging",
        inputs=[target_audience_input],
        outputs=[
            ProcessOutput(
                id="audience_segments",
                name="audience_segments",
                description="Segmented audience groups",
                data_type="array"
            )
        ],
        agent_capabilities=["strategy.audience_segmentation"]
    )
    
    campaign_strategy_activity = Activity(
        activity_id="campaign_strategy",
        name="Campaign Strategy Development",
        description="Develop the overall campaign strategy",
        inputs=[
            target_audience_input,
            budget_input,
            timeline_input,
            ProcessInput(
                id="market_analysis",
                name="market_analysis",
                description="Analysis of the market landscape",
                data_type="object"
            ),
            ProcessInput(
                id="audience_segments",
                name="audience_segments",
                description="Segmented audience groups",
                data_type="array"
            )
        ],
        outputs=[campaign_plan_output],
        agent_capabilities=["strategy.campaign_planning"]
    )
    
    # Add activities to planning process
    planning_process.add_activity(market_analysis_activity)
    planning_process.add_activity(audience_segmentation_activity)
    planning_process.add_activity(campaign_strategy_activity)
    
    # Create creative sub-process
    creative_process = Process(
        process_id="creative_process",
        name="Creative Development",
        description="Develop creative concepts and content for the campaign",
        inputs=[campaign_plan_output, brand_guidelines_input],
        outputs=[creative_concepts_output],
        roles=[creative_role]
    )
    
    # Create creative activities
    concept_development_activity = Activity(
        activity_id="concept_development",
        name="Creative Concept Development",
        description="Develop creative concepts for the campaign",
        inputs=[campaign_plan_output, brand_guidelines_input],
        outputs=[
            ProcessOutput(
                id="creative_concepts_draft",
                name="creative_concepts_draft",
                description="Draft creative concepts",
                data_type="array"
            )
        ],
        agent_capabilities=["creative.concept_development"]
    )
    
    content_creation_activity = Activity(
        activity_id="content_creation",
        name="Content Creation",
        description="Create content based on approved concepts",
        inputs=[
            ProcessInput(
                id="creative_concepts_draft",
                name="creative_concepts_draft",
                description="Draft creative concepts",
                data_type="array"
            ),
            brand_guidelines_input
        ],
        outputs=[creative_concepts_output],
        agent_capabilities=["creative.content_creation"]
    )
    
    # Add activities to creative process
    creative_process.add_activity(concept_development_activity)
    creative_process.add_activity(content_creation_activity)
    
    # Create media sub-process
    media_process = Process(
        process_id="media_process",
        name="Media Planning",
        description="Plan media placements and buys for the campaign",
        inputs=[campaign_plan_output, budget_input, timeline_input],
        outputs=[media_plan_output],
        roles=[media_role]
    )
    
    # Create media activities
    channel_selection_activity = Activity(
        activity_id="channel_selection",
        name="Channel Selection",
        description="Select appropriate media channels for the campaign",
        inputs=[campaign_plan_output, target_audience_input],
        outputs=[
            ProcessOutput(
                id="selected_channels",
                name="selected_channels",
                description="Selected media channels",
                data_type="array"
            )
        ],
        agent_capabilities=["media.channel_selection"]
    )
    
    media_planning_activity = Activity(
        activity_id="media_planning",
        name="Media Planning",
        description="Create a detailed media plan",
        inputs=[
            ProcessInput(
                id="selected_channels",
                name="selected_channels",
                description="Selected media channels",
                data_type="array"
            ),
            budget_input,
            timeline_input
        ],
        outputs=[media_plan_output],
        agent_capabilities=["media.planning"]
    )
    
    # Add activities to media process
    media_process.add_activity(channel_selection_activity)
    media_process.add_activity(media_planning_activity)
    
    # Add sub-processes to main process
    campaign_process.add_sub_process(planning_process)
    campaign_process.add_sub_process(creative_process)
    campaign_process.add_sub_process(media_process)
    
    # Add to framework
    framework.add_process(campaign_process)
    
    return framework


class MarketAnalysisAgent(BaseProcessAwareAgent):
    """Example agent that performs market analysis activities."""
    
    def __init__(self, agent_id: str, name: str) -> None:
        """Initialize the market analysis agent.
        
        Args:
            agent_id: Unique identifier for the agent
            name: Human-readable name for the agent
        """
        super().__init__(agent_id, name)
        
        # Register activity handlers
        self.register_activity_handler(
            activity_id="market_analysis",
            handler=self._perform_market_analysis,
            requirements={
                "inputs": ["target_audience"],
                "outputs": ["market_analysis"]
            }
        )
        
        self.register_activity_handler(
            activity_id="audience_segmentation",
            handler=self._perform_audience_segmentation,
            requirements={
                "inputs": ["target_audience"],
                "outputs": ["audience_segments"]
            }
        )
    
    def _perform_market_analysis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform market analysis.
        
        Args:
            context: Execution context with inputs
            
        Returns:
            Analysis results
        """
        # In a real implementation, this would perform actual analysis
        # For this example, we'll just simulate it
        
        target_audience = context.get("target_audience", {})
        
        # Simulate processing time
        time.sleep(1)
        
        # Return simulated results
        return {
            "market_analysis": {
                "market_size": 1000000,
                "growth_rate": 5.2,
                "competitive_landscape": [
                    {"name": "Competitor A", "market_share": 25},
                    {"name": "Competitor B", "market_share": 20},
                    {"name": "Competitor C", "market_share": 15}
                ],
                "trends": [
                    "Mobile-first engagement",
                    "Video content dominance",
                    "Personalization"
                ],
                "opportunities": [
                    "Underserved younger demographic",
                    "Growing interest in sustainability"
                ],
                "threats": [
                    "Increasing ad fatigue",
                    "Rising customer acquisition costs"
                ]
            }
        }
    
    def _perform_audience_segmentation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform audience segmentation.
        
        Args:
            context: Execution context with inputs
            
        Returns:
            Segmentation results
        """
        # In a real implementation, this would perform actual segmentation
        # For this example, we'll just simulate it
        
        target_audience = context.get("target_audience", {})
        
        # Simulate processing time
        time.sleep(1)
        
        # Return simulated results
        return {
            "audience_segments": [
                {
                    "name": "Young Professionals",
                    "age_range": "25-34",
                    "demographics": {
                        "income": "Medium to High",
                        "education": "College Degree",
                        "location": "Urban"
                    },
                    "psychographics": {
                        "interests": ["Technology", "Travel", "Fitness"],
                        "values": ["Innovation", "Experience", "Well-being"]
                    },
                    "size": 35
                },
                {
                    "name": "Established Families",
                    "age_range": "35-44",
                    "demographics": {
                        "income": "High",
                        "education": "College Degree",
                        "location": "Suburban"
                    },
                    "psychographics": {
                        "interests": ["Home Improvement", "Family Activities", "Financial Planning"],
                        "values": ["Security", "Comfort", "Family"]
                    },
                    "size": 45
                },
                {
                    "name": "Early Adopters",
                    "age_range": "18-29",
                    "demographics": {
                        "income": "Medium",
                        "education": "Some College",
                        "location": "Urban"
                    },
                    "psychographics": {
                        "interests": ["Gaming", "Social Media", "Technology"],
                        "values": ["Innovation", "Connectivity", "Self-expression"]
                    },
                    "size": 20
                }
            ]
        }


class StrategyAgent(BaseProcessAwareAgent):
    """Example agent that performs campaign strategy activities."""
    
    def __init__(self, agent_id: str, name: str) -> None:
        """Initialize the strategy agent.
        
        Args:
            agent_id: Unique identifier for the agent
            name: Human-readable name for the agent
        """
        super().__init__(agent_id, name)
        
        # Register activity handlers
        self.register_activity_handler(
            activity_id="campaign_strategy",
            handler=self._develop_campaign_strategy,
            requirements={
                "inputs": [
                    "target_audience", 
                    "budget", 
                    "timeline", 
                    "market_analysis", 
                    "audience_segments"
                ],
                "outputs": ["campaign_plan"]
            }
        )
    
    def _develop_campaign_strategy(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Develop campaign strategy.
        
        Args:
            context: Execution context with inputs
            
        Returns:
            Campaign strategy
        """
        # In a real implementation, this would develop an actual strategy
        # For this example, we'll just simulate it
        
        target_audience = context.get("target_audience", {})
        budget = context.get("budget", 0)
        timeline = context.get("timeline", {})
        market_analysis = context.get("market_analysis", {})
        audience_segments = context.get("audience_segments", [])
        
        # Simulate processing time
        time.sleep(2)
        
        # Return simulated results
        return {
            "campaign_plan": {
                "campaign_name": "Innovation Everywhere",
                "objectives": [
                    "Increase brand awareness by 20%",
                    "Drive 10,000 qualified leads",
                    "Achieve 2.5% conversion rate"
                ],
                "key_messages": [
                    "Innovation made simple",
                    "Technology for everyone",
                    "The future is now"
                ],
                "target_segments": [segment["name"] for segment in audience_segments],
                "budget_allocation": {
                    "digital": 0.6 * budget,
                    "social": 0.3 * budget,
                    "traditional": 0.1 * budget
                },
                "timeline": {
                    "planning_phase": "2 weeks",
                    "creative_development": "4 weeks",
                    "production": "3 weeks",
                    "launch": timeline.get("start_date", "2025-06-01"),
                    "duration": timeline.get("duration", "12 weeks")
                },
                "success_metrics": [
                    "Impressions",
                    "Engagement rate",
                    "Click-through rate",
                    "Conversion rate",
                    "Return on ad spend"
                ]
            }
        }


class CreativeAgent(BaseProcessAwareAgent):
    """Example agent that performs creative activities."""
    
    def __init__(self, agent_id: str, name: str) -> None:
        """Initialize the creative agent.
        
        Args:
            agent_id: Unique identifier for the agent
            name: Human-readable name for the agent
        """
        super().__init__(agent_id, name)
        
        # Register activity handlers
        self.register_activity_handler(
            activity_id="concept_development",
            handler=self._develop_creative_concepts,
            requirements={
                "inputs": ["campaign_plan", "brand_guidelines"],
                "outputs": ["creative_concepts_draft"]
            }
        )
        
        self.register_activity_handler(
            activity_id="content_creation",
            handler=self._create_content,
            requirements={
                "inputs": ["creative_concepts_draft", "brand_guidelines"],
                "outputs": ["creative_concepts"]
            }
        )
    
    def _develop_creative_concepts(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Develop creative concepts.
        
        Args:
            context: Execution context with inputs
            
        Returns:
            Creative concepts
        """
        # In a real implementation, this would develop actual concepts
        # For this example, we'll just simulate it
        
        campaign_plan = context.get("campaign_plan", {})
        brand_guidelines = context.get("brand_guidelines", {})
        
        # Simulate processing time
        time.sleep(1.5)
        
        # Return simulated results
        return {
            "creative_concepts_draft": [
                {
                    "name": "Future Forward",
                    "tagline": "Step into tomorrow, today",
                    "concept": "Visuals of everyday people using advanced technology in simple ways, highlighting how our product makes innovation accessible to everyone.",
                    "tone": "Optimistic, empowering",
                    "visual_style": "Bright, clean, minimalist",
                    "key_visuals": [
                        "Person using product while commuting",
                        "Family enjoying product benefits at home",
                        "Professional boosting productivity with product"
                    ]
                },
                {
                    "name": "Innovation Simplified",
                    "tagline": "Complex technology. Simple living.",
                    "concept": "Before/after scenarios showing complicated tasks transformed into simple ones through our product. Emphasizes the 'simplicity' message.",
                    "tone": "Helpful, enlightening",
                    "visual_style": "Split-screen comparisons, clean transitions",
                    "key_visuals": [
                        "Split screen of complex task vs. simple solution",
                        "Timelapse showing efficiency gains",
                        "Close-up on satisfied user expressions"
                    ]
                },
                {
                    "name": "The Everyday Revolution",
                    "tagline": "Revolutionizing your everyday",
                    "concept": "Showcase how small, everyday moments are transformed by our technology, creating a subtle but powerful revolution in how people live and work.",
                    "tone": "Thoughtful, inspiring",
                    "visual_style": "Documentary-style, authentic moments, soft lighting",
                    "key_visuals": [
                        "Dawn to dusk timeline of product improving daily life",
                        "Close-ups of small moments made better",
                        "Community of users sharing experiences"
                    ]
                }
            ]
        }
    
    def _create_content(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create content based on approved concepts.
        
        Args:
            context: Execution context with inputs
            
        Returns:
            Finalized creative content
        """
        # In a real implementation, this would create actual content
        # For this example, we'll just simulate it
        
        creative_concepts_draft = context.get("creative_concepts_draft", [])
        brand_guidelines = context.get("brand_guidelines", {})
        
        # Simulate processing time
        time.sleep(2)
        
        # Return simulated results with expanded details
        concepts = creative_concepts_draft.copy()
        
        # Add additional details to concepts to simulate content creation
        for concept in concepts:
            concept["assets"] = [
                {
                    "type": "Video",
                    "title": f"{concept['name']} - 30s Main Spot",
                    "description": f"30-second video showcasing {concept['concept']}",
                    "specifications": {
                        "duration": "30 seconds",
                        "format": "16:9 HD",
                        "platforms": ["YouTube", "Instagram", "Website"]
                    },
                    "storyboard": "Link to storyboard would go here"
                },
                {
                    "type": "Social Media",
                    "title": f"{concept['name']} - Social Media Package",
                    "description": "Series of static and animated posts",
                    "specifications": {
                        "formats": ["1:1", "9:16", "4:5"],
                        "platforms": ["Instagram", "Facebook", "LinkedIn"],
                        "pieces": 12
                    },
                    "mockups": "Link to mockups would go here"
                },
                {
                    "type": "Display Ads",
                    "title": f"{concept['name']} - Digital Display Package",
                    "description": "Banner ads in various standard sizes",
                    "specifications": {
                        "sizes": ["300x250", "728x90", "160x600", "320x50"],
                        "platforms": ["Google Display Network", "Website Banners"],
                        "pieces": 8
                    },
                    "mockups": "Link to mockups would go here"
                }
            ]
            concept["messaging"] = {
                "headlines": [
                    f"{concept['tagline']}",
                    f"Discover the power of {concept['name']}",
                    "Innovation that works for you"
                ],
                "body_copy": [
                    "Experience technology that adapts to your life, not the other way around.",
                    "We've reimagined what technology can do for you everyday.",
                    "Simple, powerful, and designed with you in mind."
                ],
                "calls_to_action": [
                    "Learn more",
                    "See it in action",
                    "Join the revolution",
                    "Try it today"
                ]
            }
        
        return {
            "creative_concepts": concepts
        }


class MediaAgent(BaseProcessAwareAgent):
    """Example agent that performs media planning activities."""
    
    def __init__(self, agent_id: str, name: str) -> None:
        """Initialize the media agent.
        
        Args:
            agent_id: Unique identifier for the agent
            name: Human-readable name for the agent
        """
        super().__init__(agent_id, name)
        
        # Register activity handlers
        self.register_activity_handler(
            activity_id="channel_selection",
            handler=self._select_channels,
            requirements={
                "inputs": ["campaign_plan", "target_audience"],
                "outputs": ["selected_channels"]
            }
        )
        
        self.register_activity_handler(
            activity_id="media_planning",
            handler=self._create_media_plan,
            requirements={
                "inputs": ["selected_channels", "budget", "timeline"],
                "outputs": ["media_plan"]
            }
        )
    
    def _select_channels(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Select appropriate media channels.
        
        Args:
            context: Execution context with inputs
            
        Returns:
            Selected channels
        """
        # In a real implementation, this would select actual channels
        # For this example, we'll just simulate it
        
        campaign_plan = context.get("campaign_plan", {})
        target_audience = context.get("target_audience", {})
        
        # Simulate processing time
        time.sleep(1)
        
        # Return simulated results
        return {
            "selected_channels": [
                {
                    "name": "Social Media",
                    "platforms": ["Instagram", "Facebook", "LinkedIn", "TikTok"],
                    "rationale": "High engagement with target demographic, strong visual format for creative concepts",
                    "metrics": ["Impressions", "Engagement", "Click-through", "Video Completion Rate"],
                    "audience_match": 85
                },
                {
                    "name": "Search",
                    "platforms": ["Google Ads", "Bing Ads"],
                    "rationale": "Captures high-intent users actively searching for solutions",
                    "metrics": ["Impressions", "Click-through", "Conversion", "Cost-per-Acquisition"],
                    "audience_match": 75
                },
                {
                    "name": "Display",
                    "platforms": ["Google Display Network", "Programmatic"],
                    "rationale": "Wide reach and retargeting capabilities",
                    "metrics": ["Impressions", "Click-through", "View-through Conversions"],
                    "audience_match": 70
                },
                {
                    "name": "Video",
                    "platforms": ["YouTube", "OTT/CTV"],
                    "rationale": "Strong storytelling medium for brand messaging",
                    "metrics": ["Views", "Completion Rate", "Brand Lift"],
                    "audience_match": 80
                },
                {
                    "name": "Audio",
                    "platforms": ["Spotify", "Podcast Advertising"],
                    "rationale": "Growing channel with targeted reach to specific interest groups",
                    "metrics": ["Listens", "Completion Rate", "Brand Recall"],
                    "audience_match": 65
                }
            ]
        }
    
    def _create_media_plan(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create a detailed media plan.
        
        Args:
            context: Execution context with inputs
            
        Returns:
            Media plan
        """
        # In a real implementation, this would create an actual media plan
        # For this example, we'll just simulate it
        
        selected_channels = context.get("selected_channels", [])
        budget = context.get("budget", 0)
        timeline = context.get("timeline", {})
        
        # Simulate processing time
        time.sleep(2)
        
        # Calculate budget allocation
        total_match_points = sum(channel["audience_match"] for channel in selected_channels)
        channel_budgets = {}
        
        for channel in selected_channels:
            allocation = (channel["audience_match"] / total_match_points) * budget
            channel_budgets[channel["name"]] = allocation
        
        # Return simulated results
        return {
            "media_plan": {
                "total_budget": budget,
                "channel_allocation": channel_budgets,
                "phasing": {
                    "awareness_phase": {
                        "start": timeline.get("start_date", "2025-06-01"),
                        "duration": "4 weeks",
                        "budget_percentage": 40,
                        "primary_channels": ["Video", "Display", "Audio"]
                    },
                    "consideration_phase": {
                        "start": "2025-07-01",  # Example date
                        "duration": "4 weeks",
                        "budget_percentage": 35,
                        "primary_channels": ["Social Media", "Display", "Audio"]
                    },
                    "conversion_phase": {
                        "start": "2025-08-01",  # Example date
                        "duration": "4 weeks",
                        "budget_percentage": 25,
                        "primary_channels": ["Search", "Social Media", "Display"]
                    }
                },
                "channels": [
                    {
                        **channel,
                        "budget": channel_budgets[channel["name"]],
                        "placements": [
                            {
                                "platform": platform,
                                "ad_units": ["Standard units appropriate for platform"],
                                "targeting": ["Demographics", "Interests", "Behaviors"],
                                "budget_percentage": 100 / len(channel["platforms"])
                            }
                            for platform in channel["platforms"]
                        ]
                    }
                    for channel in selected_channels
                ],
                "optimizations": [
                    "Weekly performance reviews",
                    "A/B testing of creative executions",
                    "Budget reallocation based on channel performance",
                    "Audience targeting refinement"
                ],
                "projected_results": {
                    "impressions": budget * 1000,  # Simplified calculation
                    "engagements": budget * 50,
                    "clicks": budget * 20,
                    "conversions": budget * 0.5
                }
            }
        }


def run_workflow_example():
    """Run a complete workflow example using the process framework.
    
    This function demonstrates how to use the process framework to execute
    a complete business process with multiple agents.
    """
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger("ProcessFrameworkExample")
    
    # Create a temporary directory for repositories and workflows
    temp_dir = tempfile.mkdtemp()
    try:
        # Create directories
        repo_dir = os.path.join(temp_dir, "repository")
        workflow_dir = os.path.join(temp_dir, "workflows")
        os.makedirs(repo_dir, exist_ok=True)
        os.makedirs(workflow_dir, exist_ok=True)
        
        logger.info("Setting up process framework example...")
        
        # Create example framework
        framework = create_example_framework()
        
        # Set up repository
        repository = ProcessRepository(repo_dir)
        
        # Save framework to repository
        parser = JsonFrameworkParser()
        with open(os.path.join(repo_dir, "example_framework.json"), 'w') as f:
            f.write(parser.to_json(framework))
            
        # Load framework into repository
        repository.save_framework(framework)
        
        # Set up workflow engine
        workflow_engine = WorkflowEngine(repository, workflow_dir)
        
        # Define event listener
        def event_listener(event: WorkflowEvent):
            logger.info(f"Event: {event.event_type.value} - "
                      f"Process: {event.process_id}, "
                      f"Activity: {event.activity_id or 'N/A'}, "
                      f"Agent: {event.agent_id or 'N/A'}")
            
        # Add event listener
        workflow_engine.add_event_listener(event_listener)
        
        # Create agents
        market_analysis_agent = MarketAnalysisAgent("market_agent", "Market Analysis Agent")
        strategy_agent = StrategyAgent("strategy_agent", "Strategy Agent")
        creative_agent = CreativeAgent("creative_agent", "Creative Agent")
        media_agent = MediaAgent("media_agent", "Media Agent")
        
        # Create workflow manager
        workflow_manager = AgentWorkflowManager(workflow_engine)
        
        # Register agents
        workflow_manager.register_agent(market_analysis_agent)
        workflow_manager.register_agent(strategy_agent)
        workflow_manager.register_agent(creative_agent)
        workflow_manager.register_agent(media_agent)
        
        # Define initial context
        initial_context = {
            "target_audience": {
                "demographic": {
                    "age_range": "25-45",
                    "gender": "All",
                    "income_level": "Middle to Upper",
                    "education": "College degree or higher",
                    "location": "Urban and suburban areas"
                },
                "psychographic": {
                    "interests": ["Technology", "Innovation", "Productivity", "Professional Development"],
                    "behaviors": ["Early technology adopters", "Active on social media", "Research before purchase"],
                    "pain_points": ["Complexity of technology", "Time management", "Information overload"]
                }
            },
            "budget": 500000,
            "timeline": {
                "start_date": "2025-06-01",
                "end_date": "2025-08-31",
                "duration": "12 weeks"
            },
            "brand_guidelines": {
                "colors": {
                    "primary": "#0052CC",
                    "secondary": "#00B8D9",
                    "accent": "#36B37E"
                },
                "typography": {
                    "primary_font": "Roboto",
                    "secondary_font": "Montserrat"
                },
                "voice": {
                    "tone": "Professional but approachable",
                    "personality": ["Innovative", "Helpful", "Expert", "Forward-thinking"]
                },
                "logo_usage": {
                    "clear_space": "Equal to the height of the logo on all sides",
                    "minimum_size": "30px height for digital, 0.5 inches for print"
                }
            }
        }
        
        # Start a process instance
        logger.info("Starting campaign process...")
        process_instance_id = workflow_engine.start_process(
            process_id="campaign_process",
            framework_id="example_framework",
            initial_context=initial_context
        )
        
        if not process_instance_id:
            logger.error("Failed to start process")
            return
            
        logger.info(f"Process instance started: {process_instance_id}")
        
        # Main workflow loop
        process_complete = False
        max_iterations = 100  # Safety limit
        iteration = 0
        
        while not process_complete and iteration < max_iterations:
            iteration += 1
            logger.info(f"Workflow iteration {iteration}")
            
            # Get process instance
            instance = workflow_engine.get_process_instance(process_instance_id)
            if not instance:
                logger.error("Process instance not found")
                break
                
            # Check if process is complete
            if instance.status in [ProcessStatus.COMPLETED, ProcessStatus.FAILED]:
                process_complete = True
                logger.info(f"Process is {instance.status.value}")
                break
                
            # Check for agent assignments
            for agent in [market_analysis_agent, strategy_agent, creative_agent, media_agent]:
                assignments = workflow_manager.get_agent_assignments(agent)
                
                for assignment in assignments:
                    activity_instance_id = assignment["activity_instance_id"]
                    activity_id = assignment["activity_id"]
                    
                    logger.info(f"Agent {agent.name} executing activity {activity_id}")
                    
                    try:
                        # Execute the activity
                        outputs = workflow_manager.execute_activity(agent, activity_instance_id)
                        logger.info(f"Activity {activity_id} completed successfully")
                    except Exception as e:
                        logger.error(f"Activity {activity_id} failed: {str(e)}")
                        
            # Short delay before next iteration
            time.sleep(0.5)
            
        # Get final process state
        instance = workflow_engine.get_process_instance(process_instance_id)
        if instance:
            if instance.status == ProcessStatus.COMPLETED:
                logger.info("Process completed successfully!")
                
                # Print final outputs
                logger.info("Final outputs:")
                campaign_plan = instance.context.get("campaign_plan")
                if campaign_plan:
                    logger.info(f"Campaign Plan: {campaign_plan['campaign_name']}")
                    
                creative_concepts = instance.context.get("creative_concepts")
                if creative_concepts:
                    logger.info(f"Creative Concepts: {', '.join(c['name'] for c in creative_concepts)}")
                    
                media_plan = instance.context.get("media_plan")
                if media_plan:
                    logger.info(f"Media Plan Budget: ${media_plan['total_budget']:,.2f}")
                    
            else:
                logger.info(f"Process ended with status: {instance.status.value}")
                if "error" in instance.context:
                    logger.error(f"Error: {instance.context['error']}")
    finally:
        # Clean up
        shutil.rmtree(temp_dir)
        
    logger.info("Process framework example completed.")


if __name__ == "__main__":
    run_workflow_example()