[-] 关于矛盾战斗中的特殊机制：The player begins this elite combat with the Debuff Surrounded. This only serves as a telegraph for their Back Attack mechanic and does not actually add any damage bonus.
Smoke Bomb cannot be used while Surrounded

[-] 大bug: 很多Enemy的intention中莫名有self.enemy.calculate_damage之类的调用。实际上，根本不需要这个函数，直接传self.damage到AttackAction就可以了

[-] 大bug: AttackAction中已经存在了一个resolve_potential_damage的伤害修改器。然而现在在DealDamageAction里面，又有get_damage_dealt_modifier，逻辑重复。个人认为，应当统一在resolve_potential_damage && resolve_card_damage 里面处理 power 的 modify_damage_dealt 和 modify_get_damage_taken_multiplier 修正。并且还要区分好顺序：关于加减算的优先，乘除放到后面

[-] 原来卡牌/药水/遗物的攻击选中目标，要么直接从所有enemy里面选，要么从不是is_dead的enemy里面选。应该统一改为从hp>0的enemy里面选。（即如果enemy还存活，但是hp=0，也无法选中）

[-] 补全/修改逻辑：act的地图布局。现在的地图布局是符合act1和act2。在act3，在ancension<20时，floor_in_act=17的楼层是VictoryRoom而不是TreasureRoom；而ancension=20时，由于有双boss站，floor_in_act=16和17是两个BossRoom（boss不同），而floor_in_act=18才是VictoryRoom。这个VictoryRoom会判断，player是否拥有3把钥匙。若没有，则直接胜利；若有，则转换到act4。act4的地图布局很独特，只有InitialRoom(act3的VictoryRoom)->RestRoom->ShopRoom->CombatRoom(Elite)->CombatRoom(Boss)->VictoryRoom，到达最后就代表最终的胜利。至于ancension，在config中调整。

[-] ApplyPower的问题。
1. 有些power只有duration有意义，amount没有意义。
2. 而有的power，其duration=-1（永久），靠amount指定效果。
3. 有的power，duration=-1, amount也没有意义。
4. 有的power则amount和duration都有意义。
5. 还有的power，其amount值和duration锚定在一起。
这个问题相当复杂。首先要分析所有power所属的类型，可以用Web的skill/mcp搜索官方定义，也可以在本地的powers/buff.md和powers/debuff.md中搜索。其次，要对ApplyPowerAction的定义进行分析，是否要进行修改。最后检查所有ApplyPowerAction调用。
又：关于堆叠。有些能力不能堆叠，且能重复存在；有的能力不能堆叠，且不能重复存在。有的能可以堆叠（所以不可能重复存在）。如果可以堆叠，对于上面5中情况，1-只堆叠duration;2-堆叠amount;3-不堆叠;4-这种情况很少。像Bomb，就不可堆叠，可重复；5-这种情况同步堆叠

[?] 检查所有 cards
[?] 检查所有 enemies
[?] 检查所有 powers
[-] 检查所有 relics
    遍历所有relic，看有没有对应的实现。用 webtool 的 mcp/skill 搜索官方实现，和现有实现比较。如果现有实现有误/没有实现，则补充实现。
[-] 检查所有 events
[] 检查游戏能够成功运行
   1. 执行 run_games.ps1，如果10个结果文件中有任何一个出现Error，都对bug进行修复，重新跑脚本，直到10个程序都不报错。
   2. 执行所有现存的测试脚本，如果报错，先根据测试的对象，重新写一个测试文件。重新测试后，如果还是出错，再对测试对象代码和测试脚本代码进行分析，尝试修复游戏机制中存在的问题。直到所有测试代码100% pass。
[-] 战斗界面美观化
[] 接入ai接口进行测试
    1. 扩展SelectAction，多接受一个context字段，用于ai可能需要的上下文
    2. 在config中，在ai下增加字段，包含api key and 模型网站
    3. 在ai/ai_interface下新建一个类，用于大模型的DecisionEngine。
    4. 在game_state中，如果是ai模式，则新建这样一个DecisionEngine的对象，用api key and model 初始化
    5. 在SelecAction中，如果是ai模式，就把prompt+context+title+options拼接起来，调用decision engine的函数，进一步发给大模型
    6. 大模型返回结果后，可能需要后处理，把结果处理为序号列表的形式，返回给SelectAction。后面步骤一致

    几个实现上的疑问：
    1. 大模型可能 有/无 思维链功能，怎么把 thinking 和 answer 区分开？
    2. 和大模型的连接，可能 有/无 流式功能，两种情况下，实现是否不同？

todo 完善进阶功能
todo 钥匙获取以及是否随心模式

[-] 重构event pool的注册系统。event分类根据所属的act

[-] 修改 on_fatal 触发条件：杀死的敌人没有 "MinorPower" (被召唤出的怪物拥有的能力) 。
有些敌怪（比如各种地精），正常情况下不是minor。但是被召唤时是minor。这应该在初始化的时候设置。
检查几个会召唤小弟的elite/boss的intention，如果小弟不是minor，则要设置为minor

[-] 补充卡牌 Innate 的实现：combat战斗开始，在 reset card_manager 之后，把Innate的卡牌从draw_pile move 到 hand
连锁反应：需要进一步修改战斗第一次抽牌；记hand已经有X手牌张牌（cause: 固有/瓶装），战斗开始时应该抽Y张牌（本来是5，受遗物影响）则只需再抽 max(Y-X, 0) 张牌

[-] 战斗胜利获得的卡牌，在act2/act3有可能能获得升级的卡牌
```markdown
The chances that a card is upgraded are shown below:
|         | Act 1 | Act 2 | Act 3 |
|---------|-------|-------|-------|
| Normal  | 100%  | 75%   | 50%   |
| Upgraded| 0%    | 25%   | 50%   |
On Ascension 12 and beyond, the chances that a card is upgraded on the card reward screen is cut in half.
The chances for Ascension 12+ are:
|         | Act 1 | Act 2 | Act 3 |
|---------|-------|-------|-------|
| Normal  | 100%  | 87.5% | 75%   |
| Upgraded| 0%    | 12.5% | 25%   |
```

[x] resolve_potential_damage中，攻击计算的modify，需要增加类别（可以用枚举）：加算->乘算->限定。最后一种目前没有，指的是像IntangiblePower一样，把所有伤害降到一点。而对于每一个阶段，都是先能力后遗物，即：能力加算->遗物加算->能力乘算->...

[-] 把StartFightAction的enemies，类型改为 List[Enemy] （更新所有引用）


1. tui模式下，三个panel区域，要做到可以通过鼠标滚轮滑动，来浏览超出范围之外的内容
2. tui模式下, display_panel，地图显示有问题。须和map_manager.py下display_map_for_human实现一致（但不要打印debug）