# Scoring Methodology

## Overview

This document provides comprehensive specifications for all scoring dimensions used in the Athena Guardian Legal Document Scoring System. All scores are on a 0-1000 scale unless otherwise specified.

---

## Score Scale Standard

### Universal Score Scale (0-1000)

```
┌────────────────────────────────────────────────────────┐
│  SCORE INTERPRETATION                                  │
├────────────────────────────────────────────────────────┤
│  900-1000: EXCELLENT / SMOKING GUN / PROSECUTABLE      │
│  800-899:  VERY STRONG / HIGH SIGNIFICANCE            │
│  700-799:  STRONG / SIGNIFICANT                       │
│  600-699:  MODERATE / NOTABLE                         │
│  500-599:  NEUTRAL / UNCERTAIN                        │
│  400-499:  WEAK / CONCERNING                          │
│  300-399:  VERY WEAK / SERIOUS CONCERN                │
│  200-299:  CRITICAL / VIOLATION LIKELY                │
│  100-199:  SEVERE VIOLATION / CRIMINAL                │
│  000-099:  AGGRAVATED / EXTREME VIOLATION             │
└────────────────────────────────────────────────────────┘
```

---

## TIER 1: Document Master Score (DMS)

The Document Master Score aggregates four major dimensions to provide an overall assessment of document quality, credibility, and legal impact.

### Formula

```
DMS = (ES × 0.35) + (LI × 0.35) + (SV × 0.20) + (IC × 0.10)

Where:
  ES = Evidence Strength (0-1000)
  LI = Legal Impact (0-1000)
  SV = Strategic Value (0-1000)
  IC = Intent & Conduct (0-1000)
```

---

## 1. Evidence Strength (ES): 0-1000

**Weight in DMS:** 35%

Measures the reliability, authenticity, and quality of evidence presented in the document.

### Components

#### 1.1 Truth/Reliability (TRU): 0-1000

Assesses the truthfulness of statements in the document.

**Scale:**
```
950-1000: ABSOLUTE TRUTH - Objectively proven, multiple sources
900-949:  PROVEN TRUE - Documented, verified
850-899:  VERY LIKELY TRUE - Strong corroboration
800-849:  PROBABLY TRUE - Good evidence supports
750-799:  LIKELY TRUE - Some evidence supports
700-749:  LEANING TRUE - More evidence for than against
650-699:  UNCERTAIN - Conflicting evidence
600-649:  LEANING FALSE - More evidence against than for
550-599:  PROBABLY FALSE - Some evidence disproves
500-549:  LIKELY FALSE - Good evidence of falsehood
450-499:  VERY LIKELY FALSE - Strong evidence disproves
400-449:  ALMOST CERTAINLY FALSE - Overwhelming evidence
350-399:  PROVEN FALSE - Documented falsehood
300-349:  DELIBERATE LIE - Knowingly false
200-299:  MATERIAL LIE - False + impacts case outcome
100-199:  PERJURY LEVEL - Material lie under oath
000-099:  AGGRAVATED PERJURY - Material lie + obstruction
```

**Calculation Logic:**
```python
def calculate_truth_reliability(statement, evidence_for, evidence_against):
    """
    Calculate TRU score
    """
    # Count corroborating evidence
    corroboration_strength = sum([e.weight for e in evidence_for])

    # Count contradicting evidence
    contradiction_strength = sum([e.weight for e in evidence_against])

    # Calculate net truth score
    if corroboration_strength > contradiction_strength:
        # Statement likely true
        ratio = corroboration_strength / (contradiction_strength + 1)
        tru = min(1000, 500 + (ratio * 100))
    elif contradiction_strength > corroboration_strength:
        # Statement likely false
        ratio = contradiction_strength / (corroboration_strength + 1)
        tru = max(0, 500 - (ratio * 100))
    else:
        # Uncertain
        tru = 500

    # Adjust for statement type
    if statement.under_oath and tru < 500:
        # False statement under oath = perjury territory
        tru = min(tru, 200)

    return int(tru)
```

#### 1.2 Verification Status (VER): 0-1000

Measures how well the information has been verified.

