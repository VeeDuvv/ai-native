"""
Implementations of metrics reporting systems.

This module provides concrete implementations of the metrics reporting
interfaces for generating reports and visualizations.
"""

import csv
import json
import logging
from io import StringIO, BytesIO
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
import time

from .interfaces import MetricsReporter, MetricsStorage, MetricValue


class BasicMetricsReporter(MetricsReporter):
    """
    Basic implementation of a metrics reporter.
    
    This implementation generates simple reports and exports from
    the metrics storage.
    """
    
    def __init__(self, storage: MetricsStorage):
        """
        Initialize the metrics reporter.
        
        Args:
            storage: The metrics storage to use
        """
        self.storage = storage
        self.logger = logging.getLogger("metrics.reporter")
    
    def generate_report(self, metrics: List[str], start_time: datetime,
                      end_time: datetime, tags: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Generate a report for specified metrics."""
        report = {
            "generated_at": datetime.now().isoformat(),
            "time_range": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "duration_seconds": (end_time - start_time).total_seconds()
            },
            "metrics": {},
            "tags": tags or {}
        }
        
        for metric_name in metrics:
            summary = self.storage.get_metrics_summary(
                metric_name, start_time, end_time, tags
            )
            
            report["metrics"][metric_name] = summary
        
        self.logger.info(f"Generated report for {len(metrics)} metrics from {start_time} to {end_time}")
        return report
    
    def export_metrics(self, metrics: List[str], start_time: datetime,
                     end_time: datetime, format: str,
                     tags: Optional[Dict[str, str]] = None) -> bytes:
        """Export metrics in a specified format."""
        if format.lower() == "json":
            return self._export_json(metrics, start_time, end_time, tags)
        elif format.lower() == "csv":
            return self._export_csv(metrics, start_time, end_time, tags)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _export_json(self, metrics: List[str], start_time: datetime,
                   end_time: datetime, tags: Optional[Dict[str, str]] = None) -> bytes:
        """Export metrics in JSON format."""
        data = {
            "metadata": {
                "exported_at": datetime.now().isoformat(),
                "time_range": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat()
                },
                "tags": tags or {}
            },
            "metrics": {}
        }
        
        for metric_name in metrics:
            metric_values = self.storage.get_metrics(
                metric_name, start_time, end_time, tags
            )
            
            data["metrics"][metric_name] = [value.as_dict() for value in metric_values]
        
        return json.dumps(data, indent=2).encode('utf-8')
    
    def _export_csv(self, metrics: List[str], start_time: datetime,
                  end_time: datetime, tags: Optional[Dict[str, str]] = None) -> bytes:
        """Export metrics in CSV format."""
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        header = ["metric_name", "timestamp", "value"]
        
        # Add tag columns if tags are specified
        tag_keys = []
        if tags:
            tag_keys = list(tags.keys())
            header.extend(tag_keys)
        
        writer.writerow(header)
        
        # Write metric values
        for metric_name in metrics:
            metric_values = self.storage.get_metrics(
                metric_name, start_time, end_time, tags
            )
            
            for value in metric_values:
                row = [
                    metric_name,
                    value.timestamp.isoformat(),
                    value.value
                ]
                
                # Add tag values if tags are specified
                if tags:
                    for key in tag_keys:
                        if hasattr(value, 'tags') and key in value.tags:
                            row.append(value.tags[key])
                        else:
                            row.append("")
                
                writer.writerow(row)
        
        return output.getvalue().encode('utf-8')


class CampaignPerformanceReporter(BasicMetricsReporter):
    """
    Reporter specialized for campaign performance metrics.
    
    This reporter provides campaign-specific reports and analyses.
    """
    
    def generate_campaign_report(self, campaign_id: str, start_time: datetime,
                               end_time: datetime) -> Dict[str, Any]:
        """
        Generate a performance report for a specific campaign.
        
        Args:
            campaign_id: The ID of the campaign
            start_time: The start of the time range
            end_time: The end of the time range
            
        Returns:
            A dictionary with the campaign report data
        """
        # Define the metrics to include in the report
        metrics = [
            f"campaign_impressions",
            f"campaign_clicks",
            f"campaign_conversions",
            f"campaign_spend",
            f"campaign_revenue"
        ]
        
        # Generate the report using the core reporter
        report = self.generate_report(
            metrics, start_time, end_time, {"campaign_id": campaign_id}
        )
        
        # Calculate derived metrics
        metrics_data = report["metrics"]
        
        impressions = metrics_data.get(f"campaign_impressions", {}).get("last", 0) or 0
        clicks = metrics_data.get(f"campaign_clicks", {}).get("last", 0) or 0
        conversions = metrics_data.get(f"campaign_conversions", {}).get("last", 0) or 0
        spend = metrics_data.get(f"campaign_spend", {}).get("last", 0) or 0
        revenue = metrics_data.get(f"campaign_revenue", {}).get("last", 0) or 0
        
        # Calculate performance metrics
        performance = {
            "ctr": clicks / impressions if impressions > 0 else 0,
            "cvr": conversions / clicks if clicks > 0 else 0,
            "cpa": spend / conversions if conversions > 0 else 0,
            "roas": revenue / spend if spend > 0 else 0
        }
        
        # Add performance metrics to the report
        report["performance"] = performance
        
        # Add campaign metadata
        report["campaign_id"] = campaign_id
        
        return report
    
    def generate_multi_campaign_report(self, campaign_ids: List[str],
                                    start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """
        Generate a comparative report for multiple campaigns.
        
        Args:
            campaign_ids: The IDs of the campaigns to compare
            start_time: The start of the time range
            end_time: The end of the time range
            
        Returns:
            A dictionary with the comparative report data
        """
        report = {
            "generated_at": datetime.now().isoformat(),
            "time_range": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "duration_seconds": (end_time - start_time).total_seconds()
            },
            "campaigns": {}
        }
        
        # Generate individual campaign reports
        for campaign_id in campaign_ids:
            campaign_report = self.generate_campaign_report(
                campaign_id, start_time, end_time
            )
            
            report["campaigns"][campaign_id] = campaign_report
        
        # Calculate comparative metrics
        if len(campaign_ids) > 1:
            comparative = {
                "impressions": {},
                "clicks": {},
                "conversions": {},
                "spend": {},
                "revenue": {},
                "ctr": {},
                "cvr": {},
                "cpa": {},
                "roas": {}
            }
            
            for metric in comparative:
                best_campaign = None
                best_value = 0 if metric not in ["cpa"] else float("inf")
                
                for campaign_id, campaign_data in report["campaigns"].items():
                    if metric in ["ctr", "cvr", "cpa", "roas"]:
                        value = campaign_data["performance"][metric]
                    else:
                        value = campaign_data["metrics"][f"campaign_{metric}"]["last"] or 0
                    
                    # For cost metrics, lower is better
                    if metric in ["cpa"]:
                        if value < best_value and value > 0:
                            best_value = value
                            best_campaign = campaign_id
                    else:
                        if value > best_value:
                            best_value = value
                            best_campaign = campaign_id
                
                comparative[metric] = {
                    "best_campaign": best_campaign,
                    "best_value": best_value
                }
            
            report["comparative"] = comparative
        
        return report
    
    def export_campaign_timeseries(self, campaign_id: str, metrics: List[str],
                                start_time: datetime, end_time: datetime,
                                interval: str = "day") -> bytes:
        """
        Export a time series of campaign metrics.
        
        Args:
            campaign_id: The ID of the campaign
            metrics: The metrics to include
            start_time: The start of the time range
            end_time: The end of the time range
            interval: The time interval for aggregation (hour, day, week, month)
            
        Returns:
            The exported time series data as JSON bytes
        """
        # Map interval to timedelta
        interval_map = {
            "hour": timedelta(hours=1),
            "day": timedelta(days=1),
            "week": timedelta(weeks=1),
            "month": timedelta(days=30)  # Approximate
        }
        
        if interval not in interval_map:
            raise ValueError(f"Invalid interval: {interval}")
        
        delta = interval_map[interval]
        
        # Create time slots
        time_slots = []
        current = start_time
        
        while current <= end_time:
            time_slots.append((current, current + delta))
            current += delta
        
        # Collect data for each time slot
        timeseries = {
            "campaign_id": campaign_id,
            "interval": interval,
            "metrics": metrics,
            "data": []
        }
        
        for start, end in time_slots:
            slot_data = {
                "start_time": start.isoformat(),
                "end_time": end.isoformat(),
                "metrics": {}
            }
            
            for metric in metrics:
                full_metric = f"campaign_{metric}"
                summary = self.storage.get_metrics_summary(
                    full_metric, start, end, {"campaign_id": campaign_id}
                )
                
                if summary["count"] > 0:
                    slot_data["metrics"][metric] = summary["last"]
                else:
                    slot_data["metrics"][metric] = 0
            
            timeseries["data"].append(slot_data)
        
        return json.dumps(timeseries, indent=2).encode('utf-8')