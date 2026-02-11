"""
Uncommon Global Relics
Global relics available to all characters at uncommon rarity.
"""
from typing import List
from actions.base import Action, LambdaAction
from actions.card import DrawCardsAction, AddCardAction, ExhaustCardAction
from actions.combat import GainBlockAction, GainEnergyAction, HealAction, DealDamageAction, ApplyPowerAction, ModifyMaxHpAction
# GainGoldAction imported lazily when needed to avoid circular import
from relics.base import Relic
from utils.types import RarityType, CardType
from utils.registry import register

# Existing relic
@register("relic")
class HornCleat(Relic):
    """At the start of your 2nd turn, gain 14 Block."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON

    def on_player_turn_start(self, player, entities):
        """At the start of your 2nd turn, gain 14 Block."""
        from engine.game_state import game_state
        if game_state.current_combat is not None:
            if game_state.current_combat.combat_state.combat_turn == 2:
                return [GainBlockAction(block=14)]
        return []

# New Uncommon relics
@register("relic")
class BlueCandle(Relic):
    """Curse Cards can now be played. Playing a Curse will make you lose 1 HP and Exhaust Card."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON
    
    # This would need to hook into card play for curses
    # For now, implemented as a passive effect description

@register("relic")
class BottledFlame(Relic):
    """Upon pick up, choose an Attack. Start each combat with this Card in your hand."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON
        self.selected_card = None  # Would be set on pickup
    
    # todo: combat 中卡牌的机制没有完全实现
    # 1. 先把deck copy一份到draw_pile
    # 2. 第一回合，抽5张牌。
    # 2.1 首先在draw_pile中找到selected_card，move到hand。
    # 2.2 其次在draw_pile中找到innate的卡牌，move到hand。剩下的空缺再抽牌

@register("relic")
class BottledLightning(Relic):
    """Upon pick up, choose a Skill. Start each combat with this Card in your hand."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON
        self.selected_card = None  # Would be set on pickup
    
    # todo: combat 中卡牌的机制没有完全实现
    # 1. 先把deck copy一份到draw_pile
    # 2. 第一回合，抽5张牌。
    # 2.1 首先在draw_pile中找到selected_card，move到hand。
    # 2.2 其次在draw_pile中找到innate的卡牌，move到hand。剩下的空缺再抽牌

@register("relic")
class BottledTornado(Relic):
    """Upon pick up, choose a Power. Start each combat with this Card in your hand."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON
        self.selected_card = None  # Would be set on pickup
    
    # todo: combat 中卡牌的机制没有完全实现
    # 1. 先把deck copy一份到draw_pile
    # 2. 第一回合，抽5张牌。
    # 2.1 首先在draw_pile中找到selected_card，move到hand。
    # 2.2 其次在draw_pile中找到innate的卡牌，move到hand。剩下的空缺再抽牌

@register("relic")
class DarkstonePeriapt(Relic):
    """Whenever you obtain a Curse, increase your Max HP by 6."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON
    
    # This would need to hook into curse acquisition events
    # For now, implemented as a passive effect description

@register("relic")
class EternalFeather(Relic):
    """For every 5 Cards in your deck, heal 3 HP whenever you enter a Rest Site."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON
    
    # This would need to hook into rest events
    # For now, implemented as a passive effect description

@register("relic")
class FrozenEgg(Relic):
    """Whenever you add a Power to your deck, it is Upgraded."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON
    
    # This would need to hook into card addition events
    # For now, implemented as a passive effect description

@register("relic")
class GremlinHorn(Relic):
    """Whenever an enemy dies, gain 1 Energy and draw 1 Card."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON
    
    def on_damage_dealt(self, damage, target, player, entities):
        """When an enemy dies, gain energy and draw card"""
        if target.is_dead():
            return [
                GainEnergyAction(energy=1),
                DrawCardsAction(count=1)
            ]
        return []

@register("relic")
class InkBottle(Relic):
    """Whenever you play 10 cards, draw 1 Card."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON
        self.cards_played = 0
    
    def on_card_play(self, card, player, entities):
        """Track cards played"""
        self.cards_played += 1
        if self.cards_played >= 10:
            self.cards_played = 0
            return [DrawCardsAction(count=1)]
        return []

