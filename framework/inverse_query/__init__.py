"""Inverse Query Generation: a teacher model teaches a student via examples and probes."""

from framework.inverse_query.session import InverseQuerySession, create_inverse_query_session

__all__ = ["InverseQuerySession", "create_inverse_query_session"]
