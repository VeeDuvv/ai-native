# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file shows examples of how to use our analytics system to track how well ads are doing.
# It's like a guide that shows how to collect, analyze, and understand information about ads.

# High School Explanation:
# This module provides examples of how to use the analytics system for tracking and analyzing
# advertising campaign performance. It demonstrates how to set up data collectors, processors,
# storage, and pipeline components to gather, process, and generate insights from campaign data.

import asyncio
import random
from datetime import datetime, timedelta
import json
import os
from pathlib import Path

from .core.models import Metric, Dimension, TimeRange, Segment, PerformanceData
from .core.collectors import DataCollector, GoogleAdsCollector, FacebookAdsCollector
from .core.processors import (
    DataProcessor, 
    MetricCalculator, 
    DataCleaner,
    DataTransformer,
    DataAggregator,
    AnomalyDetector,
    InsightGenerator
)
from .core.storage import create_storage, StorageBackend
from .core.pipeline import AnalyticsPipeline, PipelineBuilder
from .api.reporting import AnalyticsReportingAPI, ReportFormatter


# Example 1: Basic analytics pipeline with in-memory storage
async def example_basic_pipeline():
    print("\n=== Example 1: Basic Analytics Pipeline ===")
    
    # Create storage
    storage = create_storage("memory")
    
    # Create collectors
    google_collector = GoogleAdsCollector(
        client_id="example_client",
        use_synthetic_data=True  # For demonstration
    )
    
    facebook_collector = FacebookAdsCollector(
        account_id="example_account",
        use_synthetic_data=True  # For demonstration
    )
    
    # Create processors
    cleaner = DataCleaner()
    transformer = DataTransformer()
    calculator = MetricCalculator()
    aggregator = DataAggregator()
    
    # Create a builder
    builder = PipelineBuilder(storage)
    
    # Configure the pipeline
    pipeline = (builder
        .with_collector(google_collector)
        .with_collector(facebook_collector)
        .with_processor(cleaner, "CLEANED")
        .with_processor(transformer, "TRANSFORMED")
        .with_processor(calculator, "ENRICHED")
        .with_processor(aggregator, "AGGREGATED")
        .build())
    
    # Set up a callback
    pipeline.register_callback("collection_completed", lambda data_ids: print(f"Collected {len(data_ids)} data points"))
    pipeline.register_callback("processing_completed", lambda processed_ids: print(f"Processed data through {len(processed_ids)} stages"))
    
    # Define time range for the last day
    time_range = TimeRange.last_24_hours()
    
    # Collect data
    print("Collecting data...")
    data_ids = await pipeline.collect_data(time_range)
    
    # Process data
    print("Processing data...")
    processed_ids = await pipeline.process_data(data_ids)
    
    # Query and print some results
    print("\nQuerying results:")
    results = storage.query_data(
        time_range=time_range,
        metrics=[Metric(name="impressions"), Metric(name="clicks")],
        processing_stage="AGGREGATED"
    )
    
    for i, data in enumerate(results[:3]):  # Show just the first 3 results
        print(f"\nResult {i+1}:")
        print(f"  Dimensions: {data.dimensions}")
        print(f"  Metrics: {data.metrics}")
    
    return pipeline, storage


