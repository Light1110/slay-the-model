from cards.watcher._base import *

@register("card")
class WaveOfTheHand(Card):
    card_type = CardType.POWER
    target_type = TargetType.SELF
    rarity = RarityType.UNCOMMON
    base_cost = 1
    base_magic = {"weak": 1}
    upgrade_magic = {"weak": 2}
    text_name = "Wave of the Hand"
    text_description = "Whenever you gain Block this turn, apply {magic.weak} Weak to ALL enemies."

    def on_play(self, targets: List = []):
        add_action(ApplyPowerAction(WaveOfTheHandPower(amount=self.get_magic_value("weak"), duration=1, owner=_player()), _player()))
