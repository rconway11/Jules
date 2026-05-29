from config import TARGET_CITIES, KEYWORDS
from thefuzz import fuzz
import re

def filter_jobs(jobs):
    filtered = []
    seen = set()

    # Threshold for fuzzy matching
    FUZZ_THRESHOLD = 80

    for job in jobs:
        # Deduplication
        job_id = f"{job['company']}-{job['title']}-{job['location']}"
        if job_id in seen:
            continue

        title_lower = job['title'].lower()

        # 1. Exact or Keyword match
        keyword_match = any(kw.lower() in title_lower for kw in KEYWORDS)

        if not keyword_match:
            # Standalone word check for common acronyms
            keyword_match = any(re.search(rf'\b{re.escape(kw.lower())}\b', title_lower) for kw in KEYWORDS)

        # 2. Intelligent Emergency Tech match
        if not keyword_match:
            # Catch "Hospital Tech" or "Emergency Technician" in "Emergency Department"
            is_emergency = any(kw in title_lower for kw in ["emergency", "er ", "er-", "dept", "department", "ed "])
            is_tech = any(kw in title_lower for kw in ["tech", "technician"])
            if is_emergency and is_tech:
                keyword_match = True

        # 3. Fuzzy match fallback
        if not keyword_match:
            for kw in KEYWORDS:
                if len(kw) < 6: continue # Only fuzzy match longer phrases
                score = fuzz.partial_ratio(kw.lower(), title_lower)
                if score >= FUZZ_THRESHOLD:
                    keyword_match = True
                    break

        if not keyword_match:
            continue

        # Noise reduction: Filter out non-clinical technician roles
        noise_keywords = ["biomedical", "field services", "it tech", "information technology", "sleep", "dialysis", "maintenance"]
        if any(noise in title_lower for noise in noise_keywords):
            # Only allow if EMT/ER Tech is explicitly mentioned
            if not any(re.search(rf'\b{kw.lower()}\b', title_lower) for kw in ["emt", "er tech"]):
                continue

        # Location check
        location_lower = job['location'].lower()

        # Special case for John Muir in Concord/Walnut Creek
        is_john_muir_target = (
            job['company'] == "John Muir Health" and
            ("concord" in location_lower or "walnut creek" in location_lower)
        )

        # General distance check (based on city names)
        city_match = any(city.lower() in location_lower for city in TARGET_CITIES)

        if location_lower in ["n/a", "", "various locations", "california", "united states"]:
            city_match = True

        if is_john_muir_target or city_match:
            filtered.append(job)
            seen.add(job_id)

    return filtered
