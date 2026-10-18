from typing import TYPE_CHECKING, Sequence

from localization import BaseLocalStr, resolve_text, t

if TYPE_CHECKING:
    from actions.base import Action


class Option:
    """One selectable option in an input request."""

    def __init__(
        self,
        name: BaseLocalStr | str,
        actions: list["Action"],
        enabled: bool = True,
        commands: list[str] | None = None,
        detail: BaseLocalStr | str | None = None,
        disabled_reason: BaseLocalStr | str | None = None,
    ):
        self.name = name
        self.actions = actions
        self.enabled = enabled
        self.commands = [command.strip().lower() for command in (commands or []) if command.strip()]
        self.detail = detail
        self.disabled_reason = disabled_reason


def match_option_command(raw_input: str, options: list[Option]) -> list[int] | None:
    """Match a textual command alias to a single option selection."""
    normalized = (raw_input or "").strip().lower()
    if not normalized:
        return None

    matches = [
        idx
        for idx, option in enumerate(options)
        if getattr(option, "enabled", True) and normalized in getattr(option, "commands", [])
    ]
    if len(matches) != 1:
        return None
    return [matches[0]]


def option_label(option) -> str:
    name = resolve_text(getattr(option, "name", option))
    if not getattr(option, "enabled", True):
        label = t("ui.selection_locked", name=name)
        reason = getattr(option, "disabled_reason", None)
        return f"{label} — {resolve_text(reason)}" if reason else label
    return name


def selection_error(
    options: Sequence, indices: Sequence[int], max_select: int = -1, must_select: bool = False,
) -> str | None:
    """Validate a whole selection without silently dropping invalid entries."""
    if any(not isinstance(index, int) or isinstance(index, bool) or index < 0 or index >= len(options) for index in indices):
        return t("ui.invalid_option", default="Invalid option.")
    if len(indices) != len(set(indices)):
        return t("ui.selection_duplicate")
    for index in indices:
        option = options[index]
        if not getattr(option, "enabled", True):
            reason = getattr(option, "disabled_reason", None)
            return resolve_text(reason) if reason else t("ui.selection_disabled")
    limit = sum(bool(getattr(option, "enabled", True)) for option in options) if max_select == -1 else max_select
    if len(indices) > limit:
        return t("ui.too_many_options", max_select=limit)
    if must_select and len(indices) != limit:
        return t("ui.selection_count_mismatch", count=limit)
    return None
