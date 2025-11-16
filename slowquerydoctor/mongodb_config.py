"""
MongoDB Configuration Module

This module provides configuration management for MongoDB slow query detection,
including threshold configuration, connection settings, and analysis parameters.
"""

import logging
import os
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional
import yaml

logger = logging.getLogger(__name__)


@dataclass
class MongoDBConnectionConfig:
    """MongoDB connection configuration."""

    connection_string: str = "mongodb://localhost:27017"
    connection_timeout_ms: int = 5000
    server_selection_timeout_ms: int = 5000
    socket_timeout_ms: int = 30000
    max_pool_size: int = 100

    # Authentication
    username: Optional[str] = None
    password: Optional[str] = None
    auth_source: str = "admin"

    # SSL/TLS
    use_ssl: bool = False
    ssl_cert_file: Optional[str] = None
    ssl_key_file: Optional[str] = None
    ssl_ca_file: Optional[str] = None

    def to_mongo_uri(self) -> str:
        """Convert configuration to MongoDB URI."""
        if self.username and self.password:
            auth_part = f"{self.username}:{self.password}@"
            base_uri = self.connection_string.replace(
                "mongodb://", f"mongodb://{auth_part}"
            )
        else:
            base_uri = self.connection_string

        # Add connection options
        options: List[str] = []
        if self.connection_timeout_ms != 5000:
            options.append(f"connectTimeoutMS={self.connection_timeout_ms}")
        if self.server_selection_timeout_ms != 5000:
            options.append(
                f"serverSelectionTimeoutMS={self.server_selection_timeout_ms}"
            )
        if self.socket_timeout_ms != 30000:
            options.append(f"socketTimeoutMS={self.socket_timeout_ms}")
        if self.max_pool_size != 100:
            options.append(f"maxPoolSize={self.max_pool_size}")
        if self.auth_source != "admin":
            options.append(f"authSource={self.auth_source}")
        if self.use_ssl:
            options.append("ssl=true")

        if options:
            connector = "&" if "?" in base_uri else "?"
            base_uri += connector + "&".join(options)

        return base_uri


@dataclass
class MongoDBThresholdConfig:
    """MongoDB performance threshold configuration."""

    # Duration thresholds (milliseconds)
    slow_threshold_ms: float = 100.0
    very_slow_threshold_ms: float = 1000.0
    critical_threshold_ms: float = 5000.0

    # Document examination thresholds
    max_examined_ratio: float = 10.0  # examined/returned ratio
    max_examined_docs: int = 100000

    # Collection scan detection
    detect_collection_scans: bool = True
    max_collection_scan_docs: int = 1000

    # Index usage thresholds
    require_index_usage: bool = True
    min_index_hit_ratio: float = 0.95

    # Frequency thresholds for pattern analysis
    min_frequency_for_analysis: int = 5
    time_window_minutes: int = 60

    # Resource usage thresholds
    max_cpu_time_ms: float = 1000.0
    max_memory_usage_mb: float = 100.0

    # Analysis scoring weights
    duration_weight: float = 0.4
    efficiency_weight: float = 0.3
    frequency_weight: float = 0.2
    impact_weight: float = 0.1

    def get_severity_level(self, duration_ms: float) -> str:
        """Get severity level based on duration."""
        if duration_ms >= self.critical_threshold_ms:
            return "critical"
        elif duration_ms >= self.very_slow_threshold_ms:
            return "high"
        elif duration_ms >= self.slow_threshold_ms:
            return "medium"
        else:
            return "low"


@dataclass
class MongoDBProfilingConfig:
    """MongoDB profiling configuration."""

    # Profiling settings
    profiling_level: int = 1  # 0=off, 1=slow ops, 2=all ops
    enable_on_startup: bool = True

    # Collection settings
    profile_collection_size_mb: int = 100
    profile_collection_max_docs: int = 1000000

    # Data retention
    profile_data_retention_hours: int = 24
    auto_cleanup_enabled: bool = True

    # Sampling
    sample_rate: float = 1.0  # 1.0 = 100%, 0.1 = 10%

    # Operation filtering
    include_operations: Optional[List[str]] = None
    exclude_operations: Optional[List[str]] = None

    def __post_init__(self) -> None:
        """Initialize default values."""
        if self.include_operations is None:
            self.include_operations = [
                "find",
                "aggregate",
                "update",
                "delete",
                "insert",
                "count",
                "distinct",
                "createIndex",
            ]

        if self.exclude_operations is None:
            self.exclude_operations = ["ping", "buildInfo", "serverStatus"]


