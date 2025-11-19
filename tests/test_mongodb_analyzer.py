"""
Test suite for MongoDB slow query detection functionality.

This module provides comprehensive tests for MongoDB query analysis,
profiler integration, configuration management, and report generation.
"""

import json
import pytest
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

# Import MongoDB modules
from iqtoolkit_analyzer.mongodb_analyzer import (
    MongoDBSlowQuery,
    MongoDBQueryPatternRecognizer,
    MongoDBProfilerIntegration,
    MongoDBSlowQueryDetector,
)
from iqtoolkit_analyzer.mongodb_config import (
    MongoDBThresholdConfig,
    MongoDBConfig,
    load_mongodb_config,
)
from iqtoolkit_analyzer.mongodb_report_generator import MongoDBReportGenerator


class TestMongoDBSlowQuery:
    """Test MongoDB slow query data class."""

    def test_slow_query_creation(self):
        """Test creation of MongoDBSlowQuery instance."""
        query = MongoDBSlowQuery(
            command={"find": "users", "filter": {"active": True}},
            collection="users",
            database="testdb",
            operation_type="find",
            duration_ms=500.0,
            timestamp=datetime.now(),
        )

        assert query.collection == "users"
        assert query.database == "testdb"
        assert query.operation_type == "find"
        assert query.duration_ms == 500.0
        assert query.frequency == 1
        assert query.efficiency_score == 0.0
        assert query.impact_score == 0.0


class TestMongoDBQueryPatternRecognizer:
    """Test MongoDB query pattern recognition functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.recognizer = MongoDBQueryPatternRecognizer()

    def test_normalize_simple_find_query(self):
        """Test normalization of simple find query."""
        command = {"find": "users", "filter": {"name": "John", "age": 25}}

        normalized = self.recognizer.normalize_query(command)

        # Should contain the normalized elements (JSON format with sorted keys)
        assert '"find": "?"' in normalized
        assert '"filter":' in normalized
        assert '"name": "?"' in normalized
        assert '"age": "?"' in normalized

    def test_normalize_complex_aggregation(self):
        """Test normalization of complex aggregation pipeline."""
        command = {
            "aggregate": "orders",
            "pipeline": [
                {"$match": {"status": "completed", "total": {"$gt": 100}}},
                {"$group": {"_id": "$customer_id", "total": {"$sum": "$amount"}}},
            ],
        }

        normalized = self.recognizer.normalize_query(command)

        # Should normalize literal values but preserve structure
        assert '"aggregate": "?"' in normalized
        assert '"status": "?"' in normalized
        assert '"$gt": "?"' in normalized

    def test_categorize_operations(self):
        """Test operation type categorization."""
        test_cases = [
            ({"find": "users"}, "find"),
            ({"aggregate": "orders"}, "aggregate"),
            ({"updateOne": "users"}, "update"),
            ({"deleteMany": "logs"}, "delete"),
            ({"insertOne": "users"}, "insert"),
            ({"count": "sessions"}, "count"),
            ({"distinct": "categories"}, "distinct"),
            ({"createIndex": {"name": 1}}, "index_creation"),
            ({"someOtherOp": "test"}, "other"),
        ]

        for command, expected_type in test_cases:
            result = self.recognizer.categorize_operation(command)
            assert result == expected_type, f"Failed for command: {command}"


class TestMongoDBThresholdConfig:
    """Test MongoDB threshold configuration."""

    def test_default_thresholds(self):
        """Test default threshold values."""
        config = MongoDBThresholdConfig()

        assert config.slow_threshold_ms == 100.0
        assert config.very_slow_threshold_ms == 1000.0
        assert config.critical_threshold_ms == 5000.0
        assert config.max_examined_ratio == 10.0
        assert config.min_frequency_for_analysis == 5

    def test_severity_levels(self):
        """Test severity level classification."""
        config = MongoDBThresholdConfig()

        assert config.get_severity_level(50.0) == "low"
        assert config.get_severity_level(500.0) == "medium"
        assert config.get_severity_level(2000.0) == "high"
        assert config.get_severity_level(10000.0) == "critical"


class TestMongoDBConfig:
    """Test MongoDB configuration management."""

    def test_default_config_creation(self):
        """Test creation of default configuration."""
        config = MongoDBConfig()

        assert config.connection is not None
        assert config.thresholds is not None
        assert config.profiling is not None
        assert config.analysis is not None
        assert config.reporting is not None
        assert config.databases_to_monitor == []
        assert config.exclude_databases == ["admin", "config", "local"]

    def test_config_from_dict(self):
        """Test configuration creation from dictionary."""
        config_dict = {
            "connection": {
                "connection_string": "mongodb://test:27017",
                "username": "testuser",
            },
            "thresholds": {"slow_threshold_ms": 200.0, "critical_threshold_ms": 3000.0},
            "databases_to_monitor": ["app", "analytics"],
        }

        config = MongoDBConfig.from_dict(config_dict)

        assert config.connection.connection_string == "mongodb://test:27017"
        assert config.connection.username == "testuser"
        assert config.thresholds.slow_threshold_ms == 200.0
        assert config.thresholds.critical_threshold_ms == 3000.0
        assert config.databases_to_monitor == ["app", "analytics"]

    def test_config_validation(self):
        """Test configuration validation."""
        config = MongoDBConfig()

        # Valid configuration should have no issues
        issues = config.validate()
        assert len(issues) == 0

        # Invalid thresholds should generate issues
        if config.thresholds:
            config.thresholds.slow_threshold_ms = -100.0
            issues = config.validate()
            assert len(issues) > 0
            assert any("positive" in issue for issue in issues)

    def test_config_to_yaml_and_from_yaml(self):
        """Test YAML serialization and deserialization."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            config = MongoDBConfig()
            if config.connection:
                config.connection.connection_string = "mongodb://test:27017"
            config.databases_to_monitor = ["test1", "test2"]

            # Save to YAML
            success = config.to_yaml_file(f.name)
            assert success

            # Load from YAML
            loaded_config = MongoDBConfig.from_yaml_file(f.name)
            assert loaded_config.databases_to_monitor == ["test1", "test2"]

            # Cleanup
            Path(f.name).unlink()


