import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging

logger = logging.getLogger(__name__)

def send_email(jobs):
    smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    sender_email = os.environ.get("EMAIL_USER")
    sender_pass = os.environ.get("EMAIL_PASS")
    recipient_email = os.environ.get("RECIPIENT_EMAIL")

    if not all([sender_email, sender_pass, recipient_email]):
        logger.warning("Email credentials not fully set. Printing results to console instead.")
        print_results(jobs)
        return

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = f"Daily EMT/ER Tech Job Report - {len(jobs)} jobs found"

    html = f"<h2>Daily Job Report</h2><p>Found {len(jobs)} roles matching your criteria:</p>"
    html += "<table border='1'><tr><th>Company</th><th>Title</th><th>Location</th><th>Link</th></tr>"

    for job in jobs:
        html += f"<tr><td>{job['company']}</td><td>{job['title']}</td><td>{job['location']}</td><td><a href='{job['link']}'>Link</a></td></tr>"

    html += "</table>"

    msg.attach(MIMEText(html, 'html'))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_pass)
            server.send_message(msg)
        logger.info("Email sent successfully.")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")

def print_results(jobs):
    print(f"\n--- Daily Job Report: {len(jobs)} jobs found ---")
    for job in jobs:
        print(f"[{job['company']}] {job['title']} - {job['location']}")
        print(f"  Link: {job['link']}\n")
