# SQL Server Sample Logs

**Status**: 🚧 Coming in v0.4.0 (Q3 2026)

This directory will contain sample SQL Server Extended Events and performance log files for testing and demonstration purposes.

## Planned SQL Server Log Support

### Extended Events Format
```xml
<event name="sql_statement_completed" package="sqlserver" timestamp="2025-10-28T19:31:23.123456Z">
  <data name="duration">
    <type name="uint64" />
    <value>15123456</value>
  </data>
  <data name="cpu_time">
    <type name="uint64" />
    <value>12000000</value>
  </data>
  <data name="physical_reads">
    <type name="uint64" />
    <value>45000</value>
  </data>
  <data name="logical_reads">
    <type name="uint64" />
    <value>125000</value>
  </data>
  <data name="statement">
    <type name="unicode_string" />
    <value>SELECT o.OrderID, c.CustomerName, SUM(od.Quantity * od.UnitPrice) as OrderTotal,
           AVG(p.UnitPrice) OVER (PARTITION BY p.CategoryID) as AvgCategoryPrice
    FROM Orders o
    INNER JOIN Customers c ON o.CustomerID = c.CustomerID  
    INNER JOIN [Order Details] od ON o.OrderID = od.OrderID
    INNER JOIN Products p ON od.ProductID = p.ProductID
    WHERE o.OrderDate BETWEEN '2024-01-01' AND '2024-12-31'
      AND c.Country IN ('USA', 'Canada', 'Mexico')
    GROUP BY o.OrderID, c.CustomerName, p.CategoryID
    HAVING SUM(od.Quantity * od.UnitPrice) > 1000
    ORDER BY OrderTotal DESC</value>
  </data>
</event>
```

### Sample Query Types (Planned)
- **Table scans** on large tables without proper indexing
- **Key lookups** from non-covering indexes
- **Implicit conversions** causing performance issues
- **Window functions** without proper partitioning
- **CTE performance** vs temporary tables
- **Parameter sniffing** issues with stored procedures
- **Missing statistics** and outdated statistics

## Configuration for SQL Server Monitoring

### Extended Events Session
```sql
-- Create Extended Events session for slow queries
CREATE EVENT SESSION [SlowQueries] ON SERVER 
ADD EVENT sqlserver.sql_statement_completed(
    ACTION(sqlserver.sql_text, sqlserver.database_name, sqlserver.username)
    WHERE ([duration] > 1000000)  -- > 1 second in microseconds
),
ADD EVENT sqlserver.rpc_completed(
    ACTION(sqlserver.sql_text, sqlserver.database_name, sqlserver.username) 
    WHERE ([duration] > 1000000)
)
ADD TARGET package0.event_file(SET filename=N'C:\temp\SlowQueries.xel')
WITH (MAX_MEMORY=4096 KB, EVENT_RETENTION_MODE=ALLOW_SINGLE_EVENT_LOSS, 
      MAX_DISPATCH_LATENCY=30 SECONDS, MAX_EVENT_SIZE=0 KB, 
      MEMORY_PARTITION_MODE=NONE, TRACK_CAUSALITY=OFF, STARTUP_STATE=ON)
GO

-- Start the session
ALTER EVENT SESSION [SlowQueries] ON SERVER STATE = START;
```

### Query Store Integration
```sql
-- Enable Query Store (SQL Server 2016+)
ALTER DATABASE [YourDatabase] SET QUERY_STORE = ON;
ALTER DATABASE [YourDatabase] SET QUERY_STORE (
    OPERATION_MODE = READ_WRITE,
    CLEANUP_POLICY = (STALE_QUERY_THRESHOLD_DAYS = 30),
    DATA_FLUSH_INTERVAL_SECONDS = 900,
    MAX_STORAGE_SIZE_MB = 1000,
    INTERVAL_LENGTH_MINUTES = 60
);
```

## SQL Server Specific Features (Planned)

- **Execution Plan Analysis**: Parse and analyze XML execution plans
- **Wait Statistics Integration**: Identify bottlenecks beyond just duration
- **Index Usage Statistics**: Recommend missing indexes and unused indexes
- **Parameter Sniffing Detection**: Identify plan cache pollution
- **Tempdb Contention**: Detect allocation and deallocation issues
- **Always On AG Performance**: Analyze replica lag and synchronization

## Early Feedback Welcome

**If you're a SQL Server DBA**, we'd love to hear from you:
- Do you primarily use Extended Events, Query Store, or other monitoring tools?
- What SQL Server versions should we prioritize (2016+, 2019+, etc.)?
- Which performance anti-patterns are most critical in your environment?
- Any specific Always On or clustering scenarios we should consider?

📧 Contact: [Create an issue](https://github.com/iqtoolkit/slow-query-doctor/issues) with label `sqlserver-feedback`

---

**Timeline**: SQL Server support planned for v0.4.0 (Q3 2026)  
**Current Focus**: Perfecting PostgreSQL analysis with v0.2.0 configurable AI providers  
**AI Note**: Current v0.1.x requires OpenAI API key; v0.2.0+ will support local Ollama models