from cards.watcher._base import *

@register("card")
class EmptyFist(Card):
    card_type = CardType.ATTACK
    target_type = TargetType.ENEMY_SELECT
    rarity = RarityType.COMMON
    base_cost = 1
    base_damage = 9
    upgrade_damage = 14
    text_name = "Empty Fist"
    text_description = "Deal {damage} damage. Exit your stance."

    def on_play(self, targets: List = []):
        super().on_play(targets)
        add_action(ChangeStanceAction(StatusType.NEUTRAL))
