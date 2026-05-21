import httpx
import logging

logger = logging.getLogger(__name__)

# FDA public API - no API key needed
FDA_BASE_URL = "https://api.fda.gov/drug/event.json"

async def fetch_adverse_events(limit: int = 10, skip: int = 0) -> dict:
    """
    Fetches adverse event reports from FDA FAERS public API.
    
    limit = how many reports to fetch (max 100 per call)
    skip  = how many reports to skip (for pagination)
    """
    params = {
        "limit": limit,
        "skip": skip
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            logger.info(f"Fetching {limit} reports from FDA API...")
            response = await client.get(FDA_BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Successfully fetched {len(data.get('results', []))} reports")
            return data
        except httpx.TimeoutException:
            logger.error("FDA API request timed out")
            raise
        except httpx.HTTPStatusError as e:
            logger.error(f"FDA API returned error: {e.response.status_code}")
            raise

def parse_report(raw_report: dict) -> dict:
    """
    Extracts the fields we care about from a raw FDA report.
    FDA reports have a complex nested structure - this flattens it.
    """
    try:
        # Get patient info
        patient = raw_report.get("patient", {})
        
        # Get drug info - take the first drug listed
        drugs = patient.get("drug", [])
        drug_name = "Unknown"
        if drugs:
            drug_name = drugs[0].get("medicinalproduct", "Unknown")

        # Get reactions - there can be multiple
        reactions_raw = patient.get("reaction", [])
        reactions = [
            r.get("reactionmeddrapt", "Unknown") 
            for r in reactions_raw
        ]

        # Get patient demographics
        patient_age = patient.get("patientonsetage", None)
        patient_sex = patient.get("patientsex", None)

        # Map sex codes to readable values
        sex_map = {"1": "Male", "2": "Female", "0": "Unknown"}
        patient_sex = sex_map.get(str(patient_sex), "Unknown")

        # Is this a serious report?
        serious = raw_report.get("serious", "2")
        serious = "Yes" if str(serious) == "1" else "No"

        # Get outcome
        outcomes = patient.get("patientdeath", None)
        outcome = "Death" if outcomes else "Unknown"

        return {
            "report_id": raw_report.get("safetyreportid", "Unknown"),
            "drug_name": drug_name,
            "patient_age": str(patient_age) if patient_age else None,
            "patient_sex": patient_sex,
            "reactions": reactions,
            "serious": serious,
            "outcome": outcome,
            "raw_data": raw_report
        }

    except Exception as e:
        logger.error(f"Error parsing report: {e}")
        raise