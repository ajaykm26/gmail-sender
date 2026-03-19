"""
Gmail Sender Script
--------------------
Sends emails to recipients defined in email_config.json using Gmail SMTP
with an App Password. Supports HTML + plain text fallback.

Setup:
  1. Enable 2-Step Verification on your Google account.
  2. Go to: https://myaccount.google.com/apppasswords
  3. Generate an App Password for "Mail" and paste it into email_config.json.
  4. Run: python gmail_sender.py
     Or with a custom config: python gmail_sender.py --config my_config.json
"""

import json
import smtplib
import argparse
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Config loader
# ---------------------------------------------------------------------------
def load_config(config_path: str) -> dict:
    """Load and validate the JSON config file."""
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(path, "r", encoding="utf-8") as f:
        config = json.load(f)

    # Basic validation
    required_keys = ["sender", "recipients", "email"]
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required config key: '{key}'")

    if not config["sender"].get("email"):
        raise ValueError("sender.email is required in config.")
    if not config["sender"].get("app_password"):
        raise ValueError("sender.app_password is required in config.")
    if not config["recipients"]:
        raise ValueError("recipients list cannot be empty.")

    return config


# ---------------------------------------------------------------------------
# Email builder
# ---------------------------------------------------------------------------
def build_message(
    sender_email: str,
    recipient: dict,
    cc_list: list,
    email_cfg: dict,
) -> MIMEMultipart:
    """
    Build a MIME email with both HTML and plain-text parts.
    {name} in subject/body is replaced with the recipient's name.
    """
    name = recipient.get("name", recipient["email"])
    to_email = recipient["email"]

    subject = email_cfg.get("subject", "(No Subject)").replace("{name}", name)
    body_text = email_cfg.get("body_text", "").replace("{name}", name)
    body_html = email_cfg.get("body_html", "").replace("{name}", name)

    msg = MIMEMultipart("alternative")
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = subject

    if cc_list:
        cc_addresses = [r["email"] for r in cc_list if "email" in r]
        if cc_addresses:
            msg["Cc"] = ", ".join(cc_addresses)

    # Attach plain text first, HTML second (clients prefer last part)
    if body_text:
        msg.attach(MIMEText(body_text, "plain", "utf-8"))
    if body_html:
        msg.attach(MIMEText(body_html, "html", "utf-8"))

    return msg


# ---------------------------------------------------------------------------
# Sender
# ---------------------------------------------------------------------------
def send_emails(config: dict, dry_run: bool = False) -> None:
    """
    Connect to Gmail SMTP and send emails to all recipients.
    If dry_run=True, messages are printed but not sent.
    """
    sender_cfg = config["sender"]
    sender_email = sender_cfg["email"]
    app_password = sender_cfg["app_password"]
    recipients = config["recipients"]
    cc_list = config.get("cc", [])
    email_cfg = config["email"]

    logger.info("Preparing to send %d email(s) from %s", len(recipients), sender_email)

    if dry_run:
        logger.info("--- DRY RUN MODE: emails will NOT be sent ---")

    success_count = 0
    failure_count = 0

    # Open one SMTP connection for all recipients
    try:
        if not dry_run:
            smtp = smtplib.SMTP("smtp.gmail.com", 587, timeout=30)
            smtp.ehlo()
            smtp.starttls()
            smtp.login(sender_email, app_password)
            logger.info("Authenticated with Gmail SMTP successfully.")

        for recipient in recipients:
            to_email = recipient.get("email")
            if not to_email:
                logger.warning("Skipping recipient with no email: %s", recipient)
                continue

            try:
                msg = build_message(sender_email, recipient, cc_list, email_cfg)

                all_recipients = [to_email] + [
                    r["email"] for r in cc_list if "email" in r
                ]

                if dry_run:
                    logger.info(
                        "[DRY RUN] Would send to: %s | Subject: %s",
                        to_email,
                        msg["Subject"],
                    )
                else:
                    smtp.sendmail(sender_email, all_recipients, msg.as_string())
                    logger.info("Email sent to: %s (%s)", to_email, recipient.get("name", ""))

                success_count += 1

            except Exception as e:
                logger.error("Failed to send email to %s: %s", to_email, e)
                failure_count += 1

        if not dry_run:
            smtp.quit()

    except smtplib.SMTPAuthenticationError:
        logger.error(
            "Authentication failed. Check your Gmail address and App Password.\n"
            "  - Ensure 2-Step Verification is enabled: https://myaccount.google.com/security\n"
            "  - Generate an App Password at: https://myaccount.google.com/apppasswords"
        )
        return
    except smtplib.SMTPException as e:
        logger.error("SMTP error: %s", e)
        return
    except Exception as e:
        logger.error("Unexpected error: %s", e)
        return

    logger.info(
        "Done. %d sent, %d failed.", success_count, failure_count
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Send emails via Gmail SMTP.")
    parser.add_argument(
        "--config",
        default="email_config.json",
        help="Path to the JSON config file (default: email_config.json)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview emails without actually sending them.",
    )
    args = parser.parse_args()

    try:
        config = load_config(args.config)
    except (FileNotFoundError, ValueError) as e:
        logger.error("Config error: %s", e)
        return

    send_emails(config, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
