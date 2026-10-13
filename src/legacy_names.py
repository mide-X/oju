# src/legacy_names.py
"""Backward compatibility with the project's former name, Odysseus.

Installs that predate the rename still have ODYSSEUS_* variables in their
.env / shell, session cookies named `odysseus_session`, emails stamped with
X-Odysseus-* headers, and Chroma collections named `odysseus_*`. The new
names win; the old ones are only read when the new one is absent.

Kept dependency-free so entry points can import it before anything else.
"""

import os

ENV_PREFIX = "OJU_"
LEGACY_ENV_PREFIX = "ODYSSEUS_"

LEGACY_SESSION_COOKIE = "odysseus_session"

# Value of the *-Origin header on mail Oju sends; the legacy value is still
# recognised so old reminders aren't re-triaged as new mail.
LEGACY_MAIL_ORIGIN = "odysseus-ui"

# Subject prefix used by reminder emails before the rename.
LEGACY_REMINDER_SUBJECT = "Reminder (Odysseus):"


def apply_legacy_env(environ=None) -> None:
    """Copy every ODYSSEUS_X into OJU_X unless OJU_X is already set.

    Call once, after .env is loaded and before reading OJU_* settings.
    Child processes inherit the result, so they only need the new names.
    """
    env = os.environ if environ is None else environ
    for key, value in list(env.items()):
        if key.startswith(LEGACY_ENV_PREFIX):
            env.setdefault(ENV_PREFIX + key[len(LEGACY_ENV_PREFIX):], value)


def legacy_header(name: str) -> str:
    """`X-Oju-Kind` -> `X-Odysseus-Kind`."""
    return name.replace("X-Oju-", "X-Odysseus-", 1)


def get_header(headers, name: str, default=None):
    """Read an X-Oju-* header from a Message / request headers mapping,
    falling back to its X-Odysseus-* name."""
    value = headers.get(name)
    if value is None:
        value = headers.get(legacy_header(name))
    return default if value is None else value


def get_or_migrate_collection(client, name: str, legacy_name: str, **kwargs):
    """get_or_create a Chroma collection, first renaming a pre-rename
    `legacy_name` collection to `name` so existing vectors carry over."""
    try:
        existing = {getattr(c, "name", c) for c in client.list_collections()}
        if legacy_name in existing and name not in existing:
            client.get_collection(legacy_name).modify(name=name)
    except Exception:
        pass
    return client.get_or_create_collection(name=name, **kwargs)
