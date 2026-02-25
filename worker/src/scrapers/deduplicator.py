import hashlib
import logging
from typing import List, Dict, Any, Set

logger = logging.getLogger(__name__)

class Deduplicator:
    def __init__(self):
        self.seen_hashes: Set[str] = set()
        
    def _generate_hash(self, job: Dict[str, Any]) -> str:
        """Hashes (title + company + location) to detect duplicates."""
        title = job.get("title", "").lower().strip()
        company = job.get("company", "").lower().strip()
        location = job.get("location", "").lower().strip()
        
        raw_string = f"{title}_{company}_{location}"
        return hashlib.sha256(raw_string.encode('utf-8')).hexdigest()

    def process_and_deduplicate(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Removes duplicates from the given list of jobs.
        Logs deduplication stats.
        """
        initial_count = len(jobs)
        unique_jobs = []
        
        for job in jobs:
            job_hash = self._generate_hash(job)
            if job_hash not in self.seen_hashes:
                self.seen_hashes.add(job_hash)
                unique_jobs.append(job)
                
        duplicates_removed = initial_count - len(unique_jobs)
        logger.info(f"Deduplicator: processed {initial_count}, removed {duplicates_removed} duplicates, returned {len(unique_jobs)} unique.")
        
        return unique_jobs
