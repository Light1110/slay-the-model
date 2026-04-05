from cards.watcher._base import *

@register("card")
class FollowUp(Card):
    card_type = CardType.ATTACK
    target_type = TargetType.ENEMY_SELECT
    rarity = RarityType.COMMON
    base_cost = 1
    base_damage = 7
    upgrade_damage = 11
    text_name = "Follow-Up"
    text_description = "Deal {damage} damage. If the previous card played this turn was an Attack, gain 1 Energy."

    def on_play(self, targets: List = []):
        previous = _last_played_card() # todo: 同理。应当从combat_state里面看
        super().on_play(targets)
        if previous is not None and getattr(previous, "card_type", None) == CardType.ATTACK:
            add_action(GainEnergyAction(1))
