# MongoDB Sample Logs

This directory contains sample MongoDB slow query logs for testing and development of the MongoDB analyzer (v0.2.0).

## MongoDB Slow Query Logging Setup

### Enable MongoDB Profiling

MongoDB uses the database profiler to log slow operations. Configure it to capture slow queries:

```javascript
// Enable profiling for operations slower than 100ms
db.setProfilingLevel(2, { slowms: 100 })

// Check current profiling status
db.getProfilingStatus()

// Query the profiler collection
db.system.profile.find().limit(5).sort({ ts: -1 }).pretty()
```

### Configuration Options

```javascript
// Profile only slow operations (recommended for production)
db.setProfilingLevel(1, { slowms: 1000 })  // Log operations > 1 second

// Profile all operations (use with caution)
db.setProfilingLevel(2)

// Disable profiling
db.setProfilingLevel(0)
```

## Sample Log Files

### Coming in v0.2.0 Development

- `mongodb-slow-queries-sample.json` - Sample profiler collection output
- `mongodb-aggregation-slow.json` - Aggregation pipeline slow operations
- `mongodb-index-missing.json` - Queries that would benefit from indexes

## MongoDB Slow Query Analysis Features (v0.2.0)

### Planned Analysis Capabilities

1. **Aggregation Pipeline Optimization**
   - Pipeline stage analysis
   - Index usage recommendations
   - Stage reordering suggestions

2. **Index Strategy Analysis**
   - Missing index detection
   - Compound index recommendations
   - Index usage statistics

3. **Query Pattern Detection**
   - Collection scan identification
   - Inefficient regex patterns
   - Large result set queries

4. **Document Structure Analysis**
   - Schema optimization suggestions
   - Embedded vs referenced document recommendations

## Supported MongoDB Log Formats

### Profiler Collection Output (JSON)
- Direct query from `db.system.profile`
- Structured JSON format with timing data
- Includes execution stats and query plans

### MongoDB Log Files (v0.2.0+)
- Standard MongoDB log files with slow query entries
- JSON format with structured data
- Includes operation type, database, collection info

## Contributing MongoDB Requirements

We're actively developing MongoDB support! Help us by:

1. **Sharing sample logs**: Anonymized slow query logs from your MongoDB instances
2. **Optimization needs**: What MongoDB performance issues do you face most?
3. **Log formats**: What log formats does your MongoDB setup use?

**Contribute:** [File a MongoDB feedback issue](https://github.com/iqtoolkit/slow-query-doctor/issues/new?labels=mongodb-feedback&title=MongoDB%20Requirements)

---

**Status**: 🚧 **Priority Development for v0.2.0** (Nov 2025 - Q1 2026)