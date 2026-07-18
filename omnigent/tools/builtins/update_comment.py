"""Built-in tool: update the status of a review comment."""

from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any

from omnigent.tools.base import Tool, ToolContext

_VALID_STATUSES = {"draft", "addressed"}


class UpdateCommentTool(Tool):
    """
    Update the status of a review comment in the current session.

    Used by the agent to mark a comment as ``"addressed"`` after
    the underlying issue has been fixed, so the UI reflects the
    current state of the review.
    """

    @classmethod
    def name(cls) -> str:
        """
        :returns: ``"update_comment"``.
        """
        return "update_comment"

    @classmethod
    def description(cls) -> str:
        """
        :returns: Human-readable description of the tool.
        """
        return (
            "Update the status of a review comment. "
            "Call this after fixing the issue a comment describes "
            'to mark it as "addressed", so the user can see which '
            "comments have been resolved."
        )

    def get_schema(self) -> dict[str, Any]:
        """
        Return the OpenAI-format tool schema.

        :returns: A tool schema dict.
        """
        return {
            "type": "function",
            "function": {
                "name": "update_comment",
                "description": self.description(),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "comment_id": {
                            "type": "string",
                            "description": (
                                "The ID of the comment to update, "
                                "as returned by list_comments, "
                                'e.g. "a1b2c3d4-e5f6-...".'
                            ),
                        },
                        "status": {
                            "type": "string",
                            "enum": ["draft", "addressed"],
                            "description": (
                                'The new status. Use "addressed" after '
                                "fixing the issue the comment describes."
                            ),
                        },
                    },
                    "required": ["comment_id", "status"],
                },
            },
        }

    def invoke(self, arguments: str, ctx: ToolContext) -> str:
        """
        Update a comment's status and return the updated comment.

        The comment must belong to the current session
        (``ctx.conversation_id``); an error is returned if the
        comment is not found or belongs to a different session.

        :param arguments: JSON with ``"comment_id"`` and
            ``"status"`` keys, e.g.
            ``'{"comment_id": "a1b2c3d4-...", "status": "addressed"}'``.
        :param ctx: Server-side execution context; uses
            ``ctx.conversation_id`` to verify session ownership.
        :returns: JSON string with the updated comment dict, or
            an ``"error"`` key if the update failed.
        """
        if ctx.conversation_id is None:
            return json.dumps({"error": "no conversation context — cannot scope comment update"})

        from omnigent.runtime import get_comment_store

        store = get_comment_store()
        if store is None:
            return json.dumps({"error": "comment store not configured for this deployment"})

        try:
            args: dict[str, Any] = json.loads(arguments) if arguments.strip() else {}
        except json.JSONDecodeError:
            return json.dumps({"error": "malformed JSON arguments"})
        comment_id: str | None = args.get("comment_id")
        status: str | None = args.get("status")

        if not comment_id:
            return json.dumps({"error": "missing required argument: comment_id"})
        if not status:
            return json.dumps({"error": "missing required argument: status"})
        if status not in _VALID_STATUSES:
            return json.dumps(
                {"error": f"invalid status {status!r}; must be one of {sorted(_VALID_STATUSES)}"}
            )

        updated = store.update_comment(comment_id, ctx.conversation_id, status=status)
        if updated is None:
            return json.dumps({"error": f"comment not found: {comment_id}"})
        return json.dumps({"comment": asdict(updated)})
