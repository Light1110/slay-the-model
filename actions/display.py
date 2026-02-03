# -*- coding: utf-8 -*-
"""
Display-related actions
"""
from actions.base import Action
from utils.parser import parse
from utils.registry import register
# 延迟导入以避免循环导入
def get_game_state():
    from engine.game_state import game_state
    return game_state

@register("action")
class DisplayTextAction(Action):
    """Display text to user

    Required:
        text_key (str): key for localized text

    Optional:
        None
    """
    REQUIRED_PARAMS = {}
    OPTIONAL_PARAMS = {
        "text_key": (str, ""),
    }

    def execute(self):
        text_key = self.kwargs.get('text_key', '')
        text = self.translate(text_key, default=text_key)
        print(text)

@register("action")
class SelectAction(Action):
    """向用户展示选项并返回所选的动作列表。

    选项格式：
        - dict: {"name_key": str, "actions": list}

    自动化行为：
        - 仅有一个选项时可自动选择（AI 或配置允许时）
        - 无选项时自动前进（返回空列表）
        - AI 调试模式可自动选择第一项
    """

    REQUIRED_PARAMS = {
        "title_key": str,
        "options": list,
        "format_dict": dict | None,
    }
    OPTIONAL_PARAMS = {}
    def __init__(self, title_key, options, format_dict, **kwargs):
        super().__init__(**kwargs)
        self.title_key = title_key
        self.options = options  # List of dicts with 'name_key' and 'actions'
        self.format_dict = format_dict or {}

    def _normalize_options(self):
        """将选项统一为 (name_key, actions) 元组列表。"""
        normalized = []
        for option in self.options:
            if isinstance(option, dict):
                normalized.append((option.get('name_key', ''), option.get('actions', [])))
            elif isinstance(option, (list, tuple)) and len(option) == 2:
                normalized.append(option)
            else:
                # Invalid format, skip or handle
                normalized.append(('', []))
        return normalized

    def execute(self):
        """执行选择流程，返回需要执行的动作列表。"""

        # 1) 基础选项（不含"返回菜单"）
        base_choices = self._normalize_options()
        if len(base_choices) == 1:
            if get_game_state().config.get("mode") != "human":
                _, action_list = base_choices[0]
                return action_list
            if bool(get_game_state().config.get("auto_select_single_option", False)):
                _, action_list = base_choices[0]
                return action_list
        if len(base_choices) == 0:
            return []

        # 2) 若为人类玩家，追加"返回菜单"选项
        # menu_action 内部可选择 return，将当前 SelectAction 插回队首
        # todo
        from actions.menu import add_menu_choice_if_human
        effective_choices = add_menu_choice_if_human(
            base_choices,
            self,
        )

        # 3) 展示标题与选项（翻译 title_key）
        title = parse()
        if bool(get_game_state().config.get("show_menu", True)):
            print(f"\n=== {title} ===")
            for i, (title_key, _) in enumerate(effective_choices):
                label = self.translate(title_key, default=title_key)
                print(f"{i+1}. {label}")

        # 4) AI 调试模式可自动选择第一项
        if effective_choices and bool(get_game_state().config.get("ai_debug", False)):
            _, action_list = effective_choices[0]
            return action_list

        # 5) 交互式选择
        while True:
            try:
                prompt = self.translate(
                    "ui.select_prompt",
                    default=f"Choose (1-{len(effective_choices)}): ",
                    count=len(effective_choices),
                )
                choice = int(input(prompt)) - 1
                if 0 <= choice < len(effective_choices):
                    _, action_list = effective_choices[choice]
                    return action_list
                print(self.translate("ui.invalid_choice", default="Invalid choice!"))
            except (ValueError, EOFError):
                print(self.translate("ui.invalid_number", default="Please enter a valid number"))
