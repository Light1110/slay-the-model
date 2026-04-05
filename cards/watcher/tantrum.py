from cards.watcher._base import *

@register("card")
class Tantrum(Card):
    card_type = CardType.ATTACK
    target_type = TargetType.ENEMY_SELECT
    rarity = RarityType.UNCOMMON
    base_cost = 1
    base_damage = 3
    upgrade_damage = 4
    base_attack_times = 3
    text_name = "Tantrum"
    text_description = "Deal {damage} damage {attack_times} times. Enter Wrath."

    # todo: 效果补全。还会将这张牌洗入抽牌堆
    def on_play(self, targets: List = []):
        super().on_play(targets)
        add_action(ChangeStanceAction(StatusType.WRATH))
