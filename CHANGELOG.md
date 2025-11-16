# Changelog

All notable changes to Slow Query Doctor will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Preparing for next feature development cycle

## [0.2.0] - 2025-11-15

### Added
- **🎉 MongoDB Support**: Complete MongoDB slow query analysis engine
- **Real-time Profiler Integration**: MongoDB profiler integration for live query monitoring
- **Multi-format Reports**: JSON, HTML, and Markdown report generation for MongoDB
- **MongoDB Configuration**: YAML-based configuration system for MongoDB connections
- **CLI Enhancement**: Database-specific subcommands (`postgresql`, `mongodb`)
- **Comprehensive Testing**: 25 MongoDB test cases with full coverage
- **Query Intelligence**: Pattern recognition and normalization for MongoDB operations
- **Performance Analysis**: Impact scoring and optimization recommendations
- **Index Analysis**: Usage analysis and optimization suggestions for MongoDB indexes
- **Collection Insights**: Collection-level performance analysis and statistics

### Changed
- **Enhanced CLI**: Restructured to support multiple database types with subcommands
- **Configuration System**: Expanded to handle multiple database connection types
- **Documentation**: Updated to highlight multi-database support capabilities
- **Error Handling**: Improved error handling for database connections and operations

### Fixed
- **Code Quality**: All linting and formatting issues resolved across codebase
- **Test Reliability**: MongoDB connection failure handling in test suite
- **Import Handling**: Proper fallback for optional PyMongo dependency
- **Documentation**: Line length and formatting issues in examples

### Added
- Complete MongoDB slow query analysis engine
- MongoDB profiler integration for real-time query monitoring
- Multi-format report generation (JSON, HTML, Markdown) for MongoDB
- MongoDB-specific configuration system with YAML support
- CLI integration with `mongodb` and `mongo` command aliases
- Comprehensive test suite with 25 MongoDB test cases
- Query pattern recognition and normalization for MongoDB
- Impact scoring and performance analysis for MongoDB operations
- Index usage analysis and optimization recommendations
- Collection-level performance insights and statistics

### Changed
- Restructured CLI to support multiple database types
- Enhanced configuration system to handle MongoDB connections
- Improved error handling for database connections and operations
- Updated project documentation to highlight MongoDB support

### Fixed
- MongoDB connection failure handling in test suite
- Code formatting issues identified by Black formatter
- Linting errors in documentation examples and utility scripts
- Import handling for optional PyMongo dependency

## [0.1.6] - 2025-11-01

### Added
- Comprehensive ARCHITECTURE.md documentation
- Clear roadmap timeline and scope boundaries in ROADMAP.md
- Project discipline guidelines with .gitmessage template
- Sample log directories for future MySQL and SQL Server support
- AI provider extensibility guide in ARCHITECTURE.md
- Release tagging strategy documentation

### Changed
- Updated all references from "PostgreSQL-specific" to "database log analyzer"
- Prepared codebase architecture for multi-database expansion in v0.4.0
- Established feature freeze for v0.1.x branch (bug fixes only going forward)
- Enhanced project documentation and contribution guidelines

### Fixed
- Various documentation improvements and clarifications
- Consistency issues in project messaging and scope

## [0.1.5] - 2025-10-28

### Added
- Initial PostgreSQL slow query log parsing and analysis
- AI-powered optimization recommendations using OpenAI GPT models
- Query normalization and grouping functionality
- Statistical analysis with impact scores and percentiles
- Markdown report generation with detailed recommendations
- Anti-pattern detection for common PostgreSQL performance issues
- Multi-format log support (plain, CSV, JSON)
- Docker containerization support
- Comprehensive sample log files with real slow query examples
- Command-line interface with configurable options

### Changed
- N/A (Initial major release)

### Fixed
- N/A (Initial major release)

## [0.1.0] - 2025-10-15

### Added
- Project initialization
- Basic PostgreSQL log parsing functionality
- Core project structure and dependencies
- Initial documentation and README

---

## Release Timeline Summary

| Version | Status | Key Features | Timeline |
|---------|--------|--------------|----------|
| v0.1.5 | ✅ Released | PostgreSQL analyzer with OpenAI only | October 2025 |
| v0.1.6 | ✅ Released | Final v0.1.x feature release, documentation | November 2025 |
| v0.2.0 | 🔧 In Progress | **MongoDB support** + Enhanced config system | November 2025 - Q1 2026 |
| v0.2.x | 📋 Planned | Configurable AI providers (Ollama default) | Q1 2026 |
| v0.3.0 | 📋 Planned | ML/self-learning features | Q2 2026 |
| v0.4.0 | 📋 Planned | **MySQL, SQL Server support** | Q3 2026 |
| v1.0.0 | 📋 Planned | Production-ready with Web UI | Q4 2026 |

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## Versioning

We use [Semantic Versioning](https://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/gmartinez-dbai/slow-query-doctor/tags).

---

**Note**: This project follows a disciplined release process. v0.1.6 was the final v0.1.x release with new features. All future v0.1.x releases (v0.1.7+) contain bug fixes only. New feature development has moved to v0.2.0+.