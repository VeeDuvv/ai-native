# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file contains code that takes the raw data about ad performance and 
# transforms it into useful information. It's like taking a pile of numbers
# and turning them into a clear report card that shows how well the ads are doing.

# High School Explanation:
# This module implements data processors for transforming, aggregating, and analyzing
# campaign performance data. It includes functionality for calculating metrics,
# detecting anomalies, generating insights, and creating standardized performance reports.

import logging
import math
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union
import statistics

from .models import (
    AggregationType, ComparisonPeriod, Dimension, Metric, MetricType,
    PerformanceData, PerformanceReport, Segment, TimeRange,
    COMMON_METRICS, COMMON_DIMENSIONS
)

# Set up logging
logger = logging.getLogger(__name__)


class DataProcessorType(Enum):
    """Types of data processors."""
    AGGREGATOR = "aggregator"              # Combines data points
    TRANSFORMER = "transformer"            # Changes data structure
    CALCULATOR = "calculator"              # Calculates derived metrics
    ANOMALY_DETECTOR = "anomaly_detector"  # Detects outliers
    INSIGHT_GENERATOR = "insight_generator"  # Generates insights from data
    FORECASTER = "forecaster"              # Makes predictions


class ProcessingStage(Enum):
    """Stages in the data processing pipeline."""
    RAW_DATA = "raw_data"                 # Unprocessed data
    CLEANED = "cleaned"                   # Validated and standardized data
    TRANSFORMED = "transformed"           # Restructured data
    AGGREGATED = "aggregated"             # Grouped and summed data
    ENRICHED = "enriched"                 # Data with calculated metrics
    ANALYZED = "analyzed"                 # Data with insights


class AnomalyType(Enum):
    """Types of anomalies that can be detected."""
    SPIKE = "spike"                        # Sudden increase
    DROP = "drop"                          # Sudden decrease
    TREND_CHANGE = "trend_change"          # Change in trend direction
    OUTLIER = "outlier"                    # Statistical outlier
    THRESHOLD_BREACH = "threshold_breach"  # Exceeds threshold
    SEASONAL_DEVIATION = "seasonal_deviation"  # Deviates from seasonal pattern


class InsightType(Enum):
    """Types of insights that can be generated."""
    TREND = "trend"                        # Time-based pattern
    CORRELATION = "correlation"            # Relationship between metrics
    COMPARISON = "comparison"              # Comparison between segments
    ANOMALY = "anomaly"                    # Detected anomaly
    RECOMMENDATION = "recommendation"      # Suggested action
    FORECAST = "forecast"                  # Predicted future performance


