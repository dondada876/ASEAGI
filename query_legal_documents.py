#!/usr/bin/env python3
"""
Query Legal Documents from Supabase
PROJ344 - Query Interface for Legal Assessment
"""

import os
import sys
from supabase import create_client
import json
from datetime import datetime

class LegalDocumentQuery:
    def __init__(self, supabase_url, supabase_key):
        self.client = create_client(supabase_url, supabase_key)

    def get_total_count(self):
        """Get total count of documents in database"""
        result = self.client.table('legal_documents').select('id', count='exact').execute()
        return result.count

    def get_smoking_guns(self, min_relevancy=900):
        """Get smoking gun documents (relevancy 900+)"""
        result = self.client.table('legal_documents')\
            .select('*')\
            .gte('relevancy_number', min_relevancy)\
            .order('relevancy_number', desc=True)\
            .execute()
        return result.data

    def get_critical_documents(self):
        """Get critical importance documents"""
        result = self.client.table('legal_documents')\
            .select('*')\
            .eq('importance', 'CRITICAL')\
            .order('relevancy_number', desc=True)\
            .execute()
        return result.data

    def get_perjury_documents(self):
        """Get documents with perjury indicators"""
        result = self.client.table('legal_documents')\
            .select('*')\
            .eq('contains_false_statements', True)\
            .order('relevancy_number', desc=True)\
            .execute()
        return result.data

    def search_documents(self, keyword):
        """Search documents by keyword"""
        result = self.client.table('legal_documents')\
            .select('*')\
            .ilike('document_title', f'%{keyword}%')\
            .order('relevancy_number', desc=True)\
            .execute()
        return result.data

    def get_by_document_type(self, doc_type):
        """Get documents by type (PLCR, ORDR, DECL, etc.)"""
        result = self.client.table('legal_documents')\
            .select('*')\
            .eq('document_type', doc_type)\
            .order('relevancy_number', desc=True)\
            .execute()
        return result.data

    def get_statistics(self):
        """Get database statistics"""
        stats = {}

        # Total documents
        stats['total_documents'] = self.get_total_count()

        # By importance
        for importance in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            result = self.client.table('legal_documents')\
                .select('id', count='exact')\
                .eq('importance', importance)\
                .execute()
            stats[f'{importance.lower()}_importance'] = result.count

        # By document type
        types_result = self.client.table('legal_documents')\
            .select('document_type')\
            .execute()

        type_counts = {}
        for doc in types_result.data:
            doc_type = doc.get('document_type', 'UNKNOWN')
            type_counts[doc_type] = type_counts.get(doc_type, 0) + 1

        stats['by_type'] = type_counts

        # Smoking guns
        smoking_guns = self.get_smoking_guns()
        stats['smoking_guns_count'] = len(smoking_guns)

        # Perjury indicators
        perjury_docs = self.get_perjury_documents()
        stats['perjury_documents'] = len(perjury_docs)

        # Relevancy distribution
        high_rel = self.client.table('legal_documents')\
            .select('id', count='exact')\
            .gte('relevancy_number', 800)\
            .execute()
        stats['high_relevancy_800plus'] = high_rel.count

        mid_rel = self.client.table('legal_documents')\
            .select('id', count='exact')\
            .gte('relevancy_number', 600)\
            .lt('relevancy_number', 800)\
            .execute()
        stats['mid_relevancy_600_799'] = mid_rel.count

        return stats

    def print_document(self, doc):
        """Pretty print a document"""
        print(f"\n{'='*80}")
        print(f"📄 {doc['document_title']}")
        print(f"{'='*80}")
        print(f"Type: {doc.get('document_type', 'N/A')}")
        print(f"Date: {doc.get('document_date', 'N/A')}")
        print(f"File: {doc['original_filename']}")
        print(f"\n🎯 PROJ344 Scores:")
        print(f"   Relevancy: {doc['relevancy_number']}/999")
        print(f"   Legal:     {doc['legal_number']}/999")
        print(f"   Micro:     {doc['micro_number']}/999")
        print(f"   Macro:     {doc['macro_number']}/999")
        print(f"\n📊 Assessment:")
        print(f"   Importance: {doc.get('importance', 'N/A')}")
        print(f"   Purpose: {doc.get('purpose', 'N/A')}")
        print(f"   Status: {doc.get('status', 'N/A')}")
        print(f"\n📝 Summary:")
        print(f"   {doc.get('executive_summary', 'N/A')}")

        if doc.get('smoking_guns'):
            print(f"\n🔥 Smoking Guns:")
            for sg in doc['smoking_guns']:
                print(f"   • {sg}")

        if doc.get('key_quotes'):
            print(f"\n💬 Key Quotes:")
            for quote in doc['key_quotes'][:3]:  # First 3 quotes
                print(f"   • {quote}")

        if doc.get('perjury_indicators'):
            print(f"\n⚠️  Perjury Indicators:")
            for pi in doc['perjury_indicators']:
                print(f"   • {pi}")

        print(f"{'='*80}")

