#!/usr/bin/env python3
"""
Code Repository Sentinel - Repository Scanner
==============================================
Scans code repositories and extracts comprehensive metadata for inventory management.

Purpose:
- Analyze local and remote repositories
- Extract metadata (language, dependencies, stats, etc.)
- Store in Supabase for querying
- Track changes over time

Usage:
    python repository_scanner.py /path/to/repo
    python repository_scanner.py /path/to/repo --scan-type full
    python repository_scanner.py --scan-all ~/projects
    python repository_scanner.py --repository-id github-owner-repo --update

Author: ASEAGI Team
Date: 2025-11-18
Version: 1.0.0
"""

import os
import sys
import json
import hashlib
import subprocess
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import argparse

try:
    from supabase import create_client, Client
except ImportError:
    print("ERROR: Supabase not installed")
    print("Install with: pip install supabase")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("WARNING: python-dotenv not installed. Using environment variables only.")


# ============================================================================
# Configuration
# ============================================================================

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: SUPABASE_URL and SUPABASE_KEY must be set")
    print("Set them in .env file or environment variables")
    sys.exit(1)

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# ============================================================================
# Language Detection & Statistics
# ============================================================================

LANGUAGE_EXTENSIONS = {
    'Python': ['.py', '.pyw', '.pyx', '.pyd'],
    'JavaScript': ['.js', '.mjs', '.cjs'],
    'TypeScript': ['.ts', '.tsx'],
    'Java': ['.java'],
    'C++': ['.cpp', '.cc', '.cxx', '.hpp', '.h'],
    'C': ['.c', '.h'],
    'Go': ['.go'],
    'Rust': ['.rs'],
    'Ruby': ['.rb'],
    'PHP': ['.php'],
    'Swift': ['.swift'],
    'Kotlin': ['.kt', '.kts'],
    'Shell': ['.sh', '.bash', '.zsh'],
    'HTML': ['.html', '.htm'],
    'CSS': ['.css', '.scss', '.sass', '.less'],
    'SQL': ['.sql'],
    'Markdown': ['.md', '.markdown'],
    'JSON': ['.json'],
    'YAML': ['.yaml', '.yml'],
    'XML': ['.xml'],
    'Dockerfile': ['Dockerfile'],
}

# Files to exclude from scanning
EXCLUDE_PATTERNS = [
    '.git', '.svn', '.hg',
    'node_modules', '__pycache__', '.pytest_cache',
    'venv', 'env', '.env',
    'dist', 'build', 'target',
    '.idea', '.vscode',
    '*.pyc', '*.pyo', '*.so', '*.dylib',
    '*.min.js', '*.min.css',
]


