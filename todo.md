# TODO 改动计划

本文件整理了整个工程中的所有 `# todo` 注释，并按优先级排序。

---

## P0 - 紧急修复（影响核心游戏机制）

### 1. 敌人攻击力动态计算
- **位置**: `enemies/act1/cultist_intentions.py:48`
- **TODO**: 这个攻击力应该是动态计算的，考虑能力和玩家状态
- **当前问题**: CultistAttackIntention 使用固定的 `base_damage = 6`，没有考虑敌人的 Strength 和玩家的 Vulnerable 状态
- **改动方案**:
  1. 在 `AttackAction` 中已经处理了 Weak/Vulnerable 的影响
  2. 修改所有敌人 intention 使用动态计算而非固定值
- **影响范围**: 所有敌人意图系统
- **预计工作量**: 2-3小时

---

## P1 - 高优先级（核心功能缺失）

### 2. 创建 ConfusedPower 并应用到 SneckoEye 遗物
- **位置**: `relics/global/boss.py:23`
- **TODO**: Create ConfusedPower and apply it here
- **当前问题**: SneckoEye 遗物需要在战斗开始时应用 ConfusedPower（随机化卡牌费用），但这个 Power 尚未实现
- **改动方案**:
  1. 在 `powers/definitions/` 下创建 `confused.py`
  2. 实现 ConfusedPower: 随机化抽取到的卡牌的费用 (0-3)
  3. 在 SneckoEye 的 `on_combat_start` 中应用该 Power
  4. 这个 power 的 `on_card_draw` 时，会随机设置卡牌的 cost
- **影响范围**: Power 系统、卡牌费用计算
- **预计工作量**: 3-4小时

### 3. Akabeko 遗物攻击加成实现
- **位置**: `relics/global/common.py:23`
- **TODO**: 怎么应用攻击加成
- **当前问题**: Akabeko 遗物应该让每场战斗的第一张攻击卡额外造成 8 点伤害，但只设置了标记未实现
- **改动方案**:
  1. 在 `utils/dynmic_values.py` 中的 `?` 中检查 Akabeko
  2. 如果是本场战斗的第一张攻击卡，额外造成 8 点伤害
  3. 修改 `CombatState` 类添加 `first_attack_played` 标记
  4. Akabeko 在战斗开始时重置该标记
- **影响范围**: 卡牌播放逻辑
- **预计工作量**: 2小时

### 4. 战斗胜利金币奖励波动
- **位置**: `rooms/combat.py:73`
- **TODO**: 价格波动
- **当前问题**: 战斗胜利后的金币奖励是固定值（Boss 150, Elite 50, 普通 15），应该有随机波动
- **改动方案**:
Normal encounters drop 10-20 Gold.
Elites drop 25-35 Gold.
Bosses drop 95-105 (71-79 Ascension13) Gold.
- **影响范围**: 战斗奖励系统
- **预计工作量**: 0.5小时

---

## P2 - 中优先级（架构优化）

### 5. 抽卡数量可被遗物/能力修改
- **位置**: `engine/combat.py:175`
- **TODO**: modified by relics/powers
- **当前问题**: 每回合抽卡数量固定为 5，但应该受遗物（如 BagOfPreparation）和能力影响
- **改动方案**:
  1. 在 `Player` 类添加 `base_draw_count` 属性（默认为 5）
  2. 遗物可以修改该属性（长蛇之戒，暂时不实现）
  3. BagOfPreparation 在 `on_combat_start` 时 `DrawCardsAction`
- **影响范围**: 玩家属性系统、遗物系统
- **预计工作量**: 1小时

### 6. 战斗信息显示
- **位置**: `engine/combat.py:113`
- **TODO**: print combat information
- **当前问题**: 战斗阶段没有显示当前状态（HP、能量、格挡等）
- **改动方案**:
  1. 在 `_build_player_action` 中添加战斗信息显示
  2. 显示: 玩家 HP/格挡/能量、敌人 HP/格挡/意图
  3. 使用 `DisplayTextAction` 格式化输出
- **影响范围**: 战斗 UI
- **预计工作量**: 1小时

---

## P3 - 低优先级（代码质量/架构清理）

