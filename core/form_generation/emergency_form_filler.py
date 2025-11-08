#!/usr/bin/env python3
"""
Emergency Legal Form Filler
Generates JV-180 (W&I § 388 Petition) and JV-575 (Declaration) forms
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

try:
    from supabase import create_client, Client
except ImportError:
    print("❌ Missing supabase. Install: pip install supabase")
    sys.exit(1)

try:
    from anthropic import Anthropic
except ImportError:
    print("❌ Missing anthropic. Install: pip install anthropic")
    sys.exit(1)

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
except ImportError:
    print("❌ Missing reportlab. Install: pip install reportlab")
    sys.exit(1)


class EmergencyFormFiller:
    """
    Emergency Legal Form Filler

    Queries Supabase for high-scoring evidence, uses Claude API to generate
    legal arguments, and creates professional PDF court forms.
    """

    def __init__(self, supabase_url: str, supabase_key: str, anthropic_key: str):
        """
        Initialize the form filler

        Args:
            supabase_url: Supabase project URL
            supabase_key: Supabase API key (service_role recommended)
            anthropic_key: Anthropic API key for Claude
        """
        self.supabase: Client = create_client(supabase_url, supabase_key)
        self.anthropic = Anthropic(api_key=anthropic_key)
        self.evidence: Dict = {}
        self.case_id: str = ""

    def gather_evidence(self, case_id: str) -> Dict:
        """
        Query Supabase for case evidence

        Retrieves:
        - Critical documents (score >= 900)
        - Mother's admissions
        - Medical/forensic records
        - Dismissal transcripts
        - Timeline of events

        Args:
            case_id: Case identifier (e.g., J24-00478)

        Returns:
            Dictionary of evidence organized by category
        """
        print(f"\n📊 Gathering evidence for case {case_id}...")
        self.case_id = case_id
        evidence = {
            'critical_docs': [],
            'mother_admissions': [],
            'medical_forensic': [],
            'dismissals': [],
            'timeline': [],
            'police_reports': [],
            'high_scoring': []
        }

        try:
            # Critical documents (score >= 900)
            print("  🔥 Querying critical documents (score >= 900)...")
            response = self.supabase.table('legal_documents')\
                .select('*')\
                .gte('relevancy_number', 900)\
                .order('relevancy_number', desc=True)\
                .execute()

            evidence['critical_docs'] = response.data if response.data else []
            print(f"     Found {len(evidence['critical_docs'])} critical documents")

            # Mother's admissions
            print("  🎯 Searching for mother's admissions...")
            response = self.supabase.table('legal_documents')\
                .select('*')\
                .ilike('executive_summary', '%mother%admit%')\
                .order('relevancy_number', desc=True)\
                .execute()

            evidence['mother_admissions'] = response.data if response.data else []
            print(f"     Found {len(evidence['mother_admissions'])} documents with admissions")

            # Medical/Forensic records
            print("  🏥 Querying medical and forensic records...")
            response = self.supabase.table('legal_documents')\
                .select('*')\
                .in_('document_type', ['Medical Record', 'Forensic Report', 'CPS Report'])\
                .order('relevancy_number', desc=True)\
                .limit(50)\
                .execute()

            evidence['medical_forensic'] = response.data if response.data else []
            print(f"     Found {len(evidence['medical_forensic'])} medical/forensic records")

            # Dismissal transcripts
            print("  ⚖️ Searching for dismissal documents...")
            response = self.supabase.table('legal_documents')\
                .select('*')\
                .ilike('executive_summary', '%dismissal%')\
                .order('created_at', desc=True)\
                .execute()

            evidence['dismissals'] = response.data if response.data else []
            print(f"     Found {len(evidence['dismissals'])} dismissal-related documents")

            # Police reports
            print("  🚔 Querying police reports...")
            response = self.supabase.table('legal_documents')\
                .select('*')\
                .ilike('original_filename', '%police%')\
                .order('relevancy_number', desc=True)\
                .execute()

            evidence['police_reports'] = response.data if response.data else []
            print(f"     Found {len(evidence['police_reports'])} police reports")

            # Timeline (all docs by date)
            print("  📅 Building timeline...")
            response = self.supabase.table('legal_documents')\
                .select('document_date, original_filename, executive_summary, relevancy_number')\
                .not_.is_('document_date', 'null')\
                .order('document_date', desc=False)\
                .limit(200)\
                .execute()

            evidence['timeline'] = response.data if response.data else []
            print(f"     Timeline includes {len(evidence['timeline'])} dated events")

            # High scoring overall
            print("  ⭐ Compiling high-scoring documents...")
            response = self.supabase.table('legal_documents')\
                .select('*')\
                .gte('relevancy_number', 850)\
                .order('relevancy_number', desc=True)\
                .limit(100)\
                .execute()

            evidence['high_scoring'] = response.data if response.data else []
            print(f"     Found {len(evidence['high_scoring'])} high-scoring documents")

        except Exception as e:
            print(f"\n❌ Error gathering evidence: {e}")
            raise

        self.evidence = evidence

        # Summary
        total = sum(len(v) for v in evidence.values() if isinstance(v, list))
        print(f"\n✅ Evidence gathered: {total} documents across {len(evidence)} categories")

        return evidence

    def generate_changed_circumstances(self) -> str:
        """
        Generate "Changed Circumstances" section using Claude API

        Returns:
            300-500 word argument for W&I § 388 petition
        """
        print("\n📝 Generating Changed Circumstances section...")

        # Build evidence context
        context = self._build_evidence_context()

        prompt = f"""You are a legal assistant preparing a W&I Code § 388 petition (JV-180 form) for case {self.case_id}.

