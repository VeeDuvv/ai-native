# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Campaign Analytics System

## Overview

The Campaign Analytics System is a comprehensive framework for collecting, processing, analyzing, and visualizing advertising campaign performance data. It provides flexible components for gathering data from various advertising platforms, processing this data through a series of stages, and generating insights to drive campaign optimization.

## Architecture

The system is built around the following core components:

### Data Models

Located in `core/models.py`, these provide the foundation for representing analytics data:

- **Metric**: Represents measurable values like impressions, clicks, and conversions
- **Dimension**: Represents attributes for segmenting data like campaign, channel, and date
- **Segment**: Defines specific portions of data based on dimension values
- **TimeRange**: Specifies time periods for data collection and analysis
- **PerformanceData**: Combines metrics, dimensions, and segments into comprehensive data points

### Data Collection

Located in `core/collectors.py`, these components gather raw data from various sources:

- **DataCollector**: Abstract base class for all collectors
- **GoogleAdsCollector**: Collects data from Google Ads platform
- **FacebookAdsCollector**: Collects data from Facebook Ads platform
- **PlatformCollector**: Generic collector for other advertising platforms

### Data Processing

Located in `core/processors.py`, these components transform and analyze the collected data:

- **DataProcessor**: Abstract base class for all processors
- **DataCleaner**: Validates and sanitizes raw data
- **DataTransformer**: Converts data into standardized formats
- **MetricCalculator**: Computes derived metrics from raw data
- **DataAggregator**: Combines data points for higher-level analysis
- **AnomalyDetector**: Identifies unusual patterns in the data
- **InsightGenerator**: Creates actionable recommendations based on the processed data

### Data Storage

Located in `core/storage.py`, these components provide persistence for analytics data:

- **StorageBackend**: Abstract base class for all storage implementations
- **InMemoryStorage**: Stores data in memory (ideal for testing)
- **FileStorage**: Stores data in the filesystem
- **SQLiteStorage**: Stores data in a SQLite database

### Analytics Pipeline

Located in `core/pipeline.py`, this component orchestrates the entire analytics process:

- **AnalyticsPipeline**: Manages the flow of data through collection, processing, and storage
- **PipelineBuilder**: Provides a fluent interface for configuring pipelines

### Reporting Interfaces

Located in `api/reporting.py`, these components expose the analytics data for consumption:

- **AnalyticsReportingAPI**: Provides API endpoints for querying and reporting
- **ReportFormatter**: Formats reports in various output formats (JSON, CSV, HTML, Markdown)

## Key Features

- **Modular Architecture**: Each component is designed to be used independently or as part of the whole system
- **Flexible Storage**: Support for multiple storage backends (memory, file, database)
- **Pipeline-Based Processing**: Data flows through a series of processing stages
- **Insight Generation**: Automatic detection of anomalies and generation of recommendations
- **Comprehensive Reporting**: Flexible query capabilities and multiple output formats
- **API-First Design**: All functionality is exposed through a consistent API

## Usage Examples

See `examples.py` for detailed usage examples, including:

1. Basic Analytics Pipeline
2. Advanced Analytics with Insights
3. File-Based Storage
4. Reporting API

## Getting Started

```python
import asyncio
from src.analytics import create_analytics_system

async def main():
    # Create a complete analytics system with default components
    pipeline, api = create_analytics_system(storage_type="memory")
    
    # Start the pipeline (collects and processes data once)
    await pipeline.start()
    
    # Query the data
    report_request = {
        "name": "Campaign Performance",
        "time_range": {
            "start_date": "2025-01-01T00:00:00",
            "end_date": "2025-01-31T23:59:59"
        },
        "metrics": [
            {"name": "impressions"},
            {"name": "clicks"},
            {"name": "cost"}
        ]
    }
    
    report = await api.create_router().post("/reports")(request=report_request, storage=pipeline.storage)
    print(f"Generated report with {len(report['data'])} data points")

if __name__ == "__main__":
    asyncio.run(main())
```

## Future Enhancements

- Integration with popular BI tools
- Machine learning-based predictive analytics
- Real-time streaming data processing
- Additional storage backends (e.g., Redis, PostgreSQL)
- Extended collection capabilities for more advertising platforms