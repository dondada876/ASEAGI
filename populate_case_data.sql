-- ============================================================================
-- POPULATE COMPREHENSIVE CASE DATA
-- Case: In re Ashe B., J24-00478
-- Realistic legal violations, court events, and communications
-- ============================================================================
-- Author: ASEAGI System
-- Date: 2025-11-05
-- Purpose: Populate dashboard with comprehensive case data
-- ============================================================================

-- ============================================================================
-- 1. LEGAL VIOLATIONS
-- ============================================================================

-- Clear existing test data if needed
-- DELETE FROM legal_violations WHERE case_number = 'J24-00478';

-- Insert comprehensive violations based on typical family law case

INSERT INTO legal_violations (
    violation_title,
    violation_description,
    violation_date,
    violation_category,
    perpetrator,
    severity_score,
    proof_strength_score,
    case_number,
    violation_location,
    legal_code_violated,
    evidence_document_ids,
    witness_list,
    reported_to_court,
    court_response,
    damages_claimed
) VALUES

-- DVRO Violations
(
    'Violation of DVRO - Unauthorized Contact via Text',
    'Respondent sent threatening text messages to protected party in violation of active Domestic Violence Restraining Order issued 2024-08-01. Messages contained threats and harassment.',
    '2024-08-15 14:30:00',
    'DVRO_VIOLATION',
    'Jane Doe',
    95,
    90,
    'J24-00478',
    'Via cell phone',
    'California Family Code §6320, Penal Code §273.6',
    ARRAY['TEXT-001', 'DVRO-2024-001'],
    ARRAY['John Smith', 'Detective Johnson'],
    TRUE,
    'Court issued Order to Show Cause',
    NULL
),

(
    'Violation of DVRO - Proximity Violation at School',
    'Respondent came within 100 yards of protected party at child''s school in violation of DVRO stay-away order. Documented by school security cameras and principal.',
    '2024-08-20 15:45:00',
    'DVRO_VIOLATION',
    'Jane Doe',
    90,
    95,
    'J24-00478',
    'Oak Elementary School, 123 Main St',
    'California Family Code §6320, Penal Code §273.6',
    ARRAY['VIDEO-001', 'PRINCIPAL-STMT-001', 'DVRO-2024-001'],
    ARRAY['Principal Martinez', 'Security Guard Wilson'],
    TRUE,
    'Pending hearing',
    NULL
),

(
    'Violation of DVRO - Third Party Contact',
    'Respondent used her mother to contact protected party multiple times, violating no-contact provisions. Mother admitted to acting as intermediary at respondent''s direction.',
    '2024-08-25 10:00:00',
    'DVRO_VIOLATION',
    'Jane Doe',
    85,
    85,
    'J24-00478',
    'Protected party residence',
    'California Family Code §6320',
    ARRAY['WITNESS-STMT-002', 'PHONE-RECORDS-001'],
    ARRAY['Mother of respondent (Maria Doe)', 'Protected party'],
    TRUE,
    NULL,
    NULL
),

-- Perjury Violations
(
    'Perjury - False Income Declaration',
    'Respondent declared income as $2,500/month in sworn declaration dated 2024-08-10, when IRS tax returns, W-2s, and bank statements show actual income of $6,200/month. Intentional false statement under oath to reduce support obligations.',
    '2024-08-10 09:00:00',
    'PERJURY',
    'Jane Doe',
    98,
    100,
    'J24-00478',
    'Sworn Declaration to Superior Court',
    'California Penal Code §118',
    ARRAY['TAX-2023-W2', 'TAX-2023-1040', 'BANK-STATEMENTS-001-012', 'DECLARATION-2024-08-10'],
    ARRAY['IRS Records', 'Employer HR Department'],
    TRUE,
    'Under investigation',
    NULL
),

