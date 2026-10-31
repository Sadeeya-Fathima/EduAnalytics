"""Safe audit-event recording for Developer operations."""

from app.extensions import db
from app.models import AuditEvent


SENSITIVE_TERMS = ("password", "hash", "secret", "token", "cookie")


def _safe_context(context):
    if not context:
        return None
    normalized = str(context).strip()
    if any(term in normalized.lower() for term in SENSITIVE_TERMS):
        return "Sensitive context redacted."
    return normalized[:500]


def record_audit_event(
    *, actor_userid, action, resource, outcome, record_reference=None, context=None
):
    """Persist one minimal audit event without recording sensitive values."""
    event = AuditEvent(
        actor_userid=str(actor_userid) if actor_userid is not None else None,
        action=str(action)[:100],
        resource=str(resource)[:100],
        record_reference=(str(record_reference)[:255] if record_reference is not None else None),
        outcome=str(outcome)[:20],
        context=_safe_context(context),
    )
    db.session.add(event)
    db.session.commit()
    return event
