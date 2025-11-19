#!/usr/bin/env python3
"""
Multi-Source Document Processor for Timeline Hub
=================================================

Processes documents from multiple sources and extracts:
- Events
- Communications
- Statements
- Participants

Supported Sources:
- Court documents (orders, transcripts, filings)
- Text message screenshots
- Emails
- Police reports
- Medical records
- Generic documents

Usage:
    processor = DocumentProcessor(supabase_url, supabase_key, anthropic_key)
    events = processor.process_document(file_path, source_type='TEXT_MESSAGE')
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from supabase import create_client
import anthropic
from PIL import Image
import base64
from io import BytesIO
import json
import re

# Import schema types
from database.schema import TimelineEvent, Communication

class DocumentProcessor:
    """Process documents from multiple sources and extract timeline events"""

    def __init__(self, supabase_url: str, supabase_key: str, anthropic_key: str):
        self.supabase = create_client(supabase_url, supabase_key)
        self.anthropic = anthropic.Anthropic(api_key=anthropic_key)
        self.case_number = 'J24-00478'

        # Participant code mapping
        self.participant_codes = {
            'mother': 'MOT',
            'mariyam': 'MOT',
            'mom': 'MOT',
            'father': 'FAT',
            'don': 'FAT',
            'dad': 'FAT',
            'ashe': 'MIN',
            'child': 'MIN',
            'minor': 'MIN',
            'cps': 'CPS',
            'social worker': 'CPS',
            'judge': 'JUD',
            'court': 'JUD',
            'police': 'POL',
            'officer': 'POL',
            'doctor': 'MED',
            'medical': 'MED'
        }

    def process_document(
        self,
        file_path: str,
        source_type: str,
        extract_events: bool = True,
        extract_communications: bool = True,
        extract_statements: bool = True
    ) -> Dict[str, Any]:
        """
        Process a document and extract timeline data

        Args:
            file_path: Path to document
            source_type: TEXT_MESSAGE, EMAIL, COURT_DOC, POLICE_REPORT, etc.
            extract_events: Whether to extract timeline events
            extract_communications: Whether to extract communications
            extract_statements: Whether to extract statements

        Returns:
            Dict with extracted data and processing results
        """
        print(f"\n{'='*80}")
        print(f"PROCESSING: {Path(file_path).name}")
        print(f"Type: {source_type}")
        print(f"{'='*80}\n")

        # Queue the document
        queue_id = self._add_to_queue(file_path, source_type, extract_events, extract_communications, extract_statements)

        try:
            # Read and convert document
            file_content = self._read_file(file_path)

            # Send to Claude for analysis
            analysis = self._analyze_with_claude(file_content, source_type)

            # Extract data based on requests
            results = {
                'events': [],
                'communications': [],
                'statements': [],
                'queue_id': queue_id
            }

            if extract_events and analysis.get('events'):
                results['events'] = self._process_events(analysis['events'], file_path)

            if extract_communications and analysis.get('communications'):
                results['communications'] = self._process_communications(
                    analysis['communications'],
                    file_path
                )

            if extract_statements and analysis.get('statements'):
                results['statements'] = self._process_statements(analysis['statements'], file_path)

            # Update queue status
            self._update_queue_status(
                queue_id,
                'completed',
                len(results['events']),
                len(results['communications']),
                len(results['statements'])
            )

            print(f"\n✅ Processing complete:")
            print(f"   Events: {len(results['events'])}")
            print(f"   Communications: {len(results['communications'])}")
            print(f"   Statements: {len(results['statements'])}")

            return results

        except Exception as e:
            print(f"❌ Error processing document: {e}")
            self._update_queue_status(queue_id, 'failed', errors=[str(e)])
            raise

    def _read_file(self, file_path: str) -> str:
        """Read file and convert to base64 or text"""
        ext = Path(file_path).suffix.lower()

        if ext in ['.jpg', '.jpeg', '.png', '.heic']:
            # Convert image to base64
            with Image.open(file_path) as img:
                # Resize if needed
                max_size = 1568
                if img.width > max_size or img.height > max_size:
                    img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

                if img.mode != 'RGB':
                    img = img.convert('RGB')

                buffered = BytesIO()
                img.save(buffered, format="JPEG", quality=85)
                return base64.b64encode(buffered.getvalue()).decode()

        elif ext in ['.txt', '.rtf']:
            # Read text file
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()

        else:
            raise ValueError(f"Unsupported file type: {ext}")

    def _analyze_with_claude(self, file_content: str, source_type: str) -> Dict:
        """Send to Claude for analysis"""

        # Build system prompt based on source type
        system_prompt = self._get_system_prompt(source_type)

        # Build message
        if file_content.startswith('data:') or len(file_content) > 1000:
            # Image data
            messages = [{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": file_content
                        }
                    },
                    {
                        "type": "text",
                        "text": f"Extract timeline data from this {source_type}."
                    }
                ]
            }]
        else:
            # Text data
            messages = [{
                "role": "user",
                "content": f"Extract timeline data from this {source_type}:\n\n{file_content}"
            }]

        # Call Claude
        response = self.anthropic.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            temperature=0.1,
            system=system_prompt,
            messages=messages
        )

        response_text = response.content[0].text.strip()

        # Parse JSON response
        if response_text.startswith('```'):
            response_text = response_text.split('\n', 1)[1].rsplit('```', 1)[0]

        return json.loads(response_text.strip())

    def _get_system_prompt(self, source_type: str) -> str:
        """Get analysis prompt based on source type"""

        base_prompt = """You are a timeline analysis expert. Extract ALL events, communications, and statements from the document.