class InsightPriority(Enum):
    """Priority levels for insights."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DataProcessor(ABC):
    """Base class for data processors."""
    
    def __init__(
        self,
        name: str,
        processor_type: DataProcessorType,
        input_stage: ProcessingStage,
        output_stage: ProcessingStage,
        required_metrics: Optional[List[str]] = None,
        required_dimensions: Optional[List[str]] = None,
    ):
        self.name = name
        self.processor_type = processor_type
        self.input_stage = input_stage
        self.output_stage = output_stage
        self.required_metrics = required_metrics or []
        self.required_dimensions = required_dimensions or []
    
    @abstractmethod
    async def process(
        self,
        data: List[PerformanceData],
        context: Optional[Dict[str, Any]] = None
    ) -> List[Any]:
        """Process the provided data."""
        pass
    
    def can_process(self, data: List[PerformanceData]) -> bool:
        """Check if this processor can process the provided data."""
        if not data:
            return False
        
        # Check if all required metrics are available
        for metric_id in self.required_metrics:
            if any(metric_id not in item.metrics for item in data):
                logger.warning(f"Processor {self.name} missing required metric: {metric_id}")
                return False
        
        # Check if all required dimensions are available
        for dimension_id in self.required_dimensions:
            if any(dimension_id not in item.dimensions for item in data):
                logger.warning(f"Processor {self.name} missing required dimension: {dimension_id}")
                return False
        
        return True


class MetricCalculator(DataProcessor):
    """Processor that calculates derived metrics."""
    
    def __init__(
        self,
        name: str,
        metrics_to_calculate: List[str],
        required_metrics: Optional[List[str]] = None,
    ):
        super().__init__(
            name=name,
            processor_type=DataProcessorType.CALCULATOR,
            input_stage=ProcessingStage.CLEANED,
            output_stage=ProcessingStage.ENRICHED,
            required_metrics=required_metrics,
        )
        self.metrics_to_calculate = metrics_to_calculate
        
        # Ensure required metrics include dependencies
        if self.metrics_to_calculate and not self.required_metrics:
            self.required_metrics = []
            for metric_id in self.metrics_to_calculate:
                if metric_id in COMMON_METRICS and COMMON_METRICS[metric_id].is_calculated:
                    self.required_metrics.extend(COMMON_METRICS[metric_id].depends_on)
    
    async def process(
        self,
        data: List[PerformanceData],
        context: Optional[Dict[str, Any]] = None
    ) -> List[PerformanceData]:
        """Calculate derived metrics for each data point."""
        if not self.can_process(data):
            logger.warning(f"Processor {self.name} cannot process the provided data")
            return data
        
        result = []
        
        for data_point in data:
            # Create a copy of the data point to modify
            new_metrics = dict(data_point.metrics)
            
            # Calculate each requested metric
            for metric_id in self.metrics_to_calculate:
                if metric_id not in COMMON_METRICS:
                    logger.warning(f"Unknown metric: {metric_id}")
                    continue
                
                metric = COMMON_METRICS[metric_id]
                
                if not metric.is_calculated:
                    logger.warning(f"Metric {metric_id} is not a calculated metric")
                    continue
                
                # Check if all dependencies are available
                if not all(dep in new_metrics for dep in metric.depends_on):
                    logger.warning(f"Missing dependencies for metric {metric_id}")
                    continue
                
                # Calculate the metric based on its type
                if metric_id == "ctr":
                    # CTR = (clicks / impressions) * 100
                    impressions = new_metrics["impressions"]
                    clicks = new_metrics["clicks"]
                    if impressions > 0:
                        new_metrics["ctr"] = (clicks / impressions) * 100
                    else:
                        new_metrics["ctr"] = 0
                
                elif metric_id == "conversion_rate":
                    # Conversion Rate = (conversions / clicks) * 100
                    clicks = new_metrics["clicks"]
                    conversions = new_metrics["conversions"]
                    if clicks > 0:
                        new_metrics["conversion_rate"] = (conversions / clicks) * 100
                    else:
                        new_metrics["conversion_rate"] = 0
                
                elif metric_id == "cpa":
                    # CPA = spend / conversions
                    spend = new_metrics["spend"]
                    conversions = new_metrics["conversions"]
                    if conversions > 0:
                        new_metrics["cpa"] = spend / conversions
                    else:
                        new_metrics["cpa"] = 0
                
                elif metric_id == "roas":
                    # ROAS = revenue / spend
                    revenue = new_metrics["revenue"]
                    spend = new_metrics["spend"]
                    if spend > 0:
                        new_metrics["roas"] = revenue / spend
                    else:
                        new_metrics["roas"] = 0
            
            # Create a new data point with the calculated metrics
            new_data_point = PerformanceData(
                metrics=new_metrics,
                dimensions=data_point.dimensions,
                timestamp=data_point.timestamp,
                campaign_id=data_point.campaign_id,
                ad_group_id=data_point.ad_group_id,
                creative_id=data_point.creative_id,
                channel_id=data_point.channel_id,
            )
            
            result.append(new_data_point)
        
        logger.info(f"Calculated metrics for {len(result)} data points")
        return result


class DataAggregator(DataProcessor):
    """Processor that aggregates data by dimensions."""
    
    def __init__(
        self,
        name: str,
        dimensions: List[str],
        metrics: List[str],
        required_metrics: Optional[List[str]] = None,
        required_dimensions: Optional[List[str]] = None,
    ):
        super().__init__(
            name=name,
            processor_type=DataProcessorType.AGGREGATOR,
            input_stage=ProcessingStage.CLEANED,
            output_stage=ProcessingStage.AGGREGATED,
            required_metrics=required_metrics or metrics,
            required_dimensions=required_dimensions or dimensions,
        )
        self.dimensions = dimensions
        self.metrics = metrics
    
    async def process(
        self,
        data: List[PerformanceData],
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Aggregate data by the specified dimensions."""
        if not self.can_process(data):
            logger.warning(f"Processor {self.name} cannot process the provided data")
            return []
        
        # Group data by dimensions
        grouped_data = {}
        
        for data_point in data:
            # Create a key from the dimension values
            key_parts = []
            for dimension in self.dimensions:
                value = data_point.get_dimension(dimension)
                if value is None:
                    # Skip data points missing required dimensions
                    break
                key_parts.append(f"{dimension}:{value}")
            
            if len(key_parts) != len(self.dimensions):
                # Skip data points missing required dimensions
                continue
            
            key = "|".join(key_parts)
            
            if key not in grouped_data:
                # Initialize a new group
                grouped_data[key] = {
                    "dimensions": {dim: data_point.get_dimension(dim) for dim in self.dimensions},
                    "metrics": {metric: 0 for metric in self.metrics},
                    "count": 0
                }
            
            # Update metrics for the group
            for metric in self.metrics:
                value = data_point.get_metric(metric)
                if value is not None:
                    metric_def = COMMON_METRICS.get(metric)
                    
                    if metric_def and metric_def.aggregation == AggregationType.SUM:
                        # Simple addition
                        grouped_data[key]["metrics"][metric] += value
                    elif metric_def and metric_def.aggregation == AggregationType.AVERAGE:
                        # For average, we'll collect values and calculate at the end
                        if "avg_values" not in grouped_data[key]:
                            grouped_data[key]["avg_values"] = {}
                        
                        if metric not in grouped_data[key]["avg_values"]:
                            grouped_data[key]["avg_values"][metric] = []
                        
                        grouped_data[key]["avg_values"][metric].append(value)
                    elif metric_def and metric_def.aggregation == AggregationType.MAX:
                        # Max value
                        grouped_data[key]["metrics"][metric] = max(
                            grouped_data[key]["metrics"][metric], value
                        )
                    elif metric_def and metric_def.aggregation == AggregationType.MIN:
                        # Min value (initialize with first value)
                        if grouped_data[key]["count"] == 0:
                            grouped_data[key]["metrics"][metric] = value
                        else:
                            grouped_data[key]["metrics"][metric] = min(
                                grouped_data[key]["metrics"][metric], value
                            )
            
            # Increment the count for this group
            grouped_data[key]["count"] += 1
        
        # Process averages and other calculations
        for key, group in grouped_data.items():
            if "avg_values" in group:
                for metric, values in group["avg_values"].items():
                    if values:
                        group["metrics"][metric] = sum(values) / len(values)
                
                # Remove the temporary avg_values field
                del group["avg_values"]
            
            # Calculate derived metrics if needed
            # This is a simplified approach - in a real implementation,
            # you'd probably use the MetricCalculator
            if "clicks" in group["metrics"] and "impressions" in group["metrics"]:
                impressions = group["metrics"]["impressions"]
                clicks = group["metrics"]["clicks"]
                if impressions > 0 and "ctr" in self.metrics:
                    group["metrics"]["ctr"] = (clicks / impressions) * 100
            
            if "conversions" in group["metrics"] and "clicks" in group["metrics"]:
                clicks = group["metrics"]["clicks"]
                conversions = group["metrics"]["conversions"]
                if clicks > 0 and "conversion_rate" in self.metrics:
                    group["metrics"]["conversion_rate"] = (conversions / clicks) * 100
            
            if "spend" in group["metrics"] and "conversions" in group["metrics"]:
                spend = group["metrics"]["spend"]
                conversions = group["metrics"]["conversions"]
                if conversions > 0 and "cpa" in self.metrics:
                    group["metrics"]["cpa"] = spend / conversions
            
            if "revenue" in group["metrics"] and "spend" in group["metrics"]:
                revenue = group["metrics"]["revenue"]
                spend = group["metrics"]["spend"]
                if spend > 0 and "roas" in self.metrics:
                    group["metrics"]["roas"] = revenue / spend
        
        # Convert to list of dictionaries
        result = []
        for group in grouped_data.values():
            item = {
                **group["dimensions"],
                **group["metrics"]
            }
            result.append(item)
        
        logger.info(f"Aggregated {len(data)} data points into {len(result)} groups")
        return result


