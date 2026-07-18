"""Built-in tools for runtime policy management.

``sys_add_policy``
    Create a policy on the current session using a builtin handler.

``sys_policy_registry``
    List all available policy templates from the built-in registry
    so the agent can pick the best fit before creating one.
"""

from __future__ import annotations

from typing import Any

from omnigent.tools.base import Tool


class SysAddPolicyTool(Tool):
    """
    Create a policy on the current session.

    The agent picks a handler from ``sys_policy_registry`` and
    passes its ``factory_params``. The runner forwards the request
    to the Omnigent server's ``POST /v1/sessions/{session_id}/policies``
    endpoint.
    """

    @classmethod
    def name(cls) -> str:
        """
        :returns: ``"sys_add_policy"``.
        """
        return "sys_add_policy"

    @classmethod
    def description(cls) -> str:
        """
        :returns: Human-readable description of the tool.
        """
        return (
            "Add a runtime policy to the current session. "
            "First call sys_policy_registry to see available policies "
            "and their parameter schemas, then call this tool with "
            "the chosen handler and factory_params."
        )

    def get_schema(self) -> dict[str, Any]:
        """
        Return the OpenAI-format tool schema.

        :returns: A tool schema dict.
        """
        return {
            "type": "function",
            "function": {
                "name": self.name(),
                "description": self.description(),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": (
                                "Unique policy name within the session, "
                                'e.g. "block_shell" or "rate_limit_50".'
                            ),
                        },
                        "handler": {
                            "type": "string",
                            "description": (
                                "Dotted import path of a policy from "
                                "sys_policy_registry. Example: "
                                '"omnigent.policies.builtins.cel.cel_policy"'
                            ),
                        },
                        "factory_params": {
                            "type": "object",
                            "description": (
                                "Parameters for the policy factory. "
                                "Schema available from sys_policy_registry. "
                                "Example for CEL policy: "
                                '{"expression": "event.type == \\"tool_call\\"", '
                                '"reason": "Blocked."}'
                            ),
                        },
                    },
                    "required": ["name", "handler"],
                    "additionalProperties": False,
                },
            },
        }


class SysPolicyRegistryTool(Tool):
    """
    List available policy templates from the built-in registry.

    Returns every registered policy with its handler path,
    description, kind (callable vs factory), and parameter
    schema. The agent uses this to pick the right policy
    before calling ``sys_add_policy``.
    """

    @classmethod
    def name(cls) -> str:
        """
        :returns: ``"sys_policy_registry"``.
        """
        return "sys_policy_registry"

    @classmethod
    def description(cls) -> str:
        """
        :returns: Human-readable description of the tool.
        """
        return (
            "List all available built-in policy templates. Returns each "
            "policy's handler path, description, kind (callable or factory), "
            "and factory_params schema. Use this to find the right policy "
            "before adding it with sys_add_policy."
        )

    def get_schema(self) -> dict[str, Any]:
        """
        Return the OpenAI-format tool schema.

        :returns: A tool schema dict with no parameters (list-all).
        """
        return {
            "type": "function",
            "function": {
                "name": self.name(),
                "description": self.description(),
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                    "additionalProperties": False,
                },
            },
        }
