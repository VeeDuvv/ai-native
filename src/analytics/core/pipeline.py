# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file is like a manager for all the parts that collect, clean, and analyze ad data.
# It makes sure everything happens in the right order and all the information gets stored properly.

# High School Explanation:
# This module implements the analytics pipeline orchestrator that coordinates the collection,
# processing, analysis, and storage of advertising campaign data. It manages the sequence of
# operations, handles dependencies between processing stages, and ensures proper data flow
# through the entire analytics system.

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Awaitable, Set, Tuple, Union
import traceback

from .models import Metric, Dimension, PerformanceData, TimeRange
from .collectors import DataCollector
from .processors import DataProcessor
from .storage import StorageBackend

# Define processing stages in order of execution
PROCESSING_STAGES = [
    "RAW_DATA",      # Initial data as collected from source
    "CLEANED",       # Data after validation and cleaning
    "TRANSFORMED",   # Data after transformation and normalization
    "AGGREGATED",    # Data after aggregation and summarization
    "ENRICHED",      # Data after enrichment with additional information
    "ANALYZED"       # Data after analysis and insight generation
]

# Configure logging
logger = logging.getLogger(__name__)


class AnalyticsPipeline:
    """
    Orchestrates the collection, processing, and storage of analytics data.
    
    This class manages the flow of data through the analytics system, from
    collection to processing to storage and reporting. It coordinates the
    execution of collectors and processors in the correct sequence and handles
    dependencies between stages.
    """
    
    def __init__(self, 
                storage: StorageBackend,
                collectors: Optional[List[DataCollector]] = None,
                processors: Optional[Dict[str, List[DataProcessor]]] = None):
        """
        Initialize the analytics pipeline with the given components.
        
        Args:
            storage: The storage backend to use for persisting data
            collectors: List of data collectors to use
            processors: Dictionary mapping processing stages to lists of processors for that stage
        """
        self.storage = storage
        self.collectors = collectors or []
        self.processors = processors or {stage: [] for stage in PROCESSING_STAGES}
        self.running = False
        self.collection_tasks = set()
        self.processing_tasks = set()
        
        # Event for signaling collection completion
        self.collection_complete_event = asyncio.Event()
        
        # Registry of callbacks
        self.callbacks = {
            "collection_started": [],
            "collection_completed": [],
            "collection_failed": [],
            "processing_started": [],
            "processing_completed": [],
            "processing_failed": [],
            "pipeline_started": [],
            "pipeline_completed": [],
            "pipeline_failed": []
        }
    
    def register_collector(self, collector: DataCollector):
        """Register a new data collector with the pipeline."""
        self.collectors.append(collector)
    
    def register_processor(self, processor: DataProcessor, stage: str):
        """Register a new data processor with the pipeline for the given stage."""
        if stage not in PROCESSING_STAGES:
            raise ValueError(f"Invalid processing stage: {stage}. Must be one of {PROCESSING_STAGES}")
        
        if stage not in self.processors:
            self.processors[stage] = []
        
        self.processors[stage].append(processor)
    
    def register_callback(self, event: str, callback: Callable[..., Any]):
        """Register a callback function for a specific event."""
        if event not in self.callbacks:
            raise ValueError(f"Invalid event: {event}. Must be one of {list(self.callbacks.keys())}")
        
        self.callbacks[event].append(callback)
    
    async def _trigger_callbacks(self, event: str, **kwargs):
        """Trigger all registered callbacks for the given event."""
        for callback in self.callbacks.get(event, []):
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(**kwargs)
                else:
                    callback(**kwargs)
            except Exception as e:
                logger.error(f"Error in {event} callback: {e}")
                logger.debug(traceback.format_exc())
    
    async def collect_data(self, time_range: Optional[TimeRange] = None, max_concurrent: int = 5):
        """
        Collect data from all registered collectors.
        
        Args:
            time_range: Optional time range to collect data for
            max_concurrent: Maximum number of collectors to run concurrently
        
        Returns:
            List of data IDs for the collected data
        """
        await self._trigger_callbacks("collection_started", collectors=self.collectors)
        
        # Reset collection completion event
        self.collection_complete_event.clear()
        
        # Use a semaphore to limit concurrency
        semaphore = asyncio.Semaphore(max_concurrent)
        
        # Create a task for each collector
        data_ids = []
        
        async def collect_with_collector(collector: DataCollector):
            async with semaphore:
                try:
                    logger.info(f"Starting collection from {collector.name}")
                    collected_data = await collector.collect(time_range)
                    
                    # Store each collected data item
                    for data in collected_data:
                        data_id = self.storage.store_raw_data(
                            source=collector.name,
                            data=data,
                            timestamp=datetime.now()
                        )
                        data_ids.append(data_id)
                        logger.debug(f"Stored raw data with ID {data_id} from {collector.name}")
                
                except Exception as e:
                    logger.error(f"Error collecting data from {collector.name}: {e}")
                    logger.debug(traceback.format_exc())
                    await self._trigger_callbacks(
                        "collection_failed", 
                        collector=collector, 
                        error=str(e)
                    )
        
        # Schedule all collection tasks
        self.collection_tasks = {
            asyncio.create_task(collect_with_collector(collector))
            for collector in self.collectors
        }
        
        # Wait for all collection tasks to complete
        if self.collection_tasks:
            await asyncio.gather(*self.collection_tasks)
        
        # Signal that collection is complete
        self.collection_complete_event.set()
        
        await self._trigger_callbacks(
            "collection_completed", 
            data_ids=data_ids
        )
        
        return data_ids
    
    async def process_data(self, 
                        data_ids: List[str],
                        start_stage: str = "RAW_DATA",
                        end_stage: str = "ANALYZED",
                        max_concurrent: int = 10) -> Dict[str, List[str]]:
        """
        Process the data with the given IDs through the pipeline.
        
        Args:
            data_ids: List of data IDs to process
            start_stage: The stage to start processing from
            end_stage: The stage to stop processing at
            max_concurrent: Maximum number of processing tasks to run concurrently
        
        Returns:
            Dictionary mapping processing stages to lists of processed data IDs
        """
        await self._trigger_callbacks(
            "processing_started", 
            data_ids=data_ids, 
            start_stage=start_stage, 
            end_stage=end_stage
        )
        
        # Validate stages
        if start_stage not in PROCESSING_STAGES or end_stage not in PROCESSING_STAGES:
            raise ValueError(f"Invalid stage. Must be one of {PROCESSING_STAGES}")
        
        start_idx = PROCESSING_STAGES.index(start_stage)
        end_idx = PROCESSING_STAGES.index(end_stage)
        
        if start_idx > end_idx:
            raise ValueError(f"Start stage {start_stage} comes after end stage {end_stage}")
        
        # Track processed data IDs by stage
        processed_ids = {stage: [] for stage in PROCESSING_STAGES[start_idx:end_idx+1]}
        
        # For the first stage, use the input data IDs
        current_data_ids = data_ids
        
        # Create a semaphore to limit concurrency
        semaphore = asyncio.Semaphore(max_concurrent)
        
        # Process each stage in sequence
        for stage_idx in range(start_idx, end_idx + 1):
            stage = PROCESSING_STAGES[stage_idx]
            processors = self.processors.get(stage, [])
            
            if not processors:
                logger.warning(f"No processors registered for stage {stage}")
                continue
            
            logger.info(f"Processing stage {stage} with {len(current_data_ids)} data points")
            next_data_ids = []
            tasks = set()
            
            # Define the processing task for a single data point
            async def process_data_point(data_id: str, stage: str, processors: List[DataProcessor]):
                async with semaphore:
                    try:
                        # For the first stage, get raw data; otherwise get processed data
                        if stage == "RAW_DATA":
                            data = self.storage.retrieve_raw_data(data_id)
                            # Convert to PerformanceData for processors
                            performance_data = PerformanceData(
                                metrics={},
                                dimensions={"data_id": data_id},
                                segments=[]
                            )
                            # Add the raw data
                            performance_data.raw_data = data
                        else:
                            performance_data = self.storage.retrieve_processed_data(data_id)
                        
                        # Apply each processor in sequence
                        for processor in processors:
                            performance_data = await processor.process(performance_data)
                        
                        # Store the processed data
                        processed_id = self.storage.store_processed_data(
                            data_id=data_id,
                            data=performance_data,
                            processing_stage=stage
                        )
                        
                        next_data_ids.append(processed_id)
                        logger.debug(f"Processed data {data_id} to {processed_id} in stage {stage}")
                        
                        return processed_id
                    
                    except Exception as e:
                        logger.error(f"Error processing data {data_id} in stage {stage}: {e}")
                        logger.debug(traceback.format_exc())
                        await self._trigger_callbacks(
                            "processing_failed", 
                            data_id=data_id, 
                            stage=stage, 
                            error=str(e)
                        )
                        return None
            
            # Create tasks for all data points in this stage
            for data_id in current_data_ids:
                task = asyncio.create_task(
                    process_data_point(data_id, stage, processors)
                )
                tasks.add(task)
            
            # Wait for all tasks to complete
            if tasks:
                results = await asyncio.gather(*tasks)
                # Filter out None results (failed processing)
                next_data_ids = [result for result in results if result is not None]
            
            # Update processed IDs for this stage
            processed_ids[stage] = next_data_ids
            
            # Use the output of this stage as input for the next stage
            current_data_ids = next_data_ids
        
        await self._trigger_callbacks(
            "processing_completed", 
            processed_ids=processed_ids
        )
        
        return processed_ids
    
    async def generate_insights(self, 
                            processed_ids: Dict[str, List[str]],
                            insight_processors: List[DataProcessor]) -> List[str]:
        """
        Generate insights from processed data.
        
        Args:
            processed_ids: Dictionary mapping processing stages to lists of processed data IDs
            insight_processors: List of processors to use for generating insights
        
        Returns:
            List of insight IDs
        """
        if not insight_processors:
            logger.warning("No insight processors provided")
            return []
        
        # Collect all processed data IDs from the final stage
        final_stage = list(processed_ids.keys())[-1]
        data_ids = processed_ids[final_stage]
        
        if not data_ids:
            logger.warning(f"No processed data available in stage {final_stage}")
            return []
        
        insight_ids = []
        
        # Load all processed data
        processed_data = [self.storage.retrieve_processed_data(data_id) for data_id in data_ids]
        
        # Apply each insight processor
        for processor in insight_processors:
            try:
                # Most insight processors work on batches of data
                insights = await processor.process_batch(processed_data)
                
                # Store each insight
                for insight in insights:
                    insight_id = self.storage.store_insight(
                        data_ids=data_ids,
                        insight_type=processor.name,
                        insight_data=insight
                    )
                    insight_ids.append(insight_id)
                    logger.debug(f"Generated insight {insight_id} of type {processor.name}")
            
            except Exception as e:
                logger.error(f"Error generating insights with processor {processor.name}: {e}")
                logger.debug(traceback.format_exc())
        
        return insight_ids
    
    async def start(self, interval: Optional[int] = None):
        """
        Start the analytics pipeline.
        
        Args:
            interval: Optional interval in seconds to run the pipeline at.
                     If None, the pipeline runs once and then stops.
        """
        if self.running:
            logger.warning("Pipeline is already running")
            return
        
        self.running = True
        await self._trigger_callbacks("pipeline_started")
        
        try:
            if interval is None:
                # Run once
                time_range = TimeRange.last_24_hours()
                data_ids = await self.collect_data(time_range)
                processed_ids = await self.process_data(data_ids)
            else:
                # Run periodically
                while self.running:
                    try:
                        # Collect data for the past interval
                        end_date = datetime.now()
                        start_date = end_date - timedelta(seconds=interval)
                        time_range = TimeRange(start_date, end_date)
                        
                        # Collect and process data
                        data_ids = await self.collect_data(time_range)
                        if data_ids:
                            processed_ids = await self.process_data(data_ids)
                        
                        # Wait for the next interval
                        await asyncio.sleep(interval)
                    
                    except asyncio.CancelledError:
                        logger.info("Pipeline execution was cancelled")
                        break
                    
                    except Exception as e:
                        logger.error(f"Error in pipeline execution: {e}")
                        logger.debug(traceback.format_exc())
                        await self._trigger_callbacks("pipeline_failed", error=str(e))
                        
                        # Wait a bit before trying again
                        await asyncio.sleep(min(interval, 60))
        
        except Exception as e:
            logger.error(f"Fatal error in pipeline: {e}")
            logger.debug(traceback.format_exc())
            await self._trigger_callbacks("pipeline_failed", error=str(e))
        
        finally:
            self.running = False
            await self._trigger_callbacks("pipeline_completed")
    
    async def stop(self):
        """Stop the analytics pipeline."""
        if not self.running:
            logger.warning("Pipeline is not running")
            return
        
        logger.info("Stopping analytics pipeline")
        self.running = False
        
        # Cancel all collection tasks
        for task in self.collection_tasks:
            task.cancel()
        
        # Cancel all processing tasks
        for task in self.processing_tasks:
            task.cancel()
        
        # Wait for tasks to cancel
        if self.collection_tasks:
            await asyncio.gather(*self.collection_tasks, return_exceptions=True)
        
        if self.processing_tasks:
            await asyncio.gather(*self.processing_tasks, return_exceptions=True)
        
        logger.info("Analytics pipeline stopped")