@dataclass
class MongoDBAnalysisConfig:
    """MongoDB analysis configuration."""

    # Query pattern recognition
    normalize_queries: bool = True
    group_similar_queries: bool = True
    similarity_threshold: float = 0.8

    # Collection analysis
    analyze_collections: bool = True
    max_collections_to_analyze: int = 50
    skip_system_collections: bool = True

    # Index analysis
    analyze_index_usage: bool = True
    suggest_new_indexes: bool = True
    detect_unused_indexes: bool = True

    # Aggregation pipeline analysis
    analyze_pipeline_stages: bool = True
    suggest_pipeline_optimizations: bool = True

    # Report generation
    include_query_examples: bool = True
    max_query_examples: int = 5
    truncate_large_queries: bool = True
    max_query_length: int = 1000

    # Performance impact calculation
    calculate_impact_scores: bool = True
    include_efficiency_metrics: bool = True

    # Machine learning features (future enhancement)
    enable_ml_pattern_detection: bool = False
    ml_model_path: Optional[str] = None


@dataclass
class MongoDBReportingConfig:
    """MongoDB reporting configuration."""

    # Report formats
    supported_formats: Optional[List[str]] = None
    default_format: str = "json"

    # Report content
    include_executive_summary: bool = True
    include_detailed_analysis: bool = True
    include_optimization_suggestions: bool = True
    include_collection_stats: bool = True

    # Visualization
    generate_charts: bool = False
    chart_library: str = "matplotlib"  # matplotlib, plotly

    # Export options
    export_raw_data: bool = False
    compress_reports: bool = False

    # Scheduling
    auto_generate_reports: bool = False
    report_schedule_cron: str = "0 6 * * 1"  # Weekly on Monday at 6 AM

    def __post_init__(self) -> None:
        """Initialize default values."""
        if self.supported_formats is None:
            self.supported_formats = ["json", "yaml", "html", "markdown"]


