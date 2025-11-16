"""
MongoDB Slow Query Detection and Analysis Module

This module provides comprehensive MongoDB query profiling, detection,
and analysis capabilities for the Slow Query Doctor.
"""

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

from .mongodb_config import MongoDBThresholdConfig

try:
    from pymongo import MongoClient
    from pymongo.errors import PyMongoError

    pymongo_available = True
except ImportError:
    MongoClient = None
    PyMongoError = Exception
    pymongo_available = False

logger = logging.getLogger(__name__)


@dataclass
class MongoDBSlowQuery:
    """Represents a MongoDB slow query with analysis metadata."""

    # Core query information
    command: Dict[str, Any]
    collection: str
    database: str
    operation_type: str  # find, aggregate, update, delete, etc.
    duration_ms: float
    timestamp: datetime

    # Query analysis
    query_shape: str = ""  # Normalized query pattern
    index_usage: Dict[str, Any] = field(default_factory=dict)
    examined_docs: int = 0
    returned_docs: int = 0

    # Performance metrics
    execution_stats: Dict[str, Any] = field(default_factory=dict)
    planSummary: str = ""

    # Analysis results
    efficiency_score: float = 0.0
    impact_score: float = 0.0
    optimization_suggestions: List[str] = field(default_factory=list)

    # Frequency tracking
    frequency: int = 1
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    total_duration_ms: float = 0.0
    avg_duration_ms: float = 0.0


class MongoDBQueryPatternRecognizer:
    """Recognizes and categorizes MongoDB query patterns."""

    def __init__(self) -> None:
        self.pattern_cache: Dict[str, str] = {}

    def normalize_query(self, command: Dict[str, Any]) -> str:
        """
        Normalize MongoDB command to create a query pattern/shape.

        Args:
            command: MongoDB command document

        Returns:
            Normalized query pattern string
        """
        try:
            normalized = self._normalize_dict(command)
            return str(normalized)
        except Exception as e:
            logger.warning(f"Error normalizing MongoDB command: {e}")
            return str(command)

    def _normalize_dict(self, obj: Any, depth: int = 0) -> Any:
        """Recursively normalize dictionary values."""
        if depth > 10:  # Prevent infinite recursion
            return "..."

        if isinstance(obj, dict):
            normalized: Dict[str, Any] = {}
            for key, value in obj.items():
                if key in ["$regex", "$options"]:
                    normalized[key] = "?"
                elif isinstance(value, (str, int, float, bool)):
                    normalized[key] = "?"
                elif isinstance(value, list):
                    if len(value) > 0:
                        normalized[key] = [self._normalize_dict(value[0], depth + 1)]
                    else:
                        normalized[key] = []
                else:
                    normalized[key] = self._normalize_dict(value, depth + 1)
            return normalized
        elif isinstance(obj, list):
            if len(obj) > 0:
                return [self._normalize_dict(obj[0], depth + 1)]
            return []
        else:
            return "?"

    def categorize_operation(self, command: Dict[str, Any]) -> str:
        """Categorize the MongoDB operation type."""
        if "find" in command:
            return "find"
        elif "aggregate" in command:
            return "aggregate"
        elif "update" in command or "updateOne" in command or "updateMany" in command:
            return "update"
        elif "delete" in command or "deleteOne" in command or "deleteMany" in command:
            return "delete"
        elif "insert" in command or "insertOne" in command or "insertMany" in command:
            return "insert"
        elif "count" in command or "countDocuments" in command:
            return "count"
        elif "distinct" in command:
            return "distinct"
        elif "createIndex" in command or "createIndexes" in command:
            return "index_creation"
        else:
            return "other"


