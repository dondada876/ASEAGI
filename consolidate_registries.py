#!/usr/bin/env python3
"""
Registry Consolidation Script
Merges document registries from multiple sources (laptop, Mac Mini, Google Drive)
and uploads to Supabase master registry with deduplication
"""

import json
import os
from pathlib import Path
from typing import List, Dict
from datetime import datetime

try:
    from supabase import create_client
except ImportError:
    print("[ERROR] supabase library not installed")
    print("Run: pip install supabase")
    exit(1)


class RegistryConsolidator:
    """Consolidate multiple source registries into master Supabase registry"""

    def __init__(self, supabase_url: str, supabase_key: str):
        self.supabase = create_client(supabase_url, supabase_key)
        self.all_documents = {}  # file_hash -> consolidated doc
        self.duplicates = []
        self.stats = {
            'total_files': 0,
            'unique_documents': 0,
            'duplicates_across_sources': 0,
            'uploaded': 0,
            'updated': 0,
            'errors': 0
        }

    def load_registry(self, registry_file: str) -> Dict:
        """Load a registry JSON file"""

        if not os.path.exists(registry_file):
            print(f"❌ Registry file not found: {registry_file}")
            return {'documents': [], 'source': 'unknown'}

        with open(registry_file) as f:
            data = json.load(f)

        print(f"✅ Loaded: {registry_file}")
        print(f"   Source: {data.get('source', 'unknown')}")
        print(f"   Documents: {len(data.get('documents', []))}")
        print()

        return data

    def consolidate(self, registry_files: List[str]):
        """Merge all source registries"""

        print("=" * 80)
        print("CONSOLIDATING REGISTRIES")
        print("=" * 80)
        print()

        for registry_file in registry_files:
            data = self.load_registry(registry_file)
            source = data.get('source', 'unknown')

            for doc in data.get('documents', []):
                self.stats['total_files'] += 1
                file_hash = doc['file_hash']

                if file_hash in self.all_documents:
                    # Duplicate across sources - add location
                    self.stats['duplicates_across_sources'] += 1

                    existing = self.all_documents[file_hash]

                    # Add new location
                    existing['source_locations'].append({
                        'source': source,
                        'path': doc.get('file_path', doc.get('gdrive_link', '')),
                        'discovered': doc.get('discovered', datetime.now().isoformat())
                    })

                    self.duplicates.append({
                        'file_hash': file_hash,
                        'file_name': doc['file_name'],
                        'locations': len(existing['source_locations'])
                    })

                    print(f"⚠️  DUPLICATE: {doc['file_name']}")
                    print(f"   Hash: {file_hash[:12]}...")
                    print(f"   Now in {len(existing['source_locations'])} locations")
                    print()

                else:
                    # New unique document
                    self.stats['unique_documents'] += 1

                    self.all_documents[file_hash] = {
                        'file_hash': file_hash,
                        'file_name': doc['file_name'],
                        'file_type': doc.get('file_type', ''),
                        'file_extension': doc.get('file_extension', ''),
                        'file_size': doc.get('file_size', 0),
                        'last_modified': doc.get('last_modified'),
                        'primary_location': source,
                        'source_locations': [{
                            'source': source,
                            'path': doc.get('file_path', doc.get('gdrive_link', '')),
                            'discovered': doc.get('discovered', datetime.now().isoformat())
                        }],
                        'processing_status': 'pending',
                        'is_cloud_backed_up': (source == 'gdrive'),
                        'first_discovered': doc.get('discovered', datetime.now().isoformat())
                    }

        print("=" * 80)
        print("CONSOLIDATION COMPLETE")
        print("=" * 80)
        print(f"Total files scanned: {self.stats['total_files']}")
        print(f"Unique documents: {self.stats['unique_documents']}")
        print(f"Duplicates across sources: {self.stats['duplicates_across_sources']}")
        print()

    def upload_to_supabase(self):
        """Upload consolidated registry to Supabase"""

        print("=" * 80)
        print("UPLOADING TO SUPABASE")
        print("=" * 80)
        print()

        print(f"📤 Uploading {len(self.all_documents)} unique documents...")
        print()

        for i, doc in enumerate(self.all_documents.values(), 1):
            try:
                # Check if document already exists
                existing = self.supabase.table('master_document_registry')\
                    .select('id, source_locations')\
                    .eq('file_hash', doc['file_hash'])\
                    .execute()

                if existing.data:
                    # Document exists - update locations if needed
                    existing_doc = existing.data[0]
                    existing_locations = existing_doc.get('source_locations', [])

                    # Merge locations
                    all_locations = existing_locations + doc['source_locations']

                    # Remove duplicate locations
                    unique_locations = []
                    seen = set()
                    for loc in all_locations:
                        key = f"{loc['source']}:{loc['path']}"
                        if key not in seen:
                            unique_locations.append(loc)
                            seen.add(key)

                    # Update
                    self.supabase.table('master_document_registry')\
                        .update({
                            'source_locations': unique_locations,
                            'last_seen': datetime.now().isoformat()
                        })\
                        .eq('file_hash', doc['file_hash'])\
                        .execute()

                    self.stats['updated'] += 1
                    print(f"[{i}/{len(self.all_documents)}] ✏️  UPDATED: {doc['file_name']}")
                    print(f"   Locations: {len(unique_locations)}")

                else:
                    # New document - insert
                    self.supabase.table('master_document_registry')\
                        .insert(doc)\
                        .execute()

                    self.stats['uploaded'] += 1
                    print(f"[{i}/{len(self.all_documents)}] ✅ NEW: {doc['file_name']}")

            except Exception as e:
                self.stats['errors'] += 1
                print(f"[{i}/{len(self.all_documents)}] ❌ ERROR: {doc['file_name']}")
                print(f"   {e}")

        print()
        print("=" * 80)
        print("UPLOAD COMPLETE")
        print("=" * 80)
        print(f"New documents: {self.stats['uploaded']}")
        print(f"Updated documents: {self.stats['updated']}")
        print(f"Errors: {self.stats['errors']}")
        print()

    def print_duplicate_summary(self):
        """Print summary of duplicates across sources"""

        if not self.duplicates:
            print("✅ No duplicates found across sources")
            return

        print()
        print("=" * 80)
        print("DUPLICATES ACROSS SOURCES")
        print("=" * 80)
        print()

        # Group by location count
        by_count = {}
        for dup in self.duplicates:
            count = dup['locations']
            if count not in by_count:
                by_count[count] = []
            by_count[count].append(dup)

        for count in sorted(by_count.keys(), reverse=True):
            dups = by_count[count]
            print(f"📍 Found in {count} locations: ({len(dups)} documents)")
            for dup in dups[:10]:  # Show first 10
                print(f"   - {dup['file_name']}")
            if len(dups) > 10:
                print(f"   ... and {len(dups) - 10} more")
            print()

    def generate_report(self, output_file: str = 'consolidation_report.json'):
        """Generate consolidation report"""

        report = {
            'consolidation_date': datetime.now().isoformat(),
            'stats': self.stats,
            'duplicates': self.duplicates,
            'unique_documents': len(self.all_documents),
            'sources': list(set(loc['source']
                              for doc in self.all_documents.values()
                              for loc in doc['source_locations']))
        }

        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"📄 Report saved: {output_file}")
        print()


