#!/usr/bin/env python3
"""
Police Report Page Scanner & Labeling System
Scans police report images/PDFs, identifies page numbers, and applies PX naming convention

Naming Convention:
- PX0 = Document with no pages (0 pages)
- PX01 = Document with 1 page
- PX06-P1-P6 = Document with 6 pages, showing page 1 of 6
- PX12-P1-P12 = Document with 12 pages, showing page 1 of 12

Author: ASEAGI System
Date: 2025-11-05
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import anthropic
from PIL import Image
import PyPDF2

# ============================================================================
# CONFIGURATION
# ============================================================================

# Get Anthropic API key
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
if not ANTHROPIC_API_KEY:
    print("⚠️  Warning: ANTHROPIC_API_KEY not set. Set it with:")
    print("   export ANTHROPIC_API_KEY='your-key-here'")

# Supported file types
IMAGE_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff']
PDF_EXTENSION = '.pdf'

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def is_police_report(file_path: str) -> bool:
    """
    Determine if a file is likely a police report based on filename
    """
    filename = os.path.basename(file_path).lower()

    police_keywords = [
        'police', 'report', 'incident', 'cad', 'call', 'dispatch',
        'officer', 'deputy', 'law enforcement', 'complaint',
        'arrest', 'citation', 'warrant', '911', 'emergency',
        'pd', 'sheriff', 'investigation', 'case number'
    ]

    return any(keyword in filename for keyword in police_keywords)


def analyze_image_for_page_info(image_path: str, api_key: str) -> Dict:
    """
    Use Claude Vision API to analyze image and extract page information
    Returns: {
        'is_police_report': bool,
        'page_number': int or None,
        'total_pages': int or None,
        'report_type': str,
        'case_number': str or None,
        'date': str or None,
        'confidence': float
    }
    """
    if not api_key:
        return {'error': 'No API key provided'}

    try:
        client = anthropic.Anthropic(api_key=api_key)

        # Read image
        with open(image_path, 'rb') as f:
            image_data = f.read()

        # Prepare image for Claude (base64 encode)
        import base64
        image_b64 = base64.b64encode(image_data).decode('utf-8')

        # Determine media type
        ext = Path(image_path).suffix.lower()
        media_type_map = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.tiff': 'image/tiff'
        }
        media_type = media_type_map.get(ext, 'image/jpeg')

        # Analyze with Claude
        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_b64
                        }
                    },
                    {
                        "type": "text",
                        "text": """Analyze this document image and extract the following information:

1. Is this a police report or law enforcement document? (yes/no)
2. What is the current page number shown? (look for "Page X of Y" or similar)
3. What is the total number of pages? (look for "Page X of Y" or similar)
4. What type of report is this? (Incident Report, CAD Report, Arrest Report, etc.)
5. Case/Incident number (if visible)
6. Report date (if visible)
7. Confidence level (0-100) that this is a police report

