# 🚦 Slow Query Doctor Roadmap

## Current Release: v0.1.5 ✅ SHIPPED

- Database slow query log parsing (PostgreSQL focus)
- Query normalization and grouping
- Statistical analysis (impact scores, percentiles)
- AI-powered optimization recommendations (OpenAI only)
- Markdown report generation
- Docker containerization
- Anti-pattern detection
- Multi-format log support (plain, CSV, JSON)

**AI Provider Limitation**: v0.1.x supports **OpenAI GPT models only** (requires OPENAI_API_KEY). For sensitive database logs, consider waiting for v0.2.0 with local Ollama support and configurable AI providers.

---

## v0.1.6 - Final v0.1.x Feature Release (November 2025) 🔒 FEATURE FREEZE

**Focus:** Complete documentation and prepare for v0.2.0

**🚨 IMPORTANT**: This is the **FINAL v0.1.x release with new features**. Any future v0.1.x updates (v0.1.7+) will be **bug fixes only**. All new features go to v0.2.0+.

- [x] Add comprehensive ARCHITECTURE.md documentation
- [x] Update all references from "PostgreSQL-specific" to "database log analyzer"
- [x] Clear roadmap timeline and scope boundaries
- [x] Project discipline guidelines (.gitmessage)
- [x] Prepare codebase for multi-database expansion in v0.4.0
- [x] Plan configurable AI provider architecture (Ollama default, OpenAI optional)
- [x] Design extensible AI provider system for future models (Claude, Gemini, etc.)
- [x] Create placeholder sample log directories for MySQL and SQL Server
- [x] Add comprehensive AI provider extensibility guide in ARCHITECTURE.md
- [x] Establish release tagging strategy (v0.1.6-final-feature)

**Post-v0.1.6**: Only critical bug fixes allowed in v0.1.x branch. Feature development moves to v0.2.0.

---

## v0.2.2a1 - MongoDB Support (Nov 2025) ✅ ALPHA READY

**Focus:** MongoDB slow query analysis and reporting

**🚨 MONGODB FEATURES COMPLETE**
- ✅ **MongoDB slow query analyzer** with profiler integration
- ✅ **MongoDB query pattern recognition** and normalization
- ✅ **Enhanced configuration system** (expanded YAML configuration with MongoDB support)
- ✅ **HTML report generation** (interactive dashboards with MongoDB-specific insights)
- ✅ **Multi-format reporting** (JSON, Markdown, HTML)
- ✅ **CLI integration** with database-specific subcommands
- ✅ **Production integration test** script for validation

**Features:**
- [x] **MongoDB slow query analyzer** (complete with profiler integration)
- [x] **Enhanced configuration system** (expanded .slowquerydoctor.yml options)
- [x] **HTML report generation** (interactive dashboards)
- [x] **Multi-file analysis** (batch processing)
- [ ] **MongoDB aggregation pipeline optimization** → v0.2.3
- [ ] **MongoDB indexing recommendations** → v0.2.3

---

## v0.2.3 - Enhanced MongoDB Analysis (Q1 2026) 📋 PLANNED

**Focus:** Advanced MongoDB optimization features

- [ ] **MongoDB aggregation pipeline optimization** recommendations
- [ ] **MongoDB indexing strategy** analysis and suggestions
- [ ] **Query complexity scoring and classification**
- [ ] **Enhanced anti-pattern detection engine**

---

## v0.2.4 - Flexible AI Providers (Q1 2026) 📋 PLANNED

**Focus:** Enterprise-grade AI provider flexibility

**🚨 AI PROVIDER FLEXIBILITY**
- Database logs = sensitive business data
- **Default: Ollama** (local, private, enterprise-safe)
- **Optional: OpenAI** (configurable for non-sensitive environments)
- **Future-ready**: Pluggable architecture for multiple AI providers

- [ ] **Configurable AI providers** (Ollama default, OpenAI optional)
- [ ] **Flexible model configuration** (custom endpoints, multiple models)
- [ ] Add EXPLAIN plan analysis integration (PostgreSQL)
- [ ] FastAPI backend for programmatic access

---

## v0.3.0 - Self-Learning & ML Intelligence (Q2 2026) 🚫 DO NOT START

**Focus:** ML-based intelligence and historical tracking

