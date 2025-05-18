# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file contains code that gathers information about how well ads are performing.
# It's like a person who counts how many people saw an ad, clicked on it, and bought
# something because of it.

# High School Explanation:
# This module implements collectors for gathering performance data from various
# advertising channels and platforms. It includes base classes for data collection,
# transformation, and synchronization, as well as specific implementations for
# different data sources like ad platforms and analytics services.

import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from .models import (
    AggregationType, Dimension, Metric, MetricType, PerformanceData,
    PerformanceReport, TimeRange, COMMON_METRICS
)

# Set up logging
logger = logging.getLogger(__name__)


class DataSourceType(Enum):
    """Types of data sources for analytics collection."""
    AD_PLATFORM = "ad_platform"          # Google Ads, Facebook Ads, etc.
    WEB_ANALYTICS = "web_analytics"      # Google Analytics, Mixpanel, etc.
    CRM = "crm"                          # Salesforce, HubSpot, etc.
    E_COMMERCE = "e_commerce"            # Shopify, WooCommerce, etc.
    CUSTOM_TRACKING = "custom_tracking"  # Custom tracking pixels or APIs
    DATABASE = "database"                # Direct database connection
    OFFLINE = "offline"                  # Offline conversion data


class CollectionFrequency(Enum):
    """Frequency of data collection."""
    REAL_TIME = "real_time"     # Continuous collection
    HOURLY = "hourly"           # Every hour
    DAILY = "daily"             # Every day
    WEEKLY = "weekly"           # Every week
    MONTHLY = "monthly"         # Every month
    ON_DEMAND = "on_demand"     # Manual trigger


class DataCollector(ABC):
    """Base class for data collectors from various sources."""
    
    def __init__(
        self,
        name: str,
        source_type: DataSourceType,
        frequency: CollectionFrequency,
        metrics: List[str],
        dimensions: List[str],
    ):
        self.name = name
        self.source_type = source_type
        self.frequency = frequency
        self.metrics = metrics
        self.dimensions = dimensions
        self.is_active = False
        self.last_collection_time = None
    
    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to the data source."""
        pass
    
    @abstractmethod
    async def validate_credentials(self) -> bool:
        """Validate that credentials are valid and have necessary permissions."""
        pass
    
    @abstractmethod
    async def collect_data(
        self, 
        time_range: TimeRange,
        metrics: Optional[List[str]] = None,
        dimensions: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[PerformanceData]:
        """Collect data for the specified time range and dimensions."""
        pass
    
    @abstractmethod
    async def collect_latest_data(self) -> List[PerformanceData]:
        """Collect the most recent data available."""
        pass
    
    async def start(self) -> bool:
        """Start the data collector."""
        if self.is_active:
            logger.warning(f"Collector {self.name} is already active")
            return True
        
        try:
            connected = await self.connect()
            if not connected:
                logger.error(f"Failed to connect collector {self.name}")
                return False
            
            valid_credentials = await self.validate_credentials()
            if not valid_credentials:
                logger.error(f"Invalid credentials for collector {self.name}")
                return False
            
            self.is_active = True
            logger.info(f"Started collector {self.name}")
            
            # Start collection loop if real-time or scheduled
            if self.frequency != CollectionFrequency.ON_DEMAND:
                asyncio.create_task(self._collection_loop())
            
            return True
        except Exception as e:
            logger.exception(f"Error starting collector {self.name}: {e}")
            return False
    
    async def stop(self) -> bool:
        """Stop the data collector."""
        if not self.is_active:
            logger.warning(f"Collector {self.name} is not active")
            return True
        
        try:
            self.is_active = False
            logger.info(f"Stopped collector {self.name}")
            return True
        except Exception as e:
            logger.exception(f"Error stopping collector {self.name}: {e}")
            return False
    
    async def _collection_loop(self) -> None:
        """Run the collection loop based on the specified frequency."""
        while self.is_active:
            try:
                await self.collect_latest_data()
                self.last_collection_time = datetime.now()
                
                # Wait based on frequency
                if self.frequency == CollectionFrequency.REAL_TIME:
                    await asyncio.sleep(10)  # Check every 10 seconds
                elif self.frequency == CollectionFrequency.HOURLY:
                    await asyncio.sleep(3600)  # 1 hour
                elif self.frequency == CollectionFrequency.DAILY:
                    await asyncio.sleep(86400)  # 24 hours
                elif self.frequency == CollectionFrequency.WEEKLY:
                    await asyncio.sleep(604800)  # 7 days
                elif self.frequency == CollectionFrequency.MONTHLY:
                    await asyncio.sleep(2592000)  # 30 days
                else:
                    # Invalid frequency, exit loop
                    logger.error(f"Invalid frequency for collector {self.name}")
                    break
            except Exception as e:
                logger.exception(f"Error in collection loop for {self.name}: {e}")
                await asyncio.sleep(60)  # Wait a minute before retrying
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the collector."""
        return {
            "name": self.name,
            "source_type": self.source_type.value,
            "frequency": self.frequency.value,
            "is_active": self.is_active,
            "last_collection_time": self.last_collection_time.isoformat() if self.last_collection_time else None,
            "metrics_count": len(self.metrics),
            "dimensions_count": len(self.dimensions),
        }


