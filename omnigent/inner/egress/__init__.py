"""L7 egress proxy — fine-grained HTTP(S) filtering with TLS interception.

Public API::

    from omnigent.inner.egress import (
        EgressProxy,
        EgressRule,
        ensure_ca,
        ensure_ca_bundle,
        parse_rule,
        parse_rules,
        check_request,
        start_relay,
    )
"""

from omnigent.inner.egress.ca import ensure_ca, ensure_ca_bundle

# ``controller`` imports the concrete classes/functions it needs
# directly from the leaf submodules (``ca``, ``proxy``, ``rules``),
# never from this package, so re-exporting it here doesn't create a
# circular import even though this file is what makes that name
# importable as ``omnigent.inner.egress.<name>``.
from omnigent.inner.egress.controller import (
    EgressProxyHandle,
    apply_egress_env,
    start_egress_proxy,
)
from omnigent.inner.egress.proxy import EgressProxy
from omnigent.inner.egress.relay import start_relay
from omnigent.inner.egress.rules import (
    EgressRule,
    check_request,
    parse_rule,
    parse_rules,
)

__all__ = [
    "EgressProxy",
    "EgressProxyHandle",
    "EgressRule",
    "apply_egress_env",
    "check_request",
    "ensure_ca",
    "ensure_ca_bundle",
    "parse_rule",
    "parse_rules",
    "start_egress_proxy",
    "start_relay",
]
