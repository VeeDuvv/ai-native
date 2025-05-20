# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file shows how our AI helpers can use a shared brain to remember things
# they learn and find information they need to do their jobs better.

# High School Explanation:
# This module demonstrates the integration of the TISIT knowledge graph with
# the agent framework. It provides examples of agents storing, retrieving, and
# leveraging knowledge through the TISIT system for more effective collaboration.

import json
import os
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

from ..core.base import Agent
from ..core.message import Message, MessageRole
from ..core.process import Process

from src.tisit.knowledge_graph import KnowledgeGraph
from src.tisit.agent_integration import TisitAgentInterface
from src.tisit.entity import Entity

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Set up a shared knowledge graph for all agents to use
KNOWLEDGE_DIR = os.path.expanduser("~/.tisit/agency_example")
KNOWLEDGE_GRAPH = KnowledgeGraph(KNOWLEDGE_DIR)


class KnowledgeEnhancedAgent(Agent):
    """
    An agent with integrated knowledge graph capabilities.
    
    This agent can store and retrieve knowledge from the TISIT knowledge graph,
    enhancing its decision-making with collective knowledge.
    """
    
    def __init__(self, name: str, description: str = ""):
        """Initialize a knowledge-enhanced agent."""
        super().__init__(name, description)
        self.knowledge_interface = TisitAgentInterface(KNOWLEDGE_GRAPH, name)
        
    def remember(self, entity_name: str, entity_type: str, description: str, 
                 details: str = "", tags: List[str] = None) -> str:
        """
        Store information in the knowledge graph.
        
        Args:
            entity_name: Name of the entity to store
            entity_type: Type of entity (concept, strategy, etc.)
            description: Short description of the entity
            details: Detailed description
            tags: List of tags for categorization
            
        Returns:
            str: ID of the created entity
        """
        return self.knowledge_interface.store_entity(
            name=entity_name,
            entity_type=entity_type,
            short_description=description,
            detailed_description=details,
            tags=tags or []
        )
    
    def connect(self, source_name: str, target_name: str, relationship: str, 
                description: str = "") -> Optional[str]:
        """
        Create a relationship between two knowledge entities.
        
        Args:
            source_name: Name of the source entity
            target_name: Name of the target entity
            relationship: Type of relationship
            description: Description of the relationship
            
        Returns:
            Optional[str]: ID of the created relationship, or None if entities not found
        """
        return self.knowledge_interface.connect_entities(
            source_name=source_name,
            target_name=target_name,
            relation_type=relationship,
            description=description
        )
    
    def recall(self, query: str, entity_types: List[str] = None, 
               tags: List[str] = None) -> Dict[str, Any]:
        """
        Retrieve relevant knowledge based on a query.
        
        Args:
            query: The query text to search for
            entity_types: Optional types of entities to search for
            tags: Optional tags to filter by
            
        Returns:
            Dict[str, Any]: Knowledge context with entities and relationships
        """
        return self.knowledge_interface.get_knowledge_context(
            query=query,
            entity_types=entity_types,
            tags=tags
        )
    
    def enhance_message_with_knowledge(self, message: str, context_query: str) -> str:
        """
        Enhance a message with relevant knowledge from TISIT.
        
        Args:
            message: The original message
            context_query: Query to find relevant knowledge
            
        Returns:
            str: Enhanced message with knowledge context
        """
        # Get relevant knowledge
        knowledge = self.recall(context_query)
        
        if not knowledge.get("entities"):
            return message  # No relevant knowledge found
        
        # Build knowledge context section
        knowledge_section = "\n\nRelevant Knowledge Context:\n"
        
        for entity in knowledge.get("entities", [])[:3]:  # Limit to 3 entities
            knowledge_section += f"- {entity['name']} ({entity['type']}): {entity['description']}\n"
        
        # Add relationships
        if knowledge.get("relationships"):
            knowledge_section += "\nRelationships:\n"
            for rel in knowledge.get("relationships", [])[:5]:  # Limit to 5 relationships
                knowledge_section += f"- {rel['source']} {rel['type']} {rel['target']}\n"
        
        # Combine original message with knowledge context
        enhanced_message = message + knowledge_section
        return enhanced_message


class StrategyAgentWithKnowledge(KnowledgeEnhancedAgent):
    """Strategic planning agent with knowledge graph integration."""
    
    def __init__(self):
        super().__init__("StrategyAgent", "Develops campaign strategies with knowledge-enhanced insights")
    
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