def main():
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

    if not all([SUPABASE_URL, SUPABASE_KEY]):
        print("❌ Missing environment variables: SUPABASE_URL, SUPABASE_KEY")
        sys.exit(1)

    query = LegalDocumentQuery(SUPABASE_URL, SUPABASE_KEY)

    # Menu
    while True:
        print("\n" + "="*80)
        print("PROJ344 LEGAL DOCUMENT QUERY INTERFACE")
        print("="*80)
        print("\n1. Database Statistics")
        print("2. Smoking Gun Documents (900+ relevancy)")
        print("3. Critical Documents")
        print("4. Documents with Perjury Indicators")
        print("5. Search by Keyword")
        print("6. Filter by Document Type")
        print("7. Exit")
        print("\nEnter choice (1-7): ", end='')

        choice = input().strip()

        if choice == '1':
            print("\n📊 DATABASE STATISTICS")
            print("="*80)
            stats = query.get_statistics()
            print(f"\nTotal Documents: {stats['total_documents']}")
            print(f"\nBy Importance:")
            print(f"   Critical: {stats.get('critical_importance', 0)}")
            print(f"   High:     {stats.get('high_importance', 0)}")
            print(f"   Medium:   {stats.get('medium_importance', 0)}")
            print(f"   Low:      {stats.get('low_importance', 0)}")
            print(f"\nBy Relevancy:")
            print(f"   High (800+):  {stats.get('high_relevancy_800plus', 0)}")
            print(f"   Mid (600-799): {stats.get('mid_relevancy_600_799', 0)}")
            print(f"\nSpecial Categories:")
            print(f"   Smoking Guns: {stats['smoking_guns_count']}")
            print(f"   Perjury Indicators: {stats['perjury_documents']}")
            print(f"\nDocument Types:")
            for doc_type, count in sorted(stats['by_type'].items(), key=lambda x: x[1], reverse=True):
                print(f"   {doc_type}: {count}")

        elif choice == '2':
            print("\n🔥 SMOKING GUN DOCUMENTS (Relevancy 900+)")
            docs = query.get_smoking_guns()
            print(f"Found: {len(docs)} documents")
            for doc in docs:
                query.print_document(doc)

        elif choice == '3':
            print("\n⚠️  CRITICAL DOCUMENTS")
            docs = query.get_critical_documents()
            print(f"Found: {len(docs)} documents")
            for doc in docs:
                query.print_document(doc)

        elif choice == '4':
            print("\n🚨 DOCUMENTS WITH PERJURY INDICATORS")
            docs = query.get_perjury_documents()
            print(f"Found: {len(docs)} documents")
            for doc in docs:
                query.print_document(doc)

        elif choice == '5':
            keyword = input("\nEnter search keyword: ").strip()
            print(f"\n🔍 SEARCHING FOR: {keyword}")
            docs = query.search_documents(keyword)
            print(f"Found: {len(docs)} documents")
            for doc in docs:
                query.print_document(doc)

        elif choice == '6':
            print("\nDocument Types: PLCR, ORDR, DECL, MOTN, RESP, EVID, TRNS, TEXT, OTHER")
            doc_type = input("Enter document type: ").strip().upper()
            print(f"\n📋 DOCUMENTS OF TYPE: {doc_type}")
            docs = query.get_by_document_type(doc_type)
            print(f"Found: {len(docs)} documents")
            for doc in docs:
                query.print_document(doc)

        elif choice == '7':
            print("\n✅ Goodbye!")
            break

        else:
            print("\n❌ Invalid choice. Please enter 1-7.")

if __name__ == "__main__":
    main()