(
    'Perjury - False Statement Regarding Custody Schedule',
    'Respondent testified under oath on 2024-08-15 that she exercises 50% custody time. School records, daycare records, and calendar evidence shows actual custody time is 12%. Demonstrable false testimony to support custody modification request.',
    '2024-08-15 14:00:00',
    'PERJURY',
    'Jane Doe',
    95,
    98,
    'J24-00478',
    'Superior Court testimony',
    'California Penal Code §118',
    ARRAY['SCHOOL-ATTENDANCE-2024', 'DAYCARE-RECORDS-001', 'CALENDAR-LOG-001'],
    ARRAY['Teacher Anderson', 'Daycare Director Chen', 'Protected party'],
    TRUE,
    NULL,
    NULL
),

(
    'Perjury - False Claim of Domestic Violence',
    'Respondent filed declaration claiming physical assault on 2024-07-20. Police report from that date shows officers found no evidence of assault, no visible injuries, and noted inconsistent statements. Medical records show no treatment. False claim made under penalty of perjury.',
    '2024-07-25 10:00:00',
    'PERJURY',
    'Jane Doe',
    92,
    95,
    'J24-00478',
    'Sworn Declaration for DVRO',
    'California Penal Code §118, Family Code §6203',
    ARRAY['POLICE-REPORT-2024-07-20', 'MEDICAL-RECORDS-NONE', 'DECLARATION-FALSE-DV'],
    ARRAY['Officer Martinez', 'Officer Johnson', 'Paramedic Williams'],
    TRUE,
    'Evidence submitted to court',
    NULL
),

-- Fraud / Contempt
(
    'Contempt of Court - Willful Disobedience of Court Order',
    'Despite court order dated 2024-08-05 requiring return of child at 6:00 PM every Sunday, respondent repeatedly returned child late (8-10 PM) for six consecutive weeks. Documented via text messages acknowledging the order and intentional violations.',
    '2024-09-15 20:00:00',
    'CONTEMPT_OF_COURT',
    'Jane Doe',
    88,
    90,
    'J24-00478',
    'Multiple locations',
    'California Code of Civil Procedure §1218',
    ARRAY['COURT-ORDER-2024-08-05', 'TEXT-MESSAGES-001-020', 'LOG-001'],
    ARRAY['Protected party', 'Daycare staff (witnessed late pickups)'],
    TRUE,
    'Motion for Contempt filed',
    NULL
),

(
    'Fraud - Concealment of Assets',
    'Respondent failed to disclose $45,000 in cryptocurrency holdings and $22,000 in secondary bank account on FL-150 Income and Expense Declaration. Assets discovered through subpoena of financial records.',
    '2024-08-12 09:00:00',
    'FRAUD',
    'Jane Doe',
    94,
    92,
    'J24-00478',
    'FL-150 Form filed with court',
    'California Family Code §2100-2113 (Fiduciary Duty)',
    ARRAY['FL-150-FALSE', 'BANK-RECORDS-HIDDEN', 'CRYPTO-RECORDS-001'],
    ARRAY['Bank records', 'Coinbase records'],
    TRUE,
    'Discovery sanctions requested',
    67000
),

-- Parental Alienation / Interference
(
    'Parental Alienation - Disparagement of Parent',
    'Respondent repeatedly told child (age 6) that father "doesn''t love you" and "abandoned us," documented by child''s therapist notes and recordings. Causing emotional harm and interfering with parent-child relationship.',
    '2024-09-01 16:00:00',
    'PARENTAL_ALIENATION',
    'Jane Doe',
    87,
    85,
    'J24-00478',
    'In presence of minor child',
    'California Family Code §3020 (Best Interest of Child)',
    ARRAY['THERAPIST-NOTES-001', 'AUDIO-RECORDING-001', 'CHILD-STATEMENTS'],
    ARRAY['Dr. Sarah Thompson (Child Psychologist)', 'Protected party'],
    TRUE,
    'Therapist appointed by court',
    NULL
),

(
    'Interference with Custody - Denied Court-Ordered Visitation',
    'Respondent denied protected party''s court-ordered visitation on 2024-09-07 claiming child was "sick" when child was observed at park with respondent 2 hours later, appearing healthy. No medical documentation provided.',
    '2024-09-07 10:00:00',
    'CUSTODY_INTERFERENCE',
    'Jane Doe',
    85,
    88,
    'J24-00478',
    'Respondent''s residence',
    'California Family Code §3027-3028, Penal Code §278.5',
    ARRAY['TEXT-DENIAL-001', 'PHOTO-PARK-001', 'WITNESS-STMT-PARK'],
    ARRAY['Neighbor witness', 'Protected party'],
    TRUE,
    NULL,
    NULL
),