Write a compelling 300-500 word "Changed Circumstances" section that explains:
1. What new evidence has emerged since the original order
2. Why this evidence was not available or known before
3. How circumstances have materially changed
4. Why the court should modify its previous order

EVIDENCE AVAILABLE:
{context}

LEGAL REQUIREMENTS:
- Must show "changed circumstances" (new facts not previously known)
- Must show evidence was unavailable at time of original hearing
- Must be factual, professional, cite specific evidence
- Focus on child safety, not parental blame
- Use formal legal tone

FORMAT:
- Single paragraph or 2-3 short paragraphs
- Professional legal writing
- Cite specific documents/dates
- Avoid emotional language
- Focus on material facts

Generate the Changed Circumstances section now:"""

        try:
            message = self.anthropic.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )

            result = message.content[0].text
            print(f"✅ Generated {len(result.split())} words")
            return result

        except Exception as e:
            print(f"❌ Error generating changed circumstances: {e}")
            raise

    def generate_best_interest(self) -> str:
        """
        Generate "Best Interest of Child" section using Claude API

        Returns:
            300-400 word argument focusing on child safety
        """
        print("\n📝 Generating Best Interest section...")

        context = self._build_evidence_context()

        prompt = f"""You are a legal assistant preparing a W&I Code § 388 petition (JV-180 form) for case {self.case_id}.

Write a compelling 300-400 word "Best Interest of Child" section that explains:
1. Why the requested modification serves the child's best interests
2. Focus on child safety and wellbeing (NOT parental rights)
3. Why investigation/review is necessary
4. Potential harm if petition is denied

EVIDENCE AVAILABLE:
{context}

LEGAL REQUIREMENTS:
- Must demonstrate proposed order is in child's best interest
- Focus on child's safety, stability, wellbeing
- Avoid parent-focused arguments
- Professional, factual tone
- Cite specific evidence of need for protection/investigation

KEY THEMES TO EMPHASIZE:
- Child's right to safety from abuse
- Need for thorough investigation of new evidence
- Intergenerational abuse patterns (if applicable)
- Systemic failures to protect
- Urgency of addressing credible safety concerns

