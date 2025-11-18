# MongoDB Slow Query Detection Guide

This guide provides comprehensive information on using the Slow Query Doctor for MongoDB performance analysis and optimization.

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Configuration](#configuration)
4. [Usage Examples](#usage-examples)
5. [Analysis Features](#analysis-features)
6. [Report Formats](#report-formats)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

## Overview

The MongoDB Slow Query Doctor provides comprehensive analysis of MongoDB query performance by:

- **Profiler Integration**: Connects to MongoDB's built-in profiler to collect query execution data
- **Pattern Recognition**: Groups similar queries and identifies common performance issues
- **Impact Analysis**: Calculates performance impact scores based on execution time, frequency, and resource usage
- **Optimization Suggestions**: Provides specific recommendations for improving query performance
- **Collection Analysis**: Analyzes collection-level performance characteristics and index usage
- **Comprehensive Reporting**: Generates detailed reports in multiple formats (JSON, HTML, Markdown)

### Key Features

- ✅ **Real-time Monitoring**: Continuous monitoring of slow queries
- ✅ **Intelligent Grouping**: Groups similar query patterns for focused analysis
- ✅ **Index Optimization**: Detects missing indexes and collection scans
- ✅ **Aggregation Analysis**: Specialized analysis for aggregation pipelines
- ✅ **Multi-format Reports**: JSON, HTML, and Markdown report generation
- ✅ **Threshold Configuration**: Customizable performance thresholds
- ✅ **Collection Insights**: Per-collection performance analysis

## Quick Start

### 1. Install Dependencies

```bash
# Install required MongoDB dependencies
pip install pymongo

# Install optional visualization dependencies
pip install matplotlib  # For chart generation
```

### 2. Create Configuration

```bash
# Create a sample configuration file
python -m slowquerydoctor.mongodb_cli config create --output mongodb_config.yml
```

### 3. Configure MongoDB Connection

Edit `mongodb_config.yml`:

```yaml
connection:
  connection_string: "mongodb://localhost:27017"
  # Add authentication if needed
  # username: "your_username"
  # password: "your_password"

databases_to_monitor:
  - "your_database_name"

thresholds:
  slow_threshold_ms: 100.0
  critical_threshold_ms: 5000.0
```

### 4. Test Connection

```bash
python -m slowquerydoctor.mongodb_cli test-connection --config mongodb_config.yml
```

### 5. Run Analysis

```bash
# Single analysis
python -m slowquerydoctor.mongodb_cli analyze --config mongodb_config.yml --database myapp

# With HTML report generation
python -m slowquerydoctor.mongodb_cli analyze --config mongodb_config.yml --database myapp --output ./reports --format html

# Continuous monitoring
python -m slowquerydoctor.mongodb_cli monitor --config mongodb_config.yml --interval 5
```

## Configuration

### Connection Settings

```yaml
connection:
  connection_string: "mongodb://localhost:27017"
  connection_timeout_ms: 5000
  username: "monitoring_user"  # Optional
  password: "password"         # Optional
  auth_source: "admin"         # Optional
  use_ssl: true               # Optional
```

### Performance Thresholds

```yaml
thresholds:
  slow_threshold_ms: 100.0          # Queries slower than 100ms
  very_slow_threshold_ms: 1000.0    # Very slow threshold  
  critical_threshold_ms: 5000.0     # Critical threshold
  max_examined_ratio: 10.0          # Max examined/returned ratio
  min_frequency_for_analysis: 5     # Minimum frequency for analysis
```

### Profiling Configuration

```yaml
profiling:
  profiling_level: 1              # 0=off, 1=slow ops, 2=all ops
  enable_on_startup: true
  sample_rate: 1.0               # 1.0 = 100%, 0.1 = 10%
  profile_data_retention_hours: 24
```

### Analysis Options

```yaml
analysis:
  normalize_queries: true
  group_similar_queries: true
  analyze_collections: true
  analyze_index_usage: true
  suggest_new_indexes: true
  include_query_examples: true
```

## Usage Examples

### Command Line Interface

#### Basic Analysis

```bash
# Analyze specific database
python -m slowquerydoctor.mongodb_cli analyze --database myapp

# Analyze with custom config
python -m slowquerydoctor.mongodb_cli analyze --config my_config.yml --database myapp

# Enable profiling before analysis
python -m slowquerydoctor.mongodb_cli analyze --database myapp --enable-profiling
```

#### Report Generation

```bash
# Generate JSON report
python -m slowquerydoctor.mongodb_cli analyze --database myapp --output ./reports --format json

# Generate HTML report
python -m slowquerydoctor.mongodb_cli analyze --database myapp --output ./reports --format html

# Generate multiple formats
python -m slowquerydoctor.mongodb_cli analyze --database myapp --output ./reports --format json html markdown
```

#### Continuous Monitoring

```bash
# Monitor with 5-minute intervals
python -m slowquerydoctor.mongodb_cli monitor --database myapp --interval 5

# Monitor multiple databases
python -m slowquerydoctor.mongodb_cli monitor --config config.yml --interval 10
```

### Programmatic Usage

#### Basic Analysis

```python
from slowquerydoctor.mongodb_analyzer import MongoDBSlowQueryDetector
from slowquerydoctor.mongodb_config import MongoDBConfig

# Load configuration
config = MongoDBConfig.from_yaml_file('mongodb_config.yml')

# Create detector
detector = MongoDBSlowQueryDetector(
    config.get_effective_connection_string(),
    config.thresholds
)

# Initialize and analyze
if detector.initialize():
    slow_queries = detector.detect_slow_queries('myapp', time_window_minutes=60)
    
    for query in slow_queries:
        print(f"Slow query in {query.collection}:")
        print(f"  Duration: {query.avg_duration_ms:.1f}ms")
        print(f"  Frequency: {query.frequency}")
        print(f"  Impact Score: {query.impact_score:.1f}/100")
```

#### Report Generation

```python
from slowquerydoctor.mongodb_report_generator import MongoDBReportGenerator

# Generate comprehensive report
report = detector.generate_comprehensive_report('myapp')

# Create report generator
generator = MongoDBReportGenerator(config)

# Generate HTML report
generator.generate_html_report(report, 'analysis_report.html')

# Generate charts
chart_files = generator.generate_charts(report, './charts')
print(f"Generated charts: {chart_files}")
```

## Analysis Features

### Query Pattern Recognition

The system automatically identifies and groups similar queries:

```javascript
// These queries are grouped as the same pattern:
db.users.find({name: "John", age: 25})
db.users.find({name: "Jane", age: 30}) 
db.users.find({name: "Bob", age: 45})

// Normalized pattern: {find: "?", filter: {name: "?", age: "?"}}
```

### Performance Metrics

Each query pattern includes comprehensive metrics:

- **Duration Metrics**: Average, minimum, maximum execution time
- **Frequency**: Number of executions in the analysis window
- **Efficiency Score**: Based on examined/returned document ratio
- **Impact Score**: Weighted score considering duration, frequency, and resource usage
- **Index Usage**: Execution plan analysis and index utilization

### Collection-Level Analysis

Per-collection insights include:

- Document count and storage size
- Index count and utilization
- Query patterns and performance
- Optimization recommendations

### Optimization Suggestions

Automated suggestions for:

- **Missing Indexes**: Identifies fields that would benefit from indexing
- **Collection Scans**: Detects queries scanning entire collections
- **Inefficient Queries**: High examined/returned document ratios
- **Aggregation Optimization**: Pipeline stage ordering and optimization
- **Query Restructuring**: Suggestions for query improvements

## Report Formats

### JSON Report

Structured data format ideal for programmatic processing:

```json
{
  "metadata": {
    "generated_at": "2025-11-15T10:30:00Z",
    "database_name": "myapp",
    "tool_version": "1.0.0"
  },
  "executive_summary": {
    "overview": {
      "total_slow_query_patterns": 15,
      "total_executions_analyzed": 1250,
      "average_query_duration_ms": 450.2,
      "collections_affected": 8
    },
    "severity_breakdown": {
      "critical_queries": 3,
      "high_impact_queries": 7,
      "medium_impact_queries": 5
    }
  },
  "slow_queries": [...],
  "recommendations": [...]
}
```

### HTML Report

Interactive web-based report with:

- Executive summary dashboard
- Sortable query analysis table
- Severity indicators and color coding
- Detailed optimization suggestions
- Collection performance overview

### Markdown Report

Human-readable format perfect for documentation:

```markdown
# MongoDB Slow Query Analysis Report

## Executive Summary

- **Total Slow Query Patterns:** 15
- **Average Query Duration:** 450.2ms
- **Collections Affected:** 8

### Key Findings

- High percentage of collection scans detected
- Several queries with low efficiency scores
- Aggregation operations dominate slow queries
```

## Best Practices

### Configuration

1. **Set Appropriate Thresholds**
   ```yaml
   thresholds:
     # Development
     slow_threshold_ms: 50.0
     
     # Production  
     slow_threshold_ms: 200.0
   ```

2. **Use Sampling in High-Traffic Environments**
   ```yaml
   profiling:
     sample_rate: 0.1  # Sample 10% of operations
   ```

3. **Configure Retention Periods**
   ```yaml
   profiling:
     profile_data_retention_hours: 24
     auto_cleanup_enabled: true
   ```

### Monitoring Strategy

1. **Regular Analysis**: Run weekly comprehensive analysis
2. **Continuous Monitoring**: Use monitoring mode for critical systems
3. **Threshold Tuning**: Adjust thresholds based on application requirements
4. **Index Monitoring**: Regular review of index recommendations

### Performance Optimization Workflow

1. **Identify Critical Queries**: Focus on high-impact queries first
2. **Analyze Execution Plans**: Review planSummary for optimization opportunities
3. **Implement Indexes**: Add recommended indexes
4. **Validate Improvements**: Re-run analysis to measure improvements
5. **Monitor Changes**: Continuous monitoring to catch regressions

## Troubleshooting

### Common Issues

#### Connection Problems

```bash
# Test connection
python -m slowquerydoctor.mongodb_cli test-connection --config config.yml

# Check configuration
python -m slowquerydoctor.mongodb_cli config validate --config config.yml
```

#### Profiling Issues

1. **Insufficient Permissions**
   ```javascript
   // Grant profiling permissions
   db.grantRolesToUser("monitoring_user", ["dbAdmin"])
   ```

2. **Profiling Not Enabled**
   ```javascript
   // Check profiling status
   db.getProfilingStatus()
   
   // Enable profiling
   db.setProfilingLevel(1, { slowms: 100 })
   ```

#### No Slow Queries Detected

1. Check if profiling is enabled and collecting data
2. Verify threshold settings are appropriate
3. Ensure sufficient analysis time window
4. Check if queries meet minimum frequency requirements

#### Memory Issues

For large datasets:

```yaml
analysis:
  max_collections_to_analyze: 20  # Limit collection analysis
  
profiling:
  sample_rate: 0.1  # Reduce sampling rate
  profile_collection_size_mb: 50  # Smaller profile collection
```

### Debug Mode

Enable verbose logging for troubleshooting:

```bash
python -m slowquerydoctor.mongodb_cli analyze --database myapp --verbose
```

Or in configuration:

```yaml
log_level: "DEBUG"
log_file: "/tmp/mongodb-slow-query-debug.log"
```

### Performance Tuning

For optimal performance:

1. **Limit Analysis Scope**
   ```yaml
   databases_to_monitor: ["critical_db"]  # Focus on critical databases
   analysis:
     max_collections_to_analyze: 10
   ```

2. **Optimize Thresholds**
   ```yaml
   thresholds:
     min_frequency_for_analysis: 10  # Higher frequency threshold
     time_window_minutes: 30         # Shorter time window
   ```

3. **Use Appropriate Sampling**
   ```yaml
   profiling:
     sample_rate: 0.05  # 5% sampling for high-volume systems
   ```

## Advanced Usage

### Custom Analysis Scripts

```python
from slowquerydoctor.mongodb_analyzer import MongoDBSlowQueryDetector
from slowquerydoctor.mongodb_config import MongoDBThresholdConfig

# Custom thresholds
thresholds = MongoDBThresholdConfig(
    slow_threshold_ms=50.0,
    critical_threshold_ms=1000.0,
    min_frequency_for_analysis=3
)

# Custom analysis
detector = MongoDBSlowQueryDetector("mongodb://localhost:27017", thresholds)
if detector.initialize():
    # Analyze last 2 hours
    queries = detector.detect_slow_queries("myapp", time_window_minutes=120)
    
    # Filter for specific collections
    user_queries = [q for q in queries if q.collection == "users"]
    
    # Custom reporting
    for query in user_queries:
        if query.impact_score > 50:
            print(f"High-impact query: {query.operation_type}")
            print(f"Suggestions: {', '.join(query.optimization_suggestions)}")
```

### Integration with Monitoring Systems

```python
# Integration example for alerting systems
def check_critical_queries(database_name: str) -> bool:
    detector = MongoDBSlowQueryDetector(connection_string, thresholds)
    if detector.initialize():
        queries = detector.detect_slow_queries(database_name, 15)  # Last 15 minutes
        critical_queries = [q for q in queries if q.impact_score > 80]
        
        if critical_queries:
            # Send alert
            send_alert(f"Critical slow queries detected in {database_name}")
            return False
    return True
```

For more examples and advanced usage patterns, see the [examples](examples.md) documentation.