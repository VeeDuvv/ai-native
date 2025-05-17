"""
Implementations of metrics storage systems.

This module provides concrete implementations of the metrics storage
interfaces for persisting and retrieving metrics.
"""

import json
import os
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime
import sqlite3
from contextlib import contextmanager

from .interfaces import MetricsStorage, MetricValue


class InMemoryMetricsStorage(MetricsStorage):
    """
    In-memory implementation of metrics storage.
    
    This implementation stores metrics in memory, suitable for testing
    and small-scale deployments.
    """
    
    def __init__(self):
        """Initialize the metrics storage."""
        self.metrics = {}  # name -> [(timestamp, value, tags)]
        self.logger = logging.getLogger("metrics.storage.memory")
    
    def store_metric(self, name: str, value: MetricValue,
                   tags: Optional[Dict[str, str]] = None) -> None:
        """Store a metric value."""
        tags = tags or {}
        
        if name not in self.metrics:
            self.metrics[name] = []
        
        self.metrics[name].append((value.timestamp, value, tags))
        self.logger.debug(f"Stored metric {name} = {value.value} at {value.timestamp}")
    
    def get_metrics(self, name: str, start_time: Optional[datetime] = None,
                 end_time: Optional[datetime] = None,
                 tags: Optional[Dict[str, str]] = None) -> List[MetricValue]:
        """Retrieve metric values."""
        if name not in self.metrics:
            return []
        
        metrics = self.metrics[name]
        
        # Filter by time range
        if start_time:
            metrics = [m for m in metrics if m[0] >= start_time]
        
        if end_time:
            metrics = [m for m in metrics if m[0] <= end_time]
        
        # Filter by tags
        if tags:
            metrics = [
                m for m in metrics
                if all(m[2].get(k) == v for k, v in tags.items())
            ]
        
        return [m[1] for m in metrics]
    
    def get_metrics_summary(self, name: str, start_time: Optional[datetime] = None,
                          end_time: Optional[datetime] = None,
                          tags: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Get a summary of metric values."""
        metrics = self.get_metrics(name, start_time, end_time, tags)
        
        if not metrics:
            return {
                "name": name,
                "count": 0,
                "min": None,
                "max": None,
                "avg": None,
                "first": None,
                "last": None
            }
        
        numeric_values = [m.value for m in metrics if isinstance(m.value, (int, float))]
        
        if numeric_values:
            return {
                "name": name,
                "count": len(metrics),
                "min": min(numeric_values),
                "max": max(numeric_values),
                "avg": sum(numeric_values) / len(numeric_values),
                "first": metrics[0].value,
                "last": metrics[-1].value,
                "first_timestamp": metrics[0].timestamp,
                "last_timestamp": metrics[-1].timestamp
            }
        else:
            return {
                "name": name,
                "count": len(metrics),
                "first": metrics[0].value,
                "last": metrics[-1].value,
                "first_timestamp": metrics[0].timestamp,
                "last_timestamp": metrics[-1].timestamp
            }


class SQLiteMetricsStorage(MetricsStorage):
    """
    SQLite implementation of metrics storage.
    
    This implementation stores metrics in a SQLite database, providing
    persistence and efficient querying.
    """
    
    def __init__(self, db_path: str):
        """
        Initialize the SQLite metrics storage.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.logger = logging.getLogger("metrics.storage.sqlite")
        
        # Ensure the database directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize the database
        self._init_db()
    
    @contextmanager
    def _get_connection(self):
        """Get a database connection with context management."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def _init_db(self):
        """Initialize the database schema."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Create metrics table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                value TEXT NOT NULL,
                value_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                metadata TEXT
            )
            ''')
            
            # Create tags table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS metric_tags (
                metric_id INTEGER,
                tag_key TEXT NOT NULL,
                tag_value TEXT NOT NULL,
                FOREIGN KEY (metric_id) REFERENCES metrics (id),
                PRIMARY KEY (metric_id, tag_key)
            )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_metrics_name ON metrics (name)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON metrics (timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_metric_tags_key ON metric_tags (tag_key, tag_value)')
            
            conn.commit()
    
    def store_metric(self, name: str, value: MetricValue,
                   tags: Optional[Dict[str, str]] = None) -> None:
        """Store a metric value in the database."""
        tags = tags or {}
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Store the metric
            cursor.execute('''
            INSERT INTO metrics (name, value, value_type, timestamp, metadata)
            VALUES (?, ?, ?, ?, ?)
            ''', (
                name,
                str(value.value),
                type(value.value).__name__,
                value.timestamp.isoformat(),
                json.dumps(value.metadata) if value.metadata else None
            ))
            
            metric_id = cursor.lastrowid
            
            # Store the tags
            for key, val in tags.items():
                cursor.execute('''
                INSERT INTO metric_tags (metric_id, tag_key, tag_value)
                VALUES (?, ?, ?)
                ''', (metric_id, key, val))
            
            conn.commit()
        
        self.logger.debug(f"Stored metric {name} = {value.value} at {value.timestamp}")
    
    def get_metrics(self, name: str, start_time: Optional[datetime] = None,
                 end_time: Optional[datetime] = None,
                 tags: Optional[Dict[str, str]] = None) -> List[MetricValue]:
        """Retrieve metric values from the database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM metrics WHERE name = ?"
            params = [name]
            
            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time.isoformat())
            
            if end_time:
                query += " AND timestamp <= ?"
                params.append(end_time.isoformat())
            
            # If tags are specified, join with the tags table
            if tags:
                tag_conditions = []
                for i, (key, val) in enumerate(tags.items()):
                    query += f'''
                    AND id IN (
                        SELECT metric_id FROM metric_tags 
                        WHERE tag_key = ? AND tag_value = ?
                    )
                    '''
                    params.extend([key, val])
            
            query += " ORDER BY timestamp"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            result = []
            for row in rows:
                # Get the metric's tags
                cursor.execute('''
                SELECT tag_key, tag_value FROM metric_tags
                WHERE metric_id = ?
                ''', (row['id'],))
                tag_rows = cursor.fetchall()
                tags = {tag['tag_key']: tag['tag_value'] for tag in tag_rows}
                
                # Parse the value based on its type
                value = row['value']
                value_type = row['value_type']
                
                if value_type == 'int':
                    value = int(value)
                elif value_type in ('float', 'double'):
                    value = float(value)
                elif value_type == 'bool':
                    value = value.lower() == 'true'
                
                # Create the metric value
                metadata = json.loads(row['metadata']) if row['metadata'] else {}
                timestamp = datetime.fromisoformat(row['timestamp'])
                
                metric_value = MetricValue(value, timestamp, metadata)
                result.append(metric_value)
            
            return result
    
    def get_metrics_summary(self, name: str, start_time: Optional[datetime] = None,
                          end_time: Optional[datetime] = None,
                          tags: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Get a summary of metric values from the database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            query = '''
            SELECT 
                COUNT(*) as count,
                MIN(CASE WHEN value_type IN ('int', 'float', 'double') THEN CAST(value AS REAL) ELSE NULL END) as min_value,
                MAX(CASE WHEN value_type IN ('int', 'float', 'double') THEN CAST(value AS REAL) ELSE NULL END) as max_value,
                AVG(CASE WHEN value_type IN ('int', 'float', 'double') THEN CAST(value AS REAL) ELSE NULL END) as avg_value,
                MIN(timestamp) as first_timestamp,
                MAX(timestamp) as last_timestamp
            FROM metrics
            WHERE name = ?
            '''
            params = [name]
            
            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time.isoformat())
            
            if end_time:
                query += " AND timestamp <= ?"
                params.append(end_time.isoformat())
            
            # If tags are specified, join with the tags table
            if tags:
                for key, val in tags.items():
                    query += f'''
                    AND id IN (
                        SELECT metric_id FROM metric_tags 
                        WHERE tag_key = ? AND tag_value = ?
                    )
                    '''
                    params.extend([key, val])
            
            cursor.execute(query, params)
            summary_row = cursor.fetchone()
            
            if not summary_row or summary_row['count'] == 0:
                return {
                    "name": name,
                    "count": 0,
                    "min": None,
                    "max": None,
                    "avg": None,
                    "first": None,
                    "last": None
                }
            
            # Get the first and last values
            query = '''
            SELECT value, value_type
            FROM metrics
            WHERE name = ? 
            '''
            params = [name]
            
            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time.isoformat())
            
            if end_time:
                query += " AND timestamp <= ?"
                params.append(end_time.isoformat())
            
            if tags:
                for key, val in tags.items():
                    query += f'''
                    AND id IN (
                        SELECT metric_id FROM metric_tags 
                        WHERE tag_key = ? AND tag_value = ?
                    )
                    '''
                    params.extend([key, val])
            
            # Get first value
            first_query = query + " ORDER BY timestamp ASC LIMIT 1"
            cursor.execute(first_query, params)
            first_row = cursor.fetchone()
            
            # Get last value
            last_query = query + " ORDER BY timestamp DESC LIMIT 1"
            cursor.execute(last_query, params)
            last_row = cursor.fetchone()
            
            # Parse values based on their types
            first_value = first_row['value']
            first_type = first_row['value_type']
            
            if first_type == 'int':
                first_value = int(first_value)
            elif first_type in ('float', 'double'):
                first_value = float(first_value)
            elif first_type == 'bool':
                first_value = first_value.lower() == 'true'
            
            last_value = last_row['value']
            last_type = last_row['value_type']
            
            if last_type == 'int':
                last_value = int(last_value)
            elif last_type in ('float', 'double'):
                last_value = float(last_value)
            elif last_type == 'bool':
                last_value = last_value.lower() == 'true'
            
            return {
                "name": name,
                "count": summary_row['count'],
                "min": summary_row['min_value'],
                "max": summary_row['max_value'],
                "avg": summary_row['avg_value'],
                "first": first_value,
                "last": last_value,
                "first_timestamp": datetime.fromisoformat(summary_row['first_timestamp']),
                "last_timestamp": datetime.fromisoformat(summary_row['last_timestamp'])
            }