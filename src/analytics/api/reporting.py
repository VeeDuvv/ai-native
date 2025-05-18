# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file helps show the results of ad campaigns in a way that's easy to understand.
# It's like turning numbers and data into charts and stories that tell how well the ads are doing.

# High School Explanation:
# This module implements the reporting interfaces for the analytics system. It provides
# API endpoints and formatted output methods that transform raw and processed analytics data
# into structured, consumable formats. The module supports various report types, visualization
# options, and export formats to make analytics insights accessible to both humans and other systems.

import json
import csv
import io
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from fastapi import APIRouter, Query, Path, Depends, HTTPException
from pydantic import BaseModel, Field

from ..core.models import Metric, Dimension, PerformanceData, TimeRange, Segment
from ..core.storage import StorageBackend


# Pydantic models for API request/response schemas
class TimeRangeRequest(BaseModel):
    start_date: datetime = Field(..., description="Start date for the time range")
    end_date: datetime = Field(..., description="End date for the time range")
    
    def to_time_range(self) -> TimeRange:
        return TimeRange(self.start_date, self.end_date)


class MetricRequest(BaseModel):
    name: str = Field(..., description="Name of the metric")
    display_name: Optional[str] = Field(None, description="Display name for the metric")


class DimensionRequest(BaseModel):
    name: str = Field(..., description="Name of the dimension")
    display_name: Optional[str] = Field(None, description="Display name for the dimension")


class SegmentRequest(BaseModel):
    name: str = Field(..., description="Name of the segment")
    dimension: str = Field(..., description="Dimension to segment on")
    value: str = Field(..., description="Value to segment by")


class PerformanceDataResponse(BaseModel):
    id: str = Field(..., description="ID of the performance data")
    timestamp: datetime = Field(..., description="Timestamp of the data")
    metrics: Dict[str, float] = Field(..., description="Metrics and their values")
    dimensions: Dict[str, Any] = Field(..., description="Dimensions and their values")
    segments: List[Dict[str, Any]] = Field([], description="Segments applied to the data")


class InsightResponse(BaseModel):
    id: str = Field(..., description="ID of the insight")
    type: str = Field(..., description="Type of insight")
    timestamp: datetime = Field(..., description="Timestamp of the insight")
    title: str = Field(..., description="Title of the insight")
    description: str = Field(..., description="Description of the insight")
    campaign_id: Optional[str] = Field(None, description="Campaign ID if applicable")
    severity: Optional[str] = Field(None, description="Severity level of the insight")
    metrics: Optional[List[Dict[str, Any]]] = Field(None, description="Metrics related to the insight")
    recommendations: Optional[List[Dict[str, Any]]] = Field(None, description="Recommendations based on the insight")


class ReportRequest(BaseModel):
    name: str = Field(..., description="Name of the report")
    description: Optional[str] = Field(None, description="Description of the report")
    time_range: TimeRangeRequest = Field(..., description="Time range for the report")
    metrics: List[MetricRequest] = Field(..., description="Metrics to include in the report")
    dimensions: Optional[List[DimensionRequest]] = Field(None, description="Dimensions to include in the report")
    segments: Optional[List[SegmentRequest]] = Field(None, description="Segments to include in the report")
    filters: Optional[Dict[str, Any]] = Field(None, description="Filters to apply to the report")
    format: str = Field("json", description="Output format (json, csv, html)")


class ReportResponse(BaseModel):
    id: str = Field(..., description="ID of the report")
    name: str = Field(..., description="Name of the report")
    description: Optional[str] = Field(None, description="Description of the report")
    created_at: datetime = Field(..., description="Timestamp when the report was created")
    time_range: Dict[str, datetime] = Field(..., description="Time range for the report")
    metrics: List[Dict[str, str]] = Field(..., description="Metrics included in the report")
    dimensions: Optional[List[Dict[str, str]]] = Field(None, description="Dimensions included in the report")
    segments: Optional[List[Dict[str, Any]]] = Field(None, description="Segments included in the report")
    filters: Optional[Dict[str, Any]] = Field(None, description="Filters applied to the report")
    data: Optional[List[Dict[str, Any]]] = Field(None, description="Report data")
    insights: Optional[List[Dict[str, Any]]] = Field(None, description="Insights related to the report")


