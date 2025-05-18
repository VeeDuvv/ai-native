# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file helps the computer remember all the information about how well ads are doing.
# It's like a special notebook that stores and finds important numbers about ads.

# High School Explanation:
# This module implements a flexible data storage system for analytics data. It provides
# interfaces for persisting raw performance data, processed metrics, and insights,
# with implementations for different storage backends (in-memory, file-based, and database).
# The module handles data serialization, querying, and lifecycle management.

import os
import json
import sqlite3
import pickle
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Tuple
from pathlib import Path

from .models import Metric, Dimension, PerformanceData, Segment, TimeRange


class StorageBackend(ABC):
    """Abstract base class for analytics data storage backends."""
    
    @abstractmethod
    def store_raw_data(self, source: str, data: Dict[str, Any], timestamp: Optional[datetime] = None) -> str:
        """Store raw data collected from a source. Returns a unique identifier for the stored data."""
        pass
    
    @abstractmethod
    def store_processed_data(self, data_id: str, data: PerformanceData, processing_stage: str) -> str:
        """Store processed performance data. Returns a unique identifier for the stored processed data."""
        pass
    
    @abstractmethod
    def store_insight(self, data_ids: List[str], insight_type: str, insight_data: Dict[str, Any]) -> str:
        """Store an insight generated from processed data. Returns a unique identifier for the stored insight."""
        pass
    
    @abstractmethod
    def retrieve_raw_data(self, data_id: str) -> Dict[str, Any]:
        """Retrieve raw data by its identifier."""
        pass
    
    @abstractmethod
    def retrieve_processed_data(self, data_id: str) -> PerformanceData:
        """Retrieve processed data by its identifier."""
        pass
    
    @abstractmethod
    def retrieve_insight(self, insight_id: str) -> Dict[str, Any]:
        """Retrieve an insight by its identifier."""
        pass
    
    @abstractmethod
    def query_data(self, 
                   time_range: Optional[TimeRange] = None,
                   metrics: Optional[List[Metric]] = None,
                   dimensions: Optional[List[Dimension]] = None,
                   segments: Optional[List[Segment]] = None,
                   filters: Optional[Dict[str, Any]] = None,
                   processing_stage: Optional[str] = None) -> List[PerformanceData]:
        """Query processed data based on various criteria."""
        pass
    
    @abstractmethod
    def query_insights(self,
                      insight_types: Optional[List[str]] = None,
                      time_range: Optional[TimeRange] = None,
                      campaigns: Optional[List[str]] = None,
                      limit: int = 100) -> List[Dict[str, Any]]:
        """Query insights based on various criteria."""
        pass
    
    @abstractmethod
    def purge_old_data(self, older_than: datetime) -> int:
        """Remove data older than the specified datetime. Returns the number of records removed."""
        pass