**Scale:**
```
900-1000: Multiple independent verifications
800-899:  Single strong verification (official record)
700-799:  Corroborated by witness testimony
600-699:  Partially verified
500-599:  Unverified but plausible
400-499:  Unverified and questionable
300-399:  Contradicted by other evidence
200-299:  Falsified
100-199:  Proven fabricated
000-099:  Systematic falsification
```

#### 1.3 Source Credibility (SRC): 0-1000

Assesses the credibility of the document's author/source.

**Scale:**
```
900-1000: Expert/professional (doctor, investigator, etc.)
800-899:  Neutral third party with no stake
700-799:  Party with good credibility history
600-699:  Party with mixed credibility
500-599:  Party with unknown credibility
400-499:  Party with questionable credibility
300-399:  Party with poor credibility history
200-299:  Party with established lie pattern
100-199:  Party with perjury history
000-099:  Party with criminal fraud history
```

#### 1.4 Authenticity (AUT): 0-1000

Measures whether the document is genuine and unaltered.

**Scale:**
```
950-1000: Digitally signed, certified
900-949:  Official court filing with stamp
850-899:  Original document, verified signature
800-849:  Certified copy
750-799:  Uncertified copy, appears authentic
700-749:  Copy with some authentication
600-699:  Copy without authentication
500-599:  Authenticity uncertain
400-499:  Potential alterations detected
300-399:  Likely altered/tampered
200-299:  Proven altered
100-199:  Forged document
000-099:  Fabricated document
```

#### 1.5 Evidence Type Quality (EVQ): 0-1000

Rates the inherent strength of the evidence type.

**Scale:**
```
950-1000: Objective physical evidence (medical records, photos)
900-949:  Expert testimony/reports
850-899:  Video/audio recordings
800-849:  Official government records
750-799:  Contemporaneous written records
700-749:  Witness testimony (neutral third party)
650-699:  Party declaration under oath
600-649:  Party statement not under oath
550-599:  Hearsay (admissible)
500-549:  Circumstantial evidence
400-499:  Hearsay (inadmissible)
300-399:  Speculation
200-299:  Opinion without foundation
100-199:  Irrelevant information
000-099:  Inadmissible evidence
```

### Evidence Strength Composite Formula

```python
def calculate_evidence_strength(document):
    """
    Calculate ES composite score
    """
    tru = calculate_truth_reliability(document)
    ver = calculate_verification_status(document)
    src = calculate_source_credibility(document)
    aut = calculate_authenticity(document)
    evq = calculate_evidence_type_quality(document)

    # Weighted average
    es = (tru * 0.30 +
          ver * 0.25 +
          src * 0.20 +
          aut * 0.15 +
          evq * 0.10)

    return int(es)
```

---

## 2. Legal Impact (LI): 0-1000

**Weight in DMS:** 35%

Measures the document's impact on legal outcomes and whether it meets legal standards.

### Components

#### 2.1 Proves Statutory Element (LGW): 0-1000

Assesses whether the document proves required elements of a legal claim.

**Scale:**
```
950-1000: Proves all elements decisively
900-949:  Proves most elements strongly
850-899:  Proves key elements
800-849:  Proves several elements
750-799:  Proves some elements
700-749:  Supports elements partially
600-699:  Relevant to elements
500-599:  Tangentially related
400-499:  Minimal relevance
300-399:  Unclear relevance
200-299:  Not relevant to elements
100-199:  Contradicts own case
000-099:  Proves opponent's case
```

**Example: Perjury (PC § 118)**
```python
def prove_perjury_elements(statement):
    """
    Perjury requires proving:
    1. Statement made under oath
    2. Statement was false
    3. Statement was material
    4. Defendant knew it was false
    """
    elements_proven = 0

    if statement.under_oath:
        elements_proven += 250  # Element 1

    if statement.truth_score < 300:  # Proven false
        elements_proven += 250  # Element 2

    if statement.materiality_score > 800:
        elements_proven += 250  # Element 3

    if statement.intent_score > 800:  # Knowing falsehood
        elements_proven += 250  # Element 4

    return elements_proven  # Max 1000
```

#### 2.2 Admissibility (ADM): 0-1000

Assesses whether evidence is admissible in court.

**Scale:**
```
900-1000: Clearly admissible, no objections likely
800-899:  Admissible under standard rules
700-799:  Likely admissible
600-699:  Admissible with foundation
500-599:  Admissibility uncertain
400-499:  Likely inadmissible
300-399:  Inadmissible without exception
200-299:  Clearly inadmissible
100-199:  Prejudicial, must be excluded
000-099:  Illegal evidence
```

