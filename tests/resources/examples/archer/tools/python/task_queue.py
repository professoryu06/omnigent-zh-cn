"""Stateful task-queue tools for the archer e2e fixture."""

from __future__ import annotations

from typing import Literal

from omnigent_client.tools import ToolState, tool


def _empty_state() -> dict[str, object]:
    """
    Return a fresh task-queue state document.

    :returns: State dict with a next id counter and task list.
    """
    return {"next_id": 1, "tasks": []}


@tool
def add_task(description: str, tool_state: ToolState) -> dict[str, object]:
    """
    Add a pending task to the conversation-local queue.

    :param description: Human-readable task description.
    :param tool_state: Injected per-agent/per-conversation state store.
    :returns: The created task record.
    """
    with tool_state.transaction("tasks.json", default_factory=_empty_state) as state:
        tasks = list(state.get("tasks", []))
        task_id = int(state.get("next_id", 1))
        task: dict[str, object] = {
            "id": task_id,
            "description": description,
            "status": "pending",
        }
        tasks.append(task)
        state["tasks"] = tasks
        state["next_id"] = task_id + 1
        return task


@tool
def list_tasks(
    tool_state: ToolState,
    status: Literal["pending", "done"] | None = None,
) -> list[dict[str, object]]:
    """
    List tasks in the conversation-local queue.

    :param tool_state: Injected per-agent/per-conversation state store.
    :param status: Optional status filter.
    :returns: All matching task records in insertion order.
    """
    state = tool_state.read("tasks.json", default_factory=_empty_state)
    tasks = list(state.get("tasks", []))
    if status is None:
        return tasks
    return [task for task in tasks if task.get("status") == status]


@tool
def update_task_status(
    task_id: int,
    new_status: Literal["pending", "done"],
    tool_state: ToolState,
) -> dict[str, object]:
    """
    Update the status of an existing task.

    :param task_id: Identifier returned by :func:`add_task`.
    :param new_status: Replacement status.
    :param tool_state: Injected per-agent/per-conversation state store.
    :returns: The updated task record.
    :raises ValueError: If no task with ``task_id`` exists.
    """
    with tool_state.transaction("tasks.json", default_factory=_empty_state) as state:
        tasks = list(state.get("tasks", []))
        for task in tasks:
            if int(task.get("id", 0)) == task_id:
                task["status"] = new_status
                state["tasks"] = tasks
                return task
    raise ValueError(f"task_id not found: {task_id}")