-- False Police Reports
(
    'Filing False Police Report',
    'Respondent called police on 2024-08-22 claiming protected party was "trespassing and threatening." Police investigation revealed protected party had legal right to be at location (joint property) and no threats were made. Respondent admitted she called to "cause problems." False report wasted police resources.',
    '2024-08-22 19:30:00',
    'FALSE_POLICE_REPORT',
    'Jane Doe',
    80,
    85,
    'J24-00478',
    '456 Oak Street (joint property)',
    'California Penal Code §148.5',
    ARRAY['POLICE-REPORT-2024-08-22', 'PROPERTY-DEED-001', 'OFFICER-BODYCAM-001'],
    ARRAY['Officer Davis', 'Officer Kim', 'Protected party'],
    TRUE,
    'Police declined to file charges against protected party',
    NULL
),

-- Discovery Violations
(
    'Discovery Violation - Failure to Respond to Interrogatories',
    'Respondent failed to respond to Form Interrogatories (Set One) served 2024-07-15, due 2024-08-15. No responses provided despite meet-and-confer letter. Obstruction of discovery process.',
    '2024-08-16 09:00:00',
    'DISCOVERY_VIOLATION',
    'Jane Doe',
    75,
    95,
    'J24-00478',
    'Legal discovery process',
    'California Code of Civil Procedure §2030.290',
    ARRAY['INTERROGATORIES-001', 'PROOF-SERVICE-001', 'MEET-CONFER-LETTER'],
    ARRAY['Process server', 'Attorney of record'],
    TRUE,
    'Motion to Compel filed',
    NULL
),

(
    'Discovery Violation - Spoliation of Evidence',
    'Respondent deleted all text messages from period 2024-06-01 to 2024-08-01 after being served with discovery requests specifically asking for communications. Phone records show messages existed but were intentionally deleted.',
    '2024-08-18 14:00:00',
    'DISCOVERY_VIOLATION',
    'Jane Doe',
    90,
    88,
    'J24-00478',
    'Electronic communications',
    'California Code of Civil Procedure §2023.030',
    ARRAY['PHONE-METADATA-001', 'DISCOVERY-REQUEST-001', 'FORENSIC-REPORT-001'],
    ARRAY['Cell phone carrier records', 'Forensic examiner'],
    TRUE,
    'Sanctions requested for spoliation',
    NULL
),

-- Constitutional Violations
(
    'Violation of Due Process Rights',
    'Court granted ex parte order without notice to protected party on 2024-08-08 based on false emergency claims. Protected party denied opportunity to be heard, violating constitutional due process rights.',
    '2024-08-08 10:00:00',
    'CONSTITUTIONAL_VIOLATION',
    'Judge (misled by Jane Doe)',
    85,
    80,
    'J24-00478',
    'Superior Court ex parte hearing',
    'U.S. Constitution Amendment 14, California Constitution Article I §7',
    ARRAY['EX-PARTE-ORDER-001', 'FALSE-DECLARATION-001'],
    ARRAY['Protected party', 'Court clerk'],
    TRUE,
    'Order vacated after noticed hearing',
    NULL
),

-- Child Endangerment
(
    'Child Endangerment - Driving Under Influence with Minor',
    'Respondent was arrested for DUI on 2024-09-10 with minor child (age 6) in vehicle. BAC 0.12%. Child services investigated. Criminal charges pending.',
    '2024-09-10 21:45:00',
    'CHILD_ENDANGERMENT',
    'Jane Doe',
    100,
    100,
    'J24-00478',
    'Highway 101, mile marker 42',
    'California Penal Code §273a, Vehicle Code §23572',
    ARRAY['POLICE-ARREST-REPORT-001', 'BAC-TEST-001', 'CPS-REPORT-001'],
    ARRAY['Officer Thompson', 'CHP Officer Garcia', 'CPS Investigator Lee'],
    TRUE,
    'Emergency custody modification hearing set',
    NULL
),

