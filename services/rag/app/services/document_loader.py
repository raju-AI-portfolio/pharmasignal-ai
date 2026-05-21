import httpx
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Directory where we save downloaded documents
DOCS_DIR = Path("./data/documents")

# Free regulatory documents — all publicly available
REGULATORY_DOCUMENTS = [
    {
        "name": "ich_e2b_guidelines",
        "url": "https://database.ich.org/sites/default/files/E2B_R3_Guideline.pdf",
        "description": "ICH E2B R3 — Electronic Transmission of Individual Case Safety Reports"
    },
    {
        "name": "ich_e2a_guidelines", 
        "url": "https://database.ich.org/sites/default/files/E2A_Guideline.pdf",
        "description": "ICH E2A — Clinical Safety Data Management"
    },
]

# We also create synthetic regulatory content
# because some PDFs require authentication
SYNTHETIC_DOCUMENTS = [
    {
        "name": "adverse_event_definitions",
        "content": """
# Adverse Event Definitions and Classification

## What is an Adverse Event?
An adverse event (AE) is any untoward medical occurrence in a patient administered a pharmaceutical product, 
which does not necessarily have a causal relationship with the treatment.

## Serious Adverse Events (SAE)
A serious adverse event is any untoward medical occurrence that:
- Results in death
- Is life-threatening
- Requires inpatient hospitalisation or prolongation of existing hospitalisation
- Results in persistent or significant disability/incapacity
- Is a congenital anomaly/birth defect
- Is a medically important condition

## Adverse Event Severity Grades
- Grade 1: Mild — asymptomatic or mild symptoms
- Grade 2: Moderate — minimal local or noninvasive intervention indicated
- Grade 3: Severe — hospitalisation indicated
- Grade 4: Life-threatening — urgent intervention indicated
- Grade 5: Death related to adverse event

## Causality Assessment
- Certain: A clinical event with plausible time relationship to drug intake
- Probable: A clinical event with reasonable time relationship to drug intake
- Possible: A clinical event with reasonable time relationship to drug intake but could be explained by other causes
- Unlikely: A clinical event whose time relationship to drug intake makes a connection improbable
- Unassessable: Insufficient data to assess causality
        """
    },
    {
        "name": "pharmacovigilance_guidelines",
        "content": """
# Pharmacovigilance Guidelines and Requirements

## ICH E2B Requirements
Individual Case Safety Reports (ICSRs) must be submitted electronically using the ICH E2B format.

### Minimum Data Requirements for ICSR Submission
1. An identifiable reporter
2. An identifiable patient
3. A suspected adverse reaction
4. A suspected medicinal product

## Expedited Reporting Requirements
### 15-day Expedited Reports
Fatal or life-threatening unexpected suspected adverse reactions must be reported within 15 calendar days.

### 7-day Expedited Reports  
Fatal or life-threatening unexpected suspected adverse reactions that are serious must be reported within 7 calendar days.

## Signal Detection
A safety signal is information arising from one or multiple sources suggesting a new potentially causal 
association between an intervention and an event.

### Disproportionality Analysis
- Proportional Reporting Ratio (PRR): Values greater than 2 with chi-square greater than 4 indicate a signal
- Reporting Odds Ratio (ROR): Similar threshold applies
- Minimum case threshold: At least 3 cases required

## QPPV Responsibilities
The Qualified Person for Pharmacovigilance (QPPV) is responsible for:
- Oversight of the pharmacovigilance system
- Acting as contact point for regulatory authorities
- Ensuring appropriate action is taken when required
        """
    },
    {
        "name": "gdpr_clinical_data",
        "content": """
# GDPR Requirements for Clinical and Safety Data

## Legal Basis for Processing
Processing of health data requires explicit consent or another legal basis under Article 9 GDPR.

## Data Subject Rights
- Right to access their personal data
- Right to rectification of inaccurate data
- Right to erasure (right to be forgotten)
- Right to data portability

## Pseudonymisation Requirements
Patient data in safety reports must be pseudonymised:
- Replace patient identifiers with codes
- Store mapping table separately with strict access controls
- Never include direct identifiers in regulatory submissions

## Data Retention
- Clinical trial data: Minimum 25 years after trial completion
- Pharmacovigilance data: Minimum 10 years after product withdrawal
- Safety reports: Lifetime of product plus 10 years

## Cross-border Data Transfer
Transfer of personal data outside EU requires:
- Adequacy decision by European Commission, OR
- Appropriate safeguards (Standard Contractual Clauses), OR
- Binding Corporate Rules for intra-group transfers
        """
    },
    {
        "name": "signal_detection_methodology",
        "content": """
# Signal Detection Methodology in Pharmacovigilance

## Quantitative Signal Detection Methods

### Proportional Reporting Ratio (PRR)
PRR = (a/b) / (c/d)
Where:
- a = number of reports for drug X with reaction Y
- b = number of reports for drug X without reaction Y  
- c = number of reports for all other drugs with reaction Y
- d = number of reports for all other drugs without reaction Y

Signal threshold: PRR >= 2, Chi-square >= 4, case count >= 3

### Reporting Odds Ratio (ROR)
ROR = (a/b) / (c/d) — similar interpretation to PRR
Signal threshold: Lower bound of 95% CI > 1

## Qualitative Signal Detection
- Literature monitoring
- Spontaneous report review
- Clinical trial data review
- Post-marketing surveillance

## Signal Validation Process
1. Data mining to identify potential signal
2. Clinical assessment of cases
3. Literature review
4. Causality assessment
5. Risk-benefit evaluation
6. Regulatory action if required

## Signal Prioritisation
Signals are prioritised based on:
- Seriousness of the reaction
- Frequency of reporting
- Unexpected nature of the reaction
- Vulnerable patient populations affected
        """
    }
]

async def download_documents():
    """
    Creates synthetic regulatory documents for RAG indexing.
    These represent the kind of content found in real regulatory guidelines.
    """
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    
    created = []
    for doc in SYNTHETIC_DOCUMENTS:
        file_path = DOCS_DIR / f"{doc['name']}.txt"
        if not file_path.exists():
            with open(file_path, 'w') as f:
                f.write(doc['content'])
            logger.info(f"Created document: {doc['name']}")
            created.append(doc['name'])
        else:
            logger.info(f"Document already exists: {doc['name']}")
            created.append(doc['name'])
    
    return created