class MongoDBProfilerIntegration:
    """Integrates with MongoDB profiler to collect slow query data."""

    def __init__(self, connection_string: str, thresholds: MongoDBThresholdConfig):
        if not pymongo_available:
            raise ImportError(
                "pymongo is required for MongoDB integration. "
                "Install with: pip install pymongo"
            )

        self.connection_string = connection_string
        self.thresholds = thresholds
        self.client: Any = None
        self.pattern_recognizer = MongoDBQueryPatternRecognizer()

    def connect(self) -> bool:
        """Establish connection to MongoDB."""
        try:
            self.client = MongoClient(
                self.connection_string, serverSelectionTimeoutMS=5000
            )
            # Test connection
            self.client.admin.command("ping")
            logger.info("Successfully connected to MongoDB")
            return True
        except PyMongoError as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            return False

    def enable_profiling(self, database_name: str, level: int = 2) -> bool:
        """
        Enable MongoDB profiling for slow query collection.

        Args:
            database_name: Name of the database to profile
            level: Profiling level (0=off, 1=slow ops, 2=all ops)

        Returns:
            True if profiling was enabled successfully
        """
        if not self.client:
            logger.error("Not connected to MongoDB")
            return False

        try:
            db = self.client[database_name]

            # Set profiling level and slow operation threshold
            result = db.command(
                "profile", level, slowms=int(self.thresholds.slow_threshold_ms)
            )

            logger.info(
                f"Enabled profiling for database '{database_name}' "
                f"at level {level} with {self.thresholds.slow_threshold_ms}ms threshold"
            )
            return bool(result.get("ok", 0) == 1)

        except PyMongoError as e:
            logger.error(f"Failed to enable profiling: {e}")
            return False

    def collect_profile_data(
        self, database_name: str, time_window_minutes: int = 60
    ) -> List[Dict[str, Any]]:
        """
        Collect profiling data from system.profile collection.

        Args:
            database_name: Database to collect data from
            time_window_minutes: Time window for data collection

        Returns:
            List of profile documents
        """
        if not self.client:
            logger.error("Not connected to MongoDB")
            return []

        try:
            db = self.client[database_name]
            profile_collection = db["system.profile"]

            # Calculate time window
            end_time = datetime.now()
            start_time = end_time - timedelta(minutes=time_window_minutes)

            # Query profile collection
            cursor = profile_collection.find(
                {
                    "ts": {"$gte": start_time, "$lte": end_time},
                    "millis": {"$gte": self.thresholds.slow_threshold_ms},
                }
            ).sort("ts", -1)

            profile_data = list(cursor)
            logger.info(f"Collected {len(profile_data)} profile records")

            return profile_data

        except PyMongoError as e:
            logger.error(f"Failed to collect profile data: {e}")
            return []

    def analyze_profile_record(self, record: Dict[str, Any]) -> MongoDBSlowQuery:
        """
        Analyze a single profile record and create MongoDBSlowQuery object.

        Args:
            record: Profile record from system.profile

        Returns:
            MongoDBSlowQuery object with analysis
        """
        command = record.get("command", {})

        # Extract basic information
        collection = (
            record.get("ns", "").split(".")[-1] if "." in record.get("ns", "") else ""
        )
        database = (
            record.get("ns", "").split(".")[0] if "." in record.get("ns", "") else ""
        )
        duration_ms = record.get("millis", 0)
        timestamp = record.get("ts", datetime.now())

        # Determine operation type
        operation_type = self.pattern_recognizer.categorize_operation(command)

        # Create query shape
        query_shape = self.pattern_recognizer.normalize_query(command)

        # Extract execution statistics
        execution_stats = {
            "totalDocsExamined": record.get("totalDocsExamined", 0),
            "totalDocsReturned": record.get("docsReturned", 0),
            "executionTimeMillisEstimate": record.get("executionTimeMillisEstimate", 0),
            "planSummary": record.get("planSummary", ""),
            "keysExamined": record.get("keysExamined", 0),
            "docsExamined": record.get("docsExamined", 0),
        }

        # Calculate efficiency metrics
        examined_docs = execution_stats["totalDocsExamined"]
        returned_docs = execution_stats["totalDocsReturned"]

        efficiency_score = self._calculate_efficiency_score(
            examined_docs, returned_docs, duration_ms, execution_stats
        )

        impact_score = self._calculate_impact_score(
            duration_ms, examined_docs, operation_type
        )

        # Generate optimization suggestions
        suggestions = self._generate_optimization_suggestions(
            record, execution_stats, operation_type
        )

        return MongoDBSlowQuery(
            command=command,
            collection=collection,
            database=database,
            operation_type=operation_type,
            duration_ms=duration_ms,
            timestamp=timestamp,
            query_shape=query_shape,
            examined_docs=examined_docs,
            returned_docs=returned_docs,
            execution_stats=execution_stats,
            planSummary=execution_stats["planSummary"],
            efficiency_score=efficiency_score,
            impact_score=impact_score,
            optimization_suggestions=suggestions,
            total_duration_ms=duration_ms,
            avg_duration_ms=duration_ms,
        )

    def _calculate_efficiency_score(
        self,
        examined_docs: int,
        returned_docs: int,
        duration_ms: float,
        execution_stats: Dict[str, Any],
    ) -> float:
        """Calculate query efficiency score (0-1, higher is better)."""
        score = 1.0

        # Penalize high examined/returned ratio
        if returned_docs > 0:
            exam_ratio = examined_docs / returned_docs
            if exam_ratio > self.thresholds.max_examined_ratio:
                score *= 0.3
            elif exam_ratio > 5:
                score *= 0.6
            elif exam_ratio > 2:
                score *= 0.8

        # Penalize collection scans
        plan_summary = execution_stats.get("planSummary", "")
        if "COLLSCAN" in plan_summary:
            score *= 0.2
        elif "IXSCAN" not in plan_summary and examined_docs > 100:
            score *= 0.4

        # Penalize high duration
        if duration_ms > self.thresholds.critical_threshold_ms:
            score *= 0.3
        elif duration_ms > self.thresholds.very_slow_threshold_ms:
            score *= 0.6

        return max(0.0, min(1.0, score))

    def _calculate_impact_score(
        self, duration_ms: float, examined_docs: int, operation_type: str
    ) -> float:
        """Calculate query impact score (0-100, higher is worse)."""
        score = 0.0

        # Duration impact
        if duration_ms > self.thresholds.critical_threshold_ms:
            score += 40
        elif duration_ms > self.thresholds.very_slow_threshold_ms:
            score += 25
        elif duration_ms > self.thresholds.slow_threshold_ms:
            score += 10

        # Document examination impact
        if examined_docs > 1000000:
            score += 30
        elif examined_docs > 100000:
            score += 20
        elif examined_docs > 10000:
            score += 10

        # Operation type impact
        if operation_type in ["update", "delete"]:
            score += 15
        elif operation_type == "aggregate":
            score += 10
        elif operation_type == "find":
            score += 5

        return min(100.0, score)

    def _generate_optimization_suggestions(
        self,
        record: Dict[str, Any],
        execution_stats: Dict[str, Any],
        operation_type: str,
    ) -> List[str]:
        """Generate optimization suggestions based on query analysis."""
        suggestions = []

        plan_summary = execution_stats.get("planSummary", "")
        examined_docs = execution_stats.get("totalDocsExamined", 0)
        returned_docs = execution_stats.get("totalDocsReturned", 0)

        # Collection scan detection
        if "COLLSCAN" in plan_summary:
            suggestions.append(
                "⚠️ Collection scan detected - consider adding an index on "
                "frequently queried fields"
            )

        # High examined/returned ratio
        if returned_docs > 0 and examined_docs / returned_docs > 10:
            suggestions.append(
                "📊 High document examination ratio - optimize query selectivity "
                "or add compound indexes"
            )

        # Missing index usage
        if "IXSCAN" not in plan_summary and examined_docs > 1000:
            suggestions.append(
                "🔍 No index usage detected - create indexes on query filters"
            )

        # Sort without index
        if record.get("command", {}).get("sort") and "SORT" in plan_summary:
            suggestions.append(
                "🔄 In-memory sort detected - consider adding an index to support "
                "the sort operation"
            )

        # Large result sets
        if returned_docs > 10000:
            suggestions.append(
                "📄 Large result set - consider adding pagination using limit() "
                "and skip() or cursor-based pagination"
            )

        # Aggregation optimization
        if operation_type == "aggregate" and examined_docs > 100000:
            suggestions.append(
                "🔧 Aggregation pipeline optimization - ensure $match stages "
                "are early in the pipeline and use indexes"
            )

        return suggestions