class PipelineBuilder:
    """
    Builder class for creating and configuring analytics pipelines.
    
    This class provides a fluent interface for building analytics pipelines
    with specific collectors, processors, and storage backends.
    """
    
    def __init__(self, storage: StorageBackend):
        """Initialize the pipeline builder with the given storage backend."""
        self.storage = storage
        self.collectors = []
        self.processors = {stage: [] for stage in PROCESSING_STAGES}
        self.insight_processors = []
    
    def with_collector(self, collector: DataCollector) -> 'PipelineBuilder':
        """Add a collector to the pipeline."""
        self.collectors.append(collector)
        return self
    
    def with_processor(self, processor: DataProcessor, stage: str) -> 'PipelineBuilder':
        """Add a processor to the pipeline for the given stage."""
        if stage not in PROCESSING_STAGES:
            raise ValueError(f"Invalid processing stage: {stage}. Must be one of {PROCESSING_STAGES}")
        
        self.processors[stage].append(processor)
        return self
    
    def with_insight_processor(self, processor: DataProcessor) -> 'PipelineBuilder':
        """Add an insight processor to the pipeline."""
        self.insight_processors.append(processor)
        return self
    
    def build(self) -> AnalyticsPipeline:
        """Build and return an analytics pipeline with the configured components."""
        pipeline = AnalyticsPipeline(
            storage=self.storage,
            collectors=self.collectors,
            processors=self.processors
        )
        
        return pipeline
    
    @staticmethod
    def from_config(config: Dict[str, Any], storage: StorageBackend) -> 'PipelineBuilder':
        """
        Create a pipeline builder from a configuration dictionary.
        
        Args:
            config: Configuration dictionary with keys for collectors, processors, and insights
            storage: Storage backend to use
        
        Returns:
            Configured PipelineBuilder instance
        """
        builder = PipelineBuilder(storage)
        
        # Add collectors from config
        collector_configs = config.get("collectors", [])
        for collector_config in collector_configs:
            collector_type = collector_config.pop("type")
            # Instantiate collector based on type
            # This would need to be extended with actual collector classes
            # For now, we'll just log what would happen
            logger.info(f"Would create collector of type {collector_type} with config {collector_config}")
        
        # Add processors from config
        processor_configs = config.get("processors", {})
        for stage, stage_processors in processor_configs.items():
            for processor_config in stage_processors:
                processor_type = processor_config.pop("type")
                # Instantiate processor based on type
                # This would need to be extended with actual processor classes
                # For now, we'll just log what would happen
                logger.info(f"Would create processor of type {processor_type} for stage {stage} with config {processor_config}")
        
        # Add insight processors from config
        insight_configs = config.get("insights", [])
        for insight_config in insight_configs:
            insight_type = insight_config.pop("type")
            # Instantiate insight processor based on type
            # This would need to be extended with actual insight processor classes
            # For now, we'll just log what would happen
            logger.info(f"Would create insight processor of type {insight_type} with config {insight_config}")
        
        return builder