# Example 2: Advanced analytics with insights generation
async def example_advanced_analytics():
    print("\n=== Example 2: Advanced Analytics with Insights ===")
    
    # Create storage
    storage = create_storage("memory")
    
    # Create collectors
    google_collector = GoogleAdsCollector(
        client_id="example_client",
        use_synthetic_data=True
    )
    
    # Create processors
    cleaner = DataCleaner()
    transformer = DataTransformer()
    calculator = MetricCalculator()
    aggregator = DataAggregator()
    
    # Create insight processors
    anomaly_detector = AnomalyDetector()
    insight_generator = InsightGenerator()
    
    # Create pipeline
    builder = PipelineBuilder(storage)
    pipeline = (builder
        .with_collector(google_collector)
        .with_processor(cleaner, "CLEANED")
        .with_processor(transformer, "TRANSFORMED")
        .with_processor(calculator, "ENRICHED")
        .with_processor(aggregator, "AGGREGATED")
        .with_insight_processor(anomaly_detector)
        .with_insight_processor(insight_generator)
        .build())
    
    # Define time range for the last 7 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    time_range = TimeRange(start_date, end_date)
    
    # Collect and process data
    print("Collecting and processing data...")
    data_ids = await pipeline.collect_data(time_range)
    processed_ids = await pipeline.process_data(data_ids)
    
    # Generate insights
    print("Generating insights...")
    insight_ids = await pipeline.generate_insights(
        processed_ids,
        [anomaly_detector, insight_generator]
    )
    
    # Query and print insights
    print(f"\nGenerated {len(insight_ids)} insights:")
    insights = storage.query_insights(
        time_range=time_range,
        limit=5  # Just show top 5
    )
    
    for i, insight in enumerate(insights):
        print(f"\nInsight {i+1}: {insight['type']}")
        print(f"  Title: {insight.get('title', 'No title')}")
        print(f"  Description: {insight.get('description', 'No description')}")
        if insight.get('severity'):
            print(f"  Severity: {insight['severity']}")
        if insight.get('recommendations'):
            print(f"  Recommendations: {len(insight['recommendations'])} items")
    
    return pipeline, storage, insight_ids


# Example 3: Using file-based storage
async def example_file_storage():
    print("\n=== Example 3: File-Based Storage ===")
    
    # Create a temporary directory for the example
    base_dir = Path("./temp_analytics_data")
    base_dir.mkdir(exist_ok=True)
    
    print(f"Using file storage at: {base_dir.absolute()}")
    
    # Create storage
    storage = create_storage("file", base_dir=base_dir)
    
    # Create collectors and processors
    google_collector = GoogleAdsCollector(
        client_id="example_client",
        use_synthetic_data=True
    )
    
    cleaner = DataCleaner()
    calculator = MetricCalculator()
    
    # Create pipeline
    builder = PipelineBuilder(storage)
    pipeline = (builder
        .with_collector(google_collector)
        .with_processor(cleaner, "CLEANED")
        .with_processor(calculator, "ENRICHED")
        .build())
    
    # Define time range for yesterday
    end_date = datetime.now()
    start_date = end_date - timedelta(days=1)
    time_range = TimeRange(start_date, end_date)
    
    # Collect and process data
    print("Collecting and processing data...")
    data_ids = await pipeline.collect_data(time_range)
    processed_ids = await pipeline.process_data(data_ids, end_stage="ENRICHED")
    
    # Show directory structure
    print("\nStorage directory structure:")
    for path in sorted(base_dir.glob("**/*"))[0:10]:  # Show first 10 files/dirs
        if path.is_file():
            print(f"  File: {path.relative_to(base_dir)} ({path.stat().st_size} bytes)")
        else:
            print(f"  Dir:  {path.relative_to(base_dir)}")
    
    # Query data
    print("\nQuerying data from file storage:")
    results = storage.query_data(
        time_range=time_range,
        processing_stage="ENRICHED",
        limit=3
    )
    
    print(f"Found {len(results)} results")
    
    # Clean up (comment this line if you want to examine the files)
    # import shutil
    # shutil.rmtree(base_dir)
    
    return pipeline, storage


