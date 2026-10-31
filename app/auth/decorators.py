# app\auth\decorators.py


from functools import wraps
from ipaddress import ip_address

from flask import abort, current_app, request
from flask_login import current_user, login_required


def role_required(*allowed_roles):
    """Restrict a route to authenticated users with an allowed role."""

    def decorator(view_function):
        @wraps(view_function)
        @login_required
        def wrapped_view(*args, **kwargs):
            if current_user.role not in allowed_roles:
                abort(403)

            return view_function(*args, **kwargs)

        return wrapped_view

    return decorator


def _is_development_installation():
    """Return whether this installation explicitly permits developer tools."""
    return (
        current_app.config.get("EDUANALYTICS_ENV") == "development"
        and current_app.config.get("EDUANALYTICS_DEV_TOOLS_ENABLED") is True
    )


def _is_local_request():
    """Accept only loopback requests; never trust forwarded headers."""
    remote_addr = request.remote_addr
    if not remote_addr:
        return False

    try:
        return ip_address(remote_addr).is_loopback
    except ValueError:
        return False


def developer_access_required(view_function):
    """Require an active Developer on an explicitly enabled local install."""

    @wraps(view_function)
    @login_required
    def wrapped_view(*args, **kwargs):
        if not _is_development_installation():
            _audit_developer_access("disabled_or_non_development", "failure")
            abort(403)

        if (
            current_app.config.get("EDUANALYTICS_DEV_TOOLS_LOCAL_ONLY", True)
            and not _is_local_request()
        ):
            _audit_developer_access("non_loopback_request", "failure")
            abort(403)

        if current_user.role != "developer":
            _audit_developer_access("non_developer_role", "failure")
            abort(403)

        response = view_function(*args, **kwargs)
        _audit_developer_access(view_function.__name__, "success")
        return response

    return wrapped_view


def _audit_developer_access(action, outcome):
    """Best-effort audit for protected Developer route access."""
    try:
        from app.developer.audit import record_audit_event

        actor = None
        if getattr(current_user, "is_authenticated", False):
            actor = current_user.get_id()
        record_audit_event(
            actor_userid=actor,
            action="developer_access",
            resource=action,
            outcome=outcome,
            context="Protected Developer route access.",
        )
    except Exception:
        current_app.logger.exception("Could not write Developer audit event.")


def developer_tools_enabled():
    """Return whether Developer tools are explicitly enabled for development."""
    return _is_development_installation()
