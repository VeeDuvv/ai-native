# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file helps the computer understand how to use all the different parts of our analytics system.
# It's like a map that shows how all the pieces fit together to help us understand how well ads work.

# High School Explanation:
# This module initializes the analytics package and provides the main entry points 
# for using the analytics system. It imports and exposes the core components, 
# including data models, collectors, processors, storage backends, and the analytics API.
# This provides a clean interface for other parts of the application to interact with
# the analytics system.

from .core.models import Metric, Dimension, PerformanceData, TimeRange, Segment
from .core.collectors import DataCollector
from .core.processors import DataProcessor
from .core.storage import StorageBackend, create_storage
from .core.pipeline import AnalyticsPipeline, PipelineBuilder
from .api.reporting import AnalyticsReportingAPI, ReportFormatter

# Package version
__version__ = '0.1.0'


def create_analytics_system(storage_type='memory', **storage_kwargs):
    """
    Create a complete analytics system with default components.
    
    Args:
        storage_type: Type of storage backend to use ('memory', 'file', or 'sqlite')
        **storage_kwargs: Additional arguments to pass to the storage backend
    
    Returns:
        Tuple of (AnalyticsPipeline, AnalyticsReportingAPI)
    """
    # Create storage backend
    storage = create_storage(storage_type, **storage_kwargs)
    
    # Create pipeline
    pipeline_builder = PipelineBuilder(storage)
    pipeline = pipeline_builder.build()
    
    # Create API
    api = AnalyticsReportingAPI(storage)
    
    return pipeline, api