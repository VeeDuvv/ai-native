# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file defines the different types of data we collect about advertising campaigns,
# like how many people clicked on an ad or how much money was spent.

# High School Explanation:
# This module defines the data models used in the campaign analytics system. It includes
# classes for metrics, dimensions, time periods, and segment definitions which form the
# foundation for collecting, aggregating, and analyzing campaign performance data.

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Union, Any
from uuid import UUID, uuid4


class MetricType(Enum):
    """Types of metrics that can be tracked in the analytics system."""
    COUNT = "count"                  # Simple count metrics (impressions, clicks)
    CURRENCY = "currency"            # Monetary values (spend, revenue)
    PERCENTAGE = "percentage"        # Ratio metrics (CTR, conversion rate)
    DURATION = "duration"            # Time-based metrics (avg. session duration)
    COMPOSITE = "composite"          # Calculated from other metrics (ROAS, CPA)


class AggregationType(Enum):
    """Types of aggregation methods for metrics."""
    SUM = "sum"                      # Simple addition (impressions, clicks)
    AVERAGE = "average"              # Average value (avg. position)
    WEIGHTED_AVERAGE = "weighted_avg"  # Weighted average (CTR across campaigns)
    LAST = "last"                    # Last value (current bid)
    MAX = "max"                      # Maximum value (highest position)
    MIN = "min"                      # Minimum value (lowest CPC)
    COUNT_UNIQUE = "count_unique"    # Count unique values (unique users)


class ComparisonPeriod(Enum):
    """Standard time periods for comparisons."""
    PREVIOUS_PERIOD = "previous_period"  # Previous equivalent period
    PREVIOUS_WEEK = "previous_week"      # Last week
    PREVIOUS_MONTH = "previous_month"    # Last month
    PREVIOUS_QUARTER = "previous_quarter"  # Last quarter
    PREVIOUS_YEAR = "previous_year"      # Last year
    CUSTOM = "custom"                    # Custom date range


@dataclass
class Metric:
    """Definition of an analytics metric."""
    id: str
    name: str
    description: str
    type: MetricType
    aggregation: AggregationType
    unit: Optional[str] = None
    is_calculated: bool = False
    depends_on: List[str] = field(default_factory=list)
    format_spec: Optional[str] = None
    
    def format_value(self, value: Union[int, float]) -> str:
        """Format the metric value for display."""
        if self.format_spec:
            return self.format_spec.format(value)
        
        if self.type == MetricType.CURRENCY:
            return f"${value:.2f}"
        elif self.type == MetricType.PERCENTAGE:
            return f"{value:.2f}%"
        elif self.type == MetricType.DURATION:
            # Format duration in seconds to minutes:seconds
            minutes, seconds = divmod(int(value), 60)
            return f"{minutes}:{seconds:02d}"
        else:
            # Default formatting for other types
            return f"{value:,}"


@dataclass
class Dimension:
    """Definition of a dimension used for data segmentation."""
    id: str
    name: str
    description: str
    cardinality: str  # "low", "medium", "high"
    is_temporal: bool = False
    allowed_values: Optional[List[str]] = None
    
    def validate_value(self, value: str) -> bool:
        """Validate if a value is allowed for this dimension."""
        if self.allowed_values is None:
            return True
        return value in self.allowed_values