-- Financial Violations
(
    'Unauthorized Use of Joint Funds',
    'Respondent withdrew $18,000 from joint account on 2024-08-03 (after filing) without consent and spent on personal expenses including vacation. Family Code requires written agreement for withdrawals over $5,000.',
    '2024-08-03 11:20:00',
    'FINANCIAL_VIOLATION',
    'Jane Doe',
    82,
    95,
    'J24-00478',
    'Wells Fargo Joint Account #xxx-1234',
    'California Family Code §1100-1102',
    ARRAY['BANK-STATEMENTS-001', 'WITHDRAWAL-RECEIPT-001', 'CREDIT-CARD-VACATION'],
    ARRAY['Bank records', 'Credit card statements'],
    TRUE,
    'Motion for reimbursement filed',
    18000
),

-- Harassment
(
    'Harassment via Social Media',
    'Respondent created fake social media accounts to harass protected party and post false information about custody case. 23 posts identified over 3-week period.',
    '2024-09-15 00:00:00',
    'HARASSMENT',
    'Jane Doe',
    78,
    75,
    'J24-00478',
    'Facebook, Instagram',
    'California Penal Code §653.2',
    ARRAY['SOCIAL-MEDIA-POSTS-001-023', 'IP-ADDRESS-TRACE'],
    ARRAY['Protected party', 'Digital forensics investigator'],
    TRUE,
    NULL,
    NULL
),

-- School Interference
(
    'Interference with Child''s Education',
    'Respondent changed child''s school without consulting protected party (joint legal custody). Removed child from established school mid-semester causing educational disruption.',
    '2024-09-20 08:00:00',
    'CUSTODY_INTERFERENCE',
    'Jane Doe',
    80,
    90,
    'J24-00478',
    'School enrollment change',
    'California Family Code §3003 (Joint Legal Custody)',
    ARRAY['ENROLLMENT-RECORDS-001', 'COURT-ORDER-JOINT-CUSTODY'],
    ARRAY['Principal at original school', 'Teacher'],
    TRUE,
    'Motion for orders filed',
    NULL
),

-- Witness Tampering
(
    'Attempted Witness Intimidation',
    'Respondent contacted potential witness (neighbor) and asked them "not to get involved" and offered to "make it worth your while" if witness didn''t testify. Witness reported to protected party''s attorney.',
    '2024-09-25 16:30:00',
    'WITNESS_TAMPERING',
    'Jane Doe',
    92,
    85,
    'J24-00478',
    'Witness residence',
    'California Penal Code §136.1',
    ARRAY['WITNESS-STMT-INTIMIDATION', 'RECORDING-001'],
    ARRAY['Neighbor witness', 'Protected party attorney'],
    TRUE,
    'Reported to District Attorney',
    NULL
),

-- Document Forgery
(
    'Forgery of Consent Document',
    'Respondent forged protected party''s signature on medical consent form dated 2024-09-05. Handwriting analysis confirms forgery. Used to authorize medical procedure without actual consent.',
    '2024-09-05 14:00:00',
    'FORGERY',
    'Jane Doe',
    96,
    93,
    'J24-00478',
    'Pediatric office',
    'California Penal Code §470',
    ARRAY['FORGED-CONSENT-001', 'HANDWRITING-ANALYSIS-001', 'DOCTOR-STMT'],
    ARRAY['Handwriting expert', 'Doctor', 'Protected party'],
    TRUE,
    'Criminal complaint filed',
    NULL
);

-- ============================================================================
-- 2. COURT EVENTS
-- ============================================================================

INSERT INTO court_events (
    event_title,
    event_type,
    event_date,
    event_description,
    court_location,
    judge_name,
    case_number,
    event_outcome,
    next_steps,
    documents_filed,
    appearance_required
) VALUES