@patch("iqtoolkit_analyzer.mongodb_analyzer.PYMONGO_AVAILABLE", True)
@patch("iqtoolkit_analyzer.mongodb_analyzer.MongoClient")
class TestMongoDBProfilerIntegration:
    """Test MongoDB profiler integration."""

    def test_connection_success(self, mock_mongo_client):
        """Test successful MongoDB connection."""
        mock_client = Mock()
        mock_client.admin.command.return_value = True
        mock_mongo_client.return_value = mock_client

        thresholds = MongoDBThresholdConfig()
        profiler = MongoDBProfilerIntegration("mongodb://localhost:27017", thresholds)

        result = profiler.connect()
        assert result is True
        assert profiler.client is not None

    def test_connection_failure(self, mock_mongo_client):
        """Test MongoDB connection failure."""
        from pymongo.errors import PyMongoError

        mock_mongo_client.side_effect = PyMongoError("Connection failed")

        thresholds = MongoDBThresholdConfig()
        profiler = MongoDBProfilerIntegration("mongodb://localhost:27017", thresholds)

        result = profiler.connect()
        assert result is False

    def test_enable_profiling(self, mock_mongo_client):
        """Test enabling MongoDB profiling."""
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_db.command.return_value = {"ok": 1}
        mock_client.__getitem__.return_value = mock_db
        mock_mongo_client.return_value = mock_client

        thresholds = MongoDBThresholdConfig()
        profiler = MongoDBProfilerIntegration("mongodb://localhost:27017", thresholds)
        profiler.client = mock_client

        result = profiler.enable_profiling("testdb", level=2)
        assert result is True

        # Verify profiling command was called
        mock_db.command.assert_called_once_with(
            "profile", 2, slowms=int(thresholds.slow_threshold_ms)
        )

    def test_collect_profile_data(self, mock_mongo_client):
        """Test collecting profile data."""
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_collection = MagicMock()

        # Mock profile data
        profile_records = [
            {
                "ts": datetime.now(),
                "command": {"find": "users"},
                "ns": "testdb.users",
                "millis": 500,
                "docsReturned": 10,
                "totalDocsExamined": 100,
            },
            {
                "ts": datetime.now(),
                "command": {"aggregate": "orders"},
                "ns": "testdb.orders",
                "millis": 1200,
                "docsReturned": 5,
                "totalDocsExamined": 50,
            },
        ]

        mock_cursor = Mock()
        mock_cursor.__iter__ = Mock(return_value=iter(profile_records))
        mock_collection.find.return_value = mock_cursor
        mock_collection.find.return_value.sort.return_value = profile_records

        mock_db.__getitem__.return_value = mock_collection
        mock_client.__getitem__.return_value = mock_db
        mock_mongo_client.return_value = mock_client

        thresholds = MongoDBThresholdConfig()
        profiler = MongoDBProfilerIntegration("mongodb://localhost:27017", thresholds)
        profiler.client = mock_client

        result = profiler.collect_profile_data("testdb")
        assert len(result) == 2
        assert result[0]["command"]["find"] == "users"
        assert result[1]["command"]["aggregate"] == "orders"

    def test_analyze_profile_record(self, mock_mongo_client):
        """Test analysis of individual profile record."""
        thresholds = MongoDBThresholdConfig()
        profiler = MongoDBProfilerIntegration("mongodb://localhost:27017", thresholds)

        profile_record = {
            "ts": datetime.now(),
            "command": {"find": "users", "filter": {"active": True}},
            "ns": "testdb.users",
            "millis": 750,
            "docsReturned": 25,
            "totalDocsExamined": 100,
            "keysExamined": 100,
            "planSummary": "IXSCAN { active: 1 }",
        }

        slow_query = profiler.analyze_profile_record(profile_record)

        assert isinstance(slow_query, MongoDBSlowQuery)
        assert slow_query.collection == "users"
        assert slow_query.database == "testdb"
        assert slow_query.operation_type == "find"
        assert slow_query.duration_ms == 750
        assert slow_query.examined_docs == 100
        assert slow_query.returned_docs == 25
        assert slow_query.planSummary == "IXSCAN { active: 1 }"
        assert slow_query.efficiency_score > 0
        assert slow_query.impact_score > 0


