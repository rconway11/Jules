from config import TARGET_CITIES, KEYWORDS

def filter_jobs(jobs):
    filtered = []
    seen = set()

    for job in jobs:
        # Deduplication
        job_id = f"{job['company']}-{job['title']}-{job['location']}"
        if job_id in seen:
            continue

        # Keyword check
        title_lower = job['title'].lower()
        keyword_match = any(kw.lower() in title_lower for kw in KEYWORDS)

        # Also check if EMT is a standalone word
        if not keyword_match:
            import re
            keyword_match = any(re.search(rf'\b{re.escape(kw.lower())}\b', title_lower) for kw in KEYWORDS)

        if not keyword_match:
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

        # If location is N/A or empty, we might want to include it if the company is in the Bay Area
        if location_lower in ["n/a", "", "various locations", "california", "united states"]:
            city_match = True

        if is_john_muir_target or city_match:
            filtered.append(job)
            seen.add(job_id)

    return filtered