(
    'Initial Filing - Request for DVRO',
    'FILING',
    '2024-07-25 09:00:00',
    'Petitioner filed Request for Domestic Violence Restraining Order (DV-100) with supporting declaration',
    'Superior Court of California, County of Santa Clara',
    'Commissioner Rodriguez',
    'J24-00478',
    'Temporary restraining order granted same day',
    'Hearing set for 2024-08-15',
    ARRAY['DV-100', 'DV-110', 'Declaration'],
    FALSE
),

(
    'Ex Parte Hearing - Emergency Custody Orders',
    'EX_PARTE',
    '2024-08-08 08:30:00',
    'Respondent filed ex parte request for emergency custody modification claiming false emergency. Court granted without notice to petitioner.',
    'Superior Court of California, County of Santa Clara',
    'Judge Wilson',
    'J24-00478',
    'Ex parte order granted; vacated 3 days later after noticed hearing',
    'Order vacated 2024-08-11',
    ARRAY['Ex parte application', 'False declaration'],
    TRUE
),

(
    'DVRO Hearing',
    'HEARING',
    '2024-08-15 13:30:00',
    'Noticed hearing on Request for Domestic Violence Restraining Order. Both parties present with counsel.',
    'Superior Court of California, County of Santa Clara, Dept 12',
    'Commissioner Rodriguez',
    'J24-00478',
    'DVRO granted for 3 years. Stay-away order: 100 yards. No-contact order in effect.',
    'Respondent ordered to stay 100 yards away, no contact',
    ARRAY['DV-130 Order', 'Findings and Order After Hearing'],
    TRUE
),

(
    'Order to Show Cause Re: Contempt (DVRO Violation #1)',
    'OSC',
    '2024-08-28 10:00:00',
    'OSC hearing regarding respondent''s violation of DVRO via text messages on 2024-08-15',
    'Superior Court of California, County of Santa Clara, Dept 12',
    'Commissioner Rodriguez',
    'J24-00478',
    'Contempt found. Respondent ordered to pay $500 fine and complete DV classes',
    'Fine due within 30 days; DV classes within 90 days',
    ARRAY['OSC Declaration', 'Evidence of texts', 'Contempt order'],
    TRUE
),

(
    'Case Management Conference',
    'GENERAL',
    '2024-09-05 09:00:00',
    'Status conference to discuss custody evaluation and trial setting',
    'Superior Court of California, County of Santa Clara, Dept 12',
    'Judge Martinez',
    'J24-00478',
    'Custody evaluator appointed: Dr. Jennifer Lee. Trial set for 2024-12-10',
    'Evaluation to be completed by 2024-11-15',
    ARRAY['Case management order'],
    TRUE
),

(
    'Motion Hearing - Contempt (Late Custody Exchanges)',
    'HEARING',
    '2024-09-18 14:00:00',
    'Hearing on petitioner''s motion for contempt regarding repeated late custody exchanges',
    'Superior Court of California, County of Santa Clara, Dept 12',
    'Judge Martinez',
    'J24-00478',
    'Contempt found. Respondent ordered to comply strictly or face jail time. Makeup time ordered.',
    'If late again, jail time will be imposed',
    ARRAY['Motion for Contempt', 'Evidence log', 'Contempt order'],
    TRUE
),

(
    'Emergency Hearing - Child Endangerment (DUI Arrest)',
    'EX_PARTE',
    '2024-09-12 08:30:00',
    'Emergency hearing following respondent''s DUI arrest with minor child in vehicle',
    'Superior Court of California, County of Santa Clara, Dept 12',
    'Judge Martinez',
    'J24-00478',
    'Emergency order: Respondent''s custody suspended pending investigation. Supervised visitation only.',
    'CPS investigation ongoing; next hearing 2024-10-01',
    ARRAY['Police report', 'CPS report', 'Emergency order'],
    TRUE
),

(
    'Review Hearing - Supervised Visitation',
    'HEARING',
    '2024-10-01 13:30:00',
    'Review of supervised visitation order following DUI arrest',
    'Superior Court of California, County of Santa Clara, Dept 12',
    'Judge Martinez',
    'J24-00478',
    'Supervised visitation continued. Respondent must complete substance abuse evaluation and treatment.',
    'Substance abuse evaluation due 2024-10-30; review hearing set for 2024-11-12',
    ARRAY['CPS update', 'Visitation logs', 'Order continuing supervision'],
    TRUE
),