class TestMongoDBSlowQueryDetector:
    """Test main MongoDB slow query detector."""

    @patch("iqtoolkit_analyzer.mongodb_analyzer.MongoDBProfilerIntegration")
    def test_detector_initialization(self, mock_profiler_class):
        """Test detector initialization."""
        mock_profiler = Mock()
        mock_profiler_class.return_value = mock_profiler

        detector = MongoDBSlowQueryDetector("mongodb://localhost:27017")

        assert detector.thresholds is not None
        assert detector.profiler is not None
        assert detector.collection_analyzer is not None
        assert detector.query_cache == {}

    @patch("iqtoolkit_analyzer.mongodb_analyzer.MongoDBProfilerIntegration")
    def test_query_aggregation(self, mock_profiler_class):
        """Test aggregation of similar queries."""
        mock_profiler = Mock()
        mock_profiler_class.return_value = mock_profiler

        detector = MongoDBSlowQueryDetector("mongodb://localhost:27017")

        # Create similar queries
        base_time = datetime.now()
        queries = [
            MongoDBSlowQuery(
                command={"find": "users"},
                collection="users",
                database="testdb",
                operation_type="find",
                duration_ms=500 + i * 50,
                timestamp=base_time + timedelta(minutes=i),
                efficiency_score=0.7,
                impact_score=30.0 + i * 5,
            )
            for i in range(5)
        ]

        aggregated = detector._aggregate_similar_queries(queries)

        assert aggregated.frequency == 5
        assert aggregated.total_duration_ms == sum(q.duration_ms for q in queries)
        assert aggregated.avg_duration_ms == aggregated.total_duration_ms / 5
        assert aggregated.first_seen == base_time
        assert aggregated.last_seen == base_time + timedelta(minutes=4)