#### 2.3 Legal Standard Met (LSM): 0-1000

Assesses whether document meets the burden of proof for relevant legal standards.

**Legal Standards:**
```
Preponderance of Evidence (Civil):     > 500/1000  (50%)
Clear and Convincing (Some Civil):     > 750/1000  (75%)
Beyond Reasonable Doubt (Criminal):    > 950/1000  (95%)
```

**Scale:**
```
950-1000: Meets beyond reasonable doubt
900-949:  Very strong, near certainty
850-899:  Clear and convincing
800-849:  Strong preponderance
750-799:  Preponderance met
700-749:  Likely meets preponderance
600-699:  Close to preponderance
500-599:  Neutral/uncertain
400-499:  Below preponderance
300-399:  Weak evidence
200-299:  Very weak
100-199:  Minimal value
000-099:  No probative value
```

#### 2.4 Precedent Value (PRE): 0-1000

Assesses the document's value as precedent or authority.

**Scale:**
```
900-1000: Binding precedent/statute
800-899:  Persuasive authority
700-799:  Relevant case law
600-699:  Analogous authority
500-599:  General legal principle
400-499:  Weak authority
300-399:  Inapplicable precedent
200-299:  Outdated/overruled
100-199:  Contradicts precedent
000-099:  Legally incorrect
```

### Legal Impact Composite Formula

```python
def calculate_legal_impact(document):
    """
    Calculate LI composite score
    """
    lgw = calculate_proves_elements(document)
    adm = calculate_admissibility(document)
    lsm = calculate_legal_standard(document)
    pre = calculate_precedent_value(document)

    # Weighted average
    li = (lgw * 0.40 +
          adm * 0.30 +
          lsm * 0.20 +
          pre * 0.10)

    return int(li)
```

---

## 3. Strategic Value (SV): 0-1000

**Weight in DMS:** 20%

Measures the document's strategic importance in the case.

### Components

#### 3.1 Case Impact (IMP): 0-1000

Assesses how much this document impacts the overall case outcome.

**Scale:**
```
950-1000: Case-determinative (smoking gun)
900-949:  Critical to case outcome
850-899:  Very significant impact
800-849:  Significant impact
750-799:  Important evidence
700-749:  Notable contribution
600-699:  Moderate importance
500-599:  Some relevance
400-499:  Minor relevance
300-399:  Minimal impact
200-299:  Negligible impact
100-199:  Irrelevant
000-099:  Harmful to case
```

#### 3.2 Opposition Impact (OPP): 0-1000

Measures impact on opposing party's case.

**Scale:**
```
900-1000: Destroys opposition's case
800-899:  Severely undermines opposition
700-799:  Significantly weakens opposition
600-699:  Moderately weakens opposition
500-599:  Neutral
400-499:  Slightly strengthens opposition
300-399:  Moderately strengthens opposition
200-299:  Significantly strengthens opposition
100-199:  Severely strengthens opposition
000-099:  Proves opposition's case
```

#### 3.3 Timeline Significance (TIM): 0-1000

Measures significance based on when document was created/filed.

**Scale:**
```
900-1000: Contemporaneous with key event
800-899:  Within 24 hours of key event
700-799:  Within 48 hours
600-699:  Within one week
500-599:  Within one month
400-499:  Within three months
300-399:  Within six months
200-299:  Within one year
100-199:  More than one year after
000-099:  Untimely/stale
```

#### 3.4 Evidence Gap Filled (EGF): 0-1000

Measures whether document fills a critical gap in evidence.

**Scale:**
```
900-1000: Fills critical missing element
800-899:  Fills important gap
700-799:  Adds new significant evidence
600-699:  Supplements existing evidence
500-599:  Corroborates existing evidence
400-499:  Duplicative of other evidence
300-399:  Redundant
200-299:  Adds nothing new
100-199:  Conflicts with other evidence
000-099:  Creates evidentiary problems
```

### Strategic Value Composite Formula

