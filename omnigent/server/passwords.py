"""Password hashing for the ``accounts`` auth provider.

Thin wrapper around ``argon2-cffi`` (OWASP-recommended modern KDF).
We do NOT implement our own crypto — this module just centralizes
the hasher configuration so the password lifecycle (hash, verify,
needs-rehash on parameter upgrade) is consistent across routes.

argon2id is the variant used; ``PasswordHasher()`` defaults are
sane for an interactive login flow (≈100 ms verify on a modern
core), which is the trade-off OWASP recommends.

Verify is constant-time by construction: argon2's verifier
internally does the comparison in a way that doesn't short-circuit
on the first mismatching byte. We additionally raise the same
exception class regardless of the failure mode so callers can't
distinguish "unknown user" from "wrong password" by timing —
matching the standard advice (e.g. NIST SP 800-63B §5.2.2).
"""

from __future__ import annotations

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

# Module-level singleton — argon2 PasswordHasher is thread-safe and
# stateless aside from its parameter set.
_HASHER = PasswordHasher()


class InvalidPasswordError(Exception):
    """Raised by :func:`verify_password` when the password is wrong.

    Distinct from any "user not found" error so the route handler
    can map both to the same 401 response without branching on the
    exception type.
    """


def hash_password(plaintext: str) -> str:
    """Hash a plaintext password.

    :param plaintext: The password as typed by the user. UTF-8
        encoded internally by argon2-cffi.
    :returns: The encoded argon2id hash string (includes the
        algorithm parameters, salt, and digest — self-describing,
        so future parameter upgrades don't need a schema change).
    """
    return _HASHER.hash(plaintext)


def verify_password(plaintext: str, password_hash: str) -> None:
    """Verify a plaintext password against a stored hash.

    :param plaintext: The password the user just typed.
    :param password_hash: The previously stored argon2id hash.
    :raises InvalidPasswordError: The password does not match.
        Raised uniformly for both "wrong password" and "malformed
        hash" so the caller can't leak which case applies.
    """
    try:
        _HASHER.verify(password_hash, plaintext)
    except VerifyMismatchError as exc:
        raise InvalidPasswordError() from exc
    except Exception as exc:
        # Any other argon2 error (malformed encoded hash, unknown
        # variant, etc.) — collapse to the same exception so a
        # corrupted DB row doesn't reveal itself via response shape.
        raise InvalidPasswordError() from exc


def needs_rehash(password_hash: str) -> bool:
    """Whether the hash should be rewritten with the current params.

    Lets routes opportunistically upgrade a user's hash on
    successful login if we later raise the argon2 cost parameters.
    Cheap to call on every login; argon2-cffi parses and compares
    against ``_HASHER.parameters``.
    """
    return _HASHER.check_needs_rehash(password_hash)
