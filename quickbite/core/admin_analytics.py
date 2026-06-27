"""Operational metrics — delegates to analytics.queries."""

from analytics.queries import get_admin_command_center_context, get_full_bi_context


def get_admin_dashboard_context():
    """KPIs for admin index (command center)."""
    return get_admin_command_center_context()