(
    'Discovery Motion - Motion to Compel Responses',
    'HEARING',
    '2024-10-08 10:00:00',
    'Hearing on petitioner''s motion to compel discovery responses (interrogatories and document production)',
    'Superior Court of California, County of Santa Clara, Dept 12',
    'Judge Martinez',
    'J24-00478',
    'Motion granted. Respondent ordered to provide complete responses within 15 days. Sanctions: $2,500.',
    'Responses due 2024-10-23; sanctions payable immediately',
    ARRAY['Motion to Compel', 'Meet and confer letters', 'Order granting motion'],
    TRUE
),

(
    'OSC Re: Sanctions (Spoliation of Evidence)',
    'OSC',
    '2024-10-15 14:00:00',
    'Order to Show Cause why sanctions should not be imposed for deletion of text messages (spoliation)',
    'Superior Court of California, County of Santa Clara, Dept 12',
    'Judge Martinez',
    'J24-00478',
    'Sanctions granted: $5,000 + evidentiary inference that deleted messages were harmful to respondent''s case',
    'Sanctions due within 30 days',
    ARRAY['OSC Declaration', 'Forensic evidence', 'Sanctions order'],
    TRUE
),

(
    'Custody Evaluation Report Filed',
    'FILING',
    '2024-11-10 10:00:00',
    'Court-appointed custody evaluator Dr. Jennifer Lee filed comprehensive evaluation report (140 pages)',
    'Superior Court of California, County of Santa Clara',
    'N/A - Filed document',
    'J24-00478',
    'Report recommends: Primary custody to petitioner, supervised visitation for respondent, reunification therapy',
    'Trial set for 2024-12-10',
    ARRAY['Custody Evaluation Report', 'Psychological testing results', 'Interview summaries'],
    FALSE
),

(
    'Pre-Trial Conference',
    'GENERAL',
    '2024-12-03 09:00:00',
    'Final pre-trial conference before trial. Settlement discussions and trial preparation.',
    'Superior Court of California, County of Santa Clara, Dept 12',
    'Judge Martinez',
    'J24-00478',
    'No settlement reached. Trial confirmed for 2024-12-10. 5-day trial estimate.',
    'Trial to proceed as scheduled',
    ARRAY['Pre-trial statement', 'Witness list', 'Exhibit list'],
    TRUE
),

(
    'Trial - Day 1 (Opening Statements & Petitioner''s Case)',
    'HEARING',
    '2024-12-10 09:00:00',
    'First day of trial. Opening statements. Petitioner presents evidence and witnesses.',
    'Superior Court of California, County of Santa Clara, Dept 12',
    'Judge Martinez',
    'J24-00478',
    'Petitioner testified; 3 witnesses called (police officer, therapist, neighbor)',
    'Trial continues 2024-12-11',
    ARRAY['Trial exhibits PX-001 through PX-045', 'Witness testimony transcripts'],
    TRUE
),

(
    'Trial - Day 2 (Petitioner''s Case Continued)',
    'HEARING',
    '2024-12-11 09:00:00',
    'Continuation of petitioner''s case-in-chief. Additional witnesses and documentary evidence.',
    'Superior Court of California, County of Santa Clara, Dept 12',
    'Judge Martinez',
    'J24-00478',
    'Custody evaluator Dr. Lee testified (2 hours). CPS investigator testified.',
    'Trial continues 2024-12-12',
    ARRAY['Trial exhibits PX-046 through PX-089', 'Expert testimony'],
    TRUE
),

(
    'Trial - Day 3 (Respondent''s Case)',
    'HEARING',
    '2024-12-12 09:00:00',
    'Respondent''s case-in-chief. Respondent testified and presented witnesses.',
    'Superior Court of California, County of Santa Clara, Dept 12',
    'Judge Martinez',
    'J24-00478',
    'Respondent testified (cross-examination revealed numerous inconsistencies). 2 character witnesses.',
    'Trial continues 2024-12-13',
    ARRAY['Respondent exhibits RX-001 through RX-023', 'Respondent testimony'],
    TRUE
);

