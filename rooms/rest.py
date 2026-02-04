"""
Rest room implementation.
"""
from actions.base import Action, action_queue
from actions.card import ChooseRemoveCardAction, ChooseUpgradeCardAction
from actions.display import SelectAction
from actions.health import HealAction
from actions.reward import AddRelicAction, AddRandomRelicAction
from engine.game_state import game_state
from localization import LocalStr
from rooms.base import Room
from utils.option import Option
from utils.registry import register
from utils.types import RarityType


def _has_relic(relic_name: str) -> bool:
    """Check if player has a specific relic"""
    for relic in game_state.player.relics:
        if relic.idstr == relic_name:
            return True
    return False


@register("room")
class RestRoom(Room):
    """Rest site room where player can rest, upgrade cards, or recall Ruby Key"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.localization_prefix = "rooms"

    def enter_room(self):
        """Enter the rest room"""
        super().enter_room()

        # Handle Eternal Feather - heal on enter
        if _has_relic("EternalFeather"):
            deck = game_state.player.card_manager.get_pile('deck')
            deck_size = len(deck)
            heal_amount = (deck_size // 5) * 3
            if heal_amount > 0:
                HealAction(amount=heal_amount).execute()

        # Create options based on available actions
        options = []

        # Rest option
        if not (_has_relic("CoffeeDripper") or _has_relic("MarkOfTheBloom")):
            heal_amount = int(game_state.player.max_hp * 0.30)
            if _has_relic("RegalPillow"):
                heal_amount += 15
            actions = [HealAction(amount=heal_amount)]
            options.append(Option(
                name=self.local("RestRoom.rest", amount=heal_amount),
                actions=actions
            ))

        # Smith option (upgrade card)
        can_smith = not _has_relic("FusionHammer")
        if can_smith:
            deck = game_state.player.card_manager.get_pile('deck')
            for card in deck:
                if not card.upgraded:
                    can_smith = True
                    break
        if can_smith:
            options.append(Option(
                name=self.local("RestRoom.smith"),
                actions=[ChooseUpgradeCardAction(pile="deck")]
            ))

        # todo: Recall option (Ruby Key) - disabled for now
        # if _can_recall():
        #     options.append(Option(
        #         name=self.local("RestRoom.recall"),
        #         actions=[AddRelicAction(relic="RubyKey")]
        #     ))

        # Special relic options (Girya, Peace Pipe, Shovel)
        if _has_relic("Girya"):
            options.append(Option(
                name=self.local("RestRoom.lift"),
                actions=[] # todo: Lift Action：更新遗物Lift的计数
            ))

        if _has_relic("PeacePipe"):
            options.append(Option(
                name=self.local("RestRoom.toke"),
                actions=[ChooseRemoveCardAction(pile="deck")]
            ))

        if _has_relic("Shovel"):
            options.append(Option(
                name=self.local("RestRoom.dig"),
                actions=[AddRandomRelicAction(rarities=[RarityType.COMMON, RarityType.UNCOMMON, RarityType.RARE])]
            ))
            
        # 直接离开
        options.append(Option(
            name=self.local("RestRoom.skip"),
            actions=[]
        ))

        # Add selection action
        action_queue.add_action(SelectAction(
            title=self.local("RestRoom.title"),
            options=options
        ))

    def leave_room(self):
        """Leave the rest room"""
        # Handle Ancient Tea Set - add energy next turn
        if _has_relic("AncientTeaSet"):
            # Add 2 energy for next combat
            # todo: Would need to track this in game state
            pass
        super().leave_room()
