#!/usr/bin/env python3
"""
WhatsApp Message Analyzer for Legal Violation Detection
Parses WhatsApp text export and analyzes for constitutional violations,
perjury indicators, and fraud indicators.

Usage:
    python3 scanners/whatsapp_analyzer.py data/whatsapp-input/chat.txt
"""

import os
import sys
import json
import re
from datetime import datetime
from pathlib import Path
import anthropic
from supabase import create_client

class WhatsAppAnalyzer:
    def __init__(self, supabase_url, supabase_key, anthropic_key):
        self.client = create_client(supabase_url, supabase_key)
        self.anthropic = anthropic.Anthropic(api_key=anthropic_key)
        self.case_id = 'ashe-bucknor-j24-00478'
        self.total_cost = 0.0

    def parse_whatsapp_export(self, file_path):
        """
        Parse WhatsApp text export format:
        [MM/DD/YY, HH:MM:SS AM/PM] Contact Name: Message text
        or
        MM/DD/YY, HH:MM - Contact Name: Message text
        """
        print(f"\n📱 Parsing WhatsApp export: {file_path}")

        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Pattern 1: [MM/DD/YY, HH:MM:SS AM/PM] Name: Message
        pattern1 = r'\[(\d{1,2}/\d{1,2}/\d{2,4}),?\s+(\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM)?)\]\s*([^:]+?):\s*(.+?)(?=\[\d{1,2}/\d{1,2}/\d{2,4}|$)'

        # Pattern 2: MM/DD/YY, HH:MM - Name: Message
        pattern2 = r'(\d{1,2}/\d{1,2}/\d{2,4}),?\s+(\d{1,2}:\d{2})\s*-\s*([^:]+?):\s*(.+?)(?=\d{1,2}/\d{1,2}/\d{2,4}|$)'

        messages = []

        # Try pattern 1
        matches = re.findall(pattern1, content, re.DOTALL)
        if matches:
            for match in matches:
                date_str, time_str, sender, message = match
                messages.append({
                    'date': date_str.strip(),
                    'time': time_str.strip(),
                    'sender': sender.strip(),
                    'message': message.strip()
                })
        else:
            # Try pattern 2
            matches = re.findall(pattern2, content, re.DOTALL)
            for match in matches:
                date_str, time_str, sender, message = match
                messages.append({
                    'date': date_str.strip(),
                    'time': time_str.strip(),
                    'sender': sender.strip(),
                    'message': message.strip()
                })

        print(f"✅ Parsed {len(messages)} messages")

        # Group messages by conversation segments (by date)
        conversations = self.group_messages_by_date(messages)
        print(f"✅ Grouped into {len(conversations)} conversation segments")

        return conversations

    def group_messages_by_date(self, messages):
        """Group messages by date for batch analysis"""
        conversations = {}
        for msg in messages:
            date = msg['date']
            if date not in conversations:
                conversations[date] = []
            conversations[date].append(msg)
        return conversations

    def analyze_conversation_segment(self, date, messages):
        """Analyze a conversation segment for violations"""
        print(f"\n📅 Analyzing conversation from {date}")
        print(f"   Messages: {len(messages)}")

        # Format conversation for analysis
        conversation_text = f"WhatsApp Conversation - Date: {date}\n\n"
        for msg in messages:
            conversation_text += f"[{msg['time']}] {msg['sender']}: {msg['message']}\n"

        # Limit to 15K characters for cost efficiency
        if len(conversation_text) > 15000:
            conversation_text = conversation_text[:15000] + "\n... [truncated]"

        print(f"   Text length: {len(conversation_text)} chars")

        # Analyze with Claude
        system_prompt = """You are a legal violation analyst. Analyze this WhatsApp conversation for:

1. Constitutional violations (4th Amendment unlawful search/seizure, due process violations, etc.)
2. Perjury indicators (false statements, contradictions, lying under oath)
3. Fraud indicators (misrepresentations, falsification, forgery, coercion)
4. Criminal activity (threats, intimidation, witness tampering, obstruction)
5. Child welfare violations (neglect, abuse, false reporting to CPS)

Return ONLY valid JSON:
{
  "constitutional_violations": ["Specific violation with evidence from chat"],
  "perjury_indicators": ["False statement with evidence"],
  "fraud_indicators": ["Fraudulent activity with evidence"],
  "key_quotes": ["Important verbatim quotes from conversation"],
  "participants": ["Person 1", "Person 2"],
  "summary": "Brief summary of conversation and violations",
  "severity": "CRITICAL|HIGH|MEDIUM|LOW"
}

Be specific and quote exact statements from the conversation as evidence."""

        try:
            message = self.anthropic.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=2000,
                system=system_prompt,
                messages=[{
                    "role": "user",
                    "content": f"Analyze this WhatsApp conversation for violations:\n\n{conversation_text}"
                }]
            )

            # Calculate cost
            input_tokens = message.usage.input_tokens
            output_tokens = message.usage.output_tokens
            cost = (input_tokens * 0.015 / 1000) + (output_tokens * 0.075 / 1000)
            self.total_cost += cost

            print(f"   💰 Cost: ${cost:.4f} | Tokens: {input_tokens}+{output_tokens}")

            # Parse response - extract JSON from response
            response_text = message.content[0].text

            # Try to extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                json_str = json_match.group(0)
                analysis = json.loads(json_str)
            else:
                print(f"   ⚠️  Could not extract JSON, using raw response")
                analysis = {"raw_response": response_text}

            # Display findings
            const_v = analysis.get('constitutional_violations', [])
            perjury = analysis.get('perjury_indicators', [])
            fraud = analysis.get('fraud_indicators', [])

            print(f"\n   📊 VIOLATIONS FOUND:")
            print(f"      🏛️  Constitutional: {len(const_v)}")
            print(f"      ⚖️  Perjury: {len(perjury)}")
            print(f"      🚨 Fraud: {len(fraud)}")
            if analysis.get('severity'):
                print(f"      ⚠️  Severity: {analysis['severity']}")

            return analysis

        except Exception as e:
            print(f"   ❌ Analysis error: {e}")
            return None

    def upload_to_supabase(self, date, messages, analysis, source_file):
        """Upload analyzed conversation to Supabase"""
        print(f"   💾 Uploading to Supabase...")

        # Prepare document data
        participants = analysis.get('participants', [])
        participants_str = ', '.join(participants) if participants else 'Unknown'

        # Create conversation transcript
        conversation_text = ""
        for msg in messages:
            conversation_text += f"[{msg['time']}] {msg['sender']}: {msg['message']}\n"

        document_data = {
            'case_id': self.case_id,
            'original_filename': f"WhatsApp_{date.replace('/', '-')}_{Path(source_file).stem}.txt",
            'document_type': 'TEXT',
            'document_date': date,
            'document_title': f"WhatsApp Conversation - {date} ({participants_str})",
            'executive_summary': analysis.get('summary', 'WhatsApp conversation analysis'),
            'full_text': conversation_text,

            # PROJ344 Scores
            'relevancy_number': 850 if analysis.get('severity') == 'CRITICAL' else 750,
            'legal_number': 800,
            'macro_number': 800,
            'micro_number': 750,

            # Violations
            'constitutional_violations': analysis.get('constitutional_violations', []),
            'perjury_indicators': analysis.get('perjury_indicators', []),
            'fraud_indicators': analysis.get('fraud_indicators', []),

            # Metadata
            'key_quotes': analysis.get('key_quotes', []),
            'parties': participants,
            'status': 'ANALYZED',
            'purpose': 'EVIDENCE',
            'importance': analysis.get('severity', 'HIGH'),

            # Processing info
            'processed_by': 'WhatsApp Analyzer',
            'api_cost_usd': self.total_cost
        }

        try:
            response = self.client.table('legal_documents').insert(document_data).execute()
            doc_id = response.data[0]['id'] if response.data else None
            print(f"   ✅ Uploaded to Supabase (ID: {doc_id})")
            return doc_id
        except Exception as e:
            print(f"   ❌ Upload error: {e}")
            return None

    def process_whatsapp_file(self, file_path):
        """Process entire WhatsApp export file"""
        print("=" * 80)
        print("📱 WHATSAPP MESSAGE ANALYZER")
        print("=" * 80)
        print(f"Source file: {file_path}")

        # Parse WhatsApp export
        conversations = self.parse_whatsapp_export(file_path)

        if not conversations:
            print("❌ No messages found in file")
            return

        processed = 0
        uploaded = 0

        # Process each conversation segment
        for date, messages in conversations.items():
            analysis = self.analyze_conversation_segment(date, messages)

            if analysis:
                processed += 1

                # Upload to Supabase
                doc_id = self.upload_to_supabase(date, messages, analysis, file_path)
                if doc_id:
                    uploaded += 1

        # Final summary
        print(f"\n{'='*80}")
        print("🎉 ANALYSIS COMPLETE")
        print(f"{'='*80}")
        print(f"✅ Conversation segments processed: {processed}/{len(conversations)}")
        print(f"✅ Uploaded to Supabase: {uploaded}")
        print(f"💰 Total cost: ${self.total_cost:.2f}")
        print(f"{'='*80}")
        print(f"\n📊 View results in dashboards:")
        print(f"   http://137.184.1.91:8501 (PROJ344 Master)")
        print(f"   http://137.184.1.91:8504 (Timeline & Violations)")

def main():
    if len(sys.argv) < 2:
        print("❌ Usage: python3 scanners/whatsapp_analyzer.py <whatsapp_export_file>")
        print("\nExample:")
        print("  python3 scanners/whatsapp_analyzer.py data/whatsapp-input/chat.txt")
        sys.exit(1)

    file_path = sys.argv[1]

    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        sys.exit(1)

    # Get credentials
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
    ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')

    if not all([SUPABASE_URL, SUPABASE_KEY, ANTHROPIC_API_KEY]):
        print("❌ Missing environment variables!")
        print("   Required: SUPABASE_URL, SUPABASE_KEY, ANTHROPIC_API_KEY")
        sys.exit(1)

    # Run analyzer
    analyzer = WhatsAppAnalyzer(SUPABASE_URL, SUPABASE_KEY, ANTHROPIC_API_KEY)
    analyzer.process_whatsapp_file(file_path)

if __name__ == '__main__':
    main()