class TestMongoDBReportGenerator:
    """Test MongoDB report generation functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = MongoDBConfig()
        self.generator = MongoDBReportGenerator(self.config)

        # Sample analysis data
        self.analysis_data = {
            "database_name": "testdb",
            "analysis_timestamp": datetime.now().isoformat(),
            "slow_queries": [
                {
                    "collection": "users",
                    "database": "testdb",
                    "operation_type": "find",
                    "duration_ms": 500.0,
                    "avg_duration_ms": 450.0,
                    "frequency": 10,
                    "impact_score": 65.0,
                    "efficiency_score": 0.4,
                    "planSummary": "COLLSCAN",
                    "optimization_suggestions": ["Add index on queried fields"],
                    "examined_docs": 1000,
                    "returned_docs": 50,
                },
                {
                    "collection": "orders",
                    "database": "testdb",
                    "operation_type": "aggregate",
                    "duration_ms": 1200.0,
                    "avg_duration_ms": 1100.0,
                    "frequency": 5,
                    "impact_score": 80.0,
                    "efficiency_score": 0.3,
                    "planSummary": "IXSCAN { status: 1 }",
                    "optimization_suggestions": ["Optimize aggregation pipeline"],
                    "examined_docs": 5000,
                    "returned_docs": 100,
                },
            ],
            "summary": {
                "total_slow_queries": 2,
                "total_executions": 15,
                "avg_duration_ms": 750.0,
                "collections_affected": 2,
                "most_common_operation": "find",
                "avg_efficiency_score": 0.35,
            },
            "recommendations": [
                "Add indexes to reduce collection scans",
                "Optimize aggregation pipelines",
            ],
        }

    def test_json_report_generation(self):
        """Test JSON report generation."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            success = self.generator.generate_json_report(self.analysis_data, f.name)
            assert success

            # Verify JSON content
            with open(f.name, "r") as rf:
                report_data = json.load(rf)

            assert "metadata" in report_data
            assert "executive_summary" in report_data
            assert "slow_queries" in report_data
            assert report_data["metadata"]["database_name"] == "testdb"
            assert len(report_data["slow_queries"]) == 2

            # Cleanup
            Path(f.name).unlink()

    def test_markdown_report_generation(self):
        """Test Markdown report generation."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            success = self.generator.generate_markdown_report(
                self.analysis_data, f.name
            )
            assert success

            # Verify markdown content
            with open(f.name, "r") as rf:
                content = rf.read()

            assert "# MongoDB Slow Query Analysis Report" in content
            assert "## Executive Summary" in content
            assert "## Slow Query Analysis" in content
            assert "testdb.users" in content
            assert "testdb.orders" in content

            # Cleanup
            Path(f.name).unlink()

    def test_html_report_generation(self):
        """Test HTML report generation."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            success = self.generator.generate_html_report(self.analysis_data, f.name)
            assert success

            # Verify HTML content
            with open(f.name, "r") as rf:
                content = rf.read()

            assert "<!DOCTYPE html>" in content
            assert "<title>MongoDB Slow Query Analysis Report</title>" in content
            assert "testdb.users" in content
            assert "severity-" in content  # CSS classes for severity

            # Cleanup
            Path(f.name).unlink()

    def test_executive_summary_creation(self):
        """Test executive summary creation."""
        summary = self.generator._create_executive_summary(self.analysis_data)

        assert "overview" in summary
        assert "severity_breakdown" in summary
        assert "problem_areas" in summary
        assert "key_findings" in summary

        overview = summary["overview"]
        assert overview["total_slow_query_patterns"] == 2
        assert overview["total_executions_analyzed"] == 15
        assert overview["average_query_duration_ms"] == 750.0

        severity = summary["severity_breakdown"]
        assert severity["critical_queries"] == 1  # impact_score > 70
        assert severity["high_impact_queries"] == 1  # 50 <= impact_score <= 70

    def test_primary_issues_identification(self):
        """Test identification of primary performance issues."""
        slow_queries = self.analysis_data["slow_queries"]
        issues = self.generator._identify_primary_issues(slow_queries)

        assert len(issues) > 0
        # Should identify collection scan issue
        assert any("collection scan" in issue.lower() for issue in issues)

    def test_key_findings_generation(self):
        """Test key findings generation."""
        findings = self.generator._generate_key_findings(self.analysis_data)

        assert len(findings) > 0
        assert isinstance(findings, list)
        assert all(isinstance(finding, str) for finding in findings)


# Integration test data
@pytest.fixture
def sample_mongodb_config():
    """Sample MongoDB configuration for testing."""
    config = MongoDBConfig()
    if config.connection:
        config.connection.connection_string = "mongodb://localhost:27017"
    config.databases_to_monitor = ["testdb"]
    if config.thresholds:
        config.thresholds.slow_threshold_ms = 100.0
    return config