class MongoDBCollectionAnalyzer:
    """Provides collection-level analysis and insights."""

    def __init__(self, profiler: MongoDBProfilerIntegration):
        self.profiler = profiler
        self.collection_stats: Dict[str, Dict[str, Any]] = defaultdict(dict)

    def analyze_collection_performance(
        self, database_name: str, collection_name: str
    ) -> Dict[str, Any]:
        """
        Analyze performance characteristics of a specific collection.

        Args:
            database_name: Database name
            collection_name: Collection name

        Returns:
            Collection performance analysis
        """
        if not self.profiler.client:
            return {}

        try:
            db = self.profiler.client[database_name]
            collection = db[collection_name]

            # Get collection statistics
            stats = db.command("collStats", collection_name)

            # Get index information
            indexes = list(collection.list_indexes())

            # Analyze recent profile data for this collection
            profile_data = self.profiler.collect_profile_data(database_name, 60)
            collection_queries = [
                record
                for record in profile_data
                if record.get("ns", "").endswith(f".{collection_name}")
            ]

            analysis = {
                "collection_name": collection_name,
                "database_name": database_name,
                "document_count": stats.get("count", 0),
                "storage_size": stats.get("size", 0),
                "index_count": len(indexes),
                "indexes": [idx.get("name", "unknown") for idx in indexes],
                "recent_slow_queries": len(collection_queries),
                "avg_query_time": 0,
                "most_common_operations": {},
                "optimization_recommendations": [],
            }

            if collection_queries:
                # Calculate average query time
                total_time = sum(q.get("millis", 0) for q in collection_queries)
                analysis["avg_query_time"] = total_time / len(collection_queries)

                # Analyze operation patterns
                operations: Dict[str, int] = defaultdict(int)
                for query in collection_queries:
                    op_type = self.profiler.pattern_recognizer.categorize_operation(
                        query.get("command", {})
                    )
                    operations[op_type] += 1

                analysis["most_common_operations"] = dict(operations)

                # Generate collection-level recommendations
                analysis["optimization_recommendations"] = (
                    self._generate_collection_recommendations(
                        analysis, collection_queries, indexes
                    )
                )

            return analysis

        except PyMongoError as e:
            logger.error(f"Failed to analyze collection {collection_name}: {e}")
            return {}

    def _generate_collection_recommendations(
        self,
        analysis: Dict[str, Any],
        queries: List[Dict[str, Any]],
        indexes: List[Dict[str, Any]],
    ) -> List[str]:
        """Generate collection-level optimization recommendations."""
        recommendations = []

        # Check for missing indexes
        if analysis["recent_slow_queries"] > 10 and analysis["index_count"] < 3:
            recommendations.append(
                "📈 High slow query frequency with few indexes - consider adding "
                "indexes on commonly queried fields"
            )

        # Check for collection scans
        collscan_queries = [
            q for q in queries if "COLLSCAN" in q.get("planSummary", "")
        ]
        if len(collscan_queries) > len(queries) * 0.5:
            recommendations.append(
                "🔍 High percentage of collection scans detected - review and "
                "optimize query patterns and indexes"
            )

        # Check for large document counts with slow queries
        if analysis["document_count"] > 1000000 and analysis["avg_query_time"] > 500:
            recommendations.append(
                "⚡ Large collection with slow average query time - consider "
                "data archiving, partitioning, or index optimization"
            )

        # Check for unused indexes (basic heuristic)
        if analysis["index_count"] > 10:
            recommendations.append(
                "🗂️ High number of indexes detected - review for unused indexes "
                "that may be impacting write performance"
            )

        return recommendations


