#!/usr/bin/env python3
"""
Multi-Source Document Scanner with Deduplication
Scans local directories and registers all documents with MD5 hash deduplication
"""

import os
import hashlib
from pathlib import Path
from datetime import datetime
import json
from typing import List, Dict, Optional

class MultiSourceScanner:
    """Scan multiple local directories and register documents"""

    def __init__(self, source_name='laptop'):
        self.source_name = source_name  # 'mac_mini' | 'laptop' | 'gdrive'
        self.registry = {}  # file_hash -> doc_info
        self.stats = {
            'scanned': 0,
            'new': 0,
            'duplicates': 0,
            'errors': 0
        }

    def calculate_hash(self, file_path: str) -> str:
        """Calculate MD5 hash for file"""
        md5 = hashlib.md5()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    md5.update(chunk)
            return md5.hexdigest()
        except Exception as e:
            raise Exception(f"Failed to hash {file_path}: {e}")

    def scan_directory(
        self,
        root_path: str,
        file_extensions: Optional[List[str]] = None,
        exclude_dirs: Optional[List[str]] = None
    ) -> Dict:
        """Recursively scan directory for documents"""

        if file_extensions is None:
            file_extensions = ['.rtf', '.doc', '.docx', '.pdf', '.txt', '.md',
                             '.mp4', '.mp3', '.wav', '.m4a']  # Added media

        if exclude_dirs is None:
            exclude_dirs = ['node_modules', '__pycache__', 'venv', '.git',
                          'dist', 'build', '.streamlit']

        discovered = []
        duplicates = []

        print("=" * 80)
        print(f"🔍 SCANNING: {root_path}")
        print(f"📂 SOURCE: {self.source_name}")
        print("=" * 80)
        print()

        if not os.path.exists(root_path):
            print(f"❌ Path not found: {root_path}")
            return {
                'source': self.source_name,
                'root_path': root_path,
                'discovered': [],
                'duplicates': [],
                'error': 'Path not found'
            }

        for root, dirs, files in os.walk(root_path):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs
                      if not d.startswith('.') and d not in exclude_dirs]

            for file in files:
                self.stats['scanned'] += 1
                file_path = Path(root) / file
                extension = file_path.suffix.lower()

                # Skip non-target files
                if extension not in file_extensions:
                    continue

                # Skip hidden files
                if file.startswith('.'):
                    continue

                try:
                    # Calculate hash
                    file_hash = self.calculate_hash(file_path)
                    file_stat = file_path.stat()

                    # Check if already seen (duplicate within this scan)
                    if file_hash in self.registry:
                        self.stats['duplicates'] += 1
                        duplicates.append({
                            'file_hash': file_hash,
                            'file_name': file,
                            'duplicate_path': str(file_path),
                            'original_path': self.registry[file_hash]['file_path'],
                            'source': self.source_name
                        })
                        print(f"⚠️  DUPLICATE: {file}")
                        print(f"   Original: {self.registry[file_hash]['file_path']}")
                        print(f"   Duplicate: {file_path}")
                        print()
                        continue

                    # New document - add to registry
                    doc_info = {
                        'file_hash': file_hash,
                        'file_name': file,
                        'file_path': str(file_path),
                        'file_type': extension.replace('.', ''),
                        'file_extension': extension,
                        'file_size': file_stat.st_size,
                        'last_modified': datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                        'source': self.source_name,
                        'discovered': datetime.now().isoformat()
                    }

                    self.registry[file_hash] = doc_info
                    discovered.append(doc_info)
                    self.stats['new'] += 1

                    # Format file size
                    size_mb = file_stat.st_size / (1024 * 1024)
                    if size_mb < 1:
                        size_str = f"{file_stat.st_size / 1024:.1f} KB"
                    else:
                        size_str = f"{size_mb:.1f} MB"

                    print(f"✅ NEW: {file} ({size_str})")

                except Exception as e:
                    self.stats['errors'] += 1
                    print(f"❌ ERROR: {file} - {e}")

        print()
        print("=" * 80)
        print(f"📊 SCAN COMPLETE: {self.source_name}")
        print("=" * 80)
        print(f"📁 Root path: {root_path}")
        print(f"🔍 Files scanned: {self.stats['scanned']}")
        print(f"✅ New documents: {self.stats['new']}")
        print(f"⚠️  Duplicates found: {self.stats['duplicates']}")
        print(f"❌ Errors: {self.stats['errors']}")
        print(f"📝 Total unique: {len(self.registry)}")
        print()

        return {
            'source': self.source_name,
            'root_path': root_path,
            'discovered': discovered,
            'duplicates': duplicates,
            'total_unique': len(self.registry),
            'stats': self.stats
        }

    def scan_multiple_directories(self, paths: List[str]) -> Dict:
        """Scan multiple directories"""

        all_discovered = []
        all_duplicates = []

        for path in paths:
            if os.path.exists(path):
                result = self.scan_directory(path)
                all_discovered.extend(result['discovered'])
                all_duplicates.extend(result['duplicates'])
            else:
                print(f"⚠️  Skipping non-existent path: {path}")
                print()

        return {
            'source': self.source_name,
            'paths_scanned': paths,
            'discovered': all_discovered,
            'duplicates': all_duplicates,
            'total_unique': len(self.registry),
            'stats': self.stats
        }

    def save_registry(self, output_path: str):
        """Save registry to JSON"""

        output = {
            'source': self.source_name,
            'scan_date': datetime.now().isoformat(),
            'documents': list(self.registry.values()),
            'total_documents': len(self.registry),
            'stats': self.stats
        }

        with open(output_path, 'w') as f:
            json.dump(output, f, indent=2)

        print(f"💾 Registry saved: {output_path}")
        print(f"   {len(self.registry)} unique documents")
        print()

    def print_summary(self):
        """Print summary of scan"""

        print()
        print("=" * 80)
        print("📊 SCAN SUMMARY")
        print("=" * 80)
        print(f"Source: {self.source_name}")
        print(f"Files scanned: {self.stats['scanned']}")
        print(f"New documents: {self.stats['new']}")
        print(f"Duplicates: {self.stats['duplicates']}")
        print(f"Errors: {self.stats['errors']}")
        print(f"Total unique: {len(self.registry)}")
        print()

        # File type breakdown
        type_counts = {}
        for doc in self.registry.values():
            file_type = doc['file_type']
            type_counts[file_type] = type_counts.get(file_type, 0) + 1

        print("📄 File Types:")
        for file_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"   {file_type}: {count}")
        print()

        # Total size
        total_size = sum(doc['file_size'] for doc in self.registry.values())
        total_mb = total_size / (1024 * 1024)
        if total_mb < 1024:
            print(f"💾 Total size: {total_mb:.1f} MB")
        else:
            print(f"💾 Total size: {total_mb / 1024:.1f} GB")
        print()