class ReportSummaryResponse(BaseModel):
    id: str = Field(..., description="ID of the report")
    name: str = Field(..., description="Name of the report")
    description: Optional[str] = Field(None, description="Description of the report")
    created_at: datetime = Field(..., description="Timestamp when the report was created")
    metrics_count: int = Field(..., description="Number of metrics in the report")
    data_points_count: int = Field(..., description="Number of data points in the report")
    insights_count: int = Field(..., description="Number of insights in the report")


class AnalyticsReportingAPI:
    """
    API for generating and retrieving analytics reports.
    
    This class provides methods for creating, retrieving, and exporting analytics
    reports based on the data stored in the analytics storage backend.
    """
    
    def __init__(self, storage: StorageBackend):
        """Initialize the API with the given storage backend."""
        self.storage = storage
        self.report_cache = {}  # Simple in-memory cache for reports
    
    def create_router(self) -> APIRouter:
        """Create and return a FastAPI router with the API endpoints."""
        router = APIRouter(prefix="/analytics", tags=["analytics"])
        
        # Dependency for getting the storage backend
        def get_storage():
            return self.storage
        
        # Register endpoints
        
        @router.get("/metrics", response_model=List[Dict[str, str]])
        async def list_metrics(storage: StorageBackend = Depends(get_storage)):
            """List all available metrics."""
            # In a real implementation, this would query the storage for available metrics
            # For now, we'll return a static list
            return [
                {"name": "impressions", "display_name": "Impressions"},
                {"name": "clicks", "display_name": "Clicks"},
                {"name": "conversions", "display_name": "Conversions"},
                {"name": "cost", "display_name": "Cost"},
                {"name": "ctr", "display_name": "Click-Through Rate"},
                {"name": "cpc", "display_name": "Cost Per Click"},
                {"name": "cpa", "display_name": "Cost Per Acquisition"},
                {"name": "roas", "display_name": "Return on Ad Spend"}
            ]
        
        @router.get("/dimensions", response_model=List[Dict[str, str]])
        async def list_dimensions(storage: StorageBackend = Depends(get_storage)):
            """List all available dimensions."""
            # In a real implementation, this would query the storage for available dimensions
            # For now, we'll return a static list
            return [
                {"name": "campaign_id", "display_name": "Campaign ID"},
                {"name": "campaign_name", "display_name": "Campaign Name"},
                {"name": "ad_group_id", "display_name": "Ad Group ID"},
                {"name": "ad_group_name", "display_name": "Ad Group Name"},
                {"name": "ad_id", "display_name": "Ad ID"},
                {"name": "ad_name", "display_name": "Ad Name"},
                {"name": "channel", "display_name": "Channel"},
                {"name": "platform", "display_name": "Platform"},
                {"name": "date", "display_name": "Date"},
                {"name": "device", "display_name": "Device"},
                {"name": "audience", "display_name": "Audience"},
                {"name": "creative_type", "display_name": "Creative Type"}
            ]
        
        @router.post("/data", response_model=List[PerformanceDataResponse])
        async def query_data(
            request: Dict[str, Any],
            storage: StorageBackend = Depends(get_storage)
        ):
            """Query performance data based on various criteria."""
            # Parse the time range
            time_range = None
            if "time_range" in request:
                time_range_dict = request["time_range"]
                start_date = datetime.fromisoformat(time_range_dict["start_date"])
                end_date = datetime.fromisoformat(time_range_dict["end_date"])
                time_range = TimeRange(start_date, end_date)
            
            # Parse metrics
            metrics = None
            if "metrics" in request:
                metrics = [Metric(name=m["name"], display_name=m.get("display_name")) 
                         for m in request["metrics"]]
            
            # Parse dimensions
            dimensions = None
            if "dimensions" in request:
                dimensions = [Dimension(name=d["name"], display_name=d.get("display_name")) 
                            for d in request["dimensions"]]
            
            # Parse segments
            segments = None
            if "segments" in request:
                segments = [Segment(name=s["name"], dimension=s["dimension"], value=s["value"]) 
                          for s in request["segments"]]
            
            # Parse filters
            filters = request.get("filters")
            
            # Parse processing stage
            processing_stage = request.get("processing_stage", "ANALYZED")
            
            # Query the storage
            results = storage.query_data(
                time_range=time_range,
                metrics=metrics,
                dimensions=dimensions,
                segments=segments,
                filters=filters,
                processing_stage=processing_stage
            )
            
            # Convert to response format
            response_data = []
            for idx, data in enumerate(results):
                response_data.append({
                    "id": f"data_{idx}",  # In a real implementation, this would be the actual ID
                    "timestamp": datetime.now(),  # In a real implementation, this would be the actual timestamp
                    "metrics": data.metrics,
                    "dimensions": data.dimensions,
                    "segments": [{"name": seg.name, "dimension": seg.dimension, "value": seg.value} 
                               for seg in data.segments]
                })
            
            return response_data
        
        @router.post("/insights", response_model=List[InsightResponse])
        async def query_insights(
            request: Dict[str, Any],
            storage: StorageBackend = Depends(get_storage)
        ):
            """Query insights based on various criteria."""
            # Parse the time range
            time_range = None
            if "time_range" in request:
                time_range_dict = request["time_range"]
                start_date = datetime.fromisoformat(time_range_dict["start_date"])
                end_date = datetime.fromisoformat(time_range_dict["end_date"])
                time_range = TimeRange(start_date, end_date)
            
            # Parse insight types
            insight_types = request.get("insight_types")
            
            # Parse campaigns
            campaigns = request.get("campaigns")
            
            # Parse limit
            limit = request.get("limit", 100)
            
            # Query the storage
            results = storage.query_insights(
                insight_types=insight_types,
                time_range=time_range,
                campaigns=campaigns,
                limit=limit
            )
            
            return results
        
        @router.post("/reports", response_model=ReportResponse)
        async def create_report(
            request: ReportRequest,
            storage: StorageBackend = Depends(get_storage)
        ):
            """Create a new analytics report."""
            # Generate a report ID
            report_id = f"report_{int(datetime.now().timestamp())}"
            
            # Convert request models to core models
            time_range = request.time_range.to_time_range()
            
            metrics = [Metric(name=m.name, display_name=m.display_name) 
                     for m in request.metrics]
            
            dimensions = None
            if request.dimensions:
                dimensions = [Dimension(name=d.name, display_name=d.display_name) 
                            for d in request.dimensions]
            
            segments = None
            if request.segments:
                segments = [Segment(name=s.name, dimension=s.dimension, value=s.value) 
                          for s in request.segments]
            
            # Query the data
            data_results = storage.query_data(
                time_range=time_range,
                metrics=metrics,
                dimensions=dimensions,
                segments=segments,
                filters=request.filters,
                processing_stage="ANALYZED"
            )
            
            # Convert to response format
            data = []
            for performance_data in data_results:
                data_point = {}
                # Include metrics
                for metric_name, metric_value in performance_data.metrics.items():
                    data_point[metric_name] = metric_value
                
                # Include dimensions
                for dim_name, dim_value in performance_data.dimensions.items():
                    data_point[dim_name] = dim_value
                
                # Include segments as dimension values
                for segment in performance_data.segments:
                    data_point[f"segment_{segment.name}"] = True
                
                data.append(data_point)
            
            # Get related insights
            campaign_ids = []
            if data and "campaign_id" in data[0]:
                campaign_ids = list(set(d.get("campaign_id") for d in data if "campaign_id" in d))
            
            insights = []
            if campaign_ids:
                insight_results = storage.query_insights(
                    time_range=time_range,
                    campaigns=campaign_ids,
                    limit=10
                )
                insights = insight_results
            
            # Create the report response
            report = {
                "id": report_id,
                "name": request.name,
                "description": request.description,
                "created_at": datetime.now(),
                "time_range": {
                    "start_date": time_range.start_date,
                    "end_date": time_range.end_date
                },
                "metrics": [{"name": m.name, "display_name": m.display_name or m.name} for m in metrics],
                "dimensions": [{"name": d.name, "display_name": d.display_name or d.name} for d in dimensions] if dimensions else None,
                "segments": [{"name": s.name, "dimension": s.dimension, "value": s.value} for s in segments] if segments else None,
                "filters": request.filters,
                "data": data,
                "insights": insights
            }
            
            # Cache the report
            self.report_cache[report_id] = report
            
            # Return the report
            return report
        
        @router.get("/reports/{report_id}", response_model=ReportResponse)
        async def get_report(
            report_id: str = Path(..., description="ID of the report to retrieve"),
            storage: StorageBackend = Depends(get_storage)
        ):
            """Retrieve an existing report by ID."""
            if report_id not in self.report_cache:
                raise HTTPException(status_code=404, detail=f"Report {report_id} not found")
            
            return self.report_cache[report_id]
        
        @router.get("/reports", response_model=List[ReportSummaryResponse])
        async def list_reports(
            limit: int = Query(10, description="Maximum number of reports to return"),
            storage: StorageBackend = Depends(get_storage)
        ):
            """List all available reports."""
            reports = list(self.report_cache.values())
            reports.sort(key=lambda r: r["created_at"], reverse=True)
            
            # Create summary responses
            report_summaries = []
            for report in reports[:limit]:
                summary = {
                    "id": report["id"],
                    "name": report["name"],
                    "description": report["description"],
                    "created_at": report["created_at"],
                    "metrics_count": len(report["metrics"]),
                    "data_points_count": len(report["data"]) if "data" in report else 0,
                    "insights_count": len(report["insights"]) if "insights" in report else 0
                }
                report_summaries.append(summary)
            
            return report_summaries
        
        @router.get("/reports/{report_id}/export")
        async def export_report(
            report_id: str = Path(..., description="ID of the report to export"),
            format: str = Query("json", description="Export format (json, csv)"),
            storage: StorageBackend = Depends(get_storage)
        ):
            """Export a report in the specified format."""
            if report_id not in self.report_cache:
                raise HTTPException(status_code=404, detail=f"Report {report_id} not found")
            
            report = self.report_cache[report_id]
            
            if format.lower() == "json":
                return report
            
            elif format.lower() == "csv":
                if not report.get("data"):
                    return "No data to export"
                
                # Create a CSV string
                output = io.StringIO()
                writer = csv.writer(output)
                
                # Write header row
                first_row = report["data"][0]
                header = list(first_row.keys())
                writer.writerow(header)
                
                # Write data rows
                for row in report["data"]:
                    writer.writerow([row.get(col, "") for col in header])
                
                return output.getvalue()
            
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")
        
        return router
    
    def generate_dashboard_data(self, campaign_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate data for the dashboard, optionally filtered by campaign ID.
        
        Args:
            campaign_id: Optional campaign ID to filter data for
        
        Returns:
            Dictionary with dashboard data
        """
        # Define the time range for the dashboard (last 30 days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        time_range = TimeRange(start_date, end_date)
        
        # Define filters if campaign ID is provided
        filters = None
        if campaign_id:
            filters = {"dimension.campaign_id": campaign_id}
        
        # Query for performance data
        performance_data = self.storage.query_data(
            time_range=time_range,
            filters=filters,
            processing_stage="ANALYZED"
        )
        
        # Query for insights
        campaigns = [campaign_id] if campaign_id else None
        insights = self.storage.query_insights(
            time_range=time_range,
            campaigns=campaigns,
            limit=10
        )
        
        # Aggregate metrics
        metrics_summary = {}
        metrics_by_day = {}
        metrics_by_channel = {}
        
        for data in performance_data:
            # Update summary metrics
            for metric, value in data.metrics.items():
                if metric not in metrics_summary:
                    metrics_summary[metric] = 0
                metrics_summary[metric] += value
            
            # Update metrics by day
            if "date" in data.dimensions:
                date = data.dimensions["date"]
                if date not in metrics_by_day:
                    metrics_by_day[date] = {}
                
                for metric, value in data.metrics.items():
                    if metric not in metrics_by_day[date]:
                        metrics_by_day[date][metric] = 0
                    metrics_by_day[date][metric] += value
            
            # Update metrics by channel
            if "channel" in data.dimensions:
                channel = data.dimensions["channel"]
                if channel not in metrics_by_channel:
                    metrics_by_channel[channel] = {}
                
                for metric, value in data.metrics.items():
                    if metric not in metrics_by_channel[channel]:
                        metrics_by_channel[channel][metric] = 0
                    metrics_by_channel[channel][metric] += value
        
        # Create time series data
        dates = sorted(metrics_by_day.keys())
        time_series = {
            "dates": dates,
            "metrics": {}
        }
        
        for metric in metrics_summary.keys():
            time_series["metrics"][metric] = [metrics_by_day[date].get(metric, 0) for date in dates]
        
        # Create chart data for channel breakdown
        channels = sorted(metrics_by_channel.keys())
        channel_breakdown = {
            "channels": channels,
            "metrics": {}
        }
        
        for metric in metrics_summary.keys():
            channel_breakdown["metrics"][metric] = [metrics_by_channel[channel].get(metric, 0) for channel in channels]
        
        # Create the dashboard data
        dashboard = {
            "campaign_id": campaign_id,
            "time_range": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "summary": {
                "metrics": metrics_summary,
                "insights_count": len(insights)
            },
            "time_series": time_series,
            "channel_breakdown": channel_breakdown,
            "top_insights": insights[:5],
            "recent_insights": sorted(insights, key=lambda i: i["timestamp"], reverse=True)[:5]
        }
        
        return dashboard


class ReportFormatter:
    """
    Utility class for formatting analytics reports in various output formats.
    
    This class provides methods for transforming report data into different
    formats, such as HTML, PDF, and Markdown, for visualization and export.
    """
    
    @staticmethod
    def to_html(report: Dict[str, Any]) -> str:
        """
        Format a report as HTML.
        
        Args:
            report: Report data
        
        Returns:
            HTML string
        """
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{report['name']}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; }}
                .card {{ border: 1px solid #ddd; border-radius: 4px; padding: 15px; margin-bottom: 20px; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ text-align: left; padding: 8px; }}
                tr:nth-child(even) {{ background-color: #f2f2f2; }}
                th {{ background-color: #4CAF50; color: white; }}
            </style>
        </head>
        <body>
            <h1>{report['name']}</h1>
            <p>{report.get('description', '')}</p>
            
            <div class="card">
                <h2>Report Information</h2>
                <p><strong>Created:</strong> {report['created_at'].strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>Time Range:</strong> {report['time_range']['start_date'].strftime('%Y-%m-%d')} to {report['time_range']['end_date'].strftime('%Y-%m-%d')}</p>
            </div>
            
            <div class="card">
                <h2>Metrics</h2>
                <ul>
        """
        
        for metric in report['metrics']:
            html += f"<li><strong>{metric['display_name']}:</strong> {metric['name']}</li>"
        
        html += "</ul></div>"
        
        if report.get('dimensions'):
            html += """
            <div class="card">
                <h2>Dimensions</h2>
                <ul>
            """
            
            for dimension in report['dimensions']:
                html += f"<li><strong>{dimension['display_name']}:</strong> {dimension['name']}</li>"
            
            html += "</ul></div>"
        
        if report.get('data'):
            html += """
            <div class="card">
                <h2>Data</h2>
                <table>
                    <tr>
            """
            
            # Header row
            headers = list(report['data'][0].keys())
            for header in headers:
                html += f"<th>{header}</th>"
            
            html += "</tr>"
            
            # Data rows
            for row in report['data']:
                html += "<tr>"
                for header in headers:
                    html += f"<td>{row.get(header, '')}</td>"
                html += "</tr>"
            
            html += "</table></div>"
        
        if report.get('insights'):
            html += """
            <div class="card">
                <h2>Insights</h2>
                <ul>
            """
            
            for insight in report['insights']:
                html += f"""
                <li>
                    <strong>{insight['title']}</strong>
                    <p>{insight['description']}</p>
                    {f"<p><em>Severity: {insight.get('severity', 'Medium')}</em></p>" if insight.get('severity') else ""}
                </li>
                """
            
            html += "</ul></div>"
        
        html += """
        </body>
        </html>
        """
        
        return html
    
    @staticmethod
    def to_markdown(report: Dict[str, Any]) -> str:
        """
        Format a report as Markdown.
        
        Args:
            report: Report data
        
        Returns:
            Markdown string
        """
        markdown = f"# {report['name']}\n\n"
        
        if report.get('description'):
            markdown += f"{report['description']}\n\n"
        
        markdown += f"**Created:** {report['created_at'].strftime('%Y-%m-%d %H:%M:%S')}  \n"
        markdown += f"**Time Range:** {report['time_range']['start_date'].strftime('%Y-%m-%d')} to {report['time_range']['end_date'].strftime('%Y-%m-%d')}\n\n"
        
        markdown += "## Metrics\n\n"
        for metric in report['metrics']:
            markdown += f"- **{metric['display_name']}:** {metric['name']}\n"
        
        markdown += "\n"
        
        if report.get('dimensions'):
            markdown += "## Dimensions\n\n"
            for dimension in report['dimensions']:
                markdown += f"- **{dimension['display_name']}:** {dimension['name']}\n"
            markdown += "\n"
        
        if report.get('data'):
            markdown += "## Data\n\n"
            
            # Header row
            headers = list(report['data'][0].keys())
            markdown += "| " + " | ".join(headers) + " |\n"
            markdown += "| " + " | ".join(["---"] * len(headers)) + " |\n"
            
            # Data rows
            for row in report['data']:
                markdown += "| " + " | ".join([str(row.get(header, '')) for header in headers]) + " |\n"
            
            markdown += "\n"
        
        if report.get('insights'):
            markdown += "## Insights\n\n"
            
            for insight in report['insights']:
                markdown += f"### {insight['title']}\n\n"
                markdown += f"{insight['description']}\n\n"
                if insight.get('severity'):
                    markdown += f"*Severity: {insight['severity']}*\n\n"
        
        return markdown
    
    @staticmethod
    def to_csv(report: Dict[str, Any]) -> str:
        """
        Format a report's data as CSV.
        
        Args:
            report: Report data
        
        Returns:
            CSV string
        """
        if not report.get('data'):
            return "No data to export"
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header row
        first_row = report['data'][0]
        header = list(first_row.keys())
        writer.writerow(header)
        
        # Write data rows
        for row in report['data']:
            writer.writerow([row.get(col, "") for col in header])
        
        return output.getvalue()
    
    @staticmethod
    def to_json(report: Dict[str, Any]) -> str:
        """
        Format a report as JSON.
        
        Args:
            report: Report data
        
        Returns:
            JSON string
        """
        # Convert datetime objects to ISO format strings
        def json_serialize(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Type {type(obj)} not serializable")
        
        return json.dumps(report, default=json_serialize, indent=2)