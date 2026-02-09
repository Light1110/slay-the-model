# -*- coding: utf-8 -*-
"""
Display-related actions
"""
from typing import List, Optional
import pickle
import os
from actions.base import Action
from utils.result_types import BaseResult, NoneResult, MultipleActionsResult, SingleActionResult, GameStateResult
from localization import BaseLocalStr, LocalStr, t
from utils.option import Option
from utils.registry import register

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
    def __init__(self, text_key: str = "", **fmt):
        self.text_key = text_key
        self.fmt = fmt

    def execute(self) -> 'BaseResult':
        # Extract default from fmt if present, otherwise use text_key
        fallback = self.fmt.get('default', self.text_key)
        text = t(self.text_key, default=fallback, **{k: v for k, v in self.fmt.items() if k != 'default'})
        print(text)
        return NoneResult()

@register("action")
class SelectAction(Action):
    """向用户展示选项并返回所选的动作列表。
    
    参数：
        title (BaseLocalStr): 选择标题的本地化键
        options (List[Option]): 可供选择的选项列表

    自动化行为：
        - 仅有一个选项时可自动选择（AI 或配置允许时）
        - 无选项时自动前进（返回空列表）
        - AI 调试模式可自动选择第一项
    """

    def __init__(self, title : BaseLocalStr, options : List[Option]):
        self.title = title
        self.options = options

    def execute(self) -> 'BaseResult':
        """执行选择流程，返回需要执行的动作列表。"""

        # 1) 基础选项（不含"返回菜单"）
        if len(self.options) == 1:
            if get_game_state().config.get("mode") != "human":
                action_list = self.options[0].actions
                return MultipleActionsResult(action_list)
            if bool(get_game_state().config.get("auto_select_single_option", False)):
                action_list = self.options[0].actions
                return MultipleActionsResult(action_list)
        if len(self.options) == 0:
            return MultipleActionsResult([])

        # 2) 若为人类玩家，追加"打开菜单"选项
        effective_options = self.options.copy()
        if get_game_state().config.get("mode") == "human":
            menu_option = Option(
                name=LocalStr("ui.open_menu"),
                actions=[MenuAction(self)]
            )
            effective_options.append(menu_option)

        # 3) 展示标题与选项（翻译 name）
        if bool(get_game_state().config.get("show_menu", True)):
            print(f"\n=== {self.title} ===")
            for i, option in enumerate(effective_options):
                print(f"{i+1}. {option.name}")

        # 4) AI 调试模式可自动选择第一项
        if effective_options and bool(get_game_state().config.get("debug", False)):
            action_list = effective_options[0].actions
            return MultipleActionsResult(action_list)

        # 5) 交互式选择
        while True:
            try:
                prompt = t(
                    "ui.select_prompt",
                    default=f"Choose (1-{len(effective_options)}): ",
                    count=len(effective_options),
                )
                option = int(input(prompt)) - 1
                if 0 <= option < len(effective_options):
                    action_list = effective_options[option].actions
                    return MultipleActionsResult(action_list)
                print(t("ui.invalid_option", default="Invalid option!"))
            except (ValueError, EOFError):
                print(t("ui.invalid_number", default="Please enter a valid number"))


@register("action")
class MenuAction(Action):
    """游戏菜单系统，提供交互式命令接口。
    
    支持的命令：
        - info player: 显示玩家信息
        - info deck: 显示卡组信息
        - info relics: 显示遗物信息
        - save: 保存当前游戏状态
        - exit: 退出游戏
        - return: 返回游戏
    """

    def __init__(self, parent_select_action: 'SelectAction'):
        self.parent_select_action = parent_select_action

    def execute(self) -> 'BaseResult':
        """执行菜单交互循环。"""
        gs = get_game_state()

        print("\n" + "=" * 50)
        print("游戏菜单 (输入 'help' 查看帮助)")
        print("=" * 50)

        while True:
            try:
                cmd = input("\n> ").strip().lower()
                
                if not cmd:
                    continue

                if cmd == "help":
                    self._show_help()
                elif cmd == "info player":
                    self._show_player_info(gs)
                elif cmd == "info deck":
                    self._show_deck_info(gs)
                elif cmd == "info relics":
                    self._show_relics_info(gs)
                elif cmd == "save":
                    self._save_game(gs)
                elif cmd == "exit":
                    return GameStateResult("GAME_EXIT")
                elif cmd == "return":
                    return SingleActionResult(self.parent_select_action)
                else:
                    print(f"未知命令: {cmd} (输入 'help' 查看帮助)")

            except (ValueError, EOFError, KeyboardInterrupt):
                print("\n输入错误，请重试")
            except Exception as e:
                print(f"错误: {e}")

    def _show_help(self):
        """显示帮助信息。"""
        print("\n可用命令:")
        print("  help           - 显示此帮助信息")
        print("  info player    - 显示玩家信息")
        print("  info deck      - 显示卡组信息")
        print("  info relics    - 显示遗物信息")
        print("  save           - 保存当前游戏状态")
        print("  exit           - 退出游戏")
        print("  return         - 返回游戏")

    def _show_player_info(self, gs):
        """显示玩家信息。"""
        player = gs.player
        print(f"\n--- 玩家信息 ---")
        print(f"生命值: {player.hp}/{player.max_hp}")
        print(f"能量: {player.energy}/{player.max_energy}")
        print(f"金币: {player.gold}")
        print(f"楼层: {gs.current_floor}")
        print(f"卡组数量: {len(player.deck)}")
        print(f"遗物数量: {len(player.relics)}")

    def _show_deck_info(self, gs):
        """显示卡组信息。"""
        print(f"\n--- 卡组信息 ({len(gs.player.deck)} 张) ---")
        for i, card in enumerate(gs.player.deck, 1):
            print(f"{i}. {card.name} (能量: {card.cost}, 类型: {card.card_type})")

    def _show_relics_info(self, gs):
        """显示遗物信息。"""
        print(f"\n--- 遗物信息 ({len(gs.player.relics)} 个) ---")
        for i, relic in enumerate(gs.player.relics, 1):
            print(f"{i}. {relic.name}")

    def _save_game(self, gs):
        """保存当前游戏状态。"""
        save_dir = "saves"
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        timestamp = __import__('time').strftime("%Y%m%d_%H%M%S")
        save_file = os.path.join(save_dir, f"save_{timestamp}.dat")

        try:
            with open(save_file, 'wb') as f:
                pickle.dump(gs, f)
            print(f"\n游戏已保存到: {save_file}")
        except Exception as e:
            print(f"\n保存失败: {e}")
