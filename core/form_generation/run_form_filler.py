#!/usr/bin/env python3
"""
Emergency Legal Form Filler - CLI Wrapper
Run: python run_form_filler.py --case-id J24-00478 --output ./filing_package
"""

import argparse
import sys
from pathlib import Path

try:
    import toml
except ImportError:
    print("❌ Missing toml. Install: pip install toml")
    sys.exit(1)

from emergency_form_filler import EmergencyFormFiller


def load_config(config_path: str = None) -> dict:
    """
    Load configuration from config.toml

    Args:
        config_path: Path to config file (default: repo root config.toml)

    Returns:
        Dictionary with API credentials
    """
    if config_path is None:
        # Try to find config.toml in repo root
        current = Path(__file__).resolve()
        repo_root = current.parent.parent.parent  # core/form_generation/ -> core/ -> repo/
        config_path = repo_root / "config.toml"

    if not Path(config_path).exists():
        print(f"❌ Config file not found: {config_path}")
        print(f"\nCreate config.toml with:")
        print("""
[apis]
supabase_url = "https://jvjlhxodmbkodzmggwpu.supabase.co"
supabase_key = "your-service-role-key-here"
anthropic_api_key = "your-anthropic-key-here"
        """)
        sys.exit(1)

    try:
        config = toml.load(config_path)
        return config
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Emergency Legal Form Filler - Generate JV-180 and JV-575 forms',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate forms for case J24-00478
  python run_form_filler.py --case-id J24-00478 --output ./filing_package

  # Use custom config file
  python run_form_filler.py --case-id J24-00478 --output ./output --config /path/to/config.toml

  # Verbose output
  python run_form_filler.py --case-id J24-00478 --output ./output --verbose

Output:
  - {case_id}_JV180_JV575.pdf (petition and declaration)
  - {case_id}_Evidence_Summary.pdf (exhibit list)
        """
    )

    parser.add_argument(
        '--case-id',
        required=True,
        help='Case identifier (e.g., J24-00478)'
    )

    parser.add_argument(
        '--output',
        required=True,
        help='Output directory for generated files'
    )

    parser.add_argument(
        '--config',
        default=None,
        help='Path to config.toml (default: repo root config.toml)'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    # Load configuration
    print("🔧 Loading configuration...")
    config = load_config(args.config)

    # Get API credentials
    apis = config.get('apis', {})
    supabase_url = apis.get('supabase_url')
    supabase_key = apis.get('supabase_key')
    anthropic_key = apis.get('anthropic_api_key')

    # Validate credentials
    if not supabase_url:
        print("❌ Missing supabase_url in config.toml [apis] section")
        sys.exit(1)

    if not supabase_key:
        print("❌ Missing supabase_key in config.toml [apis] section")
        print("   Recommended: Use service_role key for full database access")
        sys.exit(1)

    if not anthropic_key:
        print("❌ Missing anthropic_api_key in config.toml [apis] section")
        print("   Get your key at: https://console.anthropic.com/")
        sys.exit(1)

    # Initialize form filler
    print("✅ Configuration loaded")
    print(f"   Supabase: {supabase_url}")
    print(f"   Anthropic: API key configured")

    try:
        filler = EmergencyFormFiller(
            supabase_url=supabase_url,
            supabase_key=supabase_key,
            anthropic_key=anthropic_key
        )

        # Run form generation
        filler.run(
            case_id=args.case_id,
            output_dir=args.output
        )

        print("\n✅ SUCCESS! Forms generated successfully.")

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)

    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