-- ============================================================================
-- 3. COMMUNICATIONS (Sample)
-- ============================================================================

INSERT INTO communications_matrix (
    communication_date,
    sender,
    recipient,
    communication_method,
    subject,
    summary,
    communication_category,
    is_smoking_gun,
    relevancy_score
) VALUES

(
    '2024-08-15 14:32:00',
    'Jane Doe',
    'John Smith',
    'Text Message',
    'DVRO Violation - Threatening Text',
    'Text message sent 2 weeks after DVRO issued: "You will regret this. I will make sure you never see your son again. Watch your back." Clear violation of no-contact order and threatening language.',
    'EVIDENCE',
    TRUE,
    980
),

(
    '2024-08-20 15:50:00',
    'Principal Martinez',
    'John Smith',
    'Email',
    'Incident Report - Respondent at School',
    'Email from school principal documenting respondent''s appearance at school campus in violation of stay-away order. Security footage attached.',
    'EVIDENCE',
    TRUE,
    950
),

(
    '2024-09-10 22:15:00',
    'Officer Thompson',
    'CPS',
    'Police Report',
    'DUI Arrest with Minor in Vehicle',
    'Police report documenting DUI arrest of Jane Doe with 6-year-old child in vehicle. BAC 0.12%. Child appeared frightened and upset.',
    'EVIDENCE',
    TRUE,
    1000
),

(
    '2024-08-25 11:45:00',
    'Maria Doe (Respondent''s Mother)',
    'John Smith',
    'Phone Call',
    'Third-Party Contact Violation',
    'Recorded phone call where respondent''s mother admits "Jane asked me to call you" regarding custody matters. Clear violation of no-contact order via third party.',
    'EVIDENCE',
    TRUE,
    920
),

(
    '2024-09-01 16:30:00',
    'Dr. Sarah Thompson (Child Psychologist)',
    'Court',
    'Professional Report',
    'Child Therapy Notes - Parental Alienation Concerns',
    'Therapist report documenting child''s statements that mother tells him "daddy doesn''t love you" and "daddy left us." Concerns about parental alienation and emotional abuse.',
    'EVIDENCE',
    TRUE,
    960
);

-- ============================================================================
-- 4. DOCUMENT PAGES (Sample high-relevancy documents)
-- ============================================================================

INSERT INTO document_pages (
    document_id,
    page_number,
    total_pages,
    page_content_summary,
    contains_smoking_gun,
    fraud_indicators,
    perjury_indicators
) VALUES

-- Assuming document_id 1 is the police report
(
    1,
    1,
    6,
    'Police report narrative: Officers responded to 911 call alleging domestic violence. Upon arrival, alleged victim (Jane Doe) had no visible injuries. Officers noted inconsistent statements between initial call and on-scene interview.',
    TRUE,
    15,
    25
),

(
    1,
    2,
    6,
    'Witness statements: Both officers documented that Jane Doe changed her story multiple times. Initial claim of "being pushed and hit" changed to "he yelled at me" when no injuries found.',
    TRUE,
    20,
    30
);

COMMIT;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Check inserted data
SELECT
    'Violations' as table_name,
    COUNT(*) as record_count,
    ROUND(AVG(severity_score), 1) as avg_severity,
    ROUND(AVG(proof_strength_score), 1) as avg_proof_strength
FROM legal_violations
WHERE case_number = 'J24-00478'

UNION ALL

SELECT
    'Court Events' as table_name,
    COUNT(*) as record_count,
    NULL as avg_severity,
    NULL as avg_proof_strength
FROM court_events
WHERE case_number = 'J24-00478'

UNION ALL

SELECT
    'Communications' as table_name,
    COUNT(*) as record_count,
    NULL as avg_severity,
    ROUND(AVG(relevancy_score), 1) as avg_proof_strength
FROM communications_matrix
WHERE is_smoking_gun = TRUE;