class AdPlatformCollector(DataCollector):
    """Base class for collecting data from advertising platforms."""
    
    def __init__(
        self,
        name: str,
        platform: str,
        api_credentials: Dict[str, str],
        account_id: str,
        **kwargs
    ):
        super().__init__(
            name=name,
            source_type=DataSourceType.AD_PLATFORM,
            **kwargs
        )
        self.platform = platform
        self.api_credentials = api_credentials
        self.account_id = account_id
        self.client = None
    
    @abstractmethod
    async def get_campaigns(self) -> List[Dict[str, Any]]:
        """Get a list of campaigns from the ad platform."""
        pass
    
    @abstractmethod
    async def get_ad_groups(self, campaign_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get a list of ad groups from the ad platform."""
        pass
    
    @abstractmethod
    async def get_ads(self, ad_group_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get a list of ads from the ad platform."""
        pass


class GoogleAdsCollector(AdPlatformCollector):
    """Collector for Google Ads data."""
    
    def __init__(
        self,
        name: str,
        api_credentials: Dict[str, str],
        account_id: str,
        frequency: CollectionFrequency = CollectionFrequency.DAILY,
        metrics: Optional[List[str]] = None,
        dimensions: Optional[List[str]] = None,
    ):
        if metrics is None:
            metrics = ["impressions", "clicks", "ctr", "spend", "conversions", "conversion_rate"]
        
        if dimensions is None:
            dimensions = ["date", "campaign", "ad_group", "creative", "device", "region"]
        
        super().__init__(
            name=name,
            platform="google_ads",
            api_credentials=api_credentials,
            account_id=account_id,
            frequency=frequency,
            metrics=metrics,
            dimensions=dimensions,
        )
    
    async def connect(self) -> bool:
        """Connect to the Google Ads API."""
        try:
            # In a real implementation, this would use the Google Ads API client
            # self.client = GoogleAdsClient.load_from_dict(self.api_credentials)
            # For demonstration, we'll simulate a successful connection
            self.client = {"connected": True}
            logger.info(f"Connected to Google Ads for account {self.account_id}")
            return True
        except Exception as e:
            logger.exception(f"Error connecting to Google Ads: {e}")
            return False
    
    async def validate_credentials(self) -> bool:
        """Validate Google Ads credentials."""
        try:
            # In a real implementation, this would make a test API call
            # account_info = self.client.get_account_info(self.account_id)
            # For demonstration, we'll simulate validation
            return self.client is not None and self.client.get("connected", False)
        except Exception as e:
            logger.exception(f"Error validating Google Ads credentials: {e}")
            return False
    
    async def collect_data(
        self, 
        time_range: TimeRange,
        metrics: Optional[List[str]] = None,
        dimensions: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[PerformanceData]:
        """Collect data from Google Ads for the specified parameters."""
        try:
            # In a real implementation, this would construct and execute a GAQL query
            # For demonstration, we'll return synthetic data
            if metrics is None:
                metrics = self.metrics
            
            if dimensions is None:
                dimensions = self.dimensions
            
            # Generate some synthetic data points
            date_range = (time_range.end_date - time_range.start_date).days
            result = []
            
            for i in range(date_range + 1):
                current_date = time_range.start_date + timedelta(days=i)
                
                for campaign_id in range(1, 4):  # Simulate 3 campaigns
                    # Create metrics with some random-like but consistent values
                    impressions = 1000 * (campaign_id + i % 5)
                    clicks = int(impressions * (0.02 + (i % 10) / 1000))
                    spend = clicks * (0.5 + campaign_id * 0.1)
                    conversions = int(clicks * (0.03 + (campaign_id % 3) / 100))
                    
                    # Create a data point
                    metrics_data = {
                        "impressions": impressions,
                        "clicks": clicks,
                        "spend": spend,
                        "conversions": conversions,
                        "ctr": (clicks / impressions) * 100 if impressions > 0 else 0,
                        "conversion_rate": (conversions / clicks) * 100 if clicks > 0 else 0,
                    }
                    
                    dimensions_data = {
                        "date": current_date.strftime("%Y-%m-%d"),
                        "campaign": f"Campaign {campaign_id}",
                        "ad_group": f"Ad Group {campaign_id}-{i % 3 + 1}",
                        "device": ["desktop", "mobile", "tablet"][i % 3],
                        "region": ["US", "UK", "CA", "AU", "DE"][i % 5],
                    }
                    
                    data_point = PerformanceData(
                        metrics=metrics_data,
                        dimensions=dimensions_data,
                        timestamp=current_date,
                        campaign_id=f"campaign-{campaign_id}",
                        ad_group_id=f"ad-group-{campaign_id}-{i % 3 + 1}",
                    )
                    
                    result.append(data_point)
            
            logger.info(f"Collected {len(result)} data points from Google Ads")
            return result
        except Exception as e:
            logger.exception(f"Error collecting data from Google Ads: {e}")
            return []
    
    async def collect_latest_data(self) -> List[PerformanceData]:
        """Collect the most recent day's worth of data."""
        time_range = TimeRange(
            start_date=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1),
            end_date=datetime.now()
        )
        return await self.collect_data(time_range)
    
    async def get_campaigns(self) -> List[Dict[str, Any]]:
        """Get a list of campaigns from Google Ads."""
        # In a real implementation, this would fetch actual campaigns
        # For demonstration, we'll return synthetic data
        return [
            {"id": f"campaign-{i}", "name": f"Campaign {i}"} 
            for i in range(1, 6)
        ]
    
    async def get_ad_groups(self, campaign_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get a list of ad groups from Google Ads."""
        # In a real implementation, this would fetch actual ad groups
        # For demonstration, we'll return synthetic data
        result = []
        
        if campaign_id:
            campaign_num = int(campaign_id.split('-')[1])
            for i in range(1, 4):
                result.append({
                    "id": f"ad-group-{campaign_num}-{i}",
                    "name": f"Ad Group {campaign_num}-{i}",
                    "campaign_id": campaign_id
                })
        else:
            for campaign_num in range(1, 6):
                for i in range(1, 4):
                    result.append({
                        "id": f"ad-group-{campaign_num}-{i}",
                        "name": f"Ad Group {campaign_num}-{i}",
                        "campaign_id": f"campaign-{campaign_num}"
                    })
        
        return result
    
    async def get_ads(self, ad_group_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get a list of ads from Google Ads."""
        # In a real implementation, this would fetch actual ads
        # For demonstration, we'll return synthetic data
        result = []
        
        if ad_group_id:
            ad_group_parts = ad_group_id.split('-')
            campaign_num = int(ad_group_parts[2])
            ad_group_num = int(ad_group_parts[3])
            
            for i in range(1, 4):
                result.append({
                    "id": f"ad-{campaign_num}-{ad_group_num}-{i}",
                    "name": f"Ad {campaign_num}-{ad_group_num}-{i}",
                    "ad_group_id": ad_group_id,
                    "type": ["text", "image", "responsive"][i % 3],
                    "status": ["enabled", "paused", "removed"][i % 3]
                })
        else:
            for campaign_num in range(1, 6):
                for ad_group_num in range(1, 4):
                    for i in range(1, 4):
                        result.append({
                            "id": f"ad-{campaign_num}-{ad_group_num}-{i}",
                            "name": f"Ad {campaign_num}-{ad_group_num}-{i}",
                            "ad_group_id": f"ad-group-{campaign_num}-{ad_group_num}",
                            "type": ["text", "image", "responsive"][i % 3],
                            "status": ["enabled", "paused", "removed"][i % 3]
                        })
        
        return result


class FacebookAdsCollector(AdPlatformCollector):
    """Collector for Facebook Ads data."""
    
    def __init__(
        self,
        name: str,
        api_credentials: Dict[str, str],
        account_id: str,
        frequency: CollectionFrequency = CollectionFrequency.DAILY,
        metrics: Optional[List[str]] = None,
        dimensions: Optional[List[str]] = None,
    ):
        if metrics is None:
            metrics = ["impressions", "clicks", "ctr", "spend", "conversions", "conversion_rate"]
        
        if dimensions is None:
            dimensions = ["date", "campaign", "ad_set", "ad", "device", "region", "platform"]
        
        super().__init__(
            name=name,
            platform="facebook_ads",
            api_credentials=api_credentials,
            account_id=account_id,
            frequency=frequency,
            metrics=metrics,
            dimensions=dimensions,
        )
    
    async def connect(self) -> bool:
        """Connect to the Facebook Ads API."""
        try:
            # In a real implementation, this would use the Facebook Ads API client
            # self.client = FacebookAdsApi.init(access_token=self.api_credentials["access_token"])
            # For demonstration, we'll simulate a successful connection
            self.client = {"connected": True}
            logger.info(f"Connected to Facebook Ads for account {self.account_id}")
            return True
        except Exception as e:
            logger.exception(f"Error connecting to Facebook Ads: {e}")
            return False
    
    async def validate_credentials(self) -> bool:
        """Validate Facebook Ads credentials."""
        try:
            # In a real implementation, this would make a test API call
            # For demonstration, we'll simulate validation
            return self.client is not None and self.client.get("connected", False)
        except Exception as e:
            logger.exception(f"Error validating Facebook Ads credentials: {e}")
            return False
    
    async def collect_data(
        self, 
        time_range: TimeRange,
        metrics: Optional[List[str]] = None,
        dimensions: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[PerformanceData]:
        """Collect data from Facebook Ads for the specified parameters."""
        try:
            # Similar to GoogleAdsCollector, we'll generate synthetic data
            # In a real implementation, this would use the Facebook Ads API
            
            if metrics is None:
                metrics = self.metrics
            
            if dimensions is None:
                dimensions = self.dimensions
            
            # Generate some synthetic data points
            date_range = (time_range.end_date - time_range.start_date).days
            result = []
            
            for i in range(date_range + 1):
                current_date = time_range.start_date + timedelta(days=i)
                
                for campaign_id in range(1, 5):  # Simulate 4 campaigns
                    for platform in ["facebook", "instagram"]:
                        # Create metrics with some random-like but consistent values
                        impressions = 1200 * (campaign_id + i % 4)
                        clicks = int(impressions * (0.025 + (i % 8) / 1000))
                        spend = clicks * (0.6 + campaign_id * 0.1)
                        conversions = int(clicks * (0.035 + (campaign_id % 4) / 100))
                        
                        # Adjust based on platform
                        if platform == "instagram":
                            impressions = int(impressions * 0.8)
                            clicks = int(clicks * 1.2)
                        
                        # Create a data point
                        metrics_data = {
                            "impressions": impressions,
                            "clicks": clicks,
                            "spend": spend,
                            "conversions": conversions,
                            "ctr": (clicks / impressions) * 100 if impressions > 0 else 0,
                            "conversion_rate": (conversions / clicks) * 100 if clicks > 0 else 0,
                        }
                        
                        dimensions_data = {
                            "date": current_date.strftime("%Y-%m-%d"),
                            "campaign": f"FB Campaign {campaign_id}",
                            "ad_set": f"Ad Set {campaign_id}-{i % 3 + 1}",
                            "ad": f"Ad {campaign_id}-{i % 3 + 1}-{i % 2 + 1}",
                            "device": ["desktop", "mobile", "tablet"][i % 3],
                            "region": ["US", "UK", "CA", "AU", "DE", "FR"][i % 6],
                            "platform": platform
                        }
                        
                        data_point = PerformanceData(
                            metrics=metrics_data,
                            dimensions=dimensions_data,
                            timestamp=current_date,
                            campaign_id=f"fb-campaign-{campaign_id}",
                            ad_group_id=f"fb-adset-{campaign_id}-{i % 3 + 1}",
                            creative_id=f"fb-ad-{campaign_id}-{i % 3 + 1}-{i % 2 + 1}",
                            channel_id="facebook_ads"
                        )
                        
                        result.append(data_point)
            
            logger.info(f"Collected {len(result)} data points from Facebook Ads")
            return result
        except Exception as e:
            logger.exception(f"Error collecting data from Facebook Ads: {e}")
            return []
    
    async def collect_latest_data(self) -> List[PerformanceData]:
        """Collect the most recent day's worth of data."""
        time_range = TimeRange(
            start_date=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1),
            end_date=datetime.now()
        )
        return await self.collect_data(time_range)
    
    async def get_campaigns(self) -> List[Dict[str, Any]]:
        """Get a list of campaigns from Facebook Ads."""
        # For demonstration, we'll return synthetic data
        return [
            {"id": f"fb-campaign-{i}", "name": f"FB Campaign {i}"} 
            for i in range(1, 5)
        ]
    
    async def get_ad_groups(self, campaign_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get a list of ad sets from Facebook Ads."""
        # In Facebook Ads, "ad groups" are called "ad sets"
        # For demonstration, we'll return synthetic data
        result = []
        
        if campaign_id:
            campaign_num = int(campaign_id.split('-')[2])
            for i in range(1, 4):
                result.append({
                    "id": f"fb-adset-{campaign_num}-{i}",
                    "name": f"Ad Set {campaign_num}-{i}",
                    "campaign_id": campaign_id
                })
        else:
            for campaign_num in range(1, 5):
                for i in range(1, 4):
                    result.append({
                        "id": f"fb-adset-{campaign_num}-{i}",
                        "name": f"Ad Set {campaign_num}-{i}",
                        "campaign_id": f"fb-campaign-{campaign_num}"
                    })
        
        return result
    
    async def get_ads(self, ad_group_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get a list of ads from Facebook Ads."""
        # For demonstration, we'll return synthetic data
        result = []
        
        if ad_group_id:
            ad_set_parts = ad_group_id.split('-')
            campaign_num = int(ad_set_parts[2])
            ad_set_num = int(ad_set_parts[3])
            
            for i in range(1, 3):
                result.append({
                    "id": f"fb-ad-{campaign_num}-{ad_set_num}-{i}",
                    "name": f"Ad {campaign_num}-{ad_set_num}-{i}",
                    "ad_set_id": ad_group_id,
                    "type": ["image", "video", "carousel"][i % 3],
                    "status": ["ACTIVE", "PAUSED", "ARCHIVED"][i % 3]
                })
        else:
            for campaign_num in range(1, 5):
                for ad_set_num in range(1, 4):
                    for i in range(1, 3):
                        result.append({
                            "id": f"fb-ad-{campaign_num}-{ad_set_num}-{i}",
                            "name": f"Ad {campaign_num}-{ad_set_num}-{i}",
                            "ad_set_id": f"fb-adset-{campaign_num}-{ad_set_num}",
                            "type": ["image", "video", "carousel"][i % 3],
                            "status": ["ACTIVE", "PAUSED", "ARCHIVED"][i % 3]
                        })
        
        return result


class AnalyticsCollectorRegistry:
    """Registry of analytics data collectors."""
    
    def __init__(self):
        self.collectors: Dict[str, DataCollector] = {}
    
    def register_collector(self, collector: DataCollector) -> bool:
        """Register a new collector."""
        if collector.name in self.collectors:
            logger.warning(f"Collector with name {collector.name} already exists")
            return False
        
        self.collectors[collector.name] = collector
        logger.info(f"Registered collector {collector.name}")
        return True
    
    def unregister_collector(self, name: str) -> bool:
        """Unregister a collector."""
        if name not in self.collectors:
            logger.warning(f"Collector with name {name} does not exist")
            return False
        
        del self.collectors[name]
        logger.info(f"Unregistered collector {name}")
        return True
    
    def get_collector(self, name: str) -> Optional[DataCollector]:
        """Get a collector by name."""
        return self.collectors.get(name)
    
    def get_collectors(self) -> List[DataCollector]:
        """Get all registered collectors."""
        return list(self.collectors.values())
    
    def get_active_collectors(self) -> List[DataCollector]:
        """Get all active collectors."""
        return [c for c in self.collectors.values() if c.is_active]
    
    def get_collectors_by_source_type(self, source_type: DataSourceType) -> List[DataCollector]:
        """Get collectors by source type."""
        return [c for c in self.collectors.values() if c.source_type == source_type]
    
    async def start_all_collectors(self) -> Dict[str, bool]:
        """Start all registered collectors."""
        results = {}
        for name, collector in self.collectors.items():
            results[name] = await collector.start()
        return results
    
    async def stop_all_collectors(self) -> Dict[str, bool]:
        """Stop all registered collectors."""
        results = {}
        for name, collector in self.collectors.items():
            results[name] = await collector.stop()
        return results
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of all collectors."""
        return {
            "total_collectors": len(self.collectors),
            "active_collectors": len(self.get_active_collectors()),
            "collectors": {name: collector.get_status() for name, collector in self.collectors.items()}
        }


# Create a singleton instance
collector_registry = AnalyticsCollectorRegistry()