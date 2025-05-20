# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file shows how our AI helpers can use a shared brain that's running on
# a different computer. It's like using a phone to talk to a friend who has a book
# you need for your homework.

# High School Explanation:
# This module demonstrates how agents can interact with a remote TISIT knowledge graph
# via its REST API. It shows how the same agent integration patterns can work whether
# the knowledge graph is local or remote, enabling distributed architectures.

import os
import json
import logging
import time
import subprocess
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional

from ..core.base import Agent
from ..core.message import Message, MessageRole
from ..core.process import Process

from src.tisit.remote_agent_integration import RemoteKnowledgeEnhancedAgent

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

API_URL = "http://localhost:8000"


class RemoteStrategyAgent(RemoteKnowledgeEnhancedAgent):
    """Strategic planning agent with remote knowledge graph integration."""
    
    def __init__(self, api_url: str = API_URL):
        super().__init__("StrategyAgent", api_url, "Develops campaign strategies with knowledge-enhanced insights")
    
    def store_campaign_strategy(self, campaign_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Store campaign strategy information in the knowledge graph.
        
        Args:
            campaign_data: Dictionary containing campaign information
            
        Returns:
            Dict[str, str]: Dictionary mapping entity names to their IDs
        """
        return self.knowledge_interface.store_campaign_knowledge(campaign_data)
    
    def process_message(self, message: Message) -> Message:
        """Process a message, enhanced with knowledge from TISIT."""
        if message.role == MessageRole.USER:
            # Extract key concepts from the message to query knowledge
            content = message.content.lower()
            query_terms = []
            
            # Look for key marketing terms
            marketing_terms = ["brand awareness", "conversion", "engagement", "targeting", 
                              "audience", "funnel", "retention", "acquisition"]
            
            for term in marketing_terms:
                if term in content:
                    query_terms.append(term)
            
            # If we found any terms, enhance the message with knowledge
            if query_terms:
                query = " ".join(query_terms)
                enhanced_content = self.enhance_message_with_knowledge(
                    message.content, 
                    query
                )
                
                # Log that we enhanced the message
                logger.info(f"Enhanced message with knowledge about: {query}")
                
                # Create a new response with the enhanced knowledge
                response = Message(
                    role=MessageRole.ASSISTANT,
                    content=f"I've analyzed your request and found relevant campaign knowledge. \n\n{enhanced_content}"
                )
            else:
                # No relevant terms found, process normally
                response = Message(
                    role=MessageRole.ASSISTANT,
                    content=f"I'll help you develop a strategic plan for this campaign."
                )
            
            # Store this interaction for future reference
            self.remember(
                entity_name=f"Strategy Request: {message.content[:50]}...",
                entity_type="strategy_request",
                description=f"User requested strategy with message: {message.content[:100]}...",
                tags=["strategy", "request"]
            )
            
            return response
        
        return Message(
            role=MessageRole.ASSISTANT,
            content="I can only respond to user messages."
        )


class RemoteCreativeAgent(RemoteKnowledgeEnhancedAgent):
    """Creative design agent with remote knowledge graph integration."""
    
    def __init__(self, api_url: str = API_URL):
        super().__init__("CreativeAgent", api_url, "Develops creative content with knowledge-enhanced insights")
    
    def store_creative_concepts(self, creative_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Store creative concept information in the knowledge graph.
        
        Args:
            creative_data: Dictionary containing creative information
            
        Returns:
            Dict[str, str]: Dictionary mapping entity names to their IDs
        """
        return self.knowledge_interface.capture_creative_knowledge(creative_data)
    
    def process_message(self, message: Message) -> Message:
        """Process a message, enhanced with knowledge from TISIT."""
        if message.role == MessageRole.USER:
            # Extract creative concepts from the message
            content = message.content.lower()
            creative_concepts = []
            
            # Look for creative concept terms
            concept_terms = ["storytelling", "visual", "copy", "headline", "imagery",
                           "emotion", "tone", "style", "brand voice"]
            
            for term in concept_terms:
                if term in content:
                    creative_concepts.append(term)
            
            # If we found any concepts, enhance with knowledge
            if creative_concepts:
                query = " ".join(creative_concepts)
                knowledge = self.recall(
                    query=query,
                    entity_types=["creative_approach", "asset", "message"]
                )
                
                # Create response with knowledge
                if knowledge.get("entities"):
                    entities_info = "\n".join([
                        f"- {e['name']}: {e['description']}"
                        for e in knowledge.get("entities", [])[:3]
                    ])
                    
                    response = Message(
                        role=MessageRole.ASSISTANT,
                        content=f"I've found some creative approaches that might help:\n\n{entities_info}\n\nI'll develop creative concepts aligned with these approaches."
                    )
                else:
                    response = Message(
                        role=MessageRole.ASSISTANT,
                        content=f"I'll help you develop creative concepts for this campaign, focusing on {', '.join(creative_concepts)}."
                    )
            else:
                response = Message(
                    role=MessageRole.ASSISTANT,
                    content="I'll help you develop compelling creative for this campaign."
                )
            
            # Store this creative request
            self.remember(
                entity_name=f"Creative Request: {message.content[:50]}...",
                entity_type="creative_request",
                description=f"User requested creative with message: {message.content[:100]}...",
                tags=["creative", "request"]
            )
            
            return response
        
        return Message(
            role=MessageRole.ASSISTANT,
            content="I can only respond to user messages."
        )


class MediaAgent(RemoteKnowledgeEnhancedAgent):
    """Media planning agent with remote knowledge graph integration."""
    
    def __init__(self, api_url: str = API_URL):
        super().__init__("MediaAgent", api_url, "Develops media plans with knowledge-enhanced insights")
    
    def store_media_plan(self, media_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Store media plan information in the knowledge graph.
        
        Args:
            media_data: Dictionary containing media planning information
            
        Returns:
            Dict[str, str]: Dictionary mapping entity names to their IDs
        """
        return self.knowledge_interface.capture_media_knowledge(media_data)
    
    def process_message(self, message: Message) -> Message:
        """Process a message, enhanced with knowledge from TISIT."""
        if message.role == MessageRole.USER:
            # Extract media concepts from the message
            content = message.content.lower()
            media_concepts = []
            
            # Look for media planning terms
            media_terms = ["channel", "budget", "targeting", "reach", "frequency",
                          "impression", "conversion", "cpm", "cpc", "roi"]
            
            for term in media_terms:
                if term in content:
                    media_concepts.append(term)
            
            # If we found any media concepts, enhance with knowledge
            if media_concepts:
                query = " ".join(media_concepts)
                enhanced_content = self.enhance_message_with_knowledge(
                    message.content, 
                    query
                )
                
                response = Message(
                    role=MessageRole.ASSISTANT,
                    content=f"I'll help you develop a media plan. Based on our knowledge base:\n\n{enhanced_content}"
                )
            else:
                response = Message(
                    role=MessageRole.ASSISTANT,
                    content="I'll help you develop an effective media plan for this campaign."
                )
            
            # Store this media request
            self.remember(
                entity_name=f"Media Request: {message.content[:50]}...",
                entity_type="media_request",
                description=f"User requested media planning with message: {message.content[:100]}...",
                tags=["media", "request"]
            )
            
            return response
        
        return Message(
            role=MessageRole.ASSISTANT,
            content="I can only respond to user messages."
        )


def start_api_server():
    """Start the TISIT API server in a separate process."""
    try:
        # Use a new data directory for this example
        data_dir = os.path.expanduser("~/.tisit/remote_example")
        
        # Build the command
        cmd = [
            "python", "-m", "src.tisit.api_server",
            "--host", "localhost",
            "--port", "8000",
            "--data-dir", data_dir,
            "--log-level", "info"
        ]
        
        # Start the server
        server_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Give the server time to start
        time.sleep(2)
        
        logger.info(f"API server started on http://localhost:8000")
        
        return server_process
    
    except Exception as e:
        logger.error(f"Error starting API server: {str(e)}")
        return None


def run_remote_knowledge_sharing_example():
    """
    Run an example demonstrating knowledge sharing between agents via the remote API.
    
    This example shows how agents can store knowledge in a remote TISIT instance and 
    then other agents can benefit from that shared knowledge, all through the API.
    """
    # Start the API server in a separate process
    server_process = start_api_server()
    
    if not server_process:
        logger.error("Failed to start API server, aborting example")
        return
    
    try:
        # Give the server some time to initialize
        time.sleep(2)
        
        # Create agents with remote knowledge graph integration
        strategy_agent = RemoteStrategyAgent()
        creative_agent = RemoteCreativeAgent()
        media_agent = MediaAgent()
        
        print("=== Remote Knowledge Sharing Between Agents Example ===\n")
        
        # Step 1: Strategy agent stores campaign knowledge
        print("Step 1: Strategy agent stores campaign information in remote TISIT...")
        campaign_data = {
            "name": "Remote Summer Product Launch",
            "objective": "Increase brand awareness and drive initial sales",
            "brand": "EcoTech Remote",
            "industry": "Sustainable Technology",
            "audiences": [
                {
                    "name": "Remote Eco-conscious Millennials",
                    "description": "25-40 year olds who prioritize sustainability in purchasing decisions"
                },
                {
                    "name": "Remote Tech Early Adopters",
                    "description": "Technology enthusiasts who embrace new products"
                }
            ],
            "creative_approaches": [
                {
                    "name": "Remote Emotional Storytelling",
                    "description": "Connect through stories of environmental impact"
                },
                {
                    "name": "Remote Product Innovation Showcase",
                    "description": "Highlight unique technological advancements"
                }
            ],
            "channels": [
                "Instagram", "YouTube", "Sustainability Blogs"
            ]
        }
        
        entity_ids = strategy_agent.store_campaign_strategy(campaign_data)
        print(f"Created campaign entity with ID: {entity_ids.get('campaign')}")
        print(f"Created audience entities: {[entity_ids.get(f'audience_{i}') for i in range(2)]}")
        print(f"Created creative approach entities: {[entity_ids.get(f'creative_{i}') for i in range(2)]}")
        print()
        
        # Step 2: Creative agent leverages strategy knowledge
        print("Step 2: Creative agent accesses campaign strategy knowledge...")
        creative_knowledge = creative_agent.recall("Remote Summer Product Launch")
        
        print(f"Creative agent found {len(creative_knowledge.get('entities', []))} relevant knowledge entities:")
        for entity in creative_knowledge.get('entities', [])[:3]:
            print(f"- {entity['name']} ({entity['type']}): {entity['description']}")
        print()
        
        # Step 3: Creative agent stores creative concept
        print("Step 3: Creative agent stores creative concept in remote TISIT...")
        creative_data = {
            "name": "Remote Nature's Technology Visuals",
            "approach": "Remote Emotional Storytelling",
            "headline": "Innovation Inspired by Nature",
            "description": "Visual series showing technology integrated with natural environments",
            "campaign": "Remote Summer Product Launch",
            "messages": [
                {
                    "name": "Remote Sustainability Message",
                    "text": "Powered by nature, designed for the future"
                },
                {
                    "name": "Remote Innovation Message",
                    "text": "Where natural wisdom meets technological innovation"
                }
            ]
        }
        
        creative_entity_ids = creative_agent.store_creative_concepts(creative_data)
        print(f"Created creative asset with ID: {creative_entity_ids.get('asset')}")
        print(f"Created message entities: {[creative_entity_ids.get(f'message_{i}') for i in range(2)]}")
        print()
        
        # Step 4: Media agent leverages both strategy and creative knowledge
        print("Step 4: Media agent accesses accumulated campaign knowledge...")
        media_knowledge = media_agent.recall("Remote Summer Product Launch")
        
        print(f"Media agent found {len(media_knowledge.get('entities', []))} relevant knowledge entities:")
        for entity in media_knowledge.get('entities', [])[:5]:
            print(f"- {entity['name']} ({entity['type']}): {entity['description']}")
        print()
        
        # Step 5: Media agent stores media plan
        print("Step 5: Media agent stores media plan in remote TISIT...")
        media_data = {
            "name": "Remote Summer Launch Media Plan",
            "campaign": "Remote Summer Product Launch",
            "objective": "Maximize reach among eco-conscious audience segments",
            "budget": 150000,
            "allocations": [
                {
                    "channel": "Instagram",
                    "budget": 60000,
                    "percentage": 40,
                    "targeting": "Interest targeting: sustainability, technology"
                },
                {
                    "channel": "YouTube",
                    "budget": 45000,
                    "percentage": 30,
                    "targeting": "Demographics and interest targeting"
                },
                {
                    "channel": "Sustainability Blogs",
                    "budget": 45000,
                    "percentage": 30,
                    "targeting": "Contextual targeting in relevant content"
                }
            ],
            "metrics": [
                {
                    "name": "Brand Awareness Lift",
                    "target": "15%",
                    "description": "Target brand awareness increase post-campaign"
                },
                {
                    "name": "Engagement Rate",
                    "target": "3.5%",
                    "description": "Target engagement rate across channels"
                }
            ]
        }
        
        media_entity_ids = media_agent.store_media_plan(media_data)
        print(f"Created media plan with ID: {media_entity_ids.get('plan')}")
        print(f"Created allocation entities: {[media_entity_ids.get(f'allocation_{i}') for i in range(3)]}")
        print(f"Created metric entities: {[media_entity_ids.get(f'metric_{i}') for i in range(2)]}")
        print()
        
        # Step 6: Now any agent can retrieve complete campaign knowledge
        print("Step 6: Any agent can now access the complete campaign knowledge...")
        
        campaign_knowledge = strategy_agent.knowledge_interface.retrieve_campaign_knowledge("Remote Summer Product Launch")
        
        print("Complete Campaign Knowledge Graph:")
        print(f"- Campaign: {campaign_knowledge['campaign']['name']}")
        print(f"- Objective: {campaign_knowledge['campaign']['description']}")
        
        print("- Audiences:")
        for audience in campaign_knowledge['audiences']:
            print(f"  * {audience['name']}: {audience['description']}")
        
        print("- Creative Approaches:")
        for approach in campaign_knowledge['creative_approaches']:
            print(f"  * {approach['name']}: {approach['description']}")
        
        print("- Assets:")
        for asset in campaign_knowledge['assets']:
            print(f"  * {asset['name']}: {asset['description']}")
        
        print("- Channels:")
        for channel in campaign_knowledge['channels']:
            print(f"  * {channel['name']}")
        
        print("- Metrics:")
        for metric in campaign_knowledge['metrics']:
            print(f"  * {metric['name']}: {metric['description']}")
        
        print("\nThis remote knowledge graph provides a unified view of the campaign across all specialized agents.")
    
    finally:
        # Terminate the server process
        if server_process:
            server_process.terminate()
            stdout, stderr = server_process.communicate()
            logger.info("API server terminated")


def interactive_remote_example():
    """Run an interactive example where users can message agents via the remote API."""
    # Start the API server in a separate process
    server_process = start_api_server()
    
    if not server_process:
        logger.error("Failed to start API server, aborting example")
        return
    
    try:
        # Give the server some time to initialize
        time.sleep(2)
        
        # Create agents with remote knowledge graph integration
        strategy_agent = RemoteStrategyAgent()
        creative_agent = RemoteCreativeAgent()
        media_agent = MediaAgent()
        
        agents = {
            "strategy": strategy_agent,
            "creative": creative_agent,
            "media": media_agent
        }
        
        print("=== Interactive Agency with Remote TISIT Knowledge Graph ===")
        print("Available agents: strategy, creative, media")
        print("Type 'exit' to quit")
        print()
        
        while True:
            agent_choice = input("Which agent would you like to talk to? ").lower()
            
            if agent_choice == 'exit':
                break
            
            if agent_choice not in agents:
                print(f"Unknown agent: {agent_choice}. Choose from: strategy, creative, media")
                continue
            
            agent = agents[agent_choice]
            print(f"Chatting with {agent.name}. Type 'back' to switch agents.")
            
            while True:
                user_message = input("\nYour message: ")
                
                if user_message.lower() == 'back':
                    break
                    
                if user_message.lower() == 'exit':
                    return
                
                message = Message(role=MessageRole.USER, content=user_message)
                response = agent.process_message(message)
                
                print(f"\n{agent.name}: {response.content}")
    
    finally:
        # Terminate the server process
        if server_process:
            server_process.terminate()
            stdout, stderr = server_process.communicate()
            logger.info("API server terminated")


if __name__ == "__main__":
    # Run the knowledge sharing example
    run_remote_knowledge_sharing_example()
    
    # Run interactive example if desired
    # interactive_remote_example()