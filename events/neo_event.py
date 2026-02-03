"""
Neo blessing event.
"""

from actions.card import ChooseAddRandomCardAction, ChooseRemoveCardAction, ChooseTransformCardAction, ChooseUpgradeCardAction, AddRandomCardAction
from events.base_event import Event, EventStage
from actions.display import SelectAction
from actions.misc import EndEventAction
from actions.reward import AddGoldAction, AddRandomPotionAction, AddRandomRelicAction, AddRelicAction, LoseGoldAction, LoseRelicAction
from actions.combat import LoseHpAction, ModifyMaxHpAction
from actions.base import action_queue
from engine.game_state import game_state
from engine.game_stats import game_stats
from localization import LocalStr
from utils.option import Option
from utils.types import CardType, RarityType

class NeoEvent(Event):
    """Neo blessing event"""

    def __init__(self, callback=None, **kwargs):
        super().__init__(callback=callback, **kwargs)

    def build_stages(self):
        return [
            NeoBlessingStage("blessing_selection")
        ]


class NeoBlessingStage(EventStage):
    """Stage for Neo blessing selection"""

    def execute(self):
        super().execute()
        
        if game_state.run_history.get("reached_exordium_boss", False):
            self.execute_four_blessings()
        else:
            self.execute_basic_blessings()
        action_queue.add_action(EndEventAction())
        
    def execute_basic_blessings(self):
        max_hp_small_increase = game_stats.neow_max_hp_small_increases.get(game_state.player.character, 0)
        action_queue.add_action(
            SelectAction(
                title = LocalStr("ui.choose_blessings"),
                options = [
                    Option(name = LocalStr("blessing.max_hp_option"),
                        actions = [
                            ModifyMaxHpAction(amount=max_hp_small_increase),
                        ]
                    ),
                    Option(name = LocalStr("blessing.random_common_relic_option"),
                        actions = [
                            AddRelicAction(relic="Neow's Blessing"),
                        ]
                    )
                ]
            )
        )
    
    def execute_four_blessings(self):
        max_hp_small_increase = game_stats.neow_max_hp_small_increases.get(game_state.player.character, 0)
        max_hp_large_increase = game_stats.neow_max_hp_large_increases.get(game_state.player.character, 0)
        max_hp_small_decrease = game_stats.neow_max_hp_small_decreases.get(game_state.player.character, 0)
        damage_taken = (game_state.player.hp // 10) * 3
        
        card_blessings = [
            Option(name = LocalStr("blessing.remove_card_option"),
                actions = [
                    ChooseRemoveCardAction(pile="deck", amount=1),
                ]
            ),
            Option(name = LocalStr("blessing.transform_card_option"),
                actions = [
                    ChooseTransformCardAction(pile="deck", amount=1),
                ]
            ),
            Option(name = LocalStr("blessing.upgrade_card_option"),
                actions = [
                    ChooseUpgradeCardAction(pile="deck", amount=1),
                ]
            ),
            Option(name = LocalStr("blessing.choose_card_option"),
                actions = [
                    ChooseAddRandomCardAction(pile="deck", total=3, namespace=game_state.player.character, rarity=None),
                ]
            ),
            Option(name = LocalStr("blessing.uncommon_colorless_option"),
                actions = [
                    ChooseAddRandomCardAction(pile="deck", total=3, namespace="colorless", rarity=RarityType.UNCOMMON),
                ]
            ),
            Option(name = LocalStr("blessing.random_rare_card_option"),
                actions = [
                    AddRandomCardAction(pile="deck", namespace=game_state.player.character, rarity=RarityType.RARE),
                ]
            )
        ]

        non_card_blessings = [
            Option(name = LocalStr("blessing.max_hp_option"),
                actions = [
                    ModifyMaxHpAction(amount=max_hp_small_increase),
                ]
            ),
            Option(name = LocalStr("blessing.neow_option"),
                actions = [
                    AddRelicAction(relic="Neow's Blessing"),
                ]
            ),
            Option(name = LocalStr("blessing.random_common_relic_option"),
                actions = [
                    AddRandomRelicAction(rarity=RarityType.COMMON),
                ]
            ),
            Option(name = LocalStr("blessing.receive_100_gold_option"),
                actions = [
                    AddGoldAction(amount=100),
                ]
            ),
            Option(name = LocalStr("blessing.three_random_potions_option"),
                actions = [
                    AddRandomPotionAction(),
                    AddRandomPotionAction(),
                    AddRandomPotionAction(),
                ]
            )
        ]
        
        disadvantage_blessings = [
            Option(name = LocalStr("blessing.lose_max_hp_option"),
                actions = [
                    ModifyMaxHpAction(amount=-max_hp_small_decrease),
                ]
            ),
            Option(name = LocalStr("blessing.take_damage_option"),
                actions = [
                    LoseHpAction(amount=damage_taken),
                ]
            ),
            Option(name = LocalStr("blessing.obtian_curse_option"),
                actions = [
                    AddRandomCardAction(pile="deck", card_type=CardType.CURSE, rarity=None),
                ]
            ),
            Option(name = LocalStr("blessing.lose_all_gold_option"),
                actions = [
                    LoseGoldAction(amount=game_state.player.gold),
                ]
            )
        ]
        
        advantage_blessings = [
            Option(name = LocalStr("blessing.remove_two_cards_option"),
                actions = [
                    ChooseRemoveCardAction(pile="deck", amount=2),
                ]
            ),
            Option(name = LocalStr("blessing.transform_two_cards_option"),
                actions = [
                    ChooseTransformCardAction(pile="deck", amount=2),
                ]
            ),
            Option(name = LocalStr("blessing.gain_250_gold_option"),
                actions = [
                    AddGoldAction(amount=250),
                ]
            ),
            Option(name = LocalStr("blessing.choose_rare_card_option"),
                actions = [
                    ChooseAddRandomCardAction(pile="deck", total=3, namespace=game_state.player.character, rarity=RarityType.RARE)
                ]
            ),
            Option(name = LocalStr("blessing.choose_rare_colorless_card_option"),
                actions = [
                    ChooseAddRandomCardAction(pile="deck", total=3, namespace="colorless", rarity=RarityType.RARE)
                ]
            ),
            Option(name = LocalStr("blessing.random_rare_relic_option"),
                actions = [
                    AddRandomRelicAction(rarity=RarityType.RARE),
                ]
            ),
            Option(name = LocalStr("blessing.big_max_hp_option"),
                actions = [
                    ModifyMaxHpAction(amount=max_hp_large_increase),
                ]
            )
        ]

        import random
        
        card_blessing_idx = random.randint(0, len(card_blessings) - 1)
        non_card_blessing_idx = random.randint(0, len(non_card_blessings) - 1)
        card_blessing = card_blessings[card_blessing_idx]
        non_card_blessing = non_card_blessings[non_card_blessing_idx]
        
        # mixed 是 disadvantage 和 advantage 做笛卡尔积
        disadvantage_blessing_idx = random.randint(0, len(disadvantage_blessings) - 1)
        advantage_blessing_idx = random.randint(0, len(advantage_blessings) - 1)
        disadvantage_blessing = disadvantage_blessings[disadvantage_blessing_idx]
        advantage_blessing = advantage_blessings[advantage_blessing_idx]
        mixed_blessing = Option(
            name = disadvantage_blessing.name + " + " + advantage_blessing.name,
            actions = disadvantage_blessing.actions + advantage_blessing.actions
        )

        relic_blessing = Option(
            name = LocalStr("blessing.replace_starter_relic_option"),
            actions = [
                LoseRelicAction(relic = game_state.player.relics[0]),
                AddRandomRelicAction(rarity=RarityType.BOSS),
            ]
        )
        
        action_queue.add_action(
            SelectAction(
                title = LocalStr("ui.choose_blessings"),
                options = [card_blessing, non_card_blessing, mixed_blessing, relic_blessing]
            )
        )
        

        
