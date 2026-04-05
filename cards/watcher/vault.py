from cards.watcher._base import *

@register("card")
class Vault(WatcherSkill):
    rarity = RarityType.RARE
    base_cost = 3
    upgrade_cost = 2
    base_exhaust = True
    text_name = "Vault"
    text_description = "End your turn. Take another turn after this one."

    # todo: 功能有漏洞。跳过怪物回合的时候，下一个回合怪物的意图将保持和上回合一致。当前没有实现
    def on_play(self, targets: List = []):
        add_actions([SkipEnemyTurnAction(), EndTurnAction()])