Return ONLY valid JSON in this format:

{
  "events": [
    {
      "event_type": "TEXT_MESSAGE|EMAIL|COURT_HEARING|INCIDENT|etc",
      "event_date": "YYYY-MM-DD",
      "event_time": "HH:MM:SS or null",
      "event_title": "Brief title",
      "event_description": "Detailed description",
      "participants": ["MOT", "FAT", "MIN", "CPS", etc],
      "sender": "MOT",
      "recipients": ["FAT"],
      "message_text": "Full message text if applicable",
      "importance": 0-999,
      "keywords": ["keyword1", "keyword2"]
    }
  ],
  "communications": [
    {
      "comm_type": "TEXT_MESSAGE|EMAIL|CALL|etc",
      "comm_date": "YYYY-MM-DD",
      "comm_time": "HH:MM:SS",
      "sender": "MOT",
      "recipients": ["FAT"],
      "message_body": "Full text",
      "contains_admission": false,
      "contains_threat": false,
      "contains_false_statement": false,
      "admission_text": [],
      "importance": 0-999
    }
  ],
  "statements": [
    {
      "speaker": "MOT",
      "statement_text": "Exact quote",
      "statement_type": "claim|fact|admission|denial",
      "subject_matter": "What it's about",
      "date_made": "YYYY-MM-DD",
      "verifiable": true|false
    }
  ]
}

Participant codes:
- MOT: Mother (Mariyam Yonas Rufael)
- FAT: Father (Don Bucknor)
- MIN: Minor (Ashe)
- CPS: CPS social worker
- JUD: Judge
- POL: Police
- MED: Medical professional
- ATT_MOT: Mother's attorney
- ATT_FAT: Father's attorney
"""

        if source_type == 'TEXT_MESSAGE':
            return base_prompt + """
SPECIFIC INSTRUCTIONS FOR TEXT MESSAGES:
- Extract the date and time of EACH message
- Identify sender and recipient
- Look for metadata (phone numbers, timestamps)
- Flag admissions, threats, false statements
- Note any mentions of Jamaica, travel, custody, abuse
- Extract ALL statements made
"""

        elif source_type == 'EMAIL':
            return base_prompt + """
SPECIFIC INSTRUCTIONS FOR EMAILS:
- Extract From, To, CC, Subject, Date
- Capture full email body
- Identify any attachments mentioned
- Look for email threads (replies)
- Flag urgent language, threats, admissions
"""

        elif source_type == 'COURT_DOC':
            return base_prompt + """
SPECIFIC INSTRUCTIONS FOR COURT DOCUMENTS:
- Identify hearing dates and times
- Extract judge name, court name
- Note all participants present
- Extract statements made under oath
- Identify rulings and orders
- Note filing dates
"""

        elif source_type == 'POLICE_REPORT':
            return base_prompt + """