class AnomalyDetector(DataProcessor):
    """Processor that detects anomalies in time series data."""
    
    def __init__(
        self,
        name: str,
        metrics_to_monitor: List[str],
        detection_methods: Optional[List[str]] = None,
        sensitivity: float = 2.0,
        min_data_points: int = 7,
        required_dimensions: Optional[List[str]] = None,
    ):
        super().__init__(
            name=name,
            processor_type=DataProcessorType.ANOMALY_DETECTOR,
            input_stage=ProcessingStage.AGGREGATED,
            output_stage=ProcessingStage.ANALYZED,
            required_metrics=metrics_to_monitor,
            required_dimensions=required_dimensions or ["date"],
        )
        self.metrics_to_monitor = metrics_to_monitor
        self.detection_methods = detection_methods or ["z_score", "threshold"]
        self.sensitivity = sensitivity
        self.min_data_points = min_data_points
    
    async def process(
        self,
        data: List[PerformanceData],
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Detect anomalies in the provided data."""
        if not self.can_process(data) or len(data) < self.min_data_points:
            logger.warning(
                f"Processor {self.name} cannot process the provided data: "
                f"insufficient data points ({len(data)} < {self.min_data_points})"
            )
            return []
        
        # Ensure data is sorted by date
        sorted_data = sorted(data, key=lambda x: x.timestamp)
        
        anomalies = []
        
        for metric in self.metrics_to_monitor:
            # Extract time series for this metric
            time_series = [
                (data_point.timestamp, data_point.get_metric(metric))
                for data_point in sorted_data
                if data_point.get_metric(metric) is not None
            ]
            
            if len(time_series) < self.min_data_points:
                logger.warning(
                    f"Insufficient data points for metric {metric}: "
                    f"{len(time_series)} < {self.min_data_points}"
                )
                continue
            
            dates, values = zip(*time_series)
            
            # Detect anomalies using different methods
            for method in self.detection_methods:
                if method == "z_score":
                    # Z-score method
                    mean_val = statistics.mean(values)
                    stdev = statistics.stdev(values) if len(values) > 1 else 0
                    
                    if stdev == 0:
                        continue
                    
                    for i, (date, value) in enumerate(time_series):
                        z_score = (value - mean_val) / stdev
                        
                        if abs(z_score) > self.sensitivity:
                            anomaly_type = AnomalyType.SPIKE if z_score > 0 else AnomalyType.DROP
                            
                            anomalies.append({
                                "metric": metric,
                                "timestamp": date,
                                "value": value,
                                "expected_value": mean_val,
                                "deviation": z_score,
                                "type": anomaly_type.value,
                                "method": method,
                                "dimensions": {
                                    dim: sorted_data[i].get_dimension(dim)
                                    for dim in self.required_dimensions
                                    if sorted_data[i].get_dimension(dim) is not None
                                },
                                "campaign_id": sorted_data[i].campaign_id,
                                "ad_group_id": sorted_data[i].ad_group_id,
                                "creative_id": sorted_data[i].creative_id,
                                "channel_id": sorted_data[i].channel_id,
                            })
                
                elif method == "threshold":
                    # Simple threshold method
                    p25 = sorted(values)[int(len(values) * 0.25)]
                    p75 = sorted(values)[int(len(values) * 0.75)]
                    iqr = p75 - p25
                    
                    lower_bound = p25 - (iqr * self.sensitivity)
                    upper_bound = p75 + (iqr * self.sensitivity)
                    
                    for i, (date, value) in enumerate(time_series):
                        if value < lower_bound:
                            anomalies.append({
                                "metric": metric,
                                "timestamp": date,
                                "value": value,
                                "expected_value": (p25 + p75) / 2,
                                "deviation": (value - lower_bound) / (iqr or 1),
                                "type": AnomalyType.DROP.value,
                                "method": method,
                                "dimensions": {
                                    dim: sorted_data[i].get_dimension(dim)
                                    for dim in self.required_dimensions
                                    if sorted_data[i].get_dimension(dim) is not None
                                },
                                "campaign_id": sorted_data[i].campaign_id,
                                "ad_group_id": sorted_data[i].ad_group_id,
                                "creative_id": sorted_data[i].creative_id,
                                "channel_id": sorted_data[i].channel_id,
                            })
                        elif value > upper_bound:
                            anomalies.append({
                                "metric": metric,
                                "timestamp": date,
                                "value": value,
                                "expected_value": (p25 + p75) / 2,
                                "deviation": (value - upper_bound) / (iqr or 1),
                                "type": AnomalyType.SPIKE.value,
                                "method": method,
                                "dimensions": {
                                    dim: sorted_data[i].get_dimension(dim)
                                    for dim in self.required_dimensions
                                    if sorted_data[i].get_dimension(dim) is not None
                                },
                                "campaign_id": sorted_data[i].campaign_id,
                                "ad_group_id": sorted_data[i].ad_group_id,
                                "creative_id": sorted_data[i].creative_id,
                                "channel_id": sorted_data[i].channel_id,
                            })
                
                elif method == "trend_change":
                    # Detect trend changes (simplified approach)
                    if len(values) < 5:
                        continue
                    
                    # Calculate moving average
                    window_size = 3
                    moving_avg = []
                    
                    for i in range(len(values) - window_size + 1):
                        window = values[i:i+window_size]
                        avg = sum(window) / window_size
                        moving_avg.append(avg)
                    
                    # Look for significant changes in the moving average
                    for i in range(1, len(moving_avg)):
                        change = (moving_avg[i] - moving_avg[i-1]) / (moving_avg[i-1] if moving_avg[i-1] else 1)
                        
                        if abs(change) > 0.2:  # 20% change threshold
                            anomaly_type = AnomalyType.TREND_CHANGE
                            
                            anomalies.append({
                                "metric": metric,
                                "timestamp": dates[i + window_size - 2],  # Adjust index for window
                                "value": values[i + window_size - 2],
                                "expected_value": moving_avg[i-1],
                                "deviation": change * 100,  # Convert to percentage
                                "type": anomaly_type.value,
                                "method": method,
                                "dimensions": {
                                    dim: sorted_data[i + window_size - 2].get_dimension(dim)
                                    for dim in self.required_dimensions
                                    if sorted_data[i + window_size - 2].get_dimension(dim) is not None
                                },
                                "campaign_id": sorted_data[i + window_size - 2].campaign_id,
                                "ad_group_id": sorted_data[i + window_size - 2].ad_group_id,
                                "creative_id": sorted_data[i + window_size - 2].creative_id,
                                "channel_id": sorted_data[i + window_size - 2].channel_id,
                            })
        
        # De-duplicate anomalies (keep the one with the highest deviation)
        unique_anomalies = {}
        
        for anomaly in anomalies:
            key = f"{anomaly['metric']}|{anomaly['timestamp']}|{anomaly.get('campaign_id', '')}"
            
            if key not in unique_anomalies or abs(anomaly['deviation']) > abs(unique_anomalies[key]['deviation']):
                unique_anomalies[key] = anomaly
        
        logger.info(f"Detected {len(unique_anomalies)} anomalies in {len(data)} data points")
        return list(unique_anomalies.values())


class InsightGenerator(DataProcessor):
    """Processor that generates insights from performance data."""
    
    def __init__(
        self,
        name: str,
        insight_types: Optional[List[str]] = None,
        max_insights: int = 10,
        required_metrics: Optional[List[str]] = None,
        required_dimensions: Optional[List[str]] = None,
    ):
        super().__init__(
            name=name,
            processor_type=DataProcessorType.INSIGHT_GENERATOR,
            input_stage=ProcessingStage.AGGREGATED,
            output_stage=ProcessingStage.ANALYZED,
            required_metrics=required_metrics or ["impressions", "clicks", "conversions", "spend", "revenue"],
            required_dimensions=required_dimensions or ["date", "campaign"],
        )
        self.insight_types = insight_types or [
            InsightType.TREND.value,
            InsightType.COMPARISON.value,
            InsightType.RECOMMENDATION.value
        ]
        self.max_insights = max_insights
    
    async def process(
        self,
        data: List[PerformanceData],
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Generate insights from the provided data."""
        if not self.can_process(data):
            logger.warning(f"Processor {self.name} cannot process the provided data")
            return []
        
        insights = []
        
        # Generate different types of insights
        if InsightType.TREND.value in self.insight_types:
            trend_insights = self._generate_trend_insights(data)
            insights.extend(trend_insights)
        
        if InsightType.COMPARISON.value in self.insight_types:
            comparison_insights = self._generate_comparison_insights(data)
            insights.extend(comparison_insights)
        
        if InsightType.RECOMMENDATION.value in self.insight_types:
            recommendation_insights = self._generate_recommendation_insights(data)
            insights.extend(recommendation_insights)
        
        # Sort by priority and limit to max_insights
        insights.sort(key=lambda x: self._priority_value(x.get("priority", InsightPriority.MEDIUM.value)), reverse=True)
        return insights[:self.max_insights]
    
    def _priority_value(self, priority: str) -> int:
        """Convert priority string to numeric value for sorting."""
        priorities = {
            InsightPriority.LOW.value: 1,
            InsightPriority.MEDIUM.value: 2,
            InsightPriority.HIGH.value: 3,
            InsightPriority.CRITICAL.value: 4
        }
        return priorities.get(priority, 2)
    
    def _generate_trend_insights(self, data: List[PerformanceData]) -> List[Dict[str, Any]]:
        """Generate insights about trends over time."""
        insights = []
        
        # Group data by date
        date_grouped = {}
        
        for data_point in data:
            date_str = data_point.get_dimension("date")
            if not date_str:
                continue
            
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
            
            if date not in date_grouped:
                date_grouped[date] = {
                    "impressions": 0,
                    "clicks": 0,
                    "conversions": 0,
                    "spend": 0,
                    "revenue": 0
                }
            
            # Aggregate metrics
            for metric in ["impressions", "clicks", "conversions", "spend", "revenue"]:
                value = data_point.get_metric(metric)
                if value is not None:
                    date_grouped[date][metric] += value
        
        if len(date_grouped) < 7:
            # Not enough data for trend analysis
            return []
        
        # Sort dates
        sorted_dates = sorted(date_grouped.keys())
        
        # Calculate week-over-week changes for the last 7 days
        if len(sorted_dates) >= 14:
            current_week = sorted_dates[-7:]
            previous_week = sorted_dates[-14:-7]
            
            current_totals = {
                metric: sum(date_grouped[date][metric] for date in current_week)
                for metric in ["impressions", "clicks", "conversions", "spend", "revenue"]
            }
            
            previous_totals = {
                metric: sum(date_grouped[date][metric] for date in previous_week)
                for metric in ["impressions", "clicks", "conversions", "spend", "revenue"]
            }
            
            # Calculate changes
            changes = {}
            for metric in ["impressions", "clicks", "conversions", "spend", "revenue"]:
                if previous_totals[metric] > 0:
                    changes[metric] = (current_totals[metric] - previous_totals[metric]) / previous_totals[metric] * 100
                else:
                    changes[metric] = 0
            
            # Generate insights based on significant changes
            for metric in ["conversions", "revenue", "spend"]:
                if abs(changes[metric]) >= 10:  # 10% change threshold
                    direction = "increased" if changes[metric] > 0 else "decreased"
                    priority = InsightPriority.HIGH.value if metric in ["revenue", "conversions"] else InsightPriority.MEDIUM.value
                    
                    insight = {
                        "type": InsightType.TREND.value,
                        "metric": metric,
                        "title": f"{metric.capitalize()} {direction} by {abs(changes[metric]):.1f}% week-over-week",
                        "description": (
                            f"Your {metric} have {direction} by {abs(changes[metric]):.1f}% "
                            f"compared to the previous week "
                            f"({current_totals[metric]:.1f} vs {previous_totals[metric]:.1f})."
                        ),
                        "priority": priority,
                        "time_range": {
                            "start": min(current_week).isoformat(),
                            "end": max(current_week).isoformat(),
                            "comparison_start": min(previous_week).isoformat(),
                            "comparison_end": max(previous_week).isoformat()
                        },
                        "change_percentage": changes[metric]
                    }
                    
                    insights.append(insight)
            
            # Look for efficiency improvements or declines
            if previous_totals["clicks"] > 0 and current_totals["clicks"] > 0:
                prev_ctr = (previous_totals["clicks"] / previous_totals["impressions"]) * 100 if previous_totals["impressions"] > 0 else 0
                curr_ctr = (current_totals["clicks"] / current_totals["impressions"]) * 100 if current_totals["impressions"] > 0 else 0
                
                ctr_change = curr_ctr - prev_ctr
                
                if abs(ctr_change) >= 0.5:  # 0.5 percentage point change threshold
                    direction = "improved" if ctr_change > 0 else "declined"
                    
                    insight = {
                        "type": InsightType.TREND.value,
                        "metric": "ctr",
                        "title": f"Click-through rate has {direction} by {abs(ctr_change):.2f} percentage points",
                        "description": (
                            f"Your click-through rate has {direction} from {prev_ctr:.2f}% to {curr_ctr:.2f}%, "
                            f"indicating that your ads are becoming {'more' if ctr_change > 0 else 'less'} engaging."
                        ),
                        "priority": InsightPriority.MEDIUM.value,
                        "time_range": {
                            "start": min(current_week).isoformat(),
                            "end": max(current_week).isoformat(),
                            "comparison_start": min(previous_week).isoformat(),
                            "comparison_end": max(previous_week).isoformat()
                        },
                        "change_percentage": (curr_ctr - prev_ctr) / prev_ctr * 100 if prev_ctr > 0 else 0
                    }
                    
                    insights.append(insight)
                
                # Check conversion rate changes
                prev_cvr = (previous_totals["conversions"] / previous_totals["clicks"]) * 100 if previous_totals["clicks"] > 0 else 0
                curr_cvr = (current_totals["conversions"] / current_totals["clicks"]) * 100 if current_totals["clicks"] > 0 else 0
                
                cvr_change = curr_cvr - prev_cvr
                
                if abs(cvr_change) >= 0.5:  # 0.5 percentage point change threshold
                    direction = "improved" if cvr_change > 0 else "declined"
                    
                    insight = {
                        "type": InsightType.TREND.value,
                        "metric": "conversion_rate",
                        "title": f"Conversion rate has {direction} by {abs(cvr_change):.2f} percentage points",
                        "description": (
                            f"Your conversion rate has {direction} from {prev_cvr:.2f}% to {curr_cvr:.2f}%, "
                            f"indicating that your landing pages are converting {'better' if cvr_change > 0 else 'worse'}."
                        ),
                        "priority": InsightPriority.HIGH.value,
                        "time_range": {
                            "start": min(current_week).isoformat(),
                            "end": max(current_week).isoformat(),
                            "comparison_start": min(previous_week).isoformat(),
                            "comparison_end": max(previous_week).isoformat()
                        },
                        "change_percentage": (curr_cvr - prev_cvr) / prev_cvr * 100 if prev_cvr > 0 else 0
                    }
                    
                    insights.append(insight)
                
                # Check ROAS changes
                prev_roas = previous_totals["revenue"] / previous_totals["spend"] if previous_totals["spend"] > 0 else 0
                curr_roas = current_totals["revenue"] / current_totals["spend"] if current_totals["spend"] > 0 else 0
                
                roas_change = curr_roas - prev_roas
                
                if abs(roas_change) >= 0.2:  # 0.2 ROAS change threshold
                    direction = "improved" if roas_change > 0 else "declined"
                    
                    insight = {
                        "type": InsightType.TREND.value,
                        "metric": "roas",
                        "title": f"Return on ad spend has {direction} by {abs(roas_change):.2f}x",
                        "description": (
                            f"Your ROAS has {direction} from {prev_roas:.2f}x to {curr_roas:.2f}x, "
                            f"indicating that your ads are becoming {'more' if roas_change > 0 else 'less'} profitable."
                        ),
                        "priority": InsightPriority.HIGH.value,
                        "time_range": {
                            "start": min(current_week).isoformat(),
                            "end": max(current_week).isoformat(),
                            "comparison_start": min(previous_week).isoformat(),
                            "comparison_end": max(previous_week).isoformat()
                        },
                        "change_percentage": (curr_roas - prev_roas) / prev_roas * 100 if prev_roas > 0 else 0
                    }
                    
                    insights.append(insight)
        
        return insights
    
    def _generate_comparison_insights(self, data: List[PerformanceData]) -> List[Dict[str, Any]]:
        """Generate insights comparing different segments."""
        insights = []
        
        # Group data by campaign
        campaign_grouped = {}
        
        for data_point in data:
            campaign = data_point.get_dimension("campaign")
            if not campaign:
                continue
            
            if campaign not in campaign_grouped:
                campaign_grouped[campaign] = {
                    "impressions": 0,
                    "clicks": 0,
                    "conversions": 0,
                    "spend": 0,
                    "revenue": 0,
                    "campaign_id": data_point.campaign_id
                }
            
            # Aggregate metrics
            for metric in ["impressions", "clicks", "conversions", "spend", "revenue"]:
                value = data_point.get_metric(metric)
                if value is not None:
                    campaign_grouped[campaign][metric] += value
        
        if len(campaign_grouped) < 2:
            # Not enough campaigns for comparison
            return []
        
        # Calculate performance metrics for each campaign
        for campaign, metrics in campaign_grouped.items():
            metrics["ctr"] = (metrics["clicks"] / metrics["impressions"]) * 100 if metrics["impressions"] > 0 else 0
            metrics["conversion_rate"] = (metrics["conversions"] / metrics["clicks"]) * 100 if metrics["clicks"] > 0 else 0
            metrics["cpa"] = metrics["spend"] / metrics["conversions"] if metrics["conversions"] > 0 else 0
            metrics["roas"] = metrics["revenue"] / metrics["spend"] if metrics["spend"] > 0 else 0
        
        # Find best and worst performing campaigns
        if len(campaign_grouped) >= 3:
            # Sort campaigns by ROAS
            sorted_by_roas = sorted(
                [(campaign, metrics) for campaign, metrics in campaign_grouped.items() if metrics["spend"] > 100],
                key=lambda x: x[1]["roas"],
                reverse=True
            )
            
            if len(sorted_by_roas) >= 2:
                best_campaign, best_metrics = sorted_by_roas[0]
                worst_campaign, worst_metrics = sorted_by_roas[-1]
                
                roas_diff = best_metrics["roas"] - worst_metrics["roas"]
                
                if roas_diff > 1.0:  # At least 1.0 ROAS difference
                    insight = {
                        "type": InsightType.COMPARISON.value,
                        "metric": "roas",
                        "title": f"Campaign '{best_campaign}' outperforms '{worst_campaign}' by {roas_diff:.2f}x ROAS",
                        "description": (
                            f"Your best-performing campaign '{best_campaign}' achieves {best_metrics['roas']:.2f}x ROAS, "
                            f"while '{worst_campaign}' only reaches {worst_metrics['roas']:.2f}x ROAS. "
                            f"Consider reallocating budget to the better-performing campaign."
                        ),
                        "priority": InsightPriority.HIGH.value,
                        "comparison": {
                            "winner": {
                                "campaign": best_campaign,
                                "campaign_id": best_metrics["campaign_id"],
                                "roas": best_metrics["roas"],
                                "spend": best_metrics["spend"],
                                "revenue": best_metrics["revenue"]
                            },
                            "loser": {
                                "campaign": worst_campaign,
                                "campaign_id": worst_metrics["campaign_id"],
                                "roas": worst_metrics["roas"],
                                "spend": worst_metrics["spend"],
                                "revenue": worst_metrics["revenue"]
                            }
                        }
                    }
                    
                    insights.append(insight)
            
            # Sort campaigns by conversion rate
            sorted_by_cvr = sorted(
                [(campaign, metrics) for campaign, metrics in campaign_grouped.items() if metrics["clicks"] > 100],
                key=lambda x: x[1]["conversion_rate"],
                reverse=True
            )
            
            if len(sorted_by_cvr) >= 2:
                best_campaign, best_metrics = sorted_by_cvr[0]
                worst_campaign, worst_metrics = sorted_by_cvr[-1]
                
                cvr_diff = best_metrics["conversion_rate"] - worst_metrics["conversion_rate"]
                
                if cvr_diff > 1.0:  # At least 1 percentage point difference
                    insight = {
                        "type": InsightType.COMPARISON.value,
                        "metric": "conversion_rate",
                        "title": f"Campaign '{best_campaign}' has {cvr_diff:.2f}% higher conversion rate than '{worst_campaign}'",
                        "description": (
                            f"Your campaign '{best_campaign}' achieves a {best_metrics['conversion_rate']:.2f}% conversion rate, "
                            f"significantly higher than '{worst_campaign}' at {worst_metrics['conversion_rate']:.2f}%. "
                            f"Consider analyzing the landing page differences."
                        ),
                        "priority": InsightPriority.MEDIUM.value,
                        "comparison": {
                            "winner": {
                                "campaign": best_campaign,
                                "campaign_id": best_metrics["campaign_id"],
                                "conversion_rate": best_metrics["conversion_rate"],
                                "clicks": best_metrics["clicks"],
                                "conversions": best_metrics["conversions"]
                            },
                            "loser": {
                                "campaign": worst_campaign,
                                "campaign_id": worst_metrics["campaign_id"],
                                "conversion_rate": worst_metrics["conversion_rate"],
                                "clicks": worst_metrics["clicks"],
                                "conversions": worst_metrics["conversions"]
                            }
                        }
                    }
                    
                    insights.append(insight)
            
            # Sort campaigns by CTR
            sorted_by_ctr = sorted(
                [(campaign, metrics) for campaign, metrics in campaign_grouped.items() if metrics["impressions"] > 1000],
                key=lambda x: x[1]["ctr"],
                reverse=True
            )
            
            if len(sorted_by_ctr) >= 2:
                best_campaign, best_metrics = sorted_by_ctr[0]
                worst_campaign, worst_metrics = sorted_by_ctr[-1]
                
                ctr_diff = best_metrics["ctr"] - worst_metrics["ctr"]
                
                if ctr_diff > 1.0:  # At least 1 percentage point difference
                    insight = {
                        "type": InsightType.COMPARISON.value,
                        "metric": "ctr",
                        "title": f"Campaign '{best_campaign}' has {ctr_diff:.2f}% higher CTR than '{worst_campaign}'",
                        "description": (
                            f"Your campaign '{best_campaign}' achieves a {best_metrics['ctr']:.2f}% click-through rate, "
                            f"significantly higher than '{worst_campaign}' at {worst_metrics['ctr']:.2f}%. "
                            f"Consider reviewing the ad creatives and messaging."
                        ),
                        "priority": InsightPriority.MEDIUM.value,
                        "comparison": {
                            "winner": {
                                "campaign": best_campaign,
                                "campaign_id": best_metrics["campaign_id"],
                                "ctr": best_metrics["ctr"],
                                "impressions": best_metrics["impressions"],
                                "clicks": best_metrics["clicks"]
                            },
                            "loser": {
                                "campaign": worst_campaign,
                                "campaign_id": worst_metrics["campaign_id"],
                                "ctr": worst_metrics["ctr"],
                                "impressions": worst_metrics["impressions"],
                                "clicks": worst_metrics["clicks"]
                            }
                        }
                    }
                    
                    insights.append(insight)
        
        return insights
    
    def _generate_recommendation_insights(self, data: List[PerformanceData]) -> List[Dict[str, Any]]:
        """Generate actionable recommendations based on the data."""
        insights = []
        
        # Group data by campaign
        campaign_grouped = {}
        
        for data_point in data:
            campaign = data_point.get_dimension("campaign")
            if not campaign:
                continue
            
            if campaign not in campaign_grouped:
                campaign_grouped[campaign] = {
                    "impressions": 0,
                    "clicks": 0,
                    "conversions": 0,
                    "spend": 0,
                    "revenue": 0,
                    "campaign_id": data_point.campaign_id
                }
            
            # Aggregate metrics
            for metric in ["impressions", "clicks", "conversions", "spend", "revenue"]:
                value = data_point.get_metric(metric)
                if value is not None:
                    campaign_grouped[campaign][metric] += value
        
        # Calculate performance metrics for each campaign
        total_spend = 0
        total_revenue = 0
        
        for campaign, metrics in campaign_grouped.items():
            metrics["ctr"] = (metrics["clicks"] / metrics["impressions"]) * 100 if metrics["impressions"] > 0 else 0
            metrics["conversion_rate"] = (metrics["conversions"] / metrics["clicks"]) * 100 if metrics["clicks"] > 0 else 0
            metrics["cpa"] = metrics["spend"] / metrics["conversions"] if metrics["conversions"] > 0 else 0
            metrics["roas"] = metrics["revenue"] / metrics["spend"] if metrics["spend"] > 0 else 0
            
            total_spend += metrics["spend"]
            total_revenue += metrics["revenue"]
        
        # Overall ROAS recommendation
        overall_roas = total_revenue / total_spend if total_spend > 0 else 0
        
        if overall_roas < 1.0 and total_spend > 1000:
            insight = {
                "type": InsightType.RECOMMENDATION.value,
                "metric": "roas",
                "title": "Improve overall return on ad spend",
                "description": (
                    f"Your overall ROAS is {overall_roas:.2f}x, which means you're spending more on ads "
                    f"than you're making in revenue. Consider reducing spend on low-performing campaigns "
                    f"or improving conversion rates to increase profitability."
                ),
                "priority": InsightPriority.HIGH.value,
                "recommendation": "Reduce spend on campaigns with ROAS < 1.0 and focus on improving conversion rates."
            }
            
            insights.append(insight)
        
        # Campaign-specific recommendations
        for campaign, metrics in campaign_grouped.items():
            # Low CTR recommendation
            if metrics["ctr"] < 1.0 and metrics["impressions"] > 10000:
                insight = {
                    "type": InsightType.RECOMMENDATION.value,
                    "metric": "ctr",
                    "title": f"Improve click-through rate for campaign '{campaign}'",
                    "description": (
                        f"Your campaign '{campaign}' has a low CTR of {metrics['ctr']:.2f}%. "
                        f"Consider improving ad creatives, headlines, or targeting to increase engagement."
                    ),
                    "priority": InsightPriority.MEDIUM.value,
                    "recommendation": "Test new ad creatives with more compelling messaging and calls-to-action.",
                    "campaign": campaign,
                    "campaign_id": metrics["campaign_id"]
                }
                
                insights.append(insight)
            
            # Low conversion rate recommendation
            if metrics["conversion_rate"] < 1.0 and metrics["clicks"] > 1000:
                insight = {
                    "type": InsightType.RECOMMENDATION.value,
                    "metric": "conversion_rate",
                    "title": f"Improve conversion rate for campaign '{campaign}'",
                    "description": (
                        f"Your campaign '{campaign}' has a low conversion rate of {metrics['conversion_rate']:.2f}%. "
                        f"Consider optimizing landing pages, offering better incentives, or improving the user experience."
                    ),
                    "priority": InsightPriority.HIGH.value,
                    "recommendation": "A/B test landing pages with different layouts, messaging, or calls-to-action.",
                    "campaign": campaign,
                    "campaign_id": metrics["campaign_id"]
                }
                
                insights.append(insight)
            
            # High CPA recommendation
            if metrics["cpa"] > 100 and metrics["conversions"] > 10:
                insight = {
                    "type": InsightType.RECOMMENDATION.value,
                    "metric": "cpa",
                    "title": f"Reduce cost per acquisition for campaign '{campaign}'",
                    "description": (
                        f"Your campaign '{campaign}' has a high CPA of ${metrics['cpa']:.2f}. "
                        f"Consider optimizing targeting, reducing bids, or improving conversion rates."
                    ),
                    "priority": InsightPriority.HIGH.value,
                    "recommendation": "Review audience targeting to focus on segments with higher conversion rates.",
                    "campaign": campaign,
                    "campaign_id": metrics["campaign_id"]
                }
                
                insights.append(insight)
            
            # Low ROAS recommendation
            if metrics["roas"] < 1.5 and metrics["spend"] > 500:
                insight = {
                    "type": InsightType.RECOMMENDATION.value,
                    "metric": "roas",
                    "title": f"Improve return on ad spend for campaign '{campaign}'",
                    "description": (
                        f"Your campaign '{campaign}' has a ROAS of {metrics['roas']:.2f}x, which is below the recommended 2.0x. "
                        f"Consider adjusting bidding strategies, targeting, or creative messaging."
                    ),
                    "priority": InsightPriority.HIGH.value,
                    "recommendation": "Focus budget on higher-converting audience segments and optimize bidding strategies.",
                    "campaign": campaign,
                    "campaign_id": metrics["campaign_id"]
                }
                
                insights.append(insight)
        
        return insights


class AnalyticsProcessorRegistry:
    """Registry of analytics data processors."""
    
    def __init__(self):
        self.processors: Dict[str, DataProcessor] = {}
    
    def register_processor(self, processor: DataProcessor) -> bool:
        """Register a new processor."""
        if processor.name in self.processors:
            logger.warning(f"Processor with name {processor.name} already exists")
            return False
        
        self.processors[processor.name] = processor
        logger.info(f"Registered processor {processor.name}")
        return True
    
    def unregister_processor(self, name: str) -> bool:
        """Unregister a processor."""
        if name not in self.processors:
            logger.warning(f"Processor with name {name} does not exist")
            return False
        
        del self.processors[name]
        logger.info(f"Unregistered processor {name}")
        return True
    
    def get_processor(self, name: str) -> Optional[DataProcessor]:
        """Get a processor by name."""
        return self.processors.get(name)
    
    def get_processors(self) -> List[DataProcessor]:
        """Get all registered processors."""
        return list(self.processors.values())
    
    def get_processors_by_type(self, processor_type: DataProcessorType) -> List[DataProcessor]:
        """Get processors by type."""
        return [p for p in self.processors.values() if p.processor_type == processor_type]
    
    def get_processors_for_stage(self, stage: ProcessingStage) -> List[DataProcessor]:
        """Get processors that operate on a specific stage."""
        return [p for p in self.processors.values() if p.input_stage == stage]
    
    async def process_data(
        self,
        data: List[PerformanceData],
        processor_names: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process data using the specified processors."""
        results = {}
        
        if processor_names:
            # Use only the specified processors
            for name in processor_names:
                processor = self.get_processor(name)
                if not processor:
                    logger.warning(f"Processor {name} not found")
                    continue
                
                if not processor.can_process(data):
                    logger.warning(f"Processor {name} cannot process the provided data")
                    continue
                
                logger.info(f"Processing data with {name}")
                result = await processor.process(data, context)
                results[name] = result
        else:
            # Process with all processors in order of stages
            stages = [
                ProcessingStage.RAW_DATA,
                ProcessingStage.CLEANED,
                ProcessingStage.TRANSFORMED,
                ProcessingStage.AGGREGATED,
                ProcessingStage.ENRICHED,
                ProcessingStage.ANALYZED
            ]
            
            current_data = data
            
            for stage in stages:
                stage_processors = self.get_processors_for_stage(stage)
                
                for processor in stage_processors:
                    if not processor.can_process(current_data):
                        logger.warning(f"Processor {processor.name} cannot process the provided data")
                        continue
                    
                    logger.info(f"Processing data with {processor.name} (stage: {stage.value})")
                    result = await processor.process(current_data, context)
                    results[processor.name] = result
                    
                    # If the processor transforms the data, update current_data
                    if isinstance(result, list) and result and isinstance(result[0], PerformanceData):
                        current_data = result
        
        return results


# Create a singleton instance
processor_registry = AnalyticsProcessorRegistry()