- [ ] Track query performance over time (historical database)
- [ ] ML-based anomaly detection for new slow queries
- [ ] Identify performance regression patterns
- [ ] Confidence scoring for recommendations
- [ ] Trend analysis (queries getting slower over time)
- [ ] Automatic baseline detection
- [ ] Predictive alerts for queries likely to become slow
- [ ] Learn from user feedback (which recommendations worked)

---

## v0.4.0 - MySQL & SQL Server Support (Q3 2026)

**Focus:** Traditional SQL databases (after MongoDB is stable)

- [ ] **MySQL slow query log support**
- [ ] **SQL Server Extended Events support**
- [ ] Database-agnostic query analysis engine
- [ ] Cross-database performance comparison (PostgreSQL + MongoDB + MySQL + SQL Server)
- [ ] Unified configuration for multiple database types
- [ ] Database-specific optimization recommendations

**Early Feedback Collection:**
- 📁 `docs/sample_logs/mysql/` - Configuration examples and feedback templates
- 📁 `docs/sample_logs/sqlserver/` - Extended Events samples and feedback collection
- 🎯 **Goal**: Collect real-world requirements before development starts

**Note:** Oracle support not planned - focusing on PostgreSQL, MongoDB, MySQL, and SQL Server as the most common enterprise databases.

---

## v1.0.0 - Production Ready (Q4 2026)

**Focus:** Enterprise-grade stability and features

- [ ] Web UI for easier analysis
- [ ] API for programmatic access
- [ ] Authentication and multi-user support
- [ ] Scheduled analysis and alerting
- [ ] Integration with monitoring tools (Prometheus, Grafana)
- [ ] Performance regression CI/CD integration
- [ ] Comprehensive test coverage
- [ ] Enterprise support options

---

## Future Ideas (Backlog)

- Real-time query monitoring integration
- Automated optimization application (with approval workflow)
- Query workload simulator
- Cost estimation for cloud databases
- Integration with query plan visualizers
- Mobile app for on-call DBAs
- Slack/Teams notification integration
- AI-powered query rewriting suggestions

---

## Community Requests

Track feature requests from users here:

- **Ravi Bhatia:** ML/self-learning system for recommendations → BACKLOG (v0.3.0, Q2 2026)
- **Uri Dimant:** Query rewrites (not just indexes) → IMPLEMENTED ✅

## Version Timeline Summary

| Version | Timeline | Status | Key Features |
|---------|----------|--------|--------------|
| v0.1.5 | ✅ SHIPPED | Mature | PostgreSQL analyzer with **OpenAI only** |
| v0.1.6 | Nov 2025 | 🔒 Feature Freeze | **Final v0.1.x with new features** - Documentation, architecture, **OpenAI only** |
| v0.1.7+ | Ongoing | 🐛 Bug Fixes Only | Critical fixes, **OpenAI only**, no new features |
| v0.2.2a1 | Nov 2025 | ✅ Alpha Ready | **MongoDB support** - analyzer, profiler integration, multi-format reports, CLI, **OpenAI only** |
| v0.2.3 | Q1 2026 | � Planned | **Enhanced MongoDB** - aggregation optimization, indexing recommendations |
| v0.2.4 | Q1 2026 | 📋 Planned | **Configurable AI providers** (Ollama default, OpenAI optional), EXPLAIN plans, FastAPI |
| v0.3.0 | Q2 2026 | 🚫 Do Not Start | ML/self-learning, anomaly detection |
| v0.4.0 | Q3 2026 | 📋 Planned | **MySQL, SQL Server support** |
| v1.0.0 | Q4 2026 | 📋 Planned | Web UI, enterprise features |

---

## Release & Versioning (short)

See the published release process and versioning guide in the documentation: `docs/release-process.md`.
Key points:
- `VERSION` at repo root is the single source of truth.
- Use the provided GitHub Action `/.github/workflows/propagate-version.yml` to propagate and tag releases.
- Automate changelog generation (Release Drafter or conventional-changelog) and add security scans to CI for release gating.


## Contributing

See issues labeled with `good-first-issue` or `help-wanted` for ways to contribute!

Questions or suggestions? Email: gio@gmartinez.net
---

**Made with ❤️ for Database performance optimization**