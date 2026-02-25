import uuid
import datetime
from typing import Dict, Any

def normalize_job(raw_job: Dict[str, Any]) -> Dict[str, Any]:
    """
    Maps scraped fields to canonical schema:
    {id, title, company, location, type, source, url, posted_at, fetched_at, tags, raw}
    """
    return {
        "id": str(uuid.uuid4()),
        "title": raw_job.get("title", "Unknown Title"),
        "company": raw_job.get("company", "Unknown Company"),
        "location": raw_job.get("location", "Portugal"),
        "type": raw_job.get("type", "Full-Time"), # "Internship", "Trainee" etc
        "source": raw_job.get("source", "Unknown"),
        "url": raw_job.get("url", ""),
        "posted_at": raw_job.get("posted_at", None),
        "fetched_at": datetime.datetime.utcnow().isoformat(),
        "tags": raw_job.get("tags", []),
        "raw": raw_job  # Keep raw data for audit/debugging
    }