class CreativeAgentWithKnowledge(KnowledgeEnhancedAgent):
    """Creative design agent with knowledge graph integration."""
    
    def __init__(self):
        super().__init__("CreativeAgent", "Develops creative content with knowledge-enhanced insights")
    
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


class MediaAgentWithKnowledge(KnowledgeEnhancedAgent):
    """Media planning agent with knowledge graph integration."""
    
    def __init__(self):
        super().__init__("MediaAgent", "Develops media plans with knowledge-enhanced insights")
    
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


def run_knowledge_sharing_example():
    """
    Run an example demonstrating knowledge sharing between agents.
    
    This example shows how agents can store knowledge in TISIT and then
    other agents can benefit from that shared knowledge.
    """
    # Create agents
    strategy_agent = StrategyAgentWithKnowledge()
    creative_agent = CreativeAgentWithKnowledge()
    media_agent = MediaAgentWithKnowledge()
    
    print("=== Knowledge Sharing Between Agents Example ===\n")
    
    # Step 1: Strategy agent stores campaign knowledge
    print("Step 1: Strategy agent stores campaign information in TISIT...")
    campaign_data = {
        "name": "Summer Product Launch",
        "objective": "Increase brand awareness and drive initial sales",
        "brand": "EcoTech",
        "industry": "Sustainable Technology",
        "audiences": [
            {
                "name": "Eco-conscious Millennials",
                "description": "25-40 year olds who prioritize sustainability in purchasing decisions"
            },
            {
                "name": "Tech Early Adopters",
                "description": "Technology enthusiasts who embrace new products"
            }
        ],
        "creative_approaches": [
            {
                "name": "Emotional Storytelling",
                "description": "Connect through stories of environmental impact"
            },
            {
                "name": "Product Innovation Showcase",
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
    creative_knowledge = creative_agent.recall("Summer Product Launch")
    
    print(f"Creative agent found {len(creative_knowledge.get('entities', []))} relevant knowledge entities:")
    for entity in creative_knowledge.get('entities', [])[:3]:
        print(f"- {entity['name']} ({entity['type']}): {entity['description']}")
    print()
    
    # Step 3: Creative agent stores creative concept
    print("Step 3: Creative agent stores creative concept in TISIT...")
    creative_data = {
        "name": "Nature's Technology Visuals",
        "approach": "Emotional Storytelling",
        "headline": "Innovation Inspired by Nature",
        "description": "Visual series showing technology integrated with natural environments",
        "campaign": "Summer Product Launch",
        "messages": [
            {
                "name": "Sustainability Message",
                "text": "Powered by nature, designed for the future"
            },
            {
                "name": "Innovation Message",
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
    media_knowledge = media_agent.recall("Summer Product Launch")
    
    print(f"Media agent found {len(media_knowledge.get('entities', []))} relevant knowledge entities:")
    for entity in media_knowledge.get('entities', [])[:5]:
        print(f"- {entity['name']} ({entity['type']}): {entity['description']}")
    print()
    
    # Step 5: Media agent stores media plan
    print("Step 5: Media agent stores media plan in TISIT...")
    media_data = {
        "name": "Summer Launch Media Plan",
        "campaign": "Summer Product Launch",
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
    
    campaign_knowledge = strategy_agent.knowledge_interface.retrieve_campaign_knowledge("Summer Product Launch")
    
    print("Complete Campaign Knowledge Graph:")
    print(f"- Campaign: {campaign_knowledge['campaign']['name']}")
    print(f"- Objective: {campaign_knowledge['campaign']['description']}")
    print(f"- Brand: {campaign_knowledge['brand'][0]['name'] if campaign_knowledge['brand'] else 'N/A'}")
    
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
    
    print("\nThis knowledge graph provides a unified view of the campaign across all specialized agents.")


def interactive_example():
    """Run an interactive example where users can message agents."""
    # Create agents
    strategy_agent = StrategyAgentWithKnowledge()
    creative_agent = CreativeAgentWithKnowledge()
    media_agent = MediaAgentWithKnowledge()
    
    agents = {
        "strategy": strategy_agent,
        "creative": creative_agent,
        "media": media_agent
    }
    
    print("=== Interactive Agency with TISIT Knowledge Graph ===")
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


if __name__ == "__main__":
    # Run the knowledge sharing example
    run_knowledge_sharing_example()
    
    # Run interactive example if desired
    # interactive_example()