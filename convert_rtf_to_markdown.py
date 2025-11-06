#!/usr/bin/env python3
"""
RTF to Markdown Converter
Analyzes and converts RTF files to clean markdown format
"""

import re
import os
from pathlib import Path
from typing import Optional

class RTFToMarkdown:
    """Convert RTF files to clean markdown"""

    def __init__(self):
        self.rtf_files = [
            'PROJ344-Multi-dimensional-legal-document-scoring-S10.rtf',
            'PROJ344-Multi-dimensional-legal-document-scoring-system-s3.rtf',
            'PROJ344-Multi-dimensional-legal-document-scoring-system-s4.rtf',
            'PROJ344-Multi-dimensional-legal-document-scoring-system-s5.rtf',
            'PROJ344-Multi-dimensional-legal-document-scoring-system-s7.rtf',
            'PROJ344-Multi-dimensional-legal-document-scoring-system-s8.rtf',
            'PROJ344-Multi-dimensional-legal-document-scoring-system-s9.rtf',
            'PROJ344-Multi-dimensional-legal-document-scoring-system-s11.rtf'
        ]

    def strip_rtf_formatting(self, rtf_content: str) -> str:
        """Strip RTF formatting codes and extract plain text"""

        # Remove RTF header and font table
        text = re.sub(r'\\rtf1.*?\\fonttbl.*?\}', '', rtf_content, flags=re.DOTALL)
        text = re.sub(r'\\colortbl;.*?\}', '', text, flags=re.DOTALL)
        text = re.sub(r'\{\\expandedcolortbl;.*?\}', '', text, flags=re.DOTALL)

        # Remove margin/view settings
        text = re.sub(r'\\marg[lrtb]\d+', '', text)
        text = re.sub(r'\\view[wh]\d+', '', text)
        text = re.sub(r'\\viewkind\d+', '', text)
        text = re.sub(r'\\deftab\d+', '', text)

        # Remove paragraph formatting
        text = re.sub(r'\\pard.*?\\partightenfactor\d+', '', text)
        text = re.sub(r'\\pardeftab\d+', '', text)
        text = re.sub(r'\\sa\d+', '', text)

        # Remove font commands
        text = re.sub(r'\\f\d+', '', text)
        text = re.sub(r'\\fs\d+', '', text)

        # Remove color/stroke commands
        text = re.sub(r'\\cf\d+', '', text)
        text = re.sub(r'\\strokec\d+', '', text)
        text = re.sub(r'\\strokewidth\d+', '', text)
        text = re.sub(r'\\outl\d+', '', text)

        # Remove kerning/spacing
        text = re.sub(r'\\expnd\d+', '', text)
        text = re.sub(r'\\expndtw\d+', '', text)
        text = re.sub(r'\\kerning\d+', '', text)

        # Convert bold markers
        text = re.sub(r'\\b\s', '**', text)  # Start bold
        text = re.sub(r'\\b0\s', '**', text)  # End bold

        # Convert italic markers
        text = re.sub(r'\\i\s', '*', text)  # Start italic
        text = re.sub(r'\\i0\s', '*', text)  # End italic

        # Convert line breaks
        text = text.replace('\\', '\n')

        # Convert unicode characters
        text = re.sub(r'\\uc0\\u(\d+)\s*\\u(\d+)\s*', lambda m: chr(int(m.group(1))) + chr(int(m.group(2))), text)
        text = re.sub(r'\\uc0\\u(\d+)\s', lambda m: chr(int(m.group(1))), text)

        # Remove remaining backslash commands
        text = re.sub(r'\\[a-z]+\d*\s*', '', text)

        # Remove curly braces
        text = text.replace('{', '')
        text = text.replace('}', '')

        # Clean up multiple newlines
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)

        # Remove leading/trailing whitespace
        text = text.strip()

        return text

    def convert_rtf_file(self, rtf_path: str) -> Optional[str]:
        """Convert a single RTF file to markdown"""

        if not os.path.exists(rtf_path):
            print(f"❌ File not found: {rtf_path}")
            return None

        try:
            # Read RTF file
            with open(rtf_path, 'r', encoding='utf-8', errors='ignore') as f:
                rtf_content = f.read()

            # Convert to plain text
            markdown_content = self.strip_rtf_formatting(rtf_content)

            # Generate output filename
            md_path = rtf_path.replace('.rtf', '.md')

            # Add header
            filename = os.path.basename(rtf_path)
            header = f"# {filename.replace('.rtf', '').replace('-', ' ').title()}\n\n"
            header += f"**Converted from:** {filename}\n\n"
            header += "---\n\n"

            final_content = header + markdown_content

            # Write markdown file
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(final_content)

            rtf_size = os.path.getsize(rtf_path) / 1024
            md_size = os.path.getsize(md_path) / 1024

            print(f"✅ Converted: {filename}")
            print(f"   RTF: {rtf_size:.1f} KB → MD: {md_size:.1f} KB")
            print(f"   Output: {md_path}")

            return md_path

        except Exception as e:
            print(f"❌ Error converting {rtf_path}: {e}")
            return None

    def analyze_files(self):
        """Analyze RTF files and check if markdown versions exist"""

        print("=" * 80)
        print("RTF TO MARKDOWN ANALYSIS")
        print("=" * 80)
        print()

        rtf_exists = []
        md_exists = []
        needs_conversion = []

        for rtf_file in self.rtf_files:
            md_file = rtf_file.replace('.rtf', '.md')

            rtf_path = Path(rtf_file)
            md_path = Path(md_file)

            if rtf_path.exists():
                rtf_size = rtf_path.stat().st_size / 1024
                rtf_exists.append((rtf_file, rtf_size))

                if md_path.exists():
                    md_size = md_path.stat().st_size / 1024
                    md_exists.append((md_file, md_size))
                    print(f"✅ {rtf_file} ({rtf_size:.1f} KB)")
                    print(f"   ✅ Markdown exists: {md_file} ({md_size:.1f} KB)")
                else:
                    needs_conversion.append(rtf_file)
                    print(f"⚠️  {rtf_file} ({rtf_size:.1f} KB)")
                    print(f"   ❌ No markdown version found")
            else:
                print(f"❌ {rtf_file} - FILE NOT FOUND")

            print()

        print("=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"RTF Files Found: {len(rtf_exists)}/{len(self.rtf_files)}")
        print(f"Markdown Versions Exist: {len(md_exists)}")
        print(f"Need Conversion: {len(needs_conversion)}")
        print()

        if needs_conversion:
            print("Files Needing Conversion:")
            for f in needs_conversion:
                print(f"  - {f}")

        return needs_conversion

    def convert_all(self):
        """Convert all RTF files that don't have markdown versions"""

        needs_conversion = self.analyze_files()

        if not needs_conversion:
            print("\n✅ All RTF files already have markdown versions!")
            return

        print("\n" + "=" * 80)
        print("STARTING CONVERSION")
        print("=" * 80)
        print()

        converted = []
        failed = []

        for rtf_file in needs_conversion:
            md_path = self.convert_rtf_file(rtf_file)
            if md_path:
                converted.append(md_path)
            else:
                failed.append(rtf_file)
            print()

        print("=" * 80)
        print("CONVERSION COMPLETE")
        print("=" * 80)
        print(f"✅ Successfully Converted: {len(converted)}")
        print(f"❌ Failed: {len(failed)}")

        if converted:
            print("\nConverted Files:")
            for f in converted:
                print(f"  ✅ {f}")

        if failed:
            print("\nFailed Files:")
            for f in failed:
                print(f"  ❌ {f}")

def main():
    """Main entry point"""

    converter = RTFToMarkdown()

    print("PROJ344 RTF to Markdown Converter")
    print()
    print("Options:")
    print("1. Analyze only (check what needs conversion)")
    print("2. Convert all RTF files to markdown")
    print()

    choice = input("Enter choice (1 or 2): ").strip()

    if choice == '1':
        converter.analyze_files()
    elif choice == '2':
        converter.convert_all()
    else:
        print("Invalid choice. Running analysis only...")
        converter.analyze_files()

if __name__ == "__main__":
    main()
