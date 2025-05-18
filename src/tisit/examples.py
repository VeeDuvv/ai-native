# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file shows how to use our knowledge system with real examples. It's like a
# demonstration that helps people understand how our system works by showing it in action.

# High School Explanation:
# This module provides example usage of the TISIT knowledge graph implementation. It 
# demonstrates how to create entities, establish relationships, perform queries, and
# use other features through practical examples related to advertising concepts.

import os
from pathlib import Path
import tempfile
import shutil

from .entity import Entity
from .relationship import Relationship
from .knowledge_graph import KnowledgeGraph

def create_sample_ad_knowledge_graph():
    """Create a sample knowledge graph with advertising-related entities.
    
    This function demonstrates how to create entities, establish relationships,
    and build a small knowledge graph of advertising concepts.
    
    Returns:
        A populated KnowledgeGraph instance
    """
    # Create a temporary directory for the knowledge graph
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Initialize the knowledge graph
        kg = KnowledgeGraph(temp_dir)
        
        # Create basic advertising concepts
        ad_campaign = Entity(
            name="Advertising Campaign",
            entity_type="concept",
            short_description="A coordinated series of linked advertisements with a single idea or theme.",
            detailed_description=(
                "An advertising campaign is a series of advertisement messages that share a "
                "single idea and theme which make up an integrated marketing communication. "
                "Campaigns appear in different media across a specific time frame."
            ),
            tags=["advertising", "marketing", "campaign"]
        )
        
        target_audience = Entity(
            name="Target Audience",
            entity_type="concept",
            short_description="The specific group of consumers most likely to respond positively to a campaign.",
            detailed_description=(
                "A target audience is the intended audience or readership of a publication, "
                "advertisement, or other message catered specifically to a group of people. "
                "In marketing and advertising, it is a specific group of people within the "
                "target market identified as likely customers."
            ),
            tags=["advertising", "demographics", "audience"]
        )
        
        ad_creative = Entity(
            name="Creative",
            entity_type="concept",
            short_description="The actual advertisement content that delivers the message.",
            detailed_description=(
                "Advertising creative refers to the actual content of an advertisement - "
                "the copy, art, design, and production elements that make up the ad. "
                "The creative aspect of advertising is the conceptualization of the messaging "
                "and how it will be presented visually and/or verbally."
            ),
            tags=["advertising", "content", "design"]
        )
        
        marketing_objective = Entity(
            name="Marketing Objective",
            entity_type="concept",
            short_description="The specific goal an organization wants to achieve through marketing efforts.",
            detailed_description=(
                "Marketing objectives are the outcomes a brand wants to generate from its "
                "marketing activities. They provide direction for all marketing efforts "
                "and a framework for measuring success. Common marketing objectives include "
                "increasing brand awareness, generating leads, acquiring new customers, "
                "retaining existing customers, and increasing market share."
            ),
            tags=["marketing", "strategy", "objectives"]
        )
        
        # Add entities to the knowledge graph
        ad_campaign_id = kg.add_entity(ad_campaign)
        target_audience_id = kg.add_entity(target_audience)
        ad_creative_id = kg.add_entity(ad_creative)
        marketing_objective_id = kg.add_entity(marketing_objective)
        
        # Create advertising platforms
        social_media = Entity(
            name="Social Media Advertising",
            entity_type="platform",
            short_description="Advertising that appears on social media platforms.",
            detailed_description=(
                "Social media advertising refers to paid content on social media platforms "
                "that is designed to drive engagement and generate traffic to specific websites. "
                "It includes various formats like image ads, video ads, carousel ads, and more "
                "across platforms such as Facebook, Instagram, Twitter, LinkedIn, and others."
            ),
            tags=["digital", "social media", "platform"]
        )
        
        search_engines = Entity(
            name="Search Engine Advertising",
            entity_type="platform",
            short_description="Advertising that appears on search engine results pages.",
            detailed_description=(
                "Search engine advertising is a method of placing online advertisements on web "
                "pages that show results from search engine queries. It includes search engine "
                "optimization (SEO) to improve organic rankings and paid search like Google Ads "
                "where advertisers bid on keywords to display ads in search results."
            ),
            tags=["digital", "search", "platform", "SEM"]
        )
        
        traditional_media = Entity(
            name="Traditional Media",
            entity_type="platform",
            short_description="Conventional advertising channels like TV, radio, and print.",
            detailed_description=(
                "Traditional media encompasses conventional channels of advertising that existed "
                "before the digital age, including television, radio, newspapers, magazines, "
                "billboards, and direct mail. Despite the rise of digital media, traditional "
                "channels remain effective for reaching certain demographics and achieving "
                "specific marketing objectives."
            ),
            tags=["traditional", "offline", "platform"]
        )
        
        # Add platform entities
        social_media_id = kg.add_entity(social_media)
        search_engines_id = kg.add_entity(search_engines)
        traditional_media_id = kg.add_entity(traditional_media)
        
        # Create specific ad formats
        display_ad = Entity(
            name="Display Advertisement",
            entity_type="format",
            short_description="Visual advertisement shown on websites, apps, or social media.",
            detailed_description=(
                "Display advertisements are graphical ads displayed on websites, apps, and "
                "social media platforms. They include various formats such as banners, "
                "rectangles, skyscrapers, and interstitials, and can contain text, images, "
                "flash, video, or audio. Display ads aim to deliver general advertisements "
                "and brand messages to site visitors."
            ),
            tags=["format", "visual", "banner"]
        )
        
        video_ad = Entity(
            name="Video Advertisement",
            entity_type="format",
            short_description="Advertisement in video format shown before, during, or after video content.",
            detailed_description=(
                "Video advertisements are promotional content in video format. They can appear "
                "before (pre-roll), during (mid-roll), or after (post-roll) online video content. "
                "Video ads are also common on television, streaming platforms, and social media. "
                "They combine visual and audio elements to create engaging promotions that can "
                "demonstrate products, tell stories, or evoke emotions."
            ),
            tags=["format", "video", "multimedia"]
        )
        
        search_ad = Entity(
            name="Search Advertisement",
            entity_type="format",
            short_description="Text-based ads shown alongside search engine results.",
            detailed_description=(
                "Search advertisements are text-based ads that appear on search engine results "
                "pages (SERPs). Advertisers bid on keywords relevant to their target market, and "
                "their ads appear when users search for those terms. These ads typically include "
                "a headline, description, and URL, and are marked as advertisements to distinguish "
                "them from organic search results."
            ),
            tags=["format", "text", "search", "PPC"]
        )
        
        # Add format entities
        display_ad_id = kg.add_entity(display_ad)
        video_ad_id = kg.add_entity(video_ad)
        search_ad_id = kg.add_entity(search_ad)
        
        # Create advertising metrics
        ctr = Entity(
            name="Click-Through Rate",
            entity_type="metric",
            short_description="The ratio of users who click on an ad to the number who view it.",
            detailed_description=(
                "Click-through rate (CTR) is a metric that measures the ratio of users who click "
                "on a specific link to the number of total users who view a page, email, or "
                "advertisement. It is commonly used to measure the success of an online advertising "
                "campaign for a particular website as well as the effectiveness of email campaigns."
            ),
            tags=["metric", "performance", "engagement"],
            metadata={"formula": "Clicks / Impressions * 100"}
        )
        
        conversion_rate = Entity(
            name="Conversion Rate",
            entity_type="metric",
            short_description="The percentage of users who take a desired action after clicking an ad.",
            detailed_description=(
                "Conversion rate is the percentage of users who take a desired action after "
                "clicking on an advertisement or visiting a website. The desired action could "
                "be purchasing a product, filling out a form, signing up for a newsletter, "
                "or any other goal defined by the advertiser. It's a key metric for measuring "
                "the effectiveness of advertising campaigns."
            ),
            tags=["metric", "performance", "ROI"],
            metadata={"formula": "Conversions / Clicks * 100"}
        )
        
        roas = Entity(
            name="Return on Ad Spend",
            entity_type="metric",
            short_description="Revenue generated per unit of money spent on advertising.",
            detailed_description=(
                "Return on Ad Spend (ROAS) is a marketing metric that measures the revenue "
                "generated for every dollar spent on advertising. It helps marketers evaluate "
                "the effectiveness of their advertising campaigns and optimize their ad spend. "
                "A higher ROAS indicates a more efficient campaign, while a lower ROAS might "
                "suggest that adjustments are needed."
            ),
            tags=["metric", "performance", "ROI"],
            metadata={"formula": "Revenue / Ad Spend"}
        )
        
        # Add metric entities
        ctr_id = kg.add_entity(ctr)
        conversion_rate_id = kg.add_entity(conversion_rate)
        roas_id = kg.add_entity(roas)
        
        # Define relationships between concepts
        kg.add_relationship(
            ad_campaign_id, target_audience_id, "targets",
            description="Campaigns are designed for specific target audiences",
            bidirectional=True
        )
        
        kg.add_relationship(
            ad_campaign_id, ad_creative_id, "contains",
            description="Campaigns include creative elements"
        )
        
        kg.add_relationship(
            ad_campaign_id, marketing_objective_id, "supports",
            description="Campaigns are designed to support marketing objectives"
        )
        
        # Connect platforms to campaigns
        kg.add_relationship(
            ad_campaign_id, social_media_id, "uses",
            description="Campaigns can use social media as a platform"
        )
        
        kg.add_relationship(
            ad_campaign_id, search_engines_id, "uses",
            description="Campaigns can use search engines as a platform"
        )
        
        kg.add_relationship(
            ad_campaign_id, traditional_media_id, "uses",
            description="Campaigns can use traditional media as a platform"
        )
        
        # Connect formats to platforms
        kg.add_relationship(
            social_media_id, display_ad_id, "supports",
            description="Social media platforms support display ads"
        )
        
        kg.add_relationship(
            social_media_id, video_ad_id, "supports",
            description="Social media platforms support video ads"
        )
        
        kg.add_relationship(
            search_engines_id, search_ad_id, "supports",
            description="Search engines support search ads"
        )
        
        kg.add_relationship(
            search_engines_id, display_ad_id, "supports",
            description="Search engines support display ads through their networks"
        )
        
        kg.add_relationship(
            traditional_media_id, video_ad_id, "supports",
            description="Traditional media like TV supports video ads"
        )
        
        # Connect metrics to formats
        kg.add_relationship(
            display_ad_id, ctr_id, "measured_by",
            description="Display ads are measured by click-through rate"
        )
        
        kg.add_relationship(
            video_ad_id, ctr_id, "measured_by",
            description="Video ads are measured by click-through rate"
        )
        
        kg.add_relationship(
            search_ad_id, ctr_id, "measured_by",
            description="Search ads are measured by click-through rate"
        )
        
        kg.add_relationship(
            display_ad_id, conversion_rate_id, "measured_by",
            description="Display ads are measured by conversion rate"
        )
        
        kg.add_relationship(
            video_ad_id, conversion_rate_id, "measured_by",
            description="Video ads are measured by conversion rate"
        )
        
        kg.add_relationship(
            search_ad_id, conversion_rate_id, "measured_by",
            description="Search ads are measured by conversion rate"
        )
        
        kg.add_relationship(
            ad_campaign_id, roas_id, "measured_by",
            description="Ad campaigns are measured by return on ad spend"
        )
        
        return kg
        
    except Exception as e:
        # Clean up in case of an error
        shutil.rmtree(temp_dir)
        raise e