@register("relic")
class Kunai(Relic):
    """Every time you play 3 Attacks in a single turn, gain 1 Dexterity."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON
        self.attacks_played_this_turn = 0
    
    def on_combat_start(self, player, entities):
        """Reset attack counter at start of each turn"""
        self.attacks_played_this_turn = 0
        return []
    
    def on_card_play(self, card, player, entities):
        """Track attacks played and gain Dexterity"""
        if card.card_type == CardType.ATTACK:
            self.attacks_played_this_turn += 1
            if self.attacks_played_this_turn >= 3:
                return [ApplyPowerAction(power="Dexterity", target=player, amount=1)]
        return []

@register("relic")
class LetterOpener(Relic):
    """Every time you play 3 Skills in a single turn, deal 5 damage to ALL enemies."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON
        self.skills_played_this_turn = 0
    
    def on_combat_start(self, player, entities):
        """Reset skill counter at start of each turn"""
        self.skills_played_this_turn = 0
        return []
    
    def on_card_play(self, card, player, entities):
        """Track skills played and deal damage"""
        if card.card_type == CardType.SKILL:
            self.skills_played_this_turn += 1
            if self.skills_played_this_turn >= 3:
                actions = []
                for enemy in entities:
                    actions.append(DealDamageAction(damage=5, target=enemy))
                return actions
        return []

@register("relic")
class Matryoshka(Relic):
    """The next 2 Chests you open contain 2 Relics."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON
        self.chests_to_spawn = 2
    
    # This would need to hook into chest opening events
    # For now, implemented as a passive effect description

@register("relic")
class MeatOnBone(Relic):
    """If your HP is at or below 50% at end of combat, heal 12 HP."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON
    
    def on_combat_end(self, player, entities):
        """Heal if HP at or below 50% at combat end"""
        if player and player.hp <= (player.max_hp / 2):
            return [HealAction(amount=12)]
        return []

@register("relic")
class MercuryHourglass(Relic):
    """At the start of your turn, deal 3 damage to ALL enemies."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON
    
    def on_player_turn_start(self, player, entities):
        """Deal 3 damage to all enemies at turn start"""
        actions = []
        for enemy in entities:
            actions.append(DealDamageAction(damage=3, target=enemy))
        return actions

@register("relic")
class MoltenEgg(Relic):
    """Whenever you add an Attack to your deck, it is Upgraded."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON
    
    # This would need to hook into card addition events
    # For now, implemented as a passive effect description

@register("relic")
class MummifiedHand(Relic):
    """Whenever you play a Power, a random card in your hand costs 0 Energy for turn."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON
    
    def on_card_play(self, card, player, entities):
        """Make random card in hand cost 0 for turn"""
        if card.card_type == CardType.POWER:
            from engine.game_state import game_state
            hand = game_state.player.card_manager.get_pile('hand')
            if hand:
                import random
                target_card = random.choice(hand)
                target_card.temp_cost = 0
        return []

@register("relic")
class NinjaScroll(Relic):
    """Start each combat with 3 Shivs in hand."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON
    
    # This is Silent-specific, would need to add Shiv cards
    # For now, implemented as a passive effect description

@register("relic")
class OrnamentalFan(Relic):
    """Every time you play 3 Attacks in a single turn, gain 4 Block."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON
        self.attacks_played_this_turn = 0
    
    def on_combat_start(self, player, entities):
        """Reset attack counter at start of each turn"""
        self.attacks_played_this_turn = 0
        return []
    
    def on_card_play(self, card, player, entities):
        """Track attacks played and gain Block"""
        if card.card_type == CardType.ATTACK:
            self.attacks_played_this_turn += 1
            if self.attacks_played_this_turn >= 3:
                return [GainBlockAction(block=4)]
        return []

@register("relic")
class Pantograph(Relic):
    """At the start of Boss combats, heal 25 HP."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON
    
    # todo:on_combat_start, then check current_room's type