### 7. Power 的 tick_down 应该由 on_turn_end 调用
- **位置**: `engine/combat.py:128`
- **TODO**: power tick_down should be called by on_turn_end
- **当前问题**: 现在的代码结构不清晰，tick_down 的调用位置不确定
- **改动方案**:
  1. 确认 Power 类的 `on_turn_end` 是否已经包含 tick_down 逻辑
  2. 如果没有，修改 `powers/base.py` 在 `on_turn_end` 中调用 `tick_down`
  3. 删除外部直接调用 `tick_down` 的代码
- **影响范围**: Power 系统
- **预计工作量**: 0.5小时

### 8. 随机卡牌选择时考虑稀有度权重
- **位置**: `utils/random.py:8`
- **TODO**: 对于没有指定稀有度的情况，考虑根据权重选择稀有度
- **当前问题**: `get_random_card` 当未指定 `rarities` 参数时，是等概率从所有卡牌中选择，应该根据稀有度权重选择
- **改动方案**:
每次获得Rare卡牌的初始概率为以下百分比减去5%。每滚动一张Common卡牌，概率就会依次增加1%。这个偏移量会从Common卡牌的概率中减去（然后是Uncommon卡牌，如果适用）。

当滚动到Rare卡牌时，概率会重置为列出的值，减去5%。因此，你在Act 1、Act 2和Act 3的第一层永远不可能有Rare卡牌，除非在特殊情况下[1]，并且Tiny House在获得Rare卡牌后直接给出Rare卡牌也是不可能的。

## 普通遭遇中的基础概率（偏移前）

| 卡牌类型 | 概率 |
|---------|------|
| Rare Card | 3% |
| Uncommon Card | 37% |
| Common Card | 60% |

## 精英遭遇中的基础概率（偏移前）

| 卡牌类型 | 概率 |
|---------|------|
| Rare Card | 10% |
| Uncommon Card | 40% |
| Common Card | 50% |

## 商店中的基础概率（偏移前）

| 卡牌类型 | 概率 |
|---------|------|
| Rare Card | 9% |
| Uncommon Card | 37% |
| Common Card | 54% |

只有来自卡牌奖励的卡牌会受到Orerry和Tiny House的影响。商店卡牌和来自?的卡牌不会影响稀有度偏移，但它们会受到稀有度的影响。Orerry的作用类似于商店中的5张卡牌奖励，但它使用的是商店的基础概率。也就是说，它既影响也被偏移量影响。生成卡牌的序列不受卡牌稀有度的影响，除了Foreign Influence[2]
- **影响范围**: 随机卡牌生成
- **预计工作量**: 1小时

### 9. Tiny Chest 遗物使用自己的计数器
- **位置**: `map/map_manager.py:90`
- **TODO**: use relic's own counter
- **当前问题**: `_tiny_chest_counter` 计数器在 `MapManager` 中，应该在 Tiny Chest 遗物内部
- **改动方案**:
  1. 在 Tiny Chest 遗物类中添加 `unknown_room_count` 属性
  2. `MapManager` 检查遗物并调用其方法递增计数
  3. 遗物判断是否触发 Treasure 房间
- **影响范围**: 遗物系统、地图系统
- **预计工作量**: 1小时

### 10. ExplosivePotion 访问敌人的架构问题
- **位置**: `potions/global_potions.py:79`
- **TODO**: game_state里面存curr_combat, combat_state是combat的属性
- **当前问题**: 使用 `game_state.combat_state.enemies` 访问敌人，但注释提示这可能不是正确的架构
- **改动方案**:
  1. 确认 `game_state` 是否应该存储 `current_combat` 引用
  2. 或者保留现有架构，但更新注释说明这是正确的用法
  3. 如果需要重构: 在 `Combat` 类添加 `get_all_enemies()` 方法
- **影响范围**: 战斗状态管理架构
- **预计工作量**: 0.5-2小时（取决于是否需要重构）

---

## 统计

- **P1 高优先级**: 3 项
- **P2 中优先级**: 2 项
- **P3 低优先级**: 4 项
- **总计**: 10 项

---

## 建议实施顺序

1. 再完成 P1-2 和 P1-3（核心功能缺失）
2. 再完成 P2-1（抽卡数量）
3. 最后完成 P1-4、P2-2 及所有 P3 项

---
*生成时间: 2026-02-10*