def demonstrate_knowledge_graph_operations():
    """Demonstrate various operations on the knowledge graph.
    
    This function shows how to perform common operations like querying,
    traversing relationships, and analyzing the knowledge graph.
    """
    # Create the sample knowledge graph
    kg = create_sample_ad_knowledge_graph()
    
    print("=== Advertising Knowledge Graph Example ===\n")
    
    # Demonstrate entity search
    print("== Finding entities by type ==")
    metrics = kg.find_entities_by_type("metric")
    print(f"Found {len(metrics)} metrics:")
    for metric in metrics:
        print(f"- {metric.name}: {metric.short_description}")
    print()
    
    # Demonstrate relationship traversal
    print("== Exploring relationships from 'Advertising Campaign' ==")
    campaign = kg.entity_storage.find_by_name("Advertising Campaign")
    if campaign:
        related = kg.get_related_entities(campaign.id)
        print(f"Entities related to {campaign.name}:")
        for rel_type, entities in related.items():
            print(f"\n{rel_type}:")
            for entity in entities:
                print(f"- {entity.name}")
    print()
    
    # Demonstrate connection finding
    print("== Finding connections between concepts ==")
    search_ad = kg.entity_storage.find_by_name("Search Advertisement")
    conversion = kg.entity_storage.find_by_name("Conversion Rate")
    
    if search_ad and conversion:
        paths = kg.find_connections(search_ad.id, conversion.id)
        print(f"Connections from {search_ad.name} to {conversion.name}:")
        for i, path in enumerate(paths):
            print(f"\nPath {i+1}:")
            for source_id, rel_type, target_id in path:
                source = kg.get_entity(source_id)
                target = kg.get_entity(target_id)
                print(f"  {source.name} -{rel_type}-> {target.name}")
    print()
    
    # Demonstrate knowledge graph statistics
    print("== Knowledge Graph Statistics ==")
    stats = kg.get_stats()
    print(f"Total entities: {stats['num_entities']}")
    print(f"Total relationships: {stats['num_relationships']}")
    print(f"Entity types: {', '.join(stats['entity_types'].keys())}")
    print(f"Relationship types: {', '.join(stats['relationship_types'].keys())}")
    print()
    
    # Clean up
    temp_dir = kg.storage_root
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    
    print("=== Example completed ===")

if __name__ == "__main__":
    demonstrate_knowledge_graph_operations()