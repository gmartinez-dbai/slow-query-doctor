"""
Anti-pattern detection and static query rewriting suggestions.

This module implements detection of common SQL anti-patterns and provides
static rewrite suggestions without requiring database schema knowledge.
"""

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum


class AntiPatternType(Enum):
    """Types of SQL anti-patterns we can detect."""

    LEADING_WILDCARD_LIKE = "leading_wildcard_like"
    FUNCTION_ON_COLUMN = "function_on_column"
    LARGE_IN_CLAUSE = "large_in_clause"
    NOT_IN_WITH_SUBQUERY = "not_in_with_subquery"
    NO_WHERE_CLAUSE_ON_JOIN = "no_where_clause_on_join"


@dataclass
class AntiPatternMatch:
    """Represents a detected anti-pattern in a query."""

    pattern_type: AntiPatternType
    problem_description: str
    rewrite_suggestion: str
    example_rewrite: Optional[str] = None
    confidence_score: float = 1.0
    line_number: Optional[int] = None
    matched_text: str = ""


class AntiPatternDetector:
    """Detects common SQL anti-patterns and suggests rewrites."""

    def __init__(self):
        self.patterns = self._initialize_patterns()

    def _initialize_patterns(self) -> Dict[AntiPatternType, Dict]:
        """Initialize anti-pattern detection rules."""
        return {
            AntiPatternType.LEADING_WILDCARD_LIKE: {
                "regex": r'\bWHERE\s+\w+\s+LIKE\s+[\'"]%[^%\'"]',
                "flags": re.IGNORECASE | re.MULTILINE,
                "problem": "Full table scan; cannot use B-tree index",
                "solution": "Use full-text search (tsvector) or restructure data if possible",
                "example": "-- Instead of: WHERE email LIKE '%@example.com'\n-- Consider: WHERE email LIKE 'user@%' (if pattern allows)\n"
                + "-- Or use: WHERE email @@ to_tsquery('example.com')",
            },
            AntiPatternType.FUNCTION_ON_COLUMN: {
                "regex": r"\bWHERE\s+\w+\s*\(\s*\w+\s*\)\s*[=<>!]",
                "flags": re.IGNORECASE | re.MULTILINE,
                "problem": "Function prevents index usage",
                "solution": "Create function-based index or restructure condition",
                "example": "-- Instead of: WHERE LOWER(email) = 'test@example.com'\n-- Create index: CREATE INDEX ON users (LOWER(email))\n"
                + "-- Or store normalized data",
            },
            AntiPatternType.LARGE_IN_CLAUSE: {
                "regex": r"\bIN\s*\(\s*[^)]*,.*?,.*?,.*?,.*?[^)]*\)",
                "flags": re.IGNORECASE | re.DOTALL,
                "problem": "Can be slow with many values",
                "solution": "Use JOIN to temporary table or VALUES list instead",
                "example": "-- Instead of: WHERE id IN (1, 2, 3, ..., 5000)\n-- Use: JOIN (VALUES (1), (2), (3)) AS t(id) ON table.id = t.id\n"
                + "-- Or create temp table with values",
            },
            AntiPatternType.NOT_IN_WITH_SUBQUERY: {
                "regex": r"\bNOT\s+IN\s*\(\s*SELECT\b",
                "flags": re.IGNORECASE | re.MULTILINE,
                "problem": "Returns incorrect results if subquery has NULL values",
                "solution": "Use NOT EXISTS or LEFT JOIN...IS NULL instead",
                "example": "-- Instead of: WHERE user_id NOT IN (SELECT id FROM deleted_users)\n-- Use: WHERE NOT EXISTS (SELECT 1 FROM deleted_users d WHERE d.id = user_id)\n"
                + "-- Or: LEFT JOIN deleted_users d ON d.id = user_id WHERE d.id IS NULL",
            },
            AntiPatternType.NO_WHERE_CLAUSE_ON_JOIN: {
                "regex": r"\bFROM\s+\w+\s*,\s*\w+(?!\s+WHERE)",
                "flags": re.IGNORECASE | re.DOTALL,
                "problem": "Cartesian product risk; hard to optimize",
                "solution": "Use explicit INNER JOIN ON with proper join condition",
                "example": "-- Instead of: SELECT * FROM orders o, customers c WHERE o.amount > 1000\n-- Use: SELECT * FROM orders o INNER JOIN customers c ON o.customer_id = c.id WHERE o.amount > 1000\n",
            },
        }

    def detect_antipatterns(self, query: str) -> List[AntiPatternMatch]:
        """
        Detect anti-patterns in a SQL query.

        Args:
            query: The SQL query to analyze

        Returns:
            List of detected anti-pattern matches
        """
        matches = []

        for pattern_type, config in self.patterns.items():
            regex_matches = re.finditer(config["regex"], query, config["flags"])

            for match in regex_matches:
                anti_pattern = AntiPatternMatch(
                    pattern_type=pattern_type,
                    problem_description=config["problem"],
                    rewrite_suggestion=config["solution"],
                    example_rewrite=config.get("example"),
                    matched_text=match.group(),
                    confidence_score=self._calculate_confidence(
                        pattern_type, match, query
                    ),
                )
                matches.append(anti_pattern)

        return matches

    def _calculate_confidence(
        self, pattern_type: AntiPatternType, match: re.Match, query: str
    ) -> float:
        """Calculate confidence score for anti-pattern detection."""
        base_confidence = 0.8

        # Adjust confidence based on context
        if pattern_type == AntiPatternType.LARGE_IN_CLAUSE:
            # Count the number of values in the IN clause
            in_values = match.group().count(",")
            if in_values > 10:
                return min(1.0, base_confidence + (in_values / 100))
            elif in_values < 5:
                return max(0.5, base_confidence - 0.2)

        elif pattern_type == AntiPatternType.LEADING_WILDCARD_LIKE:
            # Check if it's actually a leading wildcard
            like_content = re.search(
                r"LIKE\s+['\"]([^'\"]+)['\"]", match.group(), re.IGNORECASE
            )
            if like_content and like_content.group(1).startswith("%"):
                return base_confidence + 0.1

        return base_confidence

    def generate_rewrite_report(
        self, query: str, matches: List[AntiPatternMatch]
    ) -> str:
        """
        Generate a detailed report with rewrite suggestions.

        Args:
            query: Original query
            matches: List of detected anti-patterns

        Returns:
            Formatted report string
        """
        if not matches:
            return "✅ No anti-patterns detected in this query."

        report = f"🔍 **Anti-Pattern Analysis** ({len(matches)} issues found)\n\n"

        for i, match in enumerate(matches, 1):
            report += f"### Issue #{i}: {match.pattern_type.value.replace('_', ' ').title()}\n\n"
            report += f"**Problem**: {match.problem_description}\n\n"
            report += f"**Detected Pattern**: `{match.matched_text.strip()}`\n\n"
            report += f"**Recommendation**: {match.rewrite_suggestion}\n\n"

            if match.example_rewrite:
                report += f"**Example**:\n```sql\n{match.example_rewrite}\n```\n\n"

            report += f"**Confidence**: {match.confidence_score:.1%}\n\n"
            report += "---\n\n"

        return report


