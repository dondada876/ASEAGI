#!/usr/bin/env python3
"""
Criminal Complaint Evidence Analyzer
=====================================

Queries all scanned documents to find evidence supporting the criminal complaint.
Maps documents to specific false statements and generates prosecution-ready reports.

Usage:
    export SUPABASE_URL="https://jvjlhxodmbkodzmggwpu.supabase.co"
    export SUPABASE_KEY="your_key"

    python3 scanners/criminal_complaint_analyzer.py
    python3 scanners/criminal_complaint_analyzer.py --claim FS-001-JAMAICA-FLIGHT
    python3 scanners/criminal_complaint_analyzer.py --export-report report.md
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from supabase import create_client
import re

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from database.criminal_complaint_schema import (
    PERJURY_COMPLAINT_2025,
    EVIDENCE_QUERIES,
    CorrelationScoring
)

class CriminalComplaintAnalyzer:
    """Analyzes documents against criminal complaint claims"""

    def __init__(self, supabase_url: str, supabase_key: str):
        self.client = create_client(supabase_url, supabase_key)
        self.complaint = PERJURY_COMPLAINT_2025
        self.evidence_map = {}  # Maps claim_id → [document_ids]
        self.prosecutability_scores = {}

    def query_all_documents(self) -> List[Dict]:
        """Get all legal documents from database"""
        try:
            result = self.client.table('legal_documents')\
                .select('*')\
                .eq('case_id', 'ashe-bucknor-j24-00478')\
                .order('relevancy_number', desc=True)\
                .execute()

            print(f"✅ Loaded {len(result.data)} documents from database")
            return result.data
        except Exception as e:
            print(f"❌ Error loading documents: {e}")
            return []

    def calculate_date_relevance(self, doc_date: str, claim_date_range: List[str]) -> int:
        """
        Calculate date relevance score (0-100)
        100 = document is within the claim date range
        Lower = document is outside the range
        """
        if not doc_date:
            return 0

        try:
            doc_dt = datetime.fromisoformat(doc_date.split('T')[0])
            start_dt = datetime.fromisoformat(claim_date_range[0])
            end_dt = datetime.fromisoformat(claim_date_range[1])

            if start_dt <= doc_dt <= end_dt:
                return 100  # Perfect date match
            elif doc_dt < start_dt:
                days_before = (start_dt - doc_dt).days
                return max(0, 100 - days_before)
            else:
                days_after = (doc_dt - end_dt).days
                return max(0, 100 - days_after)
        except:
            return 0

    def search_keywords_in_document(self, doc: Dict, keywords: List[str]) -> int:
        """
        Search for keywords in document
        Returns number of keywords found
        """
        matches = 0
        search_fields = [
            doc.get('summary', ''),
            str(doc.get('key_quotes', [])),
            doc.get('executive_summary', ''),
            doc.get('file_name', ''),
        ]

        search_text = ' '.join(search_fields).lower()

        for keyword in keywords:
            if keyword.lower() in search_text:
                matches += 1

        return matches

    def analyze_claim(self, claim: Dict, all_documents: List[Dict]) -> Dict:
        """
        Analyze a single false statement claim against all documents
        Returns evidence supporting the claim
        """
        print(f"\n{'='*80}")
        print(f"ANALYZING CLAIM: {claim['id']}")
        print(f"Claim Type: {claim['claim_type']}")
        print(f"{'='*80}\n")

        supporting_docs = []

        for doc in all_documents:
            # Calculate keyword matches
            keyword_matches = self.search_keywords_in_document(
                doc,
                claim['search_keywords']
            )

            # Calculate date relevance
            date_relevance = self.calculate_date_relevance(
                doc.get('document_date'),
                claim['date_range']
            )

            # Check document type match
            expected_type = claim['expected_evidence_type']
            doc_type = doc.get('document_type', '')
            type_match = (doc_type == expected_type) if expected_type else True

            # Calculate contradiction score
            contradiction_score = CorrelationScoring.calculate_contradiction_score(
                document_relevancy=doc.get('relevancy_number', 0),
                keyword_matches=keyword_matches,
                date_relevance=date_relevance,
                document_type_match=type_match
            )

            # Include document if it has meaningful correlation
            if contradiction_score >= 400 or keyword_matches >= 2:
                supporting_docs.append({
                    'document_id': doc['id'],
                    'file_name': doc.get('file_name', doc.get('original_filename', 'Unknown')),
                    'document_type': doc_type,
                    'document_date': doc.get('document_date'),
                    'relevancy_number': doc.get('relevancy_number', 0),
                    'contradiction_score': contradiction_score,
                    'keyword_matches': keyword_matches,
                    'date_relevance': date_relevance,
                    'type_match': type_match,
                    'key_quotes': doc.get('key_quotes', [])[:3],  # Top 3 quotes
                    'summary': doc.get('summary', doc.get('executive_summary', ''))[:200],
                })

        # Sort by contradiction score
        supporting_docs.sort(key=lambda x: x['contradiction_score'], reverse=True)

        print(f"✅ Found {len(supporting_docs)} supporting documents")
        print(f"   Top score: {supporting_docs[0]['contradiction_score'] if supporting_docs else 0}")
        print(f"   Documents ≥900: {len([d for d in supporting_docs if d['contradiction_score'] >= 900])}")
        print(f"   Documents ≥800: {len([d for d in supporting_docs if d['contradiction_score'] >= 800])}")

        return {
            'claim': claim,
            'supporting_documents': supporting_docs,
            'total_documents': len(supporting_docs),
            'avg_contradiction_score': sum(d['contradiction_score'] for d in supporting_docs) / len(supporting_docs) if supporting_docs else 0,
            'smoking_guns': [d for d in supporting_docs if d['contradiction_score'] >= 900],
            'critical_evidence': [d for d in supporting_docs if d['contradiction_score'] >= 800],
        }

    def analyze_all_claims(self) -> Dict:
        """
        Analyze all false statements in the complaint
        Returns complete evidence mapping
        """
        print(f"\n{'='*80}")
        print(f"CRIMINAL COMPLAINT EVIDENCE ANALYZER")
        print(f"{'='*80}")
        print(f"Subject: {self.complaint['subject_name']}")
        print(f"Complainant: {self.complaint['complainant_name']}")
        print(f"Case: {self.complaint['case_reference']}")
        print(f"Date: {self.complaint['complaint_date']}")
        print(f"Penal Codes: {', '.join(self.complaint['penal_codes'])}")
        print(f"False Statements: {len(self.complaint['false_statements'])}")
        print(f"{'='*80}\n")

        # Load all documents
        all_documents = self.query_all_documents()

        if not all_documents:
            print("❌ No documents found. Exiting.")
            return {}

        # Analyze each claim
        results = {}
        for claim in self.complaint['false_statements']:
            claim_result = self.analyze_claim(claim, all_documents)
            results[claim['id']] = claim_result

        # Calculate overall prosecutability
        total_docs = sum(r['total_documents'] for r in results.values())
        avg_contradiction = sum(r['avg_contradiction_score'] for r in results.values()) / len(results) if results else 0
        direct_contradictions = sum(len(r['smoking_guns']) for r in results.values())

        prosecutability = CorrelationScoring.calculate_prosecutability_score(
            total_documents=total_docs,
            avg_contradiction=int(avg_contradiction),
            direct_contradictions=direct_contradictions,
            witness_statements=0  # To be counted manually
        )

        print(f"\n{'='*80}")
        print(f"OVERALL ANALYSIS")
        print(f"{'='*80}")
        print(f"Total Supporting Documents: {total_docs}")
        print(f"Average Contradiction Score: {avg_contradiction:.0f}")
        print(f"Smoking Gun Evidence (≥900): {direct_contradictions}")
        print(f"Prosecutability Score: {prosecutability}/100")
        print(f"{'='*80}\n")

        return {
            'complaint': self.complaint,
            'analysis_date': datetime.now().isoformat(),
            'total_documents_analyzed': len(all_documents),
            'claims_analyzed': len(results),
            'results': results,
            'overall_metrics': {
                'total_supporting_documents': total_docs,
                'avg_contradiction_score': avg_contradiction,
                'smoking_guns': direct_contradictions,
                'prosecutability_score': prosecutability,
            }
        }

    def export_master_report(self, analysis: Dict, output_file: str = "MASTER_PERJURY_REPORT.md"):
        """
        Export complete analysis to markdown report
        Prosecution-ready format
        """
        print(f"\n📝 Generating master report...")

        report = []
        report.append("# MASTER EVIDENCE REPORT")
        report.append("## Criminal Complaint - Perjury & Fraud")
        report.append("")
        report.append(f"**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
        report.append(f"**Subject:** {self.complaint['subject_name']}")
        report.append(f"**Complainant:** {self.complaint['complainant_name']}")
        report.append(f"**Case Reference:** {self.complaint['case_reference']}")
        report.append(f"**Penal Codes:** {', '.join(self.complaint['penal_codes'])}")
        report.append("")
        report.append("---")
        report.append("")

        # Executive Summary
        metrics = analysis['overall_metrics']
        report.append("## EXECUTIVE SUMMARY")
        report.append("")
        report.append(f"**Total Documents Analyzed:** {analysis['total_documents_analyzed']}")
        report.append(f"**Supporting Evidence Found:** {metrics['total_supporting_documents']}")
        report.append(f"**Smoking Gun Evidence (≥900):** {metrics['smoking_guns']}")
        report.append(f"**Average Contradiction Score:** {metrics['avg_contradiction_score']:.0f}/999")
        report.append(f"**Prosecutability Score:** {metrics['prosecutability_score']}/100")
        report.append("")

        if metrics['prosecutability_score'] >= 80:
            report.append("✅ **STRONG CASE FOR PROSECUTION**")
        elif metrics['prosecutability_score'] >= 60:
            report.append("⚠️ **MODERATE CASE FOR PROSECUTION**")
        else:
            report.append("⚠️ **WEAK CASE - NEEDS MORE EVIDENCE**")

        report.append("")
        report.append("---")
        report.append("")

        # Individual Claims
        for claim_id, result in analysis['results'].items():
            claim = result['claim']
            report.append(f"## CLAIM {claim_id.split('-')[1]}: {claim['claim_type']}")
            report.append("")
            report.append(f"**Declaration Date:** {claim['declaration_date']}")
            report.append(f"**Penal Code:** {', '.join(claim['penal_code'])}")
            report.append(f"**Evidence Weight:** {claim['evidence_weight']}/100")
            report.append("")
            report.append("### False Statement Under Oath:")
            report.append("")
            report.append(f"> {claim['claim_text']}")
            report.append("")
            report.append("### Evidence Analysis:")
            report.append("")
            report.append(f"- **Supporting Documents:** {result['total_documents']}")
            report.append(f"- **Smoking Guns (≥900):** {len(result['smoking_guns'])}")
            report.append(f"- **Critical Evidence (≥800):** {len(result['critical_evidence'])}")
            report.append(f"- **Average Contradiction Score:** {result['avg_contradiction_score']:.0f}/999")
            report.append("")

            # Top supporting documents
            if result['supporting_documents']:
                report.append("### Top Supporting Documents:")
                report.append("")
                for i, doc in enumerate(result['supporting_documents'][:10], 1):
                    score_badge = "🔥" if doc['contradiction_score'] >= 900 else "⚠️" if doc['contradiction_score'] >= 800 else "📌"
                    report.append(f"#### {i}. {score_badge} {doc['file_name']}")
                    report.append("")
                    report.append(f"- **Contradiction Score:** {doc['contradiction_score']}/999")
                    report.append(f"- **Document Type:** {doc['document_type']}")
                    report.append(f"- **Date:** {doc['document_date'] or 'Unknown'}")
                    report.append(f"- **Relevancy:** {doc['relevancy_number']}/999")
                    report.append(f"- **Keyword Matches:** {doc['keyword_matches']}")
                    report.append(f"- **Date Relevance:** {doc['date_relevance']}/100")

                    if doc['key_quotes']:
                        report.append(f"- **Key Quotes:**")
                        for quote in doc['key_quotes']:
                            report.append(f"  - \"{quote}\"")

                    if doc['summary']:
                        report.append(f"- **Summary:** {doc['summary']}")

                    report.append("")

            report.append("---")
            report.append("")

        # Save report
        output_path = Path(output_file)
        output_path.write_text('\n'.join(report))

        print(f"✅ Master report saved: {output_path}")
        print(f"   File size: {output_path.stat().st_size:,} bytes")
        print(f"   Total pages: ~{len(report) // 50} pages")

        return str(output_path)

    def export_json(self, analysis: Dict, output_file: str = "criminal_complaint_analysis.json"):
        """Export analysis to JSON for programmatic access"""
        output_path = Path(output_file)
        with open(output_path, 'w') as f:
            json.dump(analysis, f, indent=2, default=str)

        print(f"✅ JSON export saved: {output_path}")
        return str(output_path)

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Analyze documents against criminal complaint')
    parser.add_argument('--claim', help='Analyze specific claim ID (e.g., FS-001-JAMAICA-FLIGHT)')
    parser.add_argument('--export-report', default='MASTER_PERJURY_REPORT.md', help='Output markdown report file')
    parser.add_argument('--export-json', default='criminal_complaint_analysis.json', help='Output JSON file')
    parser.add_argument('--no-export', action='store_true', help='Skip export, just print results')
    args = parser.parse_args()

    # Get credentials
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

    if not all([SUPABASE_URL, SUPABASE_KEY]):
        print("❌ Missing environment variables!")
        print("   Required: SUPABASE_URL, SUPABASE_KEY")
        sys.exit(1)

    # Create analyzer
    analyzer = CriminalComplaintAnalyzer(SUPABASE_URL, SUPABASE_KEY)

    # Run analysis
    if args.claim:
        # Analyze single claim
        all_documents = analyzer.query_all_documents()
        claim = next((c for c in PERJURY_COMPLAINT_2025['false_statements'] if c['id'] == args.claim), None)

        if not claim:
            print(f"❌ Claim not found: {args.claim}")
            sys.exit(1)

        result = analyzer.analyze_claim(claim, all_documents)
        print(json.dumps(result, indent=2, default=str))
    else:
        # Analyze all claims
        analysis = analyzer.analyze_all_claims()

        # Export reports
        if not args.no_export:
            analyzer.export_master_report(analysis, args.export_report)
            analyzer.export_json(analysis, args.export_json)

if __name__ == "__main__":
    main()