def main():
    """Main entry point"""

    print()
    print("=" * 80)
    print("MULTI-SOURCE DOCUMENT SCANNER")
    print("Scan local directories and register all documents with deduplication")
    print("=" * 80)
    print()

    # Detect current machine
    import platform
    hostname = platform.node()

    if 'Mac' in hostname or 'mac' in hostname:
        source_name = 'mac_mini'
    else:
        source_name = 'laptop'

    print(f"📍 Detected source: {source_name}")
    print()

    # Initialize scanner
    scanner = MultiSourceScanner(source_name=source_name)

    # Paths to scan
    paths_to_scan = [
        "/home/user/ASEAGI",
        "/home/user/Documents",
        "/home/user/Downloads",
        os.path.expanduser("~/Documents"),
        os.path.expanduser("~/Downloads")
    ]

    # Remove duplicates
    paths_to_scan = list(set(paths_to_scan))

    print("📂 Paths to scan:")
    for path in paths_to_scan:
        if os.path.exists(path):
            print(f"   ✅ {path}")
        else:
            print(f"   ❌ {path} (not found)")
    print()

    input("Press Enter to start scanning...")
    print()

    # Scan all paths
    result = scanner.scan_multiple_directories(paths_to_scan)

    # Print summary
    scanner.print_summary()

    # Save registry
    output_file = f"{source_name}_document_registry.json"
    scanner.save_registry(output_file)

    print("=" * 80)
    print("✅ SCAN COMPLETE")
    print("=" * 80)
    print()
    print("Next steps:")
    print(f"1. Review registry: {output_file}")
    print("2. Run scanner on other machines (Mac Mini, etc.)")
    print("3. Consolidate registries: python3 consolidate_registries.py")
    print("4. Upload to Supabase master registry")
    print()


if __name__ == "__main__":
    main()
