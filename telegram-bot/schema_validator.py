#!/usr/bin/env python3
"""
ASEAGI Database Schema Validator
Verifies NON-NEGOTIABLE tables exist with correct structure
CRITICAL: These 3 tables are non-negotiable and must exist:
  • communications (evidence)
  • events (timeline - MOST IMPORTANT)
  • document_journal (processing & growth)
"""

from typing import Dict, List, Set, Optional, Tuple
from supabase import Client
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# NON-NEGOTIABLE TABLE DEFINITIONS
# ============================================================================

REQUIRED_TABLES = {
    'communications': {
        'description': 'Evidence tracking - CRITICAL for legal case',
        'why_critical': 'Every communication is potential evidence',
        'required_columns': [
            'id',
            'sender',
            'recipient',
            'communication_date',
            'communication_method',
            'content',
            'truthfulness_score',
            'contains_contradiction',
            'contains_manipulation',
            'relevancy_score'
        ],
        'critical_columns': [
            'sender', 'recipient', 'communication_date', 'truthfulness_score'
        ]
    },
    'events': {
        'description': 'Timeline - MOST IMPORTANT for case progression',
        'why_critical': 'Events are the most important timeline factor',
        'required_columns': [
            'id',
            'event_date',
            'event_title',
            'event_type',
            'event_description',
            'significance_score',
            'violations_occurred',
            'evidence_strength',
            'requires_action'
        ],
        'critical_columns': [
            'event_date', 'event_title', 'event_type', 'significance_score'
        ]
    },
    'document_journal': {
        'description': 'Processing & growth assessment',
        'why_critical': 'Journal entry after every scan - critical to fix upgrade and assess long-term growth',
        'required_columns': [
            'id',
            'document_id',
            'original_filename',
            'processing_status',
            'scan_date',
            'processed_date',
            'relevancy_score',
            'micro_score',
            'insights_extracted',
            'contradictions_found',
            'version'
        ],
        'critical_columns': [
            'original_filename', 'processing_status', 'relevancy_score'
        ]
    }
}

# ============================================================================
# SCHEMA VALIDATION FUNCTIONS
# ============================================================================

class SchemaValidationError(Exception):
    """Raised when database schema validation fails"""
    pass

class SchemaValidator:
    """Validates database schema against NON-NEGOTIABLE requirements"""

    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
        self.validation_results = {}

    def validate_all(self, strict: bool = False) -> Tuple[bool, List[str]]:
        """
        Validate all NON-NEGOTIABLE tables

        Args:
            strict: If True, raise exception on validation failure
                   If False, log warnings and continue

        Returns:
            (success, errors) tuple
        """
        logger.info("🔍 Starting NON-NEGOTIABLE table validation...")
        errors = []

        for table_name, table_config in REQUIRED_TABLES.items():
            try:
                table_errors = self._validate_table(table_name, table_config)
                if table_errors:
                    errors.extend(table_errors)
                else:
                    logger.info(f"✅ Table '{table_name}' validated successfully")
            except Exception as e:
                error_msg = f"❌ CRITICAL: Table '{table_name}' validation failed: {e}"
                logger.error(error_msg)
                errors.append(error_msg)

        if errors:
            error_summary = "\n".join(errors)
            logger.error(f"\n{'='*70}\n🚨 DATABASE SCHEMA VALIDATION FAILED\n{'='*70}\n{error_summary}\n{'='*70}")

            if strict:
                raise SchemaValidationError(
                    f"Database schema validation failed with {len(errors)} error(s):\n{error_summary}"
                )
            return False, errors
        else:
            logger.info("✅ All NON-NEGOTIABLE tables validated successfully")
            return True, []

    def _validate_table(self, table_name: str, config: Dict) -> List[str]:
        """Validate a single table"""
        errors = []

        # Check if table exists and is accessible
        try:
            result = self.supabase.table(table_name).select('*').limit(1).execute()
        except Exception as e:
            errors.append(
                f"❌ CRITICAL: Table '{table_name}' does not exist or is inaccessible\n"
                f"   Why critical: {config['why_critical']}\n"
                f"   Error: {e}\n"
                f"   Fix: Run mcp-servers/aseagi-mvp-server/database/01_create_critical_tables.sql"
            )
            return errors

        # Check if table has data to validate schema
        if not result.data:
            logger.warning(
                f"⚠️ Table '{table_name}' exists but is empty\n"
                f"   Description: {config['description']}\n"
                f"   Recommendation: Add sample data to validate full schema"
            )
            return errors

        # Validate columns
        actual_columns = set(result.data[0].keys())
        required_columns = set(config['required_columns'])
        critical_columns = set(config['critical_columns'])

        # Check for missing required columns
        missing_required = required_columns - actual_columns
        if missing_required:
            errors.append(
                f"❌ Table '{table_name}' missing REQUIRED columns: {missing_required}\n"
                f"   Description: {config['description']}\n"
                f"   Fix: ALTER TABLE to add missing columns"
            )

        # Check for missing critical columns (more severe)
        missing_critical = critical_columns - actual_columns
        if missing_critical:
            errors.append(
                f"🚨 CRITICAL: Table '{table_name}' missing CRITICAL columns: {missing_critical}\n"
                f"   Why critical: {config['why_critical']}\n"
                f"   These columns are NON-NEGOTIABLE and must exist\n"
                f"   Fix: Run database migration immediately"
            )

        # Log extra columns (not an error, just informational)
        extra_columns = actual_columns - required_columns
        if extra_columns:
            logger.debug(f"ℹ️ Table '{table_name}' has extra columns: {extra_columns}")

        return errors

    def validate_table_data_quality(self, table_name: str, sample_size: int = 100) -> Dict:
        """
        Validate data quality in a table
        Returns statistics about data completeness
        """
        try:
            result = self.supabase.table(table_name)\
                .select('*')\
                .limit(sample_size)\
                .execute()

            if not result.data:
                return {
                    'table': table_name,
                    'record_count': 0,
                    'data_quality': 'empty'
                }

            records = result.data
            total_records = len(records)

            # Calculate completeness for critical columns
            config = REQUIRED_TABLES.get(table_name, {})
            critical_columns = config.get('critical_columns', [])

            completeness = {}
            for column in critical_columns:
                non_null_count = sum(1 for record in records if record.get(column) is not None)
                completeness[column] = (non_null_count / total_records) * 100

            # Check for score columns (should be 0-1000 range)
            score_columns = [col for col in records[0].keys() if '_score' in col]
            score_ranges = {}
            for score_col in score_columns:
                scores = [r.get(score_col) for r in records if r.get(score_col) is not None]
                if scores:
                    score_ranges[score_col] = {
                        'min': min(scores),
                        'max': max(scores),
                        'avg': sum(scores) / len(scores),
                        'valid_range': all(0 <= s <= 1000 for s in scores)
                    }

            return {
                'table': table_name,
                'record_count': total_records,
                'completeness': completeness,
                'score_ranges': score_ranges,
                'data_quality': 'good' if all(c >= 80 for c in completeness.values()) else 'needs_improvement'
            }

        except Exception as e:
            logger.error(f"Error validating data quality for '{table_name}': {e}")
            return {
                'table': table_name,
                'error': str(e),
                'data_quality': 'unknown'
            }

    def get_schema_summary(self) -> Dict:
        """Get summary of database schema validation"""
        summary = {
            'tables': {},
            'overall_status': 'unknown'
        }

        all_valid = True
        for table_name, config in REQUIRED_TABLES.items():
            try:
                # Check table existence
                result = self.supabase.table(table_name).select('id', count='exact').limit(1).execute()

                # Get data quality
                quality = self.validate_table_data_quality(table_name)

                summary['tables'][table_name] = {
                    'exists': True,
                    'description': config['description'],
                    'why_critical': config['why_critical'],
                    'record_count': result.count or 0,
                    'data_quality': quality.get('data_quality', 'unknown'),
                    'completeness': quality.get('completeness', {})
                }
            except Exception as e:
                all_valid = False
                summary['tables'][table_name] = {
                    'exists': False,
                    'error': str(e),
                    'description': config['description'],
                    'why_critical': config['why_critical']
                }

        summary['overall_status'] = 'valid' if all_valid else 'invalid'
        return summary

# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def validate_schema(supabase_client: Client, strict: bool = False) -> bool:
    """
    Validate database schema (convenience function)

    Args:
        supabase_client: Supabase client instance
        strict: If True, raise exception on validation failure

    Returns:
        True if validation successful, False otherwise (when strict=False)

    Raises:
        SchemaValidationError: If validation fails and strict=True
    """
    validator = SchemaValidator(supabase_client)
    success, errors = validator.validate_all(strict=strict)
    return success

def get_schema_status(supabase_client: Client) -> Dict:
    """
    Get schema validation status (convenience function)

    Returns:
        Dictionary with schema summary
    """
    validator = SchemaValidator(supabase_client)
    return validator.get_schema_summary()

# ============================================================================
# CLI TOOL (for manual testing)
# ============================================================================

if __name__ == "__main__":
    import os
    from supabase import create_client

    # Get credentials from environment
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY environment variables required")
        print("\nUsage:")
        print("  export SUPABASE_URL='your-url'")
        print("  export SUPABASE_KEY='your-key'")
        print("  python3 schema_validator.py")
        exit(1)

    # Create client
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s'
    )

    print("="*70)
    print("ASEAGI DATABASE SCHEMA VALIDATOR")
    print("Validating NON-NEGOTIABLE tables")
    print("="*70)
    print()

    # Run validation
    validator = SchemaValidator(supabase)
    success, errors = validator.validate_all(strict=False)

    print()
    print("="*70)
    print("SCHEMA SUMMARY")
    print("="*70)
    print()

    summary = validator.get_schema_summary()
    for table_name, info in summary['tables'].items():
        print(f"📋 {table_name}")
        print(f"   Description: {info['description']}")
        print(f"   Why Critical: {info['why_critical']}")

        if info.get('exists'):
            print(f"   ✅ Exists: Yes")
            print(f"   📊 Records: {info.get('record_count', 0)}")
            print(f"   ⭐ Quality: {info.get('data_quality', 'unknown')}")

            completeness = info.get('completeness', {})
            if completeness:
                print(f"   📈 Completeness:")
                for col, pct in completeness.items():
                    emoji = "✅" if pct >= 80 else "⚠️" if pct >= 50 else "❌"
                    print(f"      {emoji} {col}: {pct:.1f}%")
        else:
            print(f"   ❌ Exists: No")
            print(f"   Error: {info.get('error', 'Unknown')}")

        print()

    print("="*70)
    print(f"Overall Status: {'✅ VALID' if summary['overall_status'] == 'valid' else '❌ INVALID'}")
    print("="*70)

    exit(0 if success else 1)
