import json
import os
import sys
from datetime import datetime, timezone

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "escalations.jsonl")


def log_escalation(reason: str, top_similarity: float, language: str,
                   apartment: str, subject: str, guest_message: str,
                   ai_replied: str) -> None:
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "reason": reason,
            "top_similarity": top_similarity,
            "language": language,
            "apartment": apartment,
            "subject": subject,
            "guest_message": guest_message,
            "ai_replied": ai_replied,
        }
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"escalation_logger error: {e}", file=sys.stderr)
