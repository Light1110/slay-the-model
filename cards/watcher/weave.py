from cards.watcher._base import *

@register("card")
class Weave(Card):
    card_type = CardType.ATTACK
    target_type = TargetType.ENEMY_SELECT
    rarity = RarityType.UNCOMMON
    base_cost = 0
    base_damage = 4
    upgrade_damage = 6
    text_name = "Weave"
    text_description = "Deal {damage} damage. Whenever you Scry, return this from your discard pile to your hand."

    @subscribe(ScryMessage, priority=MessagePriority.CARD)
    def on_scry(self, count):
        add_action(ReturnCardToHandAction(self))