# Example 4: Using the reporting API
async def example_reporting_api():
    print("\n=== Example 4: Analytics Reporting API ===")
    
    # Create storage and fill it with some data
    storage = create_storage("memory")
    
    # Add some synthetic data
    for i in range(10):
        # Raw data
        data = {
            "impressions": random.randint(1000, 10000),
            "clicks": random.randint(10, 500),
            "cost": random.uniform(100, 1000),
            "campaign_id": f"campaign_{i % 3 + 1}",
            "ad_group_id": f"adgroup_{i % 5 + 1}",
            "date": (datetime.now() - timedelta(days=i % 7)).strftime("%Y-%m-%d"),
            "platform": random.choice(["google", "facebook", "linkedin"]),
            "channel": random.choice(["search", "display", "social", "video"])
        }
        
        data_id = storage.store_raw_data(
            source="example",
            data=data,
            timestamp=datetime.now() - timedelta(days=i % 7)
        )
        
        # Processed data
        metrics = {
            "impressions": data["impressions"],
            "clicks": data["clicks"],
            "cost": data["cost"],
            "ctr": data["clicks"] / data["impressions"] if data["impressions"] > 0 else 0,
            "cpc": data["cost"] / data["clicks"] if data["clicks"] > 0 else 0,
            "conversions": random.randint(0, 50),
        }
        
        dimensions = {
            "campaign_id": data["campaign_id"],
            "ad_group_id": data["ad_group_id"],
            "date": data["date"],
            "platform": data["platform"],
            "channel": data["channel"]
        }
        
        performance_data = PerformanceData(
            metrics=metrics,
            dimensions=dimensions,
            segments=[]
        )
        
        processed_id = storage.store_processed_data(
            data_id=data_id,
            data=performance_data,
            processing_stage="ANALYZED"
        )
        
        # Add some insights
        if i % 3 == 0:
            insight_data = {
                "title": f"Performance anomaly in {data['campaign_id']}",
                "description": f"Unusually high cost per click detected in {data['channel']} campaigns",
                "campaign_id": data["campaign_id"],
                "severity": random.choice(["low", "medium", "high"]),
                "metrics": [{"name": "cpc", "value": metrics["cpc"], "threshold": 2.0}],
                "recommendations": [
                    {"action": "Adjust bidding strategy", "impact": "medium"},
                    {"action": "Review ad creative", "impact": "high"}
                ]
            }
            
            storage.store_insight(
                data_ids=[processed_id],
                insight_type="anomaly",
                insight_data=insight_data
            )
    
    # Create the reporting API
    reporting_api = AnalyticsReportingAPI(storage)
    
    # Test creating a report
    print("Creating a performance report...")
    report_request = {
        "name": "Campaign Performance Report",
        "description": "Overview of campaign performance metrics",
        "time_range": {
            "start_date": (datetime.now() - timedelta(days=7)).isoformat(),
            "end_date": datetime.now().isoformat()
        },
        "metrics": [
            {"name": "impressions", "display_name": "Impressions"},
            {"name": "clicks", "display_name": "Clicks"},
            {"name": "cost", "display_name": "Cost"},
            {"name": "ctr", "display_name": "CTR"},
            {"name": "cpc", "display_name": "CPC"}
        ],
        "dimensions": [
            {"name": "campaign_id", "display_name": "Campaign"},
            {"name": "channel", "display_name": "Channel"},
            {"name": "date", "display_name": "Date"}
        ],
        "filters": {
            "dimension.platform": "google"
        },
        "format": "json"
    }
    
    report = await reporting_api.create_router().post("/reports")(request=report_request, storage=storage)
    
    print(f"Report created with ID: {report['id']}")
    print(f"Report contains {len(report['data'])} data points and {len(report.get('insights', []))} insights")
    
    # Format the report as HTML
    html_report = ReportFormatter.to_html(report)
    print(f"\nHTML report size: {len(html_report)} bytes")
    
    # Print as markdown (limited for brevity)
    markdown_report = ReportFormatter.to_markdown(report)
    print("\nMarkdown Report Preview:")
    print(markdown_report.split("\n\n")[0])  # Just show the first paragraph
    
    # Generate dashboard data
    dashboard_data = reporting_api.generate_dashboard_data()
    print("\nDashboard Summary:")
    print(f"Time Range: {dashboard_data['time_range']['start_date']} to {dashboard_data['time_range']['end_date']}")
    print(f"Metrics Summary: {json.dumps(dashboard_data['summary']['metrics'], indent=2)}")
    print(f"Channel Breakdown: {len(dashboard_data['channel_breakdown']['channels'])} channels")
    print(f"Time Series: {len(dashboard_data['time_series']['dates'])} days")
    print(f"Top Insights: {len(dashboard_data['top_insights'])}")
    
    return reporting_api, report


# Run all examples
async def run_examples():
    await example_basic_pipeline()
    await example_advanced_analytics()
    await example_file_storage()
    await example_reporting_api()


if __name__ == "__main__":
    asyncio.run(run_examples())