```python
def calculate_strategic_value(document, case_context):
    """
    Calculate SV composite score
    """
    imp = calculate_case_impact(document, case_context)
    opp = calculate_opposition_impact(document, case_context)
    tim = calculate_timeline_significance(document, case_context)
    egf = calculate_evidence_gap(document, case_context)

    # Weighted average
    sv = (imp * 0.35 +
          opp * 0.30 +
          tim * 0.20 +
          egf * 0.15)

    return int(sv)
```

---

## 4. Intent & Conduct (IC): 0-1000

**Weight in DMS:** 10%

Measures the intent and behavior of the document's author.

### 4.1 Intent Classification (INT): 0-1000

Classifies the intent behind statements/actions.

**Scale (Inverted for IC - Higher = Worse Intent):**
```
PROTECTIVE/GOOD FAITH (0-350):
000-099:  HEROIC - Extraordinary protective action
100-199:  EXEMPLARY - Above-and-beyond care
200-299:  DILIGENT - High standard of care
300-349:  GOOD FAITH - Reasonable belief, proper care

NEUTRAL/ACCIDENTAL (350-650):
350-449:  REASONABLE - Normal standard
450-549:  ACCIDENTAL - Honest mistake
550-649:  NEGLIGENT - Should have known

BAD FAITH (650-1000):
650-699:  CARELESS - Below standard
700-749:  RECKLESS - Conscious disregard
750-799:  KNOWING - Intentional wrongdoing
800-849:  WILLFUL - Deliberate with awareness
850-899:  MALICIOUS - Intent to harm
900-949:  MALEVOLENT - Extreme malice
950-1000: CORRUPT - Criminal corruption level
```

### 4.2 Bad Faith Quantification (BFQ): 0-1000

Quantifies specific bad faith behaviors.

**Bad Faith Factors:**
```python
BFQ_FACTORS = {
    # Timing Manipulation (0-200 points)
    'timing_manipulation': {
        'filed_immediately_after_protective_action': 150,
        'filed_on_eve_of_hearing': 120,
        'filed_to_preempt_evidence': 180,
        'filed_during_holiday_weekend': 80,
        'strategic_timing_pattern': 200
    },

    # Forum Shopping (0-200 points)
    'forum_shopping': {
        'judge_shopping': 150,
        'venue_manipulation': 120,
        'jurisdiction_gaming': 180,
        'serial_refiling': 200,
        'ex_parte_abuse': 170
    },

    # Evidence Manipulation (0-200 points)
    'evidence_manipulation': {
        'concealed_evidence': 180,
        'destroyed_evidence': 200,
        'fabricated_evidence': 200,
        'selective_disclosure': 150,
        'withheld_material_facts': 170
    },

    # Child Endangerment (0-200 points)
    'child_endangerment': {
        'ignored_abuse_disclosure': 200,
        'exposed_child_to_abuser': 190,
        'blocked_protective_investigation': 180,
        'prioritized_custody_over_safety': 170,
        'retaliated_against_protective_parent': 160
    },

    # Procedural Abuse (0-200 points)
    'procedural_abuse': {
        'perjury': 200,
        'fraud_on_court': 190,
        'false_emergency_claims': 180,
        'violation_of_orders': 150,
        'contempt': 140,
        'obstruction': 170
    }
}

def calculate_bfq(document, party_history):
    """
    Calculate Bad Faith Quantification
    """
    applicable_factors = detect_bad_faith_factors(document, party_history)

    # Sum points from each category
    category_sums = {}
    for category, factors in applicable_factors.items():
        category_sums[category] = sum(factors.values())

    # Average across categories, scale to 1000
    avg_per_category = sum(category_sums.values()) / len(BFQ_FACTORS)
    bfq = (avg_per_category / 200) * 1000  # Normalize to 0-1000

    return int(min(1000, bfq))
```

### Intent & Conduct Composite Formula

```python
def calculate_intent_conduct(document, party_history):
    """
    Calculate IC composite score
    """
    intent = calculate_intent_classification(document)
    bfq = calculate_bad_faith_quantification(document, party_history)

    # Weighted average
    ic = (intent * 0.50 +
          bfq * 0.50)

    return int(ic)
```

---

## Document Master Score Calculation

### Complete Formula with Example

