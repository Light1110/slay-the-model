"""
Boss Global Relics
Global relics available at boss rarity.
"""
from typing import List
from actions.base import Action, LambdaAction
from actions.card import AddCardAction, ChooseRemoveCardAction, DrawCardsAction, TransformCardAction
from actions.combat import GainBlockAction, GainEnergyAction, HealAction, DealDamageAction, ApplyPowerAction
from cards.colorless.curse_of_the_bell import CurseOfTheBell
from cards.colorless.wound import Wound
from relics.base import Relic
from utils.types import CombatType, PilePosType, RarityType, CardType
from utils.registry import register

# NOTE: AddRandomRelicAction must be imported lazily inside methods
# to avoid circular import between actions.reward -> relics.base -> relics.global_relics.boss

@register("relic")
class SneckoEye(Relic):
    """Draw 2 additional cards each turn. Start each combat Confused."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.BOSS

    def on_combat_start(self, player, entities):
        """Start each combat confused"""
        return [ApplyPowerAction(power="Confused", target=player, amount=0)]
    
    def on_player_turn_start(self, player, entities):
        """Draw 2 additional cards at start of turn"""
        return [DrawCardsAction(count=2)]

@register("relic")
class Astrolabe(Relic):
    """Upon pickup, choose and Transform 3 Cards, then Upgrade them."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.BOSS
    
    def on_obtain(self) -> List[Action]:
        # todo: ChooseTransformAndUpgradeAction
        return []

@register("relic")
class BlackStar(Relic):
    """Elites drop an additional Relic when defeated."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.BOSS
    
    # This would need to hook into elite enemy defeat events
    # For now, implemented as a passive effect description

@register("relic")
class BlackBlood(Relic):
    """Replaces Burning Blood. At the end of combat, heal 12 HP."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.BOSS
    
    def on_combat_end(self, player, entities):
        """Heal 12 HP at combat end"""
        return [HealAction(amount=12)]

@register("relic")
class BustedCrown(Relic):
    """Gain 1 Energy at start of each turn. On Card Reward screens, you have 2 fewer Cards to choose from."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.BOSS
    
    def on_player_turn_start(self, player, entities):
        """Gain 1 Energy at start of each turn"""
        return [GainEnergyAction(energy=1)]
    
    # todo: Implement action in actions/reward.py, If player has this relic, the total options in ChooseAddAction change 3->1

@register("relic")
class CallingBell(Relic):
    """Upon pickup, obtain a unique Curse and 3 Relics."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.BOSS
        
    def on_obtain(self) -> List[Action]:
        # Lazy import to avoid circular dependency
        from actions.reward import AddRandomRelicAction
        return [
            AddCardAction(CurseOfTheBell(), "deck"),
            AddRandomRelicAction([RarityType.COMMON]),
            AddRandomRelicAction([RarityType.UNCOMMON]),
            AddRandomRelicAction([RarityType.RARE])
        ]

@register("relic")
class CoffeeDripper(Relic):
    """Gain 1 Energy at start of each turn. You can no longer Rest at Rest Sites."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.BOSS
    
    def on_player_turn_start(self, player, entities):
        """Gain 1 Energy at start of each turn"""
        return [GainEnergyAction(energy=1)]
    
    # Implement logic in RestRoom

@register("relic")
class CursedKey(Relic):
    """Gain 1 Energy at start of each turn. Whenever you open a non-boss chest, obtain a Curse."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.BOSS
    
    def on_player_turn_start(self, player, entities):
        """Gain 1 Energy at start of each turn"""
        return [GainEnergyAction(energy=1)]
    
    # todo: on_chest_open

@register("relic")
class Ectoplasm(Relic):
    """Gain 1 Energy at start of each turn. You can no longer gain Gold."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.BOSS
    
    def on_player_turn_start(self, player, entities):
        """Gain 1 Energy at start of each turn"""
        return [GainEnergyAction(energy=1)]
    
    # todo: Implement in AddGoldAction

@register("relic")
class EmptyCage(Relic):
    """Upon pickup, remove 2 Cards from your Deck."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.BOSS
    
    def on_obtain(self) -> List[Action]:
        return [ChooseRemoveCardAction("deck", 2)]

@register("relic")
class FusionHammer(Relic):
    """Gain 1 Energy at start of each turn. You can no longer Smith at Rest Sites."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.BOSS
    
    def on_player_turn_start(self, player, entities):
        """Gain 1 Energy at start of each turn"""
        return [GainEnergyAction(energy=1)]
    
    # Implement logic in RestRoom

@register("relic")
class HoveringKite(Relic):
    """The first time you discard a Card each turn, gain 1 Energy."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.BOSS
        self.discarded_this_turn = False

    def on_combat_start(self, player, entities) -> List[Action]:
        """Reset discard flag at start of each turn"""
        return [LambdaAction(func=lambda: setattr(self, 'discarded_this_turn', False))]

    def on_card_discard(self, card, player, entities):
        """Trigger energy on first discard each turn"""
        if not self.discarded_this_turn:
            self.discarded_this_turn = True
            return [GainEnergyAction(energy=1)]
        return []