def main():
    """Main entry point"""

    print()
    print("=" * 80)
    print("REGISTRY CONSOLIDATION TOOL")
    print("Merge document registries from multiple sources")
    print("=" * 80)
    print()

    # Supabase credentials
    supabase_url = os.environ.get('SUPABASE_URL', 'https://jvjlhxodmbkodzmggwpu.supabase.co')
    supabase_key = os.environ.get('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2amxoeG9kbWJrb2R6bWdnd3B1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIyMjMxOTAsImV4cCI6MjA3Nzc5OTE5MH0.ai65vVW816bNAV56XiuRxp5PE5IhBkMGPx3IbxfPh8c')

    # Registry files to consolidate
    registry_files = [
        'laptop_document_registry.json',
        'mac_mini_document_registry.json',
        'gdrive_document_registry.json'
    ]

    # Check which files exist
    print("📁 Looking for registry files:")
    existing_files = []
    for file in registry_files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
            existing_files.append(file)
        else:
            print(f"   ❌ {file} (not found)")
    print()

    if not existing_files:
        print("❌ No registry files found!")
        print()
        print("Please run:")
        print("  1. python3 multi_source_scanner.py (on each machine)")
        print("  2. python3 google_drive_scanner.py (optional)")
        print()
        return

    input(f"Press Enter to consolidate {len(existing_files)} registries...")
    print()

    # Initialize consolidator
    consolidator = RegistryConsolidator(supabase_url, supabase_key)

    # Consolidate
    consolidator.consolidate(existing_files)

    # Show duplicate summary
    consolidator.print_duplicate_summary()

    # Upload to Supabase
    print("Ready to upload to Supabase master registry.")
    confirm = input("Continue? (yes/no): ").strip().lower()

    if confirm == 'yes':
        consolidator.upload_to_supabase()
        consolidator.generate_report()

        print()
        print("=" * 80)
        print("✅ CONSOLIDATION COMPLETE")
        print("=" * 80)
        print()
        print("Next steps:")
        print("1. Review master registry in Supabase")
        print("2. Run: python3 process_all_sources.py")
        print("3. Generate embeddings for all documents")
        print()
    else:
        print("❌ Upload cancelled")


if __name__ == "__main__":
    main()
