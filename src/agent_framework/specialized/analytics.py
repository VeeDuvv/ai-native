# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file is like a detective for advertisements. It watches how ads are performing,
# collects clues about what people like, and helps make better decisions about
# future ads.

# High School Explanation:
# This module implements an Analytics Agent that monitors campaign performance metrics,
# analyzes data patterns, and generates insights to optimize campaigns. It processes
# both real-time and historical data to produce actionable recommendations for strategy
# and media adjustments.

import logging
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
import threading
import time
import random  # For demo data generation

from ..core.base import BaseProcessAwareAgent
from ..core.message import Message, MessageType
from ..core.process import ProcessActivity, ProcessContext
from ..communication.protocol import StandardCommunicationProtocol, DeliveryStatus

logger = logging.getLogger(__name__)

class PerformanceMetric:
    """Represents a performance metric with value, timestamp, and metadata."""
    
    def __init__(self, 
                 name: str,
                 value: float,
                 unit: str,
                 timestamp: str,
                 source: str,
                 dimensions: Optional[Dict[str, str]] = None):
        self.name = name
        self.value = value
        self.unit = unit
        self.timestamp = timestamp
        self.source = source
        self.dimensions = dimensions or {}
        
    def to_dict(self) -> Dict:
        """Convert metric to dictionary representation."""
        return {
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "timestamp": self.timestamp,
            "source": self.source,
            "dimensions": self.dimensions
        }
        
    @classmethod
    def from_dict(cls, data: Dict) -> 'PerformanceMetric':
        """Create a PerformanceMetric instance from dictionary data."""
        return cls(
            name=data["name"],
            value=data["value"],
            unit=data["unit"],
            timestamp=data["timestamp"],
            source=data["source"],
            dimensions=data.get("dimensions", {})
        )


class PerformanceReport:
    """Represents a comprehensive performance report for a campaign."""
    
    def __init__(self, 
                 campaign_id: str,
                 report_id: str,
                 generated_at: str,
                 time_period: Dict[str, str],
                 metrics: List[PerformanceMetric]):
        self.campaign_id = campaign_id
        self.report_id = report_id
        self.generated_at = generated_at
        self.time_period = time_period
        self.metrics = metrics
        self.insights: List[Dict[str, Any]] = []
        self.recommendations: List[Dict[str, Any]] = []
        
    def add_insight(self, insight_type: str, description: str, importance: str, 
                   metrics: List[str], data: Optional[Dict[str, Any]] = None) -> None:
        """Add an insight to the report."""
        self.insights.append({
            "type": insight_type,
            "description": description,
            "importance": importance,
            "related_metrics": metrics,
            "data": data or {}
        })
        
    def add_recommendation(self, action: str, description: str, priority: str,
                         estimated_impact: str, implementation_details: Optional[Dict[str, Any]] = None) -> None:
        """Add a recommendation to the report."""
        self.recommendations.append({
            "action": action,
            "description": description,
            "priority": priority,
            "estimated_impact": estimated_impact,
            "implementation_details": implementation_details or {}
        })
        
    def to_dict(self) -> Dict:
        """Convert report to dictionary representation."""
        return {
            "campaign_id": self.campaign_id,
            "report_id": self.report_id,
            "generated_at": self.generated_at,
            "time_period": self.time_period,
            "metrics": [metric.to_dict() for metric in self.metrics],
            "insights": self.insights,
            "recommendations": self.recommendations
        }
        
    @classmethod
    def from_dict(cls, data: Dict) -> 'PerformanceReport':
        """Create a PerformanceReport instance from dictionary data."""
        report = cls(
            campaign_id=data["campaign_id"],
            report_id=data["report_id"],
            generated_at=data["generated_at"],
            time_period=data["time_period"],
            metrics=[PerformanceMetric.from_dict(m) for m in data["metrics"]]
        )
        
        for insight in data.get("insights", []):
            report.insights.append(insight)
            
        for recommendation in data.get("recommendations", []):
            report.recommendations.append(recommendation)
            
        return report


class DataSource:
    """Represents a data source for analytics."""
    
    def __init__(self, 
                 source_id: str,
                 name: str,
                 source_type: str,
                 metrics: List[str],
                 refresh_interval: int,  # in seconds
                 connection_params: Optional[Dict[str, Any]] = None):
        self.source_id = source_id
        self.name = name
        self.source_type = source_type
        self.metrics = metrics
        self.refresh_interval = refresh_interval
        self.connection_params = connection_params or {}
        self.last_refresh = None
        
    def to_dict(self) -> Dict:
        """Convert data source to dictionary representation."""
        return {
            "source_id": self.source_id,
            "name": self.name,
            "source_type": self.source_type,
            "metrics": self.metrics,
            "refresh_interval": self.refresh_interval,
            "connection_params": self.connection_params,
            "last_refresh": self.last_refresh
        }