class StaticQueryRewriter:
    """Provides static query rewriting suggestions without database schema."""

    def __init__(self):
        self.detector = AntiPatternDetector()

    def analyze_query(self, query: str) -> Tuple[List[AntiPatternMatch], str]:
        """
        Analyze a query for anti-patterns and generate rewrite suggestions.

        Args:
            query: SQL query to analyze

        Returns:
            Tuple of (anti-pattern matches, formatted report)
        """
        matches = self.detector.detect_antipatterns(query)
        report = self.detector.generate_rewrite_report(query, matches)

        return matches, report

    def get_optimization_score(self, matches: List[AntiPatternMatch]) -> float:
        """
        Calculate an optimization score based on detected anti-patterns.

        Args:
            matches: List of anti-pattern matches

        Returns:
            Score from 0.0 (many issues) to 1.0 (no issues)
        """
        if not matches:
            return 1.0

        # Weight different anti-patterns by severity
        severity_weights = {
            AntiPatternType.NO_WHERE_CLAUSE_ON_JOIN: 0.4,
            AntiPatternType.LEADING_WILDCARD_LIKE: 0.3,
            AntiPatternType.NOT_IN_WITH_SUBQUERY: 0.3,
            AntiPatternType.FUNCTION_ON_COLUMN: 0.2,
            AntiPatternType.LARGE_IN_CLAUSE: 0.1,
        }

        total_penalty = 0.0
        for match in matches:
            weight = severity_weights.get(match.pattern_type, 0.1)
            penalty = weight * match.confidence_score
            total_penalty += penalty

        # Convert penalty to score (max penalty of 1.0 = score of 0.0)
        return max(0.0, 1.0 - min(1.0, total_penalty))
