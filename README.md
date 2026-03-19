# 📧 Gmail Sender

A lightweight Python script to send personalized HTML emails via Gmail SMTP using a JSON config file. No third-party libraries required — uses Python's built-in `smtplib` and `email` modules.

---

## Features

- Send emails to multiple recipients defined in a JSON config file
- Supports both **HTML** and **plain text** fallback in the same email
- Personalize emails with `{name}` placeholders per recipient
- CC support
- **Dry-run mode** to preview emails without sending
- Clear logging with timestamps
- Validates config before sending

---

## Prerequisites

- Python 3.7+
- A Gmail account with **2-Step Verification** enabled
- A Gmail **App Password** (see setup below)

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/ajaykm26/gmail-sender.git
cd gmail-sender
```

### 2. Generate a Gmail App Password

Gmail no longer allows plain password authentication for scripts. You need an **App Password**:

1. Go to your Google Account → [Security](https://myaccount.google.com/security)
2. Enable **2-Step Verification** if not already enabled
3. Go to [App Passwords](https://myaccount.google.com/apppasswords)
4. Select **Mail** and generate a password
5. Copy the 16-character password — you'll use it in the next step

### 3. Configure your settings

Copy the example config and fill in your details:

```bash
cp email_config.example.json email_config.json
```

Then edit `email_config.json`:

```json
{
  "sender": {
    "email": "your_email@gmail.com",
    "app_password": "xxxx xxxx xxxx xxxx"
  },
  "recipients": [
    { "name": "Alice Smith", "email": "alice@example.com" },
    { "name": "Bob Jones",   "email": "bob@example.com" }
  ],
  "cc": [],
  "email": {
    "subject": "Hello from Python!",
    "body_text": "Hi {name},\n\nThis is a plain text fallback.\n\nBest regards,\nYour Name",
    "body_html": "<html><body><p>Hi <strong>{name}</strong>,</p><p>This is an <em>HTML email</em> sent from Python.</p></body></html>"
  }
}
```

> ⚠️ `email_config.json` is listed in `.gitignore` — your credentials will **never** be committed.

---

## Usage

### Send emails

```bash
python gmail_sender.py
```

### Preview without sending (dry run)

```bash
python gmail_sender.py --dry-run
```

### Use a custom config file

```bash
python gmail_sender.py --config path/to/my_config.json
```

---

## Config File Reference

| Field | Description |
|---|---|
| `sender.email` | Your Gmail address |
| `sender.app_password` | Your 16-character Gmail App Password |
| `recipients` | List of `{ "name": "...", "email": "..." }` objects |
| `cc` | Optional list of CC recipients (same format) |
| `email.subject` | Email subject. Supports `{name}` placeholder |
| `email.body_text` | Plain text body. Supports `{name}` placeholder |
| `email.body_html` | HTML body. Supports `{name}` placeholder |

---

## Project Structure

```
gmail-sender/
├── gmail_sender.py             # Main script
├── email_config.example.json   # Template config (safe to commit)
├── email_config.json           # Your real config (gitignored)
└── README.md
```

---

## Security Notes

- Never commit `email_config.json` — it contains your credentials
- Use App Passwords instead of your main Gmail password
- Revoke the App Password anytime from your [Google Account](https://myaccount.google.com/apppasswords) if needed

---

## License

MIT License — free to use and modify.