class AnalyticsAgent(BaseProcessAwareAgent):
    """Agent responsible for campaign performance monitoring and optimization."""
    
    def __init__(self, agent_id: str = "analytics_agent", **kwargs):
        super().__init__(agent_id=agent_id, **kwargs)
        self.communication_protocol = StandardCommunicationProtocol()
        self.active_campaigns: Dict[str, Dict[str, Any]] = {}  # campaign_id -> campaign data
        self.reports: Dict[str, PerformanceReport] = {}  # report_id -> report
        self.metrics_store: Dict[str, List[PerformanceMetric]] = {}  # campaign_id -> metrics
        self.data_sources: Dict[str, DataSource] = {}  # source_id -> data source
        
        # Alerting configuration
        self.alerts_config: Dict[str, Dict[str, Any]] = {
            "default": {
                "threshold_multiplier": 1.5,
                "min_consecutive_violations": 3,
                "cooldown_period": 3600  # seconds
            }
        }
        
        # Tracking active alerts
        self.active_alerts: Dict[str, Dict[str, Any]] = {}  # alert_id -> alert data
        
        # Set up background data collection
        self._data_collection_thread = None
        self._stop_collection = threading.Event()
        
        # Initialize default data sources
        self._initialize_default_data_sources()
        
        # Register message handlers
        self.register_message_handler("ANALYTICS_REQUEST", self._handle_analytics_request)
        self.register_message_handler("PERFORMANCE_DATA", self._handle_performance_data)
        self.register_message_handler("ALERT_CONFIG", self._handle_alert_config)
        
        # Subscribe to relevant topics
        self.communication_protocol.subscribe(
            self.agent_id,
            "campaign_performance"
        )
        self.communication_protocol.subscribe(
            self.agent_id,
            "campaign_updates"
        )
        
        # Register process activities
        self.register_activity("generate_performance_report", self._activity_generate_report)
        self.register_activity("analyze_campaign_performance", self._activity_analyze_performance)
        self.register_activity("detect_anomalies", self._activity_detect_anomalies)
        self.register_activity("generate_optimization_recommendations", self._activity_generate_recommendations)
        
    def _initialize_default_data_sources(self) -> None:
        """Initialize default data sources for analytics."""
        # Digital advertising platform data source
        self.data_sources["digital_ads"] = DataSource(
            source_id="digital_ads",
            name="Digital Advertising Platforms",
            source_type="aggregated_api",
            metrics=[
                "impressions", "clicks", "ctr", "conversions", 
                "conversion_rate", "cost", "cpc", "cpm"
            ],
            refresh_interval=3600,  # Hourly
            connection_params={
                "platforms": ["search", "social", "display"]
            }
        )
        
        # Website analytics data source
        self.data_sources["website"] = DataSource(
            source_id="website",
            name="Website Analytics",
            source_type="web_analytics",
            metrics=[
                "sessions", "users", "page_views", "bounce_rate",
                "avg_session_duration", "goal_completions"
            ],
            refresh_interval=3600,  # Hourly
            connection_params={
                "view_id": "web_analytics_view_123"
            }
        )
        
        # Social media engagement data source
        self.data_sources["social_engagement"] = DataSource(
            source_id="social_engagement",
            name="Social Media Engagement",
            source_type="social_api",
            metrics=[
                "likes", "shares", "comments", "follows",
                "engagement_rate", "video_views", "reach"
            ],
            refresh_interval=7200,  # Every 2 hours
            connection_params={
                "platforms": ["facebook", "instagram", "twitter", "linkedin"]
            }
        )
        
        # Email marketing data source
        self.data_sources["email"] = DataSource(
            source_id="email",
            name="Email Marketing",
            source_type="email_api",
            metrics=[
                "sends", "opens", "open_rate", "clicks",
                "click_rate", "unsubscribes", "conversions"
            ],
            refresh_interval=10800,  # Every 3 hours
            connection_params={
                "provider": "email_service_provider"
            }
        )
        
        logger.info(f"Initialized {len(self.data_sources)} default data sources")
    
    def start_background_collection(self, interval: int = 300) -> None:
        """Start background data collection thread.
        
        Args:
            interval: Collection interval in seconds (default: 5 minutes)
        """
        if self._data_collection_thread and self._data_collection_thread.is_alive():
            logger.warning("Background data collection already running")
            return
            
        self._stop_collection.clear()
        self._data_collection_thread = threading.Thread(
            target=self._background_collection_worker,
            args=(interval,),
            daemon=True
        )
        self._data_collection_thread.start()
        logger.info(f"Started background data collection with interval {interval}s")
    
    def stop_background_collection(self) -> None:
        """Stop background data collection thread."""
        if not self._data_collection_thread or not self._data_collection_thread.is_alive():
            logger.warning("No background data collection running")
            return
            
        self._stop_collection.set()
        self._data_collection_thread.join(timeout=5.0)
        logger.info("Stopped background data collection")
    
    def _background_collection_worker(self, interval: int) -> None:
        """Background worker for data collection.
        
        Args:
            interval: Collection interval in seconds
        """
        while not self._stop_collection.is_set():
            try:
                # Check which data sources need refreshing
                now = datetime.now()
                for source_id, source in self.data_sources.items():
                    if (source.last_refresh is None or 
                        (now - datetime.fromisoformat(source.last_refresh)).total_seconds() >= source.refresh_interval):
                        # Refresh data from this source
                        self._collect_data_from_source(source_id)
                        source.last_refresh = now.isoformat()
                
                # Check for any anomalies in the data
                for campaign_id in self.active_campaigns:
                    self._check_for_anomalies(campaign_id)
                
            except Exception as e:
                logger.error(f"Error in background data collection: {str(e)}")
                
            # Sleep until next collection interval
            self._stop_collection.wait(interval)
    
    def _collect_data_from_source(self, source_id: str) -> None:
        """Collect data from a specific data source.
        
        Args:
            source_id: ID of the data source
        """
        if source_id not in self.data_sources:
            logger.warning(f"Unknown data source: {source_id}")
            return
            
        source = self.data_sources[source_id]
        logger.info(f"Collecting data from {source.name}")
        
        # In a real implementation, this would call APIs or databases
        # For this demo, we'll generate synthetic data
        for campaign_id in self.active_campaigns:
            self._generate_synthetic_metrics(campaign_id, source)
    
    def _generate_synthetic_metrics(self, campaign_id: str, source: DataSource) -> None:
        """Generate synthetic metrics for demonstration purposes.
        
        Args:
            campaign_id: Campaign ID
            source: Data source
        """
        if campaign_id not in self.metrics_store:
            self.metrics_store[campaign_id] = []
            
        now = datetime.now()
        
        # Generate a metric for each metric type in this source
        for metric_name in source.metrics:
            # Get base value (either from previous metrics or default)
            previous_metrics = [m for m in self.metrics_store[campaign_id] 
                               if m.name == metric_name and m.source == source.source_id]
            
            if previous_metrics:
                # Use latest value as base with some random variation
                latest = max(previous_metrics, key=lambda m: m.timestamp)
                base_value = latest.value
                # Add some variation (±15%)
                variation = base_value * (0.85 + random.random() * 0.3)
            else:
                # No previous value, generate a reasonable default
                if metric_name in ["impressions", "page_views", "sessions"]:
                    base_value = random.randint(1000, 10000)
                elif metric_name in ["clicks", "conversions", "goal_completions"]:
                    base_value = random.randint(10, 500)
                elif metric_name in ["ctr", "conversion_rate", "bounce_rate"]:
                    base_value = random.uniform(0.01, 0.2)
                elif metric_name in ["cost", "cpc"]:
                    base_value = random.uniform(0.5, 10.0)
                elif metric_name in ["cpm"]:
                    base_value = random.uniform(2.0, 30.0)
                elif metric_name in ["engagement_rate", "open_rate", "click_rate"]:
                    base_value = random.uniform(0.05, 0.4)
                else:
                    base_value = random.uniform(1.0, 100.0)
                    
                variation = base_value
            
            # Determine unit based on metric name
            if metric_name in ["rate", "ratio", "ctr", "conversion_rate", "bounce_rate", "engagement_rate"]:
                unit = "ratio"
            elif metric_name in ["cost", "cpc", "cpm"]:
                unit = "currency"
            elif metric_name in ["duration", "time"]:
                unit = "seconds"
            else:
                unit = "count"
                
            # Generate dimensions based on source type
            dimensions = {}
            if source.source_type == "aggregated_api":
                platforms = source.connection_params.get("platforms", [])
                if platforms:
                    dimensions["platform"] = random.choice(platforms)
                    
            elif source.source_type == "social_api":
                platforms = source.connection_params.get("platforms", [])
                if platforms:
                    dimensions["network"] = random.choice(platforms)
                    
            # Create the metric
            metric = PerformanceMetric(
                name=metric_name,
                value=variation,
                unit=unit,
                timestamp=now.isoformat(),
                source=source.source_id,
                dimensions=dimensions
            )
            
            # Add to metrics store
            self.metrics_store[campaign_id].append(metric)
            
        logger.debug(f"Generated {len(source.metrics)} synthetic metrics for campaign {campaign_id}")
    
    def register_campaign(self, campaign_id: str, details: Dict[str, Any]) -> None:
        """Register a campaign for analytics tracking.
        
        Args:
            campaign_id: Campaign ID
            details: Campaign details
        """
        if campaign_id in self.active_campaigns:
            logger.warning(f"Campaign {campaign_id} already registered for analytics")
            return
            
        # Store campaign details
        self.active_campaigns[campaign_id] = {
            "details": details,
            "registered_at": datetime.now().isoformat(),
            "performance_goals": details.get("performance_goals", {}),
            "last_report_time": None
        }
        
        # Initialize metrics store for this campaign
        self.metrics_store[campaign_id] = []
        
        logger.info(f"Registered campaign {campaign_id} for analytics tracking")
    
    def generate_performance_report(self, campaign_id: str, 
                                   time_period: Optional[Dict[str, str]] = None) -> Optional[str]:
        """Generate a performance report for a campaign.
        
        Args:
            campaign_id: Campaign ID
            time_period: Optional time period (default: last 7 days)
            
        Returns:
            str: Report ID if successful, None otherwise
        """
        if campaign_id not in self.active_campaigns:
            logger.warning(f"Cannot generate report for unknown campaign {campaign_id}")
            return None
            
        # Default to last 7 days if not specified
        if not time_period:
            end_time = datetime.now()
            start_time = end_time - timedelta(days=7)
            time_period = {
                "start": start_time.isoformat(),
                "end": end_time.isoformat()
            }
            
        # Get metrics for this campaign in the specified time period
        filtered_metrics = self._get_metrics_in_period(campaign_id, time_period)
        
        if not filtered_metrics:
            logger.warning(f"No metrics found for campaign {campaign_id} in specified time period")
            return None
            
        # Create the report
        report_id = f"report-{campaign_id}-{str(uuid.uuid4())[:8]}"
        report = PerformanceReport(
            campaign_id=campaign_id,
            report_id=report_id,
            generated_at=datetime.now().isoformat(),
            time_period=time_period,
            metrics=filtered_metrics
        )
        
        # Generate insights
        self._generate_insights(report)
        
        # Generate recommendations
        self._generate_recommendations(report)
        
        # Store the report
        self.reports[report_id] = report
        
        # Update last report time
        self.active_campaigns[campaign_id]["last_report_time"] = datetime.now().isoformat()
        
        logger.info(f"Generated performance report {report_id} for campaign {campaign_id}")
        return report_id
    
    def _get_metrics_in_period(self, campaign_id: str, time_period: Dict[str, str]) -> List[PerformanceMetric]:
        """Get metrics for a campaign within a specific time period.
        
        Args:
            campaign_id: Campaign ID
            time_period: Time period with start and end timestamps
            
        Returns:
            List of performance metrics
        """
        if campaign_id not in self.metrics_store:
            return []
            
        start_time = datetime.fromisoformat(time_period["start"])
        end_time = datetime.fromisoformat(time_period["end"])
        
        return [metric for metric in self.metrics_store[campaign_id]
                if start_time <= datetime.fromisoformat(metric.timestamp) <= end_time]
    
    def _generate_insights(self, report: PerformanceReport) -> None:
        """Generate insights for a performance report.
        
        Args:
            report: Performance report
        """
        # Group metrics by name
        metrics_by_name = {}
        for metric in report.metrics:
            if metric.name not in metrics_by_name:
                metrics_by_name[metric.name] = []
            metrics_by_name[metric.name].append(metric)
            
        # Look for trends in key metrics
        for metric_name in ["impressions", "clicks", "conversions", "cost"]:
            if metric_name in metrics_by_name and len(metrics_by_name[metric_name]) > 1:
                metrics = sorted(metrics_by_name[metric_name], key=lambda m: m.timestamp)
                
                # Calculate trend
                values = [m.value for m in metrics]
                first_value = values[0]
                last_value = values[-1]
                
                if first_value > 0:
                    percent_change = ((last_value - first_value) / first_value) * 100
                    
                    if abs(percent_change) >= 10:
                        trend_direction = "increase" if percent_change > 0 else "decrease"
                        importance = "high" if abs(percent_change) > 25 else "medium"
                        
                        report.add_insight(
                            insight_type="trend",
                            description=f"{metric_name.capitalize()} {trend_direction}d by {abs(percent_change):.1f}% during this period",
                            importance=importance,
                            metrics=[metric_name],
                            data={
                                "percent_change": percent_change,
                                "first_value": first_value,
                                "last_value": last_value,
                                "trend_direction": trend_direction
                            }
                        )
        
        # Look for performance by dimension
        dimension_metrics = []
        for metric in report.metrics:
            if metric.dimensions and "platform" in metric.dimensions:
                dimension_metrics.append(metric)
                
        if dimension_metrics:
            platform_performance = {}
            for metric in dimension_metrics:
                platform = metric.dimensions["platform"]
                if platform not in platform_performance:
                    platform_performance[platform] = {}
                    
                if metric.name not in platform_performance[platform]:
                    platform_performance[platform][metric.name] = []
                    
                platform_performance[platform][metric.name].append(metric.value)
            
            # Find best performing platform for clicks or conversions
            if len(platform_performance) > 1:
                best_platform = None
                best_value = 0
                metric_name = "conversions" if "conversions" in metrics_by_name else "clicks"
                
                for platform, metrics in platform_performance.items():
                    if metric_name in metrics:
                        avg_value = sum(metrics[metric_name]) / len(metrics[metric_name])
                        if avg_value > best_value:
                            best_value = avg_value
                            best_platform = platform
                
                if best_platform:
                    report.add_insight(
                        insight_type="channel_performance",
                        description=f"{best_platform} is the best performing platform for {metric_name}",
                        importance="high",
                        metrics=[metric_name],
                        data={
                            "platform": best_platform,
                            "metric": metric_name,
                            "value": best_value
                        }
                    )
        
        # Add ROI/ROAS insight if we have cost and conversion data
        if "cost" in metrics_by_name and "conversions" in metrics_by_name:
            total_cost = sum(m.value for m in metrics_by_name["cost"])
            total_conversions = sum(m.value for m in metrics_by_name["conversions"])
            
            # Assume a default conversion value of $50 if not provided
            conversion_value = self.active_campaigns[report.campaign_id].get("details", {}).get("conversion_value", 50)
            
            if total_cost > 0 and total_conversions > 0:
                total_revenue = total_conversions * conversion_value
                roi = ((total_revenue - total_cost) / total_cost) * 100
                roas = total_revenue / total_cost
                
                report.add_insight(
                    insight_type="roi",
                    description=f"Campaign ROI is {roi:.1f}% with ROAS of {roas:.2f}",
                    importance="high",
                    metrics=["cost", "conversions"],
                    data={
                        "roi": roi,
                        "roas": roas,
                        "total_cost": total_cost,
                        "total_conversions": total_conversions,
                        "total_revenue": total_revenue
                    }
                )
    
    def _generate_recommendations(self, report: PerformanceReport) -> None:
        """Generate recommendations based on report insights.
        
        Args:
            report: Performance report
        """
        # Add recommendations based on insights
        for insight in report.insights:
            if insight["type"] == "trend":
                metric_name = insight["related_metrics"][0]
                trend_direction = insight["data"]["trend_direction"]
                percent_change = insight["data"]["percent_change"]
                
                if metric_name == "cost" and trend_direction == "increase" and percent_change > 15:
                    report.add_recommendation(
                        action="review_budget_allocation",
                        description="Review budget allocation across channels due to significant cost increase",
                        priority="high",
                        estimated_impact="Potentially reduce costs by 10-15%",
                        implementation_details={
                            "metric": metric_name,
                            "percent_change": percent_change,
                            "suggested_action": "Analyze channel performance and reallocate budget to higher-performing channels"
                        }
                    )
                    
                elif metric_name == "conversions" and trend_direction == "decrease" and percent_change < -15:
                    report.add_recommendation(
                        action="optimize_conversion_path",
                        description="Investigate and optimize conversion path due to declining conversion rate",
                        priority="high",
                        estimated_impact="Potentially increase conversions by 15-20%",
                        implementation_details={
                            "metric": metric_name,
                            "percent_change": percent_change,
                            "suggested_action": "Review landing pages, call-to-action elements, and checkout process"
                        }
                    )
                    
                elif metric_name == "clicks" and trend_direction == "decrease" and percent_change < -10:
                    report.add_recommendation(
                        action="review_creative_assets",
                        description="Review and refresh creative assets to improve engagement",
                        priority="medium",
                        estimated_impact="Potentially increase click-through rate by 5-10%",
                        implementation_details={
                            "metric": metric_name,
                            "percent_change": percent_change,
                            "suggested_action": "Test new ad creatives with stronger calls-to-action"
                        }
                    )
            
            elif insight["type"] == "channel_performance":
                platform = insight["data"]["platform"]
                metric = insight["data"]["metric"]
                
                report.add_recommendation(
                    action="increase_top_platform_budget",
                    description=f"Increase budget allocation to top-performing platform ({platform})",
                    priority="medium",
                    estimated_impact=f"Potentially increase overall {metric} by 10-15%",
                    implementation_details={
                        "platform": platform,
                        "metric": metric,
                        "suggested_action": f"Increase {platform} budget by 15-20% and monitor performance"
                    }
                )
            
            elif insight["type"] == "roi":
                roi = insight["data"]["roi"]
                roas = insight["data"]["roas"]
                
                if roi < 20:  # Low ROI
                    report.add_recommendation(
                        action="improve_campaign_efficiency",
                        description="Focus on improving campaign ROI through targeting and bid optimization",
                        priority="high",
                        estimated_impact="Potentially increase ROI by 15-25%",
                        implementation_details={
                            "current_roi": roi,
                            "current_roas": roas,
                            "suggested_action": "Refine audience targeting and optimize bids based on conversion performance"
                        }
                    )
                elif roi > 100:  # Very high ROI
                    report.add_recommendation(
                        action="scale_campaign",
                        description="Scale campaign to capitalize on strong ROI",
                        priority="high",
                        estimated_impact="Potentially increase conversions by 25-40%",
                        implementation_details={
                            "current_roi": roi,
                            "current_roas": roas,
                            "suggested_action": "Increase budget by 30-50% while maintaining targeting parameters"
                        }
                    )
        
        # Add general recommendations if there aren't enough specific ones
        if len(report.recommendations) < 2:
            # Check if we have click data
            click_metrics = [m for m in report.metrics if m.name == "clicks"]
            if click_metrics:
                report.add_recommendation(
                    action="implement_ab_testing",
                    description="Implement A/B testing for ad creatives to improve performance",
                    priority="medium",
                    estimated_impact="Potentially increase CTR by 10-20%",
                    implementation_details={
                        "suggested_action": "Create 2-3 variants of top ads and run A/B tests"
                    }
                )
                
            # Check if we have conversion data
            conversion_metrics = [m for m in report.metrics if m.name == "conversions"]
            if conversion_metrics:
                report.add_recommendation(
                    action="optimize_landing_pages",
                    description="Optimize landing pages to improve conversion rates",
                    priority="medium",
                    estimated_impact="Potentially increase conversion rate by 10-15%",
                    implementation_details={
                        "suggested_action": "Review top landing pages and optimize page elements, calls-to-action, and forms"
                    }
                )
    
    def _check_for_anomalies(self, campaign_id: str) -> None:
        """Check for anomalies in campaign metrics.
        
        Args:
            campaign_id: Campaign ID
        """
        if campaign_id not in self.metrics_store:
            return
            
        # Get recent metrics (last 24 hours)
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        
        recent_metrics = [m for m in self.metrics_store[campaign_id]
                         if m.timestamp and datetime.fromisoformat(m.timestamp) >= yesterday]
                         
        if not recent_metrics:
            return
            
        # Group by metric name
        metrics_by_name = {}
        for metric in recent_metrics:
            if metric.name not in metrics_by_name:
                metrics_by_name[metric.name] = []
            metrics_by_name[metric.name].append(metric)
            
        # Check key metrics for anomalies
        for metric_name in ["ctr", "conversion_rate", "cost", "bounce_rate"]:
            if metric_name in metrics_by_name and len(metrics_by_name[metric_name]) >= 3:
                # Get historical average (excluding recent data)
                historical = [m for m in self.metrics_store[campaign_id]
                             if m.name == metric_name and 
                             m.timestamp and 
                             datetime.fromisoformat(m.timestamp) < yesterday]
                
                if not historical or len(historical) < 5:
                    continue
                    
                historical_values = [m.value for m in historical]
                historical_avg = sum(historical_values) / len(historical_values)
                
                # Get recent values
                recent_values = [m.value for m in metrics_by_name[metric_name]]
                recent_avg = sum(recent_values) / len(recent_values)
                
                # Check if recent average is significantly different from historical
                threshold = self.alerts_config["default"]["threshold_multiplier"]
                
                # For some metrics, high is bad (cost, bounce_rate)
                # For others, low is bad (ctr, conversion_rate)
                is_negative_metric = metric_name in ["cost", "bounce_rate", "cpc", "cpm"]
                
                if is_negative_metric and recent_avg > (historical_avg * threshold):
                    # Negative metric is too high
                    self._create_alert(
                        campaign_id=campaign_id,
                        alert_type="anomaly",
                        alert_level="warning",
                        metric_name=metric_name,
                        description=f"{metric_name} is {((recent_avg/historical_avg)-1)*100:.1f}% higher than historical average",
                        data={
                            "historical_avg": historical_avg,
                            "recent_avg": recent_avg,
                            "threshold": threshold,
                            "direction": "increase"
                        }
                    )
                elif not is_negative_metric and recent_avg < (historical_avg / threshold):
                    # Positive metric is too low
                    self._create_alert(
                        campaign_id=campaign_id,
                        alert_type="anomaly",
                        alert_level="warning",
                        metric_name=metric_name,
                        description=f"{metric_name} is {((historical_avg/recent_avg)-1)*100:.1f}% lower than historical average",
                        data={
                            "historical_avg": historical_avg,
                            "recent_avg": recent_avg,
                            "threshold": threshold,
                            "direction": "decrease"
                        }
                    )
    
    def _create_alert(self, campaign_id: str, alert_type: str, alert_level: str,
                     metric_name: str, description: str, data: Dict[str, Any]) -> str:
        """Create an alert for a campaign.
        
        Args:
            campaign_id: Campaign ID
            alert_type: Type of alert
            alert_level: Severity level
            metric_name: Related metric name
            description: Alert description
            data: Additional alert data
            
        Returns:
            str: Alert ID
        """
        alert_id = f"alert-{campaign_id}-{str(uuid.uuid4())[:8]}"
        
        # Check for duplicate recent alerts
        recent_alerts = [a for a in self.active_alerts.values()
                        if a["campaign_id"] == campaign_id and
                        a["metric_name"] == metric_name and
                        a["alert_type"] == alert_type and
                        (datetime.now() - datetime.fromisoformat(a["created_at"])).total_seconds() < 
                        self.alerts_config["default"]["cooldown_period"]]
                        
        if recent_alerts:
            # Similar alert exists, don't create a duplicate
            logger.debug(f"Suppressing duplicate alert for {campaign_id} ({metric_name})")
            return recent_alerts[0]["alert_id"]
        
        # Create new alert
        self.active_alerts[alert_id] = {
            "alert_id": alert_id,
            "campaign_id": campaign_id,
            "alert_type": alert_type,
            "alert_level": alert_level,
            "metric_name": metric_name,
            "description": description,
            "data": data,
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        # Send alert notification
        self._send_alert_notification(alert_id)
        
        logger.info(f"Created {alert_level} alert for campaign {campaign_id}: {description}")
        return alert_id
    
    def _send_alert_notification(self, alert_id: str) -> None:
        """Send notification for an alert.
        
        Args:
            alert_id: Alert ID
        """
        if alert_id not in self.active_alerts:
            return
            
        alert = self.active_alerts[alert_id]
        campaign_id = alert["campaign_id"]
        
        # Send message to strategy agent (if configured)
        if campaign_id in self.active_campaigns:
            strategy_agent_id = self.active_campaigns[campaign_id].get("strategy_agent_id")
            
            if strategy_agent_id:
                message = Message(
                    message_type=MessageType.ALERT,
                    sender=self.agent_id,
                    recipient=strategy_agent_id,
                    content={
                        "alert_id": alert_id,
                        "campaign_id": campaign_id,
                        "alert_type": alert["alert_type"],
                        "alert_level": alert["alert_level"],
                        "metric_name": alert["metric_name"],
                        "description": alert["description"],
                        "created_at": alert["created_at"]
                    }
                )
                
                self.communication_protocol.send_message(message)
                logger.info(f"Sent alert notification to strategy agent {strategy_agent_id}")
        
        # Publish to campaign_updates topic
        self.communication_protocol.publish(
            sender=self.agent_id,
            topic="campaign_updates",
            content={
                "event": "performance_alert",
                "alert_id": alert_id,
                "campaign_id": campaign_id,
                "alert_level": alert["alert_level"],
                "description": alert["description"],
                "timestamp": datetime.now().isoformat()
            }
        )
    
    def _handle_analytics_request(self, message: Message) -> None:
        """Handle analytics data request message.
        
        Args:
            message: Incoming message
        """
        logger.info(f"Received analytics request from {message.sender}")
        
        request_type = message.content.get("request_type")
        campaign_id = message.content.get("campaign_id")
        
        if not campaign_id or not request_type:
            self._send_error_response(message, "Missing required fields (campaign_id, request_type)")
            return
            
        if request_type == "register_campaign":
            # Register campaign for tracking
            details = message.content.get("campaign_details", {})
            if not details:
                self._send_error_response(message, "Missing campaign_details")
                return
                
            self.register_campaign(campaign_id, details)
            
            # Send confirmation
            response = Message(
                message_type=MessageType.RESPONSE,
                sender=self.agent_id,
                recipient=message.sender,
                content={
                    "request_type": request_type,
                    "campaign_id": campaign_id,
                    "status": "success",
                    "message": "Campaign registered for analytics tracking"
                }
            )
            
            self.communication_protocol.send_message(response)
            
        elif request_type == "generate_report":
            # Generate a performance report
            time_period = message.content.get("time_period")
            
            if campaign_id not in self.active_campaigns:
                self._send_error_response(message, f"Campaign {campaign_id} not registered for analytics")
                return
                
            report_id = self.generate_performance_report(campaign_id, time_period)
            
            if not report_id:
                self._send_error_response(message, "Failed to generate performance report")
                return
                
            # Send report
            report = self.reports[report_id]
            
            response = Message(
                message_type=MessageType.RESPONSE,
                sender=self.agent_id,
                recipient=message.sender,
                content={
                    "request_type": request_type,
                    "campaign_id": campaign_id,
                    "status": "success",
                    "report_id": report_id,
                    "report_summary": {
                        "generated_at": report.generated_at,
                        "time_period": report.time_period,
                        "metrics_count": len(report.metrics),
                        "insights_count": len(report.insights),
                        "recommendations_count": len(report.recommendations)
                    }
                }
            )
            
            self.communication_protocol.send_message(response)
            
        elif request_type == "get_report":
            # Get an existing report
            report_id = message.content.get("report_id")
            
            if not report_id:
                # Get the latest report for this campaign
                campaign_reports = [r for r in self.reports.values() if r.campaign_id == campaign_id]
                
                if not campaign_reports:
                    self._send_error_response(message, f"No reports found for campaign {campaign_id}")
                    return
                    
                # Sort by generation time and get latest
                report = sorted(campaign_reports, key=lambda r: r.generated_at)[-1]
                report_id = report.report_id
            elif report_id not in self.reports:
                self._send_error_response(message, f"Report {report_id} not found")
                return
            else:
                report = self.reports[report_id]
                
            # Send report
            response = Message(
                message_type=MessageType.RESPONSE,
                sender=self.agent_id,
                recipient=message.sender,
                content={
                    "request_type": request_type,
                    "campaign_id": campaign_id,
                    "status": "success",
                    "report": report.to_dict()
                }
            )
            
            self.communication_protocol.send_message(response)
            
        elif request_type == "get_alerts":
            # Get active alerts for this campaign
            campaign_alerts = [a for a in self.active_alerts.values() 
                              if a["campaign_id"] == campaign_id and a["status"] == "active"]
            
            response = Message(
                message_type=MessageType.RESPONSE,
                sender=self.agent_id,
                recipient=message.sender,
                content={
                    "request_type": request_type,
                    "campaign_id": campaign_id,
                    "status": "success",
                    "alerts_count": len(campaign_alerts),
                    "alerts": campaign_alerts
                }
            )
            
            self.communication_protocol.send_message(response)
            
        else:
            self._send_error_response(message, f"Unknown request type: {request_type}")
    
    def _handle_performance_data(self, message: Message) -> None:
        """Handle performance data message with external metrics.
        
        Args:
            message: Incoming message
        """
        logger.info(f"Received performance data from {message.sender}")
        
        campaign_id = message.content.get("campaign_id")
        metrics_data = message.content.get("metrics", [])
        
        if not campaign_id or not metrics_data:
            self._send_error_response(message, "Missing required fields (campaign_id, metrics)")
            return
            
        # Register campaign if not already registered
        if campaign_id not in self.active_campaigns:
            self.register_campaign(campaign_id, {
                "name": message.content.get("campaign_name", f"Campaign {campaign_id}"),
                "source_agent": message.sender
            })
            
        # Process metrics
        processed_count = 0
        for metric_data in metrics_data:
            try:
                metric = PerformanceMetric.from_dict(metric_data)
                
                # Add to metrics store
                if campaign_id not in self.metrics_store:
                    self.metrics_store[campaign_id] = []
                    
                self.metrics_store[campaign_id].append(metric)
                processed_count += 1
                
            except Exception as e:
                logger.error(f"Error processing metric: {str(e)}")
                
        # Send confirmation
        response = Message(
            message_type=MessageType.RESPONSE,
            sender=self.agent_id,
            recipient=message.sender,
            content={
                "campaign_id": campaign_id,
                "status": "success",
                "metrics_processed": processed_count,
                "total_metrics": len(metrics_data),
                "timestamp": datetime.now().isoformat()
            }
        )
        
        self.communication_protocol.send_message(response)
        
        # Check for anomalies with the new data
        self._check_for_anomalies(campaign_id)
    
    def _handle_alert_config(self, message: Message) -> None:
        """Handle alert configuration message.
        
        Args:
            message: Incoming message
        """
        logger.info(f"Received alert configuration from {message.sender}")
        
        config_type = message.content.get("config_type")
        campaign_id = message.content.get("campaign_id")
        config_data = message.content.get("config", {})
        
        if not config_type or not config_data:
            self._send_error_response(message, "Missing required fields (config_type, config)")
            return
            
        if config_type == "thresholds":
            # Update threshold configuration
            metric_name = message.content.get("metric_name")
            
            if not metric_name:
                # Update default thresholds
                self.alerts_config["default"].update(config_data)
                logger.info("Updated default alert thresholds")
            else:
                # Update metric-specific thresholds
                if metric_name not in self.alerts_config:
                    self.alerts_config[metric_name] = dict(self.alerts_config["default"])
                    
                self.alerts_config[metric_name].update(config_data)
                logger.info(f"Updated alert thresholds for {metric_name}")
                
        elif config_type == "campaign_alerts":
            # Update campaign-specific alert configuration
            if not campaign_id:
                self._send_error_response(message, "Missing campaign_id for campaign_alerts configuration")
                return
                
            if campaign_id not in self.active_campaigns:
                self._send_error_response(message, f"Campaign {campaign_id} not registered for analytics")
                return
                
            # Update campaign alert settings
            self.active_campaigns[campaign_id]["alert_settings"] = config_data
            logger.info(f"Updated alert settings for campaign {campaign_id}")
            
        else:
            self._send_error_response(message, f"Unknown config_type: {config_type}")
            return
            
        # Send confirmation
        response = Message(
            message_type=MessageType.RESPONSE,
            sender=self.agent_id,
            recipient=message.sender,
            content={
                "config_type": config_type,
                "status": "success",
                "message": "Alert configuration updated successfully"
            }
        )
        
        self.communication_protocol.send_message(response)
    
    def _send_error_response(self, original_message: Message, error_text: str) -> None:
        """Send an error response for a message.
        
        Args:
            original_message: Original message
            error_text: Error message
        """
        response = Message(
            message_type=MessageType.ERROR,
            sender=self.agent_id,
            recipient=original_message.sender,
            content={
                "error": error_text,
                "original_message_id": original_message.message_id
            }
        )
        
        self.communication_protocol.send_message(response)
        logger.error(f"Sent error response to {original_message.sender}: {error_text}")
    
    def _activity_generate_report(self, context: ProcessContext) -> Dict[str, Any]:
        """Process activity to generate a performance report.
        
        Args:
            context: Process activity context
            
        Returns:
            Dict: Activity results
        """
        try:
            # Get parameters
            campaign_id = context.get_parameter("campaign_id")
            if not campaign_id:
                raise ValueError("Missing campaign_id parameter")
                
            time_period = context.get_parameter("time_period")
            
            # Generate report
            report_id = self.generate_performance_report(campaign_id, time_period)
            
            if not report_id:
                return {
                    "success": False,
                    "message": f"No data available for campaign {campaign_id}"
                }
                
            # Get report
            report = self.reports[report_id]
            
            return {
                "success": True,
                "report_id": report_id,
                "report": report.to_dict(),
                "insights_count": len(report.insights),
                "recommendations_count": len(report.recommendations)
            }
            
        except Exception as e:
            logger.error(f"Error in generate_report activity: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _activity_analyze_performance(self, context: ProcessContext) -> Dict[str, Any]:
        """Process activity to analyze campaign performance.
        
        Args:
            context: Process activity context
            
        Returns:
            Dict: Activity results
        """
        try:
            # Get parameters
            campaign_id = context.get_parameter("campaign_id")
            if not campaign_id:
                raise ValueError("Missing campaign_id parameter")
                
            metrics_of_interest = context.get_parameter("metrics", [])
            time_period = context.get_parameter("time_period")
            
            # Get metrics for this campaign
            filtered_metrics = self._get_metrics_in_period(campaign_id, time_period) if time_period else []
            
            if not filtered_metrics:
                filtered_metrics = self.metrics_store.get(campaign_id, [])
                
            if not filtered_metrics:
                return {
                    "success": False,
                    "message": f"No metrics available for campaign {campaign_id}"
                }
                
            # Filter by metrics of interest if specified
            if metrics_of_interest:
                filtered_metrics = [m for m in filtered_metrics if m.name in metrics_of_interest]
                
            # Group metrics by name
            metrics_by_name = {}
            for metric in filtered_metrics:
                if metric.name not in metrics_by_name:
                    metrics_by_name[metric.name] = []
                metrics_by_name[metric.name].append(metric)
                
            # Calculate aggregate statistics for each metric
            performance_summary = {}
            for name, metrics in metrics_by_name.items():
                values = [m.value for m in metrics]
                
                if not values:
                    continue
                    
                performance_summary[name] = {
                    "count": len(values),
                    "min": min(values),
                    "max": max(values),
                    "avg": sum(values) / len(values),
                    "latest": sorted(metrics, key=lambda m: m.timestamp)[-1].value
                }
                
                # Calculate trend if we have enough data points
                if len(values) >= 3:
                    first_value = sorted(metrics, key=lambda m: m.timestamp)[0].value
                    last_value = sorted(metrics, key=lambda m: m.timestamp)[-1].value
                    
                    if first_value > 0:
                        percent_change = ((last_value - first_value) / first_value) * 100
                        performance_summary[name]["trend"] = {
                            "direction": "up" if percent_change > 0 else "down",
                            "percent_change": percent_change
                        }
            
            return {
                "success": True,
                "campaign_id": campaign_id,
                "metrics_analyzed": len(metrics_by_name),
                "performance_summary": performance_summary
            }
            
        except Exception as e:
            logger.error(f"Error in analyze_performance activity: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _activity_detect_anomalies(self, context: ProcessContext) -> Dict[str, Any]:
        """Process activity to detect anomalies in campaign metrics.
        
        Args:
            context: Process activity context
            
        Returns:
            Dict: Activity results
        """
        try:
            # Get parameters
            campaign_id = context.get_parameter("campaign_id")
            if not campaign_id:
                raise ValueError("Missing campaign_id parameter")
                
            sensitivity = context.get_parameter("sensitivity", "medium")
            
            # Map sensitivity to threshold multiplier
            threshold_multipliers = {
                "low": 2.0,      # Only detect large anomalies
                "medium": 1.5,   # Default
                "high": 1.25     # Detect smaller anomalies
            }
            
            # Use configured threshold or default
            threshold = threshold_multipliers.get(sensitivity, 1.5)
            
            # Temporarily override default threshold
            original_threshold = self.alerts_config["default"]["threshold_multiplier"]
            self.alerts_config["default"]["threshold_multiplier"] = threshold
            
            # Check for anomalies
            self._check_for_anomalies(campaign_id)
            
            # Restore original threshold
            self.alerts_config["default"]["threshold_multiplier"] = original_threshold
            
            # Get active alerts for this campaign
            campaign_alerts = [a for a in self.active_alerts.values() 
                              if a["campaign_id"] == campaign_id and a["status"] == "active"]
            
            return {
                "success": True,
                "campaign_id": campaign_id,
                "anomalies_detected": len(campaign_alerts),
                "sensitivity": sensitivity,
                "threshold": threshold,
                "alerts": campaign_alerts
            }
            
        except Exception as e:
            logger.error(f"Error in detect_anomalies activity: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _activity_generate_recommendations(self, context: ProcessContext) -> Dict[str, Any]:
        """Process activity to generate optimization recommendations.
        
        Args:
            context: Process activity context
            
        Returns:
            Dict: Activity results
        """
        try:
            # Get parameters
            campaign_id = context.get_parameter("campaign_id")
            if not campaign_id:
                raise ValueError("Missing campaign_id parameter")
                
            focus_areas = context.get_parameter("focus_areas", [])
            
            # Generate a report first to get insights
            report_id = self.generate_performance_report(campaign_id)
            
            if not report_id:
                return {
                    "success": False,
                    "message": f"No data available for campaign {campaign_id}"
                }
                
            # Get report
            report = self.reports[report_id]
            
            # Filter recommendations by focus areas if specified
            recommendations = report.recommendations
            if focus_areas:
                # Map focus areas to recommendation actions
                focus_map = {
                    "budget": ["review_budget_allocation", "increase_top_platform_budget"],
                    "creative": ["review_creative_assets", "implement_ab_testing"],
                    "targeting": ["refine_audience_targeting", "optimize_targeting"],
                    "conversion": ["optimize_landing_pages", "optimize_conversion_path"],
                    "scaling": ["scale_campaign", "increase_budget"]
                }
                
                # Flatten the list of relevant actions
                relevant_actions = []
                for area in focus_areas:
                    if area in focus_map:
                        relevant_actions.extend(focus_map[area])
                        
                # Filter recommendations
                if relevant_actions:
                    recommendations = [r for r in recommendations if r["action"] in relevant_actions]
            
            return {
                "success": True,
                "campaign_id": campaign_id,
                "recommendations_count": len(recommendations),
                "recommendations": recommendations,
                "report_id": report_id
            }
            
        except Exception as e:
            logger.error(f"Error in generate_recommendations activity: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }


# Create example function to demonstrate the agent
def run_analytics_example():
    """Run an example of the analytics agent functionality."""
    # Create analytics agent
    analytics_agent = AnalyticsAgent("analytics-demo-agent")
    
    # Start background data collection
    analytics_agent.start_background_collection()
    
    # Register a test campaign
    campaign_id = f"test-campaign-{str(uuid.uuid4())[:8]}"
    
    analytics_agent.register_campaign(campaign_id, {
        "name": "Test Campaign",
        "objectives": ["Increase brand awareness", "Drive website traffic"],
        "start_date": (datetime.now() - timedelta(days=14)).isoformat(),
        "end_date": (datetime.now() + timedelta(days=16)).isoformat(),
        "budget": 50000,
        "target_audience": {
            "age_range": "25-45",
            "interests": ["technology", "digital marketing"]
        },
        "performance_goals": {
            "impressions": 1000000,
            "clicks": 20000,
            "conversions": 2000,
            "ctr": 0.02,
            "conversion_rate": 0.10
        }
    })
    
    # Generate some synthetic data
    for source_id in analytics_agent.data_sources:
        analytics_agent._collect_data_from_source(source_id)
    
    # Wait for data collection
    time.sleep(2)
    
    # Generate a report
    report_id = analytics_agent.generate_performance_report(campaign_id)
    
    if report_id:
        report = analytics_agent.reports[report_id]
        
        print(f"Generated report {report_id} with {len(report.metrics)} metrics")
        print(f"Insights: {len(report.insights)}")
        print(f"Recommendations: {len(report.recommendations)}")
        
        # Print top insights
        for i, insight in enumerate(report.insights[:2]):
            print(f"Insight {i+1}: {insight['description']} ({insight['importance']})")
        
        # Print top recommendations
        for i, recommendation in enumerate(report.recommendations[:2]):
            print(f"Recommendation {i+1}: {recommendation['description']} ({recommendation['priority']})")
    
    # Run an anomaly detection
    analytics_agent._check_for_anomalies(campaign_id)
    
    # Get active alerts
    alerts = [a for a in analytics_agent.active_alerts.values() 
             if a["campaign_id"] == campaign_id and a["status"] == "active"]
    
    print(f"Active alerts: {len(alerts)}")
    for i, alert in enumerate(alerts[:2]):
        print(f"Alert {i+1}: {alert['description']} ({alert['alert_level']})")
    
    # Stop background collection
    analytics_agent.stop_background_collection()
    
    return {
        "analytics_agent": analytics_agent,
        "campaign_id": campaign_id,
        "report_id": report_id,
        "alerts": alerts
    }

if __name__ == "__main__":
    run_analytics_example()