SPECIFIC INSTRUCTIONS FOR POLICE REPORTS:
- Extract report number and date
- Identify reporting officer
- Extract incident type and location
- Note all parties involved
- Extract narrative statements
- Identify evidence collected
"""

        else:
            return base_prompt

    def _process_events(self, events_data: List[Dict], source_file: str) -> List[str]:
        """Process and store events"""
        event_ids = []

        for event in events_data:
            try:
                event_record = {
                    'event_type': event.get('event_type', 'GENERIC'),
                    'event_date': event.get('event_date'),
                    'event_time': event.get('event_time'),
                    'event_title': event.get('event_title', 'Untitled Event'),
                    'event_description': event.get('event_description'),
                    'participants': event.get('participants', []),
                    'sender': event.get('sender'),
                    'recipients': event.get('recipients', []),
                    'message_full_text': event.get('message_text'),
                    'source_type': 'SCREENSHOT',  # or derive from source
                    'source_file_path': source_file,
                    'importance': event.get('importance', 500),
                    'keywords': event.get('keywords', []),
                    'case_number': self.case_number,
                    'created_by': 'timeline_processor'
                }

                # Insert into database
                result = self.supabase.table('timeline_events').insert(event_record).execute()

                if result.data:
                    event_ids.append(result.data[0]['id'])
                    print(f"  ✅ Event created: {event_record['event_title']}")

            except Exception as e:
                print(f"  ❌ Error creating event: {e}")

        return event_ids

    def _process_communications(self, comms_data: List[Dict], source_file: str) -> List[str]:
        """Process and store communications"""
        comm_ids = []

        for comm in comms_data:
            try:
                comm_record = {
                    'comm_type': comm.get('comm_type', 'TEXT_MESSAGE'),
                    'comm_date': comm.get('comm_date'),
                    'comm_time': comm.get('comm_time'),
                    'sender': comm.get('sender'),
                    'recipients': comm.get('recipients', []),
                    'message_body': comm.get('message_body'),
                    'contains_admission': comm.get('contains_admission', False),
                    'contains_threat': comm.get('contains_threat', False),
                    'contains_false_statement': comm.get('contains_false_statement', False),
                    'admission_text': comm.get('admission_text', []),
                    'source_screenshot_path': source_file,
                    'importance': comm.get('importance', 500)
                }

                # Insert into database
                result = self.supabase.table('communications').insert(comm_record).execute()

                if result.data:
                    comm_ids.append(result.data[0]['id'])
                    print(f"  ✅ Communication logged: {comm_record['sender']} → {comm_record['recipients']}")

            except Exception as e:
                print(f"  ❌ Error creating communication: {e}")

        return comm_ids

    def _process_statements(self, statements_data: List[Dict], source_file: str) -> List[str]:
        """Process and store statements"""
        statement_ids = []

        for stmt in statements_data:
            try:
                # This would insert into document_statements table
                # (from criminal complaint system)
                print(f"  📝 Statement: {stmt.get('speaker')} - {stmt.get('statement_text')[:50]}...")

                # TODO: Insert into document_statements table when integrated
                statement_ids.append(f"stmt-{len(statement_ids)+1}")

            except Exception as e:
                print(f"  ❌ Error processing statement: {e}")

        return statement_ids

    def _add_to_queue(
        self,
        file_path: str,
        source_type: str,
        extract_events: bool,
        extract_comms: bool,
        extract_stmts: bool
    ) -> str:
        """Add document to processing queue"""
        queue_record = {
            'source_type': 'UPLOAD',
            'file_path': file_path,
            'file_name': Path(file_path).name,
            'file_type': Path(file_path).suffix,
            'file_size_bytes': Path(file_path).stat().st_size,
            'processing_type': source_type,
            'extract_events': extract_events,
            'extract_communications': extract_comms,
            'extract_statements': extract_stmts,
            'status': 'processing',
            'priority': 5,
            'started_at': datetime.now().isoformat()
        }

        result = self.supabase.table('document_processing_queue').insert(queue_record).execute()
        return result.data[0]['id']

    def _update_queue_status(
        self,
        queue_id: str,
        status: str,
        events_created: int = 0,
        comms_created: int = 0,
        stmts_created: int = 0,
        errors: List[str] = None
    ):
        """Update queue status"""
        update_data = {
            'status': status,
            'events_created': events_created,
            'communications_created': comms_created,
            'statements_created': stmts_created,
            'completed_at': datetime.now().isoformat()
        }

        if errors:
            update_data['errors'] = errors

        self.supabase.table('document_processing_queue')\
            .update(update_data)\
            .eq('id', queue_id)\
            .execute()


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description='Process documents for timeline hub')
    parser.add_argument('file_path', help='Path to document')
    parser.add_argument('--type', dest='source_type', required=True,
                       choices=['TEXT_MESSAGE', 'EMAIL', 'COURT_DOC', 'POLICE_REPORT', 'SCREENSHOT'],
                       help='Document type')
    parser.add_argument('--no-events', action='store_false', dest='extract_events')
    parser.add_argument('--no-comms', action='store_false', dest='extract_communications')
    parser.add_argument('--no-statements', action='store_false', dest='extract_statements')

    args = parser.parse_args()

    # Get credentials
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')
    ANTHROPIC_KEY = os.getenv('ANTHROPIC_API_KEY')

    if not all([SUPABASE_URL, SUPABASE_KEY, ANTHROPIC_KEY]):
        print("❌ Missing environment variables!")
        sys.exit(1)

    # Process document
    processor = DocumentProcessor(SUPABASE_URL, SUPABASE_KEY, ANTHROPIC_KEY)
    results = processor.process_document(
        args.file_path,
        args.source_type,
        args.extract_events,
        args.extract_communications,
        args.extract_statements
    )

    print(f"\n{'='*80}")
    print("RESULTS:")
    print(json.dumps(results, indent=2, default=str))


if __name__ == '__main__':
    main()