FORMAT:
- 2-3 paragraphs
- Professional legal writing
- Specific facts, not generalizations
- Child-centered perspective

Generate the Best Interest section now:"""

        try:
            message = self.anthropic.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )

            result = message.content[0].text
            print(f"✅ Generated {len(result.split())} words")
            return result

        except Exception as e:
            print(f"❌ Error generating best interest: {e}")
            raise

    def generate_orders_requested(self) -> str:
        """
        Generate "Orders Requested" section using Claude API

        Returns:
            Numbered list of specific orders being requested
        """
        print("\n📝 Generating Orders Requested section...")

        context = self._build_evidence_context()

        prompt = f"""You are a legal assistant preparing a W&I Code § 388 petition (JV-180 form) for case {self.case_id}.

Generate a numbered list of specific orders being requested from the court.

EVIDENCE CONTEXT:
{context}

TYPICAL ORDERS TO INCLUDE:
1. Accept this ex parte petition for filing
2. Set a hearing date within 30 days
3. Order the collection of a confidential CPS report on [specific allegations]
4. Appoint independent investigator to review new evidence
5. Stay any pending proceedings until investigation complete
6. Order forensic evaluation of child
7. Protective orders if necessary
8. Any other appropriate relief

REQUIREMENTS:
- Be specific and actionable
- Cite legal authority where appropriate (W&I Code sections)
- Professional legal language
- Numbered list format
- 4-8 orders total
- Focus on investigation and child protection

Generate the Orders Requested section now (numbered list):"""

        try:
            message = self.anthropic.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )

            result = message.content[0].text
            print(f"✅ Generated orders list")
            return result

        except Exception as e:
            print(f"❌ Error generating orders requested: {e}")
            raise

    def generate_jv575_declaration(self) -> str:
        """
        Generate comprehensive JV-575 Declaration using Claude API

        Returns:
            2000-3000 word declaration with 12 sections
        """
        print("\n📝 Generating JV-575 Declaration (this may take a moment)...")

        context = self._build_evidence_context()

        prompt = f"""You are a legal assistant preparing a comprehensive JV-575 Declaration to support a W&I Code § 388 petition for case {self.case_id}.

Write a detailed 2000-3000 word declaration with the following 12 sections:

1. INTRODUCTION
   - Declarant's relationship to case
   - Purpose of declaration
   - Overview of new evidence

2. CHILD'S DISCLOSURE
   - What child disclosed and when
   - Circumstances of disclosure
   - Child's exact words (if known)

3. FORENSIC EXAMINATION
   - Results of any forensic medical exams
   - Expert findings
   - Medical evidence of abuse

4. MOTHER'S ADMISSION
   - What mother admitted and when
   - Context and circumstances
   - Corroborating evidence

5. SYSTEMIC FAILURE TO PROTECT
   - How system failed to investigate
   - Dismissed reports
   - Ignored evidence

6. FALSE ALLEGATIONS AGAINST FATHER
   - Pattern of false claims by mother
   - Evidence contradicting mother's claims
   - Impact on custody proceedings

7. DISMISSAL OF PRIOR CONCERNS
   - What concerns were dismissed
   - Why dismissal was premature
   - New evidence warranting review

8. NEW EVIDENCE NOT PREVIOUSLY AVAILABLE
   - What evidence is new
   - Why it wasn't available before
   - How it changes the case

9. PATTERN OF INTERGENERATIONAL ABUSE
   - Evidence of abuse patterns
   - Historical context
   - Need for investigation

10. URGENCY OF SITUATION
    - Current risks to child
    - Time-sensitive factors
    - Why immediate action needed

11. BEST INTEREST OF CHILD
    - Why investigation serves child's interests
    - Potential harm if no action taken
    - Child's right to safety

12. CONCLUSION
    - Summary of key points
    - Specific relief requested
    - Declaration under penalty of perjury