class RepositoryScanner:
    """Scans and analyzes code repositories"""

    def __init__(self, repo_path: str, scan_type: str = "full"):
        """
        Initialize scanner

        Args:
            repo_path: Path to repository
            scan_type: Type of scan (full, quick, incremental)
        """
        self.repo_path = Path(repo_path).resolve()
        self.scan_type = scan_type
        self.scan_start_time = datetime.now()

        if not self.repo_path.exists():
            raise ValueError(f"Repository path does not exist: {repo_path}")

        # Results
        self.metadata = {}
        self.file_stats = {}
        self.dependencies = {}
        self.git_info = {}

    # ========================================================================
    # Main Scan Method
    # ========================================================================

    def scan(self) -> Dict:
        """
        Perform comprehensive repository scan

        Returns:
            Dictionary with all repository metadata
        """
        print(f"\n🔍 Scanning repository: {self.repo_path}")
        print(f"📊 Scan type: {self.scan_type}")
        print(f"⏰ Started at: {self.scan_start_time}\n")

        # Extract basic information
        self._extract_basic_info()

        # Git information (if applicable)
        if self._is_git_repo():
            self._extract_git_info()

        # Scan files and calculate statistics
        self._scan_files()

        # Detect primary language
        self._detect_primary_language()

        # Scan for dependencies
        self._scan_dependencies()

        # Check for important files
        self._check_important_files()

        # Calculate code quality indicators
        self._calculate_quality_metrics()

        # Build final metadata
        self._build_metadata()

        scan_duration = (datetime.now() - self.scan_start_time).total_seconds()
        print(f"\n✅ Scan completed in {scan_duration:.2f} seconds")

        return self.metadata

    # ========================================================================
    # Basic Information Extraction
    # ========================================================================

    def _extract_basic_info(self):
        """Extract basic repository information"""
        self.metadata['repository_name'] = self.repo_path.name
        self.metadata['local_path'] = str(self.repo_path)
        self.metadata['repository_type'] = 'local'  # Will update if git repo

    # ========================================================================
    # Git Information
    # ========================================================================

    def _is_git_repo(self) -> bool:
        """Check if repository is a git repository"""
        return (self.repo_path / '.git').exists()

    def _run_git_command(self, cmd: List[str]) -> Optional[str]:
        """Run git command and return output"""
        try:
            result = subprocess.run(
                ['git'] + cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return None
        except Exception as e:
            print(f"⚠️  Git command failed: {e}")
            return None

    def _extract_git_info(self):
        """Extract git repository information"""
        print("📦 Extracting git information...")

        # Remote origin URL
        remote_url = self._run_git_command(['config', '--get', 'remote.origin.url'])
        if remote_url:
            self.git_info['remote_origin'] = remote_url
            self.metadata['remote_origin'] = remote_url

            # Parse GitHub/GitLab URL
            if 'github.com' in remote_url:
                self.metadata['repository_type'] = 'github'
                # Extract owner/repo from URL
                match = re.search(r'github\.com[:/]([^/]+)/([^/\.]+)', remote_url)
                if match:
                    owner, repo = match.groups()
                    self.metadata['repository_id'] = f'github-{owner}-{repo}'
                    self.metadata['repository_url'] = f'https://github.com/{owner}/{repo}'
                    self.metadata['owner_name'] = owner
            elif 'gitlab.com' in remote_url:
                self.metadata['repository_type'] = 'gitlab'
            elif 'bitbucket.org' in remote_url:
                self.metadata['repository_type'] = 'bitbucket'

        # Default branch
        default_branch = self._run_git_command(['rev-parse', '--abbrev-ref', 'HEAD'])
        if default_branch:
            self.metadata['default_branch'] = default_branch

        # Latest commit
        commit_hash = self._run_git_command(['rev-parse', 'HEAD'])
        if commit_hash:
            self.metadata['latest_commit_hash'] = commit_hash

        commit_date = self._run_git_command(['log', '-1', '--format=%ci'])
        if commit_date:
            self.metadata['latest_commit_date'] = commit_date

        commit_message = self._run_git_command(['log', '-1', '--format=%s'])
        if commit_message:
            self.metadata['latest_commit_message'] = commit_message

        # Total commits
        commit_count = self._run_git_command(['rev-list', '--count', 'HEAD'])
        if commit_count:
            self.metadata['total_commits'] = int(commit_count)

        # Total branches
        branch_count = self._run_git_command(['branch', '-a'])
        if branch_count:
            self.metadata['total_branches'] = len(branch_count.split('\n'))

        # First commit date
        first_commit_date = self._run_git_command(['log', '--reverse', '--format=%ci', '--max-count=1'])
        if first_commit_date:
            self.metadata['first_commit_date'] = first_commit_date

        print(f"   ✓ Git repository detected")
        print(f"   ✓ Remote: {remote_url}")
        print(f"   ✓ Branch: {default_branch}")
        print(f"   ✓ Commits: {commit_count}")

    # ========================================================================
    # File Scanning
    # ========================================================================

    def _should_exclude(self, path: Path) -> bool:
        """Check if path should be excluded"""
        path_str = str(path)
        for pattern in EXCLUDE_PATTERNS:
            if pattern in path_str:
                return True
        return False

    def _count_lines(self, file_path: Path) -> int:
        """Count lines in a file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return sum(1 for _ in f)
        except:
            return 0

    def _scan_files(self):
        """Scan all files in repository"""
        print("📂 Scanning files...")

        total_files = 0
        total_lines = 0
        language_stats = {}
        file_types = {}

        for root, dirs, files in os.walk(self.repo_path):
            # Exclude directories
            dirs[:] = [d for d in dirs if not self._should_exclude(Path(root) / d)]

            for file in files:
                file_path = Path(root) / file

                if self._should_exclude(file_path):
                    continue

                total_files += 1

                # Get file extension
                ext = file_path.suffix.lower()

                # Count lines
                lines = self._count_lines(file_path)
                total_lines += lines

                # Track language statistics
                for lang, extensions in LANGUAGE_EXTENSIONS.items():
                    if ext in extensions or file in extensions:
                        if lang not in language_stats:
                            language_stats[lang] = {'files': 0, 'lines': 0}
                        language_stats[lang]['files'] += 1
                        language_stats[lang]['lines'] += lines
                        break

                # Track file types
                if ext:
                    file_types[ext] = file_types.get(ext, 0) + 1

        self.file_stats = {
            'total_files': total_files,
            'total_lines': total_lines,
            'language_stats': language_stats,
            'file_types': file_types
        }

        self.metadata['total_files'] = total_files
        self.metadata['total_lines_of_code'] = total_lines

        print(f"   ✓ Scanned {total_files} files")
        print(f"   ✓ Total lines: {total_lines:,}")

    # ========================================================================
    # Language Detection
    # ========================================================================

    def _detect_primary_language(self):
        """Detect primary programming language"""
        language_stats = self.file_stats.get('language_stats', {})

        if not language_stats:
            self.metadata['primary_language'] = 'Unknown'
            return

        # Find language with most lines of code
        primary = max(language_stats.items(), key=lambda x: x[1]['lines'])
        self.metadata['primary_language'] = primary[0]

        # Store language breakdown as JSON
        breakdown = {lang: stats['lines'] for lang, stats in language_stats.items()}
        self.metadata['language_breakdown'] = breakdown

        print(f"   ✓ Primary language: {primary[0]} ({primary[1]['lines']:,} lines)")

    # ========================================================================
    # Dependency Scanning
    # ========================================================================

    def _scan_dependencies(self):
        """Scan for dependencies (requirements.txt, package.json, etc.)"""
        print("📦 Scanning dependencies...")

        dependencies = {}

        # Python: requirements.txt
        requirements_file = self.repo_path / 'requirements.txt'
        if requirements_file.exists():
            deps = self._parse_requirements(requirements_file)
            dependencies.update(deps)
            self.metadata['framework'] = self._detect_python_framework(deps)

        # Python: setup.py
        setup_file = self.repo_path / 'setup.py'
        if setup_file.exists():
            self.metadata['has_setup_py'] = True

        # Node.js: package.json
        package_json = self.repo_path / 'package.json'
        if package_json.exists():
            deps = self._parse_package_json(package_json)
            dependencies.update(deps)
            self.metadata['framework'] = self._detect_js_framework(deps)

        # Go: go.mod
        go_mod = self.repo_path / 'go.mod'
        if go_mod.exists():
            self.metadata['framework'] = 'Go'

        # Rust: Cargo.toml
        cargo_toml = self.repo_path / 'Cargo.toml'
        if cargo_toml.exists():
            self.metadata['framework'] = 'Rust'

        self.dependencies = dependencies
        self.metadata['dependencies'] = dependencies

        if dependencies:
            print(f"   ✓ Found {len(dependencies)} dependencies")

    def _parse_requirements(self, file_path: Path) -> Dict:
        """Parse Python requirements.txt"""
        deps = {}
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Parse package==version or package>=version
                        match = re.match(r'([a-zA-Z0-9\-_]+)(==|>=|<=|>|<|~=)(.+)', line)
                        if match:
                            pkg, op, ver = match.groups()
                            deps[pkg] = ver
                        else:
                            deps[line] = 'latest'
        except:
            pass
        return deps

    def _parse_package_json(self, file_path: Path) -> Dict:
        """Parse Node.js package.json"""
        deps = {}
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                if 'dependencies' in data:
                    deps.update(data['dependencies'])
        except:
            pass
        return deps

    def _detect_python_framework(self, deps: Dict) -> Optional[str]:
        """Detect Python framework from dependencies"""
        if 'streamlit' in deps:
            return 'Streamlit'
        elif 'django' in deps:
            return 'Django'
        elif 'flask' in deps:
            return 'Flask'
        elif 'fastapi' in deps:
            return 'FastAPI'
        return None

    def _detect_js_framework(self, deps: Dict) -> Optional[str]:
        """Detect JavaScript framework from dependencies"""
        if 'react' in deps:
            return 'React'
        elif 'vue' in deps:
            return 'Vue.js'
        elif 'angular' in deps:
            return 'Angular'
        elif 'next' in deps:
            return 'Next.js'
        elif 'express' in deps:
            return 'Express.js'
        return None

    # ========================================================================
    # Important Files Check
    # ========================================================================

    def _check_important_files(self):
        """Check for important files (README, tests, CI/CD, etc.)"""
        print("📋 Checking important files...")

        # README
        readme_files = ['README.md', 'README.rst', 'README.txt', 'README']
        self.metadata['has_readme'] = any((self.repo_path / f).exists() for f in readme_files)

        # Tests
        test_dirs = ['tests', 'test', '__tests__', 'spec']
        test_files = list(self.repo_path.glob('**/*test*.py')) + \
                     list(self.repo_path.glob('**/*spec*.js')) + \
                     list(self.repo_path.glob('**/*test*.ts'))
        self.metadata['has_tests'] = any((self.repo_path / d).exists() for d in test_dirs) or len(test_files) > 0

        # CI/CD
        ci_files = ['.github/workflows', '.gitlab-ci.yml', '.travis.yml', 'Jenkinsfile']
        self.metadata['has_ci_cd'] = any((self.repo_path / f).exists() for f in ci_files)

        # Documentation
        doc_dirs = ['docs', 'documentation', 'doc']
        self.metadata['has_documentation'] = any((self.repo_path / d).exists() for d in doc_dirs)

        # Docker
        self.metadata['has_docker'] = (self.repo_path / 'Dockerfile').exists() or \
                                      (self.repo_path / 'docker-compose.yml').exists()

        print(f"   ✓ README: {self.metadata['has_readme']}")
        print(f"   ✓ Tests: {self.metadata['has_tests']}")
        print(f"   ✓ CI/CD: {self.metadata['has_ci_cd']}")
        print(f"   ✓ Documentation: {self.metadata['has_documentation']}")

    # ========================================================================
    # Quality Metrics
    # ========================================================================

    def _calculate_quality_metrics(self):
        """Calculate code quality indicators"""
        score = 0

        # Has README (+20)
        if self.metadata.get('has_readme'):
            score += 20

        # Has tests (+25)
        if self.metadata.get('has_tests'):
            score += 25

        # Has CI/CD (+20)
        if self.metadata.get('has_ci_cd'):
            score += 20

        # Has documentation (+15)
        if self.metadata.get('has_documentation'):
            score += 15

        # Is git repo (+10)
        if self._is_git_repo():
            score += 10

        # Has recent activity (+10)
        if self.metadata.get('latest_commit_date'):
            try:
                commit_date = datetime.fromisoformat(self.metadata['latest_commit_date'].replace(' ', 'T').split('+')[0])
                days_since = (datetime.now() - commit_date).days
                if days_since < 30:
                    score += 10
            except:
                pass

        self.metadata['code_quality_score'] = min(score, 100)

    # ========================================================================
    # Build Final Metadata
    # ========================================================================

    def _build_metadata(self):
        """Build final metadata dictionary"""
        # Set defaults
        if 'repository_id' not in self.metadata:
            # Generate ID from path
            path_hash = hashlib.md5(str(self.repo_path).encode()).hexdigest()[:8]
            self.metadata['repository_id'] = f'local-{self.repo_path.name}-{path_hash}'

        # Set current status
        self.metadata['current_status'] = 'active'

        # Set scan timestamp
        self.metadata['last_scanned_at'] = datetime.now().isoformat()

        # Calculate created/modified dates
        try:
            stat = self.repo_path.stat()
            self.metadata['last_modified_date'] = datetime.fromtimestamp(stat.st_mtime).isoformat()
        except:
            pass

    # ========================================================================
    # Save to Database
    # ========================================================================

    def save_to_database(self) -> bool:
        """Save repository metadata to Supabase"""
        print(f"\n💾 Saving to database...")

        try:
            # Prepare data for insertion
            data = {
                'repository_id': self.metadata['repository_id'],
                'repository_name': self.metadata['repository_name'],
                'repository_url': self.metadata.get('repository_url'),
                'local_path': self.metadata.get('local_path'),
                'remote_origin': self.metadata.get('remote_origin'),
                'repository_type': self.metadata.get('repository_type', 'local'),
                'primary_language': self.metadata.get('primary_language'),
                'framework': self.metadata.get('framework'),
                'description': self.metadata.get('description'),
                'current_status': self.metadata.get('current_status', 'active'),
                'latest_commit_hash': self.metadata.get('latest_commit_hash'),
                'latest_commit_date': self.metadata.get('latest_commit_date'),
                'latest_commit_message': self.metadata.get('latest_commit_message'),
                'total_files': self.metadata.get('total_files', 0),
                'total_lines_of_code': self.metadata.get('total_lines_of_code', 0),
                'total_commits': self.metadata.get('total_commits', 0),
                'total_branches': self.metadata.get('total_branches', 0),
                'language_breakdown': self.metadata.get('language_breakdown'),
                'dependencies': self.metadata.get('dependencies'),
                'first_commit_date': self.metadata.get('first_commit_date'),
                'last_modified_date': self.metadata.get('last_modified_date'),
                'last_scanned_at': self.metadata.get('last_scanned_at'),
                'has_readme': self.metadata.get('has_readme', False),
                'has_tests': self.metadata.get('has_tests', False),
                'has_ci_cd': self.metadata.get('has_ci_cd', False),
                'has_documentation': self.metadata.get('has_documentation', False),
                'code_quality_score': self.metadata.get('code_quality_score', 0),
                'default_branch': self.metadata.get('default_branch', 'main'),
                'owner_name': self.metadata.get('owner_name'),
            }

            # Upsert (insert or update)
            result = supabase.table('repositories').upsert(data).execute()

            # Save scan history
            scan_history = {
                'repository_id': self.metadata['repository_id'],
                'scan_type': self.scan_type,
                'scan_duration_seconds': (datetime.now() - self.scan_start_time).total_seconds(),
                'files_scanned': self.metadata.get('total_files', 0),
                'scan_successful': True,
                'version_at_scan': self.metadata.get('version_number'),
                'commit_hash_at_scan': self.metadata.get('latest_commit_hash'),
            }

            supabase.table('repository_scan_history').insert(scan_history).execute()

            print(f"   ✅ Saved to database: {self.metadata['repository_id']}")
            return True

        except Exception as e:
            print(f"   ❌ Error saving to database: {e}")
            return False


# ============================================================================
# CLI Interface
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Code Repository Sentinel - Scan and analyze code repositories',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan single repository
  python repository_scanner.py /path/to/repo

  # Scan with specific type
  python repository_scanner.py /path/to/repo --scan-type full

  # Scan current directory
  python repository_scanner.py .

  # Scan ASEAGI project
  python repository_scanner.py /home/user/ASEAGI

  # Update existing repository
  python repository_scanner.py /path/to/repo --update
        """
    )

    parser.add_argument('path', help='Path to repository to scan')
    parser.add_argument('--scan-type', choices=['full', 'quick', 'incremental'],
                       default='full', help='Type of scan to perform')
    parser.add_argument('--update', action='store_true',
                       help='Update existing repository in database')
    parser.add_argument('--dry-run', action='store_true',
                       help='Scan but do not save to database')

    args = parser.parse_args()

    try:
        # Create scanner
        scanner = RepositoryScanner(args.path, args.scan_type)

        # Perform scan
        metadata = scanner.scan()

        # Save to database (unless dry-run)
        if not args.dry_run:
            scanner.save_to_database()
        else:
            print("\n🔍 DRY RUN - Not saving to database")
            print("\nMetadata:")
            print(json.dumps(metadata, indent=2, default=str))

        print(f"\n✅ Repository scan complete!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