class MongoDBSlowQueryDetector:
    """Main class for MongoDB slow query detection and analysis."""

    def __init__(
        self,
        connection_string: str,
        thresholds: Optional[MongoDBThresholdConfig] = None,
    ) -> None:
        self.thresholds = thresholds or MongoDBThresholdConfig()
        self.profiler = MongoDBProfilerIntegration(connection_string, self.thresholds)
        self.collection_analyzer = MongoDBCollectionAnalyzer(self.profiler)
        self.query_cache: Dict[str, MongoDBSlowQuery] = {}

    def initialize(self) -> bool:
        """Initialize the detector and establish connections."""
        success = self.profiler.connect()
        if success:
            logger.info("MongoDB Slow Query Detector initialized successfully")
        return success

    def start_monitoring(self, database_names: List[str]) -> bool:
        """Start monitoring specified databases."""
        success = True
        for db_name in database_names:
            if not self.profiler.enable_profiling(db_name, level=1):
                logger.error(f"Failed to enable profiling for database: {db_name}")
                success = False
        return success

    def detect_slow_queries(
        self, database_name: str, time_window_minutes: int = 60
    ) -> List[MongoDBSlowQuery]:
        """
        Detect and analyze slow queries from the specified database.

        Args:
            database_name: Database to analyze
            time_window_minutes: Time window for analysis

        Returns:
            List of analyzed slow queries
        """
        # Collect profile data
        profile_data = self.profiler.collect_profile_data(
            database_name, time_window_minutes
        )

        if not profile_data:
            logger.warning(f"No profile data found for database: {database_name}")
            return []

        # Analyze each profile record
        slow_queries = []
        query_groups: Dict[str, List[MongoDBSlowQuery]] = defaultdict(list)

        for record in profile_data:
            try:
                slow_query = self.profiler.analyze_profile_record(record)
                query_groups[slow_query.query_shape].append(slow_query)
            except Exception as e:
                logger.warning(f"Failed to analyze profile record: {e}")
                continue

        # Aggregate similar queries
        for query_shape, queries in query_groups.items():
            if len(queries) >= self.thresholds.min_frequency_for_analysis:
                aggregated_query = self._aggregate_similar_queries(queries)
                slow_queries.append(aggregated_query)

        # Sort by impact score
        slow_queries.sort(key=lambda q: q.impact_score, reverse=True)

        logger.info(f"Detected {len(slow_queries)} slow query patterns")
        return slow_queries

    def _aggregate_similar_queries(
        self, queries: List[MongoDBSlowQuery]
    ) -> MongoDBSlowQuery:
        """Aggregate multiple similar queries into a single analysis."""
        if not queries:
            raise ValueError("Cannot aggregate empty query list")

        base_query = queries[0]

        # Calculate aggregated metrics
        total_duration = sum(q.duration_ms for q in queries)
        avg_duration = total_duration / len(queries)
        max_duration = max(q.duration_ms for q in queries)

        # Find time range
        timestamps = [q.timestamp for q in queries]
        first_seen = min(timestamps)
        last_seen = max(timestamps)

        # Aggregate suggestions (unique only)
        all_suggestions = []
        for q in queries:
            all_suggestions.extend(q.optimization_suggestions)
        unique_suggestions = list(set(all_suggestions))

        # Calculate aggregated scores
        avg_efficiency = sum(q.efficiency_score for q in queries) / len(queries)
        avg_impact = sum(q.impact_score for q in queries) / len(queries)

        # Create aggregated query
        aggregated = MongoDBSlowQuery(
            command=base_query.command,
            collection=base_query.collection,
            database=base_query.database,
            operation_type=base_query.operation_type,
            duration_ms=max_duration,
            timestamp=last_seen,
            query_shape=base_query.query_shape,
            examined_docs=max(q.examined_docs for q in queries),
            returned_docs=max(q.returned_docs for q in queries),
            execution_stats=base_query.execution_stats,
            planSummary=base_query.planSummary,
            efficiency_score=avg_efficiency,
            impact_score=avg_impact,
            optimization_suggestions=unique_suggestions,
            frequency=len(queries),
            first_seen=first_seen,
            last_seen=last_seen,
            total_duration_ms=total_duration,
            avg_duration_ms=avg_duration,
        )

        return aggregated

    def generate_comprehensive_report(
        self, database_name: str, include_collection_analysis: bool = True
    ) -> Dict[str, Any]:
        """Generate a comprehensive analysis report."""
        report: Dict[str, Any] = {
            "database_name": database_name,
            "analysis_timestamp": datetime.now().isoformat(),
            "slow_queries": [],
            "collection_analyses": [],
            "summary": {},
            "recommendations": [],
        }

        # Detect slow queries
        slow_queries = self.detect_slow_queries(database_name)
        report["slow_queries"] = [self._query_to_dict(query) for query in slow_queries]

        # Collection-level analysis
        if include_collection_analysis and self.profiler.client:
            try:
                db = self.profiler.client[database_name]
                collections = db.list_collection_names()

                for collection_name in collections[:10]:  # Limit to first 10
                    if not collection_name.startswith("system."):
                        analysis = (
                            self.collection_analyzer.analyze_collection_performance(
                                database_name, collection_name
                            )
                        )
                        if analysis:
                            report["collection_analyses"].append(analysis)

            except Exception as e:
                logger.warning(f"Failed to perform collection analysis: {e}")

        # Generate summary
        report["summary"] = self._generate_summary_stats(slow_queries)

        # Generate database-level recommendations
        collection_analyses_data = report.get("collection_analyses", [])
        if isinstance(collection_analyses_data, list):
            collection_analyses = collection_analyses_data
        else:
            collection_analyses = []
        report["recommendations"] = self._generate_database_recommendations(
            slow_queries, collection_analyses
        )

        return report

    def _query_to_dict(self, query: MongoDBSlowQuery) -> Dict[str, Any]:
        """Convert MongoDBSlowQuery to dictionary for serialization."""
        return {
            "collection": query.collection,
            "database": query.database,
            "operation_type": query.operation_type,
            "duration_ms": query.duration_ms,
            "avg_duration_ms": query.avg_duration_ms,
            "total_duration_ms": query.total_duration_ms,
            "frequency": query.frequency,
            "examined_docs": query.examined_docs,
            "returned_docs": query.returned_docs,
            "efficiency_score": query.efficiency_score,
            "impact_score": query.impact_score,
            "planSummary": query.planSummary,
            "optimization_suggestions": query.optimization_suggestions,
            "first_seen": query.first_seen.isoformat(),
            "last_seen": query.last_seen.isoformat(),
            "query_shape": query.query_shape[:500],  # Truncate for readability
        }

    def _generate_summary_stats(
        self, slow_queries: List[MongoDBSlowQuery]
    ) -> Dict[str, Any]:
        """Generate summary statistics for the analysis."""
        if not slow_queries:
            return {
                "total_slow_queries": 0,
                "avg_duration_ms": 0,
                "total_impact_score": 0,
                "most_common_operation": "none",
                "collections_affected": 0,
            }

        operations: Dict[str, int] = defaultdict(int)
        collections: set[str] = set()

        for query in slow_queries:
            operations[query.operation_type] += query.frequency
            collections.add(query.collection)

        most_common_op = (
            max(operations.items(), key=lambda x: x[1])[0] if operations else "none"
        )

        return {
            "total_slow_queries": len(slow_queries),
            "total_executions": sum(q.frequency for q in slow_queries),
            "avg_duration_ms": sum(q.avg_duration_ms for q in slow_queries)
            / len(slow_queries),
            "total_impact_score": sum(q.impact_score for q in slow_queries),
            "most_common_operation": most_common_op,
            "collections_affected": len(collections),
            "avg_efficiency_score": sum(q.efficiency_score for q in slow_queries)
            / len(slow_queries),
        }

    def _generate_database_recommendations(
        self,
        slow_queries: List[MongoDBSlowQuery],
        collection_analyses: List[Dict[str, Any]],
    ) -> List[str]:
        """Generate database-level optimization recommendations."""
        recommendations: List[str] = []

        if not slow_queries:
            recommendations.append(
                "✅ No slow queries detected in the analyzed time window"
            )
            return recommendations

        # High-impact queries
        critical_queries = [q for q in slow_queries if q.impact_score > 50]
        if critical_queries:
            recommendations.append(
                f"🚨 {len(critical_queries)} critical slow queries detected - "
                "prioritize optimization immediately"
            )

        # Collection scan analysis
        collscan_queries = [q for q in slow_queries if "COLLSCAN" in q.planSummary]
        if len(collscan_queries) > len(slow_queries) * 0.3:
            recommendations.append(
                "🔍 High percentage of collection scans - implement comprehensive "
                "indexing strategy"
            )

        # Operation type analysis
        operations: Dict[str, int] = defaultdict(int)
        for query in slow_queries:
            operations[query.operation_type] += query.frequency

        if operations.get("aggregate", 0) > operations.get("find", 0):
            recommendations.append(
                "📊 Aggregation queries dominate slow operations - optimize "
                "pipeline stages and ensure early $match operations"
            )

        # Efficiency analysis
        low_efficiency_queries = [q for q in slow_queries if q.efficiency_score < 0.3]
        if len(low_efficiency_queries) > len(slow_queries) * 0.5:
            recommendations.append(
                "⚡ Many queries have low efficiency scores - review query "
                "selectivity and index coverage"
            )

        return recommendations
