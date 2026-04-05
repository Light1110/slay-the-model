from cards.watcher._base import *

@register("card")
class Nirvana(Card):
    card_type = CardType.POWER
    target_type = TargetType.SELF
    rarity = RarityType.UNCOMMON
    base_cost = 1
    base_magic = {"block": 3}
    upgrade_magic = {"block": 4}
    text_name = "Nirvana"
    text_description = "Whenever you Scry, gain {magic.block} Block."

    def on_play(self, targets: List = []):
        add_action(ApplyPowerAction(NirvanaPower(amount=self.get_magic_value("block"), owner=_player()), _player()))