class InMemoryStorage(StorageBackend):
    """In-memory implementation of the analytics storage backend. Useful for testing and development."""
    
    def __init__(self):
        self.raw_data = {}
        self.processed_data = {}
        self.insights = {}
        self.raw_counter = 0
        self.processed_counter = 0
        self.insight_counter = 0
    
    def store_raw_data(self, source: str, data: Dict[str, Any], timestamp: Optional[datetime] = None) -> str:
        timestamp = timestamp or datetime.now()
        data_id = f"raw_{self.raw_counter}"
        self.raw_counter += 1
        
        self.raw_data[data_id] = {
            "source": source,
            "data": data,
            "timestamp": timestamp
        }
        return data_id
    
    def store_processed_data(self, data_id: str, data: PerformanceData, processing_stage: str) -> str:
        processed_id = f"processed_{self.processed_counter}"
        self.processed_counter += 1
        
        self.processed_data[processed_id] = {
            "source_id": data_id,
            "data": data,
            "processing_stage": processing_stage,
            "timestamp": datetime.now()
        }
        return processed_id
    
    def store_insight(self, data_ids: List[str], insight_type: str, insight_data: Dict[str, Any]) -> str:
        insight_id = f"insight_{self.insight_counter}"
        self.insight_counter += 1
        
        self.insights[insight_id] = {
            "data_ids": data_ids,
            "insight_type": insight_type,
            "insight_data": insight_data,
            "timestamp": datetime.now()
        }
        return insight_id
    
    def retrieve_raw_data(self, data_id: str) -> Dict[str, Any]:
        if data_id not in self.raw_data:
            raise KeyError(f"Raw data with id {data_id} not found")
        return self.raw_data[data_id]["data"]
    
    def retrieve_processed_data(self, data_id: str) -> PerformanceData:
        if data_id not in self.processed_data:
            raise KeyError(f"Processed data with id {data_id} not found")
        return self.processed_data[data_id]["data"]
    
    def retrieve_insight(self, insight_id: str) -> Dict[str, Any]:
        if insight_id not in self.insights:
            raise KeyError(f"Insight with id {insight_id} not found")
        return self.insights[insight_id]["insight_data"]
    
    def query_data(self, 
                  time_range: Optional[TimeRange] = None,
                  metrics: Optional[List[Metric]] = None,
                  dimensions: Optional[List[Dimension]] = None,
                  segments: Optional[List[Segment]] = None,
                  filters: Optional[Dict[str, Any]] = None,
                  processing_stage: Optional[str] = None) -> List[PerformanceData]:
        results = []
        
        for data_id, entry in self.processed_data.items():
            if processing_stage and entry["processing_stage"] != processing_stage:
                continue
                
            data = entry["data"]
            timestamp = entry["timestamp"]
            
            # Apply time range filter if specified
            if time_range and not time_range.contains(timestamp):
                continue
                
            # Check if data has all required metrics
            if metrics and not all(metric in data.metrics for metric in metrics):
                continue
                
            # Check if data has all required dimensions
            if dimensions and not all(dim in data.dimensions for dim in dimensions):
                continue
                
            # Check if data has all required segments
            if segments and not all(seg in data.segments for seg in segments):
                continue
                
            # Apply custom filters if specified
            if filters:
                skip = False
                for key, value in filters.items():
                    if key.startswith("dimension."):
                        dim_name = key[10:]
                        if dim_name not in data.dimensions or data.dimensions[dim_name] != value:
                            skip = True
                            break
                    elif key.startswith("metric."):
                        metric_name = key[7:]
                        if metric_name not in data.metrics or data.metrics[metric_name] != value:
                            skip = True
                            break
                if skip:
                    continue
                    
            results.append(data)
            
        return results
    
    def query_insights(self,
                      insight_types: Optional[List[str]] = None,
                      time_range: Optional[TimeRange] = None,
                      campaigns: Optional[List[str]] = None,
                      limit: int = 100) -> List[Dict[str, Any]]:
        results = []
        
        for insight_id, entry in self.insights.items():
            # Apply type filter if specified
            if insight_types and entry["insight_type"] not in insight_types:
                continue
                
            # Apply time range filter if specified
            if time_range and not time_range.contains(entry["timestamp"]):
                continue
                
            # Apply campaign filter if specified
            if campaigns:
                campaign_id = entry["insight_data"].get("campaign_id")
                if not campaign_id or campaign_id not in campaigns:
                    continue
                    
            # Add to results
            insight_with_metadata = {
                "id": insight_id,
                "type": entry["insight_type"],
                "timestamp": entry["timestamp"],
                **entry["insight_data"]
            }
            results.append(insight_with_metadata)
            
            # Respect the limit
            if len(results) >= limit:
                break
                
        # Sort by timestamp (newest first)
        results.sort(key=lambda x: x["timestamp"], reverse=True)
        return results
    
    def purge_old_data(self, older_than: datetime) -> int:
        count = 0
        
        # Purge raw data
        to_remove = []
        for data_id, entry in self.raw_data.items():
            if entry["timestamp"] < older_than:
                to_remove.append(data_id)
                count += 1
        
        for data_id in to_remove:
            del self.raw_data[data_id]
            
        # Purge processed data
        to_remove = []
        for data_id, entry in self.processed_data.items():
            if entry["timestamp"] < older_than:
                to_remove.append(data_id)
                count += 1
        
        for data_id in to_remove:
            del self.processed_data[data_id]
            
        # Purge insights
        to_remove = []
        for insight_id, entry in self.insights.items():
            if entry["timestamp"] < older_than:
                to_remove.append(insight_id)
                count += 1
        
        for insight_id in to_remove:
            del self.insights[insight_id]
            
        return count


