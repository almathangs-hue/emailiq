import re
from dataclasses import dataclass

THRESHOLD = 50

KNOWN_ATS_DOMAINS = {
    "greenhouse.io", "lever.co", "workday.com", "ashbyhq.com",
    "icims.com", "smartrecruiters.com", "taleo.net", "jobvite.com",
    "breezy.hr", "bamboohr.com", "recruitee.com", "workable.com",
    "myworkdayjobs.com", "successfactors.com",
}

HIRING_PREFIXES = {"careers", "recruiting", "talent", "jobs", "hire", "noreply+jobs"}

JOB_KEYWORDS = [
    r"application\s+received",
    r"thank\s+you\s+for\s+applying",
    r"your\s+application",
    r"we\s+received\s+your",
    r"application\s+status",
    r"moving\s+forward",
    r"next\s+steps",
    r"interview",
    r"phone\s+screen",
    r"technical\s+(assessment|interview|screen)",
    r"take.?home",
    r"offer\s+letter",
    r"job\s+offer",
    r"unfortunately",
    r"we\s+will\s+not\s+be\s+moving",
    r"other\s+candidates",
    r"position\s+has\s+been\s+filled",
]

_KEYWORD_PATTERN = re.compile("|".join(JOB_KEYWORDS), re.IGNORECASE)

# Patterns to extract company name and role from subject
_ROLE_PATTERNS = [
    re.compile(r"(?:application|applied)\s+(?:for|to)\s+(?:the\s+)?(.+?)(?:\s+at\s+|\s+@\s+|$)", re.IGNORECASE),
    re.compile(r"your\s+(.+?)\s+application", re.IGNORECASE),
]
_COMPANY_PATTERNS = [
    re.compile(r"(?:at|@|with)\s+([A-Z][A-Za-z0-9\s&.,'-]+?)(?:\s*[|\-,]|$)"),
]


@dataclass
class DetectionResult:
    score: int
    is_job: bool
    company_name: str
    role_title: str
    inferred_status: str


def score_email(
    sender_email: str,
    subject: str,
    body_snippet: str,
    existing_thread_classified: bool = False,
) -> DetectionResult:
    score = 0
    sender_lower = sender_email.lower()

    # Extract domain and local part
    parts = sender_lower.split("@")
    local = parts[0] if len(parts) == 2 else ""
    domain = parts[1] if len(parts) == 2 else ""

    # Strip subdomains to match root domain (e.g. mail.greenhouse.io → greenhouse.io)
    domain_parts = domain.split(".")
    root_domain = ".".join(domain_parts[-2:]) if len(domain_parts) >= 2 else domain

    if root_domain in KNOWN_ATS_DOMAINS:
        score += 40

    if any(local.startswith(prefix) for prefix in HIRING_PREFIXES):
        score += 20

    if local == "no-reply" or local == "noreply":
        score += 5

    if _KEYWORD_PATTERN.search(subject):
        score += 30

    if _KEYWORD_PATTERN.search(body_snippet or ""):
        score += 15

    if existing_thread_classified:
        score += 25

    company = _extract_company(subject, sender_email)
    role = _extract_role(subject)
    status = _infer_status(subject, body_snippet or "")

    return DetectionResult(
        score=score,
        is_job=score >= THRESHOLD,
        company_name=company,
        role_title=role,
        inferred_status=status,
    )


def _extract_company(subject: str, sender_email: str) -> str:
    for pattern in _COMPANY_PATTERNS:
        match = pattern.search(subject)
        if match:
            return match.group(1).strip()

    # Fall back to sender domain as company hint
    parts = sender_email.split("@")
    if len(parts) == 2:
        domain = parts[1].split(".")[0]
        return domain.capitalize()

    return "Unknown"


def _extract_role(subject: str) -> str:
    for pattern in _ROLE_PATTERNS:
        match = pattern.search(subject)
        if match:
            return match.group(1).strip()
    return ""


def _infer_status(subject: str, body: str) -> str:
    text = f"{subject} {body}".lower()

    if any(kw in text for kw in ["offer letter", "job offer", "offer of employment"]):
        return "offer"
    if any(kw in text for kw in ["unfortunately", "will not be moving", "other candidates", "position has been filled"]):
        return "rejected"
    if any(kw in text for kw in ["interview", "phone screen", "technical assessment", "take-home"]):
        return "interview"
    if any(kw in text for kw in ["moving forward", "next steps", "recruiter"]):
        return "screening"
    return "applied"