Return ONLY a valid JSON object with this exact structure:
{
    "is_police_report": true/false,
    "page_number": number or null,
    "total_pages": number or null,
    "report_type": "string or null",
    "case_number": "string or null",
    "date": "YYYY-MM-DD or null",
    "confidence": number (0-100)
}"""
                    }
                ]
            }]
        )

        # Parse response
        response_text = message.content[0].text.strip()

        # Extract JSON from response (might have markdown code blocks)
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
            return result
        else:
            return {'error': 'Could not parse response', 'raw': response_text}

    except Exception as e:
        return {'error': str(e)}


def analyze_pdf_for_page_info(pdf_path: str, api_key: str) -> Dict:
    """
    Analyze PDF to extract page information and determine if it's a police report
    For PDFs, we'll analyze the first page with Claude Vision
    """
    try:
        # Get PDF page count
        with open(pdf_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            total_pages = len(pdf_reader.pages)

            # Extract text from first page for quick analysis
            first_page_text = pdf_reader.pages[0].extract_text()

        # Quick text analysis for police report keywords
        police_keywords = ['police', 'officer', 'incident', 'report', 'case number', 'cad']
        is_likely_police = any(keyword in first_page_text.lower() for keyword in police_keywords)

        # For detailed analysis, convert first page to image and use Claude
        # (This would require pdf2image library - for now we'll use text analysis)

        result = {
            'is_police_report': is_likely_police,
            'page_number': 1,
            'total_pages': total_pages,
            'report_type': 'PDF Document',
            'case_number': None,
            'date': None,
            'confidence': 70 if is_likely_police else 30
        }

        # Try to extract case number from text
        case_patterns = [
            r'case\s*#?\s*:?\s*([A-Z0-9\-]+)',
            r'incident\s*#?\s*:?\s*([A-Z0-9\-]+)',
            r'report\s*#?\s*:?\s*([A-Z0-9\-]+)'
        ]

        for pattern in case_patterns:
            match = re.search(pattern, first_page_text, re.IGNORECASE)
            if match:
                result['case_number'] = match.group(1)
                break

        return result

    except Exception as e:
        return {'error': str(e)}


def generate_px_filename(
    original_name: str,
    page_info: Dict,
    current_page: Optional[int] = None
) -> str:
    """
    Generate PX-formatted filename based on page information

    Examples:
    - PX0_original_name.ext = No pages
    - PX01_original_name.ext = 1 page
    - PX06-P1-P6_original_name.ext = 6 pages, page 1
    - PX12-P5-P12_original_name.ext = 12 pages, page 5
    """
    # Get extension
    ext = Path(original_name).suffix
    base_name = Path(original_name).stem

    # Clean base name (remove existing PX notation if present)
    base_name = re.sub(r'^PX\d+(-P\d+-P\d+)?_', '', base_name)

    total_pages = page_info.get('total_pages')
    page_num = current_page or page_info.get('page_number', 1)

    # Generate PX code
    if total_pages is None or total_pages == 0:
        px_code = 'PX0'
    elif total_pages == 1:
        px_code = 'PX01'
    else:
        # Pad total pages to 2 digits
        total_str = f"{total_pages:02d}"
        page_str = f"{page_num:02d}" if page_num else '01'
        px_code = f"PX{total_str}-P{page_num}-P{total_pages}"

    return f"{px_code}_{base_name}{ext}"


def scan_and_tag_file(
    file_path: str,
    api_key: str,
    output_dir: Optional[str] = None,
    rename_file: bool = False
) -> Dict:
    """
    Scan a single file, analyze it, and optionally rename/tag it

    Returns:
    {
        'original_path': str,
        'new_name': str,
        'page_info': dict,
        'renamed': bool,
        'output_path': str or None
    }
    """
    result = {
        'original_path': file_path,
        'new_name': None,
        'page_info': None,
        'renamed': False,
        'output_path': None,
        'error': None
    }

    try:
        ext = Path(file_path).suffix.lower()

        # Analyze based on file type
        if ext in IMAGE_EXTENSIONS:
            page_info = analyze_image_for_page_info(file_path, api_key)
        elif ext == PDF_EXTENSION:
            page_info = analyze_pdf_for_page_info(file_path, api_key)
        else:
            result['error'] = f"Unsupported file type: {ext}"
            return result

        result['page_info'] = page_info

        # Check if it's a police report
        if not page_info.get('is_police_report', False):
            result['error'] = 'Not identified as police report'
            return result

        # Generate new filename
        original_name = os.path.basename(file_path)
        new_name = generate_px_filename(original_name, page_info)
        result['new_name'] = new_name

        # Optionally rename/move file
        if rename_file or output_dir:
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                new_path = os.path.join(output_dir, new_name)
            else:
                new_path = os.path.join(os.path.dirname(file_path), new_name)

            # Only rename if name is different
            if file_path != new_path:
                os.rename(file_path, new_path)
                result['renamed'] = True
                result['output_path'] = new_path
                print(f"✅ Renamed: {original_name} → {new_name}")
            else:
                print(f"ℹ️  Already named correctly: {new_name}")

        return result

    except Exception as e:
        result['error'] = str(e)
        return result


def scan_directory(
    directory: str,
    api_key: str,
    output_dir: Optional[str] = None,
    rename_files: bool = False,
    recursive: bool = True
) -> List[Dict]:
    """
    Scan all police report files in a directory
    """
    results = []

    # Find all relevant files
    path = Path(directory)

    if recursive:
        patterns = [f"**/*{ext}" for ext in IMAGE_EXTENSIONS + [PDF_EXTENSION]]
    else:
        patterns = [f"*{ext}" for ext in IMAGE_EXTENSIONS + [PDF_EXTENSION]]

    files = []
    for pattern in patterns:
        files.extend(path.glob(pattern))

    print(f"📂 Found {len(files)} potential documents in {directory}")

    # Filter for police reports based on filename
    police_files = [f for f in files if is_police_report(str(f))]
    print(f"🚔 {len(police_files)} files match police report patterns")

    # Process each file
    for i, file_path in enumerate(police_files, 1):
        print(f"\n[{i}/{len(police_files)}] Processing: {file_path.name}")

        result = scan_and_tag_file(
            str(file_path),
            api_key,
            output_dir,
            rename_files
        )

        results.append(result)

        # Print status
        if result.get('error'):
            print(f"  ⚠️  {result['error']}")
        else:
            page_info = result.get('page_info', {})
            print(f"  ✓ Confidence: {page_info.get('confidence', 0)}%")
            print(f"  ✓ Type: {page_info.get('report_type', 'Unknown')}")
            if page_info.get('case_number'):
                print(f"  ✓ Case: {page_info['case_number']}")
            print(f"  ✓ Pages: {page_info.get('total_pages', '?')}")

    return results


def generate_report(results: List[Dict], output_file: str = 'police_reports_scan_results.json'):
    """
    Generate a JSON report of all scanned files
    """
    report = {
        'scan_date': datetime.now().isoformat(),
        'total_files_processed': len(results),
        'successful_scans': len([r for r in results if not r.get('error')]),
        'files_renamed': len([r for r in results if r.get('renamed')]),
        'police_reports_found': len([r for r in results if r.get('page_info', {}).get('is_police_report')]),
        'results': results
    }

    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n📊 Report saved to: {output_file}")
    print(f"\n=== SUMMARY ===")
    print(f"Total files processed: {report['total_files_processed']}")
    print(f"Successful scans: {report['successful_scans']}")
    print(f"Files renamed: {report['files_renamed']}")
    print(f"Police reports identified: {report['police_reports_found']}")

    return report


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """
    Main execution function
    """
    import argparse

    parser = argparse.ArgumentParser(
        description='Police Report Page Scanner & Labeling System'
    )
    parser.add_argument(
        'directory',
        help='Directory to scan for police reports'
    )
    parser.add_argument(
        '--output-dir',
        help='Output directory for renamed files (default: rename in place)'
    )
    parser.add_argument(
        '--rename',
        action='store_true',
        help='Actually rename files (default: dry run)'
    )
    parser.add_argument(
        '--no-recursive',
        action='store_true',
        help='Do not scan subdirectories'
    )
    parser.add_argument(
        '--api-key',
        help='Anthropic API key (or set ANTHROPIC_API_KEY env var)'
    )
    parser.add_argument(
        '--report',
        default='police_reports_scan_results.json',
        help='Output report file'
    )

    args = parser.parse_args()

    # Get API key
    api_key = args.api_key or ANTHROPIC_API_KEY
    if not api_key:
        print("❌ Error: No API key provided")
        print("   Set ANTHROPIC_API_KEY environment variable or use --api-key")
        return 1

    # Validate directory
    if not os.path.isdir(args.directory):
        print(f"❌ Error: Directory not found: {args.directory}")
        return 1

    print("=" * 70)
    print("🚔 POLICE REPORT SCANNER & LABELING SYSTEM")
    print("=" * 70)
    print(f"Directory: {args.directory}")
    print(f"Recursive: {not args.no_recursive}")
    print(f"Rename files: {args.rename}")
    if args.output_dir:
        print(f"Output directory: {args.output_dir}")
    print("=" * 70)
    print()

    # Scan directory
    results = scan_directory(
        args.directory,
        api_key,
        args.output_dir,
        args.rename,
        not args.no_recursive
    )

    # Generate report
    generate_report(results, args.report)

    print("\n✅ Scan complete!")
    return 0


if __name__ == '__main__':
    exit(main())