@dataclass
class MongoDBConfig:
    """Complete MongoDB configuration."""

    connection: Optional[MongoDBConnectionConfig] = None
    thresholds: Optional[MongoDBThresholdConfig] = None
    profiling: Optional[MongoDBProfilingConfig] = None
    analysis: Optional[MongoDBAnalysisConfig] = None
    reporting: Optional[MongoDBReportingConfig] = None

    # Database settings
    databases_to_monitor: Optional[List[str]] = None
    exclude_databases: Optional[List[str]] = None

    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = None

    def __post_init__(self) -> None:
        """Initialize default configurations."""
        if self.connection is None:
            self.connection = MongoDBConnectionConfig()
        if self.thresholds is None:
            self.thresholds = MongoDBThresholdConfig()
        if self.profiling is None:
            self.profiling = MongoDBProfilingConfig()
        if self.analysis is None:
            self.analysis = MongoDBAnalysisConfig()
        if self.reporting is None:
            self.reporting = MongoDBReportingConfig()

        if self.databases_to_monitor is None:
            self.databases_to_monitor = []

        if self.exclude_databases is None:
            self.exclude_databases = ["admin", "config", "local"]

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "MongoDBConfig":
        """Create configuration from dictionary."""
        connection_dict = config_dict.get("connection", {})
        connection = MongoDBConnectionConfig(**connection_dict)

        thresholds_dict = config_dict.get("thresholds", {})
        thresholds = MongoDBThresholdConfig(**thresholds_dict)

        profiling_dict = config_dict.get("profiling", {})
        profiling = MongoDBProfilingConfig(**profiling_dict)

        analysis_dict = config_dict.get("analysis", {})
        analysis = MongoDBAnalysisConfig(**analysis_dict)

        reporting_dict = config_dict.get("reporting", {})
        reporting = MongoDBReportingConfig(**reporting_dict)

        # Create main config
        config = cls(
            connection=connection,
            thresholds=thresholds,
            profiling=profiling,
            analysis=analysis,
            reporting=reporting,
            databases_to_monitor=config_dict.get("databases_to_monitor", []),
            exclude_databases=config_dict.get(
                "exclude_databases", ["admin", "config", "local"]
            ),
            log_level=config_dict.get("log_level", "INFO"),
            log_file=config_dict.get("log_file"),
        )

        return config

    @classmethod
    def from_yaml_file(cls, file_path: str) -> "MongoDBConfig":
        """Load configuration from YAML file."""
        try:
            with open(file_path, "r") as f:
                config_dict = yaml.safe_load(f)
            return cls.from_dict(config_dict)
        except FileNotFoundError:
            logger.warning(f"Configuration file not found: {file_path}")
            return cls()  # Return default configuration
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML configuration: {e}")
            return cls()
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return cls()

    @classmethod
    def from_environment(cls) -> "MongoDBConfig":
        """Create configuration from environment variables."""
        config = cls()

        # Connection settings
        if os.getenv("MONGODB_URI") and config.connection:
            uri = os.getenv("MONGODB_URI")
            if uri:
                config.connection.connection_string = uri
        if os.getenv("MONGODB_USERNAME") and config.connection:
            config.connection.username = os.getenv("MONGODB_USERNAME")
        if os.getenv("MONGODB_PASSWORD") and config.connection:
            config.connection.password = os.getenv("MONGODB_PASSWORD")
        if os.getenv("MONGODB_AUTH_SOURCE") and config.connection:
            auth_source = os.getenv("MONGODB_AUTH_SOURCE")
            if auth_source:
                config.connection.auth_source = auth_source

        # Threshold settings
        if os.getenv("MONGODB_SLOW_THRESHOLD_MS") and config.thresholds:
            threshold_str = os.getenv("MONGODB_SLOW_THRESHOLD_MS")
            if threshold_str:
                config.thresholds.slow_threshold_ms = float(threshold_str)
        if os.getenv("MONGODB_CRITICAL_THRESHOLD_MS") and config.thresholds:
            threshold_str = os.getenv("MONGODB_CRITICAL_THRESHOLD_MS")
            if threshold_str:
                config.thresholds.critical_threshold_ms = float(threshold_str)

        # Profiling settings
        if os.getenv("MONGODB_PROFILING_LEVEL") and config.profiling:
            level_str = os.getenv("MONGODB_PROFILING_LEVEL")
            if level_str:
                config.profiling.profiling_level = int(level_str)

        # Database settings
        if os.getenv("MONGODB_DATABASES"):
            databases_str = os.getenv("MONGODB_DATABASES")
            if databases_str:
                config.databases_to_monitor = databases_str.split(",")

        # Logging
        if os.getenv("MONGODB_LOG_LEVEL"):
            config.log_level = os.getenv("MONGODB_LOG_LEVEL") or "INFO"
        if os.getenv("MONGODB_LOG_FILE"):
            config.log_file = os.getenv("MONGODB_LOG_FILE")

        return config

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "connection": asdict(self.connection) if self.connection else {},
            "thresholds": asdict(self.thresholds) if self.thresholds else {},
            "profiling": asdict(self.profiling) if self.profiling else {},
            "analysis": asdict(self.analysis) if self.analysis else {},
            "reporting": asdict(self.reporting) if self.reporting else {},
            "databases_to_monitor": self.databases_to_monitor or [],
            "exclude_databases": self.exclude_databases or [],
            "log_level": self.log_level,
            "log_file": self.log_file,
        }

    def to_yaml_file(self, file_path: str) -> bool:
        """Save configuration to YAML file."""
        try:
            with open(file_path, "w") as f:
                yaml.dump(self.to_dict(), f, default_flow_style=False, indent=2)
            logger.info(f"Configuration saved to: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False

    def validate(self) -> List[str]:
        """Validate configuration and return list of issues."""
        issues: List[str] = []

        # Validate connection
        if self.connection and not self.connection.connection_string:
            issues.append("Connection string is required")

        # Validate thresholds
        if self.thresholds:
            if self.thresholds.slow_threshold_ms <= 0:
                issues.append("Slow threshold must be positive")
            if (
                self.thresholds.very_slow_threshold_ms
                <= self.thresholds.slow_threshold_ms
            ):
                issues.append("Very slow threshold must be greater than slow threshold")
            if (
                self.thresholds.critical_threshold_ms
                <= self.thresholds.very_slow_threshold_ms
            ):
                issues.append(
                    "Critical threshold must be greater than very slow threshold"
                )

        # Validate profiling
        if self.profiling:
            if self.profiling.profiling_level not in [0, 1, 2]:
                issues.append("Profiling level must be 0, 1, or 2")
            if self.profiling.sample_rate < 0 or self.profiling.sample_rate > 1:
                issues.append("Sample rate must be between 0 and 1")

        # Validate analysis
        if self.analysis:
            if (
                self.analysis.similarity_threshold < 0
                or self.analysis.similarity_threshold > 1
            ):
                issues.append("Similarity threshold must be between 0 and 1")

        # Validate reporting
        if self.reporting and self.reporting.supported_formats:
            if self.reporting.default_format not in self.reporting.supported_formats:
                issues.append("Default format must be in supported formats")

        return issues

    def get_effective_connection_string(self) -> str:
        """Get the effective connection string with all options."""
        if self.connection:
            return self.connection.to_mongo_uri()
        return "mongodb://localhost:27017"


def load_mongodb_config(config_file: Optional[str] = None) -> MongoDBConfig:
    """
    Load MongoDB configuration from various sources.

    Priority order:
    1. Specified config file
    2. Environment variables
    3. Default values

    Args:
        config_file: Path to configuration file

    Returns:
        MongoDBConfig instance
    """
    if config_file and os.path.exists(config_file):
        logger.info(f"Loading configuration from file: {config_file}")
        config = MongoDBConfig.from_yaml_file(config_file)
    else:
        logger.info("Loading configuration from environment variables")
        config = MongoDBConfig.from_environment()

    # Validate configuration
    issues = config.validate()
    if issues:
        logger.warning("Configuration validation issues found:")
        for issue in issues:
            logger.warning(f"  - {issue}")

    logger.info("MongoDB configuration loaded successfully")
    if config.connection:
        logger.debug(f"Connection string: {config.connection.connection_string}")
    logger.debug(f"Databases to monitor: {config.databases_to_monitor}")
    if config.thresholds:
        logger.debug(f"Slow threshold: {config.thresholds.slow_threshold_ms}ms")

    return config


def create_sample_config_file(file_path: str) -> bool:
    """Create a sample configuration file with all options."""
    sample_config = MongoDBConfig()

    # Customize sample values
    if sample_config.connection:
        sample_config.connection.connection_string = "mongodb://localhost:27017"
    sample_config.databases_to_monitor = ["myapp", "analytics"]
    if sample_config.thresholds:
        sample_config.thresholds.slow_threshold_ms = 200.0
    if sample_config.profiling:
        sample_config.profiling.enable_on_startup = True
    if sample_config.analysis:
        sample_config.analysis.analyze_collections = True
    if sample_config.reporting:
        sample_config.reporting.include_executive_summary = True

    return sample_config.to_yaml_file(file_path)


if __name__ == "__main__":
    # Example usage
    print("Creating sample MongoDB configuration...")

    # Create sample configuration
    if create_sample_config_file("mongodb_config.yml"):
        print("Sample configuration created: mongodb_config.yml")

    # Load and display configuration
    config = load_mongodb_config("mongodb_config.yml")
    print(f"Loaded configuration for databases: {config.databases_to_monitor}")
    if config.thresholds:
        print(f"Slow threshold: {config.thresholds.slow_threshold_ms}ms")