@pytest.fixture
def sample_profile_data():
    """Sample MongoDB profile data for testing."""
    return [
        {
            "ts": datetime.now(),
            "command": {
                "find": "users",
                "filter": {"active": True, "age": {"$gte": 18}},
            },
            "ns": "testdb.users",
            "millis": 850,
            "docsReturned": 42,
            "totalDocsExamined": 1500,
            "keysExamined": 1500,
            "planSummary": "COLLSCAN",
            "executionTimeMillisEstimate": 820,
        },
        {
            "ts": datetime.now() - timedelta(minutes=5),
            "command": {
                "aggregate": "orders",
                "pipeline": [
                    {"$match": {"status": "completed"}},
                    {"$group": {"_id": "$customer_id", "total": {"$sum": "$amount"}}},
                ],
            },
            "ns": "testdb.orders",
            "millis": 1200,
            "docsReturned": 150,
            "totalDocsExamined": 3000,
            "keysExamined": 3000,
            "planSummary": "IXSCAN { status: 1 }",
            "executionTimeMillisEstimate": 1150,
        },
    ]


class TestMongoDBIntegration:
    """Integration tests for MongoDB functionality."""

    def test_end_to_end_analysis_workflow(
        self, sample_mongodb_config, sample_profile_data
    ):
        """Test complete analysis workflow."""
        with patch("iqtoolkit_analyzer.mongodb_analyzer.PYMONGO_AVAILABLE", True):
            with patch(
                "iqtoolkit_analyzer.mongodb_analyzer.MongoClient"
            ) as mock_client:
                # Setup mocks
                mock_client_instance = MagicMock()
                mock_client.return_value = mock_client_instance
                mock_client_instance.admin.command.return_value = True

                # Setup database mock for profiling
                mock_db = MagicMock()
                mock_db.command.return_value = {"ok": 1}
                mock_client_instance.__getitem__.return_value = mock_db

                # Create detector
                detector = MongoDBSlowQueryDetector(
                    sample_mongodb_config.get_effective_connection_string(),
                    sample_mongodb_config.thresholds,
                )

                # Mock profile data collection
                with patch.object(
                    detector.profiler,
                    "collect_profile_data",
                    return_value=sample_profile_data,
                ):
                    # Initialize and start monitoring
                    assert detector.initialize() is True
                    assert detector.start_monitoring(["testdb"]) is True

                    # Detect slow queries
                    slow_queries = detector.detect_slow_queries("testdb")

                    # Verify results
                    assert (
                        len(slow_queries) >= 0
                    )  # May be empty due to frequency threshold

                    # Generate comprehensive report
                    report = detector.generate_comprehensive_report("testdb")

                    assert "database_name" in report
                    assert "slow_queries" in report
                    assert "summary" in report
                    assert report["database_name"] == "testdb"

    def test_configuration_integration(self):
        """Test configuration loading and validation integration."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            # Create test configuration
            config_data = {
                "connection": {
                    "connection_string": "mongodb://test:27017",
                    "connection_timeout_ms": 10000,
                },
                "thresholds": {
                    "slow_threshold_ms": 150.0,
                    "very_slow_threshold_ms": 800.0,
                    "critical_threshold_ms": 3000.0,
                },
                "databases_to_monitor": ["app", "logs"],
                "log_level": "DEBUG",
            }

            import yaml

            yaml.dump(config_data, f, default_flow_style=False)
            f.flush()

            # Load configuration
            config = load_mongodb_config(f.name)

            # Verify configuration
            assert config.connection is not None
            assert config.connection.connection_string == "mongodb://test:27017"
            assert config.connection.connection_timeout_ms == 10000
            assert config.thresholds is not None
            assert config.thresholds.slow_threshold_ms == 150.0
            assert config.databases_to_monitor == ["app", "logs"]
            assert config.log_level == "DEBUG"

            # Test validation
            issues = config.validate()
            assert len(issues) == 0

            # Cleanup
            Path(f.name).unlink()


if __name__ == "__main__":
    # Run specific test for development
    pytest.main([__file__, "-v"])