```python
def calculate_document_master_score(document, case_context):
    """
    Calculate complete Document Master Score (DMS)
    """

    # Calculate dimension scores
    es = calculate_evidence_strength(document)          # e.g., 870/1000
    li = calculate_legal_impact(document)                # e.g., 920/1000
    sv = calculate_strategic_value(document, case_context)  # e.g., 880/1000
    ic = calculate_intent_conduct(document, case_context)   # e.g., 940/1000

    # Weighted composite
    dms = (es * 0.35 +
           li * 0.35 +
           sv * 0.20 +
           ic * 0.10)

    # Example calculation:
    # dms = (870 * 0.35) + (920 * 0.35) + (880 * 0.20) + (940 * 0.10)
    #     = 304.5 + 322 + 176 + 94
    #     = 896.5

    return {
        'dms': int(dms),
        'evidence_strength': es,
        'legal_impact': li,
        'strategic_value': sv,
        'intent_conduct': ic,
        'category': categorize_score(dms),
        'confidence': calculate_confidence(document)
    }

def categorize_score(dms):
    """
    Categorize DMS into actionable bands
    """
    if dms >= 900:
        return "SMOKING GUN"
    elif dms >= 800:
        return "VERY STRONG"
    elif dms >= 700:
        return "STRONG"
    elif dms >= 600:
        return "MODERATE"
    elif dms >= 500:
        return "NEUTRAL"
    elif dms >= 400:
        return "WEAK"
    elif dms >= 300:
        return "VERY WEAK"
    elif dms >= 200:
        return "CRITICAL"
    elif dms >= 100:
        return "SEVERE"
    else:
        return "EXTREME"
```

---

## TIER 2: Collection Master Score (CMS)

Aggregates document scores for entire motion/brief.

```python
def calculate_collection_master_score(documents, collection_context):
    """
    Calculate Collection Master Score for motion/brief
    """
    doc_scores = [doc.dms for doc in documents]

    cms = {
        # Basic statistics
        'avg_document_score': mean(doc_scores),
        'max_document_score': max(doc_scores),
        'min_document_score': min(doc_scores),
        'median_document_score': median(doc_scores),
        'std_deviation': stdev(doc_scores),

        # Counts
        'document_count': len(documents),
        'smoking_gun_count': sum(1 for s in doc_scores if s >= 900),
        'strong_evidence_count': sum(1 for s in doc_scores if s >= 700),
        'weak_evidence_count': sum(1 for s in doc_scores if s < 500),
        'harmful_evidence_count': sum(1 for s in doc_scores if s < 300),

        # Aggregate scores
        'evidence_strength_avg': mean([d.evidence_strength for d in documents]),
        'legal_impact_avg': mean([d.legal_impact for d in documents]),
        'strategic_value_avg': mean([d.strategic_value for d in documents]),
        'intent_conduct_avg': mean([d.intent_conduct for d in documents]),

        # Violations
        'total_violations': count_violations(documents),
        'perjury_count': count_perjuries(documents),
        'fraud_count': count_fraud(documents),

        # Overall CMS (weighted)
        'overall_cms': calculate_weighted_cms(doc_scores, collection_context)
    }

    return cms

def calculate_weighted_cms(doc_scores, context):
    """
    Weight documents by importance in collection
    """
    weighted_sum = 0
    total_weight = 0

    for doc, score in zip(context.documents, doc_scores):
        weight = calculate_document_weight(doc, context)
        weighted_sum += score * weight
        total_weight += weight

    return int(weighted_sum / total_weight)
```

---

## TIER 3: Party Justice Score (PJS)

The "Legal Credit Score" for overall party credibility.