@register("relic")
class PaperKrane(Relic):
    """Enemies with Weak deal 50% less damage rather than 25%."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON
    
    # This would need to hook into damage calculation
    # For now, implemented as a passive effect description

@register("relic")
class PaperPhrog(Relic):
    """Enemies with Vulnerable take 75% more damage rather than 50%."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON
    
    # This would need to hook into damage calculation
    # For now, implemented as a passive effect description

@register("relic")
class Pear(Relic):
    """Raise your Max HP by 10."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON
    
    def on_obtain(self) -> List[Action]:
        return [ModifyMaxHpAction(amount=10)]

@register("relic")
class QuestionCard(Relic):
    """On future Card Reward screens you have 1 additional Card to choose from."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON
    
    # This would need to hook into card reward events
    # For now, implemented as a passive effect description

@register("relic")
class SelfFormingClay(Relic):
    """Whenever you lose HP in combat, gain 3 Block next turn."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON
        self.block_gain_next_turn = 0
    
    def on_damage_taken(self, damage, source, player, entities):
        """Track HP loss to gain Block next turn"""
        if damage > 0:
            self.block_gain_next_turn = 3
        return []
    
    def on_player_turn_start(self, player, entities):
        """Gain Block if HP was lost last turn"""
        if self.block_gain_next_turn > 0:
            block = self.block_gain_next_turn
            self.block_gain_next_turn = 0
            return [GainBlockAction(block=block)]
        return []

@register("relic")
class Shuriken(Relic):
    """Every time you play 3 Attacks in a single turn, gain 1 Strength."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON
        self.attacks_played_this_turn = 0
    
    def on_combat_start(self, player, entities):
        """Reset attack counter at start of each turn"""
        self.attacks_played_this_turn = 0
        return []
    
    def on_card_play(self, card, player, entities):
        """Track attacks played and gain Strength"""
        if card.card_type == CardType.ATTACK:
            self.attacks_played_this_turn += 1
            if self.attacks_played_this_turn >= 3:
                return [ApplyPowerAction(power="Strength", target=player, amount=1)]
        return []

@register("relic")
class SingingBowl(Relic):
    """When adding Cards to your deck, you may gain +2 Max HP instead."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON
    
    # This would need to hook into card addition events with a choice
    # For now, implemented as a passive effect description
    # This is implemented in giving card reward

@register("relic")
class StrikeDummy(Relic):
    """Cards containing "Strike" deal 3 additional damage."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON
    
    # This would need to hook into damage calculation for Strike cards
    # For now, implemented as a passive effect description
    # in resolve_card_damage && resolve_potential_damange

@register("relic")
class Sundial(Relic):
    """Every 3 times you shuffle your Drawpile, gain 2 Energy."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON
        self.shuffle_count = 0
    
    # This would need to hook into shuffle events
    # For now, implemented as a passive effect description
    # todo: on_shuffle

@register("relic")
class TheCourier(Relic):
    """The merchant no longer runs out of Cards, Relics, or Potions and his prices are reduced by 20%."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON
    
    # This would need to hook into shop events
    # For now, implemented as a passive effect description

@register("relic")
class ToxicEgg(Relic):
    """Whenever you add a Skill to your deck, it is Upgraded."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON
    
    # This would need to hook into card addition events
    # For now, implemented as a passive effect description

@register("relic")
class WhiteBeastStatue(Relic):
    """Potions always drop after combat."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON
    
    # This would need to hook into combat end events
    # For now, implemented as a passive effect description