EVIDENCE AVAILABLE:
{context}

REQUIREMENTS:
- Professional legal tone throughout
- Cite specific evidence and dates
- Use declarant voice ("I declare...", "I am informed and believe...")
- Factual, not emotional
- Organized with clear headings
- Appropriate legal citations (W&I Code, case law if relevant)
- End with standard declaration language

Generate the complete JV-575 Declaration now:"""

        try:
            message = self.anthropic.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=8000,
                messages=[{"role": "user", "content": prompt}]
            )

            result = message.content[0].text
            print(f"✅ Generated {len(result.split())} words")
            return result

        except Exception as e:
            print(f"❌ Error generating declaration: {e}")
            raise

    def create_pdf(self, form_data: Dict, output_path: str):
        """
        Create professional PDF with JV-180 and JV-575 forms

        Args:
            form_data: Dictionary with sections (changed_circumstances, best_interest, etc.)
            output_path: Path to save PDF file
        """
        print(f"\n📄 Creating PDF: {output_path}")

        # Create directory if needed
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # Create PDF
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )

        # Styles
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=14,
            textColor='black',
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Times-Bold'
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=12,
            textColor='black',
            spaceAfter=6,
            spaceBefore=12,
            fontName='Times-Bold'
        )

        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['BodyText'],
            fontSize=10,
            textColor='black',
            spaceAfter=6,
            alignment=TA_JUSTIFY,
            fontName='Times-Roman',
            leading=14
        )

        # Build document
        story = []

        # Court Header
        story.append(Paragraph("SUPERIOR COURT OF CALIFORNIA", title_style))
        story.append(Paragraph("COUNTY OF ALAMEDA", title_style))
        story.append(Spacer(1, 0.2*inch))

        # Case info
        story.append(Paragraph(f"Case No.: {self.case_id}", body_style))
        story.append(Spacer(1, 0.3*inch))

        # JV-180 Title
        story.append(Paragraph("PETITION TO CHANGE COURT ORDER", title_style))
        story.append(Paragraph("(Welfare and Institutions Code Section 388)", title_style))
        story.append(Paragraph("(JV-180)", title_style))
        story.append(Spacer(1, 0.3*inch))

        # Changed Circumstances
        story.append(Paragraph("1. CHANGED CIRCUMSTANCES", heading_style))
        story.append(Paragraph(form_data.get('changed_circumstances', ''), body_style))
        story.append(Spacer(1, 0.2*inch))

        # Best Interest
        story.append(Paragraph("2. BEST INTEREST OF CHILD", heading_style))
        story.append(Paragraph(form_data.get('best_interest', ''), body_style))
        story.append(Spacer(1, 0.2*inch))

        # Orders Requested
        story.append(Paragraph("3. ORDERS REQUESTED", heading_style))
        story.append(Paragraph(form_data.get('orders_requested', ''), body_style))
        story.append(Spacer(1, 0.3*inch))

        # Date and signature block
        story.append(Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}", body_style))
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph("_" * 50, body_style))
        story.append(Paragraph("Signature of Petitioner", body_style))

        # Page break before declaration
        story.append(PageBreak())

        # JV-575 Declaration
        story.append(Paragraph("DECLARATION IN SUPPORT OF PETITION", title_style))
        story.append(Paragraph("(JV-575)", title_style))
        story.append(Spacer(1, 0.3*inch))

        # Declaration content
        declaration = form_data.get('declaration', '')

        # Split by sections if the declaration has numbered headings
        for paragraph in declaration.split('\n\n'):
            if paragraph.strip():
                # Check if it's a heading (all caps or starts with number)
                if paragraph.isupper() or (paragraph[0].isdigit() if paragraph else False):
                    story.append(Paragraph(paragraph, heading_style))
                else:
                    story.append(Paragraph(paragraph, body_style))
                story.append(Spacer(1, 0.1*inch))

        # Declaration under penalty of perjury
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph(
            "I declare under penalty of perjury under the laws of the State of California "
            "that the foregoing is true and correct.",
            body_style
        ))
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph(f"Executed on {datetime.now().strftime('%B %d, %Y')}", body_style))
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph("_" * 50, body_style))
        story.append(Paragraph("Signature of Declarant", body_style))

        # Build PDF
        try:
            doc.build(story)
            print(f"✅ PDF created successfully")
            file_size = os.path.getsize(output_path)
            print(f"   Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        except Exception as e:
            print(f"❌ Error creating PDF: {e}")
            raise

    def create_evidence_summary(self, output_path: str):
        """
        Create exhibit list PDF summarizing evidence

        Args:
            output_path: Path to save exhibits PDF
        """
        print(f"\n📋 Creating evidence summary: {output_path}")

        # Create directory if needed
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        doc = SimpleDocTemplate(output_path, pagesize=letter,
                                rightMargin=0.75*inch, leftMargin=0.75*inch,
                                topMargin=0.75*inch, bottomMargin=0.75*inch)

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('Title', parent=styles['Heading1'],
                                     fontSize=14, alignment=TA_CENTER)
        heading_style = ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=12)
        body_style = ParagraphStyle('Body', parent=styles['BodyText'], fontSize=10)

        story = []

        # Title
        story.append(Paragraph(f"EVIDENCE SUMMARY - Case {self.case_id}", title_style))
        story.append(Spacer(1, 0.3*inch))

        # Evidence categories
        categories = [
            ('EXHIBIT A: Critical Documents (Score ≥ 900)', 'critical_docs'),
            ('EXHIBIT B: Mother\'s Admissions', 'mother_admissions'),
            ('EXHIBIT C: Medical/Forensic Records', 'medical_forensic'),
            ('EXHIBIT D: Police Reports', 'police_reports'),
            ('EXHIBIT E: Dismissal Records', 'dismissals')
        ]

        for exhibit_name, key in categories:
            docs = self.evidence.get(key, [])

            story.append(Paragraph(exhibit_name, heading_style))
            story.append(Paragraph(f"Total documents: {len(docs)}", body_style))
            story.append(Spacer(1, 0.1*inch))

            # List top documents
            for i, doc in enumerate(docs[:10], 1):  # Top 10 per category
                filename = doc.get('original_filename', 'Unknown')
                score = doc.get('relevancy_number', 0)
                summary = doc.get('executive_summary', 'No summary')[:200]

                story.append(Paragraph(
                    f"{i}. {filename} (Score: {score})<br/>{summary}...",
                    body_style
                ))
                story.append(Spacer(1, 0.05*inch))

            if len(docs) > 10:
                story.append(Paragraph(f"... and {len(docs) - 10} more documents", body_style))

            story.append(Spacer(1, 0.2*inch))

        try:
            doc.build(story)
            print(f"✅ Evidence summary created")
        except Exception as e:
            print(f"❌ Error creating evidence summary: {e}")
            raise

    def run(self, case_id: str, output_dir: str):
        """
        Main orchestration method - generates complete filing package

        Args:
            case_id: Case identifier (e.g., J24-00478)
            output_dir: Directory to save output files
        """
        print("\n" + "="*80)
        print(f"🏛️  EMERGENCY LEGAL FORM FILLER")
        print(f"📋 Case ID: {case_id}")
        print(f"📁 Output: {output_dir}")
        print("="*80)

        try:
            # Step 1: Gather evidence
            self.gather_evidence(case_id)

            # Step 2: Generate form sections
            form_data = {}

            form_data['changed_circumstances'] = self.generate_changed_circumstances()
            form_data['best_interest'] = self.generate_best_interest()
            form_data['orders_requested'] = self.generate_orders_requested()
            form_data['declaration'] = self.generate_jv575_declaration()

            # Step 3: Create PDFs
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

            forms_pdf = output_dir / f"{case_id}_JV180_JV575.pdf"
            evidence_pdf = output_dir / f"{case_id}_Evidence_Summary.pdf"

            self.create_pdf(form_data, str(forms_pdf))
            self.create_evidence_summary(str(evidence_pdf))

            # Step 4: Print summary
            print("\n" + "="*80)
            print("✅ FILING PACKAGE COMPLETE")
            print("="*80)
            print(f"\n📄 Forms Generated:")
            print(f"   • {forms_pdf}")
            print(f"   • {evidence_pdf}")

            print(f"\n📊 Evidence Summary:")
            for category, docs in self.evidence.items():
                if isinstance(docs, list):
                    print(f"   • {category}: {len(docs)} documents")

            print(f"\n🎯 Next Steps:")
            print(f"   1. Review generated forms for accuracy")
            print(f"   2. Add personal information (name, address, signature)")
            print(f"   3. Attach exhibits referenced in declaration")
            print(f"   4. File with court clerk")
            print(f"   5. Serve on all parties")

            print("\n" + "="*80)

        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            raise

    def _build_evidence_context(self) -> str:
        """
        Build summary of available evidence for Claude prompts

        Returns:
            String summarizing available evidence
        """
        context_parts = []

        # Critical docs
        critical = self.evidence.get('critical_docs', [])
        if critical:
            context_parts.append(f"CRITICAL DOCUMENTS ({len(critical)} total):")
            for doc in critical[:5]:  # Top 5
                context_parts.append(f"  - {doc.get('original_filename', 'Unknown')} "
                                   f"(Score: {doc.get('relevancy_number', 0)})")
                if doc.get('executive_summary'):
                    context_parts.append(f"    Summary: {doc['executive_summary'][:200]}")

        # Mother's admissions
        admissions = self.evidence.get('mother_admissions', [])
        if admissions:
            context_parts.append(f"\nMOTHER'S ADMISSIONS ({len(admissions)} documents):")
            for doc in admissions[:3]:
                context_parts.append(f"  - {doc.get('original_filename', 'Unknown')}")
                if doc.get('executive_summary'):
                    context_parts.append(f"    {doc['executive_summary'][:200]}")

        # Medical/Forensic
        medical = self.evidence.get('medical_forensic', [])
        if medical:
            context_parts.append(f"\nMEDICAL/FORENSIC RECORDS ({len(medical)} total):")
            for doc in medical[:3]:
                context_parts.append(f"  - {doc.get('original_filename', 'Unknown')} "
                                   f"(Type: {doc.get('document_type', 'Unknown')})")

        # Police reports
        police = self.evidence.get('police_reports', [])
        if police:
            context_parts.append(f"\nPOLICE REPORTS ({len(police)} total):")
            for doc in police[:3]:
                context_parts.append(f"  - {doc.get('original_filename', 'Unknown')}")
                if doc.get('executive_summary'):
                    context_parts.append(f"    {doc['executive_summary'][:150]}")

        # Timeline
        timeline = self.evidence.get('timeline', [])
        if timeline:
            context_parts.append(f"\nTIMELINE ({len(timeline)} dated events):")
            # Show first and last 3 events
            for doc in timeline[:3]:
                date = doc.get('document_date', 'Unknown date')
                filename = doc.get('original_filename', 'Unknown')
                context_parts.append(f"  - {date}: {filename}")
            if len(timeline) > 6:
                context_parts.append(f"  ... {len(timeline) - 6} more events ...")
            for doc in timeline[-3:]:
                date = doc.get('document_date', 'Unknown date')
                filename = doc.get('original_filename', 'Unknown')
                context_parts.append(f"  - {date}: {filename}")

        return '\n'.join(context_parts)


if __name__ == "__main__":
    print("⚠️  This is a library module. Use run_form_filler.py to run.")
