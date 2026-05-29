# Bay Area EMT & ER Tech Job Finder

This program automatically searches for entry-level EMT and ER Tech roles in the San Francisco Bay Area across multiple hospital and emergency service career portals.

## Features

- **Automated Scraping**: Targets UCSF, Sutter Health, Stanford Health Care, Kaiser Permanente, Dignity Health, El Camino Health, John Muir Health, AMR, and Royal Ambulance.
- **Geographic Filtering**: Focuses on roles within 35 miles of Belmont, CA, with special inclusion of John Muir roles in Concord and Walnut Creek.
- **Keyword Matching**: Searches for "EMT", "ER Tech", "Emergency Room Technician", and related terms.
- **Email Notifications**: Sends a daily summary of found roles via email.

## Setup

1. **Install Dependencies**:
   ```bash
   pip install playwright beautifulsoup4
   playwright install chromium
   ```

2. **Configure Environment Variables**:
   Create a script or set these in your shell to enable email notifications:
   ```bash
   export EMAIL_USER="your-email@gmail.com"
   export EMAIL_PASS="your-app-password"
   export RECIPIENT_EMAIL="target-email@example.com"
   export SMTP_SERVER="smtp.gmail.com"
   export SMTP_PORT="587"
   ```

3. **Scheduling with Cron**:
   To run the script every day at 11 AM, add the following to your `crontab -e`:
   ```cron
   0 11 * * * /usr/bin/python3 /path/to/job_finder.py >> /path/to/job_finder.log 2>&1
   ```
   *Note: Ensure environment variables are available to the cron job (e.g., by sourcing a file).*

## Project Structure

- `job_finder.py`: Main execution script.
- `scrapers.py`: Modular scraping logic for different career portals.
- `processor.py`: Filtering and deduplication logic.
- `notifier.py`: Email notification module.
- `config.py`: Search configuration (cities, keywords, URLs).