class FileStorage(StorageBackend):
    """File-based implementation of the analytics storage backend."""
    
    def __init__(self, base_dir: Union[str, Path]):
        self.base_dir = Path(base_dir)
        self.raw_data_dir = self.base_dir / "raw_data"
        self.processed_data_dir = self.base_dir / "processed_data"
        self.insights_dir = self.base_dir / "insights"
        
        # Create directories if they don't exist
        self.raw_data_dir.mkdir(parents=True, exist_ok=True)
        self.processed_data_dir.mkdir(parents=True, exist_ok=True)
        self.insights_dir.mkdir(parents=True, exist_ok=True)
        
        # Create index files if they don't exist
        self.raw_index_path = self.base_dir / "raw_index.json"
        self.processed_index_path = self.base_dir / "processed_index.json"
        self.insights_index_path = self.base_dir / "insights_index.json"
        
        if not self.raw_index_path.exists():
            with open(self.raw_index_path, 'w') as f:
                json.dump({}, f)
                
        if not self.processed_index_path.exists():
            with open(self.processed_index_path, 'w') as f:
                json.dump({}, f)
                
        if not self.insights_index_path.exists():
            with open(self.insights_index_path, 'w') as f:
                json.dump({}, f)
    
    def _generate_id(self, prefix: str) -> str:
        """Generate a unique identifier with the given prefix."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        return f"{prefix}_{timestamp}"
    
    def _update_raw_index(self, data_id: str, metadata: Dict[str, Any]):
        """Update the raw data index with metadata for the given ID."""
        with open(self.raw_index_path, 'r') as f:
            index = json.load(f)
        
        index[data_id] = metadata
        
        with open(self.raw_index_path, 'w') as f:
            json.dump(index, f)
    
    def _update_processed_index(self, data_id: str, metadata: Dict[str, Any]):
        """Update the processed data index with metadata for the given ID."""
        with open(self.processed_index_path, 'r') as f:
            index = json.load(f)
        
        index[data_id] = metadata
        
        with open(self.processed_index_path, 'w') as f:
            json.dump(index, f)
    
    def _update_insights_index(self, insight_id: str, metadata: Dict[str, Any]):
        """Update the insights index with metadata for the given ID."""
        with open(self.insights_index_path, 'r') as f:
            index = json.load(f)
        
        index[insight_id] = metadata
        
        with open(self.insights_index_path, 'w') as f:
            json.dump(index, f)
    
    def store_raw_data(self, source: str, data: Dict[str, Any], timestamp: Optional[datetime] = None) -> str:
        timestamp = timestamp or datetime.now()
        data_id = self._generate_id("raw")
        
        # Store the raw data
        with open(self.raw_data_dir / f"{data_id}.json", 'w') as f:
            json.dump(data, f)
        
        # Update the index
        metadata = {
            "source": source,
            "timestamp": timestamp.isoformat(),
            "file": f"{data_id}.json"
        }
        self._update_raw_index(data_id, metadata)
        
        return data_id
    
    def store_processed_data(self, data_id: str, data: PerformanceData, processing_stage: str) -> str:
        processed_id = self._generate_id("processed")
        
        # Store the processed data using pickle (for complex Python objects)
        with open(self.processed_data_dir / f"{processed_id}.pkl", 'wb') as f:
            pickle.dump(data, f)
        
        # Update the index
        metadata = {
            "source_id": data_id,
            "processing_stage": processing_stage,
            "timestamp": datetime.now().isoformat(),
            "file": f"{processed_id}.pkl",
            "metrics": list(data.metrics.keys()),
            "dimensions": list(data.dimensions.keys()),
            "segments": [seg.name for seg in data.segments] if data.segments else []
        }
        self._update_processed_index(processed_id, metadata)
        
        return processed_id
    
    def store_insight(self, data_ids: List[str], insight_type: str, insight_data: Dict[str, Any]) -> str:
        insight_id = self._generate_id("insight")
        
        # Store the insight data
        with open(self.insights_dir / f"{insight_id}.json", 'w') as f:
            json.dump(insight_data, f)
        
        # Update the index
        metadata = {
            "data_ids": data_ids,
            "insight_type": insight_type,
            "timestamp": datetime.now().isoformat(),
            "file": f"{insight_id}.json",
            "campaign_id": insight_data.get("campaign_id", "unknown")
        }
        self._update_insights_index(insight_id, metadata)
        
        return insight_id
    
    def retrieve_raw_data(self, data_id: str) -> Dict[str, Any]:
        with open(self.raw_index_path, 'r') as f:
            index = json.load(f)
        
        if data_id not in index:
            raise KeyError(f"Raw data with id {data_id} not found")
            
        file_name = index[data_id]["file"]
        with open(self.raw_data_dir / file_name, 'r') as f:
            return json.load(f)
    
    def retrieve_processed_data(self, data_id: str) -> PerformanceData:
        with open(self.processed_index_path, 'r') as f:
            index = json.load(f)
        
        if data_id not in index:
            raise KeyError(f"Processed data with id {data_id} not found")
            
        file_name = index[data_id]["file"]
        with open(self.processed_data_dir / file_name, 'rb') as f:
            return pickle.load(f)
    
    def retrieve_insight(self, insight_id: str) -> Dict[str, Any]:
        with open(self.insights_index_path, 'r') as f:
            index = json.load(f)
        
        if insight_id not in index:
            raise KeyError(f"Insight with id {insight_id} not found")
            
        file_name = index[insight_id]["file"]
        with open(self.insights_dir / file_name, 'r') as f:
            return json.load(f)
    
    def query_data(self, 
                  time_range: Optional[TimeRange] = None,
                  metrics: Optional[List[Metric]] = None,
                  dimensions: Optional[List[Dimension]] = None,
                  segments: Optional[List[Segment]] = None,
                  filters: Optional[Dict[str, Any]] = None,
                  processing_stage: Optional[str] = None) -> List[PerformanceData]:
        with open(self.processed_index_path, 'r') as f:
            index = json.load(f)
        
        results = []
        metric_names = [m.name for m in metrics] if metrics else None
        dimension_names = [d.name for d in dimensions] if dimensions else None
        segment_names = [s.name for s in segments] if segments else None
        
        for data_id, metadata in index.items():
            # Apply processing stage filter
            if processing_stage and metadata["processing_stage"] != processing_stage:
                continue
                
            # Apply time range filter
            if time_range:
                timestamp = datetime.fromisoformat(metadata["timestamp"])
                if not time_range.contains(timestamp):
                    continue
            
            # Apply metrics filter
            if metric_names:
                if not all(metric in metadata["metrics"] for metric in metric_names):
                    continue
            
            # Apply dimensions filter
            if dimension_names:
                if not all(dim in metadata["dimensions"] for dim in dimension_names):
                    continue
            
            # Apply segments filter
            if segment_names:
                if not all(seg in metadata["segments"] for seg in segment_names):
                    continue
            
            # Load the data for more detailed filtering
            data = self.retrieve_processed_data(data_id)
            
            # Apply custom filters
            if filters:
                skip = False
                for key, value in filters.items():
                    if key.startswith("dimension."):
                        dim_name = key[10:]
                        if dim_name not in data.dimensions or data.dimensions[dim_name] != value:
                            skip = True
                            break
                    elif key.startswith("metric."):
                        metric_name = key[7:]
                        if metric_name not in data.metrics or data.metrics[metric_name] != value:
                            skip = True
                            break
                if skip:
                    continue
            
            results.append(data)
        
        return results
    
    def query_insights(self,
                      insight_types: Optional[List[str]] = None,
                      time_range: Optional[TimeRange] = None,
                      campaigns: Optional[List[str]] = None,
                      limit: int = 100) -> List[Dict[str, Any]]:
        with open(self.insights_index_path, 'r') as f:
            index = json.load(f)
        
        results = []
        
        for insight_id, metadata in index.items():
            # Apply type filter
            if insight_types and metadata["insight_type"] not in insight_types:
                continue
                
            # Apply time range filter
            if time_range:
                timestamp = datetime.fromisoformat(metadata["timestamp"])
                if not time_range.contains(timestamp):
                    continue
            
            # Apply campaign filter
            if campaigns and metadata.get("campaign_id", "unknown") not in campaigns:
                continue
            
            # Load the insight data
            insight_data = self.retrieve_insight(insight_id)
            
            # Add to results with metadata
            insight_with_metadata = {
                "id": insight_id,
                "type": metadata["insight_type"],
                "timestamp": metadata["timestamp"],
                **insight_data
            }
            results.append(insight_with_metadata)
            
            # Respect the limit
            if len(results) >= limit:
                break
        
        # Sort by timestamp (newest first)
        results.sort(key=lambda x: x["timestamp"], reverse=True)
        return results
    
    def purge_old_data(self, older_than: datetime) -> int:
        count = 0
        
        # Purge raw data
        with open(self.raw_index_path, 'r') as f:
            raw_index = json.load(f)
        
        to_remove = []
        for data_id, metadata in raw_index.items():
            timestamp = datetime.fromisoformat(metadata["timestamp"])
            if timestamp < older_than:
                to_remove.append((data_id, metadata["file"]))
                count += 1
        
        for data_id, file_name in to_remove:
            file_path = self.raw_data_dir / file_name
            if file_path.exists():
                file_path.unlink()
            del raw_index[data_id]
        
        with open(self.raw_index_path, 'w') as f:
            json.dump(raw_index, f)
        
        # Purge processed data
        with open(self.processed_index_path, 'r') as f:
            processed_index = json.load(f)
        
        to_remove = []
        for data_id, metadata in processed_index.items():
            timestamp = datetime.fromisoformat(metadata["timestamp"])
            if timestamp < older_than:
                to_remove.append((data_id, metadata["file"]))
                count += 1
        
        for data_id, file_name in to_remove:
            file_path = self.processed_data_dir / file_name
            if file_path.exists():
                file_path.unlink()
            del processed_index[data_id]
        
        with open(self.processed_index_path, 'w') as f:
            json.dump(processed_index, f)
        
        # Purge insights
        with open(self.insights_index_path, 'r') as f:
            insights_index = json.load(f)
        
        to_remove = []
        for insight_id, metadata in insights_index.items():
            timestamp = datetime.fromisoformat(metadata["timestamp"])
            if timestamp < older_than:
                to_remove.append((insight_id, metadata["file"]))
                count += 1
        
        for insight_id, file_name in to_remove:
            file_path = self.insights_dir / file_name
            if file_path.exists():
                file_path.unlink()
            del insights_index[insight_id]
        
        with open(self.insights_index_path, 'w') as f:
            json.dump(insights_index, f)
        
        return count


class SQLiteStorage(StorageBackend):
    """SQLite-based implementation of the analytics storage backend."""
    
    def __init__(self, db_path: Union[str, Path]):
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(str(self.db_path))
        self._initialize_db()
    
    def _initialize_db(self):
        """Initialize the database schema if it doesn't exist."""
        cursor = self.conn.cursor()
        
        # Raw data table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS raw_data (
            id TEXT PRIMARY KEY,
            source TEXT NOT NULL,
            data TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
        ''')
        
        # Processed data table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS processed_data (
            id TEXT PRIMARY KEY,
            source_id TEXT NOT NULL,
            data BLOB NOT NULL,
            processing_stage TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (source_id) REFERENCES raw_data(id)
        )
        ''')
        
        # Processed data metadata table for efficient querying
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS processed_metadata (
            processed_id TEXT NOT NULL,
            key TEXT NOT NULL,
            value TEXT NOT NULL,
            PRIMARY KEY (processed_id, key),
            FOREIGN KEY (processed_id) REFERENCES processed_data(id)
        )
        ''')
        
        # Insights table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS insights (
            id TEXT PRIMARY KEY,
            insight_type TEXT NOT NULL,
            data TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
        ''')
        
        # Insight to data mapping table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS insight_data_map (
            insight_id TEXT NOT NULL,
            data_id TEXT NOT NULL,
            PRIMARY KEY (insight_id, data_id),
            FOREIGN KEY (insight_id) REFERENCES insights(id),
            FOREIGN KEY (data_id) REFERENCES processed_data(id)
        )
        ''')
        
        # Create indexes for efficient querying
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_raw_timestamp ON raw_data(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_processed_timestamp ON processed_data(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_processed_stage ON processed_data(processing_stage)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_insights_timestamp ON insights(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_insights_type ON insights(insight_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_metadata_key_value ON processed_metadata(key, value)')
        
        self.conn.commit()
    
    def store_raw_data(self, source: str, data: Dict[str, Any], timestamp: Optional[datetime] = None) -> str:
        timestamp = timestamp or datetime.now()
        data_id = f"raw_{int(timestamp.timestamp() * 1000000)}"
        
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO raw_data (id, source, data, timestamp) VALUES (?, ?, ?, ?)',
            (data_id, source, json.dumps(data), timestamp.isoformat())
        )
        self.conn.commit()
        
        return data_id
    
    def store_processed_data(self, data_id: str, data: PerformanceData, processing_stage: str) -> str:
        timestamp = datetime.now()
        processed_id = f"processed_{int(timestamp.timestamp() * 1000000)}"
        
        # Serialize the PerformanceData object
        serialized_data = pickle.dumps(data)
        
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO processed_data (id, source_id, data, processing_stage, timestamp) VALUES (?, ?, ?, ?, ?)',
            (processed_id, data_id, serialized_data, processing_stage, timestamp.isoformat())
        )
        
        # Store metadata for efficient querying
        metadata_entries = []
        
        # Store metrics as metadata
        for metric_name in data.metrics:
            metadata_entries.append((processed_id, f"metric.{metric_name}", "true"))
        
        # Store dimensions as metadata
        for dim_name, dim_value in data.dimensions.items():
            metadata_entries.append((processed_id, f"dimension.{dim_name}", str(dim_value)))
        
        # Store segments as metadata
        for segment in data.segments:
            metadata_entries.append((processed_id, f"segment.{segment.name}", "true"))
        
        # Add campaign_id as a top-level metadata for easier filtering
        if "campaign_id" in data.dimensions:
            metadata_entries.append((processed_id, "campaign_id", str(data.dimensions["campaign_id"])))
        
        cursor.executemany(
            'INSERT INTO processed_metadata (processed_id, key, value) VALUES (?, ?, ?)',
            metadata_entries
        )
        
        self.conn.commit()
        
        return processed_id
    
    def store_insight(self, data_ids: List[str], insight_type: str, insight_data: Dict[str, Any]) -> str:
        timestamp = datetime.now()
        insight_id = f"insight_{int(timestamp.timestamp() * 1000000)}"
        
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO insights (id, insight_type, data, timestamp) VALUES (?, ?, ?, ?)',
            (insight_id, insight_type, json.dumps(insight_data), timestamp.isoformat())
        )
        
        # Store the mapping between insight and data
        for data_id in data_ids:
            cursor.execute(
                'INSERT INTO insight_data_map (insight_id, data_id) VALUES (?, ?)',
                (insight_id, data_id)
            )
        
        self.conn.commit()
        
        return insight_id
    
    def retrieve_raw_data(self, data_id: str) -> Dict[str, Any]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT data FROM raw_data WHERE id = ?', (data_id,))
        result = cursor.fetchone()
        
        if not result:
            raise KeyError(f"Raw data with id {data_id} not found")
        
        return json.loads(result[0])
    
    def retrieve_processed_data(self, data_id: str) -> PerformanceData:
        cursor = self.conn.cursor()
        cursor.execute('SELECT data FROM processed_data WHERE id = ?', (data_id,))
        result = cursor.fetchone()
        
        if not result:
            raise KeyError(f"Processed data with id {data_id} not found")
        
        return pickle.loads(result[0])
    
    def retrieve_insight(self, insight_id: str) -> Dict[str, Any]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT data FROM insights WHERE id = ?', (insight_id,))
        result = cursor.fetchone()
        
        if not result:
            raise KeyError(f"Insight with id {insight_id} not found")
        
        return json.loads(result[0])
    
    def query_data(self, 
                  time_range: Optional[TimeRange] = None,
                  metrics: Optional[List[Metric]] = None,
                  dimensions: Optional[List[Dimension]] = None,
                  segments: Optional[List[Segment]] = None,
                  filters: Optional[Dict[str, Any]] = None,
                  processing_stage: Optional[str] = None) -> List[PerformanceData]:
        query_parts = ['SELECT pd.id FROM processed_data pd']
        where_clauses = []
        params = []
        
        # For each filter type, we'll need to join the metadata table
        join_count = 0
        
        # Process the time range filter
        if time_range:
            start_time = time_range.start_date.isoformat()
            end_time = time_range.end_date.isoformat()
            where_clauses.append('pd.timestamp BETWEEN ? AND ?')
            params.extend([start_time, end_time])
        
        # Process the processing stage filter
        if processing_stage:
            where_clauses.append('pd.processing_stage = ?')
            params.append(processing_stage)
        
        # Process metrics filter
        if metrics:
            for metric in metrics:
                join_count += 1
                alias = f"m{join_count}"
                query_parts.append(f'JOIN processed_metadata {alias} ON pd.id = {alias}.processed_id')
                where_clauses.append(f"{alias}.key = ?")
                params.append(f"metric.{metric.name}")
        
        # Process dimensions filter
        if dimensions:
            for dimension in dimensions:
                join_count += 1
                alias = f"m{join_count}"
                query_parts.append(f'JOIN processed_metadata {alias} ON pd.id = {alias}.processed_id')
                where_clauses.append(f"{alias}.key = ?")
                params.append(f"dimension.{dimension.name}")
        
        # Process segments filter
        if segments:
            for segment in segments:
                join_count += 1
                alias = f"m{join_count}"
                query_parts.append(f'JOIN processed_metadata {alias} ON pd.id = {alias}.processed_id')
                where_clauses.append(f"{alias}.key = ?")
                params.append(f"segment.{segment.name}")
        
        # Process custom filters
        if filters:
            for key, value in filters.items():
                join_count += 1
                alias = f"m{join_count}"
                query_parts.append(f'JOIN processed_metadata {alias} ON pd.id = {alias}.processed_id')
                where_clauses.append(f"{alias}.key = ? AND {alias}.value = ?")
                params.extend([key, str(value)])
        
        # Build the final query
        query = " ".join(query_parts)
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
        
        # Add order by timestamp (newest first)
        query += " ORDER BY pd.timestamp DESC"
        
        # Execute the query
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        data_ids = cursor.fetchall()
        
        # Retrieve the actual data objects
        results = []
        for (data_id,) in data_ids:
            try:
                data = self.retrieve_processed_data(data_id)
                results.append(data)
            except Exception as e:
                print(f"Error retrieving data {data_id}: {e}")
        
        return results
    
    def query_insights(self,
                      insight_types: Optional[List[str]] = None,
                      time_range: Optional[TimeRange] = None,
                      campaigns: Optional[List[str]] = None,
                      limit: int = 100) -> List[Dict[str, Any]]:
        query = 'SELECT i.id, i.insight_type, i.data, i.timestamp FROM insights i'
        where_clauses = []
        params = []
        
        # Process insight type filter
        if insight_types:
            placeholders = ', '.join(['?'] * len(insight_types))
            where_clauses.append(f'i.insight_type IN ({placeholders})')
            params.extend(insight_types)
        
        # Process time range filter
        if time_range:
            start_time = time_range.start_date.isoformat()
            end_time = time_range.end_date.isoformat()
            where_clauses.append('i.timestamp BETWEEN ? AND ?')
            params.extend([start_time, end_time])
        
        # Process campaign filter
        if campaigns:
            # We need to filter insights that have campaign_id in their data
            campaign_conditions = []
            for campaign_id in campaigns:
                campaign_conditions.append("i.data LIKE ?")
                params.append(f'%"campaign_id":"{campaign_id}"%')
            
            where_clauses.append('(' + ' OR '.join(campaign_conditions) + ')')
        
        # Build the final query
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
        
        # Add order by timestamp (newest first) and limit
        query += f" ORDER BY i.timestamp DESC LIMIT {limit}"
        
        # Execute the query
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        results = []
        
        for row in cursor.fetchall():
            insight_id, insight_type, data_json, timestamp = row
            insight_data = json.loads(data_json)
            
            insight_with_metadata = {
                "id": insight_id,
                "type": insight_type,
                "timestamp": timestamp,
                **insight_data
            }
            results.append(insight_with_metadata)
        
        return results
    
    def purge_old_data(self, older_than: datetime) -> int:
        cutoff_time = older_than.isoformat()
        cursor = self.conn.cursor()
        count = 0
        
        # First, get all insights to be deleted
        cursor.execute('SELECT id FROM insights WHERE timestamp < ?', (cutoff_time,))
        insight_ids = [row[0] for row in cursor.fetchall()]
        
        # Delete mappings for these insights
        if insight_ids:
            placeholders = ', '.join(['?'] * len(insight_ids))
            cursor.execute(f'DELETE FROM insight_data_map WHERE insight_id IN ({placeholders})', insight_ids)
            count += cursor.rowcount
        
        # Delete the insights themselves
        cursor.execute('DELETE FROM insights WHERE timestamp < ?', (cutoff_time,))
        count += cursor.rowcount
        
        # Get all processed data to be deleted
        cursor.execute('SELECT id FROM processed_data WHERE timestamp < ?', (cutoff_time,))
        processed_ids = [row[0] for row in cursor.fetchall()]
        
        # Delete metadata for these processed data
        if processed_ids:
            placeholders = ', '.join(['?'] * len(processed_ids))
            cursor.execute(f'DELETE FROM processed_metadata WHERE processed_id IN ({placeholders})', processed_ids)
            count += cursor.rowcount
            
            # Delete any remaining mappings that reference these processed data
            cursor.execute(f'DELETE FROM insight_data_map WHERE data_id IN ({placeholders})', processed_ids)
            count += cursor.rowcount
        
        # Delete the processed data themselves
        cursor.execute('DELETE FROM processed_data WHERE timestamp < ?', (cutoff_time,))
        count += cursor.rowcount
        
        # Finally, delete raw data
        cursor.execute('DELETE FROM raw_data WHERE timestamp < ?', (cutoff_time,))
        count += cursor.rowcount
        
        self.conn.commit()
        return count
    
    def __del__(self):
        """Ensure the database connection is closed when the object is destroyed."""
        if hasattr(self, 'conn'):
            self.conn.close()


# Factory function to create the appropriate storage backend
def create_storage(storage_type: str, **kwargs) -> StorageBackend:
    """Create and return a storage backend of the specified type with the given parameters."""
    if storage_type == "memory":
        return InMemoryStorage()
    elif storage_type == "file":
        base_dir = kwargs.get("base_dir", "./analytics_data")
        return FileStorage(base_dir)
    elif storage_type == "sqlite":
        db_path = kwargs.get("db_path", "./analytics.db")
        return SQLiteStorage(db_path)
    else:
        raise ValueError(f"Unknown storage type: {storage_type}")