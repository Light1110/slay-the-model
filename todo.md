# TODO List

## 关于战斗的所有残余逻辑

Turns
Combat is turn-based: first the player takes a turn, then the enemy party takes a turn, then repeat. This continues until either the enemy or the player dies.

Player Turn
At the start of the player's turn, three things happen:

Energy is set to the base energy (default 3), and
A number of cards are drawn (default 5), and
Start-of-turn effects trigger.
The default behavior can be changed, typically by Relics (e.g. FusionHammer.png Fusion Hammer increases the base energy by 1; SneckoEye.png Snecko Eye increases the number of cards drawn per turn by 2).

During their turn, the player may play cards or drink Potions. Cards with an energy cost will subtract that energy from the total. All player actions are resolved immediately upon being performed.

When the player presses End Turn, two things happen:

End-of-turn effects trigger.
This generally resolves in the order relics -> buffs -> cards (e.g. Orichalcum.png Orichalcum will trigger before Icon PlatedArmor.png Plated Armor, which will trigger before CardIcon Status.png Burns).
Cards in hand are shuffled into the discard pile.
This will not occur with RunicPyramid.png Runic Pyramid or any cards that are Retained, unless they are cards with end-of-turn Effects like CardIcon Curse.png Regret or CardIcon Status.png Burn.
Cards with end-of-turn Effects can sometimes also be Retained at exactly 1 point: during the Map-Awakened.png Awakened One phase shift. If Awakened One's first phase is killed with an effect that takes place right after the player's turn ends, but before the enemy turn begins (Defect's LightningOrb.png  Lightning Orb passive or StoneCalendar.png Stone Calendar), cards that would normally be discarded like CardIcon Status.png Burn can be Retained.
Then the enemy party takes its turn.

Enemy Turn
Enemy actions during their turn are governed by their Intents, visible as floating symbols above their heads. In multi-enemy encounters, enemies always take actions from left to right.

战斗流程伪代码：

```python
while True:
    result = self.execute_player_phase()
    if result.return_type in ("COMBAT_WIN", "COMBAT_LOSE", "COMBAT_ESCAPE"):
        break
    result = self.execute_enemy_phase()
    if result.return_type in ("COMBAT_WIN", "COMBAT_LOSE", "COMBAT_ESCAPE"):
        break
```

玩家回合

```python
result = self.start_player_phase() -> {
    # gain energy
    # draw crads
    # trigger Start-of-turn effects
}

while current_phase = "player"
    # build SelectAction for player: including playing cards, using potions, ending turn ...

result = self.end_player_phase() -> {
    # End-of-turn effects trigger
    # Cards in hand are shuffled into the discard pile
}
```

敌人回合

```python
# dead enemies are previously removed from the list
for enemy in self.enemies:
    enemy.take_actions()
```