```python
def calculate_party_justice_score(party_id, case_history):
    """
    Calculate Party Justice Score (PJS)
    """

    # Get all documents by this party
    party_docs = get_party_documents(party_id)
    party_statements = get_party_statements(party_id)

    # Truthfulness metrics
    truthfulness = calculate_truthfulness_rate(party_statements)
    lie_density = calculate_lie_density(party_statements)

    # Violation metrics
    perjury_count = count_perjuries(party_statements)
    violation_severity = avg_violation_severity(party_id)

    # Behavioral metrics
    bad_faith_avg = avg_bad_faith_score(party_docs)
    intent_avg = avg_intent_score(party_docs)

    # Risk scores
    flight_risk = calculate_flight_risk(party_id, case_history)
    compliance_risk = calculate_compliance_risk(party_id, case_history)
    harm_risk = calculate_harm_risk(party_id, case_history)

    # Calculate composite PJS
    pjs = calculate_pjs_composite(
        truthfulness=truthfulness,
        lie_density=lie_density,
        violations=perjury_count + violation_severity,
        bad_faith=bad_faith_avg,
        risks=(flight_risk + compliance_risk + harm_risk) / 3
    )

    return {
        'pjs': pjs,
        'rating': categorize_pjs(pjs),
        'truthfulness_rate': truthfulness,
        'lie_density': lie_density,
        'perjury_count': perjury_count,
        'violation_severity_avg': violation_severity,
        'bad_faith_average': bad_faith_avg,
        'risk_scores': {
            'flight_risk': flight_risk,
            'compliance_risk': compliance_risk,
            'harm_risk': harm_risk
        }
    }

def categorize_pjs(pjs):
    """
    Party Justice Score ratings (like credit scores)
    """
    if pjs >= 850:
        return "A+ EXCELLENT"
    elif pjs >= 750:
        return "A VERY GOOD"
    elif pjs >= 650:
        return "B GOOD"
    elif pjs >= 550:
        return "C FAIR"
    elif pjs >= 450:
        return "D POOR"
    elif pjs >= 350:
        return "E VERY POOR"
    else:
        return "F FAILING"
```

---

## Example: Real-World Scoring

### Mother's August 12, 2024 Ex Parte Declaration

**Context:**
- Filed 1 day after father's good cause report
- Filed 2 days after police confirmed child safe
- Child disclosed abuse on August 3, 2024
- Mother admitted in 2021 that grandfather abused her
- Father's passport expired August 6, 2024

**Statement 2:** "Respondent used doctor's report to file Good Cause to further alienate and keep Ashe away from me as he has throughout this case"

**Analysis:**
```python
# Truth-Lie Score: 120/1000 [MALICIOUS FALSEHOOD]
# - Father sought forensic exam due to child's disclosure
# - Purpose was protective, not alienating
# - CONTRADICTS: Mother's own 2021 admission

# Intent-Culpability: 940/1000 [MALEVOLENT]
# - She KNOWS father's concerns legitimate

# Bad Faith Quantification: 960/1000 [EXTREME]
# - Child endangerment: 200
# - Evidence concealment: 180
# - Timing manipulation: 180
# - Procedural abuse: 200
# - Forum shopping: 200

# Context-Relationship: 1000/1000 [MAXIMUM]
# - Filed 1 day after police confirmed child safe
# - Directly contradicts her 2021 admission
# - Caused immediate custody reversal

# Violations:
# - Perjury (PC 118): 980/1000
# - Child Endangerment (PC 273a): 1000/1000
# - Fraud on Court (CCP 473): 950/1000
# - Obstruction (PC 182): 880/1000

# Statement Micro-Score (SMS): 947/1000
# ⚠️ [SMOKING GUN PERJURY]
```

---

## Quality Control & Human Review

### AI Confidence Scores

All AI-generated scores include confidence metrics:

```python
confidence = {
    'overall': 0.95,  # 0-1 scale
    'truth_score': 0.98,
    'intent_score': 0.92,
    'violations': 0.96
}
```

### Human Review Triggers

Automatic human review required when:
- Confidence < 0.80
- Perjury detected (TLS < 200)
- Smoking gun (SMS > 900)
- Child endangerment detected
- Score conflicts between dimensions

### Review Workflow

```python
def require_human_review(analysis):
    """
    Determine if human review needed
    """
    triggers = []

    if analysis.confidence < 0.80:
        triggers.append("LOW_CONFIDENCE")

    if analysis.truth_score < 200:
        triggers.append("PERJURY_DETECTED")

    if analysis.sms > 900:
        triggers.append("SMOKING_GUN")

    if 'child_endangerment' in analysis.violations:
        triggers.append("CHILD_SAFETY")

    return len(triggers) > 0, triggers
```

---

## Continuous Improvement

### Feedback Loop

```python
def update_scoring_model(human_review, ai_analysis):
    """
    Learn from human corrections
    """
    if human_review.truth_score != ai_analysis.truth_score:
        # Record disagreement for model training
        log_disagreement(human_review, ai_analysis)

        # Update model weights if systematic pattern
        if detect_systematic_bias():
            retrain_model()
```

---

**Last Updated:** 2025-11-05
**Version:** 1.0.0