@register("relic")
class MarkOfPain(Relic):
    """Gain 1 Energy at start of each turn. Start combats with 2 Wounds in your Drawpile."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.BOSS
        self.wounds_added = False

    def on_combat_start(self, player, entities):
        """Add Wounds to draw pile at combat start"""
        return [AddCardAction(Wound(), "draw_pile", pos=PilePosType.RANDOM) * 2]

    def on_player_turn_start(self, player, entities):
        """Gain 1 Energy at start of each turn"""
        return [GainEnergyAction(energy=1)]

@register("relic")
class PandorasBox(Relic):
    """Transform all Strikes and Defends."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.BOSS
    
    def on_obtain(self) -> List[Action]:
        actions = []
        from engine.game_state import game_state
        namespace = game_state.player.namespace
        for card in game_state.player.card_manager.get_pile('deck'):
            if card.idstr == f"{namespace}.Attack" or card.idstr == f"{namespace}.Defend":
                actions.append(TransformCardAction(card, 'deck'))
        return actions

@register("relic")
class PhilosophersStone(Relic):
    """Gain 1 Energy at start of each turn. ALL enemies start with 1 Strength."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.BOSS

    def on_player_turn_start(self, player, entities):
        """Gain 1 Energy at start of each turn"""
        return [GainEnergyAction(energy=1)]
    
    def on_combat_start(self, player, entities) -> List[Action]:
        actions = []
        from engine.game_state import game_state
        assert game_state.current_combat is not None
        for enemy in game_state.current_combat.enemies:
            actions.append(ApplyPowerAction(
                power="Strength",
                target=enemy,
                amount=1
            ))
        return actions

@register("relic")
class RingOfSerpent(Relic):
    """Replaces Ring of Snake. At the start of your turn, draw 1 additional Card."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.BOSS

    def on_player_turn_start(self, player, entities):
        """Draw 1 additional card at start of each turn"""
        return [DrawCardsAction(count=1)]

@register("relic")
class RunicCube(Relic):
    """Whenever you lose HP, draw 1 card."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.BOSS

    def on_damage_taken(self, damage, source, player, entities):
        """Draw 1 card when taking damage"""
        if damage > 0:
            return [DrawCardsAction(count=1)]
        return []

@register("relic")
class RunicDome(Relic):
    """Gain 1 Energy at start of each turn. You can no longer see enemy Intents."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.BOSS

    def on_player_turn_start(self, player, entities):
        """Gain 1 Energy at start of each turn"""
        return [GainEnergyAction(energy=1)]
    
    # Implement the logic in Combat. Dont' print enemy intent info

@register("relic")
class RunicPyramid(Relic):
    """At the end of your turn, you no longer discard your hand."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.BOSS
    
    # This would need to hook into turn end events
    # For now, implemented as a passive effect description

@register("relic")
class SacredBark(Relic):
    """Double effectiveness of most Potions."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.BOSS

    # todo: Implement in AddPotionAction

@register("relic")
class SlaversCollar(Relic):
    """During Boss and Elite combats, gain 1 Energy at the start of your turn."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.BOSS

    def on_player_turn_start(self, player, entities):
        """Gain 1 Energy at start of each turn"""
        # Get current combat
        from engine.game_state import game_state
        combat = game_state.current_combat
        assert combat is not None
        if combat.combat_type != CombatType.NORMAL:
            return [GainEnergyAction(energy=1)]
        return []

@register("relic")
class Sozu(Relic):
    """Gain 1 Energy at start of each turn. You can no longer obtain Potions."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.BOSS

    def on_player_turn_start(self, player, entities):
        """Gain 1 Energy at start of each turn"""
        return [GainEnergyAction(energy=1)]
    
    # todo: Implement in AddPotionAction

@register("relic")
class TinyHouse(Relic):
    """Obtain 1 Potion. Gain 50 Gold. Raise your Max HP by 5. Obtain 1 Card. Upgrade 1 Random Card."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.BOSS
    
    # This would need to hook into relic pickup events
    # For now, implemented as a passive effect description

@register("relic")
class VelvetChoker(Relic):
    """Gain 1 Energy at start of each turn. You cannot play more than 6 Cards per turn."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.BOSS

    def on_player_turn_start(self, player, entities):
        """Gain Energy at start of turn if not at card limit"""
        return [GainEnergyAction(energy=1)]

    # Implement in PlayCardAction or Card.can_play. Use combat_state's turn_cards_played

@register("relic")
class WristBlade(Relic):
    """Attacks that cost 0 Energy deal 4 additional damage."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.BOSS
    
    # Implement in resolve_card_damage and resolve_final_damage
