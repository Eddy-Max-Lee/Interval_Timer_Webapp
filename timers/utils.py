from __future__ import annotations

from typing import Optional

from .models import UserProfile


def get_request_profile(request) -> Optional[UserProfile]:
    """Return the cached ``UserProfile`` from the current session if available."""

    if hasattr(request, '_cached_profile'):
        return request._cached_profile  # type: ignore[attr-defined]

    profile = None
    profile_id = request.session.get('profile_id')
    if profile_id:
        profile = UserProfile.objects.filter(pk=profile_id).first()

    request._cached_profile = profile  # type: ignore[attr-defined]
    return profile