@dataclass
class TimeRange:
    """Time range for analytics queries."""
    start_date: datetime
    end_date: datetime
    
    @classmethod
    def last_n_days(cls, n: int) -> 'TimeRange':
        """Create a TimeRange for the last n days."""
        end_date = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
        start_date = (end_date - timedelta(days=n)).replace(hour=0, minute=0, second=0, microsecond=0)
        return cls(start_date=start_date, end_date=end_date)
    
    @classmethod
    def last_week(cls) -> 'TimeRange':
        """Create a TimeRange for the last week."""
        return cls.last_n_days(7)
    
    @classmethod
    def last_month(cls) -> 'TimeRange':
        """Create a TimeRange for the last month."""
        return cls.last_n_days(30)
    
    @classmethod
    def last_quarter(cls) -> 'TimeRange':
        """Create a TimeRange for the last quarter."""
        return cls.last_n_days(90)
    
    @classmethod
    def last_year(cls) -> 'TimeRange':
        """Create a TimeRange for the last year."""
        return cls.last_n_days(365)
    
    @classmethod
    def current_month(cls) -> 'TimeRange':
        """Create a TimeRange for the current month."""
        now = datetime.now()
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        return cls(start_date=start_date, end_date=end_date)


@dataclass
class Segment:
    """Definition of a data segment for targeted analysis."""
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""
    filters: Dict[str, Any] = field(default_factory=dict)
    
    def matches(self, data_point: Dict[str, Any]) -> bool:
        """Check if a data point matches this segment's filters."""
        for dimension, value in self.filters.items():
            if dimension not in data_point:
                return False
            
            # Handle list of values (OR condition)
            if isinstance(value, list):
                if data_point[dimension] not in value:
                    return False
            # Handle exact match
            elif data_point[dimension] != value:
                return False
        
        return True


@dataclass
class PerformanceData:
    """Container for performance data with metrics."""
    metrics: Dict[str, Union[int, float]]
    dimensions: Dict[str, str]
    timestamp: datetime = field(default_factory=datetime.now)
    campaign_id: Optional[UUID] = None
    ad_group_id: Optional[UUID] = None
    creative_id: Optional[UUID] = None
    channel_id: Optional[str] = None
    
    def get_metric(self, metric_id: str) -> Union[int, float, None]:
        """Get a metric value by ID."""
        return self.metrics.get(metric_id)
    
    def get_dimension(self, dimension_id: str) -> Optional[str]:
        """Get a dimension value by ID."""
        return self.dimensions.get(dimension_id)


@dataclass
class PerformanceReport:
    """A report containing aggregated performance data."""
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""
    time_range: TimeRange = field(default_factory=TimeRange.last_week)
    metrics: List[str] = field(default_factory=list)
    dimensions: List[str] = field(default_factory=list)
    filters: Dict[str, Any] = field(default_factory=dict)
    data: List[Dict[str, Any]] = field(default_factory=list)
    comparison: Optional[ComparisonPeriod] = None
    comparison_data: List[Dict[str, Any]] = field(default_factory=list)
    segments: List[Segment] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    def add_data_point(self, data_point: Dict[str, Any]) -> None:
        """Add a data point to the report."""
        self.data.append(data_point)
    
    def add_comparison_data_point(self, data_point: Dict[str, Any]) -> None:
        """Add a comparison data point to the report."""
        self.comparison_data.append(data_point)
    
    def get_total(self, metric_id: str) -> Union[int, float]:
        """Get the total for a metric across all data points."""
        total = 0
        for data_point in self.data:
            if metric_id in data_point:
                total += data_point[metric_id]
        return total
    
    def get_comparison_total(self, metric_id: str) -> Union[int, float]:
        """Get the total for a metric across all comparison data points."""
        total = 0
        for data_point in self.comparison_data:
            if metric_id in data_point:
                total += data_point[metric_id]
        return total
    
    def get_change_percentage(self, metric_id: str) -> Optional[float]:
        """Calculate percentage change for a metric compared to the comparison period."""
        current_total = self.get_total(metric_id)
        comparison_total = self.get_comparison_total(metric_id)
        
        if comparison_total == 0:
            return None
        
        return ((current_total - comparison_total) / comparison_total) * 100


