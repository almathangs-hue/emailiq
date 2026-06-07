import base64
import email as email_lib
from datetime import datetime, date
from typing import Generator

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from sqlalchemy.orm import Session

from app.core.auth import decrypt_token, encrypt_token
from app.models import ConnectedAccount

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def _build_client(account: ConnectedAccount, db: Session):
    """Build an authenticated Gmail API client, refreshing the token if expired."""
    creds = Credentials(
        token=decrypt_token(account.access_token),
        refresh_token=decrypt_token(account.refresh_token),
        token_uri="https://oauth2.googleapis.com/token",
        scopes=SCOPES,
    )

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        account.access_token = encrypt_token(creds.token)
        db.commit()

    return build("gmail", "v1", credentials=creds, cache_discovery=False)


def _parse_headers(headers: list[dict]) -> dict:
    return {h["name"].lower(): h["value"] for h in headers}


def _decode_body(payload: dict) -> str:
    """Extract plain text body from message payload."""
    if payload.get("body", {}).get("data"):
        return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="ignore")

    for part in payload.get("parts", []):
        if part.get("mimeType") == "text/plain" and part.get("body", {}).get("data"):
            return base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="ignore")

    return ""


def _parse_sender(from_header: str) -> tuple[str, str]:
    """Return (sender_name, sender_email) from a From header."""
    if "<" in from_header:
        name = from_header.split("<")[0].strip().strip('"')
        email_addr = from_header.split("<")[1].rstrip(">").strip()
    else:
        name = ""
        email_addr = from_header.strip()
    return name, email_addr


def fetch_messages(
    account: ConnectedAccount,
    db: Session,
    start_date: date,
    end_date: date,
) -> Generator[dict, None, None]:
    """
    Yield raw message dicts for emails in [start_date, end_date].
    Each dict has: gmail_message_id, gmail_thread_id, sender_name,
    sender_email, subject, body_snippet, received_at.
    """
    service = _build_client(account, db)

    # Gmail date query uses YYYY/MM/DD format
    query = f"after:{start_date.strftime('%Y/%m/%d')} before:{end_date.strftime('%Y/%m/%d')}"
    page_token = None

    while True:
        kwargs = {"userId": "me", "q": query, "maxResults": 100}
        if page_token:
            kwargs["pageToken"] = page_token

        result = service.users().messages().list(**kwargs).execute()
        messages = result.get("messages", [])

        for msg_ref in messages:
            msg = service.users().messages().get(
                userId="me",
                id=msg_ref["id"],
                format="full",
                metadataHeaders=["From", "Subject", "Date"],
            ).execute()

            headers = _parse_headers(msg.get("payload", {}).get("headers", []))
            sender_name, sender_email = _parse_sender(headers.get("from", ""))

            # internalDate is milliseconds since epoch
            received_at = datetime.utcfromtimestamp(int(msg["internalDate"]) / 1000)

            body_text = _decode_body(msg.get("payload", {}))
            # Store only first 500 chars of body — enough for detection, not the full email
            body_snippet = body_text[:500] if body_text else msg.get("snippet", "")

            yield {
                "gmail_message_id": msg["id"],
                "gmail_thread_id": msg["threadId"],
                "sender_name": sender_name,
                "sender_email": sender_email,
                "subject": headers.get("subject", ""),
                "body_snippet": body_snippet,
                "received_at": received_at,
            }

        page_token = result.get("nextPageToken")
        if not page_token:
            break