# Common metric definitions
COMMON_METRICS = {
    "impressions": Metric(
        id="impressions",
        name="Impressions",
        description="Number of times an ad was displayed",
        type=MetricType.COUNT,
        aggregation=AggregationType.SUM,
    ),
    "clicks": Metric(
        id="clicks",
        name="Clicks",
        description="Number of clicks on an ad",
        type=MetricType.COUNT,
        aggregation=AggregationType.SUM,
    ),
    "ctr": Metric(
        id="ctr",
        name="Click-Through Rate",
        description="Percentage of impressions that resulted in a click",
        type=MetricType.PERCENTAGE,
        aggregation=AggregationType.WEIGHTED_AVERAGE,
        format_spec="{:.2f}%",
        is_calculated=True,
        depends_on=["clicks", "impressions"],
    ),
    "spend": Metric(
        id="spend",
        name="Spend",
        description="Total amount spent on ads",
        type=MetricType.CURRENCY,
        aggregation=AggregationType.SUM,
        unit="USD",
    ),
    "conversions": Metric(
        id="conversions",
        name="Conversions",
        description="Number of conversions",
        type=MetricType.COUNT,
        aggregation=AggregationType.SUM,
    ),
    "conversion_rate": Metric(
        id="conversion_rate",
        name="Conversion Rate",
        description="Percentage of clicks that resulted in a conversion",
        type=MetricType.PERCENTAGE,
        aggregation=AggregationType.WEIGHTED_AVERAGE,
        format_spec="{:.2f}%",
        is_calculated=True,
        depends_on=["conversions", "clicks"],
    ),
    "cpa": Metric(
        id="cpa",
        name="Cost Per Acquisition",
        description="Average cost per conversion",
        type=MetricType.CURRENCY,
        aggregation=AggregationType.WEIGHTED_AVERAGE,
        unit="USD",
        is_calculated=True,
        depends_on=["spend", "conversions"],
    ),
    "revenue": Metric(
        id="revenue",
        name="Revenue",
        description="Total revenue generated from conversions",
        type=MetricType.CURRENCY,
        aggregation=AggregationType.SUM,
        unit="USD",
    ),
    "roas": Metric(
        id="roas",
        name="Return On Ad Spend",
        description="Revenue divided by ad spend",
        type=MetricType.COMPOSITE,
        aggregation=AggregationType.WEIGHTED_AVERAGE,
        format_spec="{:.2f}x",
        is_calculated=True,
        depends_on=["revenue", "spend"],
    ),
}

# Common dimension definitions
COMMON_DIMENSIONS = {
    "date": Dimension(
        id="date",
        name="Date",
        description="Calendar date",
        cardinality="high",
        is_temporal=True,
    ),
    "channel": Dimension(
        id="channel",
        name="Channel",
        description="Marketing channel (e.g., Search, Display, Social)",
        cardinality="low",
        allowed_values=["search", "display", "social", "email", "video", "affiliate"],
    ),
    "platform": Dimension(
        id="platform",
        name="Platform",
        description="Specific platform within a channel (e.g., Google, Facebook)",
        cardinality="medium",
    ),
    "campaign": Dimension(
        id="campaign",
        name="Campaign",
        description="Campaign name or ID",
        cardinality="medium",
    ),
    "ad_group": Dimension(
        id="ad_group",
        name="Ad Group",
        description="Ad group name or ID",
        cardinality="high",
    ),
    "creative": Dimension(
        id="creative",
        name="Creative",
        description="Creative name or ID",
        cardinality="high",
    ),
    "device": Dimension(
        id="device",
        name="Device",
        description="Device type (e.g., Desktop, Mobile, Tablet)",
        cardinality="low",
        allowed_values=["desktop", "mobile", "tablet"],
    ),
    "country": Dimension(
        id="country",
        name="Country",
        description="Country of the user",
        cardinality="medium",
    ),
    "region": Dimension(
        id="region",
        name="Region",
        description="Region or state within a country",
        cardinality="high",
    ),
    "audience": Dimension(
        id="audience",
        name="Audience",
        description="Target audience segment",
        cardinality="medium",